---
description: "Bootstrap codebase intelligence for an existing project"
---

# Analyze Codebase

> Scan the codebase and populate intelligence files.

---

## Purpose

For existing projects, this command analyzes your code to detect patterns, conventions, and structure - populating `.planning/intel/` for context injection.

---

## Instructions

### Step 1: Scan Code Files

Find all code files in the project:
- JavaScript/TypeScript: `.js`, `.ts`, `.jsx`, `.tsx`
- Python: `.py`
- Other languages as appropriate

Exclude:
- `node_modules/`, `venv/`, `.git/`
- Build outputs, generated files
- Test fixtures with mock data

### Step 2: Extract Information

For each file, extract:

**Exports:**
- Function names and signatures
- Class names
- Constants/variables
- Default exports

**Imports:**
- What modules are imported
- Import patterns (named, default, namespace)

**Patterns:**
- Naming conventions used
- File organization patterns

### Step 3: Detect Conventions

Analyze across files (need 5+ samples, 70%+ consistency):

**Naming:**
- Variables: camelCase, snake_case, etc.
- Functions: camelCase, PascalCase, etc.
- Classes: PascalCase
- Files: kebab-case, camelCase, etc.
- Directories: lowercase, kebab-case, etc.

**Directory Purposes:**
- `src/components/` → React components
- `src/utils/` → Utility functions
- `src/hooks/` → Custom hooks
- `src/api/` → API routes
- etc.

### Step 4: Update Intel Files

**`.planning/intel/index.json`:**
```json
{
  "_version": "1.0",
  "_lastUpdated": "[timestamp]",
  "files": {
    "src/components/Button.tsx": {
      "exports": ["Button", "ButtonProps"],
      "imports": ["react", "./styles"],
      "type": "component"
    }
  }
}
```

**`.planning/intel/conventions.json`:**
```json
{
  "_version": "1.0",
  "_lastUpdated": "[timestamp]",
  "naming": {
    "variables": "camelCase",
    "functions": "camelCase",
    "classes": "PascalCase",
    "files": "PascalCase",
    "directories": "lowercase"
  },
  "directories": {
    "src/components": "React components",
    "src/utils": "Utility functions",
    "src/hooks": "Custom React hooks"
  },
  "patterns": [
    "Components export named + default",
    "Hooks prefix with 'use'",
    "Utils are pure functions"
  ]
}
```

**`.planning/intel/summary.md`:**
```markdown
# Codebase Intelligence Summary

**Last Updated:** [timestamp]
**Files Indexed:** [N]

## Tech Stack
- Language: [detected]
- Framework: [detected]
- Key libraries: [detected]

## Naming Conventions
- Variables: camelCase
- Functions: camelCase
- Components: PascalCase
- Files: PascalCase for components, camelCase for utils

## Directory Structure
- `src/components/` - React components
- `src/utils/` - Utility functions
- `src/hooks/` - Custom hooks

## Key Patterns
- Components export both named and default
- Hooks always prefixed with "use"
- API routes follow REST conventions

## High-Impact Files
- `src/lib/db.ts` - Database client (imported by 15 files)
- `src/utils/auth.ts` - Auth utilities (imported by 12 files)
```

### Step 5: Report Results

Show summary:
```
Codebase Analysis Complete
─────────────────────────
Files scanned: [N]
Exports found: [N]
Imports mapped: [N]

Conventions detected:
- Naming: [summary]
- Directories: [N] purposes identified

High-impact files:
- [file] ([N] dependents)
- [file] ([N] dependents)

Intel files updated in .planning/intel/
```

---

## When to Run

- **First time:** After `/init-project` on existing code
- **After major refactoring:** To update patterns
- **Periodically:** If intel feels stale

The intel hook will maintain this incrementally after initial analysis.
