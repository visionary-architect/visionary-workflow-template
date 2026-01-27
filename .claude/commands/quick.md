---
description: "Execute ad-hoc tasks without full planning"
arguments:
  - name: task
    description: "What you want to do (optional, will prompt if not provided)"
---

# Quick Mode

> Execute small tasks without the full planning workflow.

---

## Purpose

Not everything needs discuss → plan → execute → verify. Quick mode gives you atomic commits and tracking with a faster path for small, self-contained tasks.

---

## When to Use Quick Mode

**Good for:**
- Bug fixes
- Small features (< 30 min work)
- Config changes
- One-off tasks
- Documentation updates
- Refactoring a single file

**Not good for:**
- Features spanning multiple files/concerns
- Architectural changes
- Work that needs design decisions
- Anything you're unsure about

**Rule of thumb:** If you can describe it in one sentence, it's probably a quick task.

---

## Context

**Current State:**
${{ type STATE.md 2>nul || cat STATE.md 2>/dev/null || echo "STATE.md not found" }}

**Recent Quick Tasks:**
${{ dir .planning\quick /b 2>nul || ls .planning/quick 2>/dev/null || echo "No quick tasks yet" }}

---

## Instructions

You are executing a quick task.

### Step 1: Understand the Task

If no task was provided in the arguments, ask:
> "What do you want to do?"

Once I describe the task:
1. Confirm your understanding in ONE sentence
2. Ask if that's correct
3. Wait for my "yes" before proceeding

**Example:**
> User: "Add a loading spinner to the submit button"
> Assistant: "I'll add a loading spinner that shows when the submit button is clicked and hides when the action completes. Correct?"
> User: "Yes"

### Step 2: Execute Immediately

Do the work:
- Make the changes
- No lengthy analysis
- No exploring alternatives
- Just do the thing

### Step 3: Verify

Quick verification:
- Does it work?
- Did anything break?
- Run tests if relevant

### Step 4: Commit

Create an atomic commit:
```
{type}(quick): {description}

Co-Authored-By: visionary-architect
```

### Step 5: Track

Create a tracking folder in `.planning/quick/{NNN}-{slug}/`:

**PLAN.md:**
```markdown
# Quick Task: [Description]

**Created:** [YYYY-MM-DD]
**Status:** Complete

## Task
[One sentence description]

## Changes Made
- [Change 1]
- [Change 2]

## Files Modified
- `path/to/file`
```

**SUMMARY.md:**
```markdown
# Quick Task Summary: [Description]

## Commit
- Hash: [git hash]
- Message: [commit message]

## Verification
- [x] [What was verified]

## Notes
[Any notes for future reference]
```

### Step 6: Update STATE.md

Add to session log:
> "Quick task: [description] - complete"

### Step 7: Confirm

Tell me:
- What was done
- The commit hash
- Any notes or follow-ups needed

---

## Output Files

| File | Purpose |
|------|---------|
| `.planning/quick/{NNN}-{slug}/PLAN.md` | What was requested |
| `.planning/quick/{NNN}-{slug}/SUMMARY.md` | What was done |
| `STATE.md` | Session log updated |
| Git commit | Atomic commit |

---

## Numbering

Quick tasks are numbered sequentially:
- `001-add-loading-spinner/`
- `002-fix-typo-in-readme/`
- `003-update-dependencies/`

Check existing folders to determine the next number.

---

## Speed vs Safety

Quick mode trades thoroughness for speed:

| Full Workflow | Quick Mode |
|---------------|------------|
| Research phase | Skip |
| Plan verification | Skip |
| Post-execution verification | Light check |
| Multiple agents | Single pass |
| Detailed summaries | Brief notes |

The trade-off is acceptable for small, well-understood tasks.

---

## Example Quick Tasks

**"Fix the typo in the README"**
```
Read README, find typo, fix it, commit.
Done: fix(quick): correct typo in installation section
```

**"Add console.log to debug the login"**
```
Add logging, test it shows expected output.
Done: chore(quick): add debug logging to login flow
Note: Remember to remove before committing to main
```

**"Update the copyright year"**
```
Find copyright notices, update year.
Done: chore(quick): update copyright year to 2026
```

**"Rename getUserData to fetchUserProfile"**
```
Find all usages, rename function, update imports.
Done: refactor(quick): rename getUserData to fetchUserProfile
```

---

## Important Notes

- Quick mode still creates commits (traceability)
- Quick mode still updates STATE.md (continuity)
- Quick mode still creates tracking files (history)
- If the task grows complex, suggest switching to full workflow
- Don't use quick mode to avoid planning - use it for genuinely small tasks
