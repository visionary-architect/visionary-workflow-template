#!/usr/bin/env python3
"""
Standardized stdin JSON parsing for all hooks.

Claude Code pipes JSON to hook scripts via stdin. This module provides
a single, fault-tolerant parser that all hooks should use.

Import via sys.path injection:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from utils.stdin_parser import parse_hook_input
"""
import json
import sys


def parse_hook_input() -> dict:
    """
    Read and parse JSON from stdin. Returns empty dict on failure.

    Claude Code provides these universal fields on ALL events:
        - session_id: str
        - transcript_path: str
        - cwd: str
        - permission_mode: str (default|plan|acceptEdits|dontAsk|bypassPermissions)
        - hook_event_name: str

    Each event adds its own fields on top of these.
    See the Hook Protocol Reference in the integration plan for per-event schemas.
    """
    try:
        data = sys.stdin.read()
        if data.strip():
            return json.loads(data)
    except (json.JSONDecodeError, EOFError, OSError):
        pass
    return {}


def get_session_id(input_data: dict) -> str:
    """Extract session_id from parsed hook input."""
    return input_data.get("session_id", "unknown")


def get_tool_name(input_data: dict) -> str:
    """Extract tool_name from parsed hook input (PreToolUse/PostToolUse events)."""
    return input_data.get("tool_name", "")


def get_tool_input(input_data: dict) -> dict:
    """Extract tool_input from parsed hook input."""
    return input_data.get("tool_input", {})


def get_file_path(input_data: dict) -> str:
    """Extract file_path from tool_input (Write/Edit events)."""
    return input_data.get("tool_input", {}).get("file_path", "")


def get_command(input_data: dict) -> str:
    """Extract command from tool_input (Bash events)."""
    return input_data.get("tool_input", {}).get("command", "")


def get_transcript_path(input_data: dict) -> str:
    """Extract transcript_path from parsed hook input."""
    return input_data.get("transcript_path", "")
