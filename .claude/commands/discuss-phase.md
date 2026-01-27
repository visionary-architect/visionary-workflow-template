---
description: "Capture implementation decisions before planning a phase"
arguments:
  - name: phase
    description: "Phase number to discuss (e.g., 1, 2, 3)"
---

# Discuss Phase

> Capture implementation preferences and decisions before planning.

---

## Purpose

This command analyzes a phase and identifies "gray areas" - implementation details that could go multiple ways. By making these decisions upfront, the planning phase can create precise, actionable plans.

---

## Context

**Current State:**
${{ type STATE.md 2>nul || cat STATE.md 2>/dev/null || echo "STATE.md not found" }}

**Roadmap:**
${{ type ROADMAP.md 2>nul || cat ROADMAP.md 2>/dev/null || echo "ROADMAP.md not found" }}

---

## Instructions

You are helping me discuss Phase $arguments.phase before planning it.

### Step 1: Read Phase Details

1. Read ROADMAP.md to find Phase $arguments.phase
2. Read REQUIREMENTS.md to understand what this phase must deliver
3. Identify the phase's summary and deliverables

### Step 2: Identify Gray Areas

Based on what this phase is building, identify areas that need decisions. Different types of work have different gray areas:

**Visual/UI Features:**
- Layout and density
- Interactions and animations
- Empty states and loading states
- Responsive behavior
- Color and styling choices

**APIs/Backend:**
- Response format and structure
- Error handling approach
- Authentication method
- Rate limiting strategy
- Logging verbosity

**Data/Content:**
- Data structure and schema
- Content organization
- Naming conventions
- Validation rules

**Architecture:**
- File organization
- Component structure
- State management approach
- Testing strategy

### Step 3: Ask Targeted Questions

For each gray area you identify:

1. Explain what the decision is about
2. Present 2-3 options with trade-offs
3. Ask for my preference
4. Wait for my response before moving on

**Example:**
> "For the user list component, how should we handle empty states?
> 1. Simple text message ('No users found')
> 2. Illustrated empty state with call-to-action
> 3. Just hide the component entirely
>
> Which approach do you prefer?"

### Step 4: Document Decisions

After all questions are answered, create `.planning/{phase}-CONTEXT.md` with:

```markdown
# Phase {N} Context

> Implementation decisions captured via /discuss-phase {N}

## Phase Overview
[Summary from ROADMAP.md]

## Decisions Made

### [Decision Area 1]
**Question:** [What was decided]
**Decision:** [The choice made]
**Rationale:** [Why this was chosen]

### [Decision Area 2]
...

## Locked Decisions
These decisions are now locked for planning:
- [Decision 1]
- [Decision 2]

## Open Questions
[Any questions that couldn't be answered yet]
```

### Step 5: Update STATE.md

Update STATE.md:
- Add decisions to "Recent Decisions" table
- Update "Current Phase" status to "discussing"
- Add session log entry

### Step 6: Offer Next Step

Summarize and offer to continue:

```
✅ Phase $arguments.phase discussion complete!

Decisions captured: [N]
- [Decision 1 summary]
- [Decision 2 summary]
- ...

Open questions: [N or "None"]
```

**Then ask:**
> "Ready to create the implementation plan? I'll run `/plan-phase $arguments.phase` to break this into atomic tasks."
>
> Or if you need to discuss more, just let me know.

**If user says yes:** Immediately run the plan-phase workflow.

**If user wants changes:** Adjust decisions and re-save CONTEXT.md.

---

## Output Files

| File | Purpose |
|------|---------|
| `.planning/{N}-CONTEXT.md` | All decisions for this phase |
| `STATE.md` | Updated with decisions and status |

---

## Important Notes

- Don't ask about obvious technical choices unless they genuinely matter
- Focus on decisions that affect the user experience or architecture
- It's okay to have some open questions - note them for later
- If the phase is very simple, it might have few or no gray areas
- The goal is to eliminate ambiguity before planning

---

## Example Gray Areas by Phase Type

**"Add user authentication" phase:**
- Session vs JWT tokens?
- Remember me functionality?
- Password requirements?
- Social login options?

**"Create dashboard" phase:**
- Widget layout (grid vs list)?
- Which metrics to show first?
- Refresh frequency?
- Mobile layout?

**"API integration" phase:**
- Error retry strategy?
- Caching approach?
- Rate limiting handling?
- Timeout values?
