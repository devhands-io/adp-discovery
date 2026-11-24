"""Traceable, preliminary readiness and a Markdown discovery baseline."""

from .state import current_profile, eligible_questions


def readiness(state):
    v2 = state["version"] == 2
    profile = current_profile(state)
    records = {record["id"]: record for record in state["records"]}
    findings = []
    for dimension in profile["dimensions"] if profile else ():
        key = dimension["id"]
        if not v2 and not dimension["required"]:
            continue
        decisions = [
            record for record in records.values()
            if record["kind"] == "decision" and record["status"] == "confirmed"
            and key in record["dimensions"]
        ]
        supporting = {}
        for decision in decisions:
            evidence = [
                ref for ref in decision["refs"]
                if records[ref]["kind"] == "evidence" and key in records[ref]["dimensions"]
            ]
            if evidence:
                supporting[decision["id"]] = evidence
        if supporting:
            findings.append({"dimension": key, "status": "covered", "support": supporting})
        else:
            findings.append({
                "dimension": key, "status": "gap", "question": dimension["question"],
                "reason": "Needs a confirmed decision linked to recorded evidence for this dimension.",
            })
        if v2:
            findings[-1]["required"] = dimension["required"]

    blockers = [
        record["id"] for record in records.values()
        if (record["kind"] == "decision" and record["status"] == "reopened")
        or (record["status"] == "open" and (record["kind"] == "contradiction" or record.get("blocking")))
    ]
    if v2 and profile:
        findings.extend({
            "dimension": item["id"], "status": "unknown-applicability", "required": item["required"],
            "unresolved_tags": item["unresolved_tags"],
        } for item in profile["unresolved_dimensions"])
        findings.extend({"dimension": item["id"], "status": "inapplicable", "required": item["required"]}
                        for item in profile["inapplicable_dimensions"])

    ready = bool(profile) and not blockers and all(
        item["status"] in {"covered", "inapplicable"} for item in findings if item.get("required", True)
    )
    result = {"status": "baseline-ready" if ready else "gaps-remain", "findings": findings, "blockers": blockers}
    if v2:
        result.update(classification="confirmed" if profile else "draft",
                      frontier=state["frontier"], eligible_questions=eligible_questions(state))
    return result


def record_line(record):
    details = []
    if "source" in record:
        details.append(f"Source: {record['source']}")
    if record["dimensions"]:
        details.append(f"Dimensions: {', '.join(record['dimensions'])}")
    if record["refs"]:
        details.append(f"References: {', '.join(record['refs'])}")
    if record.get("blocking"):
        details.append("Blocking")
    if record.get("depends_on"):
        details.append(f"Prerequisites: {', '.join(record['depends_on'])}")
    if record.get("deferred"):
        details.append("Deferred")
    if "resolution" in record:
        details.append(f"Resolution: {record['resolution']}")
    text = f"- `{record['id']}` ({record['status']}) {record['text']}"
    return " ".join([text, *(f"({detail})" for detail in details)])


def markdown(state):
    report = readiness(state)
    records = state["records"]
    profile = current_profile(state)
    lines = [
        f"# {state['title']}", "", "## Discovery brief", "",
        state["summary"] or "The discovery summary is pending.", "",
    ]
    if profile:
        lines.extend([
            f"- Classification: `{profile['product']}`",
            f"- Tags: {', '.join(profile['tags']) or 'none'}",
            f"- Overlays: {', '.join(profile['overlays']) or 'none'}",
        ])
        if state["version"] == 2:
            lines.extend([
                f"- Secondary products: {', '.join(profile['secondary_products']) or 'none'}",
                f"- Absent tags: {', '.join(profile['absent_tags']) or 'none recorded'}",
                f"- Unresolved overlays: {', '.join(item['id'] for item in profile['unresolved_overlays']) or 'none recorded'}",
            ])
    else:
        lines.append("- Classification: draft, awaiting stakeholder confirmation")
    lines.append(f"- State revision: {state['revision']}")
    sections = (
        ("Decision register", ("decision",), None, "No decisions recorded."),
        ("Open questions", ("question",), "open", "No open questions recorded."),
        ("Assumptions, risks, and contradictions", ("assumption", "risk", "contradiction"), None,
         "No assumptions, risks, or contradictions recorded."),
        ("Evidence", ("evidence",), None, "No evidence recorded."),
    )
    if state["version"] == 2:
        sections += (("Stakeholder preferences", ("preference",), None, "No preferences recorded."),)
    for heading, kinds, status, empty in sections:
        entries = [
            record_line(record) for record in records
            if record["kind"] in kinds and (status is None or record["status"] == status)
        ]
        lines.extend(["", f"## {heading}", "", *(entries or [empty])])

    lines.extend(["", "## Preliminary readiness", "", f"Status: `{report['status']}`", ""])
    if state["version"] == 2:
        if report["classification"] == "draft":
            explanation = "The product classification is awaiting stakeholder confirmation."
        elif report["status"] == "baseline-ready":
            explanation = (
                "Every applicable required topic has a confirmed, evidence-backed decision. "
                "No blockers are recorded."
            )
        else:
            explanation = "Check for missing required decisions, unresolved applicability, or recorded blockers."
        lines.extend([explanation, "", "Stakeholders approve the baseline separately.", ""])
    for finding in report["findings"]:
        key = finding["dimension"]
        if finding["status"] == "gap":
            lines.append(f"- `{key}` has a gap. {finding['question']} {finding['reason']}")
        elif finding["status"] == "unknown-applicability":
            lines.append(f"- `{key}` has unknown applicability pending {', '.join(finding['unresolved_tags'])}.")
        elif finding["status"] == "inapplicable":
            lines.append(f"- `{key}` is inapplicable.")
        else:
            links = [
                f"`{decision}` with {', '.join(evidence)}"
                for decision, evidence in finding["support"].items()
            ]
            lines.append(f"- `{key}` is covered by {', '.join(links)}.")
    if report["blockers"]:
        lines.append(f"- Blocking records: {', '.join(report['blockers'])}.")
    if state["version"] == 2 and state["frontier"]:
        lines.append(f"- Current question batch: {', '.join(state['frontier'])}.")
    return "\n".join(lines) + "\n"
