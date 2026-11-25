# Review a meeting decision

Worked example for the interaction-model pilot, discovery revision 13. One person models the workflow of opening a decision, reviewing it, and returning to the list. The YAML illustrates one possible notation. The content and control labels are examples. Each action names its destination so a reader can follow the same task as a viewer.

```yaml
scope: Review a meeting decision
scenarios:
  review-and-return:
    capability: Review a decision and return to the register
    start: decision-list
    steps: [open-review, save-review, return-to-list]
  leave-review:
    capability: Leave the review form
    start: decision-list
    steps: [open-review, back-to-list]
screens:
  decision-list:
    title: Decision list
    elements:
      - {type: text, value: Publish the revised launch checklist}
    actions:
      open-review: {label: Review decision, go: review-form}
  review-form:
    title: Review decision
    elements:
      - {type: form, label: Decision review, fields: [{type: text-field, label: Decision, example: Publish the revised launch checklist}]}
    actions:
      save-review: {label: Save, go: decision-details}
      back-to-list: {label: Back, go: decision-list}
  decision-details:
    title: Decision details
    elements:
      - {type: text, value: Publish the revised launch checklist}
    actions:
      return-to-list: {label: Return to list, go: decision-list}
```

## Walkthrough for the implementation pilot

The block above shows the expected corrected flow. For a rehearsal, start with Save pointing to the list and omit the return action on the details screen. Keep the intended user tasks available when reviewing coverage.

1. Describe the review task. Open the form and select Save. In chat, ask for Save to open Decision details. Retry Save from the same example form and check its destination.
2. Review which screens and routes support the task. Ask whether the modeler can get back to the register from details. Add the missing route, then replay both scenarios and explicitly confirm coverage.
3. Open a copy of this single corrected file in a fresh location with the compatible viewer. Replay both scenarios using the embedded example content.

The form exercises navigation with example data. Persistence of field edits has no acceptance criterion in this pilot. The return path illustrates a missing product behavior that checking declared destinations alone would miss.

Source decisions include `screen-navigation-minimum`, `correcting-a-flow-decision`, `screen-list-finalization-decision`, `single-modeler`, and `walkthrough-handoff-decision`. For a post-confirmation edit, return to the changed screen, retry the action, and let the modeler choose any additional replay before confirming again (decision `modeler-chooses-replay`).
