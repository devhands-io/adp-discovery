"""Discovery state, validation, and local persistence."""

import json
import os
from contextlib import contextmanager
from graphlib import CycleError, TopologicalSorter
from pathlib import Path
from tempfile import NamedTemporaryFile

from .core import DiscoveryError, index_by_id, read_json, validate_schema
from .discovery import empty_discovery, preserve_discovery, validate_criteria, validate_discovery


def current_profile(state):
    if state["version"] == 1:
        return state["profile"]
    return state["profiles"][-1] if state["profiles"] else None


def eligible_questions(state):
    """Return eligible question IDs in ledger order, independently of priority."""
    questions = {item["id"]: item for item in state["records"] if item["kind"] == "question"}
    graph = {key: item.get("depends_on", []) for key, item in questions.items()}
    for key, dependencies in graph.items():
        missing = set(dependencies) - questions.keys()
        if missing:
            raise DiscoveryError(f"question {key!r}: unknown question dependencies {', '.join(sorted(missing))}")
    try:
        order = list(TopologicalSorter(graph).static_order())
    except CycleError as error:
        cycle = " -> ".join(error.args[1])
        raise DiscoveryError(f"question dependency cycle: {cycle}") from error

    profile = current_profile(state)
    applicable = {item["id"] for item in profile["dimensions"]} if profile else set()
    satisfied = set()
    eligible = set()
    for key in order:
        item = questions[key]
        if not satisfied.issuperset(graph[key]):
            continue
        if item["status"] == "resolved":
            satisfied.add(key)
        elif not item.get("deferred") and (not item["dimensions"] or applicable.intersection(item["dimensions"])):
            eligible.add(key)
    return [key for key in questions if key in eligible]


def validate_profile(profile, records, index):
    label = f"profile {index + 1}"
    overlays = index_by_id(
        [{"id": key} for key in (*profile["overlays"], *profile["inapplicable_overlays"])]
        + profile["unresolved_overlays"], f"{label} overlays",
    )
    dimensions = index_by_id(
        profile["dimensions"] + profile["unresolved_dimensions"] + profile["inapplicable_dimensions"],
        f"{label} dimensions",
    )
    selected = {"general", profile["product"], *profile["secondary_products"]}
    if {"general", profile["product"]}.intersection(profile["secondary_products"]):
        raise DiscoveryError(f"{label}: invalid secondary products")
    if selected.intersection(overlays) or profile["template_versions"].keys() != (selected | overlays.keys()):
        raise DiscoveryError(f"{label}: template versions must match the selected products and inspected overlays")
    if any(item["source"] not in profile["template_versions"] for item in dimensions.values()):
        raise DiscoveryError(f"{label}: unknown dimension source")
    applicable = selected | set(profile["overlays"])
    possible = applicable | {item["id"] for item in profile["unresolved_overlays"]}
    if (
        any(item["source"] not in applicable for item in profile["dimensions"])
        or any(item["source"] not in possible for item in profile["unresolved_dimensions"])
    ):
        raise DiscoveryError(f"{label}: a dimension cannot be more applicable than its source")
    known_tags = set(profile["tags"]) | set(profile["absent_tags"])
    if set(profile["tags"]).intersection(profile["absent_tags"]):
        raise DiscoveryError(f"{label}: tags cannot be both present and absent")
    if any(
        known_tags.intersection(item["unresolved_tags"])
        for item in profile["unresolved_overlays"] + profile["unresolved_dimensions"]
    ):
        raise DiscoveryError(f"{label}: unresolved tags must be unknown")
    versions = set(profile["template_versions"].values())
    if not index and versions == {None} and not profile["confirmed_by"]:
        return dimensions  # A version 1 checklist, imported without invented provenance.
    if None in versions or not profile["confirmed_by"] or any(
        records.get(key, {}).get("kind") != "evidence" for key in profile["confirmed_by"]
    ):
        raise DiscoveryError(f"{label}: classification requires confirmation evidence and template versions")
    return dimensions


def validate_state(state):
    version = state.get("version") if isinstance(state, dict) else None
    modern = version in (2, 3)
    schema = {2: "state-v2", 3: "state-v3"}.get(version) if isinstance(version, int) else None
    validate_schema(schema or "state", state, "state")
    records = index_by_id(state["records"], "records")
    if modern:
        dimensions = set()
        for index, profile in enumerate(state["profiles"]):
            dimensions.update(validate_profile(profile, records, index))
            if version == 3:
                validate_criteria(profile, index)
        eligible = eligible_questions(state)
        if set(state["frontier"]) - set(eligible):
            raise DiscoveryError("frontier must contain only eligible open questions")
    else:
        dimensions = index_by_id(state["profile"]["dimensions"], "checklist").keys()
    for record in records.values():
        label = f"record {record['id']!r}"
        missing_dimensions = set(record["dimensions"]) - dimensions
        if missing_dimensions:
            raise DiscoveryError(f"{label}: unknown dimensions {', '.join(sorted(missing_dimensions))}")
        missing_records = set(record["refs"]) - records.keys()
        if missing_records:
            raise DiscoveryError(f"{label}: unknown records {', '.join(sorted(missing_records))}")
        if record["id"] in record["refs"]:
            raise DiscoveryError(f"{label}: self reference")
        referenced = [records[key] for key in record["refs"]]
        if record["kind"] == "preference" and not any(item["kind"] == "evidence" for item in referenced):
            raise DiscoveryError(f"{label}: preferences require evidence")
        if record["kind"] == "decision" and record["status"] == "confirmed":
            if not record["dimensions"] or not any(item["kind"] == "evidence" for item in referenced):
                raise DiscoveryError(f"{label}: confirmed decisions require a dimension and evidence")
        if record["kind"] == "contradiction":
            decisions = [item for item in referenced if item["kind"] == "decision"]
            if not decisions and len(referenced) < 2:
                raise DiscoveryError(f"{label}: link a decision or at least two conflicting records")
            if record["status"] == "open" and any(item["status"] == "confirmed" for item in decisions):
                raise DiscoveryError(f"{label}: reopen linked confirmed decisions while the contradiction is open")
    if version == 3:
        validate_discovery(state, records)


