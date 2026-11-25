# ADP Discovery

**Devhands ADP (Agentic Development Platform)** is an AI-native software
development environment where people and agents plan, execute, verify, and
release work together.

**ADP Discovery** is a local product discovery framework for agent hosts that
can load its skills. Turn an early idea into a reviewable discovery
brief with confirmed decisions, open questions, and a preliminary readiness
assessment.

Current version **0.1.0**. See the [release installation and update guide](docs/releases.md) and the [catalog review](docs/catalog-review.md).

## Skills

| Skill | When to use it | What it produces |
| --- | --- | --- |
| [`interview`](.agents/skills/interview/SKILL.md) | Start discovery, resume a saved interview, or reconcile conflicting stakeholder answers. | A saved discovery workspace with classification, evidence, decisions, and the next question batch. On request, a Markdown baseline for review. |
| [`investigate`](.agents/skills/investigate/SKILL.md) | Verify a claim, assess feasibility, or compare alternatives. | Evidence, findings, and gaps with source links. |
| [`define-requirements`](.agents/skills/define-requirements/SKILL.md) | Turn confirmed decisions and supporting evidence into verifiable requirements. | Requirements with stable IDs, source links, and acceptance criteria or gaps. |
| [`model-product`](.agents/skills/model-product/SKILL.md) | Clarify a structure, relationship, workflow, or responsibility. | An optional `model.md` grounded in discovery evidence and decisions. |

The skills share the [workspace and artifact conventions](docs/supporting-skills.md).

## Try a discovery flow

