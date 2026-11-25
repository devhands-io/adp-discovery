# Milestone 7 product-agnostic validation

These three fictional scenarios exercise the same discovery state and artifact
workflow. The community center pilot concerns renovating an identified site.
The process pilot concerns invoice handling across two teams. The contract
pilot concerns a drafting handoff for maintenance services. Its counsel
records and control documents are fictional fixture inputs.

From the repository root, generate the JSON bundle and Markdown baseline for
each checkpoint and the optional model for each completed scenario.

```sh
.venv/bin/python -m examples.milestone7.replay --output /tmp/discovery-milestone7
```

The replay stores working state in temporary workspaces. Each generated
baseline and JSON bundle identify the saved revision and digest. Run the
command again to reproduce those exports.

| Product | Incomplete checkpoint | Contradictory checkpoint | High-risk checkpoint | Ready checkpoint |
| --- | --- | --- | --- | --- |
| [Facility](facility.yaml) | Owner approval applicability is unknown. | A logistics sketch appears to close the selected public entrance. | A new structural option lacks qualified assessment. | The facilities lead reviews site, access, continuity, and approval dependencies for design handoff. |
| [Process](process.yaml) | Procurement handoff ownership lacks evidence. | A manager's account conflicts with the documented payment control. | A fallback path bypasses independent verification. | The process owner reviews the controls and a walkthrough exercises normal and exceptional cases. An authorized month-end replay gap also demonstrates conditional readiness. |
| [Contract](contract.yaml) | The proposed signer lacks evidence of delegation. | The service schedule and onboarding brief specify different deadlines. | A supplier redline raises liability and jurisdiction issues that require a qualified disposition for drafting. | The drafting owner confirms completeness, including disposition of material drafting issues and the review required before signature. |

Each contradictory checkpoint retains the original decision and both sources.
The ready checkpoint carries the sponsor's clarification and the original
requirements. The later high-risk checkpoint shows that the earlier positive
review becomes stale. Current reviews of the unaffected criteria leave the
domain-specific gate and unresolved risk blocking.

## Architectural observations from replay

| Check | What the replay shows |
| --- | --- |
| Software assumptions | The facility walkthrough uses plans and site records. The process uses masked case records and the control policy. The contract uses a term sheet, delegation record, and recorded review. All three can produce observable acceptance checks. |
| Shared requirements | Intent, scope, stakeholders, success, constraints, and stakeholder baseline review apply across the three examples. Each baseline carries two grounded obligations. Site conditions, payment release controls, and signing authority stay within their applicable scopes. |
| Overlap | Facility owns the path for owner or authority approval of physical work. Process owns work handoffs and disposition. Contract owns signing authority and legal review. Security owns authorization for in-scope actions and the handling of restricted information. Evaluation reviews the process's proposed cases, and the process criterion assesses the walkthrough result. |
| Composition | The facility pilot's scope excludes external actions and sensitive information. The payment process triggers Security through external actions, and the contract triggers it through sensitive records. Evaluation applies to the repeatable process. A mixed profile composes both product checklists and each applicable overlay once. |
| Readiness boundaries | The facility report supports design handoff. The contract report supports drafting handoff and records the review required before signature. The process demonstrates the difference between a deferrable replay gap and a blocking payment-control risk. |
| Review scope | A substantive update stales every applicable review bound to the earlier subject. The stale checkpoint invalidates 2 facility, 5 process, and 4 contract attestations on the previously ready subject. |
| Optional modeling | The completed pilots use an adjacency table, a swimlane transition table, and an obligation matrix. The contract redline needs qualified review. The prior model still describes the originally supported service obligations, so the high-risk checkpoint records why a new model was skipped. |

## Context and fresh-host evaluation

| Pilot | Initial active / unresolved / excluded dimensions | Ready active / unresolved / excluded dimensions | Largest saved batch |
| --- | --- | --- | --- |
| Facility | 10 / 1 / 5 | 11 / 0 / 5 | 1 |
| Process | 14 / 0 / 1 | 14 / 0 / 1 | 1 |
| Contract | 13 / 0 / 3 | 13 / 0 / 3 | 1 |

A separate CLI process reopens the draft, the classified interview, and the
pending evidence question for each pilot using the saved workspace alone.
The replay queues one prompt per round. The incomplete checkpoint has an
empty batch and still reports the missing evidence. These checks measure
saved context. Host token usage, dialog delivery, and agent judgment require
the fresh-host pilot below.

After explicit approval to start a live interview, give a fresh host the
scenario's title, intent, and scope. Use the remaining fixture entries as
scripted replies and source excerpts when requested. Resume the interrupted
interview in a new chat with the workspace path. In separate chats, invoke
investigation for the conflicting source, requirements before and after the
conflict, and modeling for the reconciled baseline. Ask for both artifact
formats. Record pass, partial, or fail with an observed prompt or linked
record for each of the following.

- Correct classification and overlays. An unresolved fact should produce a
  relevant question, and an excluded topic should stay out of the batch.
- No duplicate questions after a fact is answered. Record repeated prompts,
  round sizes, and counts of active, unresolved, and excluded dimensions.
  Record prompt or context tokens if the host exposes them.
- Resume from the saved revision, confirmed decisions, and pending question
  without requiring the previous transcript.
- Domain-appropriate questions and acceptance checks using all four unchanged
  skills. Record any missing concern and whether a product template or a
  shared overlay should own it.
- Observable handoff boundaries, linked blockers, and consistent readiness
  across the exported forms. The contract's drafting report must carry the
  separate legal review requirement through the signature handoff.
