# Interview workflow

## Establish intent and classification

Capture the intended outcome and audience from the brief. Save the brief as
sourced evidence and the proposed classification as an open question in the
draft workspace. Ask the stakeholder to confirm or correct the primary type,
specialized secondary types, and the tag facts they can establish. Use the
catalog's descriptions and partial composition to ask for facts that could
change discovery scope.

An explicitly confirmed product can have unknown tag facts. Record tags as
present or absent when supported and leave the others undeclared. A confirmed
profile change appends a snapshot. Compare the old and new checklists, resolve
questions that became irrelevant with a reason, and reopen questions or
decisions affected by new evidence. Attach existing evidence to a newly
available dimension when the original statement applies.

## Select the next batch

1. Match the brief and latest replies against existing questions and dimensions.
   Close answered questions with links to their evidence. Ask follow-ups only
   for boundaries or consequences that remain unclear.
2. After each answer, identify the choices it unlocks. Try a concrete boundary
   case when it could change the decision. Record every material follow-up,
   including those outside the next batch or in an already covered dimension.
   Give open questions stable IDs. Add prerequisites only when their
   answers are needed to ask the dependent question meaningfully. Leave a
   classification or applicability question unscoped if it precedes the
   corresponding dimension.
3. Prioritize contradictions and gaps that block the baseline or several other
   questions. Then consider the consequences of a wrong assumption and the cost
   of resolving it. Use checklist order to break ties.
4. Choose one to three closely related eligible questions for the frontier.
   Save the IDs in asking order. When a stakeholder says the answer is unknown
   or must wait, keep the question open and defer it when useful. Reconsider it
   after a relevant change. A dismissed or skipped question stays available
   under its original ID.

Before asking for a material fact, check the brief, ledger and accessible
primary sources, including the implementation when it establishes current
behavior. Save the finding with a precise source locator. For substantial
research, use the evidence practices in the [investigation skill](../../investigate/SKILL.md).
If a check is pending or inconclusive, keep its question open and proceed
with independent decisions. Ask the stakeholder for facts only they can
supply. A source describing current behavior can conflict with a factual
claim while still leaving the intended behavior for the stakeholder to decide.

Ask neutral questions about observations and preferences. For each product
decision, recommend an answer, explain why, and name the material consequence
of accepting it. Let the stakeholder accept, amend or reject the proposal.
When evidence is insufficient, recommend how to resolve the uncertainty.
Defer implementation and modeling questions until they affect discovery.

## Interpret and save each round

- **Fact or observation.** Record the claim with a source and relevant dimensions.
  A stakeholder statement is evidence of what they said. Preserve their
  uncertainty about the underlying fact.
- **Preference.** Record what the stakeholder favors and link their statement.
- **Assumption.** Record the inference, its basis, and what would test it.
- **Decision.** Record a recommendation as proposed. Use confirmed only after
  the stakeholder makes or explicitly accepts the decision. Link that evidence.
- **Contradiction.** Link the conflicting evidence and affected decisions.
  Explain the consequence and ask which statement governs or whether they apply
  under different conditions. Reopen affected decisions in the same save. On
  resolution, attach the clarification and restore the original decision or
  supersede it with a new record. Preserve both original statements.

Save concise summaries and IDs that a new thread can interpret. On resume,
load the workspace and inspect its readiness, saved batch, and eligible
questions. Summarize confirmed decisions and blockers briefly. Reuse the
saved batch unless a new reply or source changes it.

If the batch is empty, check gaps, unknown applicability, deferred questions,
and blockers. A dimension can have evidence while still lacking confirmation
for readiness. Review whether the evidence is sufficient and who approves
the baseline. Generate a Markdown baseline on request or at a review
checkpoint. Leave ADRs out of exploratory questioning.

For v3, save material brief claims with supporting findings or explicit
uncertainty, and link confirmed decisions to their findings. Use the saved
criteria to identify who needs to review, approve, or authorize a condition.
Record the explicit outcome and source for the reviewed subject. Readiness
requires the recorded baseline review and any applicable approvals.

## Close or resume the interview

Inspect the whole ledger, including deferred questions, pending source checks,
contradictions and reopened decisions. Settle each material in-scope branch
or record the stakeholder's explicit scope exclusion and reason. A deferral
pauses that branch. A baseline may be exported and reviewed at any checkpoint.

Once those branches are accounted for, present the settled choices and scope
boundaries in a concise recap. Ask the stakeholder to confirm that it captures
their understanding. Save the recap and question before asking. On explicit
acceptance, resolve the question with a link to sourced evidence identifying
the recap and the reply. A baseline review can serve both purposes when it
explicitly covers that recap. On correction, follow the affected branches and
present a revised recap for confirmation.

On resume, compare the confirmed recap with current decisions, scope and open
work. Preserve earlier confirmations as history. A material change requires a
new recap and confirmation; an unrelated save preserves the existing outcome.
