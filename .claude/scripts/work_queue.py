#!/usr/bin/env python3
"""
Persistent work queue for multi-session task management.

This module provides functions to manage a shared task queue that workers can
pull from. Tasks are stored in .claude/session/work_queue.json and persist
across sessions.

Usage:
    from work_queue import add_task, list_tasks, claim_task, complete_task

    # Add a task
    add_task("Implement feature X", priority=1, context="See docs/feature.md")

    # List available tasks
    tasks = list_tasks(status="available")

    # Claim a task
    claim_task("task-abc123", "worker-1")

    # Complete a task
    complete_task("task-abc123", "worker-1")
"""
import json
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
from utils.file_lock import locked_json_rw

SESSION_DIR = Path(".claude/session")
QUEUE_FILE = SESSION_DIR / "work_queue.json"

_QUEUE_DEFAULT = {"tasks": [], "metadata": {"last_updated": None, "total_completed": 0}}

# Stale claim timeout (30 minutes)
STALE_CLAIM_MINUTES = 30


def load_queue():
    """Load the work queue from disk."""
    if not QUEUE_FILE.exists():
        return {"tasks": [], "metadata": {"last_updated": None, "total_completed": 0}}

    try:
        with open(QUEUE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"tasks": [], "metadata": {"last_updated": None, "total_completed": 0}}


def add_task(description, priority=2, context=None, depends_on=None, estimate=None):
    """
    Add a new task to the work queue.

    Args:
        description: Task description
        priority: 1=high, 2=normal, 3=low
        context: Optional additional context
        depends_on: Optional list of task IDs this task depends on
        estimate: Optional size estimate ("small", "medium", "large")

    Returns:
        The created task dict
    """
    with locked_json_rw(QUEUE_FILE, default=_QUEUE_DEFAULT) as (queue, save):
        task = {
            "id": f"task-{uuid.uuid4().hex[:8]}",
            "description": description,
            "priority": priority,
            "status": "available",
            "created_at": datetime.now().isoformat(),
            "claimed_by": None,
            "claimed_at": None,
            "context": context,
            "depends_on": depends_on or [],
            "estimate": estimate,
            "actual_duration": None,
            "history": [
                {
                    "action": "created",
                    "by": "system",
                    "at": datetime.now().isoformat(),
                }
            ],
        }

        # Check if dependencies exist and are not completed
        missing_deps = []
        if depends_on:
            for dep_id in depends_on:
                dep_task = None
                for t in queue["tasks"]:
                    if t["id"] == dep_id:
                        dep_task = t
                        break
                if dep_task is None:
                    missing_deps.append(dep_id)
                elif dep_task["status"] != "completed":
                    task["status"] = "blocked"

        # Store warning about missing dependencies (won't block, but user should know)
        if missing_deps:
            task["missing_deps"] = missing_deps

        queue["tasks"].append(task)
        queue["metadata"]["last_updated"] = datetime.now().isoformat()
        save(queue)

    return task


def list_tasks(status=None):
    """
    List tasks, optionally filtered by status.

    Args:
        status: Filter by status ("available", "claimed", "completed", or None for all)

    Returns:
        List of task dicts
    """
    queue = load_queue()
    tasks = queue["tasks"]

    # Release stale claims
    release_stale_claims()

    if status:
        tasks = [t for t in tasks if t["status"] == status]

    # Sort by priority (1 first), then by created_at
    tasks.sort(key=lambda t: (t.get("priority", 2), t.get("created_at", "")))

    return tasks


def get_task(task_id):
    """Get a specific task by ID."""
    queue = load_queue()

    for task in queue["tasks"]:
        if task["id"] == task_id:
            return task

    return None


def claim_task(task_id, session_tag):
    """
    Claim a task for a worker session.

    Args:
        task_id: The task ID to claim
        session_tag: The claiming session's tag (e.g., "worker-1")

    Returns:
        (success, message)
    """
    with locked_json_rw(QUEUE_FILE, default=_QUEUE_DEFAULT) as (queue, save):
        for task in queue["tasks"]:
            if task["id"] == task_id:
                if task["status"] == "claimed":
                    return False, f"Task already claimed by @{task['claimed_by']}"

                if task["status"] == "completed":
                    return False, "Task already completed"

                if task["status"] == "blocked":
                    return False, f"Task is blocked by dependencies: {task.get('depends_on', [])}"

                task["status"] = "claimed"
                task["claimed_by"] = session_tag
                task["claimed_at"] = datetime.now().isoformat()

                # Add to history
                if "history" not in task:
                    task["history"] = []
                task["history"].append({
                    "action": "claimed",
                    "by": session_tag,
                    "at": datetime.now().isoformat(),
                })

                queue["metadata"]["last_updated"] = datetime.now().isoformat()
                save(queue)
                return True, f"Task claimed by @{session_tag}"

    return False, "Task not found"