def load_state(path):
    with path.open(encoding="utf-8") as stream:
        state = read_json(stream)
    validate_state(state)
    return state


@contextmanager
def state_lock(path):
    lock = path.with_name(f".{path.name}.lock")
    try:
        lock.mkdir()
    except FileExistsError as error:
        raise DiscoveryError(f"{path}: state is locked by another writer ({lock})") from error
    try:
        yield
    finally:
        lock.rmdir()


def write_state(path, state):
    temporary = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(state, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def initialize(path, title, profile):
    state = {"version": 1, "revision": 0, "title": title, "summary": "", "profile": profile, "records": []}
    return create_state(path, state)


def initialize_draft(path, title, project, *, artifacts=False):
    state = {
        "version": 3 if artifacts else 2, "revision": 0, "project": project, "title": title, "summary": "",
        "profiles": [], "records": [], "frontier": [],
    }
    if artifacts:
        state["discovery"] = empty_discovery()
    return create_state(path, state)


def create_state(path, state):
    validate_state(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    with state_lock(path):
        if os.path.lexists(path):
            raise DiscoveryError(f"{path}: state already exists")
        write_state(path, state)
    return state


def upgrade(path, project=None, *, target=2):
    with state_lock(path):
        current = load_state(path)
        if (current["version"], target) not in {(1, 2), (1, 3), (2, 3)}:
            raise DiscoveryError(f"{path}: cannot upgrade version {current['version']} to version {target}")
        if current["version"] == 1:
            if project is None:
                raise DiscoveryError("a version 1 upgrade requires --project")
            profile = current.pop("profile")
            templates = {"general", profile["product"], *profile["overlays"]}
            profile.update(
                secondary_products=[], absent_tags=[], unresolved_overlays=[], unresolved_dimensions=[],
                inapplicable_overlays=[], inapplicable_dimensions=[],
                template_versions=dict.fromkeys(sorted(templates)), confirmed_by=[],
            )
            for record in current["records"]:
                if record["kind"] == "question":
                    record["depends_on"] = []
            current.update(project=project, profiles=[profile], frontier=[])
        elif project is not None and current["project"] != project:
            raise DiscoveryError("retain the existing project ID when upgrading version 2")
        current.update(version=target, revision=current["revision"] + 1)
        if target == 3:
            current["discovery"] = empty_discovery()
        validate_state(current)
        write_state(path, current)
    return current


def save(path, candidate):
    validate_state(candidate)
    with state_lock(path):
        current = load_state(path)
        if candidate["revision"] != current["revision"]:
            raise DiscoveryError(f"{path}: stale revision, reload revision {current['revision']} and merge your changes")
        if candidate["version"] != current["version"]:
            raise DiscoveryError(f"{path}: state version changes require an explicit upgrade")
        modern = current["version"] >= 2
        if modern:
            count = len(current["profiles"])
            if candidate["project"] != current["project"] or candidate["profiles"][:count] != current["profiles"]:
                raise DiscoveryError(f"{path}: retain project identity and saved profile history")
            appended = candidate["profiles"][count:]
            if len(appended) > 1 or any(not profile["confirmed_by"] for profile in appended):
                raise DiscoveryError(f"{path}: save at most one newly confirmed profile per revision")
            if current["version"] == 3:
                if any("readiness_criteria" not in profile for profile in appended):
                    raise DiscoveryError(f"{path}: use profile --artifacts for a version 3 readiness snapshot")
                preserve_discovery(current, candidate)
        elif candidate["profile"] != current["profile"]:
            raise DiscoveryError(f"{path}: the saved checklist and classification are immutable")

        proposed = index_by_id(candidate["records"], "records")
        for previous in current["records"]:
            key = previous["id"]
            if key not in proposed or previous["kind"] != proposed[key]["kind"]:
                raise DiscoveryError(f"{path}: retain existing record {key!r} and its kind")
            updated = proposed[key]
            if previous["kind"] == "evidence":
                expected = previous
                if modern and set(previous["dimensions"]).issubset(updated["dimensions"]):
                    expected = {**previous, "dimensions": updated["dimensions"]}
                if expected != updated:
                    raise DiscoveryError(f"{path}: retain evidence {key!r} and add a separate record for corrections")
            if previous["kind"] == "decision" and previous["status"] != "proposed":
                if previous["text"] != updated["text"]:
                    raise DiscoveryError(f"{path}: retain decision {key!r} text and add a record for a replacement")
                if modern and (
                    updated["status"] == "proposed"
                    or (previous["status"] == "superseded" and updated != previous)
                    or not set(previous["refs"]).issubset(updated["refs"])
                    or not set(previous["dimensions"]).issubset(updated["dimensions"])
                ):
                    raise DiscoveryError(f"{path}: preserve established decision {key!r} and its supporting links")

        saved = {**candidate, "revision": current["revision"] + 1}
        write_state(path, saved)
    return saved
