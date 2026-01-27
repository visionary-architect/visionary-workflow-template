---
description: "Restore context from a previous session and continue"
---

# Resume Work

> Restore context from a previous session, including bugs, fixes, and progress history.

---

## Purpose

After a break (or in a new AI session), this command:
1. Reads your handoff notes (STATE.md) for immediate context
2. Reviews recent development history (DEVLOG.md) for bugs, fixes, and progress
3. Loads project patterns from CONTEXT.md
4. Gets you back up to speed quickly

---

## Context

**Context Cache (Fast Resume):**
${{ type .claude\session\context_cache.json 2>nul || cat .claude/session/context_cache.json 2>/dev/null || echo "No context cache - will parse markdown files" }}

**Last Session Snapshot:**
${{ type .claude\session\last_snapshot.json 2>nul || cat .claude/session/last_snapshot.json 2>/dev/null || echo "No session snapshot" }}

**Test Results (if tracked):**
${{ type .claude\session\test_state.json 2>nul || cat .claude/session/test_state.json 2>/dev/null || echo "No test state" }}

**State and Handoff:**
${{ type STATE.md 2>nul || cat STATE.md 2>/dev/null || echo "STATE.md not found" }}

**Development Log (Recent Sessions):**
${{ type DEVLOG.md 2>nul | head -100 || head -100 DEVLOG.md 2>/dev/null || echo "DEVLOG.md not found" }}

**Project Rules:**
${{ type CONTEXT.md 2>nul | head -50 || head -50 CONTEXT.md 2>/dev/null || echo "CONTEXT.md not found" }}

**Codebase Intel:**
${{ type .planning\intel\summary.md 2>nul || cat .planning/intel/summary.md 2>/dev/null || echo "No codebase intel" }}

**Roadmap:**
${{ type ROADMAP.md 2>nul | head -50 || head -50 ROADMAP.md 2>/dev/null || echo "ROADMAP.md not found" }}

**Git Status:**
${{ git status --short 2>nul || git status --short 2>/dev/null || echo "Not a git repo" }}

**Uncommitted Changes:**
${{ git diff --stat 2>nul || git diff --stat 2>/dev/null || echo "No changes" }}

---

## Instructions

You are helping me resume work from a previous session.

### Step 0: Check Context Cache (Fast Path)

If `.claude/session/context_cache.json` exists and is recent (check `generated_at`):
- Use the pre-compiled context for instant resume
- Contains: handoff notes, active issues, recent commits, current phase
- Skip parsing markdown files for these fields

If `.claude/session/last_snapshot.json` exists:
- Shows state when session ended (git status, modified files, branch)
- Use to verify current state matches expected state

If `.claude/session/test_state.json` exists:
- Shows last test run results (pass/fail counts, failing tests)
- Surface any failures in the briefing

**Fallback:** If no cache exists, parse markdown files as before.

### Step 1: Read Handoff and History

**From Context Cache (if available):**
- `handoff.last_updated` - When handoff was created
- `handoff.session_ended` - Why session ended
- `active_issues[]` - Unresolved bugs
- `recent_commits[]` - Last 5 commits
- `current_phase` - Phase number

**From STATE.md (Handoff Notes):**
- What was being worked on
- Current status
- Next steps
- Important context
- Any uncommitted work

**From DEVLOG.md (Recent Sessions):**
- Active issues still unresolved
- Recent bugs found and their status
- Patterns/lessons from recent sessions
- Recent commits and progress

**From CONTEXT.md:**
- Project rules and patterns
- Lessons learned from previous sessions
- Key conventions to follow

### Step 2: Check Environment

Verify:
- [ ] Uncommitted files match what's noted in handoff
- [ ] No unexpected changes since pause
- [ ] Current branch is correct
- [ ] Active issues in DEVLOG.md are still relevant

If there are discrepancies, note them.

### Step 3: Present Task-Aware Resume Briefing

Show me a resumption briefing with task state in priority order:

```
═══════════════════════════════════════════════════
RESUMING WORK
═══════════════════════════════════════════════════

LAST SESSION: [date and time from handoff]

───────────────────────────────────────────────────
⚠️ REQUIRES ATTENTION
───────────────────────────────────────────────────

[Show blocked/failed tasks first - highest priority]
• [!] [1-B] Step 2: Update scheduler (blocked: TypeError)
• [!] [BG] pytest (failed: 2 tests)

[If test_state.json shows failures:]
• 🧪 TESTS FAILING: [N] tests failed in last run
  - test_foo.py::test_bar - AssertionError
  - test_baz.py::test_qux - TypeError

[Or "None - all clear"]

───────────────────────────────────────────────────
→ RESUME POINT
───────────────────────────────────────────────────

[Show current in_progress task]
• [→] [1-B] Step 3: Add integration tests
  - Depends on: [1-B] Steps 1-2 ✓
  - Blocked by: None

───────────────────────────────────────────────────
○ REMAINING IN CURRENT PHASE
───────────────────────────────────────────────────

• [ ] [1-B] Step 4: Commit changes
• [ ] [1-C] Step 1: Create endpoint scaffolding
  ... (+N more)

───────────────────────────────────────────────────
ACTIVE ISSUES (from DEVLOG.md)
───────────────────────────────────────────────────

[If any unresolved bugs:]
• BUG-XXX: [Description] - [Status]

[Or "No active issues"]

───────────────────────────────────────────────────
SESSION CONTEXT
───────────────────────────────────────────────────

Last session: [date]
Phase: [N] - [Phase Name]
Progress: [Plan A complete, Plan B in progress]
Commits: [count] commits pushed

───────────────────────────────────────────────────
UNCOMMITTED WORK
───────────────────────────────────────────────────

[List files, or "None - all committed"]

═══════════════════════════════════════════════════

Ready to continue? What would you like to do?
• Continue with resume point
• Address blocked tasks first
• Review uncommitted changes
• Check something else
```

### Handling Interrupted Tasks

If a task was `[→]` in_progress when session ended:

1. **Flag it explicitly**:
   ```
   ⚠️ INTERRUPTED TASK
   • [→] [1-B] Step 2: Update scheduler
     - Was in_progress at session end
     - Action: Verify state before continuing
   ```

2. **Before continuing**:
   - Check file state — were changes partially applied?
   - Run relevant tests — is current state valid?
   - Mark complete or reset to pending based on findings

3. **Never assume interrupted = complete**

### Detecting Stale Tasks (Multi-Session)

If you see a task claimed by a different session tag:

1. **Check if stale** (>30 min since last activity):
   ```
   ⚠️ Stale task detected: [1-A] Step 2 (@worker-2)
   Last activity: 45 min ago
   ```

2. **Options**:
   - Wait for other session to resume
   - Check STATE.md for handoff notes from that session
   - Force unclaim if clearly abandoned

3. **Force unclaim procedure** (last resort):
   - Read the other session's last STATE.md update
   - Check git for partial commits
   - Run tests to verify current state
   - Unclaim with documentation:
     ```
     [→] [1-A] Step 2: Description (@main, unclaimed from @worker-2 - stale)
     ```
   - Continue from verified state

### What NOT to Include

- Full list of completed tasks (reference DEVLOG.md)
- Completed phases (only current phase relevant)
- Background task details if passed (just note "✓ All background tasks passed")

### Step 4: Handle Uncommitted Work

If there's uncommitted work:
- Show what files are modified
- Ask if I want to:
  1. Review the changes
  2. Continue where we left off
  3. Commit them first
  4. Discard and start fresh

### Step 5: Update STATE.md

Add to session log:
```markdown
### [YYYY-MM-DD]
- Resumed from [previous date] session
- Starting: [next step from handoff]
```

Clear or archive the handoff notes (optional - can keep for reference).

### Step 6: Continue

Based on the handoff, suggest the appropriate command:
- If mid-execution: "Continue with the implementation"
- If ready for next step: `/execute-phase N` or `/verify-work N`
- If planning: `/plan-phase N`
- If active bugs: "Address BUG-XXX first?"

---

## No Handoff Found

If there are no handoff notes:

```
═══════════════════════════════════════════════════
NO HANDOFF FOUND
═══════════════════════════════════════════════════

No handoff notes found in STATE.md.

Let me check DEVLOG.md and current state...

───────────────────────────────────────────────────
RECENT ACTIVITY (from DEVLOG.md)
───────────────────────────────────────────────────

[Show last session summary from DEVLOG.md]

───────────────────────────────────────────────────
ACTIVE ISSUES
───────────────────────────────────────────────────

[Show any active issues from DEVLOG.md]

───────────────────────────────────────────────────
CURRENT PHASE STATUS
───────────────────────────────────────────────────

[Show progress report like /progress]

Would you like to:
1. Continue from current phase status
2. Review recent DEVLOG entries
3. Start fresh with /init-project
═══════════════════════════════════════════════════
```

---

## Quick Resume

For fast resumption without the full briefing:

> "Resuming Phase [N]. Last working on [task]. [X] active issues. Next step: [action]. Ready to continue?"

---

## Important Notes

- Always read both STATE.md AND DEVLOG.md
- STATE.md has immediate context (what's next)
- DEVLOG.md has history (bugs, fixes, patterns)
- Check for active issues before continuing
- Recent patterns/lessons help avoid repeated mistakes
