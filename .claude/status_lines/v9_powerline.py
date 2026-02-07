#!/usr/bin/env python3
"""
v9 Powerline Status Line — Powerline-style with Unicode glyphs and ANSI colors.

Output:  main  Opus  ████░░ 42%  $0.12

Features:
- Unicode powerline separators
- Background color segments: blue (branch) → cyan (model) → dynamic (context) → magenta (cost)
- Smart path shortening: home → ~, long paths → first/.../last
- Fallback git detection via .git/HEAD if git command fails
"""
import json
import os
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows (needed for powerline/bar characters)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ANSI colors and styles
BG_BLUE = "\033[44m"
BG_CYAN = "\033[46m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_RED = "\033[41m"
BG_MAGENTA = "\033[45m"
FG_WHITE = "\033[97m"
FG_BLACK = "\033[30m"
FG_BLUE = "\033[34m"
FG_CYAN = "\033[36m"
FG_GREEN = "\033[32m"
FG_YELLOW = "\033[33m"
FG_MAGENTA = "\033[35m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Powerline separator
SEP = "\ue0b0"  #

BAR_WIDTH = 8
FILLED = "\u2588"  # █
EMPTY = "\u2591"   # ░


def bar_color_bg(pct: int) -> str:
    if pct < 50:
        return BG_GREEN
    elif pct < 75:
        return BG_YELLOW
    return BG_RED


def bar_fg_after(pct: int) -> str:
    if pct < 50:
        return FG_GREEN
    elif pct < 75:
        return FG_YELLOW
    return "\033[31m"


def format_cost(usd: float) -> str:
    if usd < 0.01:
        return f"${usd:.4f}"
    return f"${usd:.2f}"


def shorten_path(path: str) -> str:
    """Smart path shortening: home → ~, long paths → first/.../last."""
    home = os.path.expanduser("~")
    if path.startswith(home):
        path = "~" + path[len(home):]

    parts = path.replace("\\", "/").split("/")
    if len(parts) <= 3:
        return "/".join(parts)
    return f"{parts[0]}/\u2026/{parts[-1]}"


def get_git_branch(project_dir: str) -> str:
    """Get git branch via command, fallback to reading .git/HEAD directly."""
    # Try git command first
    try:
        import subprocess
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=2,
            cwd=project_dir,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass

    # Fallback: read .git/HEAD directly
    try:
        head_file = Path(project_dir) / ".git" / "HEAD"
        if head_file.exists():
            content = head_file.read_text(encoding="utf-8").strip()
            if content.startswith("ref: refs/heads/"):
                return content[len("ref: refs/heads/"):]
            # Detached HEAD — return short hash
            return content[:7]
    except Exception:
        pass

    return "?"


def main():
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        data = {}

    project_dir = (data.get("workspace") or {}).get("project_dir", os.getcwd())
    model = (data.get("model") or {}).get("display_name", "?")
    ctx = data.get("context_window") or {}
    used_pct = ctx.get("used_percentage", 0)
    cost = (data.get("cost") or {}).get("total_cost_usd", 0)

    branch = get_git_branch(project_dir)
    short_path = shorten_path(project_dir)

    # Build context bar (compact)
    filled = int(BAR_WIDTH * used_pct / 100)
    empty = BAR_WIDTH - filled
    bar = f"{FILLED * filled}{EMPTY * empty} {used_pct}%"

    # Powerline segments
    segments = []

    # Branch segment (blue bg)
    segments.append(f"{BG_BLUE}{FG_WHITE}{BOLD} {branch} {RESET}{FG_BLUE}{BG_CYAN}{SEP}{RESET}")

    # Model segment (cyan bg)
    segments.append(f"{BG_CYAN}{FG_BLACK} {model} {RESET}{FG_CYAN}{bar_color_bg(used_pct)}{SEP}{RESET}")

    # Context bar segment (dynamic color bg)
    bg = bar_color_bg(used_pct)
    fg_after = bar_fg_after(used_pct)
    segments.append(f"{bg}{FG_BLACK} {bar} {RESET}{fg_after}{BG_MAGENTA}{SEP}{RESET}")

    # Cost + path segment (magenta bg)
    segments.append(f"{BG_MAGENTA}{FG_WHITE} {format_cost(cost)} {short_path} {RESET}{FG_MAGENTA}{SEP}{RESET}")

    print("".join(segments))


if __name__ == "__main__":
    main()
