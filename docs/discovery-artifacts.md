# Discovery artifacts and readiness

Version 3 workspaces store the structured inputs for seven discovery
artifacts. Generate the canonical JSON bundle or a Markdown review copy from
a single saved revision. The bundle records the project, state version,
revision, profile index, and SHA-256 digest of the source state.

```sh
.venv/bin/python -m src.adp_discovery init .discovery/example/state.json --project example --title "Example" --artifacts
.venv/bin/python -m src.adp_discovery profile --product agent-skill --no-tag external-actions --confirmed-by type-confirmation --artifacts
.venv/bin/python -m src.adp_discovery show .discovery/example/state.json
.venv/bin/python -m src.adp_discovery save .discovery/example/state.json < candidate.json
.venv/bin/python -m src.adp_discovery artifacts .discovery/example/state.json
.venv/bin/python -m src.adp_discovery artifacts .discovery/example/state.json --format markdown
.venv/bin/python -m src.adp_discovery report .discovery/example/state.json --format json
```

Compose and save a profile after the stakeholder confirms the classification.
Append the result to the candidate's `profiles` and include the referenced
confirmation evidence in its ledger. Each new snapshot pins the composed
readiness criteria and their applicability. Saving structured records uses
the same revision check and atomic write as saving an interview round.

## Canonical formats

| JSON section | Contents |
| --- | --- |
| `discovery_brief` | Title, saved classification, claims by section, assumptions, and preferences. Material claims carry supported finding IDs or a reason they are uncertain. |
| `decision_register` | Ledger decisions, source and confirmation references, finding IDs, support status, and replacement links. |
| `requirements_baseline` | Requirement IDs, obligations, lifecycle, source decisions, justification, and observable acceptance outcomes with stable IDs. |
| `evidence_register` | Source locators and recorded statements, plus findings, their evidence IDs, assessment, rationale, and recorded disputes. |
| `risk_register` | Ledger risks with impact scope, affected requirement IDs, severity, and evidenced disposition. |
| `open_questions` | Open ledger questions with impact scope, requirement IDs, blocking and deferral state, prerequisites, and the current batch. |
| `discovery_readiness_report` | Status, criterion results and reasons, contradictions, review subjects, and recorded assessments, approvals, and conditions. |

The [state schema](../schemas/state-v3.schema.json) defines the inputs.
The [bundle schema](../schemas/artifact-bundle.schema.json) defines the
output. Cross-schema references resolve to the local files through the
repository's schema registry. Registered URI names identify schemas for
resolution.

## Traceability and judgment

1. Add an evidence record with what the source actually says and a precise
   locator. Record a finding with evidence IDs, an assessment of
   `supported`, `uncertain`, or `disputed`, and the rationale for that
   assessment.
2. Link findings to the decisions they support in `discovery.decision_links`.
   Keep ledger references to direct confirmation evidence. When a decision is
   superseded, put the successor in its ledger references and use
   `superseded_by` in its structured link.
3. Link each active requirement to confirmed, supported decisions and record
   why they justify the obligation. Give each acceptance criterion an
   observable outcome and relevant test conditions or method. Use
   `proposed` for unsettled obligations and retain replaced or withdrawn
   obligations with their rationale and links.
4. Add an impact record for each risk or question whose affected requirements
   are known. Use `project` for cross-cutting impacts and `unknown` when
   impact is still under investigation. For a critical risk, record an
   evidenced mitigation or avoidance, or explicit acceptance by the
   stakeholder role responsible for baseline review.
5. Write material brief claims under `discovery.claims`. Link supporting
   findings and record any uncertainty explicitly. Keep source statements and
   agent assessments attributable to their sources.

The gate verifies structure, references, coverage, and recorded outcomes.
Agents assess evidence and requirement justification. Stakeholders confirm
decisions and provide or designate the required reviews and authorizations.
An open contradiction disputes the findings that depend on its evidence.
Reopened and superseded decisions lose their ability to justify an active
requirement. The report identifies the affected IDs. Readiness describes the
discovery handoff. Legal validity and safety certification require their own
qualified processes.

