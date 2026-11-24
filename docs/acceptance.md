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
| Checkpoint | An empty batch with unresolved required gaps remains unready. Stakeholders review evidence and approve the baseline independently of coverage. |
| Legacy compatibility | The v1 pilot export is unchanged. Explicitly upgrading a copy preserves the checklist, record IDs, and blocker findings. Unknown template versions are visible in the upgraded state. |

## Stakeholder question delivery

Start a fresh interview with a product idea whose classification or tags need
confirmation. Use a separate discovery workspace for each run.

| Session | Acceptance condition |
| --- | --- |
| Built-in question dialog available | The first confirmation appears in the dialog without a duplicate question in chat. Submit a correction through the dialog and verify that the saved profile reflects the reply. The next unresolved question also appears in a dialog. |
| Built-in question dialog unavailable | The agent briefly explains the fallback and asks in chat. Reply in chat and verify that the saved profile reflects the reply. |
| Dialog dismissed or unanswered | Leave the first confirmation unanswered. Verify that the draft exists, keeps the same question open, and has no confirmed profile. Resume from the same path and verify that it still awaits an explicit reply. |
