# Visionary Workflow Template

A production-ready workflow template for Claude Code that turns AI-augmented development into a structured, repeatable process — with automated validation, multi-session coordination, and full lifecycle hooks.

## Quick Start

```
1. Copy this template into your project directory
2. Open Claude Code
3. Run /init-project
```

The wizard walks you through naming your project, defining your vision, and setting up your first milestone. Everything else is automatic.

See [SETUP.md](SETUP.md) for detailed configuration and customization options.

### Optional Dependencies

None of these are required. Each feature degrades gracefully when its dependency is missing.

```bash
pip install pyttsx3       # Spoken TTS notifications (completions, subagent summaries)
pip install anthropic     # LLM-powered agent naming and completion messages
pip install ruff          # Auto-lint on every Write/Edit
pip install ty            # Auto-type-check on every Write/Edit
```

## How It Works

Development is organized into **phases**, each following a four-step cycle:

```
/discuss-phase 1  -->  /plan-phase 1  -->  /execute-phase 1  -->  /verify-work 1
     |                      |                      |                      |
  Capture             Create atomic         Implement with         Validate against
  decisions           task plans             auto-validation        requirements
```

Between phases, use `/pause-work` and `/resume-work` to maintain context across sessions. The template handles checkpointing, handoff notes, and session state automatically.

For parallel work, use `/add-task` to queue work items and `/tandem` to launch additional worker sessions that pull from the shared queue.

## What's Included

| Component | Count | Location |
|-----------|-------|----------|
| Slash Commands | 31 | `.claude/commands/` |
| Specialized Agents | 9 | `.claude/agents/` |
| Lifecycle Hooks | 41 | `.claude/hooks/` |
| Status Line Styles | 8 | `.claude/status_lines/` |
| Output Styles | 8 | `.claude/output-styles/` |
| Reusable Skills | 3 | `.claude/skills/` |
| Worker Scripts | 3 | `.claude/scripts/` |

## Commands

### Core Workflow

| Command | What It Does |
|---------|-------------|
| `/init-project` | Interactive wizard: name your project, define vision, create roadmap |
| `/discuss-phase N` | Capture requirements and decisions before planning phase N |
| `/plan-phase N` | Break phase N into atomic, verifiable task plans |
| `/execute-phase N` | Implement the plans with automatic progress tracking |
| `/verify-work N` | Walk through user acceptance testing for phase N |

### Planning and Execution

| Command | What It Does |
|---------|-------------|
| `/plan-w-team` | Create a team-orchestrated plan with builder/validator agent assignments |
| `/build <plan>` | Deploy builder and validator agents to execute a plan file |
| `/cook` | Launch parallel subagents for independent tasks |
| `/quick` | Fast execution for small, ad-hoc tasks (skips full planning) |

### Session Management

| Command | What It Does |
|---------|-------------|
| `/pause-work` | Save current state, create handoff notes for the next session |
| `/resume-work` | Restore context from a previous session and continue |
| `/progress` | Show current project status, phase, and next steps |
| `/prime` | Load project context into conversation (read-only) |

### Multi-Session Workers

| Command | What It Does |
|---------|-------------|
| `/add-task` | Add a task to the persistent work queue |
| `/list-tasks` | View work queue with status of all tasks |
| `/claim-task` | Claim a queued task for the current session |
| `/complete-task` | Mark a claimed task as done |
| `/remove-task` | Remove a task from the queue |
| `/tandem` | Launch an additional worker session for parallel execution |

### Code Quality

| Command | What It Does |
|---------|-------------|
| `/review` | Thorough code review with actionable feedback |
| `/full-review-pipeline` | Complete review pipeline with quality gates |
| `/test` | Smart test runner based on changed files |
| `/check-invariants` | Validate code against project-defined invariants |
| `/commit-push-pr` | Automated commit, push, and PR creation |

### Utilities

| Command | What It Does |
|---------|-------------|
| `/explain` | Plain-language code explanations |
| `/question` | Research-only mode (no code modifications) |
| `/analyze-codebase` | Bootstrap codebase intelligence for an existing project |
| `/update-status-line` | Write custom key-value pairs to the status bar |
| `/add-todo` | Capture ideas for later without interrupting current work |
| `/complete-milestone` | Archive a milestone and tag the release |
| `/new-milestone` | Start a new version/milestone |

## Agents

| Agent | Model | Role |
|-------|-------|------|
| **builder** | opus | Implements code changes with per-edit ruff/ty validation |
| **validator** | opus | Reviews code in read-only mode (cannot modify files) |
| **meta-agent** | sonnet | Creates new agent definitions on demand |
| **research** | sonnet | Deep web research with multi-source verification |
| **code-simplifier** | - | Reviews code and suggests simplifications |
| **debug-helper** | - | Systematic debugging assistance |
| **verify-app** | - | QA testing and verification |
| **greeting** | haiku | Friendly session greeting |
| **work-completion** | haiku | Spoken TTS summary of completed work |

## Lifecycle Hooks

All 12 Claude Code lifecycle events are covered:

| Event | What Happens |
|-------|-------------|
| **SessionStart** | Injects project context, detects branch and recent commits, sets up session state |
| **UserPromptSubmit** | Logs prompts, names agents, validates input |
| **PreToolUse** | Blocks dangerous Bash commands, checks file conflicts between sessions, registers session heartbeat |
| **PermissionRequest** | Auto-allows read-only tools and safe Bash patterns |
| **PostToolUse** | Runs ruff + ty on every edit, validates JSON/markdown, tracks file changes, indexes codebase, validates commit messages |
| **PostToolUseFailure** | Tracks errors, warns on repeated failures |
| **Notification** | TTS spoken notifications |
| **SubagentStart** | Tracks spawned agents in session state |
| **SubagentStop** | TTS summary of what the subagent accomplished |
| **Stop** | Reminds about uncompleted tasks, creates git snapshot, writes devlog entry, cleans up session locks |
| **PreCompact** | Backs up transcript before context compaction |
| **SessionEnd** | Finalizes session audit data |

