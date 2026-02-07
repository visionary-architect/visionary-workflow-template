#!/usr/bin/env python3
"""
PermissionRequest lifecycle hook — auto-allow read-only and safe operations.

Fires on: PermissionRequest
Sync: YES (MUST be sync — returns allow/deny decisions)

IMPORTANT: Does NOT fire in headless mode (-p flag).
Use PreToolUse for automated permission decisions in headless mode.

CLI flags:
  --auto-allow   Enable auto-allow for read-only tools and safe Bash patterns

Decision protocol (DIFFERENT from PreToolUse):
  hookSpecificOutput.decision.behavior = "allow" | "deny"
"""
import json
import sys
import time
from pathlib import Path

# Shared utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.constants import SESSION_DATA_DIR
from utils.stdin_parser import parse_hook_input, get_session_id, get_tool_name, get_tool_input


# ---------------------------------------------------------------------------
# Auto-allow rules
# ---------------------------------------------------------------------------
# Tools that are always safe (read-only)
SAFE_TOOLS = {"Read", "Glob", "Grep", "WebSearch", "WebFetch", "TodoRead"}

# Bash command prefixes that are safe to auto-allow
SAFE_BASH_PREFIXES = [
    "ls", "dir", "pwd", "cat", "type", "head", "tail", "wc",
    "git status", "git log", "git diff", "git branch", "git tag",
    "git show", "git stash list", "git remote",
    "npm list", "npm ls", "npm outdated", "npm view",
    "pip list", "pip show", "pip freeze",
    "uv run pytest", "uv run ruff", "uv run mypy",
    "python .claude/hooks/", "python3 .claude/hooks/",
    "find", "which", "where", "echo", "printf",
]


def is_safe_bash(command: str) -> bool:
    """Check if a Bash command matches safe patterns."""
    cmd = command.strip()
    for prefix in SAFE_BASH_PREFIXES:
        if cmd.startswith(prefix):
            return True
    return False


def make_allow_response() -> dict:
    """Build auto-allow JSON response."""
    return {
        "hookSpecificOutput": {
            "hookEventName": "PermissionRequest",
            "decision": {
                "behavior": "allow",
            }
        }
    }


def make_deny_response(reason: str) -> dict:
    """Build deny JSON response."""
    return {
        "hookSpecificOutput": {
            "hookEventName": "PermissionRequest",
            "decision": {
                "behavior": "deny",
                "message": reason,
                "interrupt": False,
            }
        }
    }


def log_permission(session_id: str, tool_name: str, decision: str, reason: str) -> None:
    """Log permission decision to session JSON."""
    session_file = SESSION_DATA_DIR / f"{session_id}.json"
    try:
        if session_file.exists():
            data = json.loads(session_file.read_text(encoding="utf-8"))
        else:
            data = {"session_id": session_id, "permissions": []}

        data.setdefault("permissions", []).append({
            "tool": tool_name,
            "decision": decision,
            "reason": reason,
            "timestamp": time.time(),
        })
        session_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except (json.JSONDecodeError, OSError):
        pass


def main():
    flags = set(sys.argv[1:])
    auto_allow = "--auto-allow" in flags

    input_data = parse_hook_input()
    tool_name = get_tool_name(input_data)
    tool_input = get_tool_input(input_data)
    session_id = get_session_id(input_data)

    if not auto_allow:
        # No auto-allow flag — exit silently, let user decide
        return

    # Check read-only tools
    if tool_name in SAFE_TOOLS:
        log_permission(session_id, tool_name, "allow", "read-only tool")
        print(json.dumps(make_allow_response()))
        return

    # Check safe Bash patterns
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if is_safe_bash(command):
            log_permission(session_id, f"Bash({command[:50]})", "allow", "safe pattern")
            print(json.dumps(make_allow_response()))
            return

    # All other operations: exit silently (no stdout = let user decide)
    log_permission(session_id, tool_name, "deferred", "user decision")


if __name__ == "__main__":
    main()
