#!/usr/bin/env python3
"""
Session cleanup on Stop.

This Stop hook:
1. Releases all task claims held by this session
2. Removes session from active registry
3. Logs session summary

Runs after auto_snapshot.py but before session_maintenance.py.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.file_lock import locked_json_rw

SESSION_DIR = Path(".claude/session")
SESSIONS_FILE = SESSION_DIR / "sessions.json"
LOCKS_FILE = SESSION_DIR / "task_locks.json"
FILE_LOCKS_FILE = SESSION_DIR / "file_locks.json"
SESSION_ID_FILE = SESSION_DIR / "current_session_id.txt"
SESSION_TAG_FILE = SESSION_DIR / "current_session_tag.txt"


def main():
    """Clean up session on stop."""
    session_id = get_current_session_id()
    session_tag = get_session_tag()

    if not session_id:
        return

    # Get session info before cleanup
    sessions = load_sessions()
    session_info = sessions.get(session_id, {})

    # Release all task claims
    released_task_count = release_all_claims(session_id)

    # Release all file locks
    released_file_count = release_all_file_locks(session_id)

    # Remove from session registry
    remove_session(session_id)

    # Clear session files
    clear_session_files()

    # Log summary
    log_session_summary(session_id, session_tag, session_info, released_task_count, released_file_count)


def get_session_tag():
    """Get current session tag."""
    if SESSION_TAG_FILE.exists():
        try:
            stored_data = SESSION_TAG_FILE.read_text().strip()
            if ":" in stored_data:
                return stored_data.split(":", 1)[1]
            return stored_data
        except Exception:
            pass
    return os.environ.get("CLAUDE_SESSION_TAG", "main")


def get_current_session_id():
    """Get the current session ID."""
    if SESSION_ID_FILE.exists():
        try:
            return SESSION_ID_FILE.read_text().strip()
        except Exception:
            pass
    return os.environ.get("CLAUDE_SESSION_ID")


def load_sessions():
    """Load sessions registry."""
    if not SESSIONS_FILE.exists():
        return {}
    try:
        with open(SESSIONS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def release_all_claims(session_id):
    """Release all task claims held by this session with file locking."""
    with locked_json_rw(LOCKS_FILE, default={}) as (locks, save):
        released = []
        for task_id, lock in list(locks.items()):
            if lock.get("session_id") == session_id:
                released.append(lock.get("task_content", task_id)[:40])
                del locks[task_id]

        if released:
            save(locks)

    return len(released)


def release_all_file_locks(session_id):
    """Release all file locks held by this session with file locking."""
    with locked_json_rw(FILE_LOCKS_FILE, default={}) as (locks, save):
        released = []
        for file_key, lock in list(locks.items()):
            if lock.get("session_id") == session_id:
                released.append(lock.get("file_path", file_key)[:40])
                del locks[file_key]

        if released:
            save(locks)

    return len(released)


def remove_session(session_id):
    """Remove session from registry with file locking."""
    with locked_json_rw(SESSIONS_FILE, default={}) as (sessions, save):
        if session_id in sessions:
            del sessions[session_id]
            save(sessions)


def clear_session_files():
    """Clear session ID and tag files."""
    try:
        if SESSION_ID_FILE.exists():
            SESSION_ID_FILE.unlink()
    except Exception:
        pass

    try:
        if SESSION_TAG_FILE.exists():
            SESSION_TAG_FILE.unlink()
    except Exception:
        pass


def log_session_summary(session_id, session_tag, session_info, released_task_count, released_file_count):
    """Log session summary."""
    started = session_info.get("started", "unknown")
    tool_count = session_info.get("tool_count", 0)

    # Calculate duration
    duration = "unknown"
    if started != "unknown":
        try:
            start_dt = datetime.fromisoformat(started)
            duration_sec = (datetime.now() - start_dt).total_seconds()
            if duration_sec < 60:
                duration = f"{int(duration_sec)}s"
            elif duration_sec < 3600:
                duration = f"{int(duration_sec / 60)}m"
            else:
                duration = f"{duration_sec / 3600:.1f}h"
        except Exception:
            pass

    print(f"Session ended: @{session_tag} ({session_id[:8]})")
    print(f"  Duration: {duration}")
    print(f"  Tool calls: {tool_count}")
    if released_task_count:
        print(f"  Task claims released: {released_task_count}")
    if released_file_count:
        print(f"  File locks released: {released_file_count}")


if __name__ == "__main__":
    main()
