# ADP Discovery

**Devhands ADP (Agentic Development Platform)** is an AI-native software
development environment where people and agents plan, execute, verify, and
release work together.

**ADP Discovery** is a local product discovery framework for agent hosts that
can load its interview skill. Turn an early idea into a reviewable discovery
brief with confirmed decisions, open questions, and a preliminary readiness
assessment.

## Skills

| Skill | When to use it | What it produces |
| --- | --- | --- |
| [`interview`](.agents/skills/interview/SKILL.md) | Start discovery, resume a saved interview, or reconcile conflicting stakeholder answers. | A saved discovery workspace with classification, evidence, decisions, and the next question batch. On request, a Markdown baseline for review. |

The current release includes `interview`. Later milestones cover
`investigate` for gathering evidence, `define-requirements` for drafting
requirements, and `model-product` for modeling the product.

## Try the interview skill

Already have the project and a Python environment with its dependencies?
Jump to [Start a sample interview](#2-start-a-sample-interview). You can send
the prompt as soon as the agent has the project open. The Python dependencies
are needed when the skill runs commands to load the checklist, save progress,
or export a baseline.

### 1. Get the project and set up Python once

**Download ZIP.** [Download the ZIP from GitHub](https://github.com/devhands-io/adp-discovery/archive/refs/heads/main.zip),
unzip it, and open a terminal in the extracted `adp-discovery-main` folder.
On GitHub, you can also choose **Code → Download ZIP**.

**Or use Git.** Paste these commands into your terminal:

```sh
git clone https://github.com/devhands-io/adp-discovery.git
cd adp-discovery
```

Both options include the skill, templates, and Python code. If you need to set
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

### 2. Start a sample interview

Open the project folder in your agent app or launch its CLI from that folder.
Use the prompt for your agent, or swap in an idea of your own.

#### Codex

Codex discovers the interview skill in `.agents/skills/`. Mention `$interview`
in your prompt. [Codex skills documentation](https://learn.chatgpt.com/docs/build-skills)

> $interview Help me discover a skill that turns meeting notes into a decision
> register. Save progress under `.discovery/meeting-decisions/`.

#### Claude Code

Claude Code looks for project skills in `.claude/skills/`. Use the skill
directly from its existing project path by asking Claude Code to read it.
[Claude Code skills documentation](https://code.claude.com/docs/en/skills#skills-locations)

> Read and follow `.agents/skills/interview/SKILL.md`. Help me discover a
> skill that turns meeting notes into a decision register. Save progress under
> `.discovery/meeting-decisions/`.

#### OpenCode

OpenCode discovers project skills in `.agents/skills/`. Mention `@interview`
in your prompt. If your version does not recognize that mention, use the
file-based prompt above. [OpenCode skills documentation](https://opencode.ai/docs/skills/)

> @interview Help me discover a skill that turns meeting notes into a decision
> register. Save progress under `.discovery/meeting-decisions/`.

#### During the interview

The skill saves a draft before classification. Confirm or correct the proposed
product type and share what you know about the tags. For the sample, you could
say that the register is for the project team and should capture each decision
and its owner. Say when you’re unsure about something. The skill saves progress in
`.discovery/meeting-decisions/state.json` as you go.

Answer in the host's built-in question dialog when it is available. In sessions
without one, the agent asks in chat.

### 3. Resume and export

Start a fresh chat in the same folder and paste this prompt.

> Read and follow `.agents/skills/interview/SKILL.md`. Resume
> `.discovery/meeting-decisions/state.json` and continue with the saved question
> batch. If the batch is empty, review the remaining gaps.

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

Run these commands from the project folder. On Windows PowerShell, use
`.\.venv\Scripts\python.exe` in place of `.venv/bin/python`.

To start a new draft from the CLI, run `init` once. If you already started the
sample interview above, use its saved state with `show` and `report`.

```sh
.venv/bin/python -m src.adp_discovery init .discovery/meeting-decisions/state.json --project meeting-decisions --title "Meeting decisions"
```

```sh
.venv/bin/python -m src.adp_discovery catalog
.venv/bin/python -m src.adp_discovery compose --product agent-skill --partial --no-tag sensitive-data
.venv/bin/python -m src.adp_discovery show .discovery/meeting-decisions/state.json
.venv/bin/python -m src.adp_discovery report .discovery/meeting-decisions/state.json > .discovery/meeting-decisions/baseline.md
.venv/bin/python -m src.adp_discovery report .discovery/meeting-decisions/state.json --format json
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
For more detail, see the [interview workflow reference](.agents/skills/interview/references/workflow.md),
[state and CLI reference](.agents/skills/interview/references/state.md),
[architecture](docs/architecture.md), and [decision log](docs/decisions.md).
Run the Python tests with `python -m unittest discover -s tests -v`. Use the
[live acceptance scenarios](docs/acceptance.md#stakeholder-question-delivery)
to verify dialog behavior in your agent host.
