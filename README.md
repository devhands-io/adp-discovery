# adp-discovery

A local product discovery framework for Codex. Use it to turn an early idea
into a discovery brief with confirmed decisions, open questions, and a
preliminary readiness assessment.

## Skills

| Skill | When to use it | What it produces |
| --- | --- | --- |
| [`$interview`](.agents/skills/interview/SKILL.md) | Start discovery, resume a saved interview, or reconcile conflicting stakeholder answers. | A saved checklist and working record of evidence, decisions, assumptions, risks, contradictions, and open questions. On request, a Markdown baseline for review. |

The current release includes `$interview`. Later milestones cover
`$investigate` for gathering evidence, `$define-requirements` for drafting
requirements, and `$model-product` for modeling the product.

## Setup

Run from the repository root with Python 3.10 or newer.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.adp_discovery validate
```

On Windows PowerShell, create the environment with `py -m venv .venv`, then
activate it with `.\.venv\Scripts\Activate.ps1` before installing dependencies.

## Run an interview

### Start

Open this repository as a Codex workspace and enter a prompt like this in chat.

> $interview Help me discover a skill that turns meeting notes into a decision
> register. Save progress under .discovery/meeting-decisions/.

Confirm the proposed product type and tags, then answer the skill's follow-up
questions. The catalog offers `agent-skill` for agent skills and `general` for
other products. Product type and tags determine which Security and Evaluation
questions apply. The skill saves progress in
`.discovery/meeting-decisions/state.json`.

### Resume

To resume after an interruption, start a fresh chat in the same workspace and
name the saved state:

> $interview Resume .discovery/meeting-decisions/state.json and continue from the
> highest-impact unresolved question.

### Export

Ask Codex to generate a baseline from the saved state.

> $interview Export the baseline for .discovery/meeting-decisions/state.json to
> .discovery/meeting-decisions/baseline.md and summarize the blockers.

The baseline includes the brief, decision register, open questions, and
preliminary readiness. Each covered required dimension points to a confirmed
decision and its evidence. Missing support and blocking records stay visible
for stakeholder review.

You can also inspect state and export directly from the repository root with
the virtual environment active.

```sh
python -m src.adp_discovery catalog
python -m src.adp_discovery show .discovery/meeting-decisions/state.json
python -m src.adp_discovery report .discovery/meeting-decisions/state.json > .discovery/meeting-decisions/baseline.md
python -m src.adp_discovery report .discovery/meeting-decisions/state.json --format json
```

Working state and exports placed in `.discovery/` are local and Git-ignored.
The JSON report contains the readiness findings and blocking record IDs.

## Included pilot

The [self-discovery pilot](examples/self-discovery/pilot.md) uses the supplied
project brief to discover the framework's first interview skill. Replay its
[checked-in state](examples/self-discovery/state.json):

```sh
python -m src.adp_discovery report examples/self-discovery/state.json
```

You can also open the [generated pilot baseline](examples/self-discovery/baseline.md).
For more detail, see the [interview workflow reference](.agents/skills/interview/references/workflow.md),
[architecture](docs/architecture.md), [decision log](docs/decisions.md), and
[acceptance scenarios](docs/acceptance.md). Run the acceptance tests with
`python -m unittest discover -s tests -v`.
