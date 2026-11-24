"""Traceable, preliminary readiness and a Markdown discovery baseline."""


def readiness(state):
    records = {record["id"]: record for record in state["records"]}
    findings = []
    for dimension in state["profile"]["dimensions"]:
        key = dimension["id"]
        if not dimension["required"]:
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

    blockers = [
        record["id"] for record in records.values()
        if (record["kind"] == "decision" and record["status"] == "reopened")
        or (record["status"] == "open" and (record["kind"] == "contradiction" or record.get("blocking")))
    ]
    ready = not blockers and all(item["status"] == "covered" for item in findings)
    return {"status": "baseline-ready" if ready else "gaps-remain", "findings": findings, "blockers": blockers}


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
    if "resolution" in record:
        details.append(f"Resolution: {record['resolution']}")
    text = f"- `{record['id']}` ({record['status']}) {record['text']}"
    return " ".join([text, *(f"({detail})" for detail in details)])


def markdown(state):
    report = readiness(state)
    records = state["records"]
    profile = state["profile"]
    lines = [
        f"# {state['title']}", "", "## Discovery brief", "",
        state["summary"] or "The discovery summary is pending.", "",
        f"- Classification: `{profile['product']}`",
        f"- Tags: {', '.join(profile['tags']) or 'none'}",
        f"- Overlays: {', '.join(profile['overlays']) or 'none'}",
        f"- State revision: {state['revision']}",
    ]
    sections = (
        ("Decision register", ("decision",), None, "No decisions recorded."),
        ("Open questions", ("question",), "open", "No open questions recorded."),
        ("Assumptions, risks, and contradictions", ("assumption", "risk", "contradiction"), None,
         "No assumptions, risks, or contradictions recorded."),
        ("Evidence", ("evidence",), None, "No evidence recorded."),
    )
    for heading, kinds, status, empty in sections:
        entries = [
            record_line(record) for record in records
            if record["kind"] in kinds and (status is None or record["status"] == status)
        ]
        lines.extend(["", f"## {heading}", "", *(entries or [empty])])

    lines.extend(["", "## Preliminary readiness", "", f"Status: `{report['status']}`", ""])
    for finding in report["findings"]:
        key = finding["dimension"]
        if finding["status"] == "gap":
            lines.append(f"- `{key}` has a gap. {finding['question']} {finding['reason']}")
        else:
            links = [
                f"`{decision}` with {', '.join(evidence)}"
                for decision, evidence in finding["support"].items()
            ]
            lines.append(f"- `{key}` is covered by {', '.join(links)}.")
    if report["blockers"]:
        lines.append(f"- Blocking records: {', '.join(report['blockers'])}.")
    return "\n".join(lines) + "\n"
