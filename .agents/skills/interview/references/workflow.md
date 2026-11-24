# Interview workflow reference

Run commands from the repository root with its Python environment active. The
[README](../../../../README.md) covers setup and
[architecture](../../../../docs/architecture.md) defines the state contract.

## Start or resume

```sh
python -m src.adp_discovery catalog
python -m src.adp_discovery compose --product agent-skill --tag sensitive-data
python -m src.adp_discovery init .discovery/example/state.json --title "Example skill" --product agent-skill --tag sensitive-data
python -m src.adp_discovery show .discovery/example/state.json
```

Use tag definitions from `catalog` to explain why the proposed tags apply.
Clarify unknown tag facts that could change the checklist before initialization.
Use the catalog order as a checklist order and prioritize blockers independently.
For a new thread, obtain the workspace path or find the matching local slug and
load persisted state before relying on recollection.

## Save after an answer

Build the complete candidate from the latest `show` output. Keep the revision
and profile intact, update the summary where appropriate, and add or update
records. Pass the candidate on standard input. A stale revision requires a
fresh load and a merge by record ID.

```sh
python -m src.adp_discovery save .discovery/example/state.json < candidate.json
```

Each record has a permanent `id`, `kind`, `status`, `text`, `dimensions`,
and `refs`. Use stable lowercase kebab-case IDs. References are record IDs.
Dimensions come from the saved checklist.

- **Evidence** uses status `recorded`, requires a source, and has empty refs.
  Summarize what was observed and where it came from. A stakeholder statement is
  evidence of their stated intent. Use minimal necessary detail.
- **Decisions** use `proposed`, `confirmed`, `reopened`, or `superseded`.
  A confirmed decision links to a dimension and recorded evidence. For coverage,
  tag that evidence with the same dimension. If a stakeholder replaces a
  previously confirmed decision, preserve its text, supersede it with a
  resolution naming the replacement, and add the new decision.
- **Assumptions, risks, questions, and contradictions** use `open` or
  `resolved`. Supply a resolution when closing a record. Risks and questions
  require a boolean `blocking` field. Mark one blocking if it prevents a
  defensible baseline.
- **Contradictions** reference the related decision or at least two conflicting
  records. Preserve both statements as evidence where available. In the same
  save, reopen each confirmed decision referenced by an open contradiction.
  Restore confirmation only when the conflict is resolved and the evidence
  supports the original decision.

## Export for review

```sh
python -m src.adp_discovery report .discovery/example/state.json --format json
python -m src.adp_discovery report .discovery/example/state.json > .discovery/example/baseline.md
```

The report reads state and includes a brief, decisions, open questions, other
ledger records, and evidence-backed readiness. Review the substance with the
stakeholder, especially evidence quality and unresolved nonblocking issues.
