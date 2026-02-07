# visionary_template_1

A comprehensive workflow template for AI-augmented software development with full lifecycle automation.

## What This Is

This is the Visionary workflow template — a structured approach to AI-augmented software development that includes phase-based planning, automated validation, persistent task tracking, session continuity, TTS notifications, and 33 automated behaviors across all 12 Claude Code lifecycle events.

## How It Works

The template organizes development into phases, each with:

1. **Discussion** - Capture requirements, constraints, and key decisions
2. **Planning** - Create atomic, verifiable task plans (with optional team-based meta-prompting)
3. **Execution** - Implement with automatic progress tracking and per-edit validation
4. **Verification** - Validate against requirements

This approach ensures work is trackable, resumable, and maintains quality throughout.

## Key Features

- **31 Slash Commands** - Streamlined workflows for common development tasks
- **9 Specialized Agents** - Builder, validator, research, meta-agent, code review, debugging, QA, greeting, and work-completion
- **41 Hook Scripts** - Automated behaviors across all 12 lifecycle events
- **8 Status Lines** - From basic to powerline-style with context bars
- **8 Output Styles** - GenUI, ultra-concise, TTS-summary, table-based, YAML, bullet-points, HTML, markdown
- **3 Skills** - Reusable skill definitions
- **Persistent Task Tracking** - Tasks survive across sessions
- **Multi-Session Coordination** - Handoff notes prevent context loss
- **TTS Notifications** - Spoken announcements for completions, subagent work, and notifications
- **Meta-Prompting** - Self-validating plans with Stop hooks that force completeness
- **Autonomous Learning** - The AI updates documentation as it learns
- **Tech-Stack Agnostic** - Works with any language or framework

## Getting Started

1. **Copy this template** to your project directory
2. **Run `/init-project`** to start the wizard

That's it! The wizard will:
- Ask for your project name and configure all template files automatically
- Guide you through defining your vision, requirements, and roadmap
- Set up everything you need to start Phase 1

See [SETUP.md](SETUP.md) for detailed instructions and customization options.

### Optional Dependencies

These are not required but enable additional features:

```bash
# TTS spoken notifications (session completions, subagent summaries)
pip install pyttsx3

# LLM-powered agent naming and completion messages
pip install anthropic
# Then set: ANTHROPIC_API_KEY=sk-ant-...

# Code quality validators (auto-run on every Write/Edit)
pip install ruff mypy
```

## Template Contents

| Path | Purpose | Count |
|------|---------|-------|
| `.claude/commands/` | Workflow commands | 31 |
| `.claude/agents/` | Specialized AI agents | 9 |
| `.claude/hooks/` | Lifecycle hooks, validators, utilities | 41 |
| `.claude/status_lines/` | Status bar configurations | 8 |
| `.claude/output-styles/` | Output format templates | 8 |
| `.claude/skills/` | Reusable skill definitions | 3 |
| `.claude/settings.json` | Hook wiring, permissions, statusLine | - |
| `.planning/` | Planning artifacts (auto-populated) | - |
| `CLAUDE.md` | Project context for the AI | - |
| `STATE.md` | Current session state | - |
| `DEVLOG.md` | Development history | - |

## Commands Overview

### Core Workflow
| Command | Purpose |
|---------|---------|
| `/init-project` | Initialize project with vision and roadmap |
| `/discuss-phase N` | Capture decisions for phase N |
| `/plan-phase N` | Create atomic task plans |
| `/plan-w-team` | Team-based planning with builder/validator agents and self-validating Stop hooks |
| `/execute-phase N` | Implement with progress tracking |
| `/verify-work N` | User acceptance testing |

### Session Management
| Command | Purpose |
|---------|---------|
| `/pause-work` | Create handoff for session break |
| `/resume-work` | Restore context from previous session |
| `/progress` | Show current status |