## Multi-Session Coordination

The template includes a full coordination system for running multiple Claude Code sessions in parallel:

- **Session registry** — Each session registers itself and maintains a heartbeat. Stale sessions (>30 min inactive) are automatically cleaned up.
- **File locking** — When one session edits a file, other sessions are warned before touching it. Prevents merge conflicts.
- **Task claiming** — When a session starts working on a task, it claims it. Other sessions see the claim and work on something else.
- **Work queue** — A persistent shared queue (`/add-task`, `/claim-task`, `/complete-task`) that multiple workers can pull from.
- **OS-level file locks** — All shared JSON state files use cross-platform file locking (Windows `msvcrt` / Unix `fcntl`) to prevent race conditions during concurrent read-modify-write operations.

## Status Lines

The status bar shows live session info. Switch styles by editing `settings.json`:

| Style | Example Output |
|-------|---------------|
| v1 basic | `project \| branch \| Model` |
| v2 smart prompts | `project \| branch \| Model \| 5 prompts` |
| v3 agent sessions | `project \| branch \| Model \| Agent: Phoenix` |
| v5 cost tracking | `project \| branch \| $0.12 \| 45s` |
| **v6 context bar** (default) | `project \| branch \| Model \| [####....] 42% \| $0.12` |
| v7 duration | `project \| branch \| 12m 34s \| $0.12` |
| v8 token stats | `project \| In: 15.2k \| Out: 4.5k \| 42% ctx \| $0.12` |
| v9 powerline | Powerline-style with background colors and Unicode glyphs |

To change: edit `.claude/settings.json` > `statusLine.command` to point at a different `v*.py` file.

## Output Styles

Available in `.claude/output-styles/` for use as custom output formats:

| Style | Best For |
|-------|----------|
| genui | Standalone HTML5 pages |
| ultra-concise | Minimal, no-frills responses |
| tts-summary | TTS-friendly (no markdown symbols) |
| table-based | Data-heavy responses |
| yaml-structured | Machine-readable output |
| bullet-points | Scannable lists |
| html-structured | Embeddable HTML fragments |
| markdown-focused | Rich markdown documentation |

## Customization

### Adding Project Invariants

Define rules that every code change must satisfy. Edit `.claude/hooks/validators/invariant_validator.py`:

```python
INVARIANTS = [
    {
        "id": "INV-1",
        "name": "No Debug Statements",
        "patterns": [
            (r"console\.log\(", "Use logger instead"),
        ],
        "components": ["src/*"],
        "severity": "error",
    }
]
```

These run automatically on every Write/Edit and block violations.

### Configuring Auto-Allow Permissions

The `permission_request.py` hook auto-approves safe operations (read-only tools, git commands, test runners). Customize the allowlists in `.claude/hooks/lifecycle/permission_request.py`.

### TTS Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `ENGINEER_NAME` | "Developer" | Personalized TTS messages |
| `ANTHROPIC_API_KEY` | (none) | LLM-powered agent naming and completion messages |

TTS rate and volume are adjustable in `.claude/hooks/utils/constants.py`.

## Architecture

```
.claude/
  commands/           # 31 slash commands (markdown with YAML frontmatter)
  agents/             # 9 agent definitions (team/builder, team/validator, meta-agent, etc.)
  hooks/
    intel/            # Codebase indexer, event logger, file tracker, test tracker
    lifecycle/        # All 12 lifecycle event handlers
    session/          # Multi-session coordination, task claiming, file conflicts
    validators/       # Commit, JSON, markdown, ruff, ty, invariant validators
    utils/            # Shared utilities:
      file_lock.py        # Cross-platform OS-level file locking for JSON RMW
      constants.py        # Shared config (paths, models, TTS settings)
      platform_compat.py  # Windows/Unix compatibility
      stdin_parser.py     # Hook input parsing
      tts/                # TTS wrapper with graceful degradation
      llm/                # Anthropic client with wordlist fallback
  scripts/            # Work queue manager, worker launcher, session status
  status_lines/       # 8 status bar styles
  output-styles/      # 8 output format templates
  skills/             # 3 reusable skill definitions
  settings.json       # Hook wiring, permissions, env vars, status line config
```

### Graceful Degradation

Every optional feature works when its dependency is missing:

| Dependency | When Missing |
|------------|-------------|
| pyttsx3 | TTS calls silently return False |
| anthropic SDK | Agent names use wordlist fallback, completions use static messages |
| ruff / ty | Validators output empty JSON (pass silently) |
| ANTHROPIC_API_KEY | LLM features fall back to zero-cost alternatives |

### Security

- **Dangerous command checker** blocks `rm -rf`, `git reset --hard`, `DROP TABLE`, `.env` exposure, and 30+ destructive patterns
- **Safe pattern allowlist** permits `.env.sample`, `.env.example`, etc.
- **Research agent** has read-only Bash access (git ls-files, ls, dir only)
- **Validator agent** cannot Write, Edit, or NotebookEdit

## Requirements

**Required:**
- Claude Code (CLI or VSCode extension)
- Git
- Python 3.11+ (hooks are Python scripts)

**Optional:** See [Optional Dependencies](#optional-dependencies) above.

## License

MIT

---

*Created by visionary-architect*
