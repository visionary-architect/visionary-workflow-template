---
description: "Create atomic task plans for a phase"
arguments:
  - name: phase
    description: "Phase number to plan (e.g., 1, 2, 3)"
---

# Plan Phase

> Research and create atomic task plans for implementation.

---

## Purpose

This command takes the decisions from `/discuss-phase` and creates detailed, atomic task plans. Each plan should be small enough to execute in a fresh context window without degradation.

---

## Context

**Current State:**
${{ type STATE.md 2>nul || cat STATE.md 2>/dev/null || echo "STATE.md not found" }}

**Phase Context (if exists):**
${{ type ".planning/$arguments.phase-CONTEXT.md" 2>nul || cat .planning/$arguments.phase-CONTEXT.md 2>/dev/null || echo "No context file yet - run /discuss-phase first" }}

**Requirements:**
${{ type REQUIREMENTS.md 2>nul || cat REQUIREMENTS.md 2>/dev/null || echo "REQUIREMENTS.md not found" }}

---

## Instructions

You are creating task plans for Phase $arguments.phase.

### Step 1: Gather Context

1. Read ROADMAP.md for phase details
2. Read `.planning/{N}-CONTEXT.md` for implementation decisions
3. Read REQUIREMENTS.md for what must be delivered
4. Read CONTEXT.md for project patterns and conventions

### Step 2: Research (Optional)

If this phase involves unfamiliar territory:

1. Identify what needs investigation
2. Research best practices, libraries, patterns
3. Document findings in `.planning/{N}-RESEARCH.md`

Research areas might include:
- Library options and trade-offs
- API documentation
- Architecture patterns
- Similar implementations to reference

### Step 3: Create Task Plans

Break the phase into **2-3 atomic tasks** (never more than 3).

**Why 2-3 tasks?**
- The AI's quality peaks at 0-30% context usage
- Quality degrades significantly beyond 50%
- Smaller tasks = fresher context = better code

**Task sizing rules:**
- Each task should be completable in one focused session
- Each task should touch no more than 5 files
- Each task should have clear, verifiable completion criteria

For each task, create a plan file `.planning/{N}-{M}-PLAN.md`:

```markdown
# Phase {N} - Plan {M}: [Task Name]

## Overview
[1-2 sentence description of what this task accomplishes]

## Prerequisites
- [What must exist before this task]
- [Dependencies on other tasks]

## Files to Create/Modify
- `path/to/file1.ts` - [What changes]
- `path/to/file2.ts` - [What changes]

## Task Details

### Step 1: [Step Name]
[Detailed instructions for this step]

### Step 2: [Step Name]
[Detailed instructions for this step]

### Step 3: [Step Name]
[Detailed instructions for this step]

## Verification
- [ ] [How to verify step 1 worked]
- [ ] [How to verify step 2 worked]
- [ ] [Overall verification command or check]

## Done When
[Clear, measurable completion criteria]

## Notes
[Any important context, gotchas, or references]
```

### Step 4: Verify Coverage

Check that your plans:
- [ ] Cover all requirements for this phase
- [ ] Respect all decisions from CONTEXT.md
- [ ] Have clear verification steps
- [ ] Don't overlap (each file changed by only one task if possible)

### Step 5: Update STATE.md

Update STATE.md:
- Set "Current Phase" status to "planning"
- Add session log entry
- Note any blockers or open questions

### Step 6: Present Plans and Offer Next Step

Summarize and offer to continue:

```
✅ Phase $arguments.phase planning complete!

Plans created: [N]
- Plan A: [Task name] - [brief description]
- Plan B: [Task name] - [brief description]
- Plan C: [Task name] - [brief description] (if applicable)

Estimated scope: [X] files across [N] tasks
```

**Then ask:**
> "Ready to start building? I'll run `/execute-phase $arguments.phase` to implement these plans with atomic commits."
>
> Or if you want to adjust the plans first, let me know what to change.

**If user says yes:** Immediately run the execute-phase workflow.

**If user wants changes:** Adjust plans and re-save.

---

## Output Files

| File | Purpose |
|------|---------|
| `.planning/{N}-RESEARCH.md` | Research findings (optional) |
| `.planning/{N}-A-PLAN.md` | First task plan |
| `.planning/{N}-B-PLAN.md` | Second task plan |
| `.planning/{N}-C-PLAN.md` | Third task plan (if needed) |
| `STATE.md` | Updated status |

---

## Task Types

Use these type annotations in plans:

| Type | Meaning |
|------|---------|
| `auto` | Execute without stopping for confirmation |
| `checkpoint:human-verify` | Stop and ask user to verify before continuing |
| `checkpoint:decision` | Stop and ask user to make a decision |

---

## Plan Quality Checklist

Good plans have:
- [ ] Clear, specific file paths
- [ ] Step-by-step instructions (not vague)
- [ ] Verification steps for each major action
- [ ] Measurable "done when" criteria
- [ ] Notes about potential gotchas

Bad plans have:
- [ ] Vague instructions ("implement the feature")
- [ ] Too many files (>5 per task)
- [ ] No verification steps
- [ ] Unclear completion criteria

---

## Example Plan

```markdown
# Phase 1 - Plan A: Create User Model and Database Schema

## Overview
Set up the user data model with Prisma and create the initial database migration.

## Prerequisites
- Prisma installed and configured
- Database connection string in .env

## Files to Create/Modify
- `prisma/schema.prisma` - Add User model
- `src/lib/db.ts` - Create database client singleton
- `src/types/user.ts` - TypeScript types for User

## Task Details

### Step 1: Define User Model
Add to prisma/schema.prisma:
- id (UUID, primary key)
- email (unique, required)
- passwordHash (required)
- createdAt (default now)
- updatedAt (auto-update)

### Step 2: Create Database Client
Create src/lib/db.ts with PrismaClient singleton pattern
to prevent multiple instances in development.

### Step 3: Generate TypeScript Types
Run prisma generate and create src/types/user.ts
with exported User type matching the schema.

## Verification
- [ ] `npx prisma validate` passes
- [ ] `npx prisma generate` succeeds
- [ ] TypeScript compiles without errors
- [ ] Can import User type in other files

## Done When
User model exists in schema, migration is ready, and types are generated.

## Notes
Using UUID instead of auto-increment for better distributed system support.
```

---

## Important Notes

- If `/discuss-phase` wasn't run, suggest running it first
- Plans should reference decisions from CONTEXT.md
- Keep plans independent when possible (parallel execution)
- If a phase genuinely needs >3 tasks, split it into sub-phases
