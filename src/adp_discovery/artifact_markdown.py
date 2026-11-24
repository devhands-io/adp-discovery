"""Markdown review view of a canonical discovery artifact bundle."""

import re


def literal(value):
    text = " ".join(value.split())
    return re.sub(r"([\\`*_{}\[\]<>#|~&$])", r"\\\1", text)


def ids(values):
    return ", ".join(f"`{value}`" for value in values)


def line(item, *parts):
    return " · ".join([f"- `{item['id']}`", *(part for part in parts if part)])


def reference(label, values):
    return f"{label} {ids(values)}" if values else ""


def outcome_text(value):
    return value.replace("-", " ")


def impact_text(item):
    return reference("Affects", item["requirement_ids"]) or f"{outcome_text(item['scope']).capitalize()} impact"


def append_section(lines, heading, entries, empty):
    lines.extend(["", f"## {heading}", ""])
    lines.extend(entries or [empty])


def render(bundle):
    source = bundle["source"]
    brief = bundle["discovery_brief"]
    profile = brief["profile"]
    lines = [
        f"# {literal(brief['title'])}", "",
        f"Project `{source['project']}` · State v{source['state_version']} · Revision {source['revision']}",
        f"State digest `{source['state_digest']}`",
    ]
    entries = [f"Classification **{brief['classification']}**"]
    if profile:
        entries[0] += " · " + ids([profile["product"], *profile["secondary_products"]])
        entries[0] += (" · " + reference("Confirmation", profile["confirmed_by"])) if profile["confirmed_by"] else ""
        entries.append(f"Applicable overlays {ids(profile['overlays']) or 'none'}")
    if draft := brief.get("draft_intent"):
        entries.append(f"- Draft intent · {literal(draft['text']) or 'Pending'} · {literal(draft['uncertainty'])}")
    entries.extend(line(item, item["section"].capitalize(), literal(item["text"]),
                        outcome_text(item["support_status"]), reference("Findings", item["finding_ids"]),
                        literal(item.get("uncertainty", ""))) for item in brief["claims"])
    for collection, label in (("assumptions", "Assumption"), ("preferences", "Preference")):
        entries.extend(line(item, label, item["status"], literal(item["text"]),
                            reference("References", item["refs"]), literal(item.get("resolution", "")))
                       for item in brief[collection])
    append_section(lines, "Discovery brief", entries, "")

    append_section(lines, "Decision register", [
        line(item, item["status"], literal(item["text"]), outcome_text(item["support_status"]),
             reference("Dimensions", item["dimensions"]), reference("Findings", item["finding_ids"]),
             reference("Replaced by", [item["superseded_by"]] if "superseded_by" in item else []),
             reference("Ledger references", item["refs"]), literal(item.get("resolution", "")))
        for item in bundle["decision_register"]["decisions"]
    ], "No decisions recorded.")

    entries = []
    for item in bundle["requirements_baseline"]["requirements"]:
        entries.append(line(item, item["status"], literal(item["text"]),
                            "justification " + outcome_text(item["justification_status"]),
                            reference("Decisions", item["decision_ids"]), literal(item.get("justification", "")),
                            reference("Replaced by", [item["superseded_by"]] if "superseded_by" in item else [])))
        entries.extend("  " + line(criterion, literal(criterion["outcome"]), literal(criterion.get("conditions", "")),
                                   literal(criterion.get("method", "")))
                       for criterion in item["acceptance_criteria"])
    append_section(lines, "Requirements baseline", entries, "No requirements recorded.")

    evidence = bundle["evidence_register"]
    entries = [line(item, literal(item["text"]), "Source " + literal(item["source"]),
                    reference("Dimensions", item["dimensions"])) for item in evidence["evidence"]]
    if evidence["findings"]:
        entries.extend(["", "### Findings", ""])
        entries.extend(line(item, item["effective_assessment"], literal(item["text"]), literal(item["rationale"]),
                            reference("Evidence", item["evidence_ids"]),
                            reference("Disputed evidence", item["disputed_evidence_ids"]))
                       for item in evidence["findings"])
    append_section(lines, "Evidence register", entries, "No evidence recorded.")

    entries = []
    for item in bundle["risk_register"]["risks"]:
        entries.append(line(item, item["status"], "blocking" if item["blocking"] else "",
                            item.get("severity", "severity unassessed"), literal(item["text"]), impact_text(item),
                            reference("Ledger references", item["refs"]), literal(item.get("resolution", ""))))
        if disposition := item.get("disposition"):
            parts = [disposition["outcome"], "Owner " + literal(disposition["owner"]),
                     literal(disposition["rationale"]), reference("Evidence", disposition["evidence_ids"])]
            if authorization := disposition.get("authorization"):
                parts.append(f"Authorized by {literal(authorization['actor'])} "
                             f"(`{authorization['role']}`) · {literal(authorization['source'])}")
            entries.append("  - " + " · ".join(parts))
    append_section(lines, "Risk register", entries, "No risks recorded.")

    questions = bundle["open_questions"]
    entries = [line(item, literal(item["text"]), "blocking" if item["blocking"] else "",
                    "deferred" if item.get("deferred") else "", impact_text(item),
                    reference("Prerequisites", item["depends_on"]), reference("Ledger references", item["refs"]))
               for item in questions["questions"]]
    if questions["frontier"]:
        entries.extend(["", reference("Current question batch", questions["frontier"])])
    append_section(lines, "Open questions", entries, "No open questions recorded.")

    report = bundle["discovery_readiness_report"]
    entries = [f"**{outcome_text(report['status']).capitalize()}**", ""]
    for item in report["checks"]:
        key = item.get("criterion_id", item.get("dimension", item["code"]))
        source = f" · Template `{item['source']}`" if "source" in item else ""
        refs = f" · {ids(item['refs'])}" if item["refs"] else ""
        entries.append(f"- **{outcome_text(item['outcome']).capitalize()}** · `{key}`{source} · "
                       f"{literal(item['reason'])}{refs}")
    if report["contradictions"]:
        entries.extend(["", "### Contradictions", ""])
        entries.extend(line(item, item["status"], literal(item["text"]), impact_text(item),
                            reference("Conflicting records", item["refs"]), literal(item.get("resolution", "")))
                       for item in report["contradictions"])
    if report["conditions"]:
        entries.extend(["", "### Recorded conditions", ""])
        applied = {item["condition_id"] for item in report["checks"] if "condition_id" in item}
        for item in report["conditions"]:
            auth = item["authorization"]
            entries.append(line(item, ids([item["criterion_id"]]), "applied" if item["id"] in applied else "recorded",
                                "Owner " + literal(item["owner"]),
                                literal(item["completion"]), literal(item["rationale"]),
                                f"Authorized by {literal(auth['actor'])} (`{auth['role']}`) · {literal(auth['source'])}"))
    if report["attestations"]:
        entries.extend(["", "### Recorded assessments, reviews, and approvals", ""])
        entries.extend(line(item, ids([item["criterion_id"]]), item["outcome"],
                            "current subject" if item["subject"] == report["review_subject"] else "earlier subject",
                            f"{literal(item['actor'])} (`{item['role']}`)", literal(item["source"]),
                            literal(item["rationale"])) for item in report["attestations"])
    append_section(lines, "Discovery readiness report", entries, "")
    return "\n".join(lines) + "\n"