## Catalog criteria and readiness outcomes

Templates may declare an ordered `readiness_criteria` list. Each entry has a
globally unique ID, description, checker kind, and `on_failure` policy, with an
optional `applies` rule. The same three-valued tag and product rules used for
dimensions determine applicability. A `dimension` check names a dimension in
its template or the base. An `assessment`, `review`, or `approval` names
the required role. Reviews and approvals are mandatory when applicable.
Reserve `baseline-review` for the unconditional stakeholder review in the
base. The agent-skill profile adds a handoff replay assessment. Facility
adds a design handoff review. Process adds a controls review and a case
replay assessment. Contract adds a drafting handoff review and a qualified
legal review when a material issue affects drafting. Evaluation adds a plan
review, and Security adds an information-handling approval.

| Outcome | Rule |
| --- | --- |
| `ready` | All mandatory checks pass and there are no outstanding conditions. |
| `conditionally-ready` | All mandatory checks pass. Each failed deferrable criterion has a current stakeholder-authorized condition, owner, rationale, and completion rule. |
| `not-ready` | At least one mandatory check fails or remains unresolved, or a deferrable failure lacks a current authorized condition. |

Optional dimension gaps and nonblocking questions appear in the report.
Questionnaire completion and the question batch do not determine the status.
Unknown applicability blocks when it affects a mandatory dimension or
criterion. An open contradiction defaults to critical until assessed.
A risk with a blocking flag and no severity assessment also defaults to
critical. An independently blocking open ledger item still needs resolution.

## Record a review or authorized condition

1. Save the content being reviewed. Run `review-subject PATH` to obtain its
   `review_subject` and `condition_subject`.
2. For a deferrable criterion, obtain explicit authorization for the owner,
   completion condition, and rationale. Append a condition with its stable
   ID, criterion ID, `subject` set to `condition_subject`, and the
   authorizing actor, role, and source. Save it before requesting baseline
   review. A new condition for the same criterion supersedes the earlier
   condition for evaluation.
3. Obtain the required outcome and source from the appropriate reviewer or
   record an explicit sourced agent assessment where the criterion calls for
   one. Append an attestation with a stable ID, criterion ID, `subject` set
   to the current `review_subject`, actor, role, source locator, outcome,
   and rationale. Use `passed` or `failed` as explicitly recorded.
4. Save and regenerate the report. The latest attestation for the required
   role on that subject governs the check. Attestations and conditions are
   append-only.

Review subjects include the active profile, saved ledger and structured
content, and any recorded conditions. Changing that content requires a fresh
review. The state revision, question batch, and attestation history are
excluded from the review subject. The condition subject also excludes the
conditions themselves, so adding one condition leaves the others current.

## Migration and examples

Run `upgrade PATH --to 3` for v2. Supply `--project ID` when upgrading v1.
The upgrade preserves the ledger and available profile history. Append a
fresh profile with `profile --artifacts` after confirming the classification
and criteria in use. Add structured findings and requirements from existing
source records. Missing provenance, reviews, and approvals remain visible
as gaps until explicit evidence is available. V1 and v2 keep their preliminary
report format. In v3, `report` renders the same Markdown as `artifacts`,
and `report --format json` returns the readiness section of the bundle.

The checked-in examples cover [ready](../examples/milestone6/ready.md),
[conditionally ready](../examples/milestone6/conditionally-ready.md), and
[not ready](../examples/milestone6/not-ready.md). The first two use synthetic
sources and reviews. The third replays the existing self-discovery pilot.

```sh
.venv/bin/python -m examples.milestone6.replay --output /tmp/discovery-examples
.venv/bin/python -m examples.milestone6.replay --output /tmp/discovery-examples --format json
.venv/bin/python -m src.adp_discovery validate
.venv/bin/python -m unittest discover -s tests -v
```
