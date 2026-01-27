---
description: "User acceptance testing for a completed phase"
arguments:
  - name: phase
    description: "Phase number to verify (e.g., 1, 2, 3)"
---

# Verify Work

> User acceptance testing to confirm the phase delivers what was promised.

---

## Purpose

Automated verification checks that code exists and tests pass. But does the feature actually work the way you expected? This command walks you through testing the deliverables yourself.

---

## Context

**Current State:**
${{ type STATE.md 2>nul || cat STATE.md 2>/dev/null || echo "STATE.md not found" }}

**Phase Summary:**
${{ type ROADMAP.md 2>nul || cat ROADMAP.md 2>/dev/null || echo "ROADMAP.md not found" }}

**Execution Summaries:**
${{ dir ".planning/$arguments.phase-*-SUMMARY.md" 2>nul || ls .planning/$arguments.phase-*-SUMMARY.md 2>/dev/null || echo "No summaries found - run /execute-phase first" }}

---

## Instructions

You are helping me verify that Phase $arguments.phase delivers what was promised.

### Step 1: Gather Deliverables

1. Read ROADMAP.md for phase deliverables
2. Read REQUIREMENTS.md for what this phase should deliver
3. Read `.planning/{N}-CONTEXT.md` for implementation decisions
4. Read execution summaries for what was actually built

### Step 2: Extract Testable Items and Create Tasks

Create a list of things I should be able to do now. Be specific:

**Good testable items:**
- "Can you create a new user account?"
- "Does the dashboard show your recent activity?"
- "Can you export data to CSV?"

**Bad testable items:**
- "Is the code clean?" (subjective)
- "Does it work?" (too vague)
- "Is performance good?" (not specific)

**Create tasks for each test case using `[UAT]` prefix:**
```
[ ] [UAT] Create new user account
[ ] [UAT] Login with credentials
[ ] [UAT] View dashboard activity
[ ] [UAT] Export data to CSV
[⋯] [BG] Run automated test suite
```

Background automated tests while performing manual verification:
- Run `uv run pytest` via `Ctrl+B` to background
- Continue with manual checks while tests run
- Mark `[✓]` as tests pass or `[!]` if blocked

### Step 3: Walk Through Testing

For each testable item, one at a time:

1. **Mark task in_progress:**
   ```
   [→] [UAT] Create new user account
   ```

2. **State what to test:**
   > "Test 1: Can you create a new user account?"

3. **Provide instructions:**
   > "Try creating a user at /register with email and password"

4. **Ask for result:**
   > "Did it work? (yes/no/describe the issue)"

5. **Mark task result:**
   - Pass: `[✓] [UAT] Create new user account`
   - Fail: `[!] [UAT] Create new user account (blocked: invalid credentials)`

6. **Wait for my response** before moving to the next item

### Step 4: Handle Failures

If I report an issue:

#### 4a. Diagnose
- Ask clarifying questions
- Try to reproduce
- Identify the root cause

#### 4b. Create Fix Plan
If the issue is clear, create a fix plan in `.planning/{N}-FIX-{M}.md`:

```markdown
# Phase {N} - Fix {M}: [Issue Description]

## Issue
[What's broken]

## Root Cause
[Why it's broken]

## Fix
### Step 1
[How to fix it]

### Step 2
[Verification]

## Verification
- [ ] [How to verify the fix]
```

#### 4c. Offer Options
> "I've identified the issue. Would you like me to:
> 1. Fix it now (run `/execute-phase {N}` with the fix plan)
> 2. Add it to the backlog for later
> 3. Investigate more first"

### Step 5: Document Results

After all testing, create `.planning/{N}-UAT.md`:

```markdown
# Phase {N} User Acceptance Testing

## Date: [YYYY-MM-DD]

## Tests Performed

### Test 1: [Test Name]
**Status:** Pass / Fail
**Notes:** [Any observations]

### Test 2: [Test Name]
**Status:** Pass / Fail
**Notes:** [Any observations]

## Summary
- **Passed:** X of Y tests
- **Failed:** X of Y tests

## Issues Found
1. [Issue description] → Fix plan: {N}-FIX-{M}.md
2. [Issue description] → Added to backlog

## Verdict
- [ ] Phase complete - all tests pass
- [ ] Phase needs fixes - see fix plans
- [ ] Phase blocked - major issues found

## Next Steps
[What to do next]
```

### Step 6: Update STATE.md and ROADMAP.md

If all tests pass:
- Update ROADMAP.md: Set phase status to "complete"
- Update STATE.md: Add session log, advance to next phase

If fixes needed:
- Keep phase status as "verifying"
- Note the fix plans in STATE.md
- Next step: Run `/execute-phase {N}` to apply fixes

### Step 7: Announce Results and Offer Next Step

Summarize and offer to continue:

**If all tests pass:**
```
✅ Phase $arguments.phase verified!

Tests: [X]/[X] passed
All deliverables confirmed working.

Phase $arguments.phase is complete!
```

**Then ask:**
> "Ready to start Phase [N+1]: [Phase name]? I'll run `/discuss-phase [N+1]` to capture decisions for the next phase."
>
> Or if this was the final phase, I'll help you with `/complete-milestone`.

**If fixes are needed:**
```
⚠️ Phase $arguments.phase needs fixes

Tests: [X]/[Y] passed
Fix plans created: [N]
```

**Then ask:**
> "Would you like me to apply the fixes now? I'll run `/execute-phase $arguments.phase` with the fix plans."

**If user says yes:** Immediately run the appropriate next workflow.

---

## Output Files

| File | Purpose |
|------|---------|
| `.planning/{N}-UAT.md` | User acceptance testing results |
| `.planning/{N}-FIX-{M}.md` | Fix plans (if issues found) |
| `STATE.md` | Updated status |
| `ROADMAP.md` | Phase status updated |

---

## Testing Tips

**For UI features:**
- Test on different screen sizes
- Test edge cases (empty states, long text)
- Test error scenarios

**For APIs:**
- Test happy path
- Test error responses
- Test with invalid input

**For integrations:**
- Test real connections (not mocked)
- Test failure recovery
- Test timeout handling

---

## Common Issues and Diagnoses

| Symptom | Likely Cause |
|---------|--------------|
| Feature doesn't appear | Not imported, wrong route |
| Crashes on load | Missing dependency, null reference |
| Works locally, fails in test | Environment differences |
| Partial functionality | Incomplete implementation |
| Wrong behavior | Logic error, misunderstood requirement |

---

## Example Verification Session

```
Starting verification for Phase 1: User Authentication

Test 1 of 4: Can you create a new user account?
→ Go to /register and submit email + password
→ Did it work?

User: Yes, account created

Test 2 of 4: Can you log in with that account?
→ Go to /login and enter your credentials
→ Did it work?

User: No, getting "Invalid credentials" error

Diagnosing...
The password hash comparison might be failing. Let me check...

Found the issue: Using wrong bcrypt compare method.

Created fix plan: .planning/1-FIX-1.md

Would you like me to:
1. Fix it now
2. Continue testing other features first

User: Fix it now

[Creates fix, runs it, re-verifies]

Test 2 retry: Can you log in now?

User: Yes, it works!

[Continue with remaining tests...]

Results:
- Passed: 4/4 tests (after fix)
- Fix applied: 1-FIX-1

Phase 1 is complete! Next: /discuss-phase 2
```
