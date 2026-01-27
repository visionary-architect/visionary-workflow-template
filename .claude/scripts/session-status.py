#!/usr/bin/env python3
"""
Show current multi-session coordination status.

Usage:
    python .claude/scripts/session-status.py

Shows:
- Active sessions and their status
- Claimed tasks per session
- File locks per session
- Potential conflicts
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

SESSION_DIR = Path(".claude/session")
SESSIONS_FILE = SESSION_DIR / "sessions.json"
LOCKS_FILE = SESSION_DIR / "task_locks.json"
FILE_LOCKS_FILE = SESSION_DIR / "file_locks.json"


def main():
    """Show session status."""
    print()
    print("=" * 70)
    print("  MULTI-SESSION COORDINATION STATUS")
    print("=" * 70)
    print()

    show_sessions()
    show_task_claims()
    show_file_locks()
    show_recommendations()


def show_sessions():
    """Show active and stale sessions."""
    sessions = load_json(SESSIONS_FILE)
    now = datetime.now()

    if not sessions:
        print("SESSIONS: None registered")
        print()
        return

    active = []
    stale = []

    for session_id, session in sessions.items():
        try:
            last_seen = datetime.fromisoformat(session.get("last_seen", ""))
            age = now - last_seen

            entry = {
                "id": session_id[:8],
                "tag": session.get("tag", "unknown"),
                "started": session.get("started", "unknown")[:10],
                "age": format_age(age),
                "tools": session.get("tool_count", 0),
                "claims": len(session.get("claimed_tasks", [])),
            }

            if age < timedelta(minutes=5):
                active.append(entry)
            elif age < timedelta(minutes=30):
                stale.append(entry)
        except Exception:
            pass

    print("SESSIONS:")
    print("-" * 70)

    if active:
        print("  ACTIVE (seen within 5 min):")
        for s in active:
            print(f"    @{s['tag']:<12} | ID: {s['id']} | {s['tools']:>4} tools | "
                  f"{s['claims']} claims | {s['age']} ago")
    else:
        print("  No active sessions")

    if stale:
        print()
        print("  STALE (will be cleaned up):")
        for s in stale:
            print(f"    @{s['tag']:<12} | ID: {s['id']} | {s['age']} since last activity")

    print()


def show_task_claims():
    """Show current task claims."""
    locks = load_json(LOCKS_FILE)

    if not locks:
        print("TASK CLAIMS: None")
        print()
        return

    # Group by session
    by_session = {}
    for task_id, lock in locks.items():
        tag = lock.get("session_tag", "unknown")
        if tag not in by_session:
            by_session[tag] = []
        by_session[tag].append({
            "content": lock.get("task_content", "")[:50],
            "claimed_at": lock.get("claimed_at", "")[:16],
        })

    print("TASK CLAIMS:")
    print("-" * 70)

    for tag, tasks in sorted(by_session.items()):
        print(f"  @{tag}:")
        for task in tasks[:5]:
            print(f"    - {task['content']}...")
        if len(tasks) > 5:
            print(f"    ... and {len(tasks) - 5} more")

    print()


def show_file_locks():
    """Show current file locks."""
    locks = load_json(FILE_LOCKS_FILE)
    now = datetime.now()

    if not locks:
        print("FILE LOCKS: None")
        print()
        return

    # Filter to active locks and group by session
    by_session = {}
    for file_key, lock in locks.items():
        try:
            last_touched = datetime.fromisoformat(lock.get("last_touched", ""))
            if (now - last_touched).total_seconds() > 600:
                continue  # Stale lock

            tag = lock.get("session_tag", "unknown")
            if tag not in by_session:
                by_session[tag] = []

            file_path = lock.get("file_path", file_key)
            # Show just filename
            filename = Path(file_path).name
            by_session[tag].append(filename)
        except Exception:
            pass

    if not by_session:
        print("FILE LOCKS: None active")
        print()
        return

    print("FILE LOCKS (active):")
    print("-" * 70)

    for tag, files in sorted(by_session.items()):
        print(f"  @{tag}:")
        for f in files[:10]:
            print(f"    - {f}")
        if len(files) > 10:
            print(f"    ... and {len(files) - 10} more")

    print()


def show_recommendations():
    """Show recommendations based on current state."""
    sessions = load_json(SESSIONS_FILE)
    locks = load_json(LOCKS_FILE)
    now = datetime.now()

    recommendations = []

    # Check for stale sessions
    stale_count = 0
    for session in sessions.values():
        try:
            last_seen = datetime.fromisoformat(session.get("last_seen", ""))
            if (now - last_seen) > timedelta(minutes=30):
                stale_count += 1
        except Exception:
            pass

    if stale_count:
        recommendations.append(
            f"Found {stale_count} stale session(s). "
            "They will be cleaned up automatically on next tool use."
        )

    # Check for unclaimed tasks (would need task list access)
    active_claims = len(locks)
    if active_claims == 0:
        recommendations.append(
            "No tasks are currently claimed. "
            "Workers can pick up any available task."
        )

    # Count active sessions
    active_count = sum(
        1 for s in sessions.values()
        if is_active(s.get("last_seen", ""))
    )

    if active_count > 1:
        recommendations.append(
            f"Multiple workers active ({active_count}). "
            "Ensure they're working on different tasks to avoid conflicts."
        )

    if recommendations:
        print("RECOMMENDATIONS:")
        print("-" * 70)
        for rec in recommendations:
            print(f"  - {rec}")
        print()


def is_active(last_seen_str):
    """Check if a session is active based on last_seen timestamp."""
    try:
        last_seen = datetime.fromisoformat(last_seen_str)
        return (datetime.now() - last_seen) < timedelta(minutes=5)
    except Exception:
        return False


def format_age(td):
    """Format timedelta as human readable."""
    seconds = int(td.total_seconds())
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m"
    else:
        return f"{seconds // 3600}h {(seconds % 3600) // 60}m"


def load_json(path):
    """Load JSON file safely."""
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


if __name__ == "__main__":
    main()
