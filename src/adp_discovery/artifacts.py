"""Project one saved discovery revision into seven canonical artifacts."""

from .core import DiscoveryError, validate_schema
from .discovery import digest, review_subject
from .report import readiness
from .state import current_profile


def index(items):
    return {item["id"]: item for item in items}


def project_artifacts(state):
    if state["version"] != 3:
        raise DiscoveryError("artifact generation requires version 3; use upgrade --to 3")
    profile = current_profile(state)
    data = state["discovery"]
    records = state["records"]
    by_kind = {kind: [item for item in records if item["kind"] == kind]
               for kind in ("evidence", "decision", "risk", "question", "assumption", "contradiction", "preference")}
    unresolved_refs = {ref for item in by_kind["contradiction"] if item["status"] == "open" for ref in item["refs"]}
    evidence = index(by_kind["evidence"])
    findings = []
    for item in data["findings"]:
        conflicts = sorted(unresolved_refs.intersection(item["evidence_ids"]))
        findings.append({**item, "effective_assessment": "disputed" if conflicts else item["assessment"],
                         "disputed_evidence_ids": conflicts})
    supported = {item["id"]: item for item in findings if item["effective_assessment"] == "supported"}
    claims = [{**item, "support_status": "supported" if not item.get("uncertainty")
               and item["finding_ids"] and all(key in supported for key in item["finding_ids"]) else "uncertain"}
              for item in data["claims"]]
    decision_links = index(data["decision_links"])
    decisions = []
    for item in by_kind["decision"]:
        link = decision_links.get(item["id"], {})
        finding_ids = link.get("finding_ids", [])
        support = (
            item["status"] == "confirmed" and item["id"] not in unresolved_refs
            and any(key in supported for key in finding_ids)
            and any(ref in evidence and ref not in unresolved_refs for ref in item["refs"])
        )
        decisions.append({**item, **link, "finding_ids": finding_ids,
                          "support_status": "supported" if support else "uncertain"})
    requirements = []
    supported_decisions = {item["id"] for item in decisions if item["support_status"] == "supported"}
    for item in data["requirements"]:
        justification = bool(
            item.get("justification") and item["decision_ids"]
            and supported_decisions.issuperset(item["decision_ids"])
        )
        requirements.append({**item, "justification_status": "supported" if justification else "uncertain"})

    impacts = index(data["impacts"])

    def with_impact(item):
        impact = impacts.get(item["id"], {"scope": "unknown", "requirement_ids": []})
        return {**item, **impact}

    risks = [with_impact(item) for item in by_kind["risk"]]
    questions = [with_impact(item) for item in by_kind["question"] if item["status"] == "open"]
    contradictions = [with_impact(item) for item in by_kind["contradiction"]]
    gate = assess(state, profile, evidence, supported, claims, decisions, requirements, risks, questions, contradictions)
    brief = {
        "title": state["title"],
        "classification": "confirmed" if profile and profile["confirmed_by"] else "uncertain",
        "profile": profile,
        "claims": claims,
        "assumptions": by_kind["assumption"],
        "preferences": by_kind["preference"],
    }
    if not any(item["section"] == "intent" for item in claims):
        brief["draft_intent"] = {"text": state["summary"], "uncertainty": "No structured intent claim was recorded."}
    bundle = {
        "schema_version": 1,
        "source": {
            "project": state["project"], "state_version": state["version"], "revision": state["revision"],
            "profile_index": len(state["profiles"]) - 1 if profile else None, "state_digest": digest(state),
        },
        "discovery_brief": brief,
        "decision_register": {"decisions": decisions},
        "requirements_baseline": {"requirements": requirements},
        "evidence_register": {"evidence": by_kind["evidence"], "findings": findings},
        "risk_register": {"risks": risks},
        "open_questions": {"questions": questions, "frontier": state["frontier"]},
        "discovery_readiness_report": {**gate, "contradictions": contradictions},
    }
    validate_schema("artifact-bundle", bundle, "artifact bundle")
    return bundle


