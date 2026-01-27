---
description: "Complete git workflow - commit, push, and create pull request"
arguments:
  - name: files
    description: "Files to commit (optional, will prompt if not provided)"
allowed-tools:
  - read
  - bash
# OPTIONAL: Uncomment to enable commit message validation
# hooks:
#   post_tool_use:
#     - tools: ["bash"]
#       command: "python ${CLAUDE_PROJECT_DIR}/.claude/hooks/validators/commit_validator.py"
---

# Commit, Push, and Create Pull Request

> **Advanced Feature**: This command includes optional YAML frontmatter for validation hooks.
> The commit validator is commented out by default. Uncomment the `hooks` section to enable
> automatic commit message validation.

## Context

**Current git status:**
${{ git status --short }}

**Current branch:**
${{ git branch --show-current }}

**Recent commits:**
${{ git log --oneline -5 }}

**Staged changes:**
${{ git diff --cached --stat }}

**Unstaged changes:**
${{ git diff --stat }}

---

## Instructions

You are helping me commit code changes and potentially create a pull request. Follow this workflow:

### Step 1: Analyze Changes
1. Review the git status, staged changes, and unstaged changes shown above
2. Identify what files have been modified
3. Understand the scope of changes (feature, fix, refactor, etc.)

### Step 2: Stage Files (if needed)
- If there are unstaged changes that should be committed, ask me which files to stage
- Use `git add <files>` to stage them
- If everything is already staged, proceed to the next step

### Step 3: Create Commit Message
Create a clear, descriptive commit message following **Conventional Commits** format:

**Format:**
```
<type>: <short description>

<optional detailed description>

Co-Authored-By: visionary-architect
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring (no functionality change)
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks (dependencies, configs, etc.)
- `style:` - Code style/formatting changes
- `perf:` - Performance improvements

**Examples:**
- `feat: add user authentication with JWT tokens`
- `fix: resolve memory leak in data processing pipeline`
- `docs: update API documentation with new endpoints`
- `refactor: simplify error handling logic`

### Step 4: Confirm with Me
**IMPORTANT:** Before committing, show me:
1. The proposed commit message
2. A summary of what will be committed
3. Ask for my explicit approval

Wait for my "yes" or "approve" before proceeding.

### Step 5: Commit
Once approved, create the commit using the message we agreed on.

### Step 6: Push
- Check if the current branch is tracking a remote branch
- If yes, push to the remote: `git push`
- If no, push and set upstream: `git push -u origin <branch-name>`

### Step 7: Create Pull Request (Optional)
- If this is a feature branch (not main/master), ask if I want to create a pull request
- If yes, use `gh pr create` with:
  - Clear title summarizing the changes
  - Description including:
    - What changed and why
    - Testing notes
    - Any breaking changes or migrations needed
  - Include the footer: "🤖 Generated with visionary-architect"

**PR Template:**
```markdown
## Summary
- <bullet point 1>
- <bullet point 2>

## Test Plan
- [ ] <how to test this>
- [ ] <verification steps>

## Notes
<any additional context>

🤖 Generated with visionary-architect
```

---

## Important Rules

- **NEVER** commit without my explicit approval
- **NEVER** force push unless I specifically request it
- **NEVER** commit to main/master directly (warn me if I try)
- **ALWAYS** include the Co-Authored-By line
- **ALWAYS** follow conventional commits format
- **ALWAYS** write clear, descriptive messages (not "fix stuff" or "update code")

---

## Error Handling

If pre-commit hooks fail:
1. Show me the error
2. Suggest fixes
3. Apply fixes
4. Create a NEW commit (never amend unless I request it)

If push fails:
1. Show me the error
2. Suggest resolution (pull, rebase, etc.)
3. Wait for my decision
