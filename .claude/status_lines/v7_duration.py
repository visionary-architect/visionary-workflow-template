#!/usr/bin/env python3
"""
v7 Duration Status Line — Session duration display.

Output: project-name | branch | 12m 34s | $0.12
"""
import json
import os
import sys


def format_cost(usd: float) -> str:
    if usd < 0.01:
        return f"${usd:.4f}"
    return f"${usd:.2f}"


def format_duration(ms: float) -> str:
    secs = int(ms / 1000)
    if secs < 60:
        return f"{secs}s"
    mins = secs // 60
    secs = secs % 60
    if mins < 60:
        return f"{mins}m {secs}s"
    hours = mins // 60
    mins = mins % 60
    return f"{hours}h {mins}m"


def main():
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        data = {}

    project_dir = (data.get("workspace") or {}).get("project_dir", os.getcwd())
    project = os.path.basename(project_dir)
    cost_data = data.get("cost") or {}
    cost = cost_data.get("total_cost_usd", 0)
    duration = cost_data.get("total_duration_ms", 0)

    branch = ""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=3,
            cwd=project_dir,
        )
        branch = result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        pass

    parts = [project]
    if branch:
        parts.append(branch)
    parts.append(format_duration(duration))
    parts.append(format_cost(cost))

    print(" | ".join(parts))


if __name__ == "__main__":
    main()