### Utilities
| Command | Purpose |
|---------|---------|
| `/quick` | Fast execution for small tasks |
| `/build <plan>` | Deploy builder/validator agents to execute a plan |
| `/cook` | Launch parallel subagents for concurrent work |
| `/prime` | Load project context (read-only) |
| `/question` | Read-only research mode |
| `/commit-push-pr` | Automated git workflow |
| `/test` | Smart test runner |
| `/review` | Comprehensive code review |
| `/full-review-pipeline` | Complete code review pipeline with quality gates |
| `/explain` | Non-technical code explanations |
| `/check-invariants` | Validate code against project-defined invariants |
| `/update-status-line` | Write custom key-value pairs to status line display |
| `/analyze-codebase` | Bootstrap codebase intelligence for existing code |

### Milestone Management
| Command | Purpose |
|---------|---------|
| `/complete-milestone` | Archive a completed milestone and tag release |
| `/new-milestone` | Start a new version/milestone |
| `/add-todo` | Capture ideas for later without interrupting current work |

### Multi-Session Workers
| Command | Purpose |
|---------|---------|
| `/add-task` | Add task to persistent work queue |
| `/list-tasks` | View work queue status |
| `/claim-task` | Claim a queued task |
| `/complete-task` | Mark claimed task done |
| `/remove-task` | Remove a task from the work queue |
| `/tandem` | Launch parallel worker session |

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `builder` | opus | Implements code with per-edit ruff/ty validation |
| `validator` | opus | Reviews code (cannot Write/Edit — read-only) |
| `meta-agent` | sonnet | Creates new agents on demand |
| `research` | sonnet | Deep web research with multi-source verification |
| `code-simplifier` | - | Reviews code and suggests simplifications |
| `debug-helper` | - | Systematic debugging assistance |
| `verify-app` | - | QA testing and verification |
| `greeting` | haiku | Proactive session greeting |
| `work-completion` | haiku | TTS work summaries |

## Lifecycle Hooks (12 Events)

All 12 Claude Code lifecycle events are wired:

| Event | Hook | Sync | What It Does |
|-------|------|------|-------------|
| SessionStart | `session_start.py` | sync | Context injection, project detection, env setup |
| UserPromptSubmit | `user_prompt_submit.py` | sync | Prompt logging, agent naming, empty-prompt blocking |
| PreToolUse | `dangerous_command_checker.py` | sync | Blocks destructive Bash commands |
| PermissionRequest | `permission_request.py` | sync | Auto-allows read-only tools and safe Bash patterns |
| PostToolUse | `ruff_validator.py`, `ty_validator.py` | sync | Per-edit lint and type checking |
| PostToolUseFailure | `post_tool_use_failure.py` | sync | Error tracking, repeat-failure warnings |
| Notification | `notification.py` | async | TTS spoken notifications |
| SubagentStart | `subagent_start.py` | async | Spawn tracking in session JSON |
| SubagentStop | `subagent_stop.py` | async | TTS summary of subagent work |
| Stop | `stop_completion.py` + 5 others | async | TTS completion, auto-snapshot, auto-devlog |
| PreCompact | `pre_compact.py` | async | Transcript backup before compaction |
| SessionEnd | `session_end.py` | async | Session finalization and audit |

## Status Lines

Switch between status line styles by editing `settings.json`:

| Style | Output |
|-------|--------|
| `v1_basic` | `project \| branch \| Model` |
| `v2_smart_prompts` | `project \| branch \| Model \| 5 prompts` |
| `v3_agent_sessions` | `project \| branch \| Model \| Agent: Phoenix` |
| `v5_cost_tracking` | `project \| branch \| $0.12 \| 45s` |
| **`v6_context_bar`** (default) | `project \| branch \| Model \| [████░░] 42% \| $0.12` |
| `v7_duration` | `project \| branch \| 12m 34s \| $0.12` |
| `v8_token_stats` | `project \| In: 15.2k \| Out: 4.5k \| 42% ctx \| $0.12` |
| `v9_powerline` | Powerline-style with Unicode glyphs and ANSI colors |

