"""Compile a portable interaction model into a local, single-page walkthrough."""

import json
import re
from hashlib import sha256
from html import escape
from pathlib import Path
from string import Template

import yaml

from .core import CatalogLoader, validate_schema


def load_model(path):
    document = path.read_text(encoding="utf-8")
    blocks = re.findall(r"^```yaml[ \t]*\n(.*?)^```[ \t]*$", document, re.M | re.S)
    if len(blocks) != 1:
        raise ValueError("expected one fenced yaml block in the Markdown model")
    try:
        model = yaml.load(blocks[0], Loader=CatalogLoader)
        validate_schema("interaction-model", model, path)
    except (RecursionError, yaml.YAMLError) as error:
        raise ValueError(f"invalid model YAML: {error}") from error
    screens = model["screens"]
    for sid, screen in screens.items():
        for aid, action in screen["actions"].items():
            if action["go"] not in screens:
                raise ValueError(f"{sid}.{aid}: unknown destination {action['go']}")
    for sid, scenario in model["scenarios"].items():
        if scenario["start"] not in screens:
            raise ValueError(f"{sid}: unknown start {scenario['start']}")
    return model, sha256(document.encode()).hexdigest()


def action_label(action):
    if "row" in action:
        return f"{action['label']} — {action['row']}"
    return action["label"]


def binding(item):
    return f' data-bind="{item["bind"]}"' if "bind" in item else ""


def action_html(aid, action):
    label = escape(action["label"])
    target = f'#screen-{action["go"]}'
    commit = ' data-commit="true"' if action.get("commit") else ""
    if "reveal" in action:
        commit += f' data-reveal="{action["reveal"]}"'
    visibility = f' hidden data-after="{action["visibleAfter"]}"' if "visibleAfter" in action else ""
    if "row" in action:
        return (f'<div class="action-row"{visibility}><span{binding(action)}>{escape(action["row"])}</span>'
                f'<a data-action="{aid}" href="{target}"{commit} aria-label="{escape(action_label(action))}">{label}</a></div>')
    return f'<a data-action="{aid}" href="{target}"{visibility}{commit}>{label}</a>'


def scenario_signature(model, scenario):
    """Identify the described scenario and only the route it exercises."""
    current = scenario["start"]
    route = []
    for aid in scenario["steps"]:
        screen = model["screens"][current]
        action = screen["actions"].get(aid)
        route.append((current, screen["title"], screen["elements"], aid, action))
        if action is None:
            break
        current = action["go"]
    destination = model["screens"][current]
    payload = [scenario, route, current, destination["title"], destination["elements"]]
    return sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def coverage(model, scenario):
    current = scenario["start"]
    rows = []
    for aid in scenario["steps"]:
        screen = model["screens"][current]
        action = screen["actions"].get(aid)
        if action is None:
            rows.append(f"{escape(screen['title'])} → Missing action <code>{aid}</code>")
            break
        target = action["go"]
        rows.append(" → ".join(escape(s) for s in (
            screen["title"], action_label(action), model["screens"][target]["title"])))
        current = target
    return "".join(f"<li>{row}</li>" for row in rows)


def element_html(element):
    if element["type"] == "text":
        return f"<p{binding(element)}>{escape(element['value'])}</p>"
    fields = "".join(
        f'<label>{escape(field["label"])}<input value="{escape(field["example"])}"{binding(field) or " readonly"}></label>'
        for field in element["fields"]
    )
    return f"<fieldset><legend>{escape(element['label'])}</legend>{fields}</fieldset>"


def render(path, output, start=None):
    if path.resolve() == output.resolve() or output.suffix.lower() != ".html":
        raise ValueError("choose a separate .html file for the preview")
    model, digest = load_model(path)
    if start is not None and start not in model["screens"]:
        raise ValueError(f"unknown retry screen: {start}")
    inventory = ", ".join(escape(s["title"]) for s in model["screens"].values())
    overview = [f'<section id="coverage"><h1>{escape(model["scope"])}</h1>',
                '<h2>Choose a scenario</h2><p id="progress" aria-live="polite"></p>']
    traces = []
    for number, (sid, scenario) in enumerate(model["scenarios"].items(), start=1):
        title = f'Scenario {number} · {escape(scenario["capability"])}'
        steps = " ".join(scenario["steps"])
        overview.append(f'<div class="scenario"><div><h3>{title}</h3><span class="status"></span></div>'
                        f'<a class="start" data-scenario="{sid}" data-steps="{steps}" '
                        f'data-signature="{scenario_signature(model, scenario)}" href="#screen-{scenario["start"]}" aria-label="Start: {title}">Start</a></div>')
        overview.append(f'<details class="scenario-notes" data-notes-for="{sid}"><summary>Notes</summary>'
                        '<div class="note-fields"></div></details>')
        traces.append(f'<h3>{title}</h3><ol>{coverage(model, scenario)}</ol>')
    overview.append('<button id="copy-notes" type="button" disabled>Copy notes</button>'
                    '<p>Copies all notes with their scenario details, including the screen and step when available. Paste them into chat when you’re ready.</p>'
                    '<p id="copy-status" role="status"></p>'
                    '<textarea id="manual-copy" aria-label="Notes to copy" readonly hidden></textarea>')
    overview.append(f'<details><summary>Review coverage</summary><h3>Screens</h3><p>{inventory}</p>'
                    + "".join(traces) + '</details></section>')
    pages = []
    for sid, screen in model["screens"].items():
        content = "".join(element_html(e) for e in screen["elements"])
        actions = "".join(action_html(aid, action) for aid, action in screen["actions"].items())
        pages.append(f'<section id="screen-{sid}"><h1>{escape(screen["title"])}</h1>{content}'
                     f'<nav aria-label="Screen actions">{actions}</nav>'
                     '<footer><a href="#coverage">Back to scenarios</a></footer></section>')
    default = "screen-" + start if start else "coverage"
    template = Path(__file__).with_name("interaction.html").read_text(encoding="utf-8")
    guide = Path(__file__).with_name("interaction-guide.js").read_text(encoding="utf-8")
    notes = Path(__file__).with_name("interaction-notes.js").read_text(encoding="utf-8")
    behavior = f'<script type="module">{notes}\n{guide}</script>'
    if any("bind" in field for screen in model["screens"].values()
           for element in screen["elements"] for field in element.get("fields", [])):
        script = Path(__file__).with_name("interaction-edit.js").read_text(encoding="utf-8")
        behavior += f"<script>{script}</script>"
    html = Template(template).substitute(default_page=default, revision=digest, model_key=sha256(str(path.resolve()).encode()).hexdigest(), title=escape(model["scope"]),
                                         pages="".join(overview + pages), behavior=behavior)
    output.write_text(html, encoding="utf-8")
    return f"{output.resolve().as_uri()}#{default}\nModel revision {digest}\n"
