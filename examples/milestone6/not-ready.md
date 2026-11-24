# adp-discovery interview skill

Project `self-discovery` · State v3 · Revision 3
State digest `a260dc2a410faaa2fc436e167dae86b879c68f93b9e8b8dc22e2dcb3eff3f33c`

## Discovery brief

Classification **uncertain** · `agent-skill`
Applicable overlays `evaluation`, `security`
- Draft intent · The first adp-discovery skill guides a stakeholder from a product idea to a reviewable discovery baseline. A later Codex session can continue from the saved checklist and decision register. This replay uses the supplied brief as its evidence and leaves workspace handling and acceptance details open. · No structured intent claim was recorded.
- `workspace-sensitivity` · Assumption · open · Interview content may contain sensitive stakeholder information. The pilot applies the Security overlay on this assumption.

## Decision register

- `discovery-goal` · confirmed · Help the project stakeholder turn a product idea into a reviewable baseline that can be resumed and checked. · uncertain · Dimensions `purpose`, `stakeholders`, `success` · Ledger references `brief-purpose`
- `first-slice` · confirmed · Focus the first version on the Discovery phase with the interview skill and local workspace files. · uncertain · Dimensions `scope`, `constraints` · Ledger references `brief-first-slice`
- `codex-invocation` · confirmed · Expose the workflow as the repository's interview skill, invokable with \$interview. · uncertain · Dimensions `invocation` · Ledger references `brief-first-slice`
- `resume-from-state` · confirmed · Use saved workspace state as the source for resuming a discovery interview. · uncertain · Dimensions `handoff` · Ledger references `brief-handoff`
- `reviewable-baseline` · confirmed · Export the brief, confirmed decisions, open questions, and preliminary readiness from saved state. · uncertain · Dimensions `outputs` · Ledger references `brief-artifacts`
- `independent-checks` · confirmed · Check normal discovery, incomplete input, contradiction recovery, and resumption with tests independent of the skill's judgment. · uncertain · Dimensions `evaluation-cases` · Ledger references `brief-tests`

## Requirements baseline

No requirements recorded.

## Evidence register

- `brief-purpose` · The brief asks for a complete discovery workflow for an unfamiliar product and recommends discovering the framework itself first. · Source Supplied brief, development strategy and first success criterion · Dimensions `purpose`, `stakeholders`, `success`
- `brief-first-slice` · The brief describes a Discovery-only first slice built from a reusable catalog and one working interview skill, followed by additional skills. · Source Supplied brief, milestones and implementation split · Dimensions `scope`, `constraints`, `invocation`
- `brief-handoff` · The brief requires an interrupted interview to continue in a fresh thread without losing confirmed decisions. · Source Supplied brief, interview milestone · Dimensions `handoff`
- `brief-artifacts` · The first pilot should produce a coherent brief, decision register, open questions, and a preliminary readiness assessment. · Source Supplied brief, complete pilot milestone · Dimensions `outputs`
- `brief-tests` · The brief calls for an independent acceptance check and scenarios involving an incomplete idea, conflicting answers, and interruption. · Source Supplied brief, regression scenarios · Dimensions `evaluation-cases`

## Risk register

No risks recorded.

## Open questions

- `handling-confirmation` · Which interview content may the team retain and share, and who may access the workspace? · blocking · Unknown impact · Ledger references `workspace-sensitivity`
- `authority-review` · Who can authorize sharing or exporting stakeholder evidence outside the interview workspace? · blocking · Unknown impact
- `acceptance-review` · Who will sign off on the first live interview and which observations will they require? · blocking · Unknown impact
- `future-skill-ownership` · What overlap will need a clear ownership rule when the companion skills are introduced? · Unknown impact

## Discovery readiness report

**Not ready**

- **Block** · `classification-unconfirmed` · Classification needs recorded stakeholder confirmation.
- **Block** · `criteria-not-pinned` · Save a confirmed profile with the composed readiness criteria.
- **Block** · `missing-brief-intent` · Record a material intent claim with its findings.
- **Block** · `purpose` · Coverage needs a confirmed decision and supported finding backed by evidence for this dimension.
- **Block** · `scope` · Coverage needs a confirmed decision and supported finding backed by evidence for this dimension.
- **Block** · `stakeholders` · Coverage needs a confirmed decision and supported finding backed by evidence for this dimension.
- **Block** · `success` · Coverage needs a confirmed decision and supported finding backed by evidence for this dimension.
- **Block** · `constraints` · Coverage needs a confirmed decision and supported finding backed by evidence for this dimension.
- **Block** · `invocation` · Coverage needs a confirmed decision and supported finding backed by evidence for this dimension.
- **Block** · `outputs` · Coverage needs a confirmed decision and supported finding backed by evidence for this dimension.
- **Block** · `handoff` · Coverage needs a confirmed decision and supported finding backed by evidence for this dimension.
- **Inform** · `adjacent-skills` · Coverage needs a confirmed decision and supported finding backed by evidence for this dimension.
- **Block** · `evaluation-cases` · Coverage needs a confirmed decision and supported finding backed by evidence for this dimension.
- **Block** · `acceptance-owner` · Coverage needs a confirmed decision and supported finding backed by evidence for this dimension.
- **Block** · `authority` · Coverage needs a confirmed decision and supported finding backed by evidence for this dimension.
- **Block** · `information-handling` · Coverage needs a confirmed decision and supported finding backed by evidence for this dimension.
- **Block** · `unsupported-decision` · The confirmed decision lacks a usable finding or confirmation evidence. · `discovery-goal`
- **Block** · `unsupported-decision` · The confirmed decision lacks a usable finding or confirmation evidence. · `first-slice`
- **Block** · `unsupported-decision` · The confirmed decision lacks a usable finding or confirmation evidence. · `codex-invocation`
- **Block** · `unsupported-decision` · The confirmed decision lacks a usable finding or confirmation evidence. · `resume-from-state`
- **Block** · `unsupported-decision` · The confirmed decision lacks a usable finding or confirmation evidence. · `reviewable-baseline`
- **Block** · `unsupported-decision` · The confirmed decision lacks a usable finding or confirmation evidence. · `independent-checks`
- **Block** · `missing-requirements` · Record an active requirements baseline.
- **Block** · `open-question` · The question remains open. · `handling-confirmation`
- **Block** · `open-question` · The question remains open. · `authority-review`
- **Block** · `open-question` · The question remains open. · `acceptance-review`
- **Inform** · `open-question` · The question remains open. · `future-skill-ownership`
- **Block** · `baseline-review-missing` · The profile has no mandatory stakeholder baseline review.
