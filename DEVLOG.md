# Development Log

> Living history of development sessions - bugs found, fixes applied, decisions made.

**Purpose:** Captures session-by-session activity. Updated by `/pause-work`, read by `/resume-work`.

---

## Active Issues

| ID | Severity | Description | Found | Status |
|----|----------|-------------|-------|--------|
| | | | | |

<!-- Add bugs here as they're discovered -->

---

## Recent Sessions

<!-- New sessions are added at the top -->

### Session: 2026-01-26 (v1.1 Release + GitHub Publication)

**Phase/Focus:** Template Release

#### Worked On
- Published template to GitHub as `visionary-workflow-template`
- Rebranded from `visionary-claude-template` to generic naming
- Restored CLAUDE.md naming convention (was incorrectly renamed to CONTEXT.md)
- Updated all references from CONTEXT.md → CLAUDE.md for root file
- Added Platform Flexibility section to SETUP.md
- Ran comprehensive review (60+ files verified)
- Fixed version inconsistency (v1.0 → v1.1 in CLAUDE.md)
- Fixed broken doc references in validators/README.md

#### Bugs Found
- **BUG-001**: CONTEXT.md rename broke Claude Code auto-read
  - **Severity:** high
  - **File:** Root `CLAUDE.md`
  - **Details:** Claude Code specifically looks for CLAUDE.md, not CONTEXT.md
  - **Status:** fixed

- **BUG-002**: Version inconsistency in CLAUDE.md
  - **Severity:** medium
  - **File:** `CLAUDE.md` lines 3, 352
  - **Details:** Still showed v1.0 instead of v1.1
  - **Status:** fixed

- **BUG-003**: Broken doc links in validators README
  - **Severity:** low
  - **File:** `.claude/hooks/validators/README.md`
  - **Details:** Referenced non-existent docs directory
  - **Status:** fixed

#### Fixes Applied
| Fix | File | Commit |
|-----|------|--------|
| Restore CLAUDE.md naming | Multiple (16 files) | `001797e` |
| Update version to v1.1 | CLAUDE.md | `8cc6d32` |
| Fix broken doc refs | validators/README.md | `8cc6d32` |

#### Decisions Made
- Root file = CLAUDE.md (Claude Code requirement)
- Component files = CONTEXT.md (subdirectories)
- Phase files = {N}-CONTEXT.md (planning docs)
- Added flexibility note for non-Claude Code users

#### Patterns Learned
- CLAUDE.md is a Claude Code convention - don't rename it
- Component-level CONTEXT.md files don't get auto-read (just docs)

#### Commits
- `c2a957a` feat: release visionary-claude-template v1.1
- `03b2877` refactor: rebrand to visionary-workflow-template
- `001797e` fix: restore CLAUDE.md naming convention
- `8cc6d32` fix: update version to v1.1 and fix broken doc references

---

### Session: {{DATE}} (Project Initialization)

**Phase/Focus:** Setup

#### Worked On
- Initialized project from visionary_template_1

#### Bugs Found
- None

#### Fixes Applied
| Fix | File | Commit |
|-----|------|--------|
| | | |

#### Decisions Made
- Using visionary_template_1 for structured development workflow

#### Patterns Learned
- None yet

#### Commits
- (none yet)

---

<!--
SESSION TEMPLATE - Copy this for new sessions:

### Session: YYYY-MM-DD (Brief Description)

**Phase/Focus:** [Phase N / Ad-hoc / Bug fix]

#### Worked On
- [What was accomplished]

#### Bugs Found
- **BUG-XXX**: [Brief description]
  - **Severity:** [critical/high/medium/low]
  - **File:** `path/to/file`
  - **Details:** [More context]
  - **Status:** [active/investigating/fixed]

#### Fixes Applied
| Fix | File | Commit |
|-----|------|--------|
| [Description] | `file` | `hash` |

#### Decisions Made
- [Decision and rationale]

#### Patterns Learned
- [Pattern or lesson for CLAUDE.md]

#### Commits
- `hash` message

-->
