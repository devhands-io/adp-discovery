# Installing and updating ADP Discovery

The first version is **0.1.0**. It includes the general base, five specialized products, three overlays, and four local skills. See the [catalog review](catalog-review.md) for selection and deferral decisions.

## Install

Extract `adp-discovery-0.1.0.zip` into a new folder and open its `adp-discovery-0.1.0` directory in Codex Desktop. To use it as a fresh Git repository, run `git init` there. Follow the [virtual environment setup](../README.md#set-up-the-project) from that directory. The following commands assume that environment is active. On Windows use `.venv\Scripts\python.exe` in place of `python` when using the environment directly.

```sh
python -m src.adp_discovery --version
python -m src.adp_discovery validate
python -m src.adp_discovery compose --partial --product reference-guide --tag access-barriers
python -m src.adp_discovery init .discovery/visitor-guide/state.json --project visitor-guide --title "Visitor guide" --artifacts
python -m src.adp_discovery show .discovery/visitor-guide/state.json
python -m src.adp_discovery artifacts .discovery/visitor-guide/state.json --format markdown
```

The first command prints `0.1.0`. The composition includes the source and correction questions and the optional accessible-task question. Initialization creates a draft. Start or resume the interview by naming the state path. Generated Markdown can be redirected into a separate review file.

## Update an existing project

1. Keep the old installation and back up the entire local workspace, including ignored `.discovery/` files and custom templates. Capture the current export for a representative workspace using its original interpreter.
2. Extract the new release alongside the old installation and create its own virtual environment. From the new root run `python -m src.adp_discovery validate --against ../OLD/templates`, substituting the old directory. For a custom catalog, merge its additions in a separate catalog copy, then run `python -m src.adp_discovery --templates MERGED validate --against OLD_CUSTOM`. Investigate every reported change before adoption.
3. Copy the saved workspace into the same relative path in the new installation. Open it with `show`, reproduce the same export and compare its contents. Use `report` for v1/v2 and `artifacts` for v3. Resume in Codex Desktop from the new project root when the checks pass. Keep the previous copy for rollback until review is complete.
4. Use the new catalog for new discoveries. Follow the [migration rules](architecture.md#catalog-evolution) to adopt new questions in an existing profile. A framework update alone requires no state upgrade.

## Version policy and release checklist

Increment the rightmost component for routine releases (0.1.0, 0.1.1, 0.1.2). Increase the minor or major component only on explicit instruction, resetting components to its right. Review breaking changes separately and obtain approval before implementing them. Maintain the schema versions independently.

- Set `VERSION`, update installation examples and release notes, and review candidate dispositions.
- Compare catalogs against the preceding release and explain changes in fresh profiles. Exercise applicable, excluded, and unknown outcomes and a mixed product profile.
- Run catalog validation and the complete unit suite. Rebuild the examples and check reproducibility. Verify each supported saved-state format with a prior workspace.
- From the release commit, build the ZIP with `git archive --format=zip --prefix=adp-discovery-0.1.0/ -o adp-discovery-0.1.0.zip HEAD` (substitute the intended version). Extract into an empty directory, install dependencies in a new environment, validate, initialize, resume and export. Record version, checksum, platform and results.
- Record fresh-host observations for any claimed skill behavior. Record outstanding limitations and separately authorize publication.

## Verification boundaries

The CLI suite exercises file-based discovery and deterministic replays. A fresh Desktop chat must be observed to evaluate dialog delivery, question quality and skill selection. A scored live interview needs stakeholder participation. Accessibility is covered by a discovery prompt for guides and facilities; specialist assessment remains a separate activity. Dependency ranges permit different resolver outcomes on other platforms. The ZIP includes source and local skills and requires a compatible Python environment.
