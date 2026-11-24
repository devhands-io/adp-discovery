"""Structured discovery records shared by state validation and artifact generation."""

import hashlib
import json

from .core import DiscoveryError, index_by_id


DISCOVERY_SECTIONS = (
    "claims", "findings", "decision_links", "requirements", "impacts", "attestations", "conditions",
)


def empty_discovery():
    return {key: [] for key in DISCOVERY_SECTIONS}


def digest(value):
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def review_subject(state, *, include_conditions=True):
    """Bind judgments to substantive content, independent of the review and question queue."""
    excluded = {"attestations"} if include_conditions else {"attestations", "conditions"}
    discovery = {key: value for key, value in state["discovery"].items() if key not in excluded}
    return digest({
        "project": state["project"], "title": state["title"], "summary": state["summary"],
        "profile": state["profiles"][-1] if state["profiles"] else None,
        "records": state["records"], "discovery": discovery,
    })


def validate_criteria(profile, index):
    entries = profile.get("readiness_criteria", [])
    label = f"profile {index + 1} readiness criteria"
    index_by_id([entry["criterion"] for entry in entries], label)
    applicable = {"general", profile["product"], *profile["secondary_products"], *profile["overlays"]}
    unresolved = {entry["id"] for entry in profile["unresolved_overlays"]}
    known_tags = set(profile["tags"]) | set(profile["absent_tags"])
    dimensions = {item["id"] for key in ("dimensions", "unresolved_dimensions", "inapplicable_dimensions")
                  for item in profile[key]}
    for entry in entries:
        criterion = entry["criterion"]
        source = entry["source"]
        status = entry["applicability"]
        if (
            source not in profile["template_versions"]
            or (status == "applicable" and source not in applicable)
            or (status == "unresolved" and source not in applicable | unresolved)
            or known_tags.intersection(entry["unresolved_tags"])
        ):
            raise DiscoveryError(f"{label}: invalid applicability for {criterion['id']!r}")
        if criterion["kind"] == "dimension" and criterion["dimension"] not in dimensions:
            raise DiscoveryError(f"{label}: unknown dimension for {criterion['id']!r}")
        if criterion["id"] == "baseline-review" and (
            source != "general" or status != "applicable" or criterion["kind"] != "review" or "applies" in criterion
        ):
            raise DiscoveryError(f"{label}: baseline-review must be an unconditional base review")


def require_targets(ids, targets, label):
    missing = sorted(set(ids) - targets)
    if missing:
        raise DiscoveryError(f"{label}: missing or wrong-type targets {', '.join(missing)}")


def validate_discovery(state, records):
    data = state["discovery"]
    indices = {key: index_by_id(data[key], key) for key in DISCOVERY_SECTIONS}
    findings = indices["findings"].keys()
    requirements = indices["requirements"]
    evidence = {key for key, record in records.items() if record["kind"] == "evidence"}
    decisions = {key for key, record in records.items() if record["kind"] == "decision"}
    index_by_id(
        [item for key in ("claims", "findings", "requirements", "attestations", "conditions")
         for item in data[key]]
        + [criterion for item in data["requirements"] for criterion in item["acceptance_criteria"]]
        + list(records.values()),
        "discovery IDs",
    )
    for claim in data["claims"]:
        require_targets(claim["finding_ids"], findings, f"claim {claim['id']} findings")
    for finding in data["findings"]:
        require_targets(finding["evidence_ids"], evidence, f"finding {finding['id']} evidence")
    for link in data["decision_links"]:
        require_targets([link["id"]], decisions, "decision links")
        require_targets(link["finding_ids"], findings, f"decision {link['id']} findings")
        if successor := link.get("superseded_by"):
            require_targets([successor], decisions, f"decision {link['id']} replacement")
            if records[link["id"]]["status"] != "superseded" or successor not in records[link["id"]]["refs"]:
                raise DiscoveryError(f"decision {link['id']}: a superseded decision must reference its replacement")
    links = indices["decision_links"]
    for key, link in links.items():
        visited = {key}
        while successor := link.get("superseded_by"):
            if successor in visited:
                raise DiscoveryError(f"decision {key}: replacement cycle")
            visited.add(successor)
            link = links.get(successor, {})
    for requirement in requirements.values():
        key = requirement["id"]
        require_targets(requirement["decision_ids"], decisions, f"requirement {key} decisions")
        visited = {key}
        item = requirement
        while "superseded_by" in item:
            successor = item["superseded_by"]
            require_targets([successor], requirements.keys(), f"requirement {key} replacement")
            if successor in visited:
                raise DiscoveryError(f"requirement {key}: replacement cycle")
            visited.add(successor)
            item = requirements[successor]
    for impact in data["impacts"]:
        key = impact["id"]
        record = records.get(key, {})
        kind = record.get("kind")
        if kind not in {"risk", "question", "contradiction"}:
            raise DiscoveryError(f"impact {key}: target must be a risk, question, or contradiction")
        if "disposition" in impact and kind != "risk":
            raise DiscoveryError(f"impact {key}: only risks may have a disposition")
        require_targets(impact["requirement_ids"], requirements.keys(), f"impact {key} requirements")
        if "disposition" in impact:
            require_targets(impact["disposition"]["evidence_ids"], evidence, f"risk {key} disposition evidence")
    criteria = {
        entry["criterion"]["id"] for profile in state["profiles"]
        for entry in profile.get("readiness_criteria", [])
    }
    for key in ("attestations", "conditions"):
        for item in data[key]:
            require_targets([item["criterion_id"]], criteria, f"{key} {item['id']} criterion")


def preserve_discovery(current, candidate):
    before = current["discovery"]
    after = candidate["discovery"]
    for key, label in (("attestations", "assessments, reviews, and approvals"), ("conditions", "conditions")):
        if after[key][:len(before[key])] != before[key]:
            raise DiscoveryError(f"retain recorded {label} in order")
    findings = index_by_id(after["findings"], "findings")
    for old in before["findings"]:
        new = findings.get(old["id"], {})
        if (old["text"] != new.get("text")
                or not set(old["evidence_ids"]).issubset(new.get("evidence_ids", []))):
            raise DiscoveryError(f"retain finding {old['id']!r} wording and evidence links")
    links = index_by_id(after["decision_links"], "decision links")
    previous_decisions = index_by_id(current["records"], "records")
    for old in before["decision_links"]:
        if previous_decisions[old["id"]]["status"] == "proposed":
            continue
        new = links.get(old["id"], {})
        if (not new or not set(old["finding_ids"]).issubset(new["finding_ids"])
                or ("superseded_by" in old and old["superseded_by"] != new.get("superseded_by"))):
            raise DiscoveryError(f"retain decision {old['id']!r} finding and replacement links")
    requirements = index_by_id(after["requirements"], "requirements")
    for old in before["requirements"]:
        key = old["id"]
        new = requirements.get(key, {})
        if not new or (old["status"] in {"superseded", "withdrawn"} and new != old):
            raise DiscoveryError(f"retain requirement {key!r} and its replacement history")
        if old["status"] == "active" and (
            new["status"] == "proposed" or new["text"] != old["text"]
            or not set(old["decision_ids"]).issubset(new["decision_ids"])
        ):
            raise DiscoveryError(f"retain active requirement {key!r} wording and source decisions")
