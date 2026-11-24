# Supporting skills and the discovery workspace

Use a named workspace or the unique matching `state.json` under `.discovery/`.
If several workspaces fit, ask which one to use. Investigation can initialize
a v2 draft from a supplied project brief using `init PATH --project ID --title TITLE`.
Requirements and modeling can work from a draft with sufficient support or
report the missing inputs. Both saved versions can be read and updated within
their existing contracts. Upgrading v1 is an explicit operation.

Run commands from the repository root with the project interpreter. Replace
the sample path and use `.venv\Scripts\python.exe` on Windows.

```sh
.venv/bin/python -m src.adp_discovery show .discovery/example/state.json
.venv/bin/python -m src.adp_discovery report .discovery/example/state.json --format json
.venv/bin/python -m src.adp_discovery save .discovery/example/state.json < candidate.json
```

Use the latest `show` output as the complete candidate, including its revision.
Use the [v2 schema](../schemas/state-v2.schema.json) or the
[v1 schema](../schemas/state.schema.json) for record fields. Preserve existing
IDs, evidence, decisions, profile history, and the saved question batch.
Use lowercase kebab-case IDs, ledger record IDs in `refs`, and saved profile
IDs for dimension references. Use an empty `dimensions` list when no saved
dimension fits. Add new evidence with a precise `source` locator (for example,
a URL and section, a file and page, or a dated stakeholder statement) and
empty `refs`. Corrections are separate evidence records.

Reuse matching open records when logging gaps. Record missing decisions or
evidence as open questions and mark them blocking only if they prevent
readiness. V2 questions require `depends_on`, which may be empty. The saved
question batch is maintained by the interview skill. When material evidence
conflicts, record an open contradiction with the conflicting IDs and affected
decisions. Reopen linked confirmed decisions in the same save and retain their
wording and supporting links. Only stakeholder confirmation can settle a
product decision. Leave unresolved gaps visible for follow-up.

Save only when the ledger needs a change. If the revision is stale, reload,
reconcile the proposed changes by record ID, and recheck the artifact against
the merged state before retrying. Use the revision returned by a successful
save, or the revision read for a run without a save.

Write `investigation.md`, `requirements.md`, or `model.md` beside `state.json`,
identifying the workspace and source revision. Cite ledger IDs for findings,
obligations, and model relationships. The Markdown files are review artifacts.
Use the latest ledger to check whether earlier findings still apply and reuse
any existing requirement IDs for the same obligations. Keep confidence
assessments, requirement details, and model details in their artifacts. The
baseline and its readiness report still derive from the saved ledger.
