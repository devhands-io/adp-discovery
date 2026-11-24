# Discovery architecture

| Component | Owns |
| --- | --- |
| Interview skill | Classification proposals, stakeholder confirmation, question selection and delivery, evidence interpretation, and contradiction analysis |
| Agent host | Availability and presentation of built-in question dialogs |
| Catalog | Product-neutral and domain-specific dimensions, tag definitions, and applicability rules |
| Python commands | Schema validation, rule evaluation, ordered composition, state integrity, and preliminary evidence coverage |
| Workspace state | Checklist snapshot, discovery summary, and traceable working records |
| Generated baseline | A reviewable view of the saved revision, including decisions, gaps, and readiness |
| Stakeholders | Confirmation of decisions, evaluation of evidence quality, and approval of the baseline |

The product type describes what is being discovered. The base template also
serves as the `general` profile for digital, physical, operational, knowledge,
agent-native, or legal and governance products that lack a specialized
template. Applicability tags describe independent facts about the product.

## Interview interaction contract

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

## Readiness contract

A required dimension is covered by a confirmed decision that links to at
least one evidence record for that dimension. Every uncovered required
dimension names its missing support. An open contradiction, reopened
decision, or open blocking question or risk prevents baseline readiness.
V2 reports optional dimensions, exclusions, and unknown applicability
explicitly. Draft classification and unknown applicability for a potentially
required dimension prevent preliminary readiness. Optional dimensions,
confirmed exclusions, and nonblocking gaps remain available for review.
Stakeholders evaluate the substance and sufficiency of the evidence and
approve the baseline independently of the question frontier.

The Markdown export is a point-in-time review of one state revision. JSON
report output gives machine-readable preliminary readiness findings.
The v2 Markdown report explains the computed status and identifies stakeholder
approval as a separate step.
