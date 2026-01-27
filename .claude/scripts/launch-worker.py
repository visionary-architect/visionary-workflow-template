#!/usr/bin/env python3
"""
Launch a Claude worker session with proper multi-session coordination.

Usage:
    python .claude/scripts/launch-worker.py [TAG]

Examples:
    python .claude/scripts/launch-worker.py          # Auto-assigns worker-N
    python .claude/scripts/launch-worker.py worker-1 # Explicit tag
    python .claude/scripts/launch-worker.py feature  # Custom tag

The script:
1. Assigns a unique worker tag if not specified
2. Shows current active sessions and their claimed tasks
3. Shows available tasks from work queue
4. Prompts for task selection (number, C=custom, S=skip)
5. Launches Claude with the appropriate environment and context
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add scripts directory to path for work_queue import
sys.path.insert(0, str(Path(__file__).parent))
from work_queue import claim_task as wq_claim_task, load_queue as wq_load_queue

SESSION_DIR = Path(".claude/session")
SESSIONS_FILE = SESSION_DIR / "sessions.json"
LOCKS_FILE = SESSION_DIR / "task_locks.json"
WORK_QUEUE_FILE = SESSION_DIR / "work_queue.json"
STARTUP_CONTEXT_FILE = SESSION_DIR / "worker_startup_context.json"


def main():
    """Launch a worker session."""
    # Get or generate session tag
    if len(sys.argv) > 1:
        session_tag = sys.argv[1]
    else:
        session_tag = get_next_worker_tag()

    print("=" * 64)
    print("  MULTI-SESSION WORKER")
    print("=" * 64)
    print()

    # Show current state
    show_active_sessions()
    show_claimed_tasks()

    # Show work queue and prompt for selection
    available_tasks = show_work_queue()
    selected_task, custom_task = prompt_task_selection(available_tasks, session_tag)

    print()
    print(f"Starting worker: @{session_tag}")
    print("-" * 64)

    # Create startup context for the new session
    startup_prompt = create_startup_context(
        session_tag=session_tag,
        selected_task=selected_task,
        custom_task=custom_task
    )

    if startup_prompt:
        print()
        print("Task context will be injected into session.")

    print()

    # Set environment and launch
    env = os.environ.copy()
    env["CLAUDE_SESSION_TAG"] = session_tag
    env["CLAUDE_CODE_ENABLE_TASKS"] = "true"
    # Use project slug from settings.json or default
    env["CLAUDE_CODE_TASK_LIST_ID"] = os.environ.get("CLAUDE_CODE_TASK_LIST_ID", "{{PROJECT_SLUG}}")

    # Build command with optional prompt
    cmd = ["claude"]
    if startup_prompt:
        cmd.extend(["--print", startup_prompt])

    # Launch Claude
    try:
        subprocess.run(cmd, env=env)
    except FileNotFoundError:
        print("Error: 'claude' command not found.")
        print("Make sure Claude Code CLI is installed and in your PATH.")
        sys.exit(1)


def get_next_worker_tag():
    """Find the next available worker-N tag."""
    sessions = load_sessions()

    # Find used worker numbers
    used_numbers = set()
    for session in sessions.values():
        tag = session.get("tag", "")
        if tag.startswith("worker-"):
            try:
                num = int(tag.split("-")[1])
                used_numbers.add(num)
            except (ValueError, IndexError):
                pass

    # Find lowest available
    worker_num = 1
    while worker_num in used_numbers:
        worker_num += 1

    return f"worker-{worker_num}"


def show_active_sessions():
    """Show currently active sessions."""
    sessions = load_sessions()
    now = datetime.now()

    active = []
    for session_id, session in sessions.items():
        try:
            last_seen = datetime.fromisoformat(session.get("last_seen", ""))
            age = now - last_seen
            if age < timedelta(minutes=5):
                active.append({
                    "tag": session.get("tag", "unknown"),
                    "id": session_id[:8],
                    "age": format_age(age),
                    "tools": session.get("tool_count", 0),
                })
        except Exception:
            pass

    if active:
        print("ACTIVE SESSIONS:")
        print("-" * 40)
        for s in active:
            print(f"  @{s['tag']:<12} ({s['id']}) - {s['tools']} tools, last seen {s['age']} ago")
        print()
    else:
        print("No other active sessions.")
        print()


def show_claimed_tasks():
    """Show currently claimed tasks."""
    locks = load_locks()

    if not locks:
        return

    print("CLAIMED TASKS:")
    print("-" * 40)
    for task_id, lock in list(locks.items())[:10]:  # Show max 10
        tag = lock.get("session_tag", "unknown")
        content = lock.get("task_content", "")[:40]
        print(f"  @{tag:<12} -> {content}...")

    if len(locks) > 10:
        print(f"  ... and {len(locks) - 10} more")
    print()


def show_work_queue():
    """Show available tasks from work queue and return them."""
    queue = load_work_queue()
    tasks = queue.get("tasks", [])

    # Filter to available tasks only
    available = [t for t in tasks if t.get("status") == "available"]

    # Sort by priority (1 first), then created_at
    available.sort(key=lambda t: (t.get("priority", 2), t.get("created_at", "")))

    print("AVAILABLE TASKS:")
    print("-" * 64)

    if not available:
        print("  No tasks in queue.")
        print()
        print("  [C] Enter a custom task")
        print("  [S] Skip (start without assigned task)")
    else:
        for i, task in enumerate(available[:10], 1):
            priority_label = {1: "[HIGH]", 2: "[NORM]", 3: "[LOW]"}.get(
                task.get("priority", 2), "[???]"
            )
            desc = task.get("description", "")[:48]
            print(f"  [{i}] {priority_label} {desc}")
            if task.get("context"):
                ctx = task["context"][:52]
                print(f"      Context: {ctx}")

        if len(available) > 10:
            print(f"      ... and {len(available) - 10} more tasks")

        print()
        print("  [C] Enter a custom task (different from above)")
        print("  [S] Skip (start without assigned task)")

    print("=" * 64)
    return available[:10]  # Return max 10 for selection


def prompt_task_selection(available_tasks, session_tag):
    """
    Prompt user to select a task.

    Args:
        available_tasks: List of available tasks from work queue
        session_tag: The session tag for claiming tasks

    Returns:
        (selected_task, custom_task) - one or both may be None
    """
    max_num = len(available_tasks)

    while True:
        print()
        if max_num > 0:
            prompt = f"Select task [1-{max_num}/C/S]: "
        else:
            prompt = "Select [C/S]: "

        try:
            choice = input(prompt).strip().upper()
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            sys.exit(0)

        if choice == "S":
            print("Starting without assigned task.")
            return None, None

        if choice == "C":
            print()
            print("Enter your custom task description:")
            try:
                custom = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nCancelled.")
                sys.exit(0)

            if custom:
                print(f"Custom task: {custom}")
                return None, custom
            else:
                print("Empty task, skipping.")
                return None, None

        # Try to parse as number
        try:
            num = int(choice)
            if 1 <= num <= max_num:
                task = available_tasks[num - 1]
                task_id = task.get("id", "unknown")
                desc = task.get("description", "")[:50]
                print(f"Selected: {desc}")

                # Claim the task
                claim_success = claim_task_in_queue(task_id, session_tag)
                if claim_success:
                    print(f"Task {task_id} claimed.")
                else:
                    print(f"Warning: Could not claim task (may already be claimed).")

                return task, None
            else:
                print(f"Please enter a number between 1 and {max_num}, or C/S.")
        except ValueError:
            if max_num > 0:
                print(f"Invalid input. Enter 1-{max_num}, C, or S.")
            else:
                print("Invalid input. Enter C or S.")


def create_startup_context(session_tag, selected_task=None, custom_task=None):
    """
    Create startup context file and return a prompt string.

    Returns:
        A prompt string to pass to Claude, or None if no task.
    """
    context = {
        "session_tag": session_tag,
        "timestamp": datetime.now().isoformat(),
        "selected_task": selected_task,
        "custom_task": custom_task,
    }

    # Save context file
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(STARTUP_CONTEXT_FILE, "w", encoding="utf-8") as f:
            json.dump(context, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save startup context: {e}")

    # Build prompt string
    if selected_task:
        task_id = selected_task.get("id", "")
        desc = selected_task.get("description", "")
        ctx = selected_task.get("context", "")

        prompt = f"You are worker @{session_tag}. "
        prompt += f"You have claimed task {task_id}: {desc}"
        if ctx:
            prompt += f"\n\nAdditional context: {ctx}"
        prompt += "\n\nPlease work on this task. Use /resume-work first to load project context."
        prompt += "\n\nIMPORTANT: When you finish this task, use /complete-task to mark it done."
        return prompt

    elif custom_task:
        prompt = f"You are worker @{session_tag}. "
        prompt += f"Your assigned task is: {custom_task}"
        prompt += "\n\nPlease work on this task. Use /resume-work first to load project context."
        prompt += "\n\nIMPORTANT: When you finish, let me know so I can help you pick up the next task."
        return prompt

    return None


def claim_task_in_queue(task_id, session_tag):
    """Claim a task in the work queue. Returns True on success."""
    success, message = wq_claim_task(task_id, session_tag)
    return success


def format_age(td):
    """Format timedelta as human readable."""
    seconds = int(td.total_seconds())
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m"
    else:
        return f"{seconds // 3600}h {(seconds % 3600) // 60}m"


def load_sessions():
    """Load sessions registry."""
    if not SESSIONS_FILE.exists():
        return {}
    try:
        with open(SESSIONS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def load_locks():
    """Load task locks."""
    if not LOCKS_FILE.exists():
        return {}
    try:
        with open(LOCKS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def load_work_queue():
    """Load work queue."""
    return wq_load_queue()


if __name__ == "__main__":
    main()
