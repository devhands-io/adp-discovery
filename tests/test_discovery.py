import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from src.adp_discovery.core import ROOT, Catalog, DiscoveryError
from src.adp_discovery.report import readiness
from src.adp_discovery.state import initialize, load_state, save, validate_state


def record(key, kind, status, dimensions, refs=(), **details):
    return {
        "id": key, "kind": kind, "status": status, "text": key,
        "dimensions": list(dimensions), "refs": list(refs), **details,
    }


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = Catalog(ROOT / "templates")
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "templates"
        shutil.copytree(ROOT / "templates", self.path)

    def change_overlay(self, transform):
        self.change_template("overlays/security.yaml", transform)

    def change_template(self, filename, transform):
        path = self.path / filename
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        transform(data)
        path.write_text(yaml.safe_dump(data), encoding="utf-8")

    def add_product(self, product, **dimension):
        path = self.path / "products" / f"{product}.yaml"
        path.write_text(yaml.safe_dump({
            "version": 1, "id": product, "dimensions": [dimension],
        }), encoding="utf-8")

    def test_composition_is_ordered_and_repeatable(self):
        first = self.catalog.compose("agent-skill", ["sensitive-data", "external-actions"])
        second = self.catalog.compose("agent-skill", ["external-actions", "sensitive-data"])
        self.assertEqual(first, second)
        self.assertEqual(first["overlays"], ["evaluation", "security"])
        sources = [item["source"] for item in first["dimensions"]]
        self.assertEqual(sources, ["general"] * 5 + ["agent-skill"] * 4 + ["evaluation"] * 2 + ["security"] * 2)
        self.assertEqual(self.catalog.compose("agent-skill", [])["overlays"], ["evaluation"])
        self.assertEqual(self.catalog.compose("general", [])["overlays"], [])
        self.assertEqual(self.catalog.compose("general", ["external-actions"])["overlays"], ["security"])

    def test_nested_rule_and_unknown_references(self):
        self.change_overlay(lambda data: data.update(applies={"all": [
            {"any": [{"product": "general"}, {"tag": "external-actions"}]},
            {"not": {"tag": "sensitive-data"}},
        ]}))
        catalog = Catalog(self.path)
        self.assertEqual(catalog.compose("general", [])["overlays"], ["security"])
        self.assertEqual(catalog.compose("general", ["sensitive-data"])["overlays"], [])
        self.assertEqual(catalog.compose("agent-skill", ["external-actions"])["overlays"], ["evaluation", "security"])
        self.change_overlay(lambda data: data["applies"]["all"][0]["any"].append({"product": "unknown"}))
        with self.assertRaisesRegex(DiscoveryError, "unknown product 'unknown'"):
            Catalog(self.path)
        self.change_overlay(lambda data: data.update(applies={"not": {"tag": "unknown"}}))
        with self.assertRaisesRegex(DiscoveryError, "unknown tag 'unknown'"):
            Catalog(self.path)

    def test_invalid_catalog_shapes_and_duplicate_dimensions(self):
        self.change_overlay(lambda data: data["dimensions"][0].update(id="purpose"))
        with self.assertRaisesRegex(DiscoveryError, "duplicate dimension ID 'purpose'"):
            Catalog(self.path)
        self.change_overlay(lambda data: data.update(applies={"any": []}))
        with self.assertRaisesRegex(DiscoveryError, "applies"):
            Catalog(self.path)
        path = self.path / "products" / "agent-skill.yaml"
        with path.open("a", encoding="utf-8") as stream:
            stream.write("\nid: agent-skill\n")
        with self.assertRaisesRegex(DiscoveryError, "duplicate key 'id'"):
            Catalog(self.path)

    def test_unknown_classification_is_rejected(self):
        with self.assertRaisesRegex(DiscoveryError, "unknown product"):
            self.catalog.compose("unlisted-product", [])
        with self.assertRaisesRegex(DiscoveryError, "unknown tags"):
            self.catalog.compose("general", ["typo"])

    def test_secondary_products_follow_input_order_and_can_activate_overlays(self):
        self.add_product("artifact", id="artifact-format", question="Which format?", required=True)
        self.add_product("policy", id="policy-owner", question="Who owns the policy?", required=False)
        self.change_template("base.yaml", lambda data: data["dimensions"][0].update(applies={"product": "policy"}))
        catalog = Catalog(self.path)

        profile = catalog.compose("artifact", [], secondary_products=["policy", "agent-skill"])
        self.assertEqual(profile["secondary_products"], ["policy", "agent-skill"])
        self.assertEqual(profile["overlays"], ["evaluation"])
        self.assertEqual(
            [dimension["source"] for dimension in profile["dimensions"]],
            ["general"] * 5 + ["artifact", "policy"] + ["agent-skill"] * 4 + ["evaluation"] * 2,
        )
        self.assertEqual(profile["dimensions"][0]["id"], "purpose")
        reversed_profile = catalog.compose("artifact", [], secondary_products=["agent-skill", "policy"])
        self.assertEqual(reversed_profile["dimensions"][5]["id"], "artifact-format")
        self.assertEqual(reversed_profile["dimensions"][6]["id"], "invocation")
        self.assertNotIn("purpose", [item["id"] for item in catalog.compose("general", [])["dimensions"]])
        general = catalog.compose("general", [], secondary_products=["policy"])
        self.assertEqual([dimension["source"] for dimension in general["dimensions"]], ["general"] * 5 + ["policy"])

    def test_invalid_secondary_products_and_tag_facts(self):
        for options, message in (
            ({"secondary_products": ["agent-skill"]}, "duplicate product selection 'agent-skill'"),
            ({"secondary_products": ["unknown"]}, "unknown product 'unknown'"),
            ({"secondary_products": ["general"]}, "cannot be selected as a secondary product"),
            ({"absent_tags": ["sensitive-data"]}, "require partial inspection"),
            ({"partial": True, "absent_tags": ["typo"]}, "unknown tags: typo"),
            ({"partial": True, "absent_tags": ["external-actions"]}, "both present and absent: external-actions"),
        ):
            with self.subTest(options=options), self.assertRaisesRegex(DiscoveryError, message):
                self.catalog.compose("agent-skill", ["external-actions"], **options)

    def test_partial_overlay_applicability_reports_relevant_unknown_tags(self):
        profile = self.catalog.compose("agent-skill", [], partial=True)
        self.assertEqual(profile["overlays"], ["evaluation"])
        self.assertEqual(profile["unresolved_overlays"], [
            {"id": "security", "unresolved_tags": ["external-actions", "sensitive-data"]},
        ])
        self.assertEqual(
            [(item["id"], item["source"]) for item in profile["unresolved_dimensions"]],
            [("authority", "security"), ("information-handling", "security")],
        )
        self.assertNotIn("security", [item["source"] for item in profile["dimensions"]])

        undecided = self.catalog.compose("agent-skill", [], partial=True, absent_tags=["external-actions"])
        self.assertEqual(undecided["unresolved_overlays"], [{"id": "security", "unresolved_tags": ["sensitive-data"]}])
        excluded = self.catalog.compose(
            "agent-skill", [], partial=True, absent_tags=["external-actions", "sensitive-data"],
        )
        self.assertEqual(excluded["overlays"], ["evaluation"])
        self.assertEqual(excluded["unresolved_overlays"], [])
        self.assertEqual(excluded["unresolved_dimensions"], [])
        included = self.catalog.compose("agent-skill", ["external-actions"], partial=True)
        self.assertEqual(included["overlays"], ["evaluation", "security"])
        self.assertEqual(included["unresolved_overlays"], [])
        self.assertEqual(included["unresolved_dimensions"], [])

    def test_dimension_condition_combines_with_overlay_condition(self):
        self.change_overlay(lambda data: data["dimensions"][0].update(
            required=False,
            applies={"all": [{"not": {"tag": "sensitive-data"}}, {"product": "agent-skill"}]},
        ))
        catalog = Catalog(self.path)
        for product, tags, absent, expected, missing in (
            ("agent-skill", [], [], "unresolved_dimensions", ["external-actions", "sensitive-data"]),
            ("agent-skill", ["external-actions"], [], "unresolved_dimensions", ["sensitive-data"]),
            ("agent-skill", ["external-actions"], ["sensitive-data"], "dimensions", []),
            ("agent-skill", ["sensitive-data"], [], None, []),
            ("general", [], [], None, []),
        ):
            with self.subTest(product=product, tags=tags, absent=absent):
                profile = catalog.compose(product, tags, partial=True, absent_tags=absent)
                locations = {
                    key: [item for item in profile[key] if item["id"] == "authority"]
                    for key in ("dimensions", "unresolved_dimensions")
                }
                self.assertEqual([key for key, items in locations.items() if items], [expected] if expected else [])
                if expected:
                    dimension, = locations[expected]
                    self.assertFalse(dimension["required"])
                    self.assertEqual(dimension["source"], "security")
                    self.assertEqual(dimension.get("unresolved_tags", []), missing)

    def test_template_version_and_dimension_rule_validation(self):
        for edit, message in (
            (lambda data: data.pop("version"), "version.*required"),
            (lambda data: data.update(version=2), r"\$\.version: 1 was expected"),
            (lambda data: data["dimensions"][0].update(id="purpose\n"), r"dimensions\[0\]\.id"),
            (lambda data: data["dimensions"][0].update(applies={"all": []}), r"dimensions\[0\]\.applies"),
            (lambda data: data["dimensions"][0].update(applies={"tag": "sensitive-data", "product": "general"}),
             r"dimensions\[0\]\.applies"),
            (lambda data: data["dimensions"][0].update(
                applies={"any": [{"product": "general"}, {"not": {"tag": "unknown"}}]},
            ), r"dimensions\[0\]\.applies\.any\[1\]\.not: unknown tag 'unknown'"),
        ):
            with self.subTest(message=message):
                shutil.copyfile(ROOT / "templates/base.yaml", self.path / "base.yaml")
                self.change_template("base.yaml", edit)
                with self.assertRaisesRegex(DiscoveryError, message):
                    Catalog(self.path)

    def test_duplicate_dimensions_identify_both_sources_and_conflicting_fields(self):
        base_dimension = self.catalog.base["dimensions"][0]
        self.add_product("overlap", **base_dimension)
        with self.assertRaisesRegex(
            DiscoveryError, r"duplicate dimension ID 'purpose'.*base\.yaml.*overlap\.yaml.*identical declaration",
        ):
            Catalog(self.path)
        self.add_product("overlap", **{**base_dimension, "question": "Why?", "required": False})
        with self.assertRaisesRegex(
            DiscoveryError, r"duplicate dimension ID 'purpose'.*base\.yaml.*overlap\.yaml.*conflicting fields: question, required",
        ):
            Catalog(self.path)

    def test_duplicates_within_a_template_and_across_template_roles(self):
        self.change_overlay(lambda data: data["dimensions"].append(data["dimensions"][0].copy()))
        with self.assertRaisesRegex(
            DiscoveryError, r"duplicate dimension ID 'authority'.*dimensions\[0\].*dimensions\[2\]",
        ):
            Catalog(self.path)
        self.add_product("security", id="security-owner", question="Who owns security?", required=True)
        with self.assertRaisesRegex(
            DiscoveryError, r"overlays/security\.yaml: duplicate template ID 'security'.*products/security\.yaml",
        ):
            Catalog(self.path)

    def test_duplicate_dimensions_are_rejected_even_with_exclusive_overlays(self):
        def negate_evaluation_condition(data):
            data["applies"] = {"not": {"tag": "sensitive-data"}}
            data["dimensions"][0]["id"] = "evaluation-cases"

        self.change_template("overlays/evaluation.yaml", lambda data: data.update(applies={"tag": "sensitive-data"}))
        self.change_overlay(negate_evaluation_condition)
        with self.assertRaisesRegex(
            DiscoveryError, r"duplicate dimension ID 'evaluation-cases'.*evaluation\.yaml.*security\.yaml",
        ):
            Catalog(self.path)


class StateTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "work" / "state.json"
        self.profile = Catalog(ROOT / "templates").compose("general", [])
        self.state = initialize(self.path, "Discovery", self.profile)

    def test_requires_evidence_and_valid_references(self):
        item = record("decision", "decision", "confirmed", ["purpose"])
        self.state["records"].append(item)
        with self.assertRaisesRegex(DiscoveryError, "require a dimension and evidence"):
            save(self.path, self.state)
        item["refs"] = ["missing"]
        with self.assertRaisesRegex(DiscoveryError, "unknown records missing"):
            save(self.path, self.state)
        item["dimensions"] = ["does-not-exist"]
        with self.assertRaisesRegex(DiscoveryError, "unknown dimensions"):
            save(self.path, self.state)
        self.assertEqual(load_state(self.path)["revision"], 0)

    def test_preliminary_readiness_and_contradiction_lifecycle(self):
        dimensions = [item["id"] for item in self.profile["dimensions"]]
        self.assertEqual(readiness(self.state)["status"], "gaps-remain")
        self.state["records"].extend([
            record("owner-statement", "evidence", "recorded", dimensions, source="Stakeholder interview"),
            record("agreed-baseline", "decision", "confirmed", dimensions, ["owner-statement"]),
        ])
        current = save(self.path, self.state)
        report = readiness(current)
        self.assertEqual(report["status"], "baseline-ready")
        self.assertEqual(report["findings"][0]["support"], {"agreed-baseline": ["owner-statement"]})

        current["records"].append(record(
            "scope-conflict", "contradiction", "open", ["scope"], ["agreed-baseline"]
        ))
        with self.assertRaisesRegex(DiscoveryError, "reopen linked confirmed decisions"):
            save(self.path, current)
        current["records"][1]["status"] = "reopened"
        current = save(self.path, current)
        self.assertEqual(readiness(current)["blockers"], ["agreed-baseline", "scope-conflict"])
        current["records"][1]["status"] = "confirmed"
        current["records"][2].update(status="resolved", resolution="Stakeholder confirmed the prior answer.")
        self.assertEqual(readiness(save(self.path, current))["status"], "baseline-ready")

    def test_stale_save_and_mutation_protections(self):
        before = copy.deepcopy(self.state)
        before["summary"] = "Saved by the first writer."
        before["records"] = [record("source", "evidence", "recorded", ["purpose"], source="Interview")]
        current = save(self.path, before)
        with self.assertRaisesRegex(DiscoveryError, "stale revision"):
            save(self.path, self.state)
        with self.assertRaisesRegex(DiscoveryError, "state already exists"):
            initialize(self.path, "Other", self.profile)
        rewritten = copy.deepcopy(current)
        rewritten["records"][0]["text"] = "Different evidence."
        with self.assertRaisesRegex(DiscoveryError, "retain evidence"):
            save(self.path, rewritten)
        rewritten = copy.deepcopy(current)
        rewritten["profile"]["dimensions"][0]["required"] = False
        with self.assertRaisesRegex(DiscoveryError, "immutable"):
            save(self.path, rewritten)
        self.assertEqual(load_state(self.path), current)

    def test_generic_contract_and_building_keep_domain_gaps(self):
        for question, source in (
            ("Which authority approves the site plan?", "Site discovery workshop"),
            ("Who will review jurisdiction and remedies?", "Contract owner interview"),
        ):
            with self.subTest(question=question):
                self.state["records"] = [
                    record("scope-source", "evidence", "recorded", ["scope"], source=source),
                    record("scope-decision", "decision", "confirmed", ["scope"], ["scope-source"]),
                    {**record("domain-review", "question", "open", ["constraints"], blocking=True),
                     "text": question},
                ]
                validate_state(self.state)
                report = readiness(self.state)
                self.assertEqual(report["status"], "gaps-remain")
                self.assertEqual(report["blockers"], ["domain-review"])
                self.assertEqual(self.state["profile"]["overlays"], [])


