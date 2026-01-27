# Template Setup Guide

This guide walks you through setting up visionary_template_1 for your project.

## Requirements

**Required:**
- the workflow system (CLI or VSCode extension)
- Git

**Optional (for advanced features):**
- Python 3.8+ (only if using codebase indexer or validators)

---

## Quick Start

### Step 1: Copy Template

Copy this template directory to your project location:

```bash
cp -r visionary_template_1 /path/to/your/project
cd /path/to/your/project
```

### Step 2: Initialize Git (if needed)

```bash
git init
```

### Step 3: Run Project Initialization

Start a session and run:
```
/init-project
```

This interactive wizard will:
1. **Ask for your project name and slug** - then automatically replace all placeholders
2. **Guide you through defining your vision** - what you're building and why
3. **Help you scope requirements** - what's in v1.0 vs later
4. **Create your roadmap** - break work into manageable phases

All 7 template files with placeholders are updated automatically - no manual find/replace needed.

### Step 4: Start Building

After initialization, begin Phase 1:
```
/discuss-phase 1
```

---

## Manual Placeholder Replacement (Alternative)

If you prefer to configure placeholders manually instead of using `/init-project`:

| Placeholder | Replace With | Example |
|-------------|--------------|---------|
| `{{PROJECT_NAME}}` | Your project name | "My Awesome App" |
| `{{PROJECT_SLUG}}` | URL-safe identifier | "my-awesome-app" |
| `{{DATE}}` | Today's date | "2026-01-24" |

Files containing placeholders:
- `CONTEXT.md`
- `STATE.md`
- `DEVLOG.md`
- `PROJECT.md`
- `SETUP.md`
- `.claude/settings.json`
- `.claude/scripts/launch-worker.py`

**bash/macOS/Linux:**
```bash
find . -type f \( -name "*.md" -o -name "*.json" \) -exec sed -i 's/{{PROJECT_NAME}}/My Project/g' {} +
find . -type f \( -name "*.md" -o -name "*.json" \) -exec sed -i 's/{{PROJECT_SLUG}}/my-project/g' {} +
find . -type f \( -name "*.md" -o -name "*.json" \) -exec sed -i 's/{{DATE}}/2026-01-24/g' {} +
```

**PowerShell/Windows:**
```powershell
Get-ChildItem -Recurse -Include *.md,*.json | ForEach-Object {
    (Get-Content $_.FullName) -replace '\{\{PROJECT_NAME\}\}', 'My Project' | Set-Content $_.FullName
}
# Repeat for other placeholders
```

---

## Post-Setup Checklist

After running `/init-project`, the wizard handles most configuration automatically:

- [x] Placeholder replacement (project name, slug, date)
- [x] Tech stack permissions in settings.json
- [x] Tech stack details in CONTEXT.md
- [ ] Updated `.gitignore` for your project type (if needed)
- [ ] (Optional) Enabled codebase indexer hook (requires Python)
- [ ] (Optional) Configured invariants (requires Python)
- [ ] (Optional) Created component-specific CONTEXT.md files

---

## Adding More Permissions (Advanced)

The `/init-project` wizard configures permissions for your primary tech stack. If you need additional tools, add them to `.claude/settings.json`:

**Node.js / JavaScript:**
```json
{
  "permissions": {
    "allow": [
      "Bash(npm *)",
      "Bash(npx *)",
      "Bash(yarn *)",
      "Bash(pnpm *)",
      "Bash(node *)"
    ]
  }
}
```

**Python:**
```json
{
  "permissions": {
    "allow": [
      "Bash(python *)",
      "Bash(python3 *)",
      "Bash(pip *)",
      "Bash(uv *)",
      "Bash(pytest*)",
      "Bash(mypy *)",
      "Bash(ruff *)"
    ]
  }
}
```

**Rust:**
```json
{
  "permissions": {
    "allow": [
      "Bash(cargo *)",
      "Bash(rustc *)"
    ]
  }
}
```

**Go:**
```json
{
  "permissions": {
    "allow": [
      "Bash(go *)"
    ]
  }
}
```

**General Build Tools:**
```json
{
  "permissions": {
    "allow": [
      "Bash(make *)",
      "Bash(docker *)",
      "Bash(docker-compose *)"
    ]
  }
}
```

---

## Optional Features

These features provide enhanced functionality but require Python 3.8+. They are **disabled by default** to keep the template tech-stack agnostic.

### Codebase Indexer

Automatically indexes your code files after edits, creating searchable intelligence in `.planning/intel/`.

**To enable:** Add to `.claude/settings.json`:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {"type": "command", "command": "python .claude/hooks/intel/codebase_indexer.py"}
        ]
      }
    ]
  },
  "permissions": {
    "allow": [
      "Bash(python .claude/hooks/intel/*)",
      "Bash(python3 .claude/hooks/intel/*)"
    ]
  }
}
```

**Manual usage:** Run `/analyze-codebase` to index existing code.

### Invariant Validator

Automatically checks code changes against project-specific rules.

**To enable:**

1. Edit `.claude/hooks/validators/invariant_validator.py` to define your invariants:
```python
INVARIANTS = [
    {
        "id": "INV-1",
        "name": "No Debug Statements",
        "description": "Debug statements should not be in production code",
        "patterns": [
            (r"console\.log\(", "Use logger instead of console.log"),
            (r"debugger;", "Remove debugger statements"),
        ],
        "components": ["src/*"],
        "file_extensions": [".js", ".ts"],
        "severity": "error",
    },
]
```

2. Add to `.claude/settings.json` hooks:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {"type": "command", "command": "python .claude/hooks/validators/invariant_validator.py $CLAUDE_FILE_PATH"}
        ]
      }
    ]
  },
  "permissions": {
    "allow": [
      "Bash(python .claude/hooks/validators/*)",
      "Bash(python3 .claude/hooks/validators/*)"
    ]
  }
}
```

