"""Replay fictional facility, process, and contract discovery workspaces."""

import json
from argparse import ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from src.adp_discovery.artifact_markdown import literal, render
from src.adp_discovery.artifacts import index, project_artifacts
from src.adp_discovery.core import ROOT, Catalog
from src.adp_discovery.discovery import review_subject
from src.adp_discovery.state import initialize_draft, load_state, save


PRODUCTS = ("facility", "process", "contract")
FIXTURES = Path(__file__).parent


def record(key, kind, status, text, dimensions=(), refs=(), **details):
    return {
        "id": key, "kind": kind, "status": status, "text": text,
        "dimensions": list(dimensions), "refs": list(refs), **details,
    }


def evidence(key, text, source, dimensions=()):
    return record(key, "evidence", "recorded", text, dimensions, source=f"Fictional {source}")


def question(key, text, dimensions=()):
    return record(key, "question", "open", text, dimensions, depends_on=[], blocking=True)


def read_scenario(product):
    return yaml.safe_load((FIXTURES / f"{product}.yaml").read_text(encoding="utf-8"))


def add_profile(state, catalog, product, tags, absent, confirmation):
    profile = catalog.compose(product, tags, absent_tags=absent, readiness=True)
    state["profiles"].append({**profile, "confirmed_by": confirmation})
    return profile


def confirm_topic(state, key, topic):
    dimensions = topic["dimensions"]
    source = evidence(f"{key}-source", topic["observation"], topic["source"], dimensions)
    confirmation = evidence(
        f"{key}-confirmation", topic["decision"], f"stakeholder interview, {key} round", dimensions,
    )
    state["records"].extend([
        source, confirmation, record(f"{key}-decision", "decision", "confirmed", topic["decision"],
                                    dimensions, [source["id"], confirmation["id"]]),
    ])
    state["discovery"]["findings"].append({
        "id": f"{key}-finding", "text": topic["observation"], "evidence_ids": [source["id"]],
        "assessment": "supported", "rationale": f"The cited fixture source directly addresses {key}.",
    })
    state["discovery"]["decision_links"].append({
        "id": f"{key}-decision", "finding_ids": [f"{key}-finding"],
    })


def add_baseline(state, scenario):
    first = next(iter(scenario["topics"]))
    state["discovery"]["claims"].extend([
        {"id": "brief-intent", "section": "intent", "text": scenario["intent"],
         "material": True, "finding_ids": [f"{first}-finding"]},
        {"id": "brief-scope", "section": "scope", "text": scenario["scope"],
         "material": True, "finding_ids": [f"{item}-finding" for item in scenario["scope_topics"]]},
    ])
    for requirement in (scenario["requirement"], scenario["additional_requirement"]):
        key = requirement["topic"]
        state["discovery"]["requirements"].append({
            "id": f"req-{key}", "text": requirement["text"], "status": "active",
            "decision_ids": [f"{key}-decision"], "justification": requirement["justification"],
            "acceptance_criteria": [{
                "id": f"ac-{key}", "outcome": requirement["outcome"], "method": requirement["method"],
            }],
        })


def record_reviews(state, scenario, checkpoint, *, withheld=None):
    subject = review_subject(state)
    for entry in state["profiles"][-1]["readiness_criteria"]:
        criterion = entry["criterion"]
        key = criterion["id"]
        if entry["applicability"] != "applicable" or key == withheld:
            continue
        actor, source, rationale = scenario["reviews"][key]
        if checkpoint == "risk":
            source += ", follow-up on revised baseline"
            rationale += " The new risk remains open in the risk register."
        state["discovery"]["attestations"].append({
            "id": f"{checkpoint}-{key}", "criterion_id": key, "subject": subject, "outcome": "passed",
            "actor": f"Fictional {actor}", "role": criterion["role"], "source": f"Fictional {source}",
            "rationale": rationale,
        })


