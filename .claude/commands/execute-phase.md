---
description: "Execute task plans for a phase with atomic commits"
arguments:
  - name: phase
    description: "Phase number to execute (e.g., 1, 2, 3)"
---

# Execute Phase

> Execute task plans with fresh context and atomic commits.

---

## Purpose

This command executes the plans created by `/plan-phase`. Each task gets executed with attention to verification steps, and commits are made atomically after each task.

---

## Context

**Current State:**
${{ type STATE.md 2>nul || cat STATE.md 2>/dev/null || echo "STATE.md not found" }}

**Available Plans:**
${{ dir ".planning/$arguments.phase-*-PLAN.md" 2>nul || ls .planning/$arguments.phase-*-PLAN.md 2>/dev/null || echo "No plans found - run /plan-phase first" }}

---

## Instructions

You are executing plans for Phase $arguments.phase.

### Step 1: Load Plans

1. Read all `.planning/{N}-*-PLAN.md` files for this phase
2. Identify task order and dependencies
3. Note any `checkpoint` tasks that need user confirmation

### Step 2: Pre-Execution Check

Before starting:
- [ ] Verify git working directory is clean (or stash changes)
- [ ] Confirm all prerequisites from plans are met
- [ ] Read project conventions from CLAUDE.md
- [ ] Read codebase patterns from `.planning/intel/summary.md` (if exists)

### Step 3: Create Task List

Before executing, create tasks with dependencies using the naming convention:

```
[<Phase>-<Plan>] Step <N>: <Verb> <object>
```

**1. Create plan-level tasks:**
```
[ ] Plan N-A: [Task Name] (no dependency)
[ ] Plan N-B: [Task Name] (depends on N-A)
[ ] Plan N-C: [Task Name] (depends on N-B)
```

**2. When starting each plan, expand to step tasks:**
```
[→] [N-A] Step 1: Add constants to constants.py
[ ] [N-A] Step 2: Update model fields
[ ] [N-A] Step 3: Run unit tests
[ ] [N-A] Step 4: Commit changes
[ ] [N-A] Step 5: Context checkpoint
```

**3. Status indicators:**
- `[ ]` Pending
- `[→]` In progress
- `[✓]` Complete
- `[!]` Blocked (requires attention)
- `[⋯]` Background (running)

**4. Background tasks use prefix:** `[BG] pytest full suite`

**5. Verification tasks use prefix:** `[UAT] <test case name>`

---

### Step 4: Execute Each Plan

For each plan, in order:

#### 4a. Announce Task
Tell me which task you're starting:
> "Starting Plan {M}: [Task Name]"

Mark the plan task as `[→]` in progress.

#### 4b. Execute Steps
Follow the plan's steps precisely:
- Mark each step `[→]` when starting
- Read the detailed instructions
- Make the code changes
- Follow project conventions
- Use patterns from the codebase intel
- Mark step `[✓]` when complete

#### 4c. Verify
Run the verification steps from the plan:
- Execute any verification commands
- Check the completion criteria
- Fix any issues before proceeding (see Failure Handling below)

#### 4d. Atomic Commit
After task verification passes, create a commit:

**Commit format:**
```
{type}({phase}-{plan}): {description}

Co-Authored-By: visionary-architect
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `test` - Adding tests
- `refactor` - Code refactoring
- `docs` - Documentation
- `chore` - Maintenance

**Example:**
```
feat(1-A): add user model and database schema

Co-Authored-By: visionary-architect
```

#### 4e. Create Summary
After each task, create `.planning/{N}-{M}-SUMMARY.md`:

```markdown
# Phase {N} - Plan {M} Summary: [Task Name]

## Status: Complete

## What Was Done
- [Change 1]
- [Change 2]

## Files Changed
- `path/to/file1.ts` - [What changed]
- `path/to/file2.ts` - [What changed]

## Verification Results
- [x] [Verification 1] - Passed
- [x] [Verification 2] - Passed

## Commit
- Hash: [git hash]
- Message: [commit message]

