#!/usr/bin/env python3
"""
v2 Smart Prompts Status Line — Color-coded by prompt type with icons.

Output: project-name | branch | Model | ⚡ 12 prompts

Prompt categories:
  commands (yellow ⚡) — starts with / or contains "run", "execute", "deploy"
  questions (blue ?) — starts with question words or contains ?
  creation (green 💡) — contains "create", "add", "new", "build", "implement"
  fix (red 🐛) — contains "fix", "bug", "error", "broken", "issue"
  refactor (magenta ♻) — contains "refactor", "rename", "move", "reorganize", "clean"
  default (white 💬)

Reads prompt data from session JSON (written by user_prompt_submit.py).
"""
import json
import os
import re
import sys

# Ensure UTF-8 output on Windows (needed for emoji/Unicode icons)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
from pathlib import Path


# ANSI colors
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
RED = "\033[31m"
MAGENTA = "\033[35m"
WHITE = "\033[37m"
DIM = "\033[2m"
RESET = "\033[0m"

# Prompt classification patterns
CATEGORIES = [
    ("command", YELLOW, "\u26a1", re.compile(r"^/|(?:run|execute|deploy|launch|start)\b", re.I)),
    ("question", BLUE, "?", re.compile(r"^(?:what|how|why|where|when|who|which|can|does|is|are|do|should|could|would)\b|[?]", re.I)),
    ("fix", RED, "\U0001f41b", re.compile(r"\b(?:fix|bug|error|broken|issue|crash|fail|wrong)\b", re.I)),
    ("refactor", MAGENTA, "\u267b", re.compile(r"\b(?:refactor|rename|move|reorganize|clean|simplif|restructur)\b", re.I)),
    ("creation", GREEN, "\U0001f4a1", re.compile(r"\b(?:create|add|new|build|implement|make|write|generate|setup|init)\b", re.I)),
]
DEFAULT_CATEGORY = ("default", WHITE, "\U0001f4ac")


def classify_prompt(text: str) -> tuple[str, str, str]:
    """Classify a prompt into a category. Returns (name, color, icon)."""
    for name, color, icon, pattern in CATEGORIES:
        if pattern.search(text):
            return name, color, icon
    return DEFAULT_CATEGORY


def get_session_data(session_id: str) -> dict:
    """Read session JSON."""
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    session_file = project_dir / ".claude" / "data" / "sessions" / f"{session_id}.json"
    try:
        if session_file.exists():
            return json.loads(session_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
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

    session = get_session_data(session_id)
    prompts = session.get("prompts", [])
    count = len(prompts)

    # Classify the last prompt for color/icon
    last_prompt = session.get("last_prompt", "")
    _name, color, icon = classify_prompt(last_prompt) if last_prompt else DEFAULT_CATEGORY

    parts = [f"{CYAN}{project}{RESET}"]
    if branch:
        parts.append(branch)
    parts.append(model)
    parts.append(f"{color}{icon} {count} prompts{RESET}")

    print(" | ".join(parts))


if __name__ == "__main__":
    main()
