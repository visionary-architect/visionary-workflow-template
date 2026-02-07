#!/usr/bin/env python3
"""
PostToolUse validator: run type checking on Python files after Write/Edit.

Tries `ty check` first, falls back to `mypy` if ty is not available.

Stdin format (PostToolUse provides):
  {"tool_name": "Write", "tool_input": {"file_path": "/path/to/file.py"}, ...}

Stdout on block:
  {"decision": "block", "reason": "Type check failed:\n<output>"}

Stdout on pass:
  {}
"""
import json
import subprocess
import sys
from pathlib import Path

# Shared utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.stdin_parser import parse_hook_input, get_file_path


def run_type_check(file_path: str) -> tuple[int, str]:
    """
    Run type checker. Returns (return_code, output).
    Tries ty first, then mypy.
    """
    # Try ty first
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ty", "check", file_path],
            capture_output=True, text=True, timeout=120,
        )
        # If ty is not installed, stderr contains "No module named"
        if result.returncode != 0 and "No module named" in result.stderr:
            pass  # Fall through to mypy
        else:
            return result.returncode, result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fall back to mypy
    try:
        result = subprocess.run(
            [sys.executable, "-m", "mypy", file_path, "--no-error-summary"],
            capture_output=True, text=True, timeout=120,
        )
        # If mypy is not installed, pass silently
        if result.returncode != 0 and "No module named" in result.stderr:
            return 0, ""
        return result.returncode, result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Neither available — pass silently
    return 0, ""


def main():
    input_data = parse_hook_input()
    file_path = get_file_path(input_data)

    # Skip non-Python files
    if not file_path or not file_path.endswith(".py"):
        print("{}")
        return

    # Skip if file doesn't exist (deleted)
    if not Path(file_path).exists():
        print("{}")
        return

    returncode, output = run_type_check(file_path)

    if returncode == 0:
        print("{}")
    else:
        output_text = output[:500]
        result = {
            "decision": "block",
            "reason": f"Type check failed:\n{output_text}",
        }
        print(json.dumps(result))


if __name__ == "__main__":
    main()
