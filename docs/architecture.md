# Discovery architecture

| Component | Owns |
| --- | --- |
| Interview skill | Classification proposals, stakeholder confirmation, question selection and delivery, evidence interpretation in interviews, and stakeholder reconciliation |
| Supporting skills | Evidence investigation, requirements derivation, and optional conceptual modeling |
| Agent host | Availability and presentation of built-in question dialogs |
| Catalog | Product-neutral and domain-specific dimensions, tag definitions, and applicability rules |
| Python commands | Schema validation, rule evaluation, ordered composition, state integrity, and preliminary evidence coverage |
| Workspace state | Checklist snapshot, discovery summary, and traceable working records |
| Generated artifacts | The canonical JSON bundle and Markdown review of one saved revision |
| Stakeholders | Confirmation of decisions, evaluation of evidence quality, and approval of the baseline |

The product type describes what is being discovered. The base template also
serves as the `general` profile for digital, physical, operational, knowledge,
agent-native, or legal and governance products that lack a specialized
template. Applicability tags describe independent facts about the product.

## Interview interaction contract

The interview workflow and its references live in `.agents/skills/interview/`.
Claude Code discovers `/interview` through `.claude/skills/interview/SKILL.md`,
which passes the user's request to the shared workflow.

The skill asks stakeholder questions through the host's built-in dialog when
the session provides one. If the session has no dialog, the skill explains the
fallback and asks in chat. Each prompt appears once per round. An unanswered
question stays open. Confirmation and dependent steps require an explicit
stakeholder reply. Starting a live pilot requires approval for the interview
itself. Python commands operate on the resulting workspace state.

## Catalog contract

Every catalog YAML file declares `version: 1`. The template schema version is
independent of the saved-state version. To use an existing unversioned custom
template, add `version: 1` at its root.

`templates/base.yaml` declares the base dimensions and the known tag IDs and
descriptions. Each file in `templates/products/` adds product dimensions.
Each file in `templates/overlays/` must declare a template-level `applies`
rule. The base uses the reserved ID `general`. Product and overlay IDs match
their filenames. Template and dimension IDs use lowercase kebab-case and are
globally unique within the catalog. Repeated dimensions fail validation even
when their definitions agree or their conditions are mutually exclusive.

The specialized catalogs include `facility`, `process`, and `contract`.
Select a secondary template when a distinct deliverable is in scope. Reuse
applicable overlays for shared concerns and keep questions about domain
obligations in their product template. Evaluate `external-actions` against
actions the discovered product performs or directs. Effects of downstream
implementation or performance are evaluated in their own discovery scope.

A dimension declares an `id`, a `question`, a Boolean `required` flag, and
an optional `applies` rule. A dimension applies only when both its template
and its own rule apply. With no dimension rule, it follows its template.
`required: true` makes coverage mandatory when the dimension applies.
`required: false` makes coverage optional.

Composition starts with the base, then adds the primary product, secondary
products in input order, and applicable overlays in filename order. It retains
dimension declaration order within each template and includes the source
template ID with every dimension. Selecting `general` as primary uses the
base once. Secondary selections must be distinct specialized product IDs.

Each rule has exactly one operator. `product` tests membership in the selected
primary and secondary product IDs. `tag` tests a known tag. `all` and `any`
take nonempty lists of rules. Validation checks references in every branch.

| Operator | True | False | Unresolved |
| --- | --- | --- | --- |
| `tag` | Present | Absent | Undeclared in partial inspection |
| `all` | All children true | Any child false | Otherwise |
| `any` | Any child true | All children false | Otherwise |
| `not` | Child false | Child true | Child unresolved |

In a confirmed classification, omitted tags are false. In `compose --partial`,
`--tag` marks a tag present and `--no-tag` marks it absent. A tag declared
both ways is an error. True overlays and dimensions are listed in `overlays`
and `dimensions`. Partial inspection also lists `unresolved_overlays` and
`unresolved_dimensions`. Each unresolved entry contains sorted
`unresolved_tags` from the branches that still affect its result. An overlay
entry's `id` identifies its source. Dimension entries use `source`. False
entries are omitted. Secondary products and partial tag facts are inputs to
inspection. `profile` uses the same three-valued evaluation and also emits
false results and the versions of the selected and inspected templates for
a v2 snapshot. Templates for unselected product types are outside that
snapshot. `init --product` retains the v1 behavior.

