#!/usr/bin/env python3
"""
PostToolUseFailure lifecycle hook — error tracking and repeat failure detection.

Fires on: PostToolUseFailure
Sync: YES (must be sync for additionalContext to reach Claude Code)

What it does:
1. Log error to session JSON errors array
2. Track repeat failures: if same tool fails 3+ times, inject warning context
3. Log to per-session error JSONL file
"""
import json
import sys
import time
from pathlib import Path

# Shared utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.constants import SESSION_DATA_DIR
from utils.stdin_parser import parse_hook_input, get_session_id, get_tool_name, get_transcript_path


def log_error_jsonl(
    session_id: str,
    tool_name: str,
    error: str,
    tool_use_id: str = "",
    transcript_path: str = "",
) -> None:
    """Append error to per-session JSONL error log."""
    SESSION_DATA_DIR.mkdir(parents=True, exist_ok=True)
    error_file = SESSION_DATA_DIR / f"{session_id}_errors.jsonl"
    try:
        entry = json.dumps({
            "tool": tool_name,
            "tool_use_id": tool_use_id,
            "error": error[:500],
            "session_id": session_id,
            "transcript_path": transcript_path,
            "timestamp": time.time(),
        })
        with open(error_file, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except OSError:
        pass


def update_session_errors(
    session_id: str,
    tool_name: str,
    error: str,
    tool_use_id: str = "",
    transcript_path: str = "",
) -> int:
    """
    Update session JSON errors array.

    Returns the count of failures for this tool_name in this session.
    """
    session_file = SESSION_DATA_DIR / f"{session_id}.json"
    try:
        if session_file.exists():
            data = json.loads(session_file.read_text(encoding="utf-8"))
        else:
            data = {"session_id": session_id, "errors": []}

        data.setdefault("errors", []).append({
            "tool": tool_name,
            "tool_use_id": tool_use_id,
            "error": error[:500],
            "transcript_path": transcript_path,
            "timestamp": time.time(),
        })

        # Count failures for this tool
        tool_failures = sum(
            1 for e in data["errors"] if e.get("tool") == tool_name
        )

        session_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return tool_failures
    except (json.JSONDecodeError, OSError):
        return 0


def main():
    input_data = parse_hook_input()
    session_id = get_session_id(input_data)
    tool_name = get_tool_name(input_data)
    error = input_data.get("error", "Unknown error")
    tool_use_id = input_data.get("tool_use_id", "")
    transcript_path = get_transcript_path(input_data)

    # Log to JSONL error file
    log_error_jsonl(session_id, tool_name, error, tool_use_id, transcript_path)

    # Update session JSON and get failure count
    failure_count = update_session_errors(
        session_id, tool_name, error, tool_use_id, transcript_path
    )

    # On repeat failures (3+), inject warning context
    if failure_count >= 3:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUseFailure",
                "additionalContext": (
                    f"Warning: {tool_name} has failed {failure_count} times this session. "
                    f"Consider a different approach."
                ),
            }
        }
        print(json.dumps(output))


if __name__ == "__main__":
    main()
