#!/usr/bin/env python3
"""
Stop lifecycle hook — TTS completion announcement.

Fires on: Stop (added to existing Stop hooks array)
Sync: NO (async — TTS is fire-and-forget)

CRITICAL: Checks stop_hook_active to prevent infinite loops.
If a previous Stop hook blocked and forced continuation, this
hook MUST exit cleanly to prevent recursive stop-hook chains.

What it does:
1. Check stop_hook_active — exit immediately if True
2. Generate completion message via get_completion_message()
3. Speak via TTS queue
4. Log to session JSON
"""
import json
import sys
import time
from pathlib import Path

# Shared utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.constants import (
    SESSION_DATA_DIR, TTS_RATE, TTS_VOLUME, TTS_LOCK_TIMEOUT,
)
from utils.stdin_parser import parse_hook_input, get_session_id


def log_completion(session_id: str, message: str) -> None:
    """Log completion event to session JSON."""
    session_file = SESSION_DATA_DIR / f"{session_id}.json"
    try:
        if session_file.exists():
            data = json.loads(session_file.read_text(encoding="utf-8"))
        else:
            data = {"session_id": session_id}

        data["completion_message"] = message
        data["completed_at"] = time.time()
        session_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except (json.JSONDecodeError, OSError):
        pass


def main():
    input_data = parse_hook_input()

    # CRITICAL: Infinite loop prevention
    # If a previous Stop hook blocked and forced continuation,
    # stop_hook_active will be True. Check both top-level and hookSpecificOutput.
    hook_output = input_data.get("hookSpecificOutput", {}) or {}
    if input_data.get("stop_hook_active", False) or hook_output.get("stop_hook_active", False):
        sys.exit(0)

    session_id = get_session_id(input_data)

    # Generate completion message
    try:
        from utils.llm.anthropic_client import get_completion_message
        from utils.constants import ENGINEER_NAME
        message = get_completion_message(ENGINEER_NAME)
    except Exception:
        message = "Work complete!"

    # Speak via TTS
    try:
        from utils.tts.tts_queue import speak_with_lock
        speak_with_lock(
            text=message,
            agent_id=f"completion-{session_id[:8]}",
            timeout=TTS_LOCK_TIMEOUT,
            rate=TTS_RATE,
            volume=TTS_VOLUME,
        )
    except Exception:
        pass

    # Log to session JSON
    log_completion(session_id, message)


if __name__ == "__main__":
    main()