def assess(state, profile, evidence, supported, claims, decisions, requirements, risks, questions, contradictions):
    checks = []

    def add(code, outcome, reason, refs=(), *, basis="deterministic", **details):
        checks.append({"code": code, "outcome": outcome, "reason": reason, "basis": basis,
                       "refs": list(refs), **details})

    if not profile or not profile["confirmed_by"]:
        add("classification-unconfirmed", "block", "Classification needs recorded stakeholder confirmation.")
    if not profile or "readiness_criteria" not in profile:
        add("criteria-not-pinned", "block", "Save a confirmed profile with the composed readiness criteria.")

    sections = {item["section"] for item in claims if item["material"]}
    if "intent" not in sections:
        add("missing-brief-intent", "block", "Record a material intent claim with its findings.")
    for claim in claims:
        if claim["support_status"] == "uncertain":
            add("unsupported-claim", "block" if claim["material"] else "inform",
                claim.get("uncertainty", "The linked findings do not fully support this claim."),
                [claim["id"], *claim["finding_ids"]])

    dimensions = {item["dimension"]: item for item in readiness(state)["findings"]}
    coverage = {}
    for dimension, item in dimensions.items():
        covered_by = []
        if item["status"] == "covered":
            for decision in decisions:
                key = decision["id"]
                if key not in item["support"] or decision["support_status"] != "supported":
                    continue
                if any(dimension in evidence[ref]["dimensions"] for finding in decision["finding_ids"]
                       if finding in supported for ref in supported[finding]["evidence_ids"]):
                    covered_by.append(key)
        coverage[dimension] = covered_by
        if item["status"] == "inapplicable":
            add("dimension-coverage", "excluded", "The dimension is inapplicable.", dimension=dimension)
        elif item["status"] == "unknown-applicability":
            add("dimension-coverage", "block" if item["required"] else "inform",
                "Applicability depends on " + ", ".join(item["unresolved_tags"]) + ".", dimension=dimension)
        elif not covered_by:
            add("dimension-coverage", "block" if item["required"] else "inform",
                "Coverage needs a confirmed decision and supported finding backed by evidence for this dimension.",
                dimension=dimension)
        else:
            add("dimension-coverage", "pass", "A supported decision covers the dimension.", covered_by, dimension=dimension)

    for item in decisions:
        if item["status"] == "reopened":
            add("reopened-decision", "block", "The decision needs stakeholder reconciliation.", [item["id"]])
        elif item["status"] == "confirmed" and item["support_status"] != "supported":
            add("unsupported-decision", "block", "The confirmed decision lacks a usable finding or confirmation evidence.",
                [item["id"], *item["finding_ids"]])
    if not any(item["status"] == "active" for item in requirements):
        add("missing-requirements", "block", "Record an active requirements baseline.")
    for item in requirements:
        if item["status"] in {"superseded", "withdrawn"}:
            continue
        key = item["id"]
        if item["status"] == "proposed":
            add("pending-requirement", "block", "Settle the proposed obligation before baselining it.", [key])
        if item["justification_status"] == "uncertain":
            add("unjustified-requirement", "block", "The obligation needs a rationale and supported, confirmed decisions.",
                [key, *item["decision_ids"]])
        if not item["acceptance_criteria"]:
            add("missing-acceptance-criteria", "block", "Specify an observable acceptance outcome.", [key])

    disputed_evidence = set()
    for item in contradictions:
        if item["status"] == "open":
            disputed_evidence.update(item["refs"])
            severity = item.get("severity", "critical")
            add("unresolved-contradiction", "block" if severity == "critical" else "inform",
                "Conflicting records remain unresolved.", [item["id"], *item["refs"], *item["requirement_ids"]])
    for item in questions:
        add("open-question", "block" if item["blocking"] else "inform", "The question remains open.",
            [item["id"], *item["requirement_ids"]])
    criteria = profile.get("readiness_criteria", []) if profile else []
    baseline = next((entry["criterion"] for entry in criteria if entry["criterion"]["id"] == "baseline-review"), None)
    for item in risks:
        if item["status"] == "open":
            add("open-risk", "block" if item["blocking"] else "inform", "The risk remains open.",
                [item["id"], *item["requirement_ids"]])
        if item.get("severity", "critical" if item["blocking"] else "noncritical") == "critical":
            disposition = item.get("disposition", {})
            accepted = disposition.get("outcome") == "accepted"
            if (not disposition or disputed_evidence.intersection(disposition["evidence_ids"])
                    or (item["status"] == "open" and not accepted)
                    or (accepted and (not baseline or disposition["authorization"]["role"] != baseline["role"]))):
                add("critical-risk-disposition", "block",
                    "A critical risk needs an authorized acceptance or an evidenced resolution.",
                    [item["id"], *item["requirement_ids"]])

    subject = review_subject(state)
    condition_subject = review_subject(state, include_conditions=False)
    if not baseline:
        add("baseline-review-missing", "block", "The profile has no mandatory stakeholder baseline review.")
    pending = {item["criterion_id"]: item for item in state["discovery"]["conditions"]}
    for entry in criteria:
        criterion = entry["criterion"]
        key = criterion["id"]
        result, reason, refs = evaluate_criterion(state, entry, dimensions, coverage, subject)
        details = {"criterion_id": key, "source": entry["source"]}
        if result == "fail" and criterion["on_failure"] == "condition":
            condition = pending.get(key)
            if (condition and baseline and condition["subject"] == condition_subject
                    and condition["authorization"]["role"] == baseline["role"]):
                result = "condition"
                refs.append(condition["id"])
                details["condition_id"] = condition["id"]
            else:
                result = "block"
                reason += " A current, stakeholder-authorized condition is required."
        elif result == "fail":
            result = criterion["on_failure"]
        if criterion["kind"] == "dimension":
            details["dimension"] = criterion["dimension"]
        basis = "deterministic" if criterion["kind"] == "dimension" else f"recorded-{criterion['kind']}"
        add("catalog-criterion", result, reason, refs, basis=basis, **details)

    outcomes = {item["outcome"] for item in checks}
    status = "not-ready" if "block" in outcomes else "conditionally-ready" if "condition" in outcomes else "ready"
    return {
        "status": status, "review_subject": subject, "condition_subject": condition_subject, "checks": checks,
        "attestations": state["discovery"]["attestations"], "conditions": state["discovery"]["conditions"],
    }


def evaluate_criterion(state, entry, dimensions, coverage, subject):
    criterion = entry["criterion"]
    kind = criterion["kind"]
    if entry["applicability"] == "inapplicable":
        return "excluded", "The criterion is inapplicable.", []
    if entry["applicability"] == "unresolved":
        return "fail", "Applicability depends on " + ", ".join(entry["unresolved_tags"]) + ".", []
    if kind == "dimension":
        dimension = criterion["dimension"]
        if dimensions[dimension]["status"] == "inapplicable":
            return "excluded", "The target dimension is inapplicable.", []
        if coverage[dimension]:
            return "pass", "The target dimension has supported coverage.", coverage[dimension]
        return "fail", "The target dimension lacks supported coverage.", []
    matches = [item for item in state["discovery"]["attestations"]
               if item["criterion_id"] == criterion["id"] and item["role"] == criterion["role"]]
    current = next((item for item in reversed(matches) if item["subject"] == subject), None)
    if current:
        return ("pass" if current["outcome"] == "passed" else "fail"), current["rationale"], [current["id"]]
    if matches:
        return "fail", f"The recorded {kind} is stale for this discovery subject.", [matches[-1]["id"]]
    return "fail", f"A recorded {kind} by the {criterion['role']} role is required.", []
