#!/usr/bin/env python3
"""
Session coordinator for multi-session task execution.

This PreToolUse hook manages:
1. Session registration and heartbeats
2. Active session registry
3. Conflict detection when multiple sessions target same tasks
4. Stale session cleanup (>30 min no activity)

Session data stored in: .claude/session/sessions.json
"""
import json
import os
import sys
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.file_lock import locked_json_rw, locked_multi_json_rw

SESSION_DIR = Path(".claude/session")
SESSIONS_FILE = SESSION_DIR / "sessions.json"
LOCKS_FILE = SESSION_DIR / "task_locks.json"
FILE_LOCKS_FILE = SESSION_DIR / "file_locks.json"
SESSION_TAG_FILE = SESSION_DIR / "current_session_tag.txt"

# Stale threshold in minutes
STALE_THRESHOLD_MINUTES = 30

# Heartbeat interval - session is considered active if updated within this time
HEARTBEAT_INTERVAL_SECONDS = 60


def main():
    """Register session heartbeat and check for conflicts."""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    # Get or generate session ID
    session_id = get_session_id()

    # Get or generate unique session tag
    session_tag = get_or_generate_session_tag(session_id)

    # Update session registry
    register_session(session_id, session_tag)

    # Clean up stale sessions
    cleanup_stale_sessions()

    # Check for potential conflicts (informational)
    check_conflicts(session_id)


def get_session_id():
    """Get or generate a unique session ID."""
    # Try to get from environment (set by wrapper)
    session_id = os.environ.get("CLAUDE_SESSION_ID")

    if session_id:
        return session_id

    # Generate based on process info and timestamp
    # This creates a stable ID for the duration of a session
    pid = os.getpid()
    ppid = os.getppid()

    # Check for existing session ID file (persists across tool calls)
    id_file = SESSION_DIR / "current_session_id.txt"

    if id_file.exists():
        try:
            stored_id = id_file.read_text().strip()
            # Validate it's still our session (check timestamp)
            sessions = load_sessions()
            if stored_id in sessions:
                session = sessions[stored_id]
                last_seen = datetime.fromisoformat(session.get("last_seen", ""))
                # If seen within last 5 minutes, same session
                if (datetime.now() - last_seen).total_seconds() < 300:
                    return stored_id
        except Exception:
            pass

    # Generate new session ID
    timestamp = datetime.now().isoformat()
    raw = f"{pid}-{ppid}-{timestamp}"
    session_id = hashlib.sha256(raw.encode()).hexdigest()[:12]

    # Persist for this session
    try:
        id_file.write_text(session_id)
    except Exception:
        pass

    return session_id


def get_or_generate_session_tag(session_id):
    """Get existing session tag or generate a unique one."""
    env_tag = os.environ.get("CLAUDE_SESSION_TAG", "main")

    # If user explicitly set a non-default tag, use it
    if env_tag != "main":
        return env_tag

    # Check if we already have a tag for this session
    if SESSION_TAG_FILE.exists():
        try:
            stored_data = SESSION_TAG_FILE.read_text().strip()
            # Format: session_id:tag
            if ":" in stored_data:
                stored_id, stored_tag = stored_data.split(":", 1)
                if stored_id == session_id:
                    return stored_tag
        except Exception:
            pass

    # Generate a unique worker tag based on active sessions
    sessions = load_sessions()

    # Find existing worker numbers
    used_numbers = set()
    for sid, session in sessions.items():
        tag = session.get("tag", "")
        if tag.startswith("worker-"):
            try:
                num = int(tag.split("-")[1])
                used_numbers.add(num)
            except (ValueError, IndexError):
                pass

    # Find the lowest available worker number
    worker_num = 1
    while worker_num in used_numbers:
        worker_num += 1

    new_tag = f"worker-{worker_num}"

    # Persist for this session
    try:
        SESSION_TAG_FILE.write_text(f"{session_id}:{new_tag}")
    except Exception:
        pass

    print(f"[MULTI-SESSION] Auto-assigned tag: @{new_tag}")
    return new_tag


