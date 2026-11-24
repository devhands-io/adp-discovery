# Discovery architecture

| Component | Owns |
| --- | --- |
| Interview skill | Classification proposals, stakeholder confirmation, question selection and delivery, evidence interpretation, and contradiction analysis |
| Agent host | Availability and presentation of built-in question dialogs |
| Catalog | Product-neutral and domain-specific dimensions, tag definitions, overlay conditions |
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

`templates/base.yaml` defines base dimensions and known tags. One entry in
`templates/products/` adds product-specific dimensions. Entries in
`templates/overlays/` add dimensions when their rules match. Template IDs
match filenames, with `general` reserved for the base. Template IDs and
dimension IDs are globally unique within the catalog. Validation checks all
rules, including branches that would short-circuit for a given profile.

Each rule has exactly one operator. `product` compares the selected product
ID. `tag` tests membership of a known, confirmed tag. `all` requires each
child to match, `any` requires at least one, and `not` inverts its child.
Both list operators require nonempty lists. Missing tags are false after
the interview confirms the tag set. Dimensions follow base order, product
order, then overlay filename order and declaration order within each overlay.

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
