---
description: "Load project context into the conversation"
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
---

# Prime — Context Loader

Load comprehensive project context into the current conversation. This is a **read-only** operation — no files are modified.

## What Gets Loaded

1. **CLAUDE.md** — Project rules, conventions, tech stack
2. **STATE.md** — Current focus, recent decisions, handoff notes
3. **DEVLOG.md** — Recent sessions, active bugs, progress history (last 50 lines)
4. **Git status** — Current branch, modified files, recent commits
5. **Open tasks** — Active and pending tasks from the task list
6. **Project structure** — Key directories and their purpose

## Workflow

1. Read CLAUDE.md (full file)
2. Read STATE.md (full file)
3. Read DEVLOG.md (last 50 lines)
4. Run `git status --short` and `git log --oneline -10`
5. Run `git branch --show-current`
6. List open tasks via TaskList
7. Glob for key files (pyproject.toml, package.json, etc.)

## Output

Present a concise summary:

```
Project: [name] | Branch: [branch] | [N] modified files
Last session: [date] — [what was done]
Active tasks: [count] in progress, [count] pending
Focus: [current focus from STATE.md]
```

## Rules

- **Read-only**: No Write, Edit, or file modifications allowed
- **Concise**: Summarize, don't dump entire file contents
- **Fast**: Skip files that don't exist rather than erroring
- **Informative**: Highlight anything that needs attention (uncommitted changes, failed tests, blockers)