## Notes
[Any issues encountered or deviations from plan]
```

### Step 5: Handle Checkpoints

If a task has type `checkpoint:human-verify`:
1. Complete the task
2. Show me what was done
3. Ask me to verify it works
4. Wait for my confirmation before committing

If a task has type `checkpoint:decision`:
1. Explain the decision needed
2. Present options
3. Wait for my decision
4. Proceed based on my choice

### Step 6: Context Checkpoint (Between Plans) — MANDATORY

**This step is REQUIRED after completing each plan.** Context degradation causes errors.

After completing ALL steps in a plan, before starting next plan:

#### 6a. Automatic Context Assessment

**Always announce context status after each plan:**
```
═══════════════════════════════════════════════════
PLAN [N-A] COMPLETE - CONTEXT CHECK
═══════════════════════════════════════════════════
Context usage: ~[X]%
Status: [GREEN/YELLOW/RED]
═══════════════════════════════════════════════════
```

**Thresholds:**
| Usage | Status | Action |
|-------|--------|--------|
| 0-50% | 🟢 GREEN | Continue to next plan |
| 50-75% | 🟡 YELLOW | Warn user, offer `/pause-work` |
| 75-90% | 🟠 ORANGE | Strongly recommend `/pause-work` |
| 90%+ | 🔴 RED | **STOP** - Must pause before continuing |

#### 6b. At YELLOW (50-75%)

```
⚠️ Context at ~60%. Quality may begin to degrade.

