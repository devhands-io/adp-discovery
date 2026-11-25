import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from examples.milestone7.replay import PRODUCTS, model_markdown, read_scenario, replay
from src.adp_discovery.artifacts import index, project_artifacts
from src.adp_discovery.core import ROOT, Catalog
from src.adp_discovery.discovery import digest
from src.adp_discovery.state import current_profile, validate_state


def gate(state):
    return project_artifacts(state)["discovery_readiness_report"]


class ProductValidationTests(unittest.TestCase):
    def cli(self, *args):
        result = subprocess.run(
            [sys.executable, "-m", "src.adp_discovery", *args], cwd=ROOT, capture_output=True,
            encoding="utf-8", timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def check(self, state, code, outcome, **fields):
        matches = [check for check in gate(state)["checks"] if check["code"] == code
                   and all(check.get(key) == value for key, value in fields.items())]
        self.assertEqual([item["outcome"] for item in matches], [outcome])
        return matches[0]

    def test_complete_workflow_and_distinct_readiness(self):
        expected = {
            "facility": ("facility-approval-path", "facility-design-handoff-review", ["accessibility"], (11, 0, 5)),
            "process": ("process-handoff-evidence", "process-controls-review", ["evaluation", "security"], (14, 0, 1)),
            "contract": ("contract-delegation-evidence", "contract-material-legal-review", ["security"], (13, 0, 3)),
        }
        with tempfile.TemporaryDirectory() as directory:
            for product in PRODUCTS:
                with self.subTest(product=product):
                    path = Path(directory) / product / "state.json"
                    checkpoints = {}
                    scenario = read_scenario(product)
                    for label, state in replay(path, product):
                        checkpoints[label] = state
                        if label in {"draft", "interview", "evidence-request"}:
                            resumed = json.loads(self.cli("show", path))
                            self.assertEqual(resumed, state)
                            self.assertEqual(len(resumed["frontier"]), 1)
                        if label == "ready":
                            bundle = json.loads(self.cli("artifacts", path))
                            self.assertEqual(bundle["source"]["state_digest"], digest(state))
                            self.assertEqual(bundle["source"]["revision"], state["revision"])
                            self.assertEqual(len(bundle), 9)
                            self.assertEqual(json.loads(self.cli("report", path, "--format", "json")),
                                             bundle["discovery_readiness_report"])
                            markdown = self.cli("artifacts", path, "--format", "markdown")
                            self.assertEqual(markdown, self.cli("report", path))
                            self.assertEqual(bundle["discovery_readiness_report"]["status"], "ready")
                            model = model_markdown(state, scenario["model"])
                            self.assertIn(scenario["model"]["representation"], model)
                            self.assertIn(f"Source revision {state['revision']}", model)
                            if product == "contract":
                                self.assertIn("Readiness applies to drafting handoff.", markdown)
                                self.assertIn("qualified legal review of the eventual agreement", markdown)
                                self.assertIn("Readiness applies to drafting handoff.",
                                              index(bundle["discovery_brief"]["claims"])["brief-scope"]["text"])
                    self.assertIsNone(current_profile(checkpoints["draft"]))
                    gap, review, overlays, counts = expected[product]
                    ready = checkpoints["ready"]
                    profile = current_profile(ready)
                    self.assertEqual(profile["product"], product)
                    self.assertEqual(profile["overlays"], overlays)
                    self.assertEqual(tuple(len(profile[key]) for key in (
                        "dimensions", "unresolved_dimensions", "inapplicable_dimensions",
                    )), counts)
                    incomplete = checkpoints["incomplete"]
                    self.assertEqual(checkpoints["evidence-request"]["frontier"], [f"ask-{scenario['gap']}"])
                    self.assertEqual(incomplete["frontier"], [])
                    self.assertEqual(gate(incomplete)["status"], "not-ready")
                    incomplete_check = self.check(incomplete, "dimension-coverage", "block", dimension=gap)
                    if product == "facility":
                        self.assertIn("facility-approval", incomplete_check["reason"])
                        self.assertEqual(ready["profiles"][0], current_profile(incomplete))

                    topic = scenario["requirement"]["topic"]
                    contradictory = checkpoints["contradictory"]
                    self.assertEqual(gate(contradictory)["status"], "not-ready")
                    blocker = self.check(contradictory, "unresolved-contradiction", "block")
                    self.assertIn(f"req-{topic}", blocker["refs"])
                    self.check(contradictory, "reopened-decision", "block", refs=[f"{topic}-decision"])
                    self.check(contradictory, "unjustified-requirement", "block",
                               refs=[f"req-{topic}", f"{topic}-decision"])
                    records = index(ready["records"])
                    self.assertEqual(records["source-conflict"]["status"], "resolved")
                    self.assertIn("conflicting-source", records)
                    self.assertIn("conflict-clarification", records[f"{topic}-decision"]["refs"])
                    requirements = index(project_artifacts(ready)["requirements_baseline"]["requirements"])
                    self.assertEqual(len(requirements), 2)
                    self.assertEqual(requirements[f"req-{topic}"]["justification_status"], "supported")
                    self.assertEqual(requirements[f"req-{topic}"]["acceptance_criteria"][0]["id"], f"ac-{topic}")

                    stale = self.check(checkpoints["stale-reviews"], "catalog-criterion", "block",
                                       criterion_id="baseline-review")
                    self.assertIn("stale", stale["reason"])
                    high_risk = checkpoints["high-risk"]
                    self.assertEqual(gate(high_risk)["status"], "not-ready")
                    self.check(high_risk, "catalog-criterion", "pass", criterion_id="baseline-review")
                    self.check(high_risk, "catalog-criterion", "block", criterion_id=review)
                    self.check(high_risk, "critical-risk-disposition", "block", refs=["handoff-risk"] + (
                        [f"req-{scenario['additional_requirement']['topic']}"] if product == "contract"
                        else [f"req-{topic}"]
                    ))
                    if product == "facility":
                        self.check(high_risk, "dimension-coverage", "block", dimension="facility-structure")

                    if product == "process":
                        self.assertEqual(gate(checkpoints["unapproved-replay-gap"])["status"], "not-ready")
                        conditional = checkpoints["conditional"]
                        self.assertEqual(gate(conditional)["status"], "conditionally-ready")
                        condition = self.check(conditional, "catalog-criterion", "condition",
                                               criterion_id="process-case-replay")
                        self.assertEqual(condition["condition_id"], "replay-condition")
                    if product == "contract":
                        wrong_role = copy.deepcopy(ready)
                        for attestation in wrong_role["discovery"]["attestations"]:
                            if attestation["criterion_id"] == review:
                                attestation["role"] = "drafting-owner"
                        validate_state(wrong_role)
                        self.assertEqual(gate(wrong_role)["status"], "not-ready")
                        self.check(wrong_role, "catalog-criterion", "block", criterion_id=review)

    def test_partial_and_mixed_profiles_keep_domain_work_with_one_owner(self):
        catalog = Catalog(ROOT / "templates")
        facility = catalog.compose("facility", [], readiness=True)
        self.assertEqual({item["id"] for item in facility["unresolved_dimensions"]
                          if item["source"] == "facility"},
                         {"facility-structure", "facility-approval-path"})
        self.assertEqual([item["id"] for item in facility["unresolved_overlays"]], ["accessibility", "evaluation", "security"])

        process = catalog.compose("process", [], absent_tags=["cross-team-handoff"], readiness=True)
        self.assertIn("process-handoff-evidence", index(process["inapplicable_dimensions"]))
        contract = catalog.compose("contract", [], absent_tags=["delegated-signature", "material-legal-issue"],
                                   readiness=True)
        self.assertIn("contract-delegation-evidence", index(contract["inapplicable_dimensions"]))
        legal, = [entry for entry in contract["readiness_criteria"]
                  if entry["criterion"]["id"] == "contract-material-legal-review"]
        self.assertEqual(legal["applicability"], "inapplicable")

        mixed = catalog.compose(
            "facility", ["external-actions", "sensitive-data", "repeatable-quality", "cross-team-handoff"],
            secondary_products=["process"], absent_tags=["structural-work", "facility-approval"], readiness=True,
        )
        self.assertEqual(mixed["overlays"], ["evaluation", "security"])
        sources = [item["source"] for item in mixed["dimensions"]]
        self.assertEqual(list(dict.fromkeys(sources)), ["general", "facility", "process", "evaluation", "security"])
        self.assertEqual(sources.count("security"), 2)
        self.assertEqual(sources.count("evaluation"), 2)
        ids = [entry["criterion"]["id"] for entry in mixed["readiness_criteria"]]
        self.assertEqual(ids.count("information-handling-approval"), 1)
        self.assertEqual(ids.count("evaluation-plan-review"), 1)

    def test_replay_builds_reproducible_artifacts_with_optional_models(self):
        with tempfile.TemporaryDirectory() as directory:
            folders = [Path(directory) / name for name in ("first", "second")]
            exports = []
            for folder in folders:
                subprocess.run(
                    [sys.executable, "-m", "examples.milestone7.replay", "--output", folder],
                    cwd=ROOT, check=True, timeout=15,
                )
                exports.append({path.relative_to(folder): path.read_bytes()
                                for path in folder.glob("*/*/*") if path.is_file()})
            self.assertEqual(exports[0], exports[1])
            models = {str(path) for path in exports[0] if path.name == "model.md"}
            self.assertEqual(models, {f"{product}/ready/model.md" for product in PRODUCTS})
            self.assertIn(Path("contract/high-risk/model-review.md"), exports[0])
            self.assertFalse(any(path.name == "state.json" for path in exports[0]))


if __name__ == "__main__":
    unittest.main()
