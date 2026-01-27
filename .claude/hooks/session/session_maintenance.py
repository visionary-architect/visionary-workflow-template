#!/usr/bin/env python3
"""
Automatic session maintenance on Stop.

Runs automatically when Claude session ends to:
1. Archive old sessions from STATE.md/DEVLOG.md (>30 days)
2. Rotate events.jsonl (archive entries >30 days)

This keeps session files manageable without manual intervention.
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
ARCHIVE_DAYS = 30
SESSION_DIR = Path(".claude/session")
EVENTS_FILE = SESSION_DIR / "events.jsonl"
EVENTS_ARCHIVE = SESSION_DIR / "events_archive.jsonl"


def main():
    """Run all maintenance tasks."""
    print(f"Session maintenance started at {datetime.now().isoformat()}")

    # Task 1: Archive old sessions
    archived_state, archived_devlog = archive_old_sessions()

    # Task 2: Rotate events
    rotated_events = rotate_events()

    # Summary
    if archived_state or archived_devlog or rotated_events:
        print(f"Maintenance complete: {archived_state} STATE sessions, {archived_devlog} DEVLOG sessions, {rotated_events} events archived")
    else:
        print("Maintenance complete: nothing to archive")


def archive_old_sessions():
    """Archive sessions older than ARCHIVE_DAYS from STATE.md and DEVLOG.md."""
    cutoff_date = datetime.now() - timedelta(days=ARCHIVE_DAYS)

    state_archived = archive_state_sessions(cutoff_date)
    devlog_archived = archive_devlog_sessions(cutoff_date)

    return state_archived, devlog_archived


def archive_state_sessions(cutoff_date):
    """Archive old sessions from STATE.md Session Log."""
    state_file = Path("STATE.md")
    archive_file = Path("STATE_ARCHIVE.md")

    if not state_file.exists():
        return 0

    try:
        content = state_file.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return 0

    # Find Session Log section
    session_log_match = re.search(
        r"(## Session Log\n)(.*?)(?=\n## |\Z)",
        content,
        re.DOTALL
    )

    if not session_log_match:
        return 0

    session_log_header = session_log_match.group(1)
    session_log_content = session_log_match.group(2)

    # Parse individual sessions
    session_pattern = r"(### \d{4}-\d{2}-\d{2}.*?)(?=\n### \d{4}-\d{2}-\d{2}|\Z)"
    sessions = re.findall(session_pattern, session_log_content, re.DOTALL)

    keep_sessions = []
    archive_sessions = []

    for session in sessions:
        date_match = re.match(r"### (\d{4}-\d{2}-\d{2})", session)
        if date_match:
            try:
                session_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                if session_date < cutoff_date:
                    archive_sessions.append(session)
                else:
                    keep_sessions.append(session)
            except ValueError:
                keep_sessions.append(session)
        else:
            keep_sessions.append(session)

    if not archive_sessions:
        return 0

    # Write archived sessions
    try:
        archive_content = ""
        if archive_file.exists():
            archive_content = archive_file.read_text(encoding="utf-8", errors="replace")
            if not archive_content.endswith("\n\n"):
                archive_content += "\n\n"

        if not archive_content:
            archive_content = f"# STATE.md Archive\n\nSessions archived on {datetime.now().strftime('%Y-%m-%d')}\n\n---\n\n"

        archive_content += "\n".join(archive_sessions)
        archive_file.write_text(archive_content, encoding="utf-8")

        # Update STATE.md
        new_session_log = session_log_header + "\n".join(keep_sessions)
        new_content = content[:session_log_match.start()] + new_session_log + content[session_log_match.end():]
        state_file.write_text(new_content, encoding="utf-8")

        return len(archive_sessions)
    except Exception as e:
        print(f"Warning: Failed to archive STATE sessions: {e}")
        return 0


def archive_devlog_sessions(cutoff_date):
    """Archive old sessions from DEVLOG.md."""
    devlog_file = Path("DEVLOG.md")
    archive_file = Path("DEVLOG_ARCHIVE.md")

    if not devlog_file.exists():
        return 0

    try:
        content = devlog_file.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return 0

    # Find Recent Sessions section
    sessions_match = re.search(
        r"(## Recent Sessions\n)(.*?)(?=\n## |\Z)",
        content,
        re.DOTALL
    )

    if not sessions_match:
        return 0

    sessions_header = sessions_match.group(1)
    sessions_content = sessions_match.group(2)

    # Parse individual sessions
    session_pattern = r"(### Session: \d{4}-\d{2}-\d{2}.*?)(?=\n### Session: \d{4}-\d{2}-\d{2}|\Z)"
    sessions = re.findall(session_pattern, sessions_content, re.DOTALL)

    keep_sessions = []
    archive_sessions = []

    for session in sessions:
        date_match = re.match(r"### Session: (\d{4}-\d{2}-\d{2})", session)
        if date_match:
            try:
                session_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                if session_date < cutoff_date:
                    archive_sessions.append(session)
                else:
                    keep_sessions.append(session)
            except ValueError:
                keep_sessions.append(session)
        else:
            keep_sessions.append(session)

    if not archive_sessions:
        return 0

    # Write archived sessions
    try:
        archive_content = ""
        if archive_file.exists():
            archive_content = archive_file.read_text(encoding="utf-8", errors="replace")
            if not archive_content.endswith("\n\n"):
                archive_content += "\n\n"

        if not archive_content:
            archive_content = f"# DEVLOG.md Archive\n\nSessions archived on {datetime.now().strftime('%Y-%m-%d')}\n\n---\n\n"

        archive_content += "\n".join(archive_sessions)
        archive_file.write_text(archive_content, encoding="utf-8")

        # Update DEVLOG.md
        new_sessions = sessions_header + "\n".join(keep_sessions)
        new_content = content[:sessions_match.start()] + new_sessions + content[sessions_match.end():]
        devlog_file.write_text(new_content, encoding="utf-8")

        return len(archive_sessions)
    except Exception as e:
        print(f"Warning: Failed to archive DEVLOG sessions: {e}")
        return 0


def rotate_events():
    """Archive events older than ARCHIVE_DAYS from events.jsonl."""
    if not EVENTS_FILE.exists():
        return 0

    cutoff_date = datetime.now() - timedelta(days=ARCHIVE_DAYS)

    try:
        keep_events = []
        archive_events = []

        with open(EVENTS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                    timestamp = event.get("timestamp", "")

                    # Parse timestamp
                    try:
                        # Handle various ISO formats
                        ts = timestamp.split("+")[0].split("-0")[0]  # Remove timezone
                        event_date = datetime.fromisoformat(ts)

                        if event_date < cutoff_date:
                            archive_events.append(line)
                        else:
                            keep_events.append(line)
                    except ValueError:
                        keep_events.append(line)  # Keep if can't parse
                except json.JSONDecodeError:
                    keep_events.append(line)  # Keep malformed lines

        if not archive_events:
            return 0

        # Append to archive
        with open(EVENTS_ARCHIVE, "a", encoding="utf-8") as f:
            for line in archive_events:
                f.write(line if line.endswith("\n") else line + "\n")

        # Rewrite events file with only recent events
        with open(EVENTS_FILE, "w", encoding="utf-8") as f:
            for line in keep_events:
                f.write(line if line.endswith("\n") else line + "\n")

        return len(archive_events)
    except Exception as e:
        print(f"Warning: Failed to rotate events: {e}")
        return 0


if __name__ == "__main__":
    main()