def release_task(task_id, released_by=None):
    """
    Release a claimed task back to available.

    Args:
        task_id: The task ID to release
        released_by: Optional session tag of who released it

    Returns:
        (success, message)
    """
    with locked_json_rw(QUEUE_FILE, default=_QUEUE_DEFAULT) as (queue, save):
        for task in queue["tasks"]:
            if task["id"] == task_id:
                if task["status"] != "claimed":
                    return False, "Task is not claimed"

                old_claimer = task["claimed_by"]
                task["status"] = "available"
                task["claimed_by"] = None
                task["claimed_at"] = None

                # Add to history
                if "history" not in task:
                    task["history"] = []
                task["history"].append({
                    "action": "released",
                    "by": released_by or old_claimer or "system",
                    "at": datetime.now().isoformat(),
                })

                queue["metadata"]["last_updated"] = datetime.now().isoformat()
                save(queue)
                return True, "Task released"

    return False, "Task not found"


def complete_task(task_id, session_tag):
    """
    Mark a task as completed.

    Args:
        task_id: The task ID to complete
        session_tag: The session completing the task

    Returns:
        (success, message)
    """
    with locked_json_rw(QUEUE_FILE, default=_QUEUE_DEFAULT) as (queue, save):
        for task in queue["tasks"]:
            if task["id"] == task_id:
                if task["status"] == "completed":
                    return False, "Task already completed"

                # Allow completion even if claimed by different session (with warning)
                if task["claimed_by"] and task["claimed_by"] != session_tag:
                    print(f"Warning: Task was claimed by @{task['claimed_by']}, "
                          f"completed by @{session_tag}")

                task["status"] = "completed"
                task["completed_by"] = session_tag
                task["completed_at"] = datetime.now().isoformat()

                # Calculate actual duration if claimed_at exists
                if task.get("claimed_at"):
                    try:
                        claimed = datetime.fromisoformat(task["claimed_at"])
                        completed = datetime.fromisoformat(task["completed_at"])
                        duration_mins = int((completed - claimed).total_seconds() / 60)
                        task["actual_duration"] = duration_mins
                    except Exception:
                        pass

                # Add to history
                if "history" not in task:
                    task["history"] = []
                task["history"].append({
                    "action": "completed",
                    "by": session_tag,
                    "at": datetime.now().isoformat(),
                })

                queue["metadata"]["total_completed"] = queue["metadata"].get("total_completed", 0) + 1

                # Unblock any tasks that depended on this one
                _unblock_dependent_tasks(queue, task_id)

                queue["metadata"]["last_updated"] = datetime.now().isoformat()
                save(queue)
                return True, "Task completed"

    return False, "Task not found"


def _unblock_dependent_tasks(queue, completed_task_id):
    """Check if any blocked tasks can now be unblocked."""
    for task in queue["tasks"]:
        if task["status"] == "blocked" and task.get("depends_on"):
            # Check if all dependencies are now completed
            all_deps_complete = True
            for dep_id in task["depends_on"]:
                for t in queue["tasks"]:
                    if t["id"] == dep_id and t["status"] != "completed":
                        all_deps_complete = False
                        break
                if not all_deps_complete:
                    break

            if all_deps_complete:
                task["status"] = "available"
                if "history" not in task:
                    task["history"] = []
                task["history"].append({
                    "action": "unblocked",
                    "by": "system",
                    "at": datetime.now().isoformat(),
                    "reason": f"dependency {completed_task_id} completed",
                })