def load_sessions():
    """Load active sessions registry."""
    if not SESSIONS_FILE.exists():
        return {}

    try:
        with open(SESSIONS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def register_session(session_id, session_tag):
    """Register or update session heartbeat with file locking."""
    with locked_json_rw(SESSIONS_FILE, default={}) as (sessions, save):
        now = datetime.now().isoformat()

        if session_id not in sessions:
            # New session
            sessions[session_id] = {
                "tag": session_tag,
                "started": now,
                "last_seen": now,
                "tool_count": 1,
                "claimed_tasks": []
            }
            print(f"Session registered: {session_tag} ({session_id[:8]})")
        else:
            # Update heartbeat
            sessions[session_id]["last_seen"] = now
            sessions[session_id]["tool_count"] = sessions[session_id].get("tool_count", 0) + 1

        save(sessions)


def cleanup_stale_sessions():
    """Remove sessions with no activity for >30 minutes. Uses multi-file lock."""
    with locked_multi_json_rw(
        (SESSIONS_FILE, {}), (LOCKS_FILE, {})
    ) as entries:
        sessions, save_sessions_fn = entries[0]
        locks, save_locks_fn = entries[1]

        now = datetime.now()
        stale_threshold = timedelta(minutes=STALE_THRESHOLD_MINUTES)

        stale_ids = []
        for session_id, session in sessions.items():
            try:
                last_seen = datetime.fromisoformat(session.get("last_seen", ""))
                if now - last_seen > stale_threshold:
                    stale_ids.append(session_id)
            except Exception:
                pass

        if not stale_ids:
            return

        locks_changed = False
        for sid in stale_ids:
            tag = sessions[sid].get("tag", "unknown")
            claimed = sessions[sid].get("claimed_tasks", [])

            # Release any claimed tasks (inline — both files are locked)
            if claimed:
                for task_id in claimed:
                    if task_id in locks:
                        if locks[task_id].get("session_id") == sid:
                            del locks[task_id]
                            locks_changed = True
                print(f"Released {len(claimed)} claims from stale session @{tag}")

            del sessions[sid]

        save_sessions_fn(sessions)
        if locks_changed:
            save_locks_fn(locks)
        print(f"Cleaned up {len(stale_ids)} stale session(s)")


def release_task_claims(session_id, task_ids):
    """Release task claims held by a session with file locking."""
    with locked_json_rw(LOCKS_FILE, default={}) as (locks, save):
        changed = False
        for task_id in task_ids:
            if task_id in locks:
                if locks[task_id].get("session_id") == session_id:
                    del locks[task_id]
                    changed = True
        if changed:
            save(locks)


def load_locks():
    """Load task locks (read-only, no locking needed)."""
    if not LOCKS_FILE.exists():
        return {}

    try:
        with open(LOCKS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def check_conflicts(current_session_id):
    """Check for potential conflicts with other active sessions."""
    sessions = load_sessions()

    # Filter to active sessions (seen in last 5 minutes)
    now = datetime.now()
    active_threshold = timedelta(minutes=5)

    active_sessions = []
    for session_id, session in sessions.items():
        if session_id == current_session_id:
            continue
        try:
            last_seen = datetime.fromisoformat(session.get("last_seen", ""))
            if now - last_seen < active_threshold:
                active_sessions.append(session)
        except Exception:
            pass

    if active_sessions:
        tags = [s.get("tag", "unknown") for s in active_sessions]
        print(f"[INFO] {len(active_sessions)} other active session(s): {', '.join('@' + t for t in tags)}")


def get_active_sessions():
    """Get list of currently active sessions (utility function)."""
    sessions = load_sessions()
    now = datetime.now()
    active_threshold = timedelta(minutes=5)

    active = []
    for session_id, session in sessions.items():
        try:
            last_seen = datetime.fromisoformat(session.get("last_seen", ""))
            if now - last_seen < active_threshold:
                active.append({
                    "id": session_id,
                    "tag": session.get("tag"),
                    "last_seen": session.get("last_seen"),
                    "claimed_tasks": session.get("claimed_tasks", [])
                })
        except Exception:
            pass

    return active


# ============ File Lock Functions ============

def load_file_locks():
    """Load file locks registry."""
    if not FILE_LOCKS_FILE.exists():
        return {}

    try:
        with open(FILE_LOCKS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def claim_file(file_path, session_id, session_tag):
    """Claim a file for editing with file locking. Returns (success, conflict_info)."""
    now = datetime.now()
    file_key = str(Path(file_path).resolve())

    with locked_json_rw(FILE_LOCKS_FILE, default={}) as (locks, save):
        if file_key in locks:
            lock = locks[file_key]
            lock_session = lock.get("session_id")

            # Check if it's our own lock
            if lock_session == session_id:
                # Update timestamp
                locks[file_key]["last_touched"] = now.isoformat()
                save(locks)
                return True, None

            # Check if lock is stale (>10 minutes)
            try:
                lock_time = datetime.fromisoformat(lock.get("last_touched", ""))
                if (now - lock_time).total_seconds() > 600:
                    # Stale lock, we can take over
                    pass
                else:
                    # Active conflict
                    return False, {
                        "file": file_path,
                        "held_by": lock.get("session_tag", "unknown"),
                        "since": lock.get("claimed_at", "unknown")
                    }
            except Exception:
                pass

        # Claim the file
        locks[file_key] = {
            "session_id": session_id,
            "session_tag": session_tag,
            "claimed_at": now.isoformat(),
            "last_touched": now.isoformat(),
            "file_path": file_path
        }
        save(locks)
    return True, None


def release_file(file_path, session_id):
    """Release a file lock with file locking."""
    file_key = str(Path(file_path).resolve())

    with locked_json_rw(FILE_LOCKS_FILE, default={}) as (locks, save):
        if file_key in locks:
            if locks[file_key].get("session_id") == session_id:
                del locks[file_key]
                save(locks)
                return True
    return False


def release_all_file_locks(session_id):
    """Release all file locks held by a session with file locking."""
    with locked_json_rw(FILE_LOCKS_FILE, default={}) as (locks, save):
        released = []

        for file_key in list(locks.keys()):
            if locks[file_key].get("session_id") == session_id:
                released.append(locks[file_key].get("file_path", file_key))
                del locks[file_key]

        if released:
            save(locks)

    return released


def get_file_locks_for_session(session_id):
    """Get all files locked by a session."""
    locks = load_file_locks()
    return [
        lock.get("file_path", key)
        for key, lock in locks.items()
        if lock.get("session_id") == session_id
    ]


def check_file_conflict(file_path, session_id):
    """Check if a file is locked by another session."""
    locks = load_file_locks()
    file_key = str(Path(file_path).resolve())
    now = datetime.now()

    if file_key not in locks:
        return None

    lock = locks[file_key]
    if lock.get("session_id") == session_id:
        return None

    # Check if lock is stale
    try:
        lock_time = datetime.fromisoformat(lock.get("last_touched", ""))
        if (now - lock_time).total_seconds() > 600:
            return None  # Stale, no conflict
    except Exception:
        return None

    return {
        "file": file_path,
        "held_by": lock.get("session_tag", "unknown"),
        "since": lock.get("claimed_at", "unknown")
    }


if __name__ == "__main__":
    main()
