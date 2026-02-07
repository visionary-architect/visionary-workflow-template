#!/usr/bin/env python3
"""
PostToolUse validator: run ruff lint on Python files after Write/Edit.

Stdin format (PostToolUse provides):
  {"tool_name": "Write", "tool_input": {"file_path": "/path/to/file.py"}, ...}

Stdout on block:
  {"decision": "block", "reason": "Ruff lint failed:\n<output>"}

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

    # Try running ruff
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", file_path],
            capture_output=True, text=True, timeout=120,
        )
    except FileNotFoundError:
        # Python not found — pass silently
        print("{}")
        return
    except subprocess.TimeoutExpired:
        print("{}")
        return

    # Check if ruff is not installed (returncode != 0 and "No module named" in stderr)
    if result.returncode != 0 and "No module named" in result.stderr:
        # ruff not installed — pass silently
        print("{}")
        return

    if result.returncode == 0:
        # All clean
        print("{}")
    else:
        # Lint errors found — block
        output_text = result.stdout.strip()[:500]
        output = {
            "decision": "block",
            "reason": f"Ruff lint failed:\n{output_text}",
        }
        print(json.dumps(output))


if __name__ == "__main__":
    main()
