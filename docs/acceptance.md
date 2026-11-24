# Acceptance scenarios

The tests exercise deterministic behavior independently of the interview skill.
Use the supplied pilot as a worked replay and the cases below for live review
of the interview in an agent host that can load the skill.

| Scenario | Acceptance condition |
| --- | --- |
| Simple agent skill | An interview covers invocation, outputs, and handoff. The Evaluation overlay applies and readiness links each covered dimension to a decision and evidence. |
| Skillset with overlapping responsibilities | The interview identifies which skill owns each trigger or output and records a conflict if two claim ownership. |
| Residential building | The generic checklist supports intended occupants, site constraints, and approval dependencies. The interviewer asks about physical constraints based on context and records missing approvals as gaps. |
| Organizational constitution | The generic checklist supports authority, rights, and amendment questions through the stakeholder context. Unsettled authority is visible in the ledger. |
| Legal service contract | Obligations, remedies, and jurisdiction can be recorded on the generic profile. The interview records unresolved legal review as a blocking question if needed. |
| Incomplete idea | A sparse state exposes coverage gaps. The interview starts from intent and follows the most consequential unknown rather than assuming answers. |
| Contradictory answers | A later answer reopens a confirmed decision. The report names the contradiction and reopened decision until the stakeholder resolves it. |
| Interrupted interview | A separate process or fresh chat loads the saved revision and decision IDs before continuing. An outdated write is rejected and preserves the newer state. |
| Invalid catalog | Malformed templates, missing rule references, and duplicate dimensions fail with readable messages. Identical classifications yield the same ordered checklist. |

## Template schema and composition

| Scenario | Acceptance condition |
| --- | --- |
| Versioned catalog | All four templates declare version 1. Validation identifies the template and field when a version is missing or unsupported, or when a rule uses an invalid shape or reference. |
| Multiple products | A fixture catalog composes the base, primary product, secondary products in input order, and applicable overlays in filename order. A secondary product can satisfy an overlay rule. Every dimension identifies its source template. |
| Overlapping declarations | Repeated dimension IDs identify both declarations. Incompatible definitions identify the fields that differ. Duplicate template IDs and repeated product selections fail validation. |
| Partial tag facts | For `agent-skill` with undeclared tags, Evaluation applies and Security is unresolved. Declaring either Security tag present applies Security. Declaring both absent excludes it. Contradictory declarations fail with a message naming the tag. |
| Conditional dimensions | A dimension follows its template and its own rule. An unresolved condition reports missing facts. A false condition excludes the dimension, including when another condition is unresolved. An applicable optional dimension keeps `required: false`. |
| Confirmed profile and pilot | Existing single-product `compose` and `init` commands produce the version 1 checklist shape. The checked-in pilot state still reproduces its Markdown baseline. |

## Persistent interview

Replay the [meeting decision register pilot](../examples/meeting-notes/pilot.md).

| Scenario | Acceptance condition |
| --- | --- |
| Draft and fresh thread | Start from a brief and interrupt before classification. A fresh thread loads the draft, presents the current question, and reuses intent already supplied. Repeat after confirming the product. |
| Unknown and inapplicable dimensions | Confirm the product while sensitivity is unknown. Security is absent from the active checklist and its dimensions show unknown applicability. Confirming sensitive inputs makes the related questions eligible after prerequisites resolve. Confirming public inputs and no external actions makes Security inapplicable. |
| Distinct records | Evidence, preferences, assumptions, proposals, and explicit decisions retain distinct types or statuses across rounds. Recommendations stay proposed when the stakeholder has only expressed a preference. |
| Dependency and contradiction | A blocked or deferred question stays out of the batch. Conflicting evidence reopens the affected decision and surfaces a blocker. Resolving the conflict preserves both statements and the superseded wording. |
| Checkpoint | An empty batch with unresolved required gaps remains unready. The v2 Markdown report explains draft, gaps, and ready statuses and identifies stakeholder approval as a separate step. |
| Legacy compatibility | The v1 pilot export is unchanged. Explicitly upgrading a copy preserves the checklist, record IDs, and blocker findings. Unknown template versions are visible in the upgraded state. |

