#!/usr/bin/env python3
"""
Auto-capture minimal session state on Claude stop.

This hook runs automatically when a Claude session ends, capturing essential
state for recovery if the user forgot to run /pause-work.

Output: .claude/session/last_snapshot.json
"""
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path


def main():
    """Capture and save session snapshot."""
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "cwd": os.getcwd(),
        "git_status": get_git_status(),
        "modified_files": get_modified_files(),
        "staged_files": get_staged_files(),
        "current_branch": get_current_branch(),
        "active_tasks": get_active_tasks(),
        "claimed_tasks": get_claimed_tasks(),
    }

    output_dir = Path(".claude/session")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "last_snapshot.json"
    temp_file = output_dir / "last_snapshot.tmp"

    # Atomic write - write to temp, then rename
    try:
        with open(temp_file, "w") as f:
            json.dump(snapshot, f, indent=2)
        temp_file.replace(output_file)
        print(f"Session snapshot saved to {output_file}")
    except Exception as e:
        print(f"Warning: Failed to save session snapshot: {e}")
        if temp_file.exists():
            temp_file.unlink()


def get_git_status():
    """Get short git status output."""
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def get_modified_files():
    """Get list of modified (unstaged) files."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        files = result.stdout.strip()
        return files.split("\n") if files else []
    except Exception:
        return []


def get_staged_files():
    """Get list of staged files."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        files = result.stdout.strip()
        return files.split("\n") if files else []
    except Exception:
        return []


def get_current_branch():
    """Get current git branch name."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def get_active_tasks():
    """Get active tasks from the persistent task list."""
    try:
        task_list_id = os.environ.get("CLAUDE_CODE_TASK_LIST_ID", "my-project")
        tasks_dir = Path.home() / ".claude" / "tasks" / task_list_id

        if not tasks_dir.exists():
            return []

        tasks = []
        for task_file in tasks_dir.glob("*.json"):
            try:
                with open(task_file, encoding="utf-8") as f:
                    task = json.load(f)
                # Only include non-completed tasks
                if task.get("status") != "completed":
                    tasks.append({
                        "id": task.get("id"),
                        "subject": task.get("subject", "")[:60],
                        "status": task.get("status", "unknown"),
                    })
            except Exception:
                pass

        return tasks[:10]  # Limit to 10
    except Exception:
        return []


def get_claimed_tasks():
    """Get tasks claimed by this session."""
    locks_file = Path(".claude/session/task_locks.json")
    session_id_file = Path(".claude/session/current_session_id.txt")

    if not locks_file.exists():
        return []

    try:
        # Get current session ID
        session_id = None
        if session_id_file.exists():
            session_id = session_id_file.read_text().strip()

        with open(locks_file, encoding="utf-8") as f:
            locks = json.load(f)

        claims = []
        for task_id, lock in locks.items():
            # Only include claims by this session
            if session_id and lock.get("session_id") == session_id:
                claims.append({
                    "content": lock.get("task_content", "")[:60],
                    "claimed_at": lock.get("claimed_at", "unknown"),
                })

        return claims
    except Exception:
        return []


if __name__ == "__main__":
    main()
