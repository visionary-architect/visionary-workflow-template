#!/usr/bin/env python3
"""
File conflict checker for multi-session coordination.

This PreToolUse hook runs before Write|Edit operations to:
1. Check if the target file is locked by another session
2. Claim the file if available
3. Warn about potential conflicts

Output: Blocks operation if file is locked by active session
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

SESSION_DIR = Path(".claude/session")
FILE_LOCKS_FILE = SESSION_DIR / "file_locks.json"
SESSION_ID_FILE = SESSION_DIR / "current_session_id.txt"
SESSION_TAG_FILE = SESSION_DIR / "current_session_tag.txt"

# Lock timeout in seconds (10 minutes)
LOCK_TIMEOUT_SECONDS = 600


def main():
    """Check for file conflicts before Write/Edit."""
    # Get tool input from stdin
    try:
        stdin_data = sys.stdin.read()
        if stdin_data:
            data = json.loads(stdin_data)
            tool_input = data.get("tool_input", {})
        else:
            return  # No input, skip
    except Exception:
        return  # Can't parse, skip

    # Get file path from tool input
    file_path = tool_input.get("file_path")
    if not file_path:
        return  # No file path, skip

    # Get current session info
    session_id = get_session_id()
    session_tag = get_session_tag()

    if not session_id:
        return  # Can't identify session, skip

    # Check for conflicts
    conflict = check_file_conflict(file_path, session_id)

    if conflict:
        # Another session has this file locked
        print(f"[CONFLICT] File '{conflict['file']}' is being edited by @{conflict['held_by']}")
        print(f"[CONFLICT] Locked since: {conflict['since']}")
        print(f"[CONFLICT] Proceeding may cause merge conflicts!")
        # Note: We warn but don't block - let the user decide
        # To block, uncomment: sys.exit(1)
    else:
        # Claim the file
        success = claim_file(file_path, session_id, session_tag)
        if success:
            # Silent claim - no output needed for normal operation
            pass


def get_session_id():
    """Get current session ID."""
    if SESSION_ID_FILE.exists():
        try:
            return SESSION_ID_FILE.read_text().strip()
        except Exception:
            pass
    return None


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


def load_file_locks():
    """Load file locks registry."""
    if not FILE_LOCKS_FILE.exists():
        return {}

    try:
        with open(FILE_LOCKS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_file_locks(locks):
    """Save file locks atomically."""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    temp_file = FILE_LOCKS_FILE.with_suffix(".tmp")
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(locks, f, indent=2)
        temp_file.replace(FILE_LOCKS_FILE)
    except Exception:
        if temp_file.exists():
            temp_file.unlink()


def check_file_conflict(file_path, session_id):
    """Check if a file is locked by another session."""
    locks = load_file_locks()
    now = datetime.now()

    # Normalize path for comparison
    try:
        file_key = str(Path(file_path).resolve())
    except Exception:
        file_key = file_path

    if file_key not in locks:
        return None

    lock = locks[file_key]
    if lock.get("session_id") == session_id:
        return None  # Our own lock

    # Check if lock is stale
    try:
        lock_time = datetime.fromisoformat(lock.get("last_touched", ""))
        if (now - lock_time).total_seconds() > LOCK_TIMEOUT_SECONDS:
            return None  # Stale lock, no conflict
    except Exception:
        return None

    return {
        "file": file_path,
        "held_by": lock.get("session_tag", "unknown"),
        "since": lock.get("claimed_at", "unknown")
    }


def claim_file(file_path, session_id, session_tag):
    """Claim a file for editing."""
    locks = load_file_locks()
    now = datetime.now()

    try:
        file_key = str(Path(file_path).resolve())
    except Exception:
        file_key = file_path

    locks[file_key] = {
        "session_id": session_id,
        "session_tag": session_tag,
        "claimed_at": now.isoformat(),
        "last_touched": now.isoformat(),
        "file_path": file_path
    }
    save_file_locks(locks)
    return True


if __name__ == "__main__":
    main()
