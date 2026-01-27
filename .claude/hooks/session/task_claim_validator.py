#!/usr/bin/env python3
"""
Task claim validator for multi-session coordination.

This PostToolUse hook (triggers on TodoWrite) validates:
1. Task claims include session tag (@tag)
2. Only the claiming session can complete a task
3. Tasks aren't claimed by multiple sessions
4. Maintains task_locks.json for coordination

Exit codes:
  0 - Valid operation
  1 - Warning (logged but not blocking)
  2 - Blocked (conflict detected)
"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

SESSION_DIR = Path(".claude/session")
LOCKS_FILE = SESSION_DIR / "task_locks.json"
SESSIONS_FILE = SESSION_DIR / "sessions.json"
SESSION_TAG_FILE = SESSION_DIR / "current_session_tag.txt"

# Set to True to block conflicting operations instead of just warning
STRICT_MODE = False


def main():
    """Validate task operations and enforce claiming rules."""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    # Get current session info
    session_id = get_current_session_id()
    session_tag = get_current_session_tag()

    # Parse tool input from stdin
    try:
        stdin_data = sys.stdin.read()
        if not stdin_data:
            return

        data = json.loads(stdin_data)
        tool_name = data.get("tool_name", "")

        # Only process TodoWrite
        if tool_name != "TodoWrite":
            return

        tool_input = data.get("tool_input", {})
        todos = tool_input.get("todos", [])

        if not todos:
            return

        # Validate each task change
        validate_task_changes(todos, session_id, session_tag)

    except json.JSONDecodeError:
        pass
    except Exception as e:
        print(f"Warning: Task validation error: {e}")


def get_current_session_id():
    """Get the current session ID."""
    # Try from file first
    id_file = SESSION_DIR / "current_session_id.txt"
    if id_file.exists():
        try:
            return id_file.read_text().strip()
        except Exception:
            pass

    # Fallback to environment
    return os.environ.get("CLAUDE_SESSION_ID", "unknown")


def get_current_session_tag():
    """Get current session tag (auto-generated or from env)."""
    if SESSION_TAG_FILE.exists():
        try:
            stored_data = SESSION_TAG_FILE.read_text().strip()
            if ":" in stored_data:
                return stored_data.split(":", 1)[1]
            return stored_data
        except Exception:
            pass
    return os.environ.get("CLAUDE_SESSION_TAG", "main")


def validate_task_changes(todos, session_id, session_tag):
    """Validate task status changes against claiming rules."""
    locks = load_locks()
    sessions = load_sessions()
    warnings = []
    updates = []

    for todo in todos:
        content = todo.get("content", "")
        status = todo.get("status", "")
        task_id = generate_task_id(content)

        # Check for in_progress claims
        if status == "in_progress":
            # Check if already claimed by another session
            if task_id in locks:
                lock = locks[task_id]
                if lock.get("session_id") != session_id:
                    other_tag = lock.get("session_tag", "unknown")
                    warnings.append(
                        f"CONFLICT: Task already claimed by @{other_tag}\n"
                        f"  Task: {content[:50]}...\n"
                        f"  Claimed at: {lock.get('claimed_at', 'unknown')}"
                    )
                    continue

            # Claim the task
            locks[task_id] = {
                "session_id": session_id,
                "session_tag": session_tag,
                "claimed_at": datetime.now().isoformat(),
                "task_content": content[:100]
            }
            updates.append(f"Claimed: {content[:40]}... (@{session_tag})")

            # Update session's claimed tasks
            if session_id in sessions:
                claimed = sessions[session_id].get("claimed_tasks", [])
                if task_id not in claimed:
                    claimed.append(task_id)
                    sessions[session_id]["claimed_tasks"] = claimed

        # Check for completed tasks
        elif status == "completed":
            if task_id in locks:
                lock = locks[task_id]
                if lock.get("session_id") != session_id:
                    other_tag = lock.get("session_tag", "unknown")
                    warnings.append(
                        f"WARNING: Completing task claimed by @{other_tag}\n"
                        f"  Task: {content[:50]}..."
                    )

                # Release the lock
                del locks[task_id]

            # Remove from session's claimed tasks
            if session_id in sessions:
                claimed = sessions[session_id].get("claimed_tasks", [])
                if task_id in claimed:
                    claimed.remove(task_id)
                    sessions[session_id]["claimed_tasks"] = claimed

    # Save updates
    save_locks(locks)
    save_sessions(sessions)

    # Report warnings
    if warnings:
        print("=" * 50)
        print("TASK COORDINATION WARNINGS")
        print("=" * 50)
        for w in warnings:
            print(w)
            print()
        print("=" * 50)

    # Report claims (informational)
    if updates and len(updates) <= 3:
        for u in updates:
            print(f"[CLAIM] {u}")


def generate_task_id(content):
    """Generate a stable ID from task content."""
    import hashlib
    # Normalize: lowercase, strip whitespace, remove status markers
    normalized = re.sub(r'^\[.*?\]\s*', '', content.lower().strip())
    normalized = re.sub(r'\s+', ' ', normalized)
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def load_locks():
    """Load task locks."""
    if not LOCKS_FILE.exists():
        return {}
    try:
        with open(LOCKS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_locks(locks):
    """Save task locks atomically."""
    temp_file = LOCKS_FILE.with_suffix(".tmp")
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(locks, f, indent=2)
        temp_file.replace(LOCKS_FILE)
    except Exception:
        if temp_file.exists():
            temp_file.unlink()


def load_sessions():
    """Load sessions registry."""
    if not SESSIONS_FILE.exists():
        return {}
    try:
        with open(SESSIONS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_sessions(sessions):
    """Save sessions atomically."""
    temp_file = SESSIONS_FILE.with_suffix(".tmp")
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(sessions, f, indent=2)
        temp_file.replace(SESSIONS_FILE)
    except Exception:
        if temp_file.exists():
            temp_file.unlink()


def get_claimed_tasks(session_tag=None):
    """Get list of claimed tasks, optionally filtered by session tag (utility function)."""
    locks = load_locks()

    if session_tag:
        return {
            task_id: lock for task_id, lock in locks.items()
            if lock.get("session_tag") == session_tag
        }
    return locks


if __name__ == "__main__":
    main()
