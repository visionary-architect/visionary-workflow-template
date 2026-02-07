#!/usr/bin/env python3
"""
v1 Basic Status Line — Minimal ANSI-colored status display.

Output: project-name | branch | Model
"""
import json
import os
import sys


# ANSI colors
CYAN = "\033[36m"
GREEN = "\033[32m"
MAGENTA = "\033[35m"
RESET = "\033[0m"


def main():
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        data = {}

    project_dir = (data.get("workspace") or {}).get("project_dir", os.getcwd())
    project = os.path.basename(project_dir)
    model = (data.get("model") or {}).get("display_name", "Unknown")

    # Get branch from git with 2-second timeout
    branch = ""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=2,
            cwd=project_dir,
        )
        branch = result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        pass

    parts = [f"{CYAN}{project}{RESET}"]
    if branch:
        parts.append(f"{GREEN}{branch}{RESET}")
    parts.append(f"{MAGENTA}{model}{RESET}")

    print(" | ".join(parts))


if __name__ == "__main__":
    main()
