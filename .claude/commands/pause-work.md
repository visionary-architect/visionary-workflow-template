---
description: "Create a handoff for continuing work in a new session"
---

# Pause Work

> Create a handoff for continuing in a new session, documenting bugs, fixes, and progress.

---

## Purpose

When you need to stop mid-work, this command:
1. Captures your current state in STATE.md (for immediate resumption)
2. Documents the session in DEVLOG.md (bugs, fixes, decisions, progress)

---

## Context

**Current State:**
${{ type STATE.md 2>nul || cat STATE.md 2>/dev/null || echo "STATE.md not found" }}

**Development Log (Recent):**
${{ type DEVLOG.md 2>nul | head -80 || head -80 DEVLOG.md 2>/dev/null || echo "DEVLOG.md not found" }}

**Git Status:**
${{ git status --short 2>nul || git status --short 2>/dev/null || echo "Not a git repo" }}

**Recent Commits (this session):**
${{ git log --oneline -10 2>nul || git log --oneline -10 2>/dev/null || echo "No commits" }}

---

## Instructions

You are helping me pause work and create a comprehensive handoff.

### Step 1: Gather Session Information

Ask me (or determine from context):

1. **What were you working on?**
   - Current phase/task
   - Specific file or feature

2. **What's the current status?**
   - How far along are you?
   - What's done vs remaining?

3. **What should be done next?**
   - Immediate next step
   - Any decisions pending

4. **Bugs or issues found this session?**
   - Any bugs discovered (even if fixed)
   - Workarounds applied
   - Known limitations

5. **Fixes applied?**
   - What was fixed and how
   - Relevant commit hashes

6. **Patterns or lessons learned?**
   - Gotchas discovered
   - Things to remember
   - Should anything go in CLAUDE.md?

### Step 2: Check for Uncommitted Work

If there are uncommitted changes:
- Ask if I want to commit them now
- Or stash them with a descriptive message
- Or leave them (note this in handoff)

### Step 3: Update DEVLOG.md

Add a new session entry at the top of "Recent Sessions":

```markdown
### Session: [YYYY-MM-DD] ([Brief Description])

**Phase/Focus:** [Phase N / Ad-hoc / Bug fix]

#### Worked On
- [What was accomplished]

#### Bugs Found
- **BUG-XXX**: [Brief description]
  - **Severity:** [critical/high/medium/low]
  - **File:** `path/to/file`
  - **Details:** [More context]
  - **Status:** [active/investigating/fixed]

#### Fixes Applied
| Fix | File | Commit |
|-----|------|--------|
| [Description] | `file` | `hash` |

#### Decisions Made
- [Decision and rationale]

#### Patterns Learned
- [Pattern or lesson for CLAUDE.md]

#### Commits
- `hash` message
```

**Also update the Active Issues table** if any bugs are still unresolved.

### Step 4: Update STATE.md

Update the "Handoff Notes" section:

```markdown
## Handoff Notes

**Last Updated:** [YYYY-MM-DD HH:MM]
**Session Ended:** [reason - EOD, switching tasks, etc.]

### In Progress
[What was being worked on]
- Phase: [N]
- Task: [description]
- Status: [how far along]

### Task State (from /tasks)

> **Note:** Snapshot ACTIVE/PENDING tasks only. Don't bloat with completed tasks.

**Session Tag:** @main (or your `CLAUDE_SESSION_TAG`)

**In Progress:**
- [→] [1-B] Step 2: Update scheduler (@main)

**Pending:**
- [ ] [1-B] Step 3: Add integration tests
- [ ] [1-C] Step 1: Create endpoint scaffolding

**Blocked (if any):**
- [!] [BG] pytest (failed: 2 tests)

**Completed this session:** N tasks (see `/tasks` or DEVLOG.md for details)

> **Multi-session note:** Include `(@session-tag)` on in_progress tasks so resuming sessions can identify ownership.

### Next Steps
1. [Immediate next action]
2. [Following action]
3. [Then this]

### Context to Remember
- [Important detail 1]
- [Important detail 2]
- [Gotcha or note]

### Uncommitted Work
- [List any uncommitted files, or "None - all committed"]

### Open Questions
- [Any decisions that need to be made]
```