def add_conflict(state, scenario):
    key = scenario["requirement"]["topic"]
    details = scenario["conflict"]
    decision = index(state["records"])[f"{key}-decision"]
    decision["status"] = "reopened"
    alternative = evidence("conflicting-source", details["observation"], details["source"], decision["dimensions"])
    state["records"].extend([
        alternative,
        record("source-conflict", "contradiction", "open", "The current sources disagree about the confirmed decision.",
               decision["dimensions"], [f"{key}-source", alternative["id"], decision["id"]]),
        question("resolve-source-conflict", "Which source governs this decision, and under what conditions?",
                 decision["dimensions"]),
    ])
    state["discovery"]["impacts"].append({
        "id": "source-conflict", "scope": "requirements", "requirement_ids": [f"req-{key}"], "severity": "critical",
    })
    # Investigation preserves the saved batch. The interview queues reconciliation in its next round.


def resolve_conflict(state, scenario):
    key = scenario["requirement"]["topic"]
    details = scenario["conflict"]
    records = index(state["records"])
    decision = records[f"{key}-decision"]
    clarification = evidence(
        "conflict-clarification", details["resolution"], details["resolution_source"], decision["dimensions"],
    )
    state["records"].append(clarification)
    decision.update(status="confirmed", refs=[*decision["refs"], clarification["id"]])
    records["source-conflict"].update(status="resolved", resolution=details["resolution"])
    records["source-conflict"]["refs"].append(clarification["id"])
    records["resolve-source-conflict"].update(status="resolved", resolution=details["resolution"])
    records["resolve-source-conflict"]["refs"].append(clarification["id"])
    finding = index(state["discovery"]["findings"])[f"{key}-finding"]
    finding["evidence_ids"].append(clarification["id"])
    state["frontier"] = []


def authorize_condition(state, details):
    state["discovery"]["conditions"].append({
        "id": "replay-condition", "criterion_id": details["criterion"],
        "subject": review_subject(state, include_conditions=False), "owner": details["owner"],
        "completion": details["completion"], "rationale": details["rationale"],
        "authorization": {"actor": "Fictional operations sponsor", "role": "stakeholder",
                          "source": f"Fictional {details['source']}"},
    })


def add_risk(state, catalog, product, scenario):
    risk = scenario["risk"]
    dimensions = [risk["dimension"]]
    source = evidence("risk-source", risk["observation"], risk["source"], dimensions)
    state["records"].extend([
        source, record("handoff-risk", "risk", "open", risk["text"], dimensions, [source["id"]], blocking=True),
    ])
    affected = [f"req-{key}" for key, topic in scenario["topics"].items()
                if risk["dimension"] in topic["dimensions"]
                and key in (scenario["requirement"]["topic"], scenario["additional_requirement"]["topic"])]
    impact = {"id": "handoff-risk", "scope": "requirements" if affected else "project",
              "requirement_ids": affected, "severity": "critical"}
    state["discovery"]["impacts"].append(impact)
    if tag := risk.get("adds_tag"):
        profile = state["profiles"][-1]
        confirmation = evidence("scope-update", "The sponsor confirms the alternate structural option is in scope.",
                                "sponsor change round, structural option L-4")
        state["records"].append(confirmation)
        add_profile(state, catalog, product, [*profile["tags"], tag],
                    [value for value in profile["absent_tags"] if value != tag], [source["id"], confirmation["id"]])


