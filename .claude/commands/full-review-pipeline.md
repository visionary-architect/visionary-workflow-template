---
description: "Complete code review pipeline with quality gates"
arguments:
  - name: target
    description: "Files or directory to review (optional, defaults to git changes)"
allowed-tools:
  - read
  - bash
  - task
# OPTIONAL: Uncomment to add final validation after the pipeline completes
# hooks:
#   stop:
#     - command: "echo 'Pipeline completed. Review all agent outputs above.'"
---

# Full Review Pipeline

> **Advanced Feature**: This command orchestrates multiple agents in sequence, each with
> their own validation. This demonstrates pipeline-based workflows with quality gates.

## Purpose

Provide comprehensive code review by chaining specialized agents together. Each agent focuses on their expertise, and the pipeline only continues if each stage passes.

## Agent Chain

This pipeline executes agents in the following order:

1. **code-simplifier** - Identify unnecessary complexity and suggest simplifications
2. **review command** - Perform security, performance, and best practices review
3. **verify-app** - Run tests and validate functionality
4. **commit-push-pr** - If all gates pass, assist with committing changes

## When to Use This Pipeline

**Use this pipeline when:**
- You've made significant changes and want thorough review
- You're preparing for deployment
- You want to catch issues before code review
- You need to ensure quality across multiple dimensions

**Skip this pipeline when:**
- Making trivial changes (typos, formatting)
- Iterating rapidly during development
- You only need one specific type of review
- Time is critical and you'll review manually

## How It Works

### Stage 1: Simplification Review

**Agent:** code-simplifier

**What it checks:**
- Unnecessary complexity
- Over-engineered solutions
- Opportunities to simplify logic
- Dead code or unused variables

**Quality gate:**
- Manual review of suggestions
- Decision to simplify before proceeding

**Output:**
```
📊 Simplification Opportunities:

🟡 MODERATE: Function `processData` has nested loops (complexity: 8)
   Suggestion: Extract inner loop to separate function

🟢 MINOR: Variable `temporaryDataStorage` could be renamed to `cache`

No critical complexity issues found.
```

### Stage 2: Code Review

**Agent:** review command

**What it checks:**
- Security vulnerabilities
- Performance issues
- Best practices violations
- Code quality problems

**Quality gate:**
- All 🔴 CRITICAL issues must be addressed
- 🟡 SUGGESTIONS should be considered
- 🟢 NICE-TO-HAVE are optional

**Output:**
```
🔴 CRITICAL: SQL query is vulnerable to injection
   File: src/database.py:42
   Fix: Use parameterized queries

🟡 SUGGESTION: Consider adding error boundary
   File: src/App.tsx:15

All security checks: PASS (with 1 critical fix needed)
```

### Stage 3: Testing & Verification

**Agent:** verify-app

**What it checks:**
- Automated test results
- Manual verification of functionality
- Regression testing
- Error handling

**Quality gate:**
- All critical tests must pass
- No new test failures introduced
- Core functionality verified

**Output:**
```
✅ Automated Tests: 62/63 passed (98.4%)
⚠️  1 failing test (non-critical)
✅ Manual verification: All core features work
✅ Regression checks: No issues found

Recommendation: Fix the 1 failing test, then ship
```

### Stage 4: Commit (Conditional)

**Agent:** commit-push-pr command

**When to execute:**
- Only if all previous stages passed or have acceptable issues
- You've addressed all critical findings
- You're ready to commit the changes

**What it does:**
- Creates conventional commit message
- Pushes to remote
- Optionally creates pull request

## Pipeline Workflow

When you run this command, follow this workflow:

### Step 1: Understand the Scope

```bash
# First, show what will be reviewed
git status --short
git diff --stat
```

Ask: "Do you want to review all changes, or specific files?"

### Step 2: Execute Simplification Review

Invoke the code-simplifier agent:
```
Use the code-simplifier agent to review [target files/changes]
```

**Wait for results**, then ask:
- "Should we address any simplification opportunities before continuing?"
- "Are there critical complexity issues that need fixing?"

**Decision point:** Fix critical complexity issues now, or note them for later.

### Step 3: Execute Code Review

Run the review command:
```
/review [target files]
```

**Wait for results**, then categorize findings:
- 🔴 CRITICAL: Must fix before proceeding
- 🟡 SUGGESTIONS: Consider fixing now
- 🟢 NICE-TO-HAVE: Note for future

**Decision point:**
- If CRITICAL issues found → pause pipeline, fix issues, restart from Stage 1
- If only suggestions → decide whether to fix now or continue
- If all clear → proceed to Stage 3

### Step 4: Execute Testing & Verification

