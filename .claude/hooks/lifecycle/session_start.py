#!/usr/bin/env python3
"""
SessionStart lifecycle hook — context injection and project detection.

Fires on: SessionStart (source: startup/resume/clear/compact)
Sync: YES (outputs additionalContext that must be available immediately)

What it does:
1. On startup ONLY: detect project type, check optional deps, persist env vars
2. On ALL sources: inject context via additionalContext (git log, status, issues)
3. Initialize session JSON audit record
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Shared utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.constants import PROJECT_DIR, SESSION_DATA_DIR, ENGINEER_NAME
from utils.stdin_parser import parse_hook_input, get_session_id


# ---------------------------------------------------------------------------
# Project type detection
# ---------------------------------------------------------------------------
PROJECT_SIGNATURES = {
    "pyproject.toml": "Python (pyproject.toml)",
    "setup.py": "Python (setup.py)",
    "package.json": "Node.js",
    "Cargo.toml": "Rust",
    "go.mod": "Go",
    "pom.xml": "Java (Maven)",
    "build.gradle": "Java (Gradle)",
    "Gemfile": "Ruby",
    "composer.json": "PHP",
    "*.csproj": "C# (.NET)",
}


def detect_project_type() -> str:
    """Detect project type from files present in the project root."""
    detected = []
    for filename, label in PROJECT_SIGNATURES.items():
        if filename.startswith("*"):
            # Glob pattern
            if list(PROJECT_DIR.glob(filename)):
                detected.append(label)
        elif (PROJECT_DIR / filename).exists():
            detected.append(label)

    return ", ".join(detected) if detected else "Unknown"


def check_optional_deps() -> dict:
    """Check availability of optional dependencies."""
    deps = {}
    for mod_name in ("pyttsx3", "anthropic"):
        try:
            __import__(mod_name)
            deps[mod_name] = True
        except ImportError:
            deps[mod_name] = False
    return deps


def persist_env_vars(input_data: dict) -> None:
    """
    Persist environment variables via CLAUDE_ENV_FILE.

    CLAUDE_ENV_FILE is ONLY available in SessionStart hooks.
    Format: KEY=VALUE lines appended to the file.
    """
    env_file = os.environ.get("CLAUDE_ENV_FILE", "")
    if not env_file:
        return

    try:
        lines = []
        # Persist project type for other hooks
        project_type = detect_project_type()
        lines.append(f"DETECTED_PROJECT_TYPE={project_type}")

        # Persist optional dep availability
        deps = check_optional_deps()
        lines.append(f"TTS_AVAILABLE={'1' if deps.get('pyttsx3') else '0'}")
        lines.append(f"LLM_AVAILABLE={'1' if deps.get('anthropic') else '0'}")

        with open(env_file, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Context gathering
# ---------------------------------------------------------------------------
def get_git_log(count: int = 5) -> str:
    """Get recent git log (oneline format)."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"-{count}"],
            capture_output=True, text=True, timeout=5, cwd=str(PROJECT_DIR),
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def get_git_status() -> str:
    """Get modified files via git status."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=5, cwd=str(PROJECT_DIR),
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split("\n")
            return f"{len(lines)} modified file(s)"
        return "Clean working tree"
    except Exception:
        return ""


def get_git_branch() -> str:
    """Get current git branch."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=5, cwd=str(PROJECT_DIR),
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def get_open_issues(limit: int = 5) -> str:
    """Get open GitHub issues if gh CLI is available."""
    if not shutil.which("gh"):
        return ""
    try:
        result = subprocess.run(
            ["gh", "issue", "list", "--state", "open", "--limit", str(limit)],
            capture_output=True, text=True, timeout=10, cwd=str(PROJECT_DIR),
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def build_context(input_data: dict) -> str:
    """Build additionalContext string from git and project data."""
    parts = []

    session_id = get_session_id(input_data)
    source = input_data.get("source", "unknown")
    model = input_data.get("model", "unknown")

    parts.append(f"Session: {session_id[:12]}... | Source: {source} | Model: {model}")

    branch = get_git_branch()
    if branch:
        parts.append(f"Branch: {branch}")

    status = get_git_status()
    if status:
        parts.append(f"Working tree: {status}")

    git_log = get_git_log()
    if git_log:
        parts.append(f"Recent commits:\n{git_log}")

    issues = get_open_issues()
    if issues:
        parts.append(f"Open issues:\n{issues}")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Session JSON management
# ---------------------------------------------------------------------------
def init_session_json(input_data: dict) -> None:
    """Initialize per-session audit JSON."""
    SESSION_DATA_DIR.mkdir(parents=True, exist_ok=True)

    session_id = get_session_id(input_data)
    session_file = SESSION_DATA_DIR / f"{session_id}.json"

    if session_file.exists():
        # Resume — update last_seen
        try:
            data = json.loads(session_file.read_text(encoding="utf-8"))
            data["last_seen"] = time.time()
            data.setdefault("resumes", 0)
            data["resumes"] += 1
            session_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except (json.JSONDecodeError, OSError):
            pass
        return

    session_data = {
        "session_id": session_id,
        "started_at": time.time(),
        "last_seen": time.time(),
        "source": input_data.get("source", "unknown"),
        "model": input_data.get("model", "unknown"),
        "engineer": ENGINEER_NAME,
        "project_type": detect_project_type(),
        "resumes": 0,
        "prompts": [],
        "notifications": [],
        "permissions": [],
        "errors": [],
        "subagents": [],
    }

    try:
        session_file.write_text(json.dumps(session_data, indent=2), encoding="utf-8")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    input_data = parse_hook_input()
    source = input_data.get("source", "unknown")

    # First-time startup tasks
    if source == "startup":
        persist_env_vars(input_data)

    # Initialize/update session JSON
    init_session_json(input_data)

    # Build and output context
    context = build_context(input_data)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
