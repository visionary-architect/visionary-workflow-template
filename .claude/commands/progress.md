---
description: "Show current project status and what's next"
---

# Progress

> Show current project status and what's next.

---

## Purpose

Quickly understand where you are in the project without reading through all the files.

---

## Context

**Project:**
${{ type PROJECT.md 2>nul || cat PROJECT.md 2>/dev/null || echo "PROJECT.md not found - run /init-project first" }}

**State:**
${{ type STATE.md 2>nul || cat STATE.md 2>/dev/null || echo "STATE.md not found" }}

**Roadmap:**
${{ type ROADMAP.md 2>nul || cat ROADMAP.md 2>/dev/null || echo "ROADMAP.md not found" }}

---

## Instructions

Generate a concise progress report.

### Report Format

```
═══════════════════════════════════════════════════
PROJECT STATUS: [Project Name]
═══════════════════════════════════════════════════

CURRENT MILESTONE: v[X.X]
CURRENT PHASE: [N] - [Phase Name]
PHASE STATUS: [discussing | planning | executing | verifying | complete]

───────────────────────────────────────────────────
PROGRESS
───────────────────────────────────────────────────

Phases:
  [✓] Phase 1: [Name] - complete
  [→] Phase 2: [Name] - in progress (executing)
  [ ] Phase 3: [Name] - not started
  [ ] Phase 4: [Name] - not started

Requirements (v1.0):
  [X/Y] Must Have completed
  [X/Y] Should Have completed

───────────────────────────────────────────────────
CURRENT FOCUS
───────────────────────────────────────────────────

[What's being worked on right now]

───────────────────────────────────────────────────
BLOCKERS
───────────────────────────────────────────────────

[Any blockers, or "None"]

───────────────────────────────────────────────────
NEXT STEPS
───────────────────────────────────────────────────

1. [Next immediate action]
2. [Following action]

═══════════════════════════════════════════════════

**After displaying the report, ask:**
> "Would you like me to run `/[next-command]` to continue?"

If user says yes, immediately run the appropriate workflow command.

### Determining Next Command

Based on current phase status:

| Status | Next Command |
|--------|--------------|
| not started | `/discuss-phase N` |
| discussing | `/plan-phase N` |
| planning | `/execute-phase N` |
| executing | `/verify-work N` |
| verifying (with fixes) | `/execute-phase N` |
| verifying (passed) | Mark complete, `/discuss-phase N+1` |
| all complete | `/complete-milestone` |

---

## Quick Status Indicators

Use these symbols:
- `[✓]` Complete
- `[→]` In progress
- `[ ]` Not started
- `[!]` Blocked
- `[~]` Partially complete

---

## Example Output

```
═══════════════════════════════════════════════════
PROJECT STATUS: Task Manager CLI
═══════════════════════════════════════════════════

CURRENT MILESTONE: v1.0
CURRENT PHASE: 2 - Add Task Management
PHASE STATUS: executing

───────────────────────────────────────────────────
PROGRESS
───────────────────────────────────────────────────

Phases:
  [✓] Phase 1: Project Setup - complete
  [→] Phase 2: Add Task Management - in progress (2/3 plans done)
  [ ] Phase 3: Add Categories - not started
  [ ] Phase 4: Add Export - not started

Requirements (v1.0):
  [2/5] Must Have completed
  [0/2] Should Have completed

───────────────────────────────────────────────────
CURRENT FOCUS
───────────────────────────────────────────────────

Implementing task deletion and update functionality.
Currently on Plan C of Phase 2.

───────────────────────────────────────────────────
BLOCKERS
───────────────────────────────────────────────────

None

───────────────────────────────────────────────────
NEXT STEPS
───────────────────────────────────────────────────

1. Complete Plan C: Add task delete/update commands
2. Run verification for Phase 2
3. Move to Phase 3: Categories

═══════════════════════════════════════════════════

Would you like me to run `/execute-phase 2` to continue?
```

---

## No Project Initialized

If PROJECT.md doesn't exist:

```
═══════════════════════════════════════════════════
NO PROJECT INITIALIZED
═══════════════════════════════════════════════════

No project has been set up yet.

To get started, run: /init-project

This will guide you through:
- Defining your project vision
- Setting requirements
- Creating your roadmap with phases
═══════════════════════════════════════════════════
```
