import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from examples.milestone6.replay import examples, record_reviews, synthetic_candidate
from src.adp_discovery.artifact_markdown import render
from src.adp_discovery.artifacts import project_artifacts
from src.adp_discovery.core import ROOT, Catalog, DiscoveryError, validate_schema
from src.adp_discovery.discovery import digest, review_subject
from src.adp_discovery.state import initialize_draft, load_state, save, upgrade, validate_state


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.folder = Path(directory.name)
        self.path = self.folder / "state.json"
        draft = initialize_draft(self.path, "Synthetic handoff", "synthetic-handoff", artifacts=True)
        self.candidate = synthetic_candidate(draft)

    def cli(self, *args, candidate=None, success=True):
        result = subprocess.run(
            [sys.executable, "-m", "src.adp_discovery", *args], cwd=ROOT, capture_output=True,
            encoding="utf-8", input=json.dumps(candidate) if candidate is not None else None, timeout=15,
        )
        self.assertEqual(result.returncode, 0 if success else 1, result.stderr)
        return result.stdout if success else result.stderr

    def report(self):
        validate_state(self.candidate)
        return project_artifacts(self.candidate)["discovery_readiness_report"]

    def checks(self, *, code=None, criterion=None):
        return [item for item in self.report()["checks"]
                if (code is None or item["code"] == code) and (criterion is None or item.get("criterion_id") == criterion)]

    def test_cli_produces_one_revision_and_one_gate(self):
        profile = json.loads(self.cli("profile", "--product", "agent-skill", "--no-tag", "sensitive-data",
                                      "--no-tag", "external-actions", "--confirmed-by", "type-confirmation",
                                      "--artifacts"))
        self.assertEqual(profile, self.candidate["profiles"][0])
        record_reviews(self.candidate, conditional=False)
        state = json.loads(self.cli("save", self.path, candidate=self.candidate))
        bundle = json.loads(self.cli("artifacts", self.path))
        self.assertEqual(bundle["source"], {
            "project": "synthetic-handoff", "state_version": 3, "revision": 1,
            "profile_index": 0, "state_digest": digest(state),
        })
        self.assertEqual(len(bundle), 9)
        report = json.loads(self.cli("report", self.path, "--format", "json"))
        self.assertEqual(report, bundle["discovery_readiness_report"])
        self.assertEqual(report["status"], "ready")
        self.assertEqual(self.cli("report", self.path), self.cli("artifacts", self.path, "--format", "markdown"))
        self.assertEqual(json.loads(self.cli("review-subject", self.path))["review_subject"], report["review_subject"])
        requirement = bundle["requirements_baseline"]["requirements"][0]
        self.assertEqual(requirement["acceptance_criteria"][0]["id"], "ac-confirmed-decisions")
        decision = next(item for item in bundle["decision_register"]["decisions"] if item["id"] == requirement["decision_ids"][0])
        finding = next(item for item in bundle["evidence_register"]["findings"] if item["id"] == decision["finding_ids"][0])
        self.assertEqual(finding["evidence_ids"], ["handoff-statement"])
        broken = copy.deepcopy(bundle)
        broken["risk_register"].pop("risks")
        with self.assertRaisesRegex(DiscoveryError, "risks"):
            validate_schema("artifact-bundle", broken, "artifact bundle")

    def test_deferral_requires_current_authorization_and_mandatory_reviews(self):
        record_reviews(self.candidate, conditional=True)
        self.assertEqual(self.report()["status"], "conditionally-ready")
        self.assertEqual(self.checks(criterion="handoff-replay")[0]["condition_id"], "condition-replay")
        condition = self.candidate["discovery"]["conditions"][0]
        condition["authorization"]["role"] = "discovery-reviewer"
        self.assertEqual(self.report()["status"], "not-ready")
        self.assertEqual(self.checks(criterion="handoff-replay")[0]["outcome"], "block")
        condition["authorization"]["role"] = "stakeholder"
        self.candidate["discovery"]["attestations"].pop(0)
        self.assertEqual(self.report()["status"], "not-ready")
        self.assertEqual(self.checks(criterion="baseline-review")[0]["outcome"], "block")
        self.candidate["records"][1]["text"] += " Changed for the test."
        self.assertIn("current, stakeholder-authorized", self.checks(criterion="handoff-replay")[0]["reason"])

    def test_condition_authorization_is_retained(self):
        state = save(self.path, record_reviews(self.candidate, conditional=True))
        state["discovery"]["conditions"][0]["completion"] = "Use a different completion rule."
        with self.assertRaisesRegex(DiscoveryError, "retain recorded conditions"):
            save(self.path, state)

    def test_review_survives_queue_updates_and_stales_on_material_change(self):
        self.candidate["records"].append({
            "id": "example-choice", "kind": "question", "status": "open", "text": "Which public sample?",
            "refs": [], "dimensions": [], "depends_on": [], "blocking": False,
        })
        state = save(self.path, record_reviews(self.candidate, conditional=False))
        state["frontier"] = ["example-choice"]
        state = save(self.path, state)
        self.assertEqual(project_artifacts(state)["discovery_readiness_report"]["status"], "ready")
        state["discovery"]["requirements"][0]["acceptance_criteria"][0]["outcome"] += " Show the source ID too."
        self.candidate = save(self.path, state)
        check, = self.checks(criterion="baseline-review")
        self.assertEqual(check["outcome"], "block")
        self.assertIn("stale", check["reason"])
        with self.assertRaisesRegex(DiscoveryError, "retain recorded"):
            self.candidate["discovery"]["attestations"].clear()
            save(self.path, self.candidate)

    def test_required_dimensions_unsupported_claims_and_weak_requirements(self):
        self.candidate["discovery"]["decision_links"].pop()
        self.candidate["discovery"]["claims"][0]["uncertainty"] = "The intended audience needs confirmation."
        requirement = self.candidate["discovery"]["requirements"][0]
        del requirement["justification"]
        requirement["acceptance_criteria"].clear()
        record_reviews(self.candidate, conditional=False)
        self.assertEqual(self.report()["status"], "not-ready")
        gaps = {item["dimension"] for item in self.checks(code="dimension-coverage") if item["outcome"] == "block"}
        self.assertEqual(gaps, {"evaluation-cases", "acceptance-owner"})
        for code in ("unsupported-claim", "unsupported-decision", "unjustified-requirement", "missing-acceptance-criteria"):
            self.assertEqual(self.checks(code=code)[0]["outcome"], "block")
        self.assertEqual(self.candidate["frontier"], [])

    def test_open_contradiction_blocks_and_reopened_source_invalidates_requirement(self):
        records = {item["id"]: item for item in self.candidate["records"]}
        conflict = {
            "id": "handoff-conflict", "kind": "contradiction", "status": "open", "text": "The source policies differ.",
            "refs": ["type-confirmation", "handoff-statement", "handoff-decision"], "dimensions": ["handoff"],
        }
        self.candidate["records"].append(conflict)
        records["handoff-decision"]["status"] = "reopened"
        self.assertEqual(self.checks(code="unresolved-contradiction")[0]["outcome"], "block")
        self.assertEqual(self.checks(code="unjustified-requirement")[0]["outcome"], "block")
        findings = project_artifacts(self.candidate)["evidence_register"]["findings"]
        self.assertEqual(next(item for item in findings if item["id"] == "handoff-finding")["effective_assessment"], "disputed")

    def test_critical_risk_needs_disposition_and_explicit_requirement_scope(self):
        risk = {
            "id": "unknown-format", "kind": "risk", "status": "open", "text": "An unknown format could hide a decision.",
            "refs": ["handoff-statement"], "dimensions": ["handoff"], "blocking": False,
        }
        self.candidate["records"].append(risk)
        impact = {"id": risk["id"], "scope": "requirements", "requirement_ids": ["req-retrieve-decisions"],
                  "severity": "critical"}
        self.candidate["discovery"]["impacts"].append(impact)
        self.assertEqual(self.checks(code="critical-risk-disposition")[0]["outcome"], "block")
        impact["disposition"] = {"outcome": "mitigated", "owner": "Synthetic lead",
                                 "rationale": "A compatibility case exercises the format.", "evidence_ids": ["handoff-statement"]}
        self.assertEqual(self.checks(code="critical-risk-disposition")[0]["outcome"], "block")
        risk.update(status="resolved", resolution="Verified with the compatibility case.")
        record_reviews(self.candidate, conditional=False)
        self.assertEqual(self.report()["status"], "ready")
        exported, = project_artifacts(self.candidate)["risk_register"]["risks"]
        self.assertEqual(exported["requirement_ids"], ["req-retrieve-decisions"])

    def test_resolved_legacy_blocking_risk_still_needs_disposition(self):
        self.candidate["records"].append({
            "id": "legacy-risk", "kind": "risk", "status": "resolved", "text": "The local log could be incomplete.",
            "refs": ["handoff-statement"], "dimensions": ["handoff"], "blocking": True,
            "resolution": "The team discussed the concern.",
        })
        self.assertEqual(self.checks(code="critical-risk-disposition")[0]["refs"], ["legacy-risk"])

    def test_typed_links_and_stable_ids(self):
        finding = self.candidate["discovery"]["findings"][0]
        finding["evidence_ids"] = ["handoff-decision"]
        with self.assertRaisesRegex(DiscoveryError, "wrong-type targets"):
            validate_state(self.candidate)
        finding["evidence_ids"] = ["purpose-statement"]
        requirement = self.candidate["discovery"]["requirements"][0]
        requirement["acceptance_criteria"][0]["id"] = finding["id"]
        with self.assertRaisesRegex(DiscoveryError, "duplicate ID"):
            validate_state(self.candidate)
        requirement["acceptance_criteria"][0]["id"] = "ac-restored-id"
        self.candidate["discovery"]["impacts"].append({
            "id": "purpose-statement", "scope": "requirements", "requirement_ids": [requirement["id"]],
        })
        with self.assertRaisesRegex(DiscoveryError, "risk, question, or contradiction"):
            validate_state(self.candidate)

    def test_catalog_applicability_role_and_snapshot_reproducibility(self):
        templates = ROOT / "templates"
        catalog = Catalog(templates)
        old_profile = self.candidate["profiles"][0]
        criteria = "readiness_criteria"
        self.assertEqual([item["source"] for item in old_profile[criteria]], ["general", "agent-skill", "evaluation", "security"])
        self.assertEqual(old_profile[criteria][-1]["applicability"], "inapplicable")
        self.candidate["profiles"][0] = {**catalog.compose(
            "agent-skill", [], readiness=True,
        ), "confirmed_by": old_profile["confirmed_by"]}
        self.assertEqual(self.checks(criterion="information-handling-approval")[0]["outcome"], "block")
        self.assertIn("sensitive-data", self.checks(criterion="information-handling-approval")[0]["reason"])
        self.candidate["profiles"][0] = {**catalog.compose(
            "agent-skill", ["sensitive-data"], readiness=True,
        ), "confirmed_by": old_profile["confirmed_by"]}
        record_reviews(self.candidate, conditional=False)
        attestation = self.candidate["discovery"]["attestations"][-1]
        self.assertEqual(attestation["criterion_id"], "information-handling-approval")
        self.assertEqual(self.checks(criterion=attestation["criterion_id"])[0]["outcome"], "pass")
        attestation["role"] = "stakeholder"
        self.assertEqual(self.checks(criterion=attestation["criterion_id"])[0]["outcome"], "block")

        self.candidate["profiles"][0] = old_profile
        self.candidate["discovery"]["attestations"].clear()
        save(self.path, record_reviews(self.candidate, conditional=False))
        before = self.cli("artifacts", self.path)
        custom = self.folder / "templates"
        shutil.copytree(templates, custom)
        base = custom / "base.yaml"
        base.write_text(base.read_text().replace("role: stakeholder", "role: additional-reviewer"), encoding="utf-8")
        self.assertEqual(self.cli("--templates", custom, "artifacts", self.path), before)

    def test_replay_keeps_conflict_history_and_review_question(self):
        rounds = json.loads((ROOT / "examples" / "meeting-notes" / "rounds.json").read_text())
        path = self.folder / "meeting.json"
        state = initialize_draft(path, rounds["title"], rounds["project"])
        for step in rounds["rounds"]:
            state["summary"] = rounds["summary"]
            records = {item["id"]: item for item in state["records"]}
            for update in step["records"]:
                records[update["id"]] = {**records.get(update["id"], {}), **update}
            state.update(records=list(records.values()), frontier=step["frontier"])
            if args := step.get("profile_args"):
                state["profiles"].append(json.loads(self.cli("profile", *args)))
            state = save(path, state)
        state = upgrade(path, target=3)
        bundle = project_artifacts(state)
        report = bundle["discovery_readiness_report"]
        self.assertEqual(report["status"], "not-ready")
        self.assertEqual(report["contradictions"][0]["status"], "resolved")
        historic = next(item for item in bundle["decision_register"]["decisions"] if item["id"] == "infer-owners")
        self.assertEqual(historic["status"], "superseded")
        self.assertIn("explicit-owners-only", historic["refs"])
        self.assertEqual(bundle["open_questions"]["frontier"], ["handling-review"])
        self.assertEqual(load_state(path)["records"], state["records"])

    def test_checked_in_examples_are_byte_reproducible(self):
        for name, state in examples():
            with self.subTest(name=name):
                bundle = project_artifacts(state)
                self.assertEqual(bundle["discovery_readiness_report"]["status"], name)
                expected = ROOT / "examples" / "milestone6" / f"{name}.md"
                self.assertEqual(render(bundle).encode("utf-8"), expected.read_bytes())


if __name__ == "__main__":
    unittest.main()
