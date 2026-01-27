---
description: "Run tests intelligently based on changed files"
---

# Run Tests Intelligently

## Context

**Recently changed files:**
${{ git diff --name-only HEAD~1 2>/dev/null || echo "No recent changes found" }}

**Currently modified files:**
${{ git status --short }}

**Git root directory:**
${{ git rev-parse --show-toplevel 2>/dev/null || pwd }}

---

## Instructions

You are helping me run tests efficiently. Follow this intelligent workflow:

### Step 1: Detect Project Type

Look for indicators to determine the test framework:

**JavaScript/TypeScript projects:**
- Check for `package.json` with test scripts
- Common: Jest, Vitest, Mocha, Jasmine
- Test command usually: `npm test`, `npm run test`, `yarn test`, `pnpm test`

**Python projects:**
- Check for `pytest.ini`, `setup.py`, `pyproject.toml`
- Common: pytest, unittest
- Test command usually: `pytest`, `python -m pytest`, `python -m unittest`

**Other indicators:**
- Check CONTEXT.md for the "Run tests" command
- Look at file extensions (.test.js, .spec.ts, _test.py, etc.)

### Step 2: Identify Relevant Tests

Based on the changed files, determine which tests are relevant:

1. **Direct test files:** If test files themselves were changed, run those
2. **Corresponding tests:** If source files changed, find matching test files
   - Example: `src/auth.js` → look for `auth.test.js`, `auth.spec.js`, `test_auth.py`
3. **Integration tests:** If multiple files changed, suggest integration tests
4. **All tests:** If core/shared files changed, recommend full test suite

### Step 3: Propose Test Strategy

Present me with a testing strategy:

```
📋 Test Strategy:

Changed files:
- <file1>
- <file2>

Recommended approach:
1. Run <specific tests> (fast, ~Xs)
2. If those pass, optionally run <broader tests>
3. Full suite available if needed

Proceed with step 1?
```

### Step 4: Run Tests

Execute the tests and monitor output:

1. Run the test command
2. Capture and display results clearly
3. Highlight:
   - ✅ Passed tests
   - ❌ Failed tests
   - ⚠️ Warnings or skipped tests

### Step 5: Report Results

**If tests pass:**
```
✅ All tests passed! (<N> tests, <time>)

Next steps:
- Run full test suite? (y/n)
- Ready to commit? Use /commit-push-pr
```

**If tests fail:**
```
❌ <N> test(s) failed

Failed tests:
- <test name 1> - <brief error>
- <test name 2> - <brief error>

Would you like me to:
1. Show detailed error output
2. Help debug the failures
3. Run just the failed tests
```

### Step 6: Offer Next Actions

Based on results, suggest:
- Rerun specific tests
- Debug failures (offer to use the `debug-helper` agent)
- Run full suite
- Proceed to commit if all passed

---

## Test Commands by Project Type

**JavaScript/Node:**
```bash
npm test                    # Run all tests
npm test -- <file>         # Run specific file
npm test -- --watch        # Watch mode
npm run test:coverage      # With coverage
```

**Python:**
```bash
pytest                      # Run all tests
pytest <file>              # Run specific file
pytest -k <pattern>        # Run matching tests
pytest --cov               # With coverage
```

**Other:**
- Check CONTEXT.md for project-specific commands
- Ask me if uncertain

---

## Smart Features

**Watch mode suggestion:**
- If I'm actively developing, offer to run tests in watch mode
- Useful for TDD workflows

**Coverage reports:**
- If tests pass, ask if I want coverage report
- Highlight uncovered areas

**Parallel execution:**
- For large test suites, suggest parallel execution if available
- Example: `pytest -n auto` or `npm test -- --maxWorkers=4`

---

## Important Rules

- **NEVER** skip tests to save time
- **ALWAYS** run at least relevant tests before suggesting commits
- **ALWAYS** show clear pass/fail status
- If tests are missing for changed code, suggest writing tests
- If project has no tests, recommend setting up a test framework

---

## Troubleshooting

**If test command not found:**
1. Check if dependencies are installed (`npm install`, `pip install -r requirements.txt`)
2. Check CONTEXT.md for correct test command
3. Ask me what test framework is being used

**If tests hang:**
1. Suggest timeout settings
2. Offer to kill and debug
3. Check for infinite loops or async issues

**If all tests fail suddenly:**
1. Check if dependencies changed
2. Verify environment variables
3. Check for syntax errors in test setup
