#!/usr/bin/env python3
"""
v6 Context Window Bar Status Line — DEFAULT status line.

Output: project-name | branch | Model | [████████░░░░░░░░] 42% 115.0k left | $0.12 | abc123

Uses context_window.used_percentage from stdin JSON to draw visual bar.
Color transitions at 50% (green), 75% (yellow), 90% (red).
Shows remaining tokens in human-readable format and session ID in dim gray.
"""
import json
import os
import sys


# ANSI colors
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
DIM = "\033[2m"
RESET = "\033[0m"

BAR_WIDTH = 16
FILLED = "\u2588"  # █
EMPTY = "\u2591"   # ░


def color_for_percentage(pct: int) -> str:
    """Color based on context usage: green < 50%, yellow < 75%, red >= 90%."""
    if pct < 50:
        return GREEN
    elif pct < 75:
        return YELLOW
    return RED


def format_tokens(count: int) -> str:
    """Format token count in human-readable form: 42.5k, 1.23M."""
    if count >= 1_000_000:
        return f"{count / 1_000_000:.2f}M"
    if count >= 1000:
        return f"{count / 1000:.1f}k"
    return str(count)


def format_cost(usd: float) -> str:
    if usd < 0.01:
        return f"${usd:.4f}"
    return f"${usd:.2f}"


def load_session_extras(project_dir: str) -> dict:
    """Load extras from status_extras.json (set via /update-status-line)."""
    try:
        from pathlib import Path
        extras_file = Path(project_dir) / ".claude" / "session" / "status_extras.json"
        if extras_file.exists():
            data = json.loads(extras_file.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data:
                return data
    except Exception:
        pass
    return {}


def main():
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        data = {}

    project_dir = (data.get("workspace") or {}).get("project_dir", os.getcwd())
    project = os.path.basename(project_dir)
    model = (data.get("model") or {}).get("display_name", "Unknown")
    session_id = data.get("session_id", "")
    ctx = data.get("context_window") or {}
    used_pct = ctx.get("used_percentage", 0)
    remaining_pct = ctx.get("remaining_percentage", 100 - used_pct)
    context_size = ctx.get("context_window_size", 200000)
    cost = (data.get("cost") or {}).get("total_cost_usd", 0)

    # Calculate remaining tokens
    remaining_tokens = int(context_size * remaining_pct / 100)

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

    # Build context bar
    filled_count = int(BAR_WIDTH * used_pct / 100)
    empty_count = BAR_WIDTH - filled_count
    color = color_for_percentage(used_pct)
    bar = f"{color}[{FILLED * filled_count}{DIM}{EMPTY * empty_count}{RESET}{color}] {used_pct}% {format_tokens(remaining_tokens)} left{RESET}"

    parts = [f"{CYAN}{project}{RESET}"]
    if branch:
        parts.append(branch)
    parts.append(model)
    parts.append(bar)
    parts.append(format_cost(cost))

    # Show session extras (set via /update-status-line)
    extras = load_session_extras(project_dir)
    if extras:
        extras_str = " ".join(f"{k}:{v}" for k, v in extras.items())
        parts.append(f"{YELLOW}{extras_str}{RESET}")

    if session_id:
        parts.append(f"{DIM}{session_id[:8]}{RESET}")

    print(" | ".join(parts))


if __name__ == "__main__":
    main()
