import tempfile
import unittest
from pathlib import Path

from src.adp_discovery.core import ROOT
from src.adp_discovery.interaction import load_model, render


class WalkthroughTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        folder = Path(temporary.name)
        self.path = folder / "model.md"
        self.output = folder / "viewer.html"
        self.source = (ROOT / "examples/interaction-model/interaction-model.md").read_text()
        self.path.write_text(self.source)

    def test_portable_corrected_routes(self):
        message = render(self.path, self.output, "review-form")
        self.assertIn("#screen-review-form", message)
        html = self.output.read_text()
        self.assertIn("Review decision → Save → Decision details", html)
        self.assertIn("Decision details → Return to list → Decision list", html)
        self.assertIn("Review decision → Back → Decision list", html)
        self.assertIn('href="#screen-decision-details">Save</a>', html)
        self.assertIn('value="Publish the revised launch checklist"', html)

    def test_missing_intended_step_stays_reviewable(self):
        self.path.write_text(self.source.replace(
            "actions:\n      return-to-list: {label: Return to list, go: decision-list}", "actions: {}"))
        render(self.path, self.output)
        self.assertIn("Decision details → Missing action <code>return-to-list", self.output.read_text())

    def test_invalid_graph_never_replaces_viewer(self):
        for before, after in [
            ("go: decision-details", "go: missing"),
            ("start: decision-list", "start: absent"),
            ("type: text-field", "type: unknown"),
            ("label: Save", "label: Save, label: Repeat"),
        ]:
            with self.subTest(before=before):
                self.path.write_text(self.source.replace(before, after))
                self.output.write_text("previous review")
                with self.assertRaises(ValueError):
                    render(self.path, self.output)
                self.assertEqual(self.output.read_text(), "previous review")

    def test_revision_and_safe_example_rendering(self):
        _, before = load_model(self.path)
        self.path.write_text(self.source.replace("Publish the revised launch checklist", "<script>"))
        _, after = load_model(self.path)
        self.assertNotEqual(before, after)
        render(self.path, self.output)
        self.assertIn("&lt;script&gt;", self.output.read_text())
        self.assertNotIn("<script>", self.output.read_text())
        with self.assertRaisesRegex(ValueError, "retry screen"):
            render(self.path, self.output, "absent")
