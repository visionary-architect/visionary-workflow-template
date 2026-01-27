#!/usr/bin/env python3
"""
Track test results from pytest runs.

This hook runs asynchronously after Bash commands to detect and track
test results. It parses pytest output patterns and saves state for
/resume-work to surface.

Output: .claude/session/test_state.json
"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

SESSION_DIR = Path(".claude/session")
STATE_FILE = SESSION_DIR / "test_state.json"
PYTEST_CACHE = Path(".pytest_cache")


def main():
    """Track test results if a test command was run."""
    # Get the command that was executed (passed via environment or stdin)
    command = os.environ.get("CLAUDE_BASH_COMMAND", "")
    exit_code = os.environ.get("CLAUDE_BASH_EXIT_CODE", "")

    # Check if this was a test-related command
    if not is_test_command(command):
        return

    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    # Try to gather test state from various sources
    state = {
        "last_run": datetime.now().isoformat(),
        "command": command[:200],  # Truncate long commands
        "exit_code": int(exit_code) if exit_code.isdigit() else None,
        "status": "unknown",
        "summary": None,
        "failed_tests": [],
        "passed_count": 0,
        "failed_count": 0,
        "error_count": 0,
        "skipped_count": 0,
    }

    # Try to parse pytest cache for last test run info
    cache_info = parse_pytest_cache()
    if cache_info:
        state.update(cache_info)

    # Determine overall status from exit code
    if state["exit_code"] is not None:
        if state["exit_code"] == 0:
            state["status"] = "passed"
        elif state["exit_code"] == 1:
            state["status"] = "failed"
        elif state["exit_code"] == 2:
            state["status"] = "error"  # Interrupted or config error
        elif state["exit_code"] == 5:
            state["status"] = "no_tests"  # No tests collected

    # Generate summary
    state["summary"] = generate_summary(state)

    # Atomic write
    temp_file = SESSION_DIR / "test_state.tmp"
    try:
        with open(temp_file, "w") as f:
            json.dump(state, f, indent=2)
        temp_file.replace(STATE_FILE)
        print(f"Test state tracked: {state['status']}")
    except Exception as e:
        print(f"Warning: Failed to save test state: {e}")
        if temp_file.exists():
            temp_file.unlink()


def is_test_command(command: str) -> bool:
    """Check if command is test-related."""
    test_patterns = [
        r"\bpytest\b",
        r"\bpy\.test\b",
        r"python\s+.*-m\s+pytest",
        r"uv\s+run\s+pytest",
        r"npm\s+run\s+test",
        r"npm\s+test\b",
        r"cargo\s+test\b",
        r"go\s+test\b",
        r"jest\b",
        r"vitest\b",
        r"mocha\b",
    ]
    command_lower = command.lower()
    return any(re.search(pattern, command_lower) for pattern in test_patterns)


def parse_pytest_cache():
    """Parse pytest cache directory for test run info."""
    if not PYTEST_CACHE.exists():
        return None

    info = {}

    # Try to read lastfailed file
    lastfailed = PYTEST_CACHE / "v" / "cache" / "lastfailed"
    if lastfailed.exists():
        try:
            content = lastfailed.read_text()
            # lastfailed is a JSON dict of failed test node IDs
            failed_dict = json.loads(content)
            info["failed_tests"] = list(failed_dict.keys())[:20]  # Limit to 20
            info["failed_count"] = len(failed_dict)
        except Exception:
            pass

    # Try to read stepwise file (shows where test run stopped)
    stepwise = PYTEST_CACHE / "v" / "cache" / "stepwise"
    if stepwise.exists():
        try:
            content = stepwise.read_text()
            stepwise_data = json.loads(content)
            if stepwise_data:
                info["stopped_at"] = str(stepwise_data)[:100]
        except Exception:
            pass

    return info if info else None


def generate_summary(state: dict) -> str:
    """Generate human-readable summary."""
    parts = []

    if state["status"] == "passed":
        parts.append("All tests passed")
    elif state["status"] == "failed":
        parts.append(f"{state['failed_count']} test(s) failed")
    elif state["status"] == "error":
        parts.append("Test run encountered an error")
    elif state["status"] == "no_tests":
        parts.append("No tests were collected")
    else:
        parts.append("Test status unknown")

    counts = []
    if state.get("passed_count"):
        counts.append(f"{state['passed_count']} passed")
    if state.get("failed_count"):
        counts.append(f"{state['failed_count']} failed")
    if state.get("skipped_count"):
        counts.append(f"{state['skipped_count']} skipped")
    if state.get("error_count"):
        counts.append(f"{state['error_count']} errors")

    if counts:
        parts.append(f"({', '.join(counts)})")

    return " ".join(parts)


if __name__ == "__main__":
    main()
