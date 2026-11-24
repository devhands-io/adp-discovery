# adp-discovery

A local product discovery framework for agent hosts that can load its
interview skill. Use it to turn an early idea into a discovery brief with
confirmed decisions, open questions, and a preliminary readiness assessment.

## Skills

| Skill | When to use it | What it produces |
| --- | --- | --- |
| [`interview`](.agents/skills/interview/SKILL.md) | Start discovery, resume a saved interview, or reconcile conflicting stakeholder answers. | A saved checklist and working record of evidence, decisions, assumptions, risks, contradictions, and open questions. On request, a Markdown baseline for review. |

The current release includes `interview`. Later milestones cover
`investigate` for gathering evidence, `define-requirements` for drafting
requirements, and `model-product` for modeling the product.

## Try the interview skill

### 1. Open the project

Get a copy of the full repository, including the hidden `.agents/` folder, and
open the repository root as a workspace in an agent host that can load the
skill. With Python 3.10 or newer, run these commands from the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.adp_discovery validate
```

On Windows PowerShell, create the environment with `py -m venv .venv`, then
activate it with `.\.venv\Scripts\Activate.ps1` before installing dependencies.

### 2. Start a sample interview

Load the interview skill from `.agents/skills/interview/SKILL.md` using your
host's supported method. Then send this prompt or swap in an idea of your own.

> Help me discover a skill that turns meeting notes into a decision
> register. Save progress under .discovery/meeting-decisions/.

Confirm or correct the proposed product type and tags, then answer two or three
follow-up questions. For the sample, you could say that the register is for the
project team and should capture each decision and its owner. Say when you’re
unsure about something. The skill saves progress in
`.discovery/meeting-decisions/state.json` as you go.

Answer in the host's built-in question dialog when it is available. In sessions
without one, the agent asks in chat.

### 3. Resume and export

Start a fresh chat in the same workspace, load the interview skill, and use
the saved state to pick up where you left off.

> Resume .discovery/meeting-decisions/state.json and continue from the
> highest-impact unresolved question.

Then ask for a baseline, even if the interview is still in progress.

> Export the baseline for .discovery/meeting-decisions/state.json to
> .discovery/meeting-decisions/baseline.md and summarize the blockers.

Open `.discovery/meeting-decisions/baseline.md` and check whether the brief
reflects your idea, the decisions match what you confirmed, and open questions
and blockers are easy to find.

### 4. Share feedback

Reply to whoever invited you to try the skill. A few bullets are enough.

- **Setup and resume** — Where did you get stuck, if anywhere? Did the new chat
  pick up the decisions you had already made?
- **Interview** — Which question helped you make a decision? Which felt
  repetitive, unclear, or missing?
- **Baseline** — What did it capture accurately? What did it miss or treat as
  settled too early?

If something broke, include the prompt and error message, with any sensitive
details removed.

## Command-line reference

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
[architecture](docs/architecture.md), and [decision log](docs/decisions.md).
Run the Python tests with `python -m unittest discover -s tests -v`. Use the
[live acceptance scenarios](docs/acceptance.md#stakeholder-question-delivery)
to verify dialog behavior in your agent host.
