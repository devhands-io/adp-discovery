# Meeting decision register pilot

The [rounds fixture](rounds.json) follows a team discovering an on-demand
decision register. Each round includes the expected next batch and changes
to apply by record ID. Profile arguments go to the `profile` command. The
replay tests save each full candidate and reopen it in a separate process.

| Round | Expected behavior |
| --- | --- |
| Start from the brief | Save intent and ask for classification. A fresh thread can start at that question. |
| Confirm the product | Keep sensitivity unknown. Record the Markdown preference and the assumption about named owners. The proposal remains unconfirmed. |
| Clarify sensitivity | Apply Security. The review question becomes eligible after the sensitivity question resolves. |
| Receive the records policy | Surface its conflict with the output decision. Preserve the earlier answer and reopen the decision. |
| Reconcile the output rule | Record the replacement decision. Preserve the original wording, and return to the open review question. |

To replay in Codex, start with “Help the project team capture decisions and
their owners from meeting notes.” Use the stakeholder statements in the fixture
to continue. Open a fresh thread between rounds and invoke `$interview` with
the exact workspace path. Verify the thread recovers the current question
without asking about purpose again. If the stakeholder cannot settle a
question, verify it stays open and can be deferred.

## Fresh interviewer pilot

Give the interviewer only the two files in `interview-input/`, an isolated
state path, and the request “Use /interview to grill the idea in the brief.”
Keep this evaluator guide and the rounds fixture out of the interview input.

Observe whether the interviewer discovers the attribution rule, cites it, and
asks what the draft should do. As stakeholder, choose to leave the owner
unassigned. Check whether the interviewer follows the consequence for review
or publication. Defer one material decision and request a baseline. Resume
from the state path, settle the remaining questions, and confirm the recap
only when accurate. Reopen the workspace with a material correction and
verify the prior confirmation is recoverable and the change needs review.
Record observed actions separately from fixture replay results.

### Observed forward test

On 2026-11-26, an isolated interviewer read the brief and policy, cited
the conflicting attribution rule, and proposed a missing-owner decision.
The checkpoint baseline retained a deferred sharing question. A fresh
interviewer resumed from state, recorded the chair's reply, and asked about
conflicting assignments. It obtained explicit recap confirmation while the
separate handoff assessment remained outstanding. A further fresh interviewer
preserved that confirmation after a retention correction and requested
confirmation of the revised recap. This run used a simulated chair and agent
messages for the questions. Desktop dialog delivery was outside the test.
