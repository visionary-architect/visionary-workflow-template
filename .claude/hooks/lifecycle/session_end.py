#!/usr/bin/env python3
"""
SessionEnd lifecycle hook — session finalization, cleanup, and audit.

Fires on: SessionEnd (reason: clear/logout/prompt_input_exit/bypass_permissions_disabled/other)
Sync: NO (async — cleanup only, cannot block)

What it does:
1. Finalize session JSON with end timestamp, duration, reason
2. Write audit summary (total prompts, tools used, errors encountered)
3. Clean up stale .tmp files from session/data directories
"""
import json
import sys
import time
from pathlib import Path

# Shared utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.constants import SESSION_DATA_DIR, SESSION_STATE_DIR, PROJECT_DIR
from utils.stdin_parser import parse_hook_input, get_session_id

# Max age for .tmp files before cleanup (24 hours)
STALE_TMP_MAX_AGE = 86400


def finalize_session(input_data: dict) -> None:
    """Update session JSON with end data."""
    session_id = get_session_id(input_data)
    session_file = SESSION_DATA_DIR / f"{session_id}.json"

    if not session_file.exists():
        return

    try:
        data = json.loads(session_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return

    now = time.time()
    started = data.get("started_at", now)

    data["ended_at"] = now
    data["duration_seconds"] = round(now - started, 1)
    data["end_reason"] = input_data.get("reason", "unknown")

    # Compute audit summary
    data["audit_summary"] = {
        "total_prompts": len(data.get("prompts", [])),
        "total_notifications": len(data.get("notifications", [])),
        "total_errors": len(data.get("errors", [])),
        "total_subagents": len(data.get("subagents", [])),
        "total_permissions": len(data.get("permissions", [])),
        "resumes": data.get("resumes", 0),
    }

    try:
        session_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except OSError:
        pass


def cleanup_tmp_files() -> int:
    """
    Remove stale .tmp files from session and data directories.

    Cleans up:
    - .claude/session/*.tmp
    - .claude/data/sessions/*.tmp
    - .claude/data/tts_queue/*.tmp

    Only removes files older than STALE_TMP_MAX_AGE seconds.
    Returns count of files removed.
    """
    cleaned = 0
    now = time.time()

    search_dirs = [
        SESSION_STATE_DIR,
        SESSION_DATA_DIR,
        PROJECT_DIR / ".claude" / "data" / "tts_queue",
    ]

    for search_dir in search_dirs:
        if not search_dir.is_dir():
            continue
        try:
            for tmp_file in search_dir.glob("*.tmp"):
                try:
                    age = now - tmp_file.stat().st_mtime
                    if age > STALE_TMP_MAX_AGE:
                        tmp_file.unlink()
                        cleaned += 1
                except OSError:
                    pass
        except OSError:
            pass

    return cleaned


def main():
    input_data = parse_hook_input()
    finalize_session(input_data)
    cleanup_tmp_files()


if __name__ == "__main__":
    main()