def replay(path, product):
    catalog = Catalog(ROOT / "templates")
    scenario = read_scenario(product)
    classification = scenario["classification"]
    gap = scenario["gap"]
    unknown = classification.get("unknown_at_first", [])
    state = initialize_draft(path, scenario["title"], product, artifacts=True)
    state["summary"] = scenario["intent"]
    state["records"].extend([
        evidence("brief", scenario["intent"], "sponsor project brief"),
        question("confirm-classification", f"Is {product} the primary product, and which applicability facts are known?"),
    ])
    state["frontier"] = ["confirm-classification"]
    yield "draft", save(path, state)

    state = load_state(path)
    state["records"].append(evidence("classification", classification["confirmation"], "stakeholder classification round"))
    index(state["records"])["confirm-classification"].update(
        status="resolved", resolution="Stakeholder confirmed the type and known facts.", refs=["classification"],
    )
    profile = add_profile(state, catalog, product, [tag for tag in classification["tags"] if tag not in unknown],
                          classification["absent"], ["classification"])
    active = index(profile["dimensions"])
    topics = scenario["topics"]
    regular = [key for key in topics if key != gap]
    for key in (*regular, gap):
        dimension = topics[key]["dimensions"][-1]
        if dimension in active:
            prompt = question(f"ask-{key}", active[dimension]["question"], [dimension])
        else:
            prompt = question(f"ask-{key}", scenario["gap_question"])
        state["records"].append(prompt)
    state["frontier"] = [f"ask-{regular[0]}"]
    yield "interview", save(path, state)

    while regular:
        state = load_state(path)
        key = regular.pop(0)
        confirm_topic(state, key, topics[key])
        index(state["records"])[f"ask-{key}"].update(
            status="resolved", refs=[f"{key}-confirmation"], resolution=topics[key]["decision"],
        )
        state["frontier"] = [f"ask-{regular[0] if regular else gap}"]
        state = save(path, state)
    yield "evidence-request", state

    state = load_state(path)
    index(state["records"])[f"ask-{gap}"]["deferred"] = True
    state["frontier"] = []
    add_baseline(state, scenario)
    yield "incomplete", save(path, state)

    state = load_state(path)
    if unknown:
        add_profile(state, catalog, product, classification["tags"], classification["absent"],
                    ["classification", f"{gap}-source", f"{gap}-confirmation"])
    confirm_topic(state, gap, topics[gap])
    prompt = index(state["records"])[f"ask-{gap}"]
    prompt.update(status="resolved", refs=[f"{gap}-confirmation"], resolution=topics[gap]["decision"])
    del prompt["deferred"]
    state = save(path, state)

    add_conflict(state, scenario)
    yield "contradictory", save(path, state)
    state = load_state(path)
    state["frontier"] = ["resolve-source-conflict"]
    state = save(path, state)
    resolve_conflict(state, scenario)
    state = save(path, state)

    if condition := scenario.get("condition"):
        record_reviews(state, scenario, "unapproved", withheld=condition["criterion"])
        yield "unapproved-replay-gap", save(path, state)
        state = load_state(path)
        authorize_condition(state, condition)
        record_reviews(state, scenario, "conditional", withheld=condition["criterion"])
        yield "conditional", save(path, state)
        state = load_state(path)

    record_reviews(state, scenario, "ready")
    yield "ready", save(path, state)

    state = load_state(path)
    add_risk(state, catalog, product, scenario)
    yield "stale-reviews", save(path, state)
    state = load_state(path)
    record_reviews(state, scenario, "risk", withheld=scenario["risk"]["criterion"])
    yield "high-risk", save(path, state)


def model_markdown(state, model):
    columns = model["columns"]
    records = index(state["records"])
    lines = [
        f"# {model['representation']}", "",
        f"Workspace `{state['project']}` · Source revision {state['revision']}", "",
        model["purpose"], "",
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for *cells, references in model["rows"]:
        links = [records[key]["id"] for key in references.split(", ")]
        lines.append("| " + " | ".join([*(literal(cell) for cell in cells),
                                       ", ".join(f"`{key}`" for key in links)]) + " |")
    return "\n".join(lines) + "\n"


def main():
    cli = ArgumentParser(description=__doc__)
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    with TemporaryDirectory() as working:
        for product in PRODUCTS:
            scenario = read_scenario(product)
            for label, state in replay(Path(working) / product / "state.json", product):
                directory = args.output / product / label
                directory.mkdir(parents=True, exist_ok=True)
                bundle = project_artifacts(state)
                (directory / "artifacts.json").write_text(
                    json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
                )
                (directory / "baseline.md").write_text(render(bundle), encoding="utf-8")
                if label == "ready":
                    (directory / "model.md").write_text(model_markdown(state, scenario["model"]), encoding="utf-8")
                if label == "high-risk" and (reason := scenario["risk"].get("model_skip")):
                    (directory / "model-review.md").write_text(
                        f"# Modeling decision\n\nSource revision {state['revision']}\n\n{reason}\n",
                        encoding="utf-8",
                    )


if __name__ == "__main__":
    main()