Use the four skills to discover a meeting decision register. Each follow-up
prompt names the same workspace, so you can continue in a fresh chat.
If you already have the project and its Python dependencies, jump to
[the walkthrough](#walkthrough).

### Set up the project

**Download ZIP.** [Download the ZIP from GitHub](https://github.com/devhands-io/adp-discovery/archive/refs/heads/main.zip),
unzip it, and open a terminal in the extracted `adp-discovery-main` folder.
On GitHub, you can also choose **Code → Download ZIP**.

**Or use Git.** Paste these commands into your terminal:

```sh
git clone https://github.com/devhands-io/adp-discovery.git
cd adp-discovery
```

Both options include the skills, templates, and Python code. If you need to set
up Python for this project, run the commands for your system from the project
folder with Python 3.10 or newer. A virtual environment is recommended to keep
dependencies isolated. If the agent can already use a Python environment with
the packages in `requirements.txt`, skip environment creation and installation.

**macOS or Linux**

```sh
# Create an isolated Python environment in the .venv folder.
python3 -m venv .venv

# Select that environment's Python for this terminal session.
source .venv/bin/activate

# Install the project's Python dependencies into the active environment.
python -m pip install -r requirements.txt

# Optional. Check the catalog and confirm the project commands run.
python -m src.adp_discovery validate
```

Activation is optional when you call `.venv/bin/python` directly in place of
`python`, including from a new terminal or agent session.

**Windows PowerShell**

```powershell
# Create an isolated Python environment in the .venv folder.
py -m venv .venv

# Use that environment's Python directly to install the dependencies.
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Optional. Check the catalog and confirm the project commands run.
.\.venv\Scripts\python.exe -m src.adp_discovery validate
```

The optional check prints `Catalog valid.` when it succeeds.

### Walkthrough

Open the project folder in your agent app or launch its CLI from that folder.
The prompts use Codex syntax. See [how to invoke the skills](#invoke-the-skills)
for other hosts.

#### 1. Start with `interview`

> $interview Help me discover a skill that turns meeting notes into a decision
> register. Save progress under `.discovery/meeting-decisions/`.

Confirm or correct the proposed product type and share what you know about
which tags apply. For this example, tell the agent the project team needs to
capture each decision and its owner. To try the conflict in step 2, start by
allowing inferred owners with a tentative label. Answer in the host's question
dialog when available, or in chat. The interview saves progress to
`.discovery/meeting-decisions/state.json`.

#### 2. Check the evidence with `investigate`

> $investigate In `.discovery/meeting-decisions/state.json`, check what the
> register may show when the notes omit an owner. Use the sample records
> policy in the `owner-policy` record of `examples/meeting-notes/rounds.json`
> and record any conflict with the current decision.

Investigation records the sourced finding and any conflict. If the policy
conflicts with a decision, resume the interview to settle it with the
stakeholder. In the sample, the stakeholder confirms the policy applies and
chooses `unassigned` when the notes omit the owner.

> $interview Resume `.discovery/meeting-decisions/state.json` and ask me to
> resolve any conflict about missing owners.

#### 3. Clarify a handoff with `model-product` (optional)

> $model-product For `.discovery/meeting-decisions/state.json`, check whether
> mapping who drafts the register, reviews it, and resolves unassigned
> entries would clarify responsibilities.

If a map helps, the skill saves it as `model.md` beside the workspace state.
Bring any unresolved responsibilities back to the interview.

#### 4. Derive requirements with `define-requirements`

> $define-requirements From `.discovery/meeting-decisions/state.json`, derive
> requirements and observable acceptance criteria from the confirmed decisions
> and supporting evidence. Flag any gaps.

For the confirmed sample rule, an acceptance check is that a decision with
no named owner appears in the register as `unassigned`.

#### 5. Export and review the baseline

> Export the discovery baseline from `.discovery/meeting-decisions/state.json`
> to `.discovery/meeting-decisions/baseline.md`. Summarize the confirmed
> decisions, requirements, and remaining blockers for stakeholder review.

Send this as a plain request whenever you want a review copy of the saved
workspace. Open the baseline and check that the brief reflects your intent,
the requirements trace back to confirmed decisions, and the remaining
questions and blockers are visible. To answer those questions or revisit
a decision, resume `$interview` with the workspace path.

You can also start with `investigate` when you have a project brief and a
question that needs evidence. Use `model-product` whenever a relationship or
handoff needs clarification. New evidence or open questions can send you
back to an earlier step.

### Invoke the skills

- **Codex** uses `$skill-name` for the skills in `.agents/skills/`.
  [Codex skills documentation](https://learn.chatgpt.com/docs/build-skills)
- **OpenCode** uses `@skill-name` for project skills in `.agents/skills/`.
  [OpenCode skills documentation](https://opencode.ai/docs/skills/)
- **Claude Code** has a bundled `/interview` entry point. For the other
  skills, use the file-based prompt below.
  [Claude Code skills documentation](https://code.claude.com/docs/en/skills#skills-locations)

If your host needs a file-based prompt, use the path from the
[skills table](#skills) in place of the skill mention. For example:

> Read and follow `.agents/skills/investigate/SKILL.md`. Check the sample
> records policy for the workspace at `.discovery/meeting-decisions/state.json`.

### Share feedback

Reply to whoever invited you to try the walkthrough. A few bullets are enough.

- **Setup and resume** — Where did you get stuck, if anywhere? Did the new chat
  pick up the decisions you had already made?
- **Interview** — Which question helped you make a decision? Which felt
  repetitive, unclear, or missing?
- **Skill handoffs** — Did each skill pick up the evidence and decisions it
  needed from the saved workspace?
- **Baseline** — What did it capture accurately? What did it miss or treat as
  settled too early?

If something broke, include the prompt and error message, with any sensitive
details removed.

## Command-line reference

Run these commands from the project folder. On Windows PowerShell, use
`.\.venv\Scripts\python.exe` in place of `.venv/bin/python`.

To start a new draft from the CLI, run `init` once. If you already started the
walkthrough above, use its saved state with `show` and `report`.

```sh
.venv/bin/python -m src.adp_discovery init .discovery/meeting-decisions/state.json --project meeting-decisions --title "Meeting decisions" --artifacts
```

```sh
# List the product types and tags available in the catalog.
.venv/bin/python -m src.adp_discovery catalog

# Preview the agent-skill checklist with sensitive data ruled out and other tags left unknown.
.venv/bin/python -m src.adp_discovery compose --product agent-skill --partial --no-tag sensitive-data

# Display the saved interview state.
.venv/bin/python -m src.adp_discovery show .discovery/meeting-decisions/state.json

# Export a Markdown baseline from the saved state.
.venv/bin/python -m src.adp_discovery report .discovery/meeting-decisions/state.json > .discovery/meeting-decisions/baseline.md

# Print readiness findings and blockers as JSON.
.venv/bin/python -m src.adp_discovery report .discovery/meeting-decisions/state.json --format json

# Export the seven canonical artifacts as one JSON bundle.
.venv/bin/python -m src.adp_discovery artifacts .discovery/meeting-decisions/state.json
```

The example composition applies Evaluation and shows Security as unresolved
pending the `external-actions` tag. Both `compose --partial` and the v2
`profile` command use `--tag` for known present tags and `--no-tag` for known
absent tags. Omitted tags remain unknown. Plain `compose` treats omitted tags
as absent. For catalogs with multiple product templates, repeat
`--secondary-product` in composition order.

Working state and exports placed in `.discovery/` are local and Git-ignored.
The v2 JSON report contains readiness findings, blocking record IDs, and both
the current question batch and eligible question IDs. Existing v1 workspace
files can still be read. Use `upgrade PATH --project ID` to adopt v2 in place.
See [Discovery artifacts and readiness](docs/discovery-artifacts.md) for the
v3 workflow, migration, and reproducible examples.

## Included pilots

The [self-discovery pilot](examples/self-discovery/pilot.md) uses the supplied
project brief to discover the framework's first interview skill. Replay its
[checked-in state](examples/self-discovery/state.json):

```sh
.venv/bin/python -m src.adp_discovery report examples/self-discovery/state.json
```

You can also open the [generated pilot baseline](examples/self-discovery/baseline.md).
The [meeting decision register pilot](examples/meeting-notes/pilot.md) replays
a v2 interview from draft through conflict resolution.
The [Milestone 7 pilots](examples/milestone7/pilot.md) replay v3 discovery for
an existing facility renovation, an invoice exception process, and a services
agreement. They generate the canonical artifacts and separate optional models.
For more detail, see the [interview workflow reference](.agents/skills/interview/references/workflow.md),
[state and CLI reference](.agents/skills/interview/references/state.md),
[architecture](docs/architecture.md), and [decision log](docs/decisions.md).
Run the Python tests with `python -m unittest discover -s tests -v`. Use the
[live acceptance scenarios](docs/acceptance.md#stakeholder-question-delivery)
to verify dialog behavior in your agent host.
