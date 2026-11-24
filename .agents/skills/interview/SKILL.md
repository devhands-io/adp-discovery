---
name: interview
description: Run or resume a product discovery interview. Use when a stakeholder wants to clarify an idea, confirm discovery decisions, reconcile conflicting answers, or produce a reviewable discovery baseline.
---

# Discovery interview

## Ask through the host's built-in dialog

Use the host's built-in question dialog for every stakeholder question when
the current session provides one you can use. Submit the question through
the dialog. Offer choices when they represent real alternatives, and allow
a free-text answer when the dialog supports it.

If the session has no usable question dialog, briefly tell the stakeholder
and ask in chat. If the stakeholder dismisses a dialog or leaves a question
unanswered, keep it open. Wait for an explicit reply before confirming a
decision or taking a step that depends on the answer.

## Interview workflow

1. Identify the product and discovery workspace. Use `.discovery/<slug>/state.json` by default. If state exists, load it with `show`, summarize the latest confirmed decisions and blockers, then resume at the highest-impact gap. If multiple workspaces fit, ask which one to use.
2. For a new interview, propose the product classification and applicable tags and verify them with the stakeholder before initialization. Select `general` if no specialized template fits. See [the interview reference](references/workflow.md) for commands and the state contract.
3. Ask one focused question or a small set of closely related questions. Use the composed checklist, the stakeholder's latest answers, and the consequences of uncertainty to choose what to ask next. Reuse prior answers and defer implementation detail until it affects a decision.
4. At each meaningful turn, record new evidence with a source, preserve stakeholder-confirmed decisions, label inferences as assumptions or proposals, and save before replying. When answers clash, name the conflicting statements and ask which should hold. Reopen affected decisions until the stakeholder resolves the conflict.
5. On request or at a natural checkpoint, generate the discovery baseline and interpret the readiness findings. Present blockers with their supporting record IDs and identify the next unresolved decision. Report uncertainty and avoid treating baseline coverage as independent approval.