## Stakeholder question delivery

Start a fresh interview with a product idea whose classification or tags need
confirmation. Use a separate discovery workspace for each run.

| Session | Acceptance condition |
| --- | --- |
| Built-in question dialog available | Each round presents its questions once in the dialog. Submit a correction and verify that the saved profile reflects it. The next unresolved question also appears once in a dialog. Chat can acknowledge the round. |
| Built-in question dialog unavailable | The agent briefly explains the fallback and asks in chat. Reply in chat and verify that the saved profile reflects the reply. |
| Dialog dismissed or unanswered | Leave the first confirmation unanswered. Verify that the draft exists, keeps the same question open, and has no confirmed profile. Resume from the same path and verify that it still awaits an explicit reply. |

## Live pilot review

Before a live pilot, agree on the product, rubric, and intended outputs, then
get approval to begin the interview. Approval to maintain the framework
covers maintenance. During the interview, reuse earlier answers and ask one
focused question or a small related batch.

For a Claude Code pilot, open the project folder and verify that `/interview`
appears in the slash menu. Use the README's Claude Code prompts to start and
resume. Check that the first invocation creates the requested workspace and
the second loads the saved question batch.

Rate each item as pass, partial, or fail and cite an observation. A pass meets
the check below, a partial leaves part unverified or unmet, and a fail records
a direct miss. Baseline coherence, traceability, and applicability must pass
for pilot acceptance.

| Criterion | What to check |
| --- | --- |
| Baseline coherence | The brief, decision register, and preliminary readiness describe the same product and expose material gaps. |
| Traceability | Confirmed decisions link to stakeholder evidence. Assumptions and risks are explicit. |
| Applicability | The profile matches confirmed facts. Composition checks exercise applicable, unresolved, and excluded cases. |
| Relevance | Questions help settle a decision or close a material evidence gap. |
| Clarity | The stakeholder can understand each question and answer it in their own terms. |
| Redundancy | The interviewer reuses prior answers and delivers each prompt once per round. |
| Missing coverage | The interview covers required topics or records the remaining gaps. |
| Premature design assumptions | Questions establish outcomes and constraints before settling design choices. |
| Context efficiency | Each round is short, and the saved batch is sufficient to resume. |
| Framework findings | The report distinguishes product findings from framework defects and links proposed fixes to observations. |

Save the traceable state and generate the baseline from it. Keep the scored
review separate from product findings and obtain approval before implementing
any proposed framework fixes.

## Supporting skills

Run each invocation in a fresh Codex chat in the project and name the exact
state path. Use disposable workspaces and check the artifacts against the saved
revision with `show` and `report --format json`.

| Invocation | Acceptance condition |
| --- | --- |
| `$investigate` against the meeting-register workspace after the sensitivity decision, with the records policy from the next round supplied as a source | Saves the policy evidence and an open contradiction, reopens `infer-owners` while preserving its text and evidence, and leaves `handling-review` in the saved batch. `investigation.md` gives the source locator, confidence and rationale, and the unresolved policy question. |
| `$define-requirements` against the meeting-register workspace before the conflict, then again after investigation | Produces IDs, evidence and decision links, and an observable check for the confirmed owner rule. Flags that rule as disputed on rerun and preserves the IDs of unchanged obligations. Preferences and proposals remain review inputs. Missing decisions stay visible. |
| `$model-product` against a `general` residential building workspace with a confirmed relationship between the entry and shared space | Produces a space adjacency model with ledger links and marks unconfirmed relationships. In a separate run where a model would add no value, explains the reason and leaves the workspace without a new model. |

Run investigation in a draft workspace with a source that answers one question
and leaves another open. Verify evidence and gaps are saved before
classification. Use a copy of the legacy pilot to check that the supporting
skills can read v1 without upgrading it automatically.
For the requirements rerun, include a second confirmed obligation outside the
conflict, such as producing a local draft without taking external actions.
