### Skills Folder

> Reusable capabilities that agents and commands can reference

## What Are Skills?

Skills are modular, reusable pieces of knowledge or capability that multiple agents/commands can use. Think of them as shared libraries or common patterns that you don't want to duplicate across multiple files.

**Example:**
Instead of explaining "conventional commits format" in 3 different places (commit-push-pr command, commit validator, and review command), create a single `conventional-commits.md` skill that all three can reference.

---

## When to Create a Skill

### ✅ Create a skill when:

1. **Multiple agents need the same knowledge**
   - Example: "Test framework detection" used by test command AND verify-app agent

2. **You have a reusable pattern**
   - Example: "Error message formatting standards"

3. **Complex logic that's used in several places**
   - Example: "Semantic version validation"

4. **Domain-specific expertise**
   - Example: "Conventional commits format" or "REST API best practices"

### ❌ Don't create a skill when:

1. **It's only used in one place**
   - Just include it directly in that command/agent

2. **It's too simple**
   - Example: Don't create a skill for "how to read a file"

3. **It's project-specific**
   - Skills should be reusable across projects in your template

---

## How to Use Skills

### In Commands

Reference skills in your command instructions:

```markdown
# My Custom Command

## Instructions

For commit message format, follow the conventional commits skill:
See: .claude/skills/conventional-commits.md

[Rest of your command]
```

### In Agents

Reference skills in agent workflows:

```markdown
# My Custom Agent

## Step 2: Detect Test Framework

Use the test framework detection skill to identify which test runner to use.
See: .claude/skills/test-detection.md

[Rest of your agent]
```

### In Validators

Reference skills in validation logic:

```python
# my_validator.py

# Check if commit follows conventional commits
# See .claude/skills/conventional-commits.md for format specification
if not follows_conventional_format(message):
    issues.append("Commit must follow conventional commits format")
```

---

## Skills Included

This template includes two example skills:

### 1. Conventional Commits
**File:** `conventional-commits.md`

**What it provides:**
- Conventional commits format specification
- Valid commit types and when to use them
- Examples of good commit messages
- Common mistakes to avoid

**Used by:**
- commit-push-pr command
- commit_validator.py
- review command

### 2. Test Detection
**File:** `test-detection.md`

**What it provides:**
- How to detect test frameworks (npm, pytest, etc.)
- Where test files are typically located
- How to run tests for different project types

**Used by:**
- test command
- verify-app agent

---

## Creating Your Own Skills

### Step 1: Identify the Reusable Pattern

Ask yourself:
- "Am I explaining this same concept in multiple files?"
- "Is this knowledge that multiple agents need?"
- "Would this be useful across different projects?"

### Step 2: Create the Skill File

**Template:**
```markdown
# [Skill Name]

## Purpose
[One sentence describing what this skill provides]

## When to Use
[When should commands/agents reference this skill?]

## The Pattern/Knowledge

[The actual reusable content]

### Examples

[Concrete examples]

### Common Mistakes

[What to avoid]

## References

[Links to documentation, standards, etc.]
```

### Step 3: Reference the Skill

Update your commands/agents to reference the skill instead of duplicating the content.

---

## Example: Creating a "REST API Design" Skill

**Scenario:** You have 3 different commands that need to know REST API best practices.

### 1. Create the skill file

**File:** `.claude/skills/rest-api-design.md`

```markdown
# REST API Design Principles

## Purpose
Provides REST API design best practices for consistent API development.

## When to Use
Reference this when creating, reviewing, or modifying REST API endpoints.

## The Principles

### URL Structure
- Use nouns, not verbs: `/users` not `/getUsers`
- Use plural for collections: `/users` not `/user`
- Use hierarchical structure: `/users/{id}/posts`

### HTTP Methods
- GET: Retrieve resources
- POST: Create new resources
- PUT: Replace entire resource
- PATCH: Update part of resource
- DELETE: Remove resource

### Status Codes
- 200 OK: Successful GET, PUT, PATCH
- 201 Created: Successful POST
- 204 No Content: Successful DELETE
- 400 Bad Request: Invalid input
- 401 Unauthorized: Missing/invalid auth
- 403 Forbidden: Valid auth but no permission
- 404 Not Found: Resource doesn't exist
- 500 Internal Server Error: Server issue

### Examples

Good:
```
GET /api/users
POST /api/users
GET /api/users/123
PUT /api/users/123
DELETE /api/users/123
GET /api/users/123/posts
```

Bad:
```
GET /api/getUsers
POST /api/createUser
GET /api/user/123
```

### Common Mistakes
- Using verbs in URLs
- Inconsistent naming (singular/plural)
- Wrong status codes
- Not versioning your API

## References
- REST: https://restfulapi.net/
- HTTP Status Codes: https://httpstatuses.com/
```