## Output Styles

Available in `.claude/output-styles/` for use as custom output formats:

| Style | Best For |
|-------|----------|
| `genui.md` | Standalone HTML5 pages |
| `ultra-concise.md` | Minimal, no-frills responses |
| `tts-summary.md` | TTS-friendly (no markdown symbols) |
| `table-based.md` | Data-heavy responses |
| `yaml-structured.md` | Machine-readable output |
| `bullet-points.md` | Scannable lists |
| `html-structured.md` | Embeddable HTML fragments |
| `markdown-focused.md` | Rich markdown documentation |

## Customization

### Changing the Status Line

Edit `.claude/settings.json` and change the `statusLine.command`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python .claude/status_lines/v9_powerline.py",
    "timeout": 3000
  }
}
```

### Adding Project Invariants (Requires Python)

Edit `.claude/hooks/validators/invariant_validator.py` to define rules that all code must follow:

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

### Configuring Auto-Allow Permissions

The `permission_request.py` hook auto-allows safe operations. Edit the `SAFE_TOOLS` and `SAFE_BASH_PREFIXES` lists in `.claude/hooks/lifecycle/permission_request.py` to customize.

### TTS Configuration

Set these environment variables (or edit `.env.sample`):

| Variable | Default | Purpose |
|----------|---------|---------|
| `ENGINEER_NAME` | "Developer" | Used in personalized TTS messages |
| `ANTHROPIC_API_KEY` | (none) | Enables LLM-powered agent naming and completion messages |

TTS rate and volume can be adjusted in `.claude/hooks/utils/constants.py`.

### Adding Component Documentation

For larger projects, create component-specific CONTEXT.md files:

```
src/
├── api/
│   └── CONTEXT.md    # API patterns
├── core/
│   └── CONTEXT.md    # Core logic patterns
└── ui/
    └── CONTEXT.md    # UI patterns
```

## Architecture

### Hook Utility System

All hooks share a utility layer in `.claude/hooks/utils/`:

```
hooks/utils/
├── constants.py          # Shared config (paths, LLM model, TTS settings)
├── platform_compat.py    # Cross-platform helpers (Windows + Unix)
├── stdin_parser.py       # Standardized hook input parsing
├── tts/
│   ├── pyttsx3_tts.py    # TTS wrapper with graceful degradation
│   └── tts_queue.py      # Cross-platform file locking for audio
└── llm/
    ├── anthropic_client.py   # Haiku API wrapper with wordlist fallback
    └── task_summarizer.py    # Subagent task summarization
```

### Graceful Degradation

Every optional dependency degrades gracefully:
- **pyttsx3 not installed**: TTS calls silently return False
- **anthropic SDK not installed**: Agent names use wordlist fallback, completions use static messages
- **ruff/mypy not installed**: Validators pass silently
- **No ANTHROPIC_API_KEY**: LLM features fall back to zero-cost alternatives

### Security

- **Dangerous command checker**: Blocks `rm -rf`, `git reset --hard`, `DROP TABLE`, `.env` exposure, and 30+ destructive patterns
- **Safe pattern allowlist**: `.env.sample`, `.env.example` etc. are not blocked
- **Per-match analysis**: Chained commands like `cat .env && cat .env.sample` correctly block the dangerous part
- **Research agent restricted**: Read-only Bash access (git ls-files, ls, dir only)
- **Validator agent restricted**: Cannot Write, Edit, or NotebookEdit

## Requirements

**Required:**
- Claude Code (CLI or VSCode extension)
- Git
- Python 3.11+ (hooks are Python scripts)

**Optional (for enhanced features):**
- `pyttsx3` — TTS spoken notifications
- `anthropic` — LLM-powered agent naming and completion messages
- `ruff` — Per-edit Python linting
- `mypy` or `ty` — Per-edit type checking

## License

MIT - Use freely in your projects.

---

*Created by visionary-architect*
