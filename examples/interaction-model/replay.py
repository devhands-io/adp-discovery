"""Rehearse in a new directory, preserving each revision for side-by-side retry."""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = HERE / "interaction-model.md"


def view(model, start=None):
    output = model.with_suffix(".html")
    command = [sys.executable, "-m", "src.adp_discovery", "interaction-view", model, output]
    if start:
        command.extend(["--start", start])
    subprocess.run(command, cwd=ROOT, check=True)


def rehearse(folder):
    folder.mkdir(parents=True, exist_ok=False)
    block = SOURCE.read_text(encoding="utf-8").split("```yaml\n", 1)[1].split("```", 1)[0]
    original = "# Review a meeting decision\n\nPilot rehearsal, discovery revision 13.\n\n```yaml\n" + block + "```\n"
    route = "      return-to-list: {label: Return to list, go: decision-list}\n"
    corrected = "save-review: {label: Save, go: decision-details}"
    wrong = "save-review: {label: Save, go: decision-list}"
    missing = "    actions: {}\n"
    routes = "    actions:\n" + route
    draft = original.replace(corrected, wrong).replace(routes, missing)
    stages = [
        ("01-draft", draft, None),
        ("02-retry-save", draft.replace(wrong, corrected), "review-form"),
    ]
    restored = stages[-1][1].replace(missing, routes)
    if restored != original or draft == restored:
        raise ValueError("rehearsal edits no longer match the worked example")
    stages.append(("03-return-added", restored, None))
    for name, document, start in stages:
        path = folder / (name + ".md")
        path.write_text(document, encoding="utf-8")
        view(path, start)

    fresh = folder / "fresh"
    fresh.mkdir()
    copy = fresh / "interaction-model.md"
    shutil.copyfile(folder / "03-return-added.md", copy)
    view(copy)

    # Independent branch, assuming a modeler explicitly confirmed stage 03.
    revised = restored.replace("label: Back, go: decision-list", "label: Back, go: decision-details")
    path = folder / "04-retry-back.md"
    path.write_text(revised, encoding="utf-8")
    view(path, "review-form")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("new_directory", type=Path)
    rehearse(parser.parse_args().new_directory.resolve())
