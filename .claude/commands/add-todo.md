---
description: "Capture ideas for later without interrupting current work"
---

# Add Todo

> Capture ideas for later without interrupting current work.

---

## Context

**Existing Todos:**
${{ dir .planning\todos /b 2>nul || ls .planning/todos 2>/dev/null || echo "No todos yet" }}

---

## Instructions

Capture an idea or task for later.

### Quick Capture
Create `.planning/todos/[YYYY-MM-DD]-[slug].md`:

```markdown
# Todo: [Brief Title]

**Added:** [YYYY-MM-DD]
**Priority:** medium
**Category:** [feature | bug | refactor | idea]

## Description
[What needs to be done]

## Context
[Why this came up]
```

Confirm: "Captured: '[title]'"

### Using Todos
When planning phases, review `.planning/todos/` and add to REQUIREMENTS.md.
