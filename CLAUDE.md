# Project: {{PROJECT_NAME}}

> **Template Version:** visionary_template_1 v1.0
> **Last Updated:** {{DATE}}
> **Status:** Not Initialized

---

## Overview

<!-- Fill in during /init-project -->
**What:** [Brief description of what you're building]
**Why:** [Problem being solved]
**For whom:** [Target users/audience]

---

## Tech Stack

<!-- Fill in during /init-project -->
**Language:** [e.g., Python 3.11+, TypeScript, Go]
**Framework:** [e.g., FastAPI, Next.js, Gin]
**Package Manager:** [e.g., UV, npm, pnpm, cargo]
**Database:** [if applicable]

**Key Dependencies:**
- [dependency 1]
- [dependency 2]

---

## Development Workflow

### Quick Reference Commands

**Install dependencies:**
```bash
# [Your install command here]
```

**Run tests:**
```bash
# [Your test command here]
```

**Lint & format:**
```bash
# [Your lint/format commands here]
```

**Start development:**
```bash
# [Your dev command here]
```

### Standard Workflow

When making changes, follow this sequence:

1. **Make your changes** to the code
2. **Quick validation** - Run your linter (fast feedback)
3. **Type check** - If applicable
4. **Run relevant tests** - Test the specific area you changed
5. **Format code** - Run your formatter
6. **Review changes** - Use `/review` command or manual review
7. **Commit** - Use `/commit-push-pr` with conventional commit message

---

## Project Structure

```
{{PROJECT_NAME}}/
├── [your directories here]
└── ...
```

<!-- Document your project structure after initialization -->

---

## Project Rules & Preferences

### Core Invariants

<!-- Define rules that every code change must preserve -->
| # | Invariant | Meaning |
|---|-----------|---------|
| 1 | [Invariant 1] | [What it means and why it matters] |
| 2 | [Invariant 2] | [What it means and why it matters] |
| 3 | [Invariant 3] | [What it means and why it matters] |

### Always Do

- **Follow conventional commits format:**
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation
  - `refactor:` for code refactoring
  - `test:` for adding/updating tests
  - `chore:` for maintenance tasks

- **Write tests for new functionality**

- [Add your project-specific rules]

### Never Do

- [Add your project-specific restrictions]

### Code Style Preferences

- **Naming conventions:** [e.g., snake_case for variables/functions, PascalCase for classes]
- **File naming:** [e.g., snake_case.py, kebab-case.ts]
- **Max line length:** [e.g., 100 characters]
- **Indentation:** [e.g., 4 spaces, 2 spaces]

---

## Workflow Commands

This project uses the Visionary workflow:

### Core Workflow
- **`/init-project`** - Initialize project with vision, requirements, and roadmap
- **`/discuss-phase N`** - Capture implementation decisions for phase N
- **`/plan-phase N`** - Create atomic task plans for phase N
- **`/execute-phase N`** - Execute plans with fresh context and atomic commits
- **`/verify-work N`** - User acceptance testing for phase N

### Supporting Commands
- **`/quick`** - Fast execution for small, ad-hoc tasks
- **`/progress`** - Show current status and next steps
- **`/pause-work`** - Create handoff + document session
- **`/resume-work`** - Restore context from STATE.md + DEVLOG.md
- **`/add-todo`** - Capture ideas for later

### Milestone Management
- **`/complete-milestone`** - Archive milestone and tag release
- **`/new-milestone`** - Start a new version

### Codebase Intelligence
- **`/analyze-codebase`** - Bootstrap intelligence for existing code

### Utility Commands
- **`/commit-push-pr`** - Automated commit, push, and PR creation
- **`/test`** - Smart test runner based on changes
- **`/explain`** - Non-technical code explanations
- **`/review`** - Comprehensive code review

---

## Task Management

This project uses persistent, dependency-aware task tracking.

### Environment Setup

Project uses these environment variables (configured in `.claude/settings.json`):
- `CLAUDE_CODE_TASK_LIST_ID={{PROJECT_SLUG}}` for persistent tasks
- `CLAUDE_SESSION_TAG=main` for session identification

Tasks persist across sessions in `~/.claude/tasks/{{PROJECT_SLUG}}/`.

### Task Naming Convention

**Format:**
```
[<Phase>-<Plan>] Step <N>: <Verb> <object>
```

**Examples:**
```
[1-A] Step 1: Add authentication middleware
[1-B] Step 2: Update user repository
[BG] pytest full suite
[UAT] Verify login flow
```

**Rules:**
1. Always include phase-plan identifier in brackets
2. Steps numbered sequentially starting at 1
3. Use specific file/function names, not vague descriptions
4. Background tasks use prefix: `[BG]`
5. Verification tasks use prefix: `[UAT]`

### Quick Reference

| Action | Command |
|--------|---------|
| View tasks | `/tasks` (built-in) |
| Pause work | `/pause-work` |
| Resume work | `/resume-work` |

### Task Queue Commands (Multi-Session)

| Command | Description |
|---------|-------------|
| `/add-task` | Add a task to the persistent work queue |
| `/list-tasks` | View all tasks in the work queue |
| `/claim-task` | Claim a task for the current session |
| `/complete-task` | Mark a claimed task as complete |
| `/remove-task` | Remove a task from the queue |
| `/tandem` | Launch an additional worker session |

> **Tip:** Use `/tandem` to spawn parallel workers that can claim tasks from the shared queue.

| Status | Meaning |
|--------|---------|
| `[ ]` | Pending |
| `[→]` | In progress |
| `[✓]` | Complete |
| `[!]` | Blocked |

### Multi-Session Coordination

When multiple sessions work on the same task list:

**Task Claiming:**
- Append `(@session-tag)` when marking task `[→]` in_progress
- Only claiming session can mark `[✓]` complete
- Any session can mark `[!]` blocked

**Stale Task Recovery:**
- Tasks claimed >30 min with no activity are stale
- Force unclaim with documentation: `(@main, unclaimed from @worker-2 - stale)`
- Verify no partial changes before continuing

---

## Specialized Agents Available

- **`code-simplifier`** - Reviews code and suggests simplifications
- **`verify-app`** - QA testing and verification after changes
- **`debug-helper`** - Systematic debugging assistance

---

## Testing Strategy

**Test Types:**
- Unit tests: [location]
- Integration tests: [location]

**Coverage Goals:** [target, e.g., 80%]

**Running Tests:**
```bash
# [Your test command here]
```

---

## Lessons Learned

> The AI automatically adds entries when mistakes are corrected or patterns are discovered.

### {{DATE}}
- Project initialized from visionary_template_1

---

## Context Management

> The AI's quality can degrade as conversations get long. Use these practices to maintain peak performance.

### Session Start Checklist
At the start of each session, The AI should read:
1. This file (CLAUDE.md)
2. STATE.md - Current focus, recent decisions, handoff notes
3. DEVLOG.md - Recent sessions, active bugs, progress history
4. `.planning/intel/summary.md` - Codebase patterns (if exists)

### When to Start a Fresh Session
- After completing a major feature or phase
- When the AI starts giving inconsistent responses
- After 30+ back-and-forth messages
- When switching to a completely different area of the codebase

### Best Practices
- **Keep tasks focused:** 2-3 related items per session works best
- **Use STATE.md:** Track progress across sessions
- **Use `/quick`:** For small, isolated changes
- **Use Plan Mode:** For complex features (Shift+Tab twice)

### Signs of Context Degradation
- The AI forgets earlier decisions
- Responses become generic
- Code suggestions contradict established patterns
- The AI asks about things already discussed

### Recovery Steps
1. Update STATE.md and DEVLOG.md with current status (`/pause-work`)
2. Start a new AI session
3. The AI reads fresh context from CLAUDE.md, STATE.md, DEVLOG.md, and intel

---

## Autonomous Learning

> The AI should proactively maintain project knowledge without being asked.

### When to Update CLAUDE.md (Lessons Learned)

The AI MUST add a new entry to "Lessons Learned" when:
1. **User corrects a mistake** - Record what was wrong and the correct approach
2. **A bug is found in The AI's code** - Document the pattern that caused it
3. **User expresses preference** - "I prefer X over Y" → record it
4. **A better pattern is discovered** - During refactoring or review
5. **An assumption proves wrong** - Document the correct understanding

**Format:**
```markdown
### YYYY-MM-DD
- [What happened] - [Correct approach going forward]
```

### When to Update STATE.md

The AI MUST update STATE.md:
1. **After completing any task** - Update "Session Log" with what was done
2. **When making a decision** - Add to "Recent Decisions" table
3. **When hitting a blocker** - Add to "Open Questions / Blockers"
4. **Before any significant code change** - Note current focus
5. **Periodically during long tasks** - Every 3-4 tool uses, checkpoint progress

### Self-Diagnosis: Context Degradation

The AI should **proactively suggest a fresh session** when noticing:
- Repeating suggestions that were already rejected
- Forgetting decisions made earlier in the conversation
- Giving generic responses instead of project-specific ones
- Making errors in code that contradict established patterns

**What to say:**
> "I'm noticing some context degradation. I recommend we save progress with `/pause-work` and start a fresh session. This will help me give you better responses."

---

## Notes for the AI

> Special instructions for the AI assistant working on this project

- Always validate against project invariants (if configured)
- Follow existing patterns in the codebase
- Ask when uncertain about requirements
- Update STATE.md after completing work
- Reference this file for project conventions

---

*Template: visionary_template_1 v1.0*
*Documentation: See SETUP.md for initialization instructions*
