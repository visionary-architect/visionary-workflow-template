---
name: conventional-commits
description: Provides the specification for conventional commits format, ensuring consistent and parseable commit messages across the project.
---

# Conventional Commits Format

## Purpose

Provides the specification for conventional commits format, ensuring consistent and parseable commit messages across the project.

## When to Use

Reference this skill when:
- Creating commit messages
- Validating commit message format
- Reviewing commit history
- Setting up commit hooks or validators

## The Format

### Structure

```
<type>(<scope>): <subject>

<body>

<footer>
```

**All parts:**
- **type** (required): The kind of change
- **scope** (optional): The area of codebase affected
- **subject** (required): Brief description in imperative mood
- **body** (optional): Detailed explanation
- **footer** (optional): Breaking changes, issue references

### Type

Must be one of:

| Type | When to Use | Example |
|------|-------------|---------|
| `feat` | New feature for the user | `feat: add user authentication` |
| `fix` | Bug fix for the user | `fix: resolve memory leak in cache` |
| `docs` | Documentation only changes | `docs: update API endpoint list` |
| `style` | Code style/formatting (no logic change) | `style: format code with prettier` |
| `refactor` | Code change that neither fixes bug nor adds feature | `refactor: extract validation to separate function` |
| `perf` | Performance improvement | `perf: optimize database query` |
| `test` | Adding or updating tests | `test: add unit tests for auth module` |
| `build` | Changes to build system or dependencies | `build: upgrade React to v18` |
| `ci` | Changes to CI/CD configuration | `ci: add automated deployment workflow` |
| `chore` | Other changes that don't modify src or test files | `chore: update .gitignore` |
| `revert` | Reverts a previous commit | `revert: revert "feat: add feature X"` |

### Scope (Optional)

The scope provides additional context about what part of the codebase changed.

**Examples:**
- `feat(auth): add JWT token refresh`
- `fix(api): handle null response from database`
- `docs(readme): add installation instructions`
- `test(utils): add edge case tests`

**Common scopes:**
- Component names: `(button)`, `(header)`, `(sidebar)`
- Modules: `(auth)`, `(api)`, `(database)`
- Features: `(checkout)`, `(dashboard)`, `(settings)`
- Files/areas: `(config)`, `(tests)`, `(docs)`

### Subject Line

**Rules:**
- Use imperative mood: "add" not "added" or "adds"
- Don't capitalize first letter
- No period at the end
- Maximum 50 characters (recommended), 72 max
- Be specific but concise

**Good examples:**
- `feat: add user profile page`
- `fix: prevent crash when input is empty`
- `refactor: simplify authentication logic`

**Bad examples:**
- `feat: Added user profile page` (not imperative, capitalized)
- `fix: fixes` (too vague)
- `update stuff` (missing type)
- `feat: add a really comprehensive user profile page with lots of features.` (too long)

### Body (Optional)

**When to include:**
- The change is complex and needs explanation
- You want to explain the "why" behind the change
- There are important side effects or considerations

**Format:**
- Separate from subject with blank line
- Wrap at 72 characters
- Explain what and why, not how
- Can have multiple paragraphs

**Example:**
```
feat: add caching layer for API requests

API requests were taking 2-3 seconds on average, causing poor UX.
This adds a Redis caching layer that caches responses for 5 minutes.

Cache invalidation happens on POST, PUT, DELETE operations.
```

### Footer (Optional)

**Used for:**
- Breaking changes
- Issue references
- Co-authored commits

**Format:**
```
BREAKING CHANGE: <description>
Fixes #123
Closes #456
Co-Authored-By: Name <email>
```

**Examples:**
```
feat: redesign authentication flow

BREAKING CHANGE: `login()` method now returns Promise<User> instead of User
Fixes #234
Co-Authored-By: visionary-architect
```

## Complete Examples

### Simple Feat
```
feat: add logout button to navigation
```

### Fix with Scope
```
fix(api): handle timeout errors gracefully
```

### Feature with Body
```
feat: implement user search

Add search functionality to the users page with:
- Real-time search as user types
- Search by name, email, or username
- Debounced to prevent excessive API calls
```

### Refactor with Breaking Change
```
refactor: reorganize API endpoint structure

Restructure API endpoints to follow REST conventions more closely.
This provides better consistency and makes the API easier to understand.

BREAKING CHANGE: All endpoints now use plural resource names.
- /user -> /users
- /post -> /posts
- /comment -> /comments

Clients will need to update their API calls.
```

### Fix with Issue Reference
```
fix: prevent duplicate user registration

Add uniqueness constraint on email field and handle duplicate
registration attempts gracefully with clear error message.

Fixes #789
```

### With Co-Author
```
feat: add dark mode toggle

Implements dark mode with user preference persistence in local storage.
Theme applies to all components and respects user's system preferences
when no manual selection has been made.

Co-Authored-By: visionary-architect
```

## Common Mistakes

### ❌ Wrong Type
```
update: add new feature
added: user profile
```
**Fix:** Use valid types: `feat`, `fix`, `docs`, etc.

### ❌ Wrong Mood
```
feat: added user authentication
feat: adding user authentication
feat: adds user authentication
```
**Fix:** Use imperative mood
```
feat: add user authentication
```

### ❌ Capitalized Subject
```
feat: Add user authentication
```
**Fix:** Don't capitalize
```
feat: add user authentication
```

### ❌ Period at End
```
feat: add user authentication.
```
**Fix:** No period
```
feat: add user authentication
```

### ❌ Too Vague
```
fix: bug fix
feat: updates
chore: changes
```
**Fix:** Be specific
```
fix: resolve null pointer in user profile
feat: add email notifications
chore: update eslint configuration
```

### ❌ Missing Blank Line
```
feat: add feature

Body starts immediately
```
**Fix:** Add blank line
```
feat: add feature

Body after blank line
```

## Validation Checklist

When writing/reviewing commits, check:

- [ ] Type is valid (feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert)
- [ ] Subject is in imperative mood
- [ ] Subject doesn't start with capital letter
- [ ] Subject doesn't end with period
- [ ] Subject is ≤50 characters (recommended) or ≤72 (max)
- [ ] Blank line between subject and body (if body exists)
- [ ] Body lines wrap at 72 characters
- [ ] Breaking changes are noted in footer
- [ ] Issue references included if applicable
- [ ] Co-Authored-By included if applicable

## Benefits

**Why use conventional commits?**

1. **Automatic changelog generation**
   - Tools can parse commits to generate CHANGELOG.md
   - Group by type (Features, Fixes, etc.)

2. **Semantic versioning**
   - `feat:` → minor version bump
   - `fix:` → patch version bump
   - `BREAKING CHANGE:` → major version bump

3. **Better git history**
   - Easy to scan and understand changes
   - Filter commits by type
   - See scope of changes at a glance

4. **Team communication**
   - Consistent format helps everyone understand changes
   - Less ambiguity about what changed

5. **Automated workflows**
   - Trigger CI/CD based on commit type
   - Run specific tests based on scope
   - Auto-assign reviewers based on scope

## Tools

**Commit message helpers:**
- `commitizen` - Interactive prompt for commits
- `commitlint` - Validate commit messages
- `husky` + `commitlint` - Git hooks for validation

**Changelog generators:**
- `standard-version` - Automated versioning and changelog
- `semantic-release` - Fully automated release workflow

## References

- Conventional Commits: https://www.conventionalcommits.org/
- Semantic Versioning: https://semver.org/
- Angular Commit Guidelines: https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit

---

*This skill is referenced by: commit-push-pr command, commit_validator.py, review command*