Invoke the verify-app agent:
```
Use the verify-app agent to verify [target changes]
```

**Wait for results**, then check:
- Did all critical tests pass?
- Are there any new test failures?
- Does functionality work as expected?

**Decision point:**
- If tests fail → fix issues, return to Stage 2
- If tests pass with warnings → evaluate if acceptable
- If all tests pass → proceed to Stage 4

### Step 5: Commit Changes (Optional)

If all previous stages passed or have acceptable issues:

```
/commit-push-pr
```

This will:
1. Create a conventional commit message
2. Include all the context from the pipeline
3. Push to remote
4. Optionally create a pull request

**In the PR description, include:**
```markdown
## Summary
[What changed and why]

## Quality Gates Passed
- ✅ Simplification review: [X opportunities identified, Y addressed]
- ✅ Code review: [No critical issues / Critical issues resolved]
- ✅ Testing: [X/Y tests passed]
- ✅ Verification: [All manual checks passed]

## Test Plan
[How to verify this change]
```

## Pipeline Results Summary

At the end of the pipeline, provide a comprehensive summary:

---

### 🎯 Pipeline Results Summary

**Date:** [Today's date]
**Target:** [Files reviewed]
**Duration:** [Approximate time]

---

**Stage 1: Simplification Review**
- Status: ✅ Passed / ⚠️ Issues found / ❌ Critical issues
- Findings: [X opportunities, Y critical]
- Actions taken: [What was simplified]

**Stage 2: Code Review**
- Status: ✅ Passed / ⚠️ Issues found / ❌ Critical issues
- Findings: [X critical, Y suggestions, Z nice-to-have]
- Actions taken: [What was fixed]

**Stage 3: Testing & Verification**
- Status: ✅ Passed / ⚠️ Warnings / ❌ Failed
- Test results: [X/Y tests passed]
- Actions taken: [What was fixed]

**Stage 4: Commit**
- Status: ✅ Committed / ⏭️ Skipped / ❌ Not attempted
- Commit: [commit hash or "not committed"]

---

**Overall Recommendation:**
- ✅ **Ship it** - All quality gates passed, ready for deployment
- ⚠️ **Ship with caution** - Minor issues remain, acceptable for deployment
- ❌ **Do not ship** - Critical issues must be resolved first

**Outstanding Issues:**
- [Issue 1]
- [Issue 2]

**Next Steps:**
1. [Action item 1]
2. [Action item 2]

---

## Customizing the Pipeline

You can customize this pipeline for your needs:

### Add More Stages

Insert additional checks:
```markdown
Stage 2.5: Performance Testing
- Run performance benchmarks
- Check bundle size
- Validate API response times
```

### Change Order

Reorder stages based on priority:
```markdown
1. Testing first (fail fast if tests don't pass)
2. Then code review
3. Then simplification
```

### Skip Stages

For specific scenarios:
```markdown
Quick pipeline (skip simplification):
1. Code review
2. Testing
3. Commit

Documentation changes (skip testing):
1. Simplification review
2. Commit
```

### Custom Validation Hooks (Optional)

You can create a custom pipeline validator by copying the template:
```bash
cp .claude/hooks/validators/TEMPLATE_validator.py .claude/hooks/validators/pipeline_validator.py
```

Then enable it in settings.json:
```yaml
# Note: Create the validator first before adding this hook
hooks:
  stop:
    - command: "python .claude/hooks/validators/pipeline_validator.py"
```

## Error Handling

If any stage fails:

1. **Stop the pipeline** - Don't continue to next stage
2. **Show the error** - Display what went wrong
3. **Suggest fixes** - Provide actionable next steps
4. **Offer to restart** - After fixes, offer to restart from failed stage

Example:
```
❌ Stage 2 Failed: Code Review found critical security issues

Critical Issues:
- SQL injection vulnerability in src/database.py:42

Recommendation:
1. Fix the SQL injection issue using parameterized queries
2. Re-run the code review: /review src/database.py
3. If review passes, continue pipeline from Stage 3

Would you like me to help fix the SQL injection issue?
```

## Best Practices

**DO:**
- ✅ Run the full pipeline before major deploys
- ✅ Address critical issues immediately
- ✅ Consider all suggestions seriously
- ✅ Document which issues were intentionally deferred
- ✅ Use this for code that will be reviewed by others

**DON'T:**
- ❌ Run this pipeline for every tiny change
- ❌ Skip stages without good reason
- ❌ Ignore critical findings
- ❌ Rush through the pipeline
- ❌ Use this for time-critical hotfixes

## Example: Complete Pipeline Run

**Scenario:** Added new user authentication feature

```
User: Run the full review pipeline on the auth changes