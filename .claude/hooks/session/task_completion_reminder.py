#!/usr/bin/env python3
"""
Remind about uncompleted tasks when session ends.

This Stop hook checks if the session has claimed tasks that weren't completed
and prints a reminder.
"""
import json
import os
from datetime import datetime
from pathlib import Path

SESSION_DIR = Path(".claude/session")
WORK_QUEUE_FILE = SESSION_DIR / "work_queue.json"
STARTUP_CONTEXT_FILE = SESSION_DIR / "worker_startup_context.json"


def main():
    """Check for uncompleted tasks and remind."""
    session_tag = os.environ.get("CLAUDE_SESSION_TAG", "main")

    # Check if this session had a claimed task from startup
    claimed_task = get_startup_task()

    if not claimed_task:
        # Check work queue for tasks claimed by this session
        claimed_task = get_claimed_task_for_session(session_tag)

    if claimed_task:
        task_id = claimed_task.get("id", "unknown")
        desc = claimed_task.get("description", "")[:60]

        reason = (
            f"TASK COMPLETION REMINDER: You have a claimed task that wasn't marked complete: "
            f"{task_id}: {desc}... "
            f"Run /complete-task to mark it done, or it returns to 'available' after 30 min."
        )
        # Output structured JSON for Stop hook protocol
        print(json.dumps({"result": "block", "reason": reason}))


def get_startup_task():
    """Get task from startup context if still valid."""
    if not STARTUP_CONTEXT_FILE.exists():
        return None

    try:
        with open(STARTUP_CONTEXT_FILE, encoding="utf-8") as f:
            context = json.load(f)

        # Check if this is a recent context (within 4 hours)
        timestamp = context.get("timestamp")
        if timestamp:
            ctx_time = datetime.fromisoformat(timestamp)
            if (datetime.now() - ctx_time).total_seconds() > 4 * 3600:
                return None  # Stale context

        task = context.get("selected_task")
        if task and task.get("status") != "completed":
            return task

        return None
    except Exception:
        return None


def get_claimed_task_for_session(session_tag):
    """Get any task claimed by this session from work queue."""
    if not WORK_QUEUE_FILE.exists():
        return None

    try:
        with open(WORK_QUEUE_FILE, encoding="utf-8") as f:
            queue = json.load(f)

        for task in queue.get("tasks", []):
            if (task.get("status") == "claimed" and
                task.get("claimed_by") == session_tag):
                return task

        return None
    except Exception:
        return None


if __name__ == "__main__":
    main()
