# Decision log

| Decision | Rationale and trade-off |
| --- | --- |
| Release the first vertical slice as the foundation, catalog, interview, and pilot | The supplied brief defines an end-to-end interview as the first success criterion. Supporting skills, a larger catalog, and additional artifacts are subsequent milestones. |
| Use local Python, YAML templates, and JSON Schema | YAML is readable for catalog authors. Python and JSON Schema provide deterministic checks with two direct dependencies. The command runs from a repository checkout. |
| Keep classification and contradiction judgment in the interview | Stakeholders confirm meaning. The core checks the consistency of the recorded results and calculates evidence coverage. |
| Require built-in question dialogs when available | The skill uses the host's input capability and falls back to chat when the session lacks one. Both paths require an explicit reply before the interview acts on an answer. |
| Store revisioned JSON with a fixed checklist snapshot | A resuming session reads the same scope after a catalog edit. A changed classification starts a new workspace in version 1. |
| Use a single Markdown export with traceable sections | One artifact is sufficient to review the first slice and can be reproduced directly from state. |
| Keep generic physical and legal acceptance scenarios | Domain-neutral behavior can be tested now. Specialized building, process, and contract templates follow the agent-skill pilot. |

## Subsequent slices

1. Add independent investigation, requirements, and modeling skills against the
   same state and artifact conventions.
2. Establish the full artifact set and deeper evidence and readiness checks.
3. Add specialized building, process, and contract templates with distinct
   discovery pilots.
4. Expand the catalog in reviewed batches and introduce migrations when the
   contracts change.
