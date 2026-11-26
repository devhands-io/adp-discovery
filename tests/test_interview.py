import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.adp_discovery.core import ROOT, DiscoveryError
from src.adp_discovery.report import readiness
from src.adp_discovery.state import load_state, save


FIXTURE = json.loads((ROOT / "examples" / "meeting-notes" / "rounds.json").read_text(encoding="utf-8"))


class InterviewTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "state.json"
        self.state = self.command("init", self.path, "--project", FIXTURE["project"], "--title", FIXTURE["title"])

    def command(self, *args, candidate=None, markdown=False):
        result = subprocess.run(
            [sys.executable, "-m", "src.adp_discovery", *args], cwd=ROOT,
            input=json.dumps(candidate) if candidate is not None else None,
            capture_output=True, encoding="utf-8", timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout if markdown else json.loads(result.stdout)

    def candidate(self, index, profile_args=None):
        step = FIXTURE["rounds"][index]
        candidate = copy.deepcopy(self.state)
        candidate["summary"] = FIXTURE["summary"]
        records = {item["id"]: item for item in candidate["records"]}
        for update in step["records"]:
            records[update["id"]] = {**records.get(update["id"], {}), **update}
        candidate["records"] = list(records.values())
        candidate["frontier"] = step["frontier"]
        args = profile_args if profile_args is not None else step.get("profile_args")
        if args:
            candidate["profiles"].append(self.command("profile", *args))
        return candidate

    def play(self, index):
        self.state = save(self.path, self.candidate(index))

    def test_multi_round_replay_from_fresh_process(self):
        for index, step in enumerate(FIXTURE["rounds"]):
            with self.subTest(round=step["name"]):
                candidate = self.candidate(index)
                self.command("save", self.path, candidate=candidate)
                self.state = self.command("show", self.path)
                self.assertEqual(self.state["revision"], index + 1)
                self.assertEqual(self.state["frontier"], step["frontier"])
                report = self.command("report", self.path, "--format", "json")
                self.assertEqual(report["classification"], "confirmed" if index else "draft")
                self.assertEqual(report["status"], "gaps-remain")
                self.assertEqual(report["frontier"], step["frontier"])
                if index == 0:
                    rendered = self.command("report", self.path, markdown=True)
                    self.assertIn("The product classification is awaiting stakeholder confirmation.", rendered)
                records = {item["id"]: item for item in self.state["records"]}
                self.assertNotIn("ask-purpose", records)
                if index == 1:
                    self.assertEqual(records["markdown-preference"]["kind"], "preference")
                    self.assertEqual(records["named-owners"]["kind"], "assumption")
                    self.assertEqual(records["recommend-owner-field"]["status"], "proposed")
                    self.assertNotIn("handling-review", report["eligible_questions"])
                    findings = {item["dimension"]: item for item in report["findings"]}
                    self.assertEqual(findings["information-handling"]["status"], "unknown-applicability")
                    self.assertEqual(findings["information-handling"]["unresolved_tags"], ["sensitive-data"])
                if index >= 2:
                    self.assertEqual(self.state["profiles"][1]["overlays"], ["evaluation", "security"])
                    self.assertEqual(self.state["profiles"][1]["template_versions"]["security"], 1)
                if index == 3:
                    self.assertEqual(records["infer-owners"]["status"], "reopened")
                    self.assertIn("owner-rule-conflict", report["blockers"])
                    self.assertIn("infer-owners", report["blockers"])
                if index == 4:
                    self.assertEqual(records["infer-owners"]["status"], "superseded")
                    self.assertEqual(records["infer-owners"]["text"], FIXTURE["rounds"][2]["records"][2]["text"])
                    self.assertEqual(records["explicit-owners-only"]["status"], "confirmed")
                    self.assertNotIn("owner-rule-conflict", report["blockers"])
                    self.assertIn("owner-policy", records)
        rendered = self.command("report", self.path, markdown=True)
        self.assertIn("Stakeholder preferences", rendered)
        self.assertIn("handling-review", rendered)
        self.assertIn("Check for missing required decisions, unresolved applicability, or recorded blockers.", rendered)

    def test_saved_batch_preserves_other_branches_and_dependencies(self):
        independent = ["purpose", "scope", "audience", "constraints", "success"]
        for key in [*independent, "follow-up"]:
            self.state["records"].append({
                "id": key, "kind": "question", "status": "open", "text": key,
                "dimensions": [], "refs": [], "blocking": True,
                "depends_on": ["scope"] if key == "follow-up" else [],
            })
        self.state["frontier"] = independent[:3]
        save(self.path, self.state)
        self.command("report", self.path, markdown=True)
        resumed = self.command("show", self.path)
        self.assertEqual(resumed["frontier"], independent[:3])
        self.assertEqual(readiness(resumed)["eligible_questions"], independent)

        scope = next(item for item in resumed["records"] if item["id"] == "scope")
        scope.update(status="resolved", resolution="Stakeholder settled the boundary.")
        resumed["frontier"] = ["constraints", "success", "follow-up"]
        save(self.path, resumed)
        self.assertEqual(readiness(load_state(self.path))["eligible_questions"],
                         ["purpose", "audience", "constraints", "success", "follow-up"])

    def test_inapplicable_questions_and_deferred_unknowns(self):
        self.play(0)
        self.play(1)
        prior = copy.deepcopy(self.state)
        self.assertIn("source-sensitivity", readiness(self.state)["eligible_questions"])
        deferred = copy.deepcopy(self.state)
        question = next(item for item in deferred["records"] if item["id"] == "source-sensitivity")
        question["deferred"] = True
        deferred["frontier"] = []
        self.state = save(self.path, deferred)
        self.assertEqual(readiness(self.state)["eligible_questions"], [])
        self.assertEqual(readiness(self.state)["status"], "gaps-remain")
        self.assertIn("source-sensitivity", readiness(self.state)["blockers"])
        with self.assertRaisesRegex(DiscoveryError, "stale revision"):
            save(self.path, prior)

        record = {
            "id": "owner-confirms-public-inputs", "kind": "evidence", "status": "recorded",
            "source": "Stakeholder, alternate round 3",
            "text": "The skill will only accept published notes and draft locally.",
            "dimensions": ["scope"], "refs": [],
        }
        self.state["records"].append(record)
        self.state["profiles"].append(self.command(
            "profile", "--product", "agent-skill", "--no-tag", "external-actions",
            "--no-tag", "sensitive-data", "--confirmed-by", record["id"],
        ))
        for item in self.state["records"]:
            if item["id"] in {"source-sensitivity", "handling-review"}:
                item.pop("deferred", None)
                item.update(status="resolved", resolution=record["text"], refs=[record["id"]])
        self.state = save(self.path, self.state)
        profile = self.state["profiles"][-1]
        self.assertEqual(profile["inapplicable_overlays"], ["accessibility", "security"])
        findings = {item["dimension"]: item["status"] for item in readiness(self.state)["findings"]}
        self.assertEqual(findings["information-handling"], "inapplicable")
        self.assertEqual(self.state["profiles"][0], prior["profiles"][0])

    def test_investigation_can_surface_conflict_without_changing_interview_batch(self):
        for index in range(3):
            self.play(index)
        previous = copy.deepcopy(self.state)
        candidate = self.candidate(3)
        # The interview can create and schedule its reconciliation prompt later.
        candidate["records"] = [item for item in candidate["records"]
                                if item["id"] != "reconcile-owner-rule"]
        candidate["frontier"] = previous["frontier"]
        self.command("save", self.path, candidate=candidate)

        saved = self.command("show", self.path)
        prior_records = {item["id"]: item for item in previous["records"]}
        records = {item["id"]: item for item in saved["records"]}
        self.assertEqual(saved["profiles"], previous["profiles"])
        self.assertEqual(saved["frontier"], ["handling-review"])
        self.assertEqual(records["infer-owners"], {**prior_records["infer-owners"], "status": "reopened"})
        self.assertEqual(records["owner-confirms-handling"], prior_records["owner-confirms-handling"])
        self.assertTrue(records["owner-policy"]["source"])
        self.assertEqual(set(records["owner-rule-conflict"]["refs"]),
                         {"infer-owners", "owner-confirms-handling", "owner-policy"})
        report = self.command("report", self.path, "--format", "json")
        self.assertIn("owner-rule-conflict", report["blockers"])
        self.assertIn("infer-owners", report["blockers"])

    def test_dependency_and_profile_integrity(self):
        self.play(0)
        candidate = self.candidate(1)
        candidate["frontier"] = ["handling-review"]
        with self.assertRaisesRegex(DiscoveryError, "eligible open questions"):
            save(self.path, candidate)
        for dependency, message in (
            ("initial-brief", "unknown question dependencies"),
            ("handling-review", "dependency cycle"),
        ):
            with self.subTest(dependency=dependency):
                candidate = self.candidate(1)
                question = next(item for item in candidate["records"] if item["id"] == "source-sensitivity")
                question["depends_on"] = [dependency]
                with self.assertRaisesRegex(DiscoveryError, message):
                    save(self.path, candidate)
        candidate = self.candidate(1)
        candidate["profiles"][0]["confirmed_by"] = ["markdown-preference"]
        with self.assertRaisesRegex(DiscoveryError, "requires confirmation evidence"):
            save(self.path, candidate)
        self.play(1)
        self.state["profiles"][0]["dimensions"][0]["required"] = False
        with self.assertRaisesRegex(DiscoveryError, "retain project identity and saved profile history"):
            save(self.path, self.state)
        self.assertEqual(load_state(self.path)["revision"], 2)

    def test_required_unknown_applicability_prevents_readiness(self):
        self.play(0)
        self.play(1)
        profile = self.state["profiles"][0]
        required = [item["id"] for item in profile["dimensions"] if item["required"]]
        self.state["records"].extend([
            {"id": "coverage-evidence", "kind": "evidence", "status": "recorded",
             "text": "The team reviewed the required parts of the active checklist.",
             "source": "Stakeholder review", "dimensions": required, "refs": []},
            {"id": "coverage-decision", "kind": "decision", "status": "confirmed",
             "text": "The team confirms the current base, skill, and evaluation scope.",
             "dimensions": required, "refs": ["coverage-evidence"]},
        ])
        for item in self.state["records"]:
            if item["kind"] == "question" and item["status"] == "open":
                item["blocking"] = False
        self.state["frontier"] = []
        self.state = save(self.path, self.state)
        report = readiness(self.state)
        self.assertEqual(report["blockers"], [])
        self.assertEqual(report["status"], "gaps-remain")

        self.state["records"].append({
            "id": "published-inputs-rule", "kind": "evidence", "status": "recorded", "refs": [],
            "text": "Only public source notes are eligible. Drafts remain local.",
            "source": "Stakeholder confirmation", "dimensions": ["scope"],
        })
        self.state["profiles"].append(self.command(
            "profile", "--product", "general", "--secondary-product", "agent-skill",
            "--no-tag", "external-actions", "--no-tag", "sensitive-data", "--confirmed-by", "published-inputs-rule",
        ))
        self.state = save(self.path, self.state)
        profile = self.state["profiles"][-1]
        self.assertEqual(profile["secondary_products"], ["agent-skill"])
        self.assertEqual(profile["overlays"], ["evaluation"])
        self.assertEqual(readiness(self.state)["status"], "baseline-ready")
        rendered = self.command("report", self.path, markdown=True)
        self.assertIn("Every applicable required topic has a confirmed, evidence-backed decision.", rendered)
        self.assertIn("Stakeholders approve the baseline separately.", rendered)

    def test_linked_confirmed_decision_must_reopen(self):
        for index in range(3):
            self.play(index)
        candidate = self.candidate(3)
        next(item for item in candidate["records"] if item["id"] == "infer-owners")["status"] = "confirmed"
        with self.assertRaisesRegex(DiscoveryError, "reopen linked confirmed decisions"):
            save(self.path, candidate)
        self.assertEqual(load_state(self.path)["revision"], 3)

    def test_explicit_legacy_upgrade_preserves_pilot(self):
        legacy = ROOT / "examples" / "self-discovery" / "state.json"
        self.path.write_bytes(legacy.read_bytes())
        before = self.command("show", self.path)
        after = self.command("upgrade", self.path, "--project", "self-discovery")
        self.assertEqual(after["revision"], before["revision"] + 1)
        self.assertEqual(after["profiles"][0]["dimensions"], before["profile"]["dimensions"])
        self.assertEqual(set(after["profiles"][0]["template_versions"].values()), {None})
        self.assertEqual(after["profiles"][0]["confirmed_by"], [])
        for old, new in zip(before["records"], after["records"]):
            self.assertEqual(new, {**old, "depends_on": []} if old["kind"] == "question" else old)
        self.assertEqual(before["revision"] + 1, self.command("show", self.path)["revision"])
        self.assertEqual(readiness(before)["blockers"], readiness(after)["blockers"])
