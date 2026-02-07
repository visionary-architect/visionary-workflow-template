#!/usr/bin/env python3
"""
v3 Agent Sessions Status Line — With agent codename and recent prompts.

Output: project-name | branch | Model | Agent: Phoenix | [prompt1 | prompt2 | prompt3]

Shows agent name in bright red. Last 3 prompts with recency-based truncation
(75/50/40 chars). Reads from per-session JSON.
"""
import json
import os
import sys
from pathlib import Path


# ANSI colors
CYAN = "\033[36m"
BRIGHT_RED = "\033[91m"
DIM = "\033[2m"
RESET = "\033[0m"

# Recency-based truncation limits (most recent first)
TRUNCATION = [75, 50, 40]


def truncate(text: str, max_len: int) -> str:
    """Truncate text with ellipsis if needed."""
    text = text.strip().replace("\n", " ")
    if len(text) <= max_len:
        return text
    return text[:max_len - 1] + "\u2026"


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
    agent = session.get("agent_name", "")
    prompts = session.get("prompts", [])

    parts = [f"{CYAN}{project}{RESET}"]
    if branch:
        parts.append(branch)
    parts.append(model)
    if agent:
        parts.append(f"{BRIGHT_RED}Agent: {agent}{RESET}")

    # Show last 3 prompts with recency-based truncation
    if prompts:
        recent = prompts[-3:]  # last 3
        recent.reverse()  # most recent first
        prompt_parts = []
        for i, prompt in enumerate(recent):
            text = prompt if isinstance(prompt, str) else prompt.get("text", str(prompt))
            limit = TRUNCATION[i] if i < len(TRUNCATION) else TRUNCATION[-1]
            prompt_parts.append(truncate(text, limit))
        prompt_parts.reverse()  # back to chronological order for display
        parts.append(f"{DIM}[{' | '.join(prompt_parts)}]{RESET}")

    print(" | ".join(parts))


if __name__ == "__main__":
    main()