def remove_task(task_id):
    """
    Remove a task from the queue entirely.

    Args:
        task_id: The task ID to remove

    Returns:
        (success, message)
    """
    with locked_json_rw(QUEUE_FILE, default=_QUEUE_DEFAULT) as (queue, save):
        for i, task in enumerate(queue["tasks"]):
            if task["id"] == task_id:
                del queue["tasks"][i]
                queue["metadata"]["last_updated"] = datetime.now().isoformat()
                save(queue)
                return True, "Task removed"

    return False, "Task not found"


def release_stale_claims():
    """Release any claims older than STALE_CLAIM_MINUTES."""
    with locked_json_rw(QUEUE_FILE, default=_QUEUE_DEFAULT) as (queue, save):
        now = datetime.now()
        stale_threshold = timedelta(minutes=STALE_CLAIM_MINUTES)
        released = []

        for task in queue["tasks"]:
            if task["status"] == "claimed" and task.get("claimed_at"):
                try:
                    claimed_at = datetime.fromisoformat(task["claimed_at"])
                    if now - claimed_at > stale_threshold:
                        old_claimer = task["claimed_by"]
                        released.append((task["id"], old_claimer))
                        task["status"] = "available"
                        task["claimed_by"] = None
                        task["claimed_at"] = None

                        # Add to history
                        if "history" not in task:
                            task["history"] = []
                        task["history"].append({
                            "action": "released",
                            "by": "system",
                            "at": now.isoformat(),
                            "reason": f"stale claim (was @{old_claimer})",
                        })
                except Exception:
                    pass

        if released:
            queue["metadata"]["last_updated"] = datetime.now().isoformat()
            save(queue)
            for task_id, session_tag in released:
                print(f"Released stale claim: {task_id} (was @{session_tag})")

    return released


def get_task_history(task_id):
    """Get the history of a task."""
    task = get_task(task_id)
    if not task:
        return None
    return task.get("history", [])


def get_queue_stats():
    """Get statistics about the work queue."""
    queue = load_queue()
    tasks = queue["tasks"]

    return {
        "total": len(tasks),
        "available": len([t for t in tasks if t["status"] == "available"]),
        "blocked": len([t for t in tasks if t["status"] == "blocked"]),
        "claimed": len([t for t in tasks if t["status"] == "claimed"]),
        "completed": len([t for t in tasks if t["status"] == "completed"]),
        "total_completed": queue["metadata"].get("total_completed", 0),
    }


