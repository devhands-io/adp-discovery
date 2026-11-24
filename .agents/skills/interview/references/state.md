# State and CLI reference

Run commands from the repository root with the project's Python interpreter.
See the [README](../../../../README.md) and
[architecture](../../../../docs/architecture.md).

## Start or resume

```sh
.venv/bin/python -m src.adp_discovery init .discovery/meeting-notes/state.json --project meeting-notes --title "Meeting notes skill"
.venv/bin/python -m src.adp_discovery catalog
.venv/bin/python -m src.adp_discovery compose --product agent-skill --partial --no-tag external-actions
.venv/bin/python -m src.adp_discovery show .discovery/meeting-notes/state.json
.venv/bin/python -m src.adp_discovery report .discovery/meeting-notes/state.json --format json
```

Use `show` for the latest revision and the JSON report for coverage, eligible
question IDs, and the saved frontier. Use the named path or identify a unique
workspace under `.discovery/` when resuming. A v1 workspace remains readable.
Run `upgrade PATH --project PROJECT-ID` to use the v2 interview fields in an
existing workspace.

## Save a round

After explicit stakeholder confirmation, compose a profile and append the
resulting object to `profiles` in the candidate state. `--confirmed-by` names
an evidence record in that candidate. Repeat `--secondary-product`, `--tag`,
`--no-tag`, or `--confirmed-by` as needed. Omit unknown tags. Compose from
the intended catalog checkout and review unrelated catalog changes before
including them in an ongoing workspace.

```sh
.venv/bin/python -m src.adp_discovery profile --product agent-skill --no-tag external-actions --confirmed-by owner-confirms-type
.venv/bin/python -m src.adp_discovery save .discovery/meeting-notes/state.json < candidate.json
```

Start from the latest `show` output. Keep its revision, project ID, and existing
profile snapshots. Update the summary, ledger, and frontier by ID. Save the
complete candidate through stdin. After a stale revision error, reload, merge
by ID, and recalculate the batch.

Records have `id`, `kind`, `status`, `text`, `dimensions`, and `refs`. Use
stable lowercase kebab-case IDs. References are record IDs, and dimensions
come from a saved profile.

| Kind | Fields and lifecycle |
| --- | --- |
| Evidence | `recorded` with a source and empty refs. Add a separate record for corrections. Existing evidence can gain dimension links. |
| Preference | `recorded`. Link evidence of the stakeholder's preference. |
| Decision | `proposed`, `confirmed`, `reopened`, or `superseded`. Confirmation needs a dimension and evidence. Tag support with the same dimension for coverage. Keep established wording. A superseded decision needs a resolution identifying the replacement. |
| Assumption, risk, question, contradiction | `open` or `resolved`. Resolution needs a reason. Questions and risks require `blocking`. Open contradictions must reopen linked confirmed decisions. |
| Question prerequisites | Set `depends_on` to prerequisite question IDs or an empty list. Set `deferred: true` on an open question to leave it out of the batch. Remove the field when reactivating or resolving the question. |

Set `frontier` to an ordered list of up to three eligible open question IDs.
A scoped question is eligible when one of its dimensions currently applies.
Every prerequisite must be resolved. Use an empty frontier when there is no
question to ask next.

## Export for review

```sh
.venv/bin/python -m src.adp_discovery report .discovery/meeting-notes/state.json > .discovery/meeting-notes/baseline.md
```

The report distinguishes applicable gaps, unknown applicability, and confirmed
exclusions. The JSON report includes blocker IDs and the current and eligible
question IDs. Readiness is preliminary and requires stakeholder review.
