"""Command-line tools for the discovery interview skill and local review."""

import argparse
import json
import sys
from pathlib import Path

from .artifact_markdown import render as artifact_markdown
from .artifacts import project_artifacts
from .core import ROOT, Catalog, read_json
from .discovery import review_subject
from .interaction import render as render_interaction
from .report import markdown, readiness
from .state import initialize, initialize_draft, load_state, save, upgrade


def parser():
    cli = argparse.ArgumentParser(prog="adp-discovery")
    cli.add_argument("--version", action="version", version=(ROOT / "VERSION").read_text().strip())
    cli.add_argument("--templates", type=Path, default=ROOT / "templates", help="catalog directory")
    commands = cli.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="validate the catalog")
    validate.add_argument("--against", type=Path, metavar="OLD_TEMPLATES", help="check existing catalog contracts")
    commands.add_parser("catalog", help="list supported products and tags")
    for name in ("compose", "profile", "init"):
        command = commands.add_parser(name, help={
            "compose": "inspect a composed discovery checklist",
            "profile": "compose a profile snapshot with explicit applicability",
            "init": "create discovery state and save the checklist",
        }[name])
        command.add_argument("--tag", action="append", default=[])
        if name != "compose":
            command.add_argument("--artifacts", action="store_true", help="use version 3 artifact and readiness state")
        if name == "init":
            mode = command.add_mutually_exclusive_group(required=True)
            mode.add_argument("--product", help="create a confirmed version 1 workspace")
            mode.add_argument("--project", help="create a draft version 2 workspace with this stable ID")
            command.add_argument("state", type=Path)
            command.add_argument("--title", required=True)
        else:
            command.add_argument("--product", required=True)
            command.add_argument("--secondary-product", action="append", default=[], help="add a product template")
            command.add_argument("--no-tag", action="append", default=[], help="declare a tag absent in partial composition")
            if name == "compose":
                command.add_argument("--partial", action="store_true", help="leave undeclared tags unresolved")
            else:
                command.add_argument("--confirmed-by", action="append", default=[], metavar="EVIDENCE_ID")
    for name, help_text in (
        ("show", "load and validate saved state"),
        ("save", "save a complete state document from standard input"),
        ("upgrade", "explicitly upgrade a saved workspace in place"),
        ("report", "render the discovery baseline and readiness"),
        ("artifacts", "generate the seven discovery artifacts from one saved revision"),
        ("review-subject", "identify the saved content to review or authorize for deferral"),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("state", type=Path)
        if name == "report":
            command.add_argument("--format", choices=("markdown", "json"), default="markdown")
        elif name == "artifacts":
            command.add_argument("--format", choices=("markdown", "json"), default="json")
        elif name == "upgrade":
            command.add_argument("--project", help="project ID for a version 1 workspace")
            command.add_argument("--to", type=int, choices=(2, 3), default=2)
    preview = commands.add_parser("interaction-view", help="render a portable Markdown walkthrough")
    preview.add_argument("model", type=Path)
    preview.add_argument("output", type=Path)
    preview.add_argument("--start", help="open the changed screen for a retry")
    return cli


def run(options):
    if options.command == "interaction-view":
        return render_interaction(options.model, options.output, options.start)
    if options.command == "show":
        return load_state(options.state)
    if options.command == "save":
        return save(options.state, read_json(sys.stdin))
    if options.command == "upgrade":
        return upgrade(options.state, options.project, target=options.to)
    if options.command == "report":
        state = load_state(options.state)
        if state["version"] == 3:
            bundle = project_artifacts(state)
            return artifact_markdown(bundle) if options.format == "markdown" else bundle["discovery_readiness_report"]
        return markdown(state) if options.format == "markdown" else readiness(state)
    if options.command == "artifacts":
        bundle = project_artifacts(load_state(options.state))
        return artifact_markdown(bundle) if options.format == "markdown" else bundle
    if options.command == "review-subject":
        state = load_state(options.state)
        if state["version"] != 3:
            raise ValueError("review subjects require version 3; use upgrade --to 3")
        return {"review_subject": review_subject(state),
                "condition_subject": review_subject(state, include_conditions=False)}

    if options.command == "init" and options.project is not None:
        if options.tag:
            raise ValueError("record classification tags in a confirmed profile after draft initialization")
        return initialize_draft(options.state, options.title, options.project, artifacts=options.artifacts)

    catalog = Catalog(options.templates)
    if options.command == "validate":
        if options.against:
            catalog.check_compatibility(Catalog(options.against))
        return "Catalog valid.\n"
    if options.command == "catalog":
        return {"products": sorted(catalog.products), "tags": catalog.tags}
    if options.command == "init":
        if options.artifacts:
            raise ValueError("use --project with --artifacts to initialize a draft")
        profile = catalog.compose(options.product, options.tag)
        return initialize(options.state, options.title, profile)
    if options.command == "profile":
        return {**catalog.compose(
            options.product, options.tag, secondary_products=options.secondary_product,
            absent_tags=options.no_tag, snapshot=True, readiness=options.artifacts,
        ), "confirmed_by": options.confirmed_by}
    return catalog.compose(
        options.product, options.tag,
        secondary_products=options.secondary_product, partial=options.partial, absent_tags=options.no_tag,
    )


def main():
    options = parser().parse_args()
    try:
        result = run(options)
    except (ValueError, OSError) as error:
        print(f"adp-discovery: {error}", file=sys.stderr)
        return 1
    if isinstance(result, str):
        print(result, end="")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
