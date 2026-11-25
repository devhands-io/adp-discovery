import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from src.adp_discovery.core import ROOT, Catalog, DiscoveryError


class ExpansionTests(unittest.TestCase):
    def cli(self, *args, success=True):
        result = subprocess.run([sys.executable, "-m", "src.adp_discovery", *args],
                                cwd=ROOT, text=True, capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0 if success else 1, result.stderr)
        return result.stdout if success else result.stderr

    def test_accessibility_matrix(self):
        catalog = Catalog(ROOT / "templates")
        for product in ("facility", "reference-guide", "process"):
            for fact in (True, False, None):
                with self.subTest(product=product, fact=fact):
                    profile = catalog.compose(product, ["access-barriers"] if fact is True else [],
                                              absent_tags=["access-barriers"] if fact is False else [],
                                              readiness=True)
                    group = "inapplicable_dimensions"
                    if product != "process" and fact is not False:
                        group = "dimensions" if fact else "unresolved_dimensions"
                    item, = [entry for entry in profile[group] if entry["source"] == "accessibility"]
                    self.assertFalse(item["required"])
                    if group == "unresolved_dimensions":
                        self.assertEqual(item["unresolved_tags"], ["access-barriers"])

    def test_independent_catalog_batches_through_cli(self):
        with tempfile.TemporaryDirectory() as folder:
            old = Path(folder) / "old"
            new = Path(folder) / "new"
            shutil.copytree(ROOT / "templates", old)
            product = Path("products/reference-guide.yaml")
            overlay = Path("overlays/accessibility.yaml")
            (old / product).unlink()
            (old / overlay).unlink()
            shutil.copytree(old, new)
            args = ["--templates", new]
            shutil.copy(ROOT / "templates" / product, new / product)
            self.cli(*args, "validate", "--against", old)
            command = [*args, "compose", "--product", "reference-guide", "--secondary-product", "facility",
                       "--tag", "access-barriers", "--tag", "repeatable-quality"]
            before = json.loads(self.cli(*command))
            self.assertIn("guide-source-authority", [item["id"] for item in before["dimensions"]])
            self.assertEqual(before["overlays"], ["evaluation"])
            shutil.copy(ROOT / "templates" / overlay, new / overlay)
            self.cli(*args, "validate", "--against", old)
            after = self.cli(*command)
            self.assertEqual(after, self.cli(*command))
            composed = json.loads(after)
            self.assertEqual(composed["overlays"], ["accessibility", "evaluation"])
            self.assertEqual([d["source"] for d in composed["dimensions"]].count("accessibility"), 1)
            self.assertNotIn("guide-source-authority", [
                d["id"] for d in json.loads(self.cli(*args, "compose", "--product", "process"))["dimensions"]
            ])
            (new / product).write_text((new / product).read_text().replace("version: 1", "version: 8"))
            workspace = Path(folder) / "state.json"
            self.assertIn("version", self.cli(*args, "init", workspace, "--product", "reference-guide",
                                              "--title", "Guide", success=False))
            self.assertFalse(workspace.exists())

    def test_incompatible_catalog_edits(self):
        original = Catalog(ROOT / "templates")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "templates"
            shutil.copytree(ROOT / "templates", path)
            file = path / "overlays/security.yaml"
            for edit, reason in (
                (lambda d: d["dimensions"].reverse(), "reordered"),
                (lambda d: d.update(applies={"tag": "sensitive-data"}), "applicability"),
                (lambda d: d["dimensions"][0].update(id="other-authority"), "removed"),
                (lambda d: d["dimensions"].append(dict(id="extra", question="Who?", required=True)), "new obligation"),
                (lambda d: d["readiness_criteria"][0].update(role="supervisor"), "readiness_criteria"),
            ):
                with self.subTest(reason=reason):
                    data = yaml.safe_load((ROOT / "templates/overlays/security.yaml").read_text())
                    edit(data)
                    file.write_text(yaml.safe_dump(data))
                    with self.assertRaisesRegex(DiscoveryError, reason):
                        Catalog(path).check_compatibility(original)
            file.unlink()
            with self.assertRaisesRegex(DiscoveryError, "template removed"):
                Catalog(path).check_compatibility(original)
