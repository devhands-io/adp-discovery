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
the session provides one. Otherwise it explains the fallback and asks in chat.
An unanswered question stays open. Confirmation and dependent steps require
an explicit stakeholder reply. Python commands operate on the resulting
workspace state.

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
inspection. `init` takes a confirmed primary product and tag set for the
version 1 workspace profile.

## State contract

Version 1 is a JSON document governed by the state schema. The saved profile
contains the exact dimensions, their sources, and applied overlays. New
catalog revisions affect new interviews. If a classification changes in this
version, initialize a new workspace with the corrected profile, retain the
previous workspace, and carry forward compatible evidence and decisions.

The working ledger stores evidence, decisions, assumptions, risks, questions,
and contradictions with stable IDs, checklist links, and record references.
Save validates the full candidate, retains record identities, preserves
recorded evidence and established decision wording, and increments the revision
after checking for stale edits. Writers use a per-file lock directory and
atomic replacement. Following a terminated writer, remove the adjacent
`.state.json.lock` directory only after verifying that no writer is active.

## Readiness contract

A required dimension is covered by a confirmed decision that links to at
least one evidence record for that dimension. Every uncovered required
dimension names its missing support. An open contradiction, reopened
decision, or open blocking question or risk prevents baseline readiness.
Optional dimensions and nonblocking gaps remain available for review.
Stakeholders evaluate the substance and sufficiency of the evidence.

The Markdown export is a point-in-time review of one state revision. JSON
report output gives machine-readable preliminary readiness findings.
