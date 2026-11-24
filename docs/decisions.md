# Decision log

| Decision | Rationale and trade-off |
| --- | --- |
| Release the first vertical slice as the foundation, catalog, interview, and pilot | The supplied brief defines an end-to-end interview as the first success criterion. Supporting skills, a larger catalog, and additional artifacts are subsequent milestones. |
| Use local Python, YAML templates, and JSON Schema | YAML is readable for catalog authors. Python and JSON Schema provide deterministic checks with two direct dependencies. The command runs from a repository checkout. |
| Keep classification, decision confirmation, and stakeholder reconciliation in the interview | Supporting skills can record conflicts and reopen affected decisions. Stakeholders confirm meaning, and the core checks consistency and calculates evidence coverage. |
| Require built-in question dialogs when available | The skill uses the host's input capability and falls back to chat when the session lacks one. Both paths require an explicit reply before the interview acts on an answer. |
| Store revisioned JSON with a fixed checklist snapshot | A resuming session reads the same scope after a catalog edit. A changed classification starts a new workspace in version 1. |
| Use a single Markdown export with traceable sections | One artifact is sufficient to review the first slice and can be reproduced directly from state. |
| Keep generic physical and legal acceptance scenarios | Domain-neutral behavior can be tested now. Specialized building, process, and contract templates follow the agent-skill pilot. |
| Require version 1 on every template | Catalog formats can evolve independently of saved workspace state. Custom unversioned templates need a version field. |
| Compose in a fixed order and give each dimension one owner | Base, primary product, ordered secondary products, and filename-ordered overlays give a reproducible checklist with a source for each dimension. Rejecting duplicate IDs prevents implicit overrides. |
| Preserve unresolved applicability in inspection | Partial tag facts can leave overlays or dimensions unresolved and surface which facts are missing. A confirmed single-product tag set still produces the existing version 1 checklist for workspace initialization. |
| Persist draft interviews and append confirmed profiles in v2 | Save the intent and first question before confirmation. Later changes keep their earlier checklist and evidence links. Explicit upgrades preserve legacy workspaces and record unknown provenance. |
| Store question dependencies and an ordered batch of IDs | The interview skill ranks meaningful questions. Python validates the dependency graph and eligibility, and a new thread can recover the batch without duplicating question text. |
| Derive readiness from applicability and evidence | Required unknown applicability stays visible as a gap. Confirmed exclusions and optional gaps can be reported without imposing coverage or implying stakeholder approval. |
| Explain readiness in v2 Markdown | A short explanation helps stakeholders interpret the status at a glance. The status values and JSON output remain compatible. |
| Keep pilot evaluation outside the interview | Maintainers agree on the rubric and get approval for the live session before opening a dialog. Stakeholders answer only the product questions. |
| Run supporting skills independently against the same ledger | A project can investigate, derive requirements, or model where it needs help. Revision-linked Markdown holds the derived details and permits review with the existing state schemas. |

## Subsequent slices

1. Establish the full artifact set and deeper evidence and readiness checks.
2. Add specialized building, process, and contract templates with distinct
   discovery pilots.
3. Expand the catalog in reviewed batches and introduce migrations when the
   contracts change.
