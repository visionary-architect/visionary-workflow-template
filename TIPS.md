# Tips for visionary_template_1 v1.1

Quick tips to get the most out of the new multi-session worker system.

---

## Multi-Session Workers

**Tip:** Use `/tandem` to boot up a second worker for your project. Great for parallel task execution while you focus on something else.

**Tip:** Before a long coding session, use `/add-task` to queue up all your planned work. Then claim tasks one at a time with `/claim-task`.

**Tip:** Use `/list-tasks` to see the queue at a glance - it shows available, claimed, and completed tasks with priority levels.

**Tip:** Workers auto-coordinate via file locks. If two workers try to claim the same task, only one succeeds.

**Tip:** Stuck tasks (claimed but inactive for 30+ minutes) auto-release back to the queue.

---

## Task Prioritization

**Tip:** Use priority 1 (High) for blocking work, priority 2 (Normal) for regular features, priority 3 (Low) for nice-to-haves.

**Tip:** When adding tasks with `/add-task`, include context about related files. This helps workers pick up tasks faster.

**Tip:** The `/add-task` command will interview you if your description is vague. Let it - specific tasks get done faster.

---

## Session Management

**Tip:** Always run `/pause-work` before ending a session. It saves your context to STATE.md and DEVLOG.md.

**Tip:** The `warmup_cache.py` hook pre-compiles your context. Run `/resume-work` in a new session for instant context restoration.

**Tip:** If you're working across multiple sessions, each gets a unique tag (@worker-1, @worker-2). Check who's claimed what with `/list-tasks`.

---

## Workflow Combinations

**Tip:** Run `/tandem` + `/add-task` for batch processing. Queue up 10 tasks, launch 2 workers, watch them complete in parallel.

**Tip:** Use `/quick` for one-off fixes. Use `/add-task` → `/tandem` for larger planned work.

**Tip:** After completing a task, `/complete-task` will offer to show you the next available task. Stay in flow.

---

## Troubleshooting

**Tip:** If hooks aren't running, check that Python 3.8+ is installed and in your PATH.

**Tip:** If tasks aren't persisting, verify `CLAUDE_CODE_TASK_LIST_ID` is set in `.claude/settings.json`.

**Tip:** The work queue is stored at `.claude/session/work_queue.json`. You can inspect or reset it manually if needed.

---

## Best Practices

**Tip:** Keep individual tasks small and focused. "Add login form" is better than "Implement entire auth system."

**Tip:** Use the priority system to signal what needs attention first. High-priority tasks show with a red indicator.

**Tip:** When working in parallel, avoid tasks that touch the same files. The `file_conflict_checker.py` hook will warn you, but it's better to plan ahead.

**Tip:** Document decisions in `/pause-work` handoffs. Future-you (or future-worker) will thank you.

---

*See [CHANGELOG.md](CHANGELOG.md) for the full list of v1.1 changes.*
