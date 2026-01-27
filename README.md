# visionary_template_1

A comprehensive workflow template for AI-augmented software development.

## What This Is

This is the Visionary workflow template created by visionary-architect. It provides a structured approach to AI-augmented software development, including phase-based planning, automated validation, persistent task tracking, and session continuity.

## How It Works

The template organizes development into phases, each with:

1. **Discussion** - Capture requirements, constraints, and key decisions
2. **Planning** - Create atomic, verifiable task plans
3. **Execution** - Implement with automatic progress tracking
4. **Verification** - Validate against requirements

This approach ensures work is trackable, resumable, and maintains quality throughout.

## Key Features

- **25 Slash Commands** - Streamlined workflows for common development tasks
- **3 Specialized Agents** - Code review, debugging, and QA assistance
- **Persistent Task Tracking** - Tasks survive across sessions
- **Multi-Session Coordination** - Handoff notes prevent context loss
- **Autonomous Learning** - Claude updates documentation as it learns
- **Tech-Stack Agnostic** - Works with any language or framework
- **Optional Automation** - Codebase indexer and validators available (requires Python)

## Getting Started

1. **Copy this template** to your project directory
2. **Run `/init-project`** to start the wizard

That's it! The wizard will:
- Ask for your project name and configure all template files automatically
- Guide you through defining your vision, requirements, and roadmap
- Set up everything you need to start Phase 1

See [SETUP.md](SETUP.md) for detailed instructions and customization options.

## Template Contents

| Path | Purpose |
|------|---------|
| `.claude/commands/` | 25 workflow commands |
| `.claude/skills/` | Reusable skill definitions |
| `.claude/agents/` | Specialized AI agents |
| `.claude/hooks/` | Validators and codebase indexer |
| `.planning/` | Planning artifacts (auto-populated) |
| `CLAUDE.md` | Project context for Claude |
| `STATE.md` | Current session state |
| `DEVLOG.md` | Development history |

## Commands Overview

### Core Workflow
| Command | Purpose |
|---------|---------|
| `/init-project` | Initialize project with vision and roadmap |
| `/discuss-phase N` | Capture decisions for phase N |
| `/plan-phase N` | Create atomic task plans |
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
| `/commit-push-pr` | Automated git workflow |
| `/test` | Smart test runner |
| `/review` | Comprehensive code review |

### Multi-Session Workers
| Command | Purpose |
|---------|---------|
| `/add-task` | Add task to persistent work queue |
| `/list-tasks` | View work queue status |
| `/claim-task` | Claim a queued task |
| `/complete-task` | Mark claimed task done |
| `/tandem` | Launch parallel worker session |

## Customization

### Adding Project Invariants (Optional - Requires Python)

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

### Adding Component Documentation

For larger projects, create component-specific CLAUDE.md files:

```
src/
├── api/
│   └── CLAUDE.md    # API patterns
├── core/
│   └── CLAUDE.md    # Core logic patterns
└── ui/
    └── CLAUDE.md    # UI patterns
```

## Requirements

**Required:**
- Claude Code (CLI or VSCode extension)
- Git

**Optional (for advanced features):**
- Python 3.8+ (only needed if using codebase indexer or validators)

## License

MIT - Use freely in your projects.

---

*Created with visionary_template_1 v1.1*
