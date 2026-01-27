---
description: "Archive a completed milestone and tag the release"
---

# Complete Milestone

> Archive a completed milestone and tag the release.

---

## Purpose

When all phases of a milestone are complete, this command archives the milestone, creates a git tag, and prepares for the next version.

---

## Context

**Current State:**
${{ type STATE.md 2>nul || cat STATE.md 2>/dev/null || echo "STATE.md not found" }}

**Roadmap:**
${{ type ROADMAP.md 2>nul || cat ROADMAP.md 2>/dev/null || echo "ROADMAP.md not found" }}

**Requirements:**
${{ type REQUIREMENTS.md 2>nul || cat REQUIREMENTS.md 2>/dev/null || echo "REQUIREMENTS.md not found" }}

**Git Status:**
${{ git status --short 2>nul || git status --short 2>/dev/null || echo "Not a git repo" }}

**Recent Tags:**
${{ git tag --sort=-creatordate | head -5 2>nul || git tag --sort=-creatordate 2>/dev/null | head -5 || echo "No tags" }}

---

## Instructions

You are helping me complete and archive the current milestone.

### Step 1: Verify Completion

Check that all phases are complete:

1. Read ROADMAP.md
2. Verify each phase has status "complete"
3. If any phase is incomplete, tell me and suggest `/verify-work N`

### Step 2: Verify Requirements

Check that requirements are met:

1. Read REQUIREMENTS.md
2. Verify all "Must Have" items for this version are checked
3. Note any "Should Have" items that weren't completed

### Step 3: Confirm with User

Show completion summary:

```
═══════════════════════════════════════════════════
MILESTONE COMPLETION: v[X.X]
═══════════════════════════════════════════════════

PHASES COMPLETED
───────────────────────────────────────────────────
[✓] Phase 1: [Name]
[✓] Phase 2: [Name]
[✓] Phase 3: [Name]

REQUIREMENTS MET
───────────────────────────────────────────────────
Must Have: [X/X] ✓
Should Have: [X/Y] (optional items)
Nice to Have: [X/Z] (optional items)

DEFERRED TO NEXT VERSION
───────────────────────────────────────────────────
• [Any should-have items not completed]

READY TO COMPLETE?
───────────────────────────────────────────────────
This will:
1. Create git tag: v[X.X.X]
2. Update ROADMAP.md (archive milestone)
3. Update STATE.md (reset for next milestone)

Proceed? (yes/no)
```

### Step 4: Create Git Tag

If user confirms:

```bash
git tag -a v[X.X.X] -m "Release v[X.X.X]: [Milestone Summary]"
```

**Tag message format:**
```
Release v1.0.0: [Milestone Name]

Completed phases:
- Phase 1: [Name]
- Phase 2: [Name]
- Phase 3: [Name]

Key features:
- [Feature 1]
- [Feature 2]
- [Feature 3]
```

### Step 5: Update ROADMAP.md

Move the completed milestone to "Completed Milestones" section:

```markdown
## Completed Milestones

### v1.0 - [Milestone Name]
**Completed:** [YYYY-MM-DD]
**Git Tag:** v1.0.0
**Summary:** [What was delivered]

**Phases:**
- Phase 1: [Name] - [Brief summary]
- Phase 2: [Name] - [Brief summary]
- Phase 3: [Name] - [Brief summary]
```

### Step 6: Archive Planning Files (Optional)

Offer to archive planning files:
- Move `.planning/*-*.md` files to `.planning/archive/v1.0/`
- Keep the intel files (they're ongoing)

### Step 7: Update STATE.md

Reset for next milestone:
- Clear "Current Phase"
- Add session log entry about completion
- Note the git tag

### Step 8: Announce Completion and Offer Next Step

```
═══════════════════════════════════════════════════
MILESTONE COMPLETE!
═══════════════════════════════════════════════════

Version: v[X.X.X]
Git Tag: v[X.X.X]
Phases: [N] completed

The milestone has been archived and tagged.
═══════════════════════════════════════════════════
```

**Then ask based on what's next:**

**If there are more phases in ROADMAP.md that weren't part of this milestone:**
> "There are more phases planned in the roadmap. Would you like me to continue with `/discuss-phase [N]` for the next phase?"

**If this was the final phase of the entire roadmap:**
> "All planned work is complete! Would you like me to start planning the next version with `/new-milestone`?"
>
> Or if you want to push the tag to remote first, I can wait:
> `git push origin v[X.X.X]`

**If user says yes to new-milestone:** Immediately run the new-milestone workflow.

**If user says yes to next phase:** Immediately run the discuss-phase workflow.

**If user wants to push first:** Wait for them to confirm, then offer the next step again.

---

## Output Changes

| File | Changes |
|------|---------|
| Git tag | Created v[X.X.X] |
| ROADMAP.md | Milestone archived |
| STATE.md | Reset for next milestone |
| `.planning/archive/` | Planning files archived (optional) |

---

## Not Ready to Complete

If phases are incomplete:

```
═══════════════════════════════════════════════════
CANNOT COMPLETE MILESTONE
═══════════════════════════════════════════════════

The following phases are not complete:

[!] Phase 2: [Name] - status: executing
[ ] Phase 4: [Name] - status: not started

Complete these phases first:
  /verify-work 2
  /discuss-phase 4

Or mark them as deferred:
  Move incomplete work to v2.0 in REQUIREMENTS.md
═══════════════════════════════════════════════════
```

---

## Important Notes

- Always create git tags (they're your release history)
- Don't skip incomplete phases without documenting why
- Archive planning files for future reference
- Consider pushing tags to remote for backup
