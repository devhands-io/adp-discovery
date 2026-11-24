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
