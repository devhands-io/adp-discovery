# adp-discovery interview skill

## Discovery brief

The first adp-discovery skill guides a stakeholder from a product idea to a reviewable discovery baseline. A later Codex session can continue from the saved checklist and decision register. This replay uses the supplied brief as its evidence and leaves workspace handling and acceptance details open.

- Classification: `agent-skill`
- Tags: sensitive-data
- Overlays: evaluation, security
- State revision: 2

## Decision register

- `discovery-goal` (confirmed) Help the project stakeholder turn a product idea into a reviewable baseline that can be resumed and checked. (Dimensions: purpose, stakeholders, success) (References: brief-purpose)
- `first-slice` (confirmed) Focus the first version on the Discovery phase with the interview skill and local workspace files. (Dimensions: scope, constraints) (References: brief-first-slice)
- `codex-invocation` (confirmed) Expose the workflow as the repository's interview skill, invokable with $interview. (Dimensions: invocation) (References: brief-first-slice)
- `resume-from-state` (confirmed) Use saved workspace state as the source for resuming a discovery interview. (Dimensions: handoff) (References: brief-handoff)
- `reviewable-baseline` (confirmed) Export the brief, confirmed decisions, open questions, and preliminary readiness from saved state. (Dimensions: outputs) (References: brief-artifacts)
- `independent-checks` (confirmed) Check normal discovery, incomplete input, contradiction recovery, and resumption with tests independent of the skill's judgment. (Dimensions: evaluation-cases) (References: brief-tests)

## Open questions

- `handling-confirmation` (open) Which interview content may the team retain and share, and who may access the workspace? (Dimensions: information-handling) (References: workspace-sensitivity) (Blocking)
- `authority-review` (open) Who can authorize sharing or exporting stakeholder evidence outside the interview workspace? (Dimensions: authority) (Blocking)
- `acceptance-review` (open) Who will sign off on the first live interview and which observations will they require? (Dimensions: acceptance-owner) (Blocking)
- `future-skill-ownership` (open) What overlap will need a clear ownership rule when the companion skills are introduced? (Dimensions: adjacent-skills)

## Assumptions, risks, and contradictions

- `workspace-sensitivity` (open) Interview content may contain sensitive stakeholder information. The pilot applies the Security overlay on this assumption. (Dimensions: information-handling)

## Evidence

- `brief-purpose` (recorded) The brief asks for a complete discovery workflow for an unfamiliar product and recommends discovering the framework itself first. (Source: Supplied brief, development strategy and first success criterion) (Dimensions: purpose, stakeholders, success)
- `brief-first-slice` (recorded) The brief describes a Discovery-only first slice built from a reusable catalog and one working interview skill, followed by additional skills. (Source: Supplied brief, milestones and implementation split) (Dimensions: scope, constraints, invocation)
- `brief-handoff` (recorded) The brief requires an interrupted interview to continue in a fresh thread without losing confirmed decisions. (Source: Supplied brief, interview milestone) (Dimensions: handoff)
- `brief-artifacts` (recorded) The first pilot should produce a coherent brief, decision register, open questions, and a preliminary readiness assessment. (Source: Supplied brief, complete pilot milestone) (Dimensions: outputs)
- `brief-tests` (recorded) The brief calls for an independent acceptance check and scenarios involving an incomplete idea, conflicting answers, and interruption. (Source: Supplied brief, regression scenarios) (Dimensions: evaluation-cases)

## Preliminary readiness

Status: `gaps-remain`

- `purpose` is covered by `discovery-goal` with brief-purpose.
- `scope` is covered by `first-slice` with brief-first-slice.
- `stakeholders` is covered by `discovery-goal` with brief-purpose.
- `success` is covered by `discovery-goal` with brief-purpose.
- `constraints` is covered by `first-slice` with brief-first-slice.
- `invocation` is covered by `codex-invocation` with brief-first-slice.
- `outputs` is covered by `reviewable-baseline` with brief-artifacts.
- `handoff` is covered by `resume-from-state` with brief-handoff.
- `evaluation-cases` is covered by `independent-checks` with brief-tests.
- `acceptance-owner` has a gap. Who reviews the results, and what evidence is sufficient for acceptance? Needs a confirmed decision linked to recorded evidence for this dimension.
- `authority` has a gap. Which actions require approval, and who can grant it? Needs a confirmed decision linked to recorded evidence for this dimension.
- `information-handling` has a gap. What information may be accessed, retained, or shared, and by whom? Needs a confirmed decision linked to recorded evidence for this dimension.
- Blocking records: handling-confirmation, authority-review, acceptance-review.
