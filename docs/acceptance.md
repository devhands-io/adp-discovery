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

## Interview behavior

Give a fresh interviewer a product brief with a material factual claim and an
accessible source that conflicts with it. Check that it locates and cites the
source, distinguishes observed facts from intended behavior, and recommends
a decision with a reason and consequence. An answer that opens a material
boundary should produce a follow-up, even in a covered dimension.

Request a baseline while a branch is deferred, then resume from the saved
state. The interview closes only after all material branches are accounted
for and the stakeholder confirms the recap. A later material correction
requires renewed confirmation and preserves the original evidence. See the
[isolated pilot instructions](../examples/meeting-notes/pilot.md#fresh-interviewer-pilot).

## Template schema and composition

| Scenario | Acceptance condition |
| --- | --- |
| Versioned catalog | Every template declares version 1. Validation identifies the template and field when a version is missing or unsupported, or when a rule uses an invalid shape or reference. |
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

## Milestone 6 artifacts and readiness

Rebuild the [three example reports](discovery-artifacts.md#migration-and-examples)
from saved revisions. The automated suite compares their bytes and replays
the meeting decision register through explicit migration to v3.

| Scenario | Acceptance condition |
| --- | --- |
| Single source revision | The seven sections share source identity, profile, and digest. Markdown and JSON resolve the same IDs and use the same status. |
| Traceable claims and obligations | The evidence-to-acceptance chain resolves to correctly typed entities. Unsupported material claims and requirements block. Superseded history remains traceable. |
| Incomplete discovery | Required coverage, critical contradictions, critical risks without disposition, and missing or stale mandatory reviews surface as blockers even with an empty batch. |
| Product and overlay policy | Applicable, excluded, and unknown criteria are visible. An approval has the configured role and current subject. Live catalog edits leave an earlier export reproducible. |
| Authorized conditions | A conditional result has a current stakeholder-authorized owner, rationale, and completion condition. Missing or stale authorization blocks. |
| Compatibility | V1 and v2 reports keep their earlier formats. Migration retains records and shows gaps for unavailable findings, criteria, and approvals. |

## Milestone 7 product-agnostic validation

Replay the [facility, process, and contract pilots](../examples/milestone7/pilot.md).
The replay covers sourced classification and applicability, saved interview
rounds, investigation, two traceable obligations per product, optional
models, and the v3 artifact and readiness workflow.

| Scenario | Acceptance condition |
| --- | --- |
| Facility renovation | Unresolved owner approval applicability blocks with an empty frontier. An alternate structural option activates a required condition assessment. The facilities reviewer gates design handoff. |
| Invoice exception process | Evaluation and Security apply. Missing handoff ownership and a critical payment-control gap block. A noncritical replay gap is conditional only with a current stakeholder authorization and all mandatory reviews. |
| Services agreement | Security applies to restricted access records. Missing delegation evidence blocks when delegated authority applies. A material issue affecting drafting requires a current qualified legal review. The exports identify drafting handoff and the separate pre-signature review. |
| Contradictions | Each affected decision reopens, the linked obligation loses support, and reconciliation preserves both reports and the clarification. |
| Combined profile | Facility with a separately scoped operating process includes both sets of domain questions and one copy of each applicable overlay. |
| Saved rounds and exports | A fresh CLI process reads the saved frontier. The two export formats share revision, digest, and status. All three model forms cite ledger IDs, and the legal redline case skips a new model. |
| Fresh-host pilot | With explicit approval to start each live interview, follow the pilot rubric and record relevance, repeated prompts, what the host needs to resume, and any missed domain or evidence questions. Score host behavior separately from fixture outcomes. |

## Milestone 8 expansion and skill evaluation

Use the [release checklist](releases.md) and the following fictional guide scenario. Evaluate in fresh Desktop chats using disposable workspace state. Record pass, partial or fail with a prompt or record ID. The automated checks exercise catalog behavior; score the live workflow after approval to start an interview.

| Skill | Input and observable outcome |
| --- | --- |
| Interview | A library maintains a visitor guide. Ask who resolves conflicts between the branch bulletin and the central directory. With an identified screen-reader barrier, the task-completion question applies. After confirmation, resume the saved next question in a fresh chat without repeating it. |
| Investigate | Supply a dated branch closure notice contradicting a confirmed opening-time decision. Link the evidence, reopen the decision, preserve the original text and keep the saved question batch. |
| Define requirements | After the stakeholder confirms who issues corrections, derive a requirement with an observable reader-notification check. Flag the opening-time decision while it remains disputed. |
| Model product | Given separately owned publication and correction steps, represent their handoff and cite ledger IDs. If all ownership is already clear and no model helps, record the reason to skip it. |

To exercise independent composition, add a facility as a secondary product only when physical work is also in scope. Both products then share one Accessibility question. A process-only profile excludes that overlay; an unknown barrier in a guide remains unresolved. A facility's circulation question remains under facility ownership.

The [single-person interaction-model pilot](../examples/interaction-model/pilot.md) exercises chat corrections, omission review, version-specific confirmation and replay from a standalone Markdown copy.

With two proposed decisions, each row has a Review action. Selecting either row opens its own populated form. Save displays the selected decision's details, and Return to list displays both rows again.

Edit the second decision title and select Save. Its details, list row and reopened form must show the new title. Edit again and select Back. Reopening must show the last saved title. The first decision retains its original title throughout.

Start a named task, follow the single visible instruction, and reach end-of-task feedback. When two rows offer the same action, the instruction identifies the row. Missing actions and alternate routes must not report success. Browser Back restores the prior instruction.

In the news blog example, the third story is absent before publication. Publishing an authored title reveals it on all three role-specific indexes. Visitors read it, its author can edit it, and a special editor can edit it.

Complete one scenario and leave another partway through. Reopen the walkthrough in the same browser and verify the completed count, Replay, and Resume at the saved step. After changing a single scenario route, verify Retry needed on that scenario and preserved status on unaffected scenarios. Following a different route must not grant completion.

Enter a scenario note and notes on two guided screens, return to the list, reload, and copy. Verify that each appears once with the correct scenario, screen and step, and that blank or deleted notes are omitted. Verify manual selection when clipboard access is declined.

Each scenario has the same one-based number in the list, its on-screen guide, and its exported notes. Numbers follow the order in the Markdown model.

After agreeing the blog scenarios, review the article and author model with the modeler. Keep proposals pending until explicitly accepted. During screen review, removing the agreed publication date from the reader’s article must surface a coverage gap even when every navigation step still works. For a scenario without meaningful domain data, record the reason for skipping this review.
