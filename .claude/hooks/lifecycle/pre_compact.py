#!/usr/bin/env python3
"""
PreCompact lifecycle hook — transcript backup before context compaction.

Fires on: PreCompact (trigger: manual/auto)
Sync: NO (async — backup is fire-and-forget)

CLI flags:
  --backup   Enable transcript backup

What it does:
1. Copy transcript file to .claude/data/sessions/{session_id}_pre_compact_{trigger}_{timestamp}.jsonl
2. Log compaction event to session JSON
"""
import json
import shutil
import sys
import time
from pathlib import Path

# Shared utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.constants import SESSION_DATA_DIR
from utils.stdin_parser import parse_hook_input, get_session_id, get_transcript_path


def backup_transcript(transcript_path: str, session_id: str, trigger: str) -> str | None:
    """Copy transcript to backup location. Returns backup path or None."""
    src = Path(transcript_path)
    if not src.exists():
        return None

    SESSION_DATA_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time())
    backup_name = f"{session_id}_pre_compact_{trigger}_{timestamp}.jsonl"
    dest = SESSION_DATA_DIR / backup_name

    try:
        shutil.copy2(str(src), str(dest))
        return str(dest)
    except OSError:
        return None


def log_compaction(session_id: str, trigger: str, backup_path: str | None) -> None:
    """Log compaction event to session JSON."""
    session_file = SESSION_DATA_DIR / f"{session_id}.json"
    try:
        if session_file.exists():
            data = json.loads(session_file.read_text(encoding="utf-8"))
        else:
            data = {"session_id": session_id}

        data.setdefault("compactions", []).append({
            "trigger": trigger,
            "backup_path": backup_path,
            "timestamp": time.time(),
        })
        session_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except (json.JSONDecodeError, OSError):
        pass


def main():
    flags = set(sys.argv[1:])
    do_backup = "--backup" in flags

    input_data = parse_hook_input()
    session_id = get_session_id(input_data)
    trigger = input_data.get("trigger", "unknown")
    transcript_path = get_transcript_path(input_data)

    backup_path = None
    if do_backup and transcript_path:
        backup_path = backup_transcript(transcript_path, session_id, trigger)

    log_compaction(session_id, trigger, backup_path)


if __name__ == "__main__":
    main()