> **Tasks persist automatically** via your `CLAUDE_CODE_TASK_LIST_ID`.
> The snapshot in STATE.md is for quick reference when resuming.

Also add to session log:
```markdown
### [YYYY-MM-DD]
- [Summary of what was done]
- Paused: [reason]
- See DEVLOG.md for full session details
```

### Step 5: Update CLAUDE.md (If Needed)

If significant patterns or lessons were learned this session, update the appropriate CLAUDE.md file.

**Where to add lessons:**

| Scope | Update |
|-------|--------|
| Project-wide patterns, workflow, architecture | Root `CLAUDE.md` |
| Component-specific patterns | Component's `CLAUDE.md` (if exists) |

**Format for lessons:**
```markdown
### YYYY-MM-DD
- [What happened] - [Correct approach going forward]
```

**Guidelines:**
- Add project-wide lessons to root CLAUDE.md
- Add component-specific lessons to that component's CLAUDE.md (if you have them)
- Don't duplicate - if it's component-specific, only add there

### Step 6: Refresh Context Cache

After updating STATE.md and DEVLOG.md, refresh the context cache for instant resume:

```bash
python .claude/hooks/session/warmup_cache.py
```

This pre-compiles the handoff notes into `.claude/session/context_cache.json` so the next `/resume-work` loads instantly.

Also mark the session as logged to prevent duplicate auto-capture:

```bash
python -c "from pathlib import Path; Path('.claude/session/session_logged.marker').touch()"
```

### Step 7: Confirm Handoff

Show me:
- Summary of what was captured
- Any active bugs noted
- Any uncommitted work noted
- Context cache refreshed (yes/no)
- How to resume: `/resume-work`

---

## Example Session Entry (DEVLOG.md)

```markdown
### Session: 2026-01-21 (Phase 4 Completion)

**Phase/Focus:** Phase 4 - End-to-End Testing

#### Worked On
- Completed Phase 4 plans (4-A, 4-B, 4-C)
- Ran code-simplifier and verify-app agents
- Fixed commit validator regex issue

#### Bugs Found
- **BUG-001**: E2E user ID format didn't match API regex
  - **Severity:** medium
  - **File:** `scripts/e2e_verify.py`
  - **Details:** Pattern expected `user-{region}-{suffix}`
  - **Status:** fixed

#### Fixes Applied
| Fix | File | Commit |
|-----|------|--------|
| Changed user ID format | `e2e_verify.py` | `0b5ca4d` |
| Combined assign_to_worker() | `task.py` | `0b5ca4d` |

#### Decisions Made
- 30s retry cooldown (fixed, not per-job)
- Heartbeat: 30s interval, 90s stale threshold

#### Patterns Learned
- SQLite returns naive datetimes - compare with `.replace(tzinfo=None)`

#### Commits
- `a6fd679` feat(4-A): add retry cooldown
- `8e93fc9` feat(4-B): add stale worker sweep
- `e1afad9` feat(4-C): add integration tests
- `0b5ca4d` refactor: simplify scheduler
```

---

## Quick Pause

If you just need a fast pause without detailed questions:

> "Pausing work on [current task]. Updates saved to STATE.md and DEVLOG.md. Resume with /resume-work."

Still capture at minimum:
- What was worked on
- Any bugs found/fixed
- Commits made

---

## Important Notes

- Always update both STATE.md AND DEVLOG.md
- STATE.md = ephemeral (current state, next steps)
- DEVLOG.md = permanent history (bugs, fixes, progress)
- Note uncommitted work to avoid losing changes
- Be specific about bugs - future you will thank you
- Add significant lessons to CLAUDE.md
