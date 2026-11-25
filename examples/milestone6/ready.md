# Synthetic handoff skill

Project `synthetic-handoff` · State v3 · Revision 1
State digest `78f718fea528a32dd20a6bdde060a8629ff155b1acddc44c615fe9fea13107e3`

## Discovery brief

Classification **confirmed** · `agent-skill` · Confirmation `type-confirmation`
Applicable overlays `evaluation`
- `brief-intent` · Intent · The team needs to retrieve previously confirmed project decisions during a handoff. · supported · Findings `purpose-finding`
- `brief-scope` · Scope · On request, the skill reads the local record. It uses public sample data and performs no external actions. · supported · Findings `boundary-finding`

## Decision register

- `purpose-decision` · confirmed · The team needs to retrieve previously confirmed project decisions during a handoff. · supported · Dimensions `purpose`, `stakeholders`, `success` · Findings `purpose-finding` · Ledger references `purpose-statement`
- `boundary-decision` · confirmed · On request, the skill reads the local record. It uses public sample data and performs no external actions. · supported · Dimensions `scope`, `constraints`, `invocation` · Findings `boundary-finding` · Ledger references `boundary-statement`
- `handoff-decision` · confirmed · Return the latest confirmed decisions with their IDs and the saved revision. Report missing state explicitly. · supported · Dimensions `outputs`, `handoff` · Findings `handoff-finding` · Ledger references `handoff-statement`
- `evaluation-decision` · confirmed · The project lead reviews successful retrieval and the missing-state response. · supported · Dimensions `evaluation-cases`, `acceptance-owner` · Findings `evaluation-finding` · Ledger references `evaluation-statement`

## Requirements baseline

- `req-retrieve-decisions` · active · Return the latest confirmed decisions with their IDs and the saved revision. Report missing state explicitly. · justification supported · Decisions `handoff-decision` · The confirmed handoff needs traceable retrieval.
  - `ac-confirmed-decisions` · The output shows that decision ID and the revision. · Given a saved revision with one confirmed decision · Replay a saved workspace.
  - `ac-missing-state` · The output identifies that the state file could not be found. · Given a missing state file

## Evidence register

- `type-confirmation` · This is an agent skill using public sample data. · Source Synthetic stakeholder classification
- `purpose-statement` · The team needs to retrieve previously confirmed project decisions during a handoff. · Source Synthetic stakeholder statement about purpose · Dimensions `purpose`, `stakeholders`, `success`
- `boundary-statement` · On request, the skill reads the local record. It uses public sample data and performs no external actions. · Source Synthetic stakeholder statement about boundary · Dimensions `scope`, `constraints`, `invocation`
- `handoff-statement` · Return the latest confirmed decisions with their IDs and the saved revision. Report missing state explicitly. · Source Synthetic stakeholder statement about handoff · Dimensions `outputs`, `handoff`
- `evaluation-statement` · The project lead reviews successful retrieval and the missing-state response. · Source Synthetic stakeholder statement about evaluation · Dimensions `evaluation-cases`, `acceptance-owner`

### Findings

- `purpose-finding` · supported · The team needs to retrieve previously confirmed project decisions during a handoff. · The population and scope are stated explicitly in the fixture. · Evidence `purpose-statement`
- `boundary-finding` · supported · On request, the skill reads the local record. It uses public sample data and performs no external actions. · The population and scope are stated explicitly in the fixture. · Evidence `boundary-statement`
- `handoff-finding` · supported · Return the latest confirmed decisions with their IDs and the saved revision. Report missing state explicitly. · The population and scope are stated explicitly in the fixture. · Evidence `handoff-statement`
- `evaluation-finding` · supported · The project lead reviews successful retrieval and the missing-state response. · The population and scope are stated explicitly in the fixture. · Evidence `evaluation-statement`

## Risk register

No risks recorded.

## Open questions

No open questions recorded.

## Discovery readiness report

**Ready**

- **Pass** · `purpose` · A supported decision covers the dimension. · `purpose-decision`
- **Pass** · `scope` · A supported decision covers the dimension. · `boundary-decision`
- **Pass** · `stakeholders` · A supported decision covers the dimension. · `purpose-decision`
- **Pass** · `success` · A supported decision covers the dimension. · `purpose-decision`
- **Pass** · `constraints` · A supported decision covers the dimension. · `boundary-decision`
- **Pass** · `invocation` · A supported decision covers the dimension. · `boundary-decision`
- **Pass** · `outputs` · A supported decision covers the dimension. · `handoff-decision`
- **Pass** · `handoff` · A supported decision covers the dimension. · `handoff-decision`
- **Inform** · `adjacent-skills` · Coverage needs a confirmed decision and supported finding backed by evidence for this dimension.
- **Pass** · `evaluation-cases` · A supported decision covers the dimension. · `evaluation-decision`
- **Pass** · `acceptance-owner` · A supported decision covers the dimension. · `evaluation-decision`
- **Excluded** · `accessible-task-completion` · The dimension is inapplicable.
- **Excluded** · `authority` · The dimension is inapplicable.
- **Excluded** · `information-handling` · The dimension is inapplicable.
- **Pass** · `baseline-review` · Template `general` · The stakeholder reviews the discovery baseline and its supporting evidence. · `record-baseline-review`
- **Pass** · `handoff-replay` · Template `agent-skill` · Assess a representative replay of the skill handoff. · `record-handoff-replay`
- **Pass** · `evaluation-plan-review` · Template `evaluation` · The acceptance owner reviews the proposed evaluation cases. · `record-evaluation-plan-review`
- **Excluded** · `information-handling-approval` · Template `security` · The criterion is inapplicable.

### Recorded assessments, reviews, and approvals

- `record-baseline-review` · `baseline-review` · passed · current subject · Synthetic stakeholder (`stakeholder`) · Synthetic source record for baseline-review · The stakeholder reviews the discovery baseline and its supporting evidence.
- `record-handoff-replay` · `handoff-replay` · passed · current subject · Synthetic discovery-reviewer (`discovery-reviewer`) · Synthetic source record for handoff-replay · Assess a representative replay of the skill handoff.
- `record-evaluation-plan-review` · `evaluation-plan-review` · passed · current subject · Synthetic acceptance-owner (`acceptance-owner`) · Synthetic source record for evaluation-plan-review · The acceptance owner reviews the proposed evaluation cases.
