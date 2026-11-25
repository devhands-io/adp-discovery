# Decision log

| Decision | Rationale and trade-off |
| --- | --- |
| Release the first vertical slice as the foundation, catalog, interview, and pilot | The supplied brief defines an end-to-end interview as the first success criterion. Supporting skills, a larger catalog, and additional artifacts are subsequent milestones. |
| Use local Python, YAML templates, and JSON Schema | YAML is readable for catalog authors. Python and JSON Schema provide deterministic checks with two direct dependencies. The command runs from a repository checkout. |
| Keep classification, decision confirmation, and stakeholder reconciliation in the interview | Supporting skills can record conflicts and reopen affected decisions. Stakeholders confirm meaning, and the core checks consistency and calculates evidence coverage. |
| Ship a Claude Code entry point for `/interview` | A regular project skill file works with Git checkouts and ZIP downloads. It forwards the request to the shared interview instructions so there is one workflow to maintain. |
| Require built-in question dialogs when available | The skill uses the host's input capability and falls back to chat when the session lacks one. Both paths require an explicit reply before the interview acts on an answer. |
| Store revisioned JSON with a fixed checklist snapshot | A resuming session reads the same scope after a catalog edit. A changed classification starts a new workspace in version 1. |
| Use a single Markdown export with traceable sections | One artifact is sufficient to review the first slice and can be reproduced directly from state. |
| Keep generic physical and legal acceptance scenarios | Domain-neutral behavior can be tested from the first slice. Specialized facility, process, and contract templates follow the agent-skill pilot. |
| Require version 1 on every template | Catalog formats can evolve independently of saved workspace state. Custom unversioned templates need a version field. |
| Compose in a fixed order and give each dimension one owner | Base, primary product, ordered secondary products, and filename-ordered overlays give a reproducible checklist with a source for each dimension. Rejecting duplicate IDs prevents implicit overrides. |
| Preserve unresolved applicability in inspection | Partial tag facts can leave overlays or dimensions unresolved and surface which facts are missing. A confirmed single-product tag set still produces the existing version 1 checklist for workspace initialization. |
| Persist draft interviews and append confirmed profiles in v2 | Save the intent and first question before confirmation. Later changes keep their earlier checklist and evidence links. Explicit upgrades preserve legacy workspaces and record unknown provenance. |
| Store question dependencies and an ordered batch of IDs | The interview skill ranks meaningful questions. Python validates the dependency graph and eligibility, and a new thread can recover the batch without duplicating question text. |
| Derive readiness from applicability and evidence | Required unknown applicability stays visible as a gap. Confirmed exclusions and optional gaps can be reported without imposing coverage or implying stakeholder approval. |
| Explain readiness in v2 Markdown | A short explanation helps stakeholders interpret the status at a glance. The status values and JSON output remain compatible. |
| Keep pilot evaluation outside the interview | Maintainers agree on the rubric and get approval for the live session before opening a dialog. Stakeholders answer only the product questions. |
| Run supporting skills independently against the same ledger | A project can investigate, derive requirements, or model where it needs help. Revision-linked Markdown holds the derived details and permits review with the existing state schemas. |
| Introduce v3 state and a single canonical seven-artifact bundle | Findings and requirements become persistent, typed inputs to traceability and readiness. V1 and v2 keep their report contracts. Markdown renders the same bundle in v3. |
| Pin readiness policy to the saved profile | Catalog criteria reuse three-valued applicability. New catalog policy takes effect through a confirmed profile snapshot, and earlier exports remain reproducible. |
| Compute the gate from deterministic checks and sourced judgments | The core can verify links and apply policy. Explicit assessments, reviews, and authorized deferrals are tied to their reviewed content and retained in order. |
| Validate three non-software products with the existing catalog and v3 state | Facility renovation, invoice exception handling, and a services agreement use distinct dimensions, reviews, and optional models. Evidence triggers reuse three-valued applicability, and shared concerns reuse Evaluation and Security. |
| Evaluate external actions against the discovered product's scope | Ask what the product itself performs or directs. This distinguishes an operational payment release from construction or contract performance that happens after the handoff being assessed. The existing Security applicability rule and saved profiles are preserved. |
| Scope the contract readiness gate to drafting handoff | Drafting completeness, disposition of material issues that affect drafting, and review before signature have distinct purposes. Qualified legal review of the eventual agreement covers legal validity and enforceability. |

## Subsequent slices

Expand the catalog in reviewed batches and introduce migrations when the
contracts change.

## Milestone 8

| Decision | Rationale and trade-off |
| --- | --- |
| Start at 0.1.0 and increment the patch component by default | Only an explicit decision increases a parent component. Release numbering is independent of schema versions and approval for breaking changes. |
| Ship reference-guide and Accessibility as separate catalog additions | Source authority and correction ownership belong to the guide. A barrier to completing a task can arise in a guide or a facility. The optional overlay preserves earlier mandatory coverage. |
| Compare authored catalog definitions before an update | Conservative comparison surfaces changed meaning, ordering and mandatory work for review. Existing state continues to use its saved snapshots. |
