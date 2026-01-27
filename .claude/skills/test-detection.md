---
name: test-detection
description: Provides logic for automatically detecting which test framework a project uses and how to run tests. Reference when running tests or setting up test execution.
---

# Test Framework Detection

## Purpose

Provides logic for automatically detecting which test framework a project uses and how to run tests.

## When to Use

Reference this skill when:
- Running tests automatically
- Setting up test execution in commands/agents
- Detecting project type for appropriate test commands
- Creating test-running workflows

## Detection Strategy

Check in this order for the fastest, most accurate detection:

### 1. Check Package Files

**Node.js / JavaScript:**
```bash
# Check package.json for test script
cat package.json | grep "\"test\":"

# Check for common test dependencies
cat package.json | grep -E "(jest|vitest|mocha|jasmine|ava)"
```

**Python:**
```bash
# Check for pytest in requirements or pyproject.toml
cat requirements.txt | grep pytest
cat pyproject.toml | grep pytest

# Check for unittest in project structure
find . -name "test_*.py" -o -name "*_test.py"
```

**Go:**
```bash
# Go uses built-in testing
# Check for _test.go files
find . -name "*_test.go"
```

**Rust:**
```bash
# Rust uses built-in testing
# Check Cargo.toml
cat Cargo.toml
```

**Ruby:**
```bash
# Check Gemfile for test frameworks
cat Gemfile | grep -E "(rspec|minitest)"
```

### 2. Check for Test Directories

Common test directory names:
- `test/`
- `tests/`
- `__tests__/`
- `spec/`
- `specs/`

```bash
# Check if test directories exist
ls -la | grep -E "(test|spec)"
```

### 3. Check for Config Files

Framework-specific config files:

| Framework | Config File |
|-----------|-------------|
| Jest | `jest.config.js`, `jest.config.json` |
| Vitest | `vitest.config.ts`, `vitest.config.js` |
| Pytest | `pytest.ini`, `pyproject.toml` |
| Mocha | `.mocharc.js`, `.mocharc.json` |
| Karma | `karma.conf.js` |
| PHPUnit | `phpunit.xml` |

```bash
# Check for config files
ls -la | grep -E "(jest|vitest|pytest|mocha|karma|phpunit)"
```

## Test Commands by Framework

### JavaScript / TypeScript

**Jest:**
```bash
# Via npm script (preferred)
npm test

# Direct
npx jest

# Watch mode
npm test -- --watch

# Coverage
npm test -- --coverage
```

**Vitest:**
```bash
npm test

# Or direct
npx vitest

# Watch mode (default)
npx vitest

# Run once
npx vitest run
```

**Mocha:**
```bash
npm test

# Or direct
npx mocha

# Specific file
npx mocha test/mytest.js
```

### Python

**Pytest:**
```bash
# All tests
pytest

# Specific file
pytest tests/test_feature.py

# Verbose
pytest -v

# Coverage
pytest --cov=src tests/
```

**Unittest:**
```bash
# Discover and run all tests
python -m unittest discover

# Specific test file
python -m unittest tests.test_feature

# Verbose
python -m unittest discover -v
```

### Go

```bash
# All tests
go test ./...

# Specific package
go test ./pkg/mypackage

# Verbose
go test -v ./...

# Coverage
go test -cover ./...
```

### Rust

```bash
# All tests
cargo test

# Specific test
cargo test test_name

# Show output
cargo test -- --nocapture
```

### Ruby

**RSpec:**
```bash
# All tests
bundle exec rspec

# Specific file
bundle exec rspec spec/models/user_spec.rb

# Format
bundle exec rspec --format documentation
```

**Minitest:**
```bash
# Via rake
bundle exec rake test

# Direct
ruby -Itest test/test_helper.rb
```

### PHP

**PHPUnit:**
```bash
# All tests
./vendor/bin/phpunit

# Specific file
./vendor/bin/phpunit tests/MyTest.php

# Coverage
./vendor/bin/phpunit --coverage-html coverage
```

## Smart Test Detection Logic

Use this decision tree:

```python
def detect_test_command():
    # 1. Check for npm/yarn project
    if file_exists("package.json"):
        package_json = read_file("package.json")

        # Check for test script
        if "scripts" in package_json and "test" in package_json["scripts"]:
            return "npm test"

        # Check dependencies
        if "jest" in str(package_json):
            return "npx jest"
        elif "vitest" in str(package_json):
            return "npx vitest run"
        elif "mocha" in str(package_json):
            return "npx mocha"

    # 2. Check for Python project
    if file_exists("requirements.txt") or file_exists("pyproject.toml"):
        if "pytest" in read_file("requirements.txt") or "pytest" in read_file("pyproject.toml"):
            return "pytest"
        return "python -m unittest discover"

    # 3. Check for Go project
    if file_exists("go.mod"):
        return "go test ./..."

    # 4. Check for Rust project
    if file_exists("Cargo.toml"):
        return "cargo test"

    # 5. Check for Ruby project
    if file_exists("Gemfile"):
        gemfile = read_file("Gemfile")
        if "rspec" in gemfile:
            return "bundle exec rspec"
        return "bundle exec rake test"

    # 6. Check for PHP project
    if file_exists("composer.json"):
        return "./vendor/bin/phpunit"

    # 7. Fallback
    return None  # Ask user
```

## Test File Patterns

### JavaScript / TypeScript

**Jest / Vitest:**
- `*.test.js`, `*.test.ts`
- `*.spec.js`, `*.spec.ts`
- `__tests__/**/*.js`, `__tests__/**/*.ts`

**Mocha:**
- `test/**/*.js`
- `test/**/*.spec.js`

### Python

**Pytest:**
- `test_*.py`
- `*_test.py`
- `tests/test_*.py`

**Unittest:**
- `test*.py`
- `tests/test_*.py`

### Go

- `*_test.go`

### Rust

- `tests/*.rs`
- `#[test]` functions in `src/`

### Ruby

**RSpec:**
- `spec/**/*_spec.rb`

**Minitest:**
- `test/**/*_test.rb`

## Running Specific Tests

### When Files Changed

Detect which tests to run based on changed files:

```bash
# Get changed files
git diff --name-only

# For each changed file, find related test file:
# src/auth.js -> tests/auth.test.js
# models/user.py -> tests/test_user.py
```

**Mapping patterns:**

| Language | Source File | Test File |
|----------|-------------|-----------|
| JavaScript | `src/auth.js` | `src/__tests__/auth.test.js` |
| Python | `src/auth.py` | `tests/test_auth.py` |
| Go | `pkg/auth.go` | `pkg/auth_test.go` |
| Rust | `src/auth.rs` | `tests/auth_test.rs` |

## Integration with Agents/Commands

### In Test Command

```markdown
## Step 1: Detect Test Framework

Use test-detection skill to identify the test command.

1. Check package.json for test script
2. Check for common test frameworks
3. Use appropriate test command
```

### In Verify-App Agent

```markdown
## Step 3: Run Automated Tests

Reference: .claude/skills/test-detection.md

Detect and run the appropriate test command:
- JavaScript: npm test or npx jest
- Python: pytest or unittest
- Go: go test ./...
[etc.]
```

## Handling Edge Cases

### Multiple Test Frameworks

Some projects have multiple test types:

```bash
# Run all test types
npm run test:unit
npm run test:integration
npm run test:e2e
```

**Detection:**
Check package.json scripts for:
- `test:unit`
- `test:integration`
- `test:e2e`
- `test:all`

### Monorepos

Projects with multiple packages:

```bash
# Lerna
npx lerna run test

# Nx
npx nx run-many --target=test --all

# Turborepo
npx turbo run test
```

### Docker-based Tests

Some projects run tests in Docker:

```bash
# Check for docker-compose.test.yml
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Watch Mode

Many frameworks support watch mode for development:

**Jest:**
```bash
npm test -- --watch
```

**Vitest:**
```bash
npx vitest  # Watch mode is default
```

**Pytest:**
```bash
pytest-watch  # Requires pytest-watch package
```

## Coverage

Generating test coverage:

**Jest:**
```bash
npm test -- --coverage
```

**Pytest:**
```bash
pytest --cov=src --cov-report=html tests/
```

**Go:**
```bash
go test -cover ./...
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

## Validation

After detecting framework, validate:

- [ ] Test command exists
- [ ] Test files are present
- [ ] Dependencies are installed
- [ ] Config files are valid

## References

- Jest: https://jestjs.io/
- Vitest: https://vitest.dev/
- Pytest: https://docs.pytest.org/
- Go Testing: https://golang.org/pkg/testing/
- RSpec: https://rspec.info/

---

*This skill is referenced by: test command, verify-app agent*
