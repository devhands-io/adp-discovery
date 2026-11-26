---
name: interview
description: Run or resume a product discovery interview. Use when a stakeholder wants to grill or stress-test a product idea, confirm discovery decisions, reconcile conflicting answers, or produce a reviewable discovery baseline.
---

# Discovery interview

Start or resume when the stakeholder requests an interview or explicitly
approves the proposed live session. Treat approval to edit the framework
as permission for maintenance.

## Ask through the host's built-in dialog

Use the host's built-in question dialog for every stakeholder question when
the current session provides one you can use. Present each question once
per round in that dialog. Keep any accompanying chat to a short progress
update. Offer choices when they represent real alternatives, and allow a
free-text answer when the dialog supports it.

If the dialog is unavailable in the current session or mode, say so briefly
when asking in chat. If the stakeholder dismisses a dialog or leaves a
question unanswered, keep it open. Wait for an explicit reply before
confirming a decision or taking a step that depends on the answer.

## Interview workflow

1. Find the workspace or start a draft under `.discovery/<slug>/state.json`. On resume, load the saved state, summarize the confirmed decisions and blockers, and use the saved question batch. If several workspaces fit, ask which one to use.
2. Capture the stated intent and reuse answers from the brief. Propose a product classification from the catalog, use `general` when no specialization fits, and confirm the type and known applicability facts with the stakeholder.
3. Check discoverable facts against accessible sources. For each product decision, present a recommendation, its reasoning, and the consequence of accepting it. Keep recommendations proposed until the stakeholder decides.
4. After each answer, pursue consequential boundaries and newly enabled decisions. Record all material branches, reopen conflicts, and save the next batch of one to three related questions before asking it.
5. Generate the baseline on request or at a review checkpoint. To close the interview, settle the material branches and obtain explicit confirmation of the closing recap.

Follow the [interview workflow](references/workflow.md) and [state and CLI reference](references/state.md).