class CliTests(unittest.TestCase):
    def command(self, *args, candidate=None):
        result = subprocess.run(
            [sys.executable, "-m", "src.adp_discovery", *args], cwd=ROOT,
            input=json.dumps(candidate) if candidate is not None else None,
            capture_output=True, encoding="utf-8", timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_resume_and_export_in_separate_processes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "state.json")
            state = json.loads(self.command("init", path, "--product", "agent-skill", "--title", "Pilot"))
            state["records"] = [
                record("owner", "evidence", "recorded", ["purpose"], source="Owner interview"),
                record("purpose-agreed", "decision", "confirmed", ["purpose"], ["owner"]),
            ]
            self.command("save", path, candidate=state)
            resumed = json.loads(self.command("show", path))
            self.assertEqual(resumed["revision"], 1)
            self.assertEqual(resumed["records"][1]["status"], "confirmed")
            rendered = self.command("report", path)
            self.assertIn("## Open questions", rendered)
            self.assertIn("covered by `purpose-agreed` with owner", rendered)
            self.assertIn("`invocation` has a gap", rendered)

    def test_compose_inspects_partial_configuration(self):
        profile = json.loads(self.command(
            "compose", "--product", "general", "--secondary-product", "agent-skill",
            "--partial", "--no-tag", "sensitive-data",
        ))
        self.assertEqual(profile["secondary_products"], ["agent-skill"])
        self.assertEqual(profile["absent_tags"], ["sensitive-data"])
        self.assertEqual(profile["overlays"], ["evaluation"])
        self.assertEqual(profile["unresolved_overlays"], [{"id": "security", "unresolved_tags": ["external-actions"]}])
        self.assertEqual(profile["unresolved_dimensions"][0]["source"], "security")
        confirmed = json.loads(self.command("compose", "--product", "agent-skill"))
        self.assertEqual(set(confirmed), {"product", "tags", "overlays", "dimensions"})
        self.assertEqual(confirmed["overlays"], ["evaluation"])

    def test_compose_rejects_contradictory_tag_facts(self):
        result = subprocess.run(
            [sys.executable, "-m", "src.adp_discovery", "compose", "--product", "general", "--partial",
             "--tag", "external-actions", "--no-tag", "external-actions"],
            cwd=ROOT, capture_output=True, encoding="utf-8", timeout=15,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("both present and absent: external-actions", result.stderr)

    def test_checked_in_pilot_export_is_reproducible(self):
        folder = ROOT / "examples" / "self-discovery"
        output = self.command("report", str(folder / "state.json"))
        self.assertEqual(output, (folder / "baseline.md").read_text(encoding="utf-8"))
        report = json.loads(self.command("report", str(folder / "state.json"), "--format", "json"))
        self.assertEqual(report["status"], "gaps-remain")
        self.assertIn("handling-confirmation", report["blockers"])


if __name__ == "__main__":
    unittest.main()
