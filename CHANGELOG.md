# Changelog

All notable changes to visionary-workflow-template will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [1.1.0] - 2026-01-26

### Added

#### Multi-Session Worker System
Run parallel AI sessions that coordinate on shared work queues.

**6 New Commands:**
| Command | Purpose |
|---------|---------|
| `/add-task` | Add tasks to a persistent queue with priority and context |
| `/list-tasks` | View queue status (available, claimed, completed) |
| `/claim-task` | Claim a queued task for your current session |
| `/complete-task` | Mark your claimed task as done |
| `/remove-task` | Remove a task from the queue |
| `/tandem` | Launch an additional worker session in a new terminal |

**New Scripts (`.claude/scripts/`):**
- `work_queue.py` - Persistent task queue with file locking
- `launch-worker.py` - Worker session launcher with task selection UI
- `launch-worker.bat` - Windows batch launcher
- `session-status.py` - View active sessions and their claimed tasks

**New Session Hooks (`.claude/hooks/session/`):**
- `session_coordinator.py` - Auto-assigns unique worker tags
- `task_claim_validator.py` - Prevents duplicate task claims
- `file_conflict_checker.py` - Warns when multiple sessions edit same file
- `warmup_cache.py` - Pre-compiles context for instant `/resume-work`
- `auto_snapshot.py` - Periodic state snapshots
- `task_completion_reminder.py` - Reminds to mark tasks complete

#### New Intel Hooks (Optional)
**Added to `.claude/hooks/intel/`:**
- `event_logger.py` - Logs tool usage for analytics
- `file_change_tracker.py` - Tracks which files change most frequently
- `test_result_tracker.py` - Records test pass/fail history

These are disabled by default. Enable in `settings.json` if you want session analytics.

#### New Validator
- `dangerous_command_checker.py` - Warns before destructive git operations (force push, reset --hard, etc.)

### Changed

- **Command count:** 19 → 25
- **SETUP.md:** Added Multi-Session Workers workflow section and updated directory structure
- **README.md:** Added Task Queue Commands table
- **CONTEXT.md:** Added Task Queue Commands reference section

### Summary

| Category | v1.0 | v1.1 |
|----------|------|------|
| Commands | 19 | 25 |
| Session hooks | 0 | 6 |
| Intel hooks | 1 | 4 |
| Scripts | 0 | 4 |
| Multi-session support | No | Yes |

### Upgrade Path

If upgrading from v1.0:

1. Copy new command files to `.claude/commands/`:
   - `add-task.md`, `list-tasks.md`, `claim-task.md`
   - `complete-task.md`, `remove-task.md`, `tandem.md`
2. Copy `.claude/scripts/` directory (new)
3. Copy `.claude/hooks/session/` directory (new)
4. Copy new intel hooks if desired
5. Update `settings.json` with new hook configurations

Or start fresh with v1.1 and migrate your `CONTEXT.md` customizations.

---

## [1.0.0] - 2026-01-24

### Added

- Initial release of visionary-workflow-template
- **19 Slash Commands** for structured development workflow
- **3 Specialized Agents:** code-simplifier, debug-helper, verify-app
- **3 Skills:** conventional-commits, test-detection, frontend-design
- **Validator hooks:** invariant_validator, commit_validator, json_validator, markdown_validator
- **Codebase indexer:** Auto-indexes code files after edits
- **Planning structure:** `.planning/` directory with intel, quick, todos, research subdirectories
- **Session management:** STATE.md, DEVLOG.md for context preservation
- **Tech-stack agnostic:** Works with any language or framework

### Core Workflow Commands

| Command | Purpose |
|---------|---------|
| `/init-project` | Interactive project setup wizard |
| `/discuss-phase` | Capture implementation decisions |
| `/plan-phase` | Create atomic task plans |
| `/execute-phase` | Implement with progress tracking |
| `/verify-work` | User acceptance testing |
| `/pause-work` | Create session handoff |
| `/resume-work` | Restore session context |
| `/quick` | Fast ad-hoc task execution |
| `/progress` | View current project status |
| `/commit-push-pr` | Automated git workflow |
| `/test` | Smart test runner |
| `/review` | Comprehensive code review |
| `/explain` | Non-technical explanations |
| `/check-invariants` | Validate against project rules |
| `/analyze-codebase` | Bootstrap codebase intelligence |
| `/complete-milestone` | Archive milestone and tag release |
| `/new-milestone` | Start new version |
| `/add-todo` | Capture ideas for later |
| `/full-review-pipeline` | Multi-stage review pipeline |

---

## Template Versioning

This template follows semantic versioning:
- **Major:** Breaking changes to workflow or file structure
- **Minor:** New features, commands, or hooks (backward compatible)
- **Patch:** Bug fixes, documentation updates

When using this template, the version is noted in:
- `README.md` footer
- `SETUP.md` footer
- This `CHANGELOG.md`