**Manual usage:** Run `/check-invariants` to validate all files.

### Other Validators

The template includes additional validators in `.claude/hooks/validators/`:
- `commit_validator.py` - Enforces conventional commit format
- `json_validator.py` - Validates JSON file syntax
- `markdown_validator.py` - Checks markdown formatting

Enable any of these by adding them to your hooks configuration.

---

## Component Documentation

For larger projects, create CONTEXT.md files in component directories:

```
src/
├── api/
│   └── CONTEXT.md    # API-specific patterns, endpoints, auth handling
├── core/
│   └── CONTEXT.md    # Business logic patterns, domain rules
├── db/
│   └── CONTEXT.md    # Database patterns, migrations, repositories
└── ui/
    └── CONTEXT.md    # UI patterns, components, state management
```

Each component CONTEXT.md should include:
- Component purpose
- Key patterns and conventions
- Common gotchas
- Related files

---

## Workflow Overview

### Visionary Workflow

```
/init-project
     ↓
  [Define vision, requirements, roadmap]
     ↓
/discuss-phase 1
     ↓
  [Capture decisions for Phase 1]
     ↓
/plan-phase 1
     ↓
  [Create atomic task plans]
     ↓
/execute-phase 1
     ↓
  [Implement with progress tracking]
     ↓
/verify-work 1
     ↓
  [User acceptance testing]
     ↓
  [Repeat for Phase 2, 3, ...]
```

### Session Management

```
[Working on tasks...]
     ↓
/pause-work
     ↓
  [Handoff saved to STATE.md + DEVLOG.md]
     ↓
[Later, new session...]
     ↓
/resume-work
     ↓
  [Context restored, ready to continue]
```

### Multi-Session Workers (Advanced)

For parallel task execution across multiple AI sessions:

```
[Create a work queue...]
     ↓
/add-task "Description of task"
     ↓
  [Task added to persistent queue]
     ↓
/tandem
     ↓
  [New terminal opens with worker session]
     ↓
  [Worker claims and executes tasks]
```

| Command | Purpose |
|---------|---------|
| `/add-task` | Add task to persistent queue |
| `/list-tasks` | View queue status |
| `/claim-task` | Claim a task in current session |
| `/complete-task` | Mark task as done |
| `/tandem` | Launch additional worker |

Workers automatically coordinate via session registry and file locks.

---

## Directory Structure

```
your-project/
├── .claude/
│   ├── commands/           # 25 workflow commands
│   │   ├── init-project.md
│   │   ├── discuss-phase.md
│   │   ├── plan-phase.md
│   │   ├── execute-phase.md
│   │   ├── verify-work.md
│   │   ├── pause-work.md
│   │   ├── resume-work.md
│   │   └── ... (18 more)
│   ├── skills/             # Reusable skills
│   │   ├── conventional-commits.md
│   │   ├── test-detection.md
│   │   └── frontend-design.md
│   ├── agents/             # Specialized agents
│   │   ├── code-simplifier.md
│   │   ├── debug-helper.md
│   │   └── verify-app.md
│   ├── hooks/              # Automation hooks (requires Python)
│   │   ├── intel/          # Codebase intelligence
│   │   ├── session/        # Multi-session coordination
│   │   └── validators/     # Code validators
│   ├── scripts/            # Worker launcher scripts
│   │   ├── work_queue.py
│   │   ├── launch-worker.py
│   │   └── session-status.py
│   ├── session/            # Session state (auto-generated)
│   └── settings.json
├── .planning/
│   ├── README.md           # Planning guide
│   ├── intel/              # Auto-populated indexes (if enabled)
│   ├── quick/              # Ad-hoc tasks
│   ├── todos/              # Captured ideas
│   └── research/           # Research artifacts
├── CONTEXT.md               # Project context
├── PROJECT.md              # Project vision
├── REQUIREMENTS.md         # Requirements tracking
├── ROADMAP.md              # Phase roadmap
├── STATE.md                # Session state
├── DEVLOG.md               # Development history
├── SETUP.md                # This file
└── README.md               # Template overview
```

---

## Troubleshooting

### Commands not found

Ensure `.claude/commands/` contains all 25 command files with proper YAML frontmatter.

### Tasks not persisting

Verify `CLAUDE_CODE_TASK_LIST_ID` is set in `.claude/settings.json`.

### Hooks not running

Hooks require Python 3.8+. Check that:
1. Python is installed and in your PATH
2. Hooks are configured in `.claude/settings.json`
3. Permissions include the hook commands

### Codebase indexer errors

The indexer supports many languages. If you get errors, check that your file extensions are recognized.

---

## Getting Help

- `/progress` - See current project status
- `/explain` - Get plain-language explanations
- Read the command files in `.claude/commands/` for detailed usage

---

*Created by visionary-architect*