Templates can also declare readiness criteria. They have globally unique
IDs and follow the same applicability rules as dimensions. V3 profiles
pin the composed definitions, source template, and known or unresolved
applicability. See the [criterion contract](discovery-artifacts.md#catalog-criteria-and-readiness-outcomes).

## State contract

Version 2 starts with `init --project`. The stable project ID, title, intent
summary, evidence, and question batch can be saved before confirmation. An
empty profile history represents a draft. After stakeholder confirmation,
append a catalog snapshot with its confirmation evidence IDs. The latest
snapshot supplies the active profile. Each snapshot pins primary and secondary
products, known tag facts, template versions, dimension text and provenance,
and applicable, unresolved, and inapplicable results. A change in known facts
or confirmed classification appends a snapshot. Older snapshots retain the
dimension IDs needed to interpret earlier records. Reading an existing
workspace does not consult the live catalog.

The ledger stores evidence, preferences, decisions, assumptions, risks,
questions, and contradictions with stable IDs and links. V2 questions can
depend on other questions. Prerequisites must resolve before the dependent
question becomes eligible. Cycles are rejected. The frontier stores up to
three eligible question IDs in asking order. Deferred questions remain open
and stay out of the frontier. The interview skill selects the batch, while
Python checks eligibility.

Save validates the full candidate, retains record identities, preserves
recorded evidence and established decision wording, and increments the
revision after checking for stale edits. Evidence can gain dimension links
in v2. Writers use a per-file lock directory and atomic replacement. Following
a terminated writer, remove the adjacent `.state.json.lock` directory only
after verifying that no writer is active.

V1 files remain readable and writable with their original contract. Their
profile is immutable. The explicit `upgrade PATH --project ID` command
preserves the checklist and ledger, increments the revision, and records
unknown template versions as `null`. It has no source for past classification
confirmation IDs or excluded dimensions, so those entries remain empty.

Version 3 uses `init --project ID --artifacts` for new workspaces and
`upgrade --to 3` for earlier ones. It retains the existing ledger and adds
structured brief claims, findings, requirements, impacts, conditions, and
attestations. The same save protects revision, profile, evidence, and
decision history. Upgraded profiles retain their existing provenance.
A new confirmed profile produced by `profile --artifacts` pins criteria.

## Readiness contract

In the v1 and v2 preliminary report, a required dimension is covered by a
confirmed decision that links to evidence for that dimension. Every uncovered required
dimension names its missing support. An open contradiction, reopened
decision, or open blocking question or risk prevents baseline readiness.
V2 reports optional dimensions, exclusions, and unknown applicability
explicitly. Draft classification and unknown applicability for a potentially
required dimension prevent preliminary readiness. Optional dimensions,
confirmed exclusions, and nonblocking gaps remain available for review.
Stakeholders evaluate the substance and sufficiency of the evidence and
approve the baseline independently of the question frontier.

The v1 and v2 Markdown exports are point-in-time reviews of one state revision.
Their JSON report output gives machine-readable preliminary readiness findings.
The v2 Markdown report explains the computed status and identifies stakeholder
approval as a separate step.

V3 adds a readiness gate with `ready`, `conditionally-ready`, and `not-ready`
outcomes. Python checks references, status and scope, and binds recorded
judgments to the reviewed content. Stakeholders confirm decisions and
provide required reviews and approvals. Agents assess evidence quality,
materiality, and justification. Each artifact references the same source
revision, and Markdown renders the JSON bundle. The [artifact contract](discovery-artifacts.md)
defines the schemas, policy, and workflow.

Product reviews define the handoff under assessment. For example, facilities
review supports design handoff and the contract review supports drafting
handoff. The contract template requires a separate qualified review when a
material issue needs disposition before drafting. Document any review of the
eventual agreement and its sequencing before signature in the baseline.

## Supporting skills

Investigation, requirements, and conceptual modeling are independently
invocable. Each reads the same workspace and uses the ledger for material
evidence, gaps, and contradictions. Supporting skills preserve the interview
frontier. An open contradiction against a confirmed decision reopens that
decision in the same save. The stakeholder settles what governs.

In v3, Investigation and Requirements save structured findings and obligations.
The artifact bundle renders them with confidence rationale and trace links.
Earlier workspaces use revision-linked Markdown outputs. Modeling uses a
representation suited to the product and can be skipped.
See the [workspace and artifact contract](supporting-skills.md).

## Catalog evolution

The repository release identifier lives in `VERSION`. Template format v1,
workspace formats v1–v3, and artifact bundle format v1 have separate version
fields. A template's version identifies its grammar. The definitions in a
confirmed snapshot preserve its content across releases.

Authors can compare two valid catalogs with
`python -m src.adp_discovery --templates NEW validate --against OLD`.
The comparison checks template roles, tag definitions, applicability, entry
ownership and relative order, questions, required flags, and readiness policy.
It accepts a new product, new tags, and optional questions. New criteria,
required additions to existing templates, and mandatory work in a new overlay
require review. It conservatively flags wording and rule rewrites even if an
author believes they are equivalent. It does not evaluate stakeholder meaning.
New optional overlays can add unresolved or excluded entries to fresh snapshots.

For migration, retain published IDs and their meanings. Introduce additive
entries with fresh IDs. For a proposed removal, rename, role change or changed
obligation, obtain explicit approval, document the old-to-new mapping, and
test old state, fresh composition, and a newly confirmed profile. Never rewrite
past snapshots or evidence links to substitute a new ID. V1 keeps its original
checklist. In v2 and v3, adopt changed definitions by appending a confirmed
profile. State format changes use the explicit upgrade command. Unsupported
template formats fail validation before a catalog-based initialization writes state.

### Interaction-model pilot

The optional screen walkthrough uses a Markdown artifact with one YAML model. The Python viewer validates the declared graph, traces intended scenario steps and emits local HTML with fragment links. Review and confirmation stay in the single-modeler conversation. A SHA-256 digest identifies the reviewed Markdown revision in ledger evidence. The viewer reads no workspace state. See the [workflow and format](interaction-model.md).

The interview establishes a scoped scenario inventory before screen design. Stable scenario IDs connect the modeler's intended outcomes to the coverage review. Unmapped scenarios remain visible as gaps in the Markdown.

An action may include a `row` containing its item's display text. The viewer pairs the text with that action and includes the item in its accessible name and coverage trace.

A text field may bind to a stable value ID using `bind`. Matching paragraph and row bindings display its value. A navigation action with `commit: true` saves its screen's bound inputs within the current walkthrough. Other navigation discards drafts. Rendering embeds the editing behavior in the preview.

The viewer opens with task selection and expandable coverage. During a guided replay the browser history entry carries the scenario and current step. The viewer resolves each prompt against the current screen's actions. Missing steps and alternate routes remain available for discussion.

Actions can declare a named event with `reveal`. An action with the matching `visibleAfter` becomes available once that event occurs in the open preview. All roles in that preview see the updated example.

Scenario progress is browser-local and keyed by model source path, scenario ID and route signature. Signatures cover the scenario, traversed actions, and involved screen content. An interrupted run records its last guided step and visibility events. Example field values keep their existing reload behavior. Progress storage is optional; the current visit works in memory when browser storage is unavailable.

Viewer feedback is browser-local and keyed by model revision, scenario, and optional screen and guided step. Scenario notes and screen notes can be edited from the scenario list. Copy notes exports the nonempty entries in scenario order with their references and the reviewed revision.

Interaction modeling reviews the conceptual data model after scenario agreement when the scenarios depend on information. Relevant facts and relationships are traced to the scenarios and screens that use them.
