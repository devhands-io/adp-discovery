---
name: interview
description: Run or resume a product discovery interview. Use when a stakeholder wants to clarify an idea, confirm discovery decisions, reconcile conflicting answers, or produce a reviewable discovery baseline.
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
3. Ask one focused question or a small related batch. Resolve prerequisites and impactful uncertainties first. Record sourced facts, preferences, assumptions, and decisions separately. Only confirm decisions the stakeholder explicitly makes or accepts.
4. Save each substantive round and the next batch before asking it. Surface conflicting evidence and reopen affected decisions. Revisit an answered question only when new evidence requires it.
5. Offer baseline review at a natural checkpoint and generate it on request or at that checkpoint. Report gaps and uncertainty. Coverage and an empty batch do not establish stakeholder approval.

Follow the [interview workflow](references/workflow.md) and [state and CLI reference](references/state.md).
