"""Discovery state, validation, and local persistence."""

import json
import os
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile

from .core import DiscoveryError, index_by_id, read_json, validate_schema


def validate_state(state):
    validate_schema("state", state, "state")
    dimensions = index_by_id(state["profile"]["dimensions"], "checklist")
    records = index_by_id(state["records"], "records")
    for record in records.values():
        label = f"record {record['id']!r}"
        missing_dimensions = set(record["dimensions"]) - dimensions.keys()
        if missing_dimensions:
            raise DiscoveryError(f"{label}: unknown dimensions {', '.join(sorted(missing_dimensions))}")
        missing_records = set(record["refs"]) - records.keys()
        if missing_records:
            raise DiscoveryError(f"{label}: unknown records {', '.join(sorted(missing_records))}")
        if record["id"] in record["refs"]:
            raise DiscoveryError(f"{label}: self reference")
        referenced = [records[key] for key in record["refs"]]
        if record["kind"] == "decision" and record["status"] == "confirmed":
            if not record["dimensions"] or not any(item["kind"] == "evidence" for item in referenced):
                raise DiscoveryError(f"{label}: confirmed decisions require a dimension and evidence")
        if record["kind"] == "contradiction":
            decisions = [item for item in referenced if item["kind"] == "decision"]
            if not decisions and len(referenced) < 2:
                raise DiscoveryError(f"{label}: link a decision or at least two conflicting records")
            if record["status"] == "open" and any(item["status"] == "confirmed" for item in decisions):
                raise DiscoveryError(f"{label}: reopen linked confirmed decisions while the contradiction is open")


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
    validate_state(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    with state_lock(path):
        if os.path.lexists(path):
            raise DiscoveryError(f"{path}: state already exists")
        write_state(path, state)
    return state


def save(path, candidate):
    validate_state(candidate)
    with state_lock(path):
        current = load_state(path)
        if candidate["revision"] != current["revision"]:
            raise DiscoveryError(f"{path}: stale revision, reload revision {current['revision']} and merge your changes")
        if candidate["profile"] != current["profile"]:
            raise DiscoveryError(f"{path}: the saved checklist and classification are immutable")

        proposed = index_by_id(candidate["records"], "records")
        for previous in current["records"]:
            key = previous["id"]
            if key not in proposed or previous["kind"] != proposed[key]["kind"]:
                raise DiscoveryError(f"{path}: retain existing record {key!r} and its kind")
            updated = proposed[key]
            if previous["kind"] == "evidence" and previous != updated:
                raise DiscoveryError(f"{path}: retain evidence {key!r} and add a separate record for corrections")
            if previous["kind"] == "decision" and previous["status"] != "proposed":
                if previous["text"] != updated["text"]:
                    raise DiscoveryError(f"{path}: retain decision {key!r} text and add a record for a replacement")

        saved = {**candidate, "revision": current["revision"] + 1}
        write_state(path, saved)
    return saved
