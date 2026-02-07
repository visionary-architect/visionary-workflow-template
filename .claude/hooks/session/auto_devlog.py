#!/usr/bin/env python3
"""
Auto-capture minimal session entry to DEVLOG.md on Stop.

When a Claude session ends without /pause-work, this hook captures:
- Date and approximate duration
- Files modified during session
- Commits made during session
- Basic session marker for continuity

This ensures no session goes completely unrecorded, even on unexpected stops.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SESSION_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")) / ".claude" / "session"
SNAPSHOT_FILE = SESSION_DIR / "last_snapshot.json"
LOCKS_FILE = SESSION_DIR / "task_locks.json"
SESSION_ID_FILE = SESSION_DIR / "current_session_id.txt"
DEVLOG_FILE = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")) / "DEVLOG.md"
MARKER_FILE = SESSION_DIR / "session_logged.marker"


def main():
    """Capture minimal session entry if not already logged."""
    # Check if /pause-work already ran this session (marker exists and is recent)
    if was_session_logged():
        return

    # Get session data from snapshot
    session_data = get_session_data()

    if not session_data.get("has_activity"):
        # No meaningful activity, skip logging
        mark_session_logged()
        return

    # Append minimal entry to DEVLOG.md
    append_devlog_entry(session_data)

    # Mark session as logged
    mark_session_logged()

    print(f"Auto-logged session to DEVLOG.md")


def was_session_logged():
    """Check if this session was already logged via /pause-work."""
    if not MARKER_FILE.exists():
        return False

    try:
        # Use session ID for marker comparison (not date).
        # Previous date-based check failed when two sessions ran on the same day.
        current_session_id = ""
        if SESSION_ID_FILE.exists():
            current_session_id = SESSION_ID_FILE.read_text().strip()

        if not current_session_id:
            # Fallback: date-based check if no session ID available
            marker_date = datetime.fromtimestamp(MARKER_FILE.stat().st_mtime).date()
            return marker_date == datetime.now().date()

        # Check if marker contains current session ID
        marker_content = MARKER_FILE.read_text(encoding="utf-8").strip()
        return marker_content == current_session_id
    except Exception:
        return False


def mark_session_logged():
    """Mark this session as logged to prevent duplicate entries."""
    try:
        SESSION_DIR.mkdir(parents=True, exist_ok=True)
        # Write session ID to marker instead of just touching the file.
        # This allows per-session detection instead of per-day.
        session_id = ""
        if SESSION_ID_FILE.exists():
            session_id = SESSION_ID_FILE.read_text().strip()
        MARKER_FILE.write_text(session_id, encoding="utf-8")
    except Exception:
        pass


def get_session_data():
    """Gather session data from various sources."""
    data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "modified_files": [],
        "commits_today": [],
        "claimed_tasks": [],
        "has_activity": False
    }

    # Get modified files from snapshot or git status
    try:
        if SNAPSHOT_FILE.exists():
            with open(SNAPSHOT_FILE, encoding="utf-8") as f:
                snapshot = json.load(f)
            data["modified_files"] = snapshot.get("modified_files", [])
            data["staged_files"] = snapshot.get("staged_files", [])
        else:
            # Fallback to git status
            result = subprocess.run(
                ["git", "status", "--short"],
                capture_output=True, text=True, timeout=5
            )
            if result.stdout.strip():
                data["modified_files"] = [
                    line[3:] for line in result.stdout.strip().split("\n")
                    if line.strip()
                ]
    except Exception:
        pass

    # Get today's commits
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        result = subprocess.run(
            ["git", "log", "--oneline", f"--since={today} 00:00:00", "--format=%s"],
            capture_output=True, text=True, timeout=5
        )
        if result.stdout.strip():
            data["commits_today"] = result.stdout.strip().split("\n")[:5]  # Max 5
    except Exception:
        pass

    # Get claimed tasks from this session
    data["claimed_tasks"] = get_claimed_tasks()

    # Determine if there was meaningful activity
    data["has_activity"] = bool(
        data.get("modified_files") or
        data.get("staged_files") or
        data.get("commits_today") or
        data.get("claimed_tasks")
    )

    return data


def get_claimed_tasks():
    """Get tasks claimed by this session."""
    if not LOCKS_FILE.exists():
        return []

    try:
        # Get current session ID
        session_id = None
        if SESSION_ID_FILE.exists():
            session_id = SESSION_ID_FILE.read_text().strip()

        if not session_id:
            return []

        with open(LOCKS_FILE, encoding="utf-8") as f:
            locks = json.load(f)

        claims = []
        for task_id, lock in locks.items():
            # Only include claims by this session
            if lock.get("session_id") == session_id:
                claims.append({
                    "content": lock.get("task_content", "")[:60],
                    "status": lock.get("status", "in_progress"),
                })

        return claims
    except Exception:
        return []


def append_devlog_entry(session_data):
    """Append minimal session entry to DEVLOG.md."""
    if not DEVLOG_FILE.exists():
        return

    try:
        content = DEVLOG_FILE.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return

    # Find Recent Sessions section
    match = re.search(r"(## Recent Sessions\n)", content)
    if not match:
        return

    # Build minimal entry
    date = session_data["date"]
    time_str = session_data["time"]

    entry_lines = [
        f"\n### Session: {date} (Auto-captured at {time_str})\n",
        "**Note:** This session ended without /pause-work.\n\n"
    ]

    # Add commits if any
    commits = session_data.get("commits_today", [])
    if commits:
        entry_lines.append("**Commits:**\n")
        for commit in commits[:5]:
            entry_lines.append(f"- {commit}\n")
        entry_lines.append("\n")

    # Add modified files if any uncommitted
    modified = session_data.get("modified_files", [])
    if modified:
        entry_lines.append("**Uncommitted changes:**\n")
        for f in modified[:10]:
            entry_lines.append(f"- {f}\n")
        if len(modified) > 10:
            entry_lines.append(f"- ... and {len(modified) - 10} more\n")
        entry_lines.append("\n")

    # Add claimed tasks if any
    claimed = session_data.get("claimed_tasks", [])
    if claimed:
        entry_lines.append("**Tasks in progress:**\n")
        for task in claimed[:5]:
            content = task.get("content", "Unknown task")
            entry_lines.append(f"- {content}\n")
        if len(claimed) > 5:
            entry_lines.append(f"- ... and {len(claimed) - 5} more\n")
        entry_lines.append("\n")

    entry = "".join(entry_lines)

    # Insert after "## Recent Sessions" header
    insert_pos = match.end()
    new_content = content[:insert_pos] + entry + content[insert_pos:]

    try:
        DEVLOG_FILE.write_text(new_content, encoding="utf-8")
    except Exception as e:
        print(f"Warning: Failed to update DEVLOG.md: {e}")


if __name__ == "__main__":
    main()
