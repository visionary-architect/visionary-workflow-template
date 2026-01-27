---
description: "Start a new version/milestone for the project"
---

# New Milestone

> Start a new version/milestone for the project.

---

## Purpose

After completing a milestone, this command helps you plan the next version - same process as `/init-project` but for an existing codebase.

---

## Context

**Current State:**
${{ type STATE.md 2>nul || cat STATE.md 2>/dev/null || echo "STATE.md not found" }}

**Project:**
${{ type PROJECT.md 2>nul || cat PROJECT.md 2>/dev/null || echo "PROJECT.md not found" }}

**Existing Requirements:**
${{ type REQUIREMENTS.md 2>nul || cat REQUIREMENTS.md 2>/dev/null || echo "REQUIREMENTS.md not found" }}

**Roadmap:**
${{ type ROADMAP.md 2>nul || cat ROADMAP.md 2>/dev/null || echo "ROADMAP.md not found" }}

---

## Instructions

You are helping me start a new milestone/version.

### Step 1: Review Previous Work

Summarize what's been completed:
- Previous milestone(s)
- Features shipped
- Any deferred items from previous versions

### Step 2: Gather New Goals

Ask me about the new milestone:

1. **What's the focus of this version?** (Main theme or goal)
2. **What new features do you want to add?**
3. **Are there any deferred items from v[previous] to include?**
4. **Any technical debt or refactoring to address?**
5. **What's the target timeline?** (rough estimate)

### Step 3: Scope Requirements

Organize the work:

1. **Must Have** - Critical for this version
2. **Should Have** - Important but can slip
3. **Nice to Have** - If time permits

### Step 4: Create Phases

Break the work into 2-5 phases:
- Each phase delivers something useful
- Phases build on each other logically
- Earlier phases are more detailed

### Step 5: Update REQUIREMENTS.md

Add new version section:

```markdown
## v[X.X] ([Milestone Name])

### Must Have
- [ ] [Requirement 1] → Phase [N]
- [ ] [Requirement 2] → Phase [N]

### Should Have
- [ ] [Requirement 3] → Phase [N]

### Nice to Have
- [ ] [Requirement 4] → Phase [N]
```

### Step 6: Update ROADMAP.md

Add new milestone section:

```markdown
## Current Milestone: v[X.X] - [Milestone Name]

**Started:** [YYYY-MM-DD]
**Target:** [YYYY-MM-DD or "When ready"]
**Status:** In Progress

---

### Phase 1: [Phase Name]
**Status:** not started
**Requirements:**
- [Requirement from REQUIREMENTS.md]

**Summary:** [1-2 sentences]

**Deliverables:**
- [ ] [Specific deliverable]

[Additional phases...]
```

### Step 7: Update STATE.md

Reset for new milestone:
- Set current milestone
- Set current phase to Phase 1
- Add session log entry
- Clear old handoff notes

### Step 8: Confirm and Offer Next Step

Show summary:

```
═══════════════════════════════════════════════════
NEW MILESTONE CREATED: v[X.X]
═══════════════════════════════════════════════════

MILESTONE: [Name]
PHASES: [N] planned

Phase Overview:
  [ ] Phase 1: [Name]
  [ ] Phase 2: [Name]
  [ ] Phase 3: [Name]

Requirements:
  Must Have: [N] items
  Should Have: [N] items
  Nice to Have: [N] items
═══════════════════════════════════════════════════
```

**Then ask:**
> "Ready to start Phase 1: [Phase 1 name]? I'll run `/discuss-phase 1` to capture implementation decisions before we start planning."

**If user says yes:** Immediately run the discuss-phase workflow for Phase 1.

**If user wants to review first:** Show the ROADMAP.md or wait for their direction.

---

## Output Files

| File | Changes |
|------|---------|
| REQUIREMENTS.md | New version section added |
| ROADMAP.md | New milestone and phases added |
| STATE.md | Reset for new milestone |

---

## Example New Milestone

**Previous:** v1.0 - Core Functionality (complete)

**New Milestone Discussion:**

```
Assistant: What's the focus of v2.0?

User: Adding team collaboration features - multiple users,
      shared projects, permissions.

Assistant: What specific features do you want?

User:
- Team creation and management
- Invite users to teams
- Role-based permissions (admin, member, viewer)
- Shared project workspaces

Assistant: Any deferred items from v1.0 to include?

User: Yeah, we never did the export feature. Add that too.

Assistant: Any technical debt?

User: The authentication system needs refactoring - it's
      getting messy.

[The AI creates phases and updates files]
```

---

## Continuing vs Starting Fresh

**New Milestone (this command):**
- Same project, new version
- Build on existing codebase
- Reference previous work
- Keep project vision intact

**Init Project (/init-project):**
- Brand new project
- Start from scratch
- Define everything fresh

---

## Important Notes

- Review deferred items from previous versions
- Don't overscope - smaller milestones ship faster
- Consider technical debt alongside features
- Keep phases achievable (1-3 sessions each)
