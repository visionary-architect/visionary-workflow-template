#!/usr/bin/env python3
"""
Track file change frequency for smarter context loading.

This async hook runs after Write/Edit operations and maintains a frequency
map of which files are edited most often. This data can be used to:
- Prioritize context loading for frequently-edited files
- Identify hot spots in the codebase
- Inform caching strategies

Output: .claude/session/file_frequency.json
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

SESSION_DIR = Path(".claude/session")
FREQUENCY_FILE = SESSION_DIR / "file_frequency.json"

# Maximum number of files to track
MAX_FILES = 100

# Decay factor for old edits (multiply by this each day)
DECAY_FACTOR = 0.9


def main():
    """Track file edit frequency."""
    # Get the file path that was edited
    file_path = os.environ.get("CLAUDE_FILE_PATH", "")

    if not file_path:
        # Try reading from stdin
        try:
            stdin_data = sys.stdin.read()
            if stdin_data:
                data = json.loads(stdin_data)
                tool_input = data.get("tool_input", {})
                file_path = tool_input.get("file_path", "") if isinstance(tool_input, dict) else ""
        except Exception:
            pass

    if not file_path or not isinstance(file_path, str):
        return

    # Normalize path
    try:
        file_path = str(Path(file_path).resolve().relative_to(Path.cwd()))
    except ValueError:
        # Path is outside cwd, use as-is
        file_path = str(Path(file_path).name)

    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing frequency data
    frequency_data = load_frequency_data()

    # Update frequency for this file
    update_frequency(frequency_data, file_path)

    # Apply decay to old entries
    apply_decay(frequency_data)

    # Trim to max files
    trim_entries(frequency_data)

    # Save updated data
    save_frequency_data(frequency_data)


def load_frequency_data():
    """Load existing frequency data from file."""
    if not FREQUENCY_FILE.exists():
        return {
            "last_updated": None,
            "files": {}
        }

    try:
        with open(FREQUENCY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "last_updated": None,
            "files": {}
        }


def update_frequency(data, file_path):
    """Update frequency count for a file."""
    files = data.get("files", {})

    if file_path not in files:
        files[file_path] = {
            "count": 0,
            "score": 0.0,
            "first_seen": datetime.now().isoformat(),
            "last_edited": None,
            "sessions": []
        }

    entry = files[file_path]
    entry["count"] = entry.get("count", 0) + 1
    entry["score"] = entry.get("score", 0.0) + 1.0
    entry["last_edited"] = datetime.now().isoformat()

    # Track unique sessions (by date)
    today = datetime.now().strftime("%Y-%m-%d")
    sessions = entry.get("sessions", [])
    if today not in sessions:
        sessions.append(today)
        # Keep only last 30 session dates
        entry["sessions"] = sessions[-30:]

    data["files"] = files
    data["last_updated"] = datetime.now().isoformat()


def apply_decay(data):
    """Apply decay to old entries based on last update time."""
    last_updated = data.get("last_updated")
    if not last_updated:
        return

    try:
        last_dt = datetime.fromisoformat(last_updated)
        days_since = (datetime.now() - last_dt).days

        if days_since > 0:
            decay = DECAY_FACTOR ** days_since
            files = data.get("files", {})
            for file_path in files:
                files[file_path]["score"] = files[file_path].get("score", 1.0) * decay
    except Exception:
        pass


def trim_entries(data):
    """Remove low-scoring entries if over max files."""
    files = data.get("files", {})

    if len(files) <= MAX_FILES:
        return

    # Sort by score and keep top MAX_FILES
    sorted_files = sorted(
        files.items(),
        key=lambda x: x[1].get("score", 0),
        reverse=True
    )

    data["files"] = dict(sorted_files[:MAX_FILES])


def save_frequency_data(data):
    """Save frequency data atomically."""
    temp_file = FREQUENCY_FILE.with_suffix(".tmp")
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        temp_file.replace(FREQUENCY_FILE)
    except Exception as e:
        print(f"Warning: Failed to save file frequency data: {e}")
        if temp_file.exists():
            temp_file.unlink()


def get_hot_files(top_n=10):
    """Get the most frequently edited files (utility function)."""
    data = load_frequency_data()
    files = data.get("files", {})

    sorted_files = sorted(
        files.items(),
        key=lambda x: x[1].get("score", 0),
        reverse=True
    )

    return [(path, info["score"], info["count"]) for path, info in sorted_files[:top_n]]


if __name__ == "__main__":
    main()