# CLI interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: work_queue.py <command> [args]")
        print()
        print("Commands:")
        print("  add <description> [--priority N] [--context TEXT] [--depends ID] [--estimate SIZE]")
        print("  list [available|claimed|completed|blocked|all]")
        print("  show <task_id>                    # Show task details")
        print("  history <task_id>                 # Show task history")
        print("  claim <task_id> <session_tag>")
        print("  complete <task_id> <session_tag>")
        print("  release <task_id>")
        print("  remove <task_id>")
        print("  stats")
        print()
        print("Estimate sizes: small, medium, large")
        sys.exit(1)

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 3:
            print("Usage: work_queue.py add <description> [--priority N] [--depends ID] [--estimate SIZE]")
            sys.exit(1)

        description = sys.argv[2]
        priority = 2
        context = None
        depends_on = []
        estimate = None

        # Parse optional args
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--priority" and i + 1 < len(sys.argv):
                priority = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--context" and i + 1 < len(sys.argv):
                context = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--depends" and i + 1 < len(sys.argv):
                depends_on.append(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--estimate" and i + 1 < len(sys.argv):
                estimate = sys.argv[i + 1]
                i += 2
            else:
                i += 1

        task = add_task(description, priority=priority, context=context,
                       depends_on=depends_on if depends_on else None, estimate=estimate)
        print(f"Added task: {task['id']}")
        print(f"  Description: {description}")
        print(f"  Priority: {priority}")
        if depends_on:
            print(f"  Depends on: {', '.join(depends_on)}")
        if estimate:
            print(f"  Estimate: {estimate}")
        if task["status"] == "blocked":
            print(f"  Status: BLOCKED (waiting for dependencies)")
        if task.get("missing_deps"):
            print(f"  WARNING: Dependencies not found: {', '.join(task['missing_deps'])}")
            print(f"           (Task is available, not blocked by missing deps)")

    elif command == "list":
        status = sys.argv[2] if len(sys.argv) > 2 else None
        if status == "all":
            status = None  # Show all tasks

        tasks = list_tasks(status=status)

        # Also get blocked tasks if showing available (but not "all")
        if status == "available":
            queue = load_queue()
            blocked = [t for t in queue["tasks"] if t["status"] == "blocked"]
            tasks = tasks + blocked

        if not tasks:
            print("No tasks found.")
        else:
            for task in tasks:
                priority_icon = {1: "[HIGH]", 2: "[NORM]", 3: "[LOW]"}.get(task.get("priority", 2), "[?]")
                status_icon = {
                    "available": "[ ]",
                    "claimed": "[->]",
                    "completed": "[X]",
                    "blocked": "[B]"
                }.get(task["status"], "[?]")
                estimate_icon = ""
                if task.get("estimate"):
                    estimate_icon = f" ({task['estimate'][0].upper()})"
                print(f"{status_icon} {priority_icon}{estimate_icon} {task['id']}: {task['description'][:45]}")
                if task["status"] == "claimed":
                    print(f"      Claimed by @{task['claimed_by']}")
                if task["status"] == "blocked":
                    print(f"      Blocked by: {', '.join(task.get('depends_on', []))}")

    elif command == "show":
        if len(sys.argv) < 3:
            print("Usage: work_queue.py show <task_id>")
            sys.exit(1)

        task = get_task(sys.argv[2])
        if not task:
            print("Task not found.")
            sys.exit(1)

        print(f"Task: {task['id']}")
        print(f"  Description: {task['description']}")
        print(f"  Priority: {task.get('priority', 2)}")
        print(f"  Status: {task['status']}")
        if task.get('context'):
            print(f"  Context: {task['context']}")
        if task.get('depends_on'):
            print(f"  Depends on: {', '.join(task['depends_on'])}")
        if task.get('estimate'):
            print(f"  Estimate: {task['estimate']}")
        if task.get('actual_duration'):
            print(f"  Actual duration: {task['actual_duration']} minutes")
        if task.get('claimed_by'):
            print(f"  Claimed by: @{task['claimed_by']}")
        if task.get('completed_by'):
            print(f"  Completed by: @{task['completed_by']}")
        print(f"  Created: {task.get('created_at', 'unknown')}")

    elif command == "history":
        if len(sys.argv) < 3:
            print("Usage: work_queue.py history <task_id>")
            sys.exit(1)

        history = get_task_history(sys.argv[2])
        if history is None:
            print("Task not found.")
            sys.exit(1)

        if not history:
            print("No history available.")
        else:
            print(f"History for {sys.argv[2]}:")
            for entry in history:
                action = entry.get('action', 'unknown')
                by = entry.get('by', 'unknown')
                at = entry.get('at', 'unknown')
                reason = entry.get('reason', '')
                if reason:
                    print(f"  [{at[:16]}] {action} by @{by} - {reason}")
                else:
                    print(f"  [{at[:16]}] {action} by @{by}")

    elif command == "claim":
        if len(sys.argv) < 4:
            print("Usage: work_queue.py claim <task_id> <session_tag>")
            sys.exit(1)

        success, message = claim_task(sys.argv[2], sys.argv[3])
        print(message)
        sys.exit(0 if success else 1)

    elif command == "complete":
        if len(sys.argv) < 4:
            print("Usage: work_queue.py complete <task_id> <session_tag>")
            sys.exit(1)

        success, message = complete_task(sys.argv[2], sys.argv[3])
        print(message)
        sys.exit(0 if success else 1)

    elif command == "release":
        if len(sys.argv) < 3:
            print("Usage: work_queue.py release <task_id>")
            sys.exit(1)

        success, message = release_task(sys.argv[2])
        print(message)
        sys.exit(0 if success else 1)

    elif command == "remove":
        if len(sys.argv) < 3:
            print("Usage: work_queue.py remove <task_id>")
            sys.exit(1)

        success, message = remove_task(sys.argv[2])
        print(message)
        sys.exit(0 if success else 1)

    elif command == "stats":
        stats = get_queue_stats()
        print("Work Queue Statistics:")
        print(f"  Total tasks: {stats['total']}")
        print(f"  Available: {stats['available']}")
        print(f"  Blocked: {stats['blocked']}")
        print(f"  Claimed: {stats['claimed']}")
        print(f"  Completed: {stats['completed']}")
        print(f"  All-time completed: {stats['total_completed']}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
