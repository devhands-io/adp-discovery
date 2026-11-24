"""Regenerate the three artifact examples. Synthetic sources are explicitly labeled."""

import json
from argparse import ArgumentParser
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from src.adp_discovery.artifact_markdown import render
from src.adp_discovery.artifacts import project_artifacts
from src.adp_discovery.core import ROOT, Catalog
from src.adp_discovery.discovery import review_subject
from src.adp_discovery.state import initialize_draft, save, upgrade


SCENARIOS = (
    ("purpose", ["purpose", "stakeholders", "success"],
     "The team needs to retrieve previously confirmed project decisions during a handoff."),
    ("boundary", ["scope", "constraints", "invocation"],
     "On request, the skill reads the local record. It uses public sample data and performs no external actions."),
    ("handoff", ["outputs", "handoff"],
     "Return the latest confirmed decisions with their IDs and the saved revision. Report missing state explicitly."),
    ("evaluation", ["evaluation-cases", "acceptance-owner"],
     "The project lead reviews successful retrieval and the missing-state response."),
)


def synthetic_candidate(draft):
    profile = Catalog(ROOT / "templates").compose(
        "agent-skill", [], absent_tags=["sensitive-data", "external-actions"], readiness=True,
    )
    draft["profiles"] = [{**profile, "confirmed_by": ["type-confirmation"]}]
    draft["records"].append({
        "id": "type-confirmation", "kind": "evidence", "status": "recorded",
        "source": "Synthetic stakeholder classification", "text": "This is an agent skill using public sample data.",
        "dimensions": [], "refs": [],
    })
    discovery = draft["discovery"]
    for key, dimensions, text in SCENARIOS:
        draft["records"].extend([
            {"id": f"{key}-statement", "kind": "evidence", "status": "recorded", "text": text,
             "dimensions": dimensions, "refs": [], "source": f"Synthetic stakeholder statement about {key}"},
            {"id": f"{key}-decision", "kind": "decision", "status": "confirmed", "text": text,
             "dimensions": dimensions, "refs": [f"{key}-statement"]},
        ])
        discovery["findings"].append({
            "id": f"{key}-finding", "text": text, "evidence_ids": [f"{key}-statement"],
            "assessment": "supported", "rationale": "The population and scope are stated explicitly in the fixture.",
        })
        discovery["decision_links"].append({"id": f"{key}-decision", "finding_ids": [f"{key}-finding"]})
    discovery["claims"].extend([
        {"id": "brief-intent", "section": "intent", "text": SCENARIOS[0][2],
         "material": True, "finding_ids": ["purpose-finding"]},
        {"id": "brief-scope", "section": "scope", "text": SCENARIOS[1][2],
         "material": True, "finding_ids": ["boundary-finding"]},
    ])
    discovery["requirements"].append({
        "id": "req-retrieve-decisions", "text": SCENARIOS[2][2], "status": "active",
        "decision_ids": ["handoff-decision"], "justification": "The confirmed handoff needs traceable retrieval.",
        "acceptance_criteria": [
            {"id": "ac-confirmed-decisions", "conditions": "Given a saved revision with one confirmed decision",
             "outcome": "The output shows that decision ID and the revision.", "method": "Replay a saved workspace."},
            {"id": "ac-missing-state", "conditions": "Given a missing state file",
             "outcome": "The output identifies that the state file could not be found."},
        ],
    })
    return draft


def record_reviews(candidate, *, conditional):
    discovery = candidate["discovery"]
    criteria = candidate["profiles"][-1]["readiness_criteria"]
    if conditional:
        discovery["conditions"].append({
            "id": "condition-replay", "criterion_id": "handoff-replay",
            "subject": review_subject(candidate, include_conditions=False),
            "owner": "Synthetic project lead",
            "completion": "Replay the handoff from a saved revision and record the result before release.",
            "rationale": "The fixture permits this replay after the discovery handoff.",
            "authorization": {"actor": "Synthetic stakeholder", "role": "stakeholder",
                              "source": "Synthetic stakeholder deferral approval"},
        })
    subject = review_subject(candidate)
    for entry in criteria:
        item = entry["criterion"]
        key = item["id"]
        if entry["applicability"] != "applicable" or (conditional and key == "handoff-replay"):
            continue
        discovery["attestations"].append({
            "id": f"record-{key}", "criterion_id": key, "subject": subject, "outcome": "passed",
            "actor": f"Synthetic {item['role']}", "role": item["role"],
            "source": f"Synthetic source record for {key}", "rationale": item["description"],
        })
    return candidate


def examples():
    with TemporaryDirectory() as directory:
        base = Path(directory)
        legacy = base / "legacy.json"
        copyfile(ROOT / "examples" / "self-discovery" / "state.json", legacy)
        yield "not-ready", upgrade(legacy, "self-discovery", target=3)
        for status in ("ready", "conditionally-ready"):
            path = base / f"{status}.json"
            draft = initialize_draft(path, "Synthetic handoff skill", "synthetic-handoff", artifacts=True)
            candidate = synthetic_candidate(draft)
            yield status, save(path, record_reviews(candidate, conditional=status == "conditionally-ready"))


def main():
    cli = ArgumentParser(description=__doc__)
    cli.add_argument("--output", type=Path, required=True)
    cli.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = cli.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for name, state in examples():
        bundle = project_artifacts(state)
        if bundle["discovery_readiness_report"]["status"] != name:
            raise RuntimeError(f"Example did not produce expected status {name}")
        if args.format == "json":
            path = args.output / f"{name}.json"
            content = json.dumps(bundle, indent=2, ensure_ascii=False) + "\n"
        else:
            path = args.output / f"{name}.md"
            content = render(bundle)
        path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
