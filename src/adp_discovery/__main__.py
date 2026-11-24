"""Command-line tools for the Codex interview skill and local review."""

import argparse
import json
import sys
from pathlib import Path

from .core import ROOT, Catalog, read_json
from .report import markdown, readiness
from .state import initialize, load_state, save


def parser():
    cli = argparse.ArgumentParser(prog="adp-discovery")
    cli.add_argument("--templates", type=Path, default=ROOT / "templates", help="catalog directory")
    commands = cli.add_subparsers(dest="command", required=True)
    commands.add_parser("validate", help="validate the catalog")
    commands.add_parser("catalog", help="list supported products and tags")
    for name in ("compose", "init"):
        command = commands.add_parser(name, help={
            "compose": "show the checklist for a confirmed classification",
            "init": "create discovery state and save the checklist",
        }[name])
        command.add_argument("--product", required=True)
        command.add_argument("--tag", action="append", default=[])
        if name == "init":
            command.add_argument("state", type=Path)
            command.add_argument("--title", required=True)
    for name, help_text in (
        ("show", "load and validate saved state"),
        ("save", "save a complete state document from standard input"),
        ("report", "render the discovery baseline and preliminary readiness"),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("state", type=Path)
        if name == "report":
            command.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return cli


def run(options):
    if options.command == "show":
        return load_state(options.state)
    if options.command == "save":
        return save(options.state, read_json(sys.stdin))
    if options.command == "report":
        state = load_state(options.state)
        return markdown(state) if options.format == "markdown" else readiness(state)

    catalog = Catalog(options.templates)
    if options.command == "validate":
        return "Catalog valid.\n"
    if options.command == "catalog":
        return {"products": sorted(catalog.products), "tags": catalog.tags}
    profile = catalog.compose(options.product, options.tag)
    if options.command == "init":
        return initialize(options.state, options.title, profile)
    return profile


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