Would you like to:
1. Continue (I'll be extra careful)
2. Pause now with `/pause-work` (recommended if >2 plans remain)
```

#### 6c. At ORANGE (75-90%)

```
⚠️ Context at ~80%. Recommend pausing to maintain quality.

Plan [N-A] is complete and committed. This is a clean breakpoint.

I'll run `/pause-work` now to save progress, then you can start
a fresh session with `/resume-work`.

Proceed with pause? (yes/continue anyway)
```

#### 6d. At RED (90%+)

```
🛑 Context at ~95%. Must pause to prevent errors.

Saving progress now...
```

**Automatically run `/pause-work`** — don't ask, just do it.
Tasks persist via `CLAUDE_CODE_TASK_LIST_ID`.

#### 6e. Fresh Session Resume

After pausing:
1. **Start fresh session**
2. Run `/resume-work`
3. Continue from next plan with full context available

**Why plan boundaries?** Plans are clean breakpoints (all steps complete, tests passing, committed). Steps are not (partial changes).

### Step 7: Update STATE.md

After all tasks complete:
- Set "Current Phase" status to "executing → verifying"
- Add session log entry with what was accomplished
- Note the commits made

### Step 8: Phase Completion Cleanup

When all plans in phase complete:

1. **Log completion to DEVLOG.md**:
   ```markdown
   ## Phase N Complete

   ### Completed Tasks
   - [N-A] Task name (X steps)
   - [N-B] Task name (Y steps)
   - [N-C] Task name (Z steps)

   ### Background Tasks
   - pytest: ✓ all passed
   - mypy: ✓ no errors
   ```

2. **Clear completed tasks** (archive/clear all `[✓]` from Phase N)

3. **Retain only**: pending tasks, future phase tasks

4. **Update STATE.md**:
   ```markdown
   - Phase N: ✓ Complete
   - Phase N+1: Not started
   ```

### Step 9: Phase Summary and Offer Next Step

Summarize and offer to continue:

```
✅ Phase $arguments.phase execution complete!

Tasks completed: [N]
- Plan A: [Task name] ✓
- Plan B: [Task name] ✓
- Plan C: [Task name] ✓ (if applicable)

Commits: [commit hashes]
Issues: [None or list]
```

**Then ask:**
> "Ready to verify the work? I'll run `/verify-work $arguments.phase` to walk you through testing the deliverables."
>
> Or if you want to review the code first, let me know.

**If user says yes:** Immediately run the verify-work workflow.

**If user wants to review first:** Show relevant code or wait for their direction.

---

## Output Files

| File | Purpose |
|------|---------|
| `.planning/{N}-{M}-SUMMARY.md` | Summary for each completed task |
| `STATE.md` | Updated status |
| Git commits | One per task |

---

## Context Management

**Why this matters:**
The AI's quality degrades as context fills. By executing plans in a focused way:
- Each task starts relatively fresh
- Plans provide precise instructions (less back-and-forth)
- Verification catches issues early

**Best practices:**
- Focus on one task at a time
- Don't add features not in the plan
- If something unexpected comes up, note it for later
- Keep the main context clean

---

## Error Handling

**If a verification step fails:**
1. Try to fix the issue
2. Re-run verification
3. If still failing, note it in the summary
4. Ask me if I want to proceed or stop

**If a task can't be completed:**
1. Document what was done and what remains
2. Create partial summary
3. Update STATE.md with blocker
4. Ask me how to proceed

**If prerequisites aren't met:**
1. Stop before starting
2. Tell me what's missing
3. Suggest how to resolve

---

## Failure Handling Protocol

### When a Step Fails

1. **Mark step as blocked**, not failed:
   ```
   [!] [1-B] Step 2: Update scheduler (blocked: TypeError in data_repository.py)
   ```

2. **Do not create separate "fix" tasks** — this fragments the workflow

3. **Address the issue within the current step's scope**:
   - Diagnose the failure
   - Implement the fix
   - Re-run verification
   - Mark step complete only when passing

4. **Downstream steps remain pending** — dependency chain stays intact

### When a Background Task Fails

1. **Surface the failure immediately** via `/tasks` or `Ctrl+T`

2. **Pause current foreground work** at next clean breakpoint (step completion)

3. **Assess severity**:
   - Single test failure → may continue, create note
   - Multiple/critical failures → block current plan

4. **Document in task**:
   ```
   [!] [BG] pytest full suite (failed: 2 tests - see output)
       → Blocking: [1-B] Step 3
   ```

5. **After fix**: Re-run background task, unblock dependent steps

### Blocked Task Format
```
[!] [Phase-Plan] Step N: <description> (blocked: <reason>)
```

### Catastrophic Failure Recovery

If the entire execution fails (not just a single step), follow this recovery protocol:

**Symptoms of catastrophic failure:**
- Multiple cascading errors
- Git in broken state (merge conflicts, detached HEAD)
- Codebase won't compile/run at all
- Tests show >50% failure rate unexpectedly

**Recovery steps:**

1. **Stop immediately** - Don't try to fix blindly
   ```
   ⛔ EXECUTION HALTED - Catastrophic failure detected
   ```

2. **Assess the damage:**
   ```bash
   git status                    # Check working directory state
   git log --oneline -5         # Find last known good commit
   git diff HEAD~1              # See what changed
   ```

3. **Determine recovery path:**

   **If changes are uncommitted:**
   ```bash
   git stash                    # Save work in progress
   git checkout .               # Reset to last commit
   ```

   **If bad commit was made:**
   ```bash
   git revert HEAD              # Create reverting commit (safe)
   # OR if user explicitly approves:
   git reset --soft HEAD~1      # Undo commit, keep changes staged
   ```

4. **Document the failure:**
   - Update STATE.md with `[!] BLOCKED: [description]`
   - Add to DEVLOG.md under "Active Issues"
   - Note the last known good commit hash

5. **Ask user how to proceed:**
   > "I've encountered a catastrophic failure and halted execution.
   >
   > Last good commit: [hash]
   > Current state: [description]
   >
   > Options:
   > 1. Revert to last good commit and retry the plan
   > 2. Investigate the root cause before proceeding
   > 3. Skip this plan and continue with the next one
   > 4. Run `/pause-work` and start fresh session
   >
   > What would you like to do?"

6. **After recovery:** Re-run verification before continuing

**Prevention:** Context checkpoints between plans catch issues early.

---

## Commit Rules

- **NEVER** force push
- **NEVER** amend commits unless asked
- **ALWAYS** include Co-Authored-By
- **ALWAYS** use conventional commit format
- **ONE** commit per task (atomic)
- Stage files individually, not `git add .`

---

## Background Task Patterns

### Background vs Foreground Operations

| Operation | Mode | Rationale |
|-----------|------|-----------|
| Full test suite | **Background** | Long-running, continue working |
| Single test file | Foreground | Quick, need immediate feedback |
| Full type check | **Background** | Can take time on full codebase |
| Lint check | Foreground | Usually fast (<10 sec) |
| Format check | Foreground | Usually fast (<10 sec) |

### Workflow Integration

After completing Plan N-A code changes:

1. Quick lint check (foreground): run your linter on changed files
2. Background full test suite: `Ctrl+B` on your test command
3. Continue with Plan N-B while tests run
4. Check test results with `/tasks` (built-in)
5. If tests fail, pause Plan N-B and address failures

### Auto-Background Thresholds

Background automatically if:
- Running full test suite (not a specific file)
- Running type check on entire codebase
- Any command expected to take >30 seconds

---

## Multi-Session Task Claiming

When multiple sessions work on the same task list, use session tags to claim ownership.

### Claiming a Task

When marking a task `[→]` in_progress, append your session tag:

```
[→] [1-A] Step 1: Add constants (@main)
```

### Claiming Rules

1. **Always append `(@session-tag)`** when marking `[→]` in_progress
2. **Only the claiming session** can mark the task `[✓]` complete
3. **Any session can mark `[!]` blocked** (emergencies)
4. **Unclaimed tasks** can be taken by any session

### Format Examples

```
[→] [1-A] Step 1: Description (@main)           # Claimed by main
[✓] [1-A] Step 1: Description (@main)           # Same tag must complete
[!] [1-B] Step 2: Description (blocked: error)  # Any session can block
```

### Conflict Detection

If you try to claim a task already owned by another session:

```
⚠️ CONFLICT: [1-A] Step 2 claimed by @worker-2
Cannot claim for @main
Options:
1. Wait for @worker-2 to complete
2. Check STATE.md for coordination notes
3. Force unclaim if stale (>30 min)
```

### Force Unclaim (Stale Tasks)

If a task has been claimed >30 minutes with no activity:

```
[→] [1-A] Step 2: Description (@main, unclaimed from @worker-2 - stale)
```

Before force unclaiming:
- Document reason in task
- Verify no partial changes from previous session
- Run tests before continuing

### Spawning Subagents

When spawning a subagent that will claim tasks:
1. Generate unique tag: `bg-{purpose}-{timestamp}` (e.g., `bg-tests-1706123456`)
2. Pass tag in prompt: "Use session tag `@bg-tests-1706123456` when claiming tasks"
3. Subagent includes tag in all task claims

**Note:** Subagents doing read-only work (exploration, analysis) don't need tags.

---

## Example Execution Flow

```
Starting Phase 1 execution...

Plan A of 3: Create User Model
- Executing step 1: Define User Model ✓
- Executing step 2: Create Database Client ✓
- Executing step 3: Generate Types ✓
- Verification: prisma validate ✓
- Verification: TypeScript compiles ✓
- Committing: feat(1-A): add user model and database schema
- Summary created: .planning/1-A-SUMMARY.md

═══════════════════════════════════════════════════
PLAN [1-A] COMPLETE - CONTEXT CHECK
═══════════════════════════════════════════════════
Context usage: ~35%
Status: 🟢 GREEN - Continuing to next plan
═══════════════════════════════════════════════════

Plan B of 3: Add Registration Endpoint
- Executing step 1: Create route handler ✓
- Executing step 2: Add validation ✓
- Verification: curl test ✓
- Committing: feat(1-B): add user registration endpoint
- Summary created: .planning/1-B-SUMMARY.md

═══════════════════════════════════════════════════
PLAN [1-B] COMPLETE - CONTEXT CHECK
═══════════════════════════════════════════════════
Context usage: ~55%
Status: 🟡 YELLOW - Recommend completing phase, then pause
═══════════════════════════════════════════════════

Plan C of 3: Add Registration Tests
- Executing step 1: Write unit tests ✓
- Executing step 2: Write integration test ✓
- Verification: tests pass ✓
- Committing: test(1-C): add registration tests
- Summary created: .planning/1-C-SUMMARY.md

Phase 1 execution complete!
Commits: abc123f, def456g, hij789k

Ready to verify the work? I'll run `/verify-work 1`
```