### 2. Reference the skill in commands/agents

**In your API review command:**
```markdown
# API Review Command

## Step 3: Check REST Compliance

Verify the API follows REST best practices.
See: .claude/skills/rest-api-design.md

Check:
- URL structure follows conventions
- HTTP methods used correctly
- Status codes are appropriate
```

**In your API generator agent:**
```markdown
# API Generator Agent

## Guidelines

When generating API endpoints, follow REST principles.
Reference: .claude/skills/rest-api-design.md

Generate endpoints that:
- Use plural nouns for resources
- Follow hierarchical structure
- Return appropriate status codes
```

---

## Skills vs. Commands vs. Agents

**Skills** = Reusable knowledge/patterns
- Example: "How to format commit messages"
- Like a reference manual or style guide

**Commands** = Entry points for specific tasks
- Example: "/commit-push-pr" - executes a workflow
- Like a function you can call

**Agents** = Specialized AI personas
- Example: "code-simplifier" - reviews code for complexity
- Like a teammate with specific expertise

**Relationship:**
- Commands and Agents USE Skills
- Skills CONTAIN reusable knowledge
- Commands ORCHESTRATE workflows
- Agents APPLY expertise

---

## Best Practices

### DO ✅

- **Keep skills focused** - One skill = one concept
- **Make them reusable** - Should work across projects
- **Include examples** - Show concrete usage
- **Update centrally** - When you improve a skill, all users benefit
- **Reference clearly** - Always point to skills instead of duplicating

### DON'T ❌

- **Don't duplicate** - If you copy/paste, make it a skill instead
- **Don't mix concerns** - Don't combine unrelated patterns in one skill
- **Don't make them too specific** - Should be reusable, not project-specific
- **Don't forget to update** - When standards change, update the skill

---

## Advanced: Skill Composition

Skills can reference other skills:

**Example:**

`api-documentation.md` skill references:
- `rest-api-design.md` for API structure
- `conventional-comments.md` for code comment format
- `markdown-formatting.md` for doc formatting

This creates a hierarchy of reusable knowledge.

---

## Troubleshooting

### "My agents aren't using the skill"

**Problem:** Created a skill but agents don't reference it

**Solution:**
- Explicitly tell agents to reference the skill in their instructions
- Example: "For commit format, see .claude/skills/conventional-commits.md"

### "Skill is too long"

**Problem:** Skill file is becoming unwieldy

**Solution:**
- Break it into multiple focused skills
- Create a "parent" skill that references the specific ones
- Example: `testing.md` references `unit-testing.md`, `e2e-testing.md`, `test-coverage.md`

### "Skill vs. inline explanation"

**Problem:** Not sure if something should be a skill

**Solution:**
- Use the "Rule of Three": If you need it in 3+ places, make it a skill
- If it's less than 5 lines, probably inline it
- If it's project-specific, probably inline it

---

## Examples from Real Projects

### JavaScript Project Skills
- `npm-scripts.md` - Common npm commands
- `eslint-rules.md` - Linting standards
- `react-patterns.md` - React best practices
- `testing-library.md` - How to write tests

### Python Project Skills
- `pep8-style.md` - Python style guide
- `pytest-patterns.md` - Test patterns
- `virtual-env.md` - Environment management
- `type-hints.md` - Type annotation guide

### DevOps Project Skills
- `dockerfile-best-practices.md`
- `ci-cd-pipeline.md`
- `kubernetes-patterns.md`
- `terraform-conventions.md`

---

## Your Next Steps

1. **Review the included skills**
   - Read `conventional-commits.md`
   - Read `test-detection.md`

2. **Identify patterns in your project**
   - Look for repeated explanations
   - Find common workflows
   - Notice domain expertise you're duplicating

3. **Create your first custom skill**
   - Pick something you explain often
   - Write it once as a skill
   - Reference it everywhere

4. **Iterate and improve**
   - Update skills as you learn
   - Add examples from real usage
   - Refine based on what works

---

*Skills are optional but powerful. They keep your template DRY (Don't Repeat Yourself) and make knowledge centralized and maintainable.*
