# Review a meeting decision

From the repository root, run the rehearsal with a new output directory. It prints a local viewer link and model digest for every stage. The last stage is an independent post-confirmation exercise.

```sh
.venv/bin/python examples/interaction-model/replay.py /tmp/decision-review-pilot
```

| Stage | One-person rehearsal | Observable result |
| --- | --- | --- |
| Before screens | Choose “Review a meeting decision.” Propose two use cases: `review-and-return` (review a listed decision, see its details, then resume the register) and `leave-review` (leave an open review and resume the register). Ask what other outcomes belong in scope. | The modeler can add, change or exclude a use case before agreeing to use the inventory for drafting. The rehearsal assumes these two for illustration. |
| 01 | Inspect coverage. Open Review decision and select Save. | The example form contains “Publish the revised launch checklist.” Save opens Decision list. The intended review-and-return scenario stops at a missing step. |
| 02 | In chat say “Save should open Decision details. Let me retry from the review form.” Open the retry link and select Save again. | The same populated form opens first. Save now opens Decision details. The screen has no product action that returns to the register. |
| Omission review | Ask “Which screens or routes are missing? How would you get back to the register from details?” | The modeler can identify the missing return route even though all declared actions have valid targets. The viewer's Review coverage link belongs to the viewer. |
| 03 | In chat say “Add Return to list on Decision details.” Inspect updated coverage. Replay Review → Save → Return to list and Review → Back from their listed starts. | Both end at Decision list. Until the modeler explicitly confirms the scope, screens and routes, the revision is pending. |
| Handoff | Open the fresh directory's preview. It was generated after copying only the corrected Markdown into that directory. | Both scenario traces, all three screens and the example field are recoverable. |
| 04 | Rehearse a later correction assuming an explicit confirmation of stage 03. Say “Back should open details.” Retry Back from the form. | The digest changes. The modeler may confirm the updated inventory and navigation immediately after the retry or replay more first. Earlier confirmation identifies only stage 03. |

For the whole-product alternative, choose the entire agreed scope before drafting and list each in-scope capability. If the entire pilot product is this decision register, both review-and-return and leaving the review form must appear in coverage. The skill handles scope and confirmation in chat. These scripted replies are rehearsal inputs, never stakeholder evidence.

## Acceptance evidence

| Baseline criteria | Verification |
| --- | --- |
| `ac-trace-scenario`, `ac-navigate-form` | Checked the source/action/destination coverage rows. Clicked Save and Back in separate Chrome attempts and observed the destination screens. |
| `ac-try-task`, `ac-retry-save` | Ran the viewer during the implementation chat. Replayed the scripted correction, opened the regenerated preview at the populated review form, and clicked Save to reach details. |
| `ac-missing-route` | Checked the skill's explicit omission question and observed the missing step in coverage and absent product action on details. After the addition, clicked Return to list. |
| `ac-independent-replay` | Copied only the corrected Markdown as input to a fresh directory, regenerated the viewer there and clicked through both scenarios. |
| `ac-whole-product`, `ac-one-workflow` | Reviewed the interview's two boundary choices. The scripted example exercises the named workflow. Whole-product elicitation still needs a live run. |
| `ac-review-then-replay`, `ac-await-confirmation`, `ac-single-modeler` | Checked the prescribed question order and single-modeler confirmation rule. Replayed both scenarios after reviewing coverage. The rehearsal creates no stakeholder confirmation. |
| `ac-reconfirm-after-retry` | Compared the revision digests and clicked the changed Back action from the same form. The choice to confirm immediately or replay further was checked in the skill instructions. A live reconfirmation remains unobserved. |

The baseline leaves the invocation trigger and formal evaluation ownership open. The pilot uses an explicit `model-product` request and keeps walkthrough confirmation with the one modeler. The example also leaves notation and persistence of field edits open. This implementation reads the supplied YAML notation and displays read-only example values.
