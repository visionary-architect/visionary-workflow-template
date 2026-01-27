#!/usr/bin/env python3
"""
Archive old sessions from STATE.md and DEVLOG.md.

Moves sessions older than 30 days to archive files to keep the main
files manageable. Can be run manually or as a periodic maintenance task.

Usage:
    python session_archiver.py              # Preview what would be archived
    python session_archiver.py --execute    # Actually archive old sessions
    python session_archiver.py --days 60    # Archive sessions older than 60 days
"""
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path

# Default age threshold for archiving (30 days)
DEFAULT_ARCHIVE_DAYS = 30


def main():
    parser = argparse.ArgumentParser(description="Archive old sessions")
    parser.add_argument(
        "--execute", action="store_true", help="Actually perform archiving (default: preview)"
    )
    parser.add_argument(
        "--days", type=int, default=DEFAULT_ARCHIVE_DAYS,
        help=f"Archive sessions older than N days (default: {DEFAULT_ARCHIVE_DAYS})"
    )
    args = parser.parse_args()

    cutoff_date = datetime.now() - timedelta(days=args.days)
    print(f"Archiving sessions older than {cutoff_date.strftime('%Y-%m-%d')} ({args.days} days)")
    print("=" * 60)

    # Archive STATE.md Session Log
    state_archived = archive_state_sessions(cutoff_date, args.execute)

    # Archive DEVLOG.md sessions
    devlog_archived = archive_devlog_sessions(cutoff_date, args.execute)

    print()
    print("=" * 60)
    print(f"STATE.md: {state_archived} sessions {'archived' if args.execute else 'would be archived'}")
    print(f"DEVLOG.md: {devlog_archived} sessions {'archived' if args.execute else 'would be archived'}")

    if not args.execute and (state_archived > 0 or devlog_archived > 0):
        print()
        print("Run with --execute to actually archive these sessions")


def archive_state_sessions(cutoff_date: datetime, execute: bool) -> int:
    """Archive old sessions from STATE.md Session Log."""
    state_file = Path("STATE.md")
    archive_file = Path("STATE_ARCHIVE.md")

    if not state_file.exists():
        print("STATE.md not found")
        return 0

    content = state_file.read_text(encoding="utf-8", errors="replace")

    # Find Session Log section
    session_log_match = re.search(
        r"(## Session Log\n)(.*?)(?=\n## |\Z)",
        content,
        re.DOTALL
    )

    if not session_log_match:
        print("No Session Log section found in STATE.md")
        return 0

    session_log_header = session_log_match.group(1)
    session_log_content = session_log_match.group(2)

    # Parse individual sessions (### YYYY-MM-DD format)
    session_pattern = r"(### \d{4}-\d{2}-\d{2}.*?)(?=\n### \d{4}-\d{2}-\d{2}|\Z)"
    sessions = re.findall(session_pattern, session_log_content, re.DOTALL)

    keep_sessions = []
    archive_sessions = []

    for session in sessions:
        # Extract date from session header
        date_match = re.match(r"### (\d{4}-\d{2}-\d{2})", session)
        if date_match:
            try:
                session_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                if session_date < cutoff_date:
                    archive_sessions.append(session)
                    print(f"  STATE.md: {date_match.group(1)} - archive")
                else:
                    keep_sessions.append(session)
            except ValueError:
                keep_sessions.append(session)  # Keep if date parsing fails
        else:
            keep_sessions.append(session)

    if not archive_sessions:
        print("  STATE.md: No sessions to archive")
        return 0

    if execute:
        # Write archived sessions to archive file
        archive_content = ""
        if archive_file.exists():
            archive_content = archive_file.read_text(encoding="utf-8", errors="replace")
            if not archive_content.endswith("\n\n"):
                archive_content += "\n\n"

        if not archive_content:
            archive_content = "# STATE.md Archive\n\n"
            archive_content += f"Sessions archived on {datetime.now().strftime('%Y-%m-%d')}\n\n"
            archive_content += "---\n\n"

        archive_content += "\n".join(archive_sessions)
        archive_file.write_text(archive_content, encoding="utf-8")

        # Update STATE.md with only kept sessions
        new_session_log = session_log_header + "\n".join(keep_sessions)
        new_content = content[:session_log_match.start()] + new_session_log + content[session_log_match.end():]
        state_file.write_text(new_content, encoding="utf-8")

        print(f"  Archived {len(archive_sessions)} sessions to STATE_ARCHIVE.md")

    return len(archive_sessions)


def archive_devlog_sessions(cutoff_date: datetime, execute: bool) -> int:
    """Archive old sessions from DEVLOG.md."""
    devlog_file = Path("DEVLOG.md")
    archive_file = Path("DEVLOG_ARCHIVE.md")

    if not devlog_file.exists():
        print("DEVLOG.md not found")
        return 0

    content = devlog_file.read_text(encoding="utf-8", errors="replace")

    # Find Recent Sessions section
    sessions_match = re.search(
        r"(## Recent Sessions\n)(.*?)(?=\n## |\Z)",
        content,
        re.DOTALL
    )

    if not sessions_match:
        print("No Recent Sessions section found in DEVLOG.md")
        return 0

    sessions_header = sessions_match.group(1)
    sessions_content = sessions_match.group(2)

    # Parse individual sessions (### Session: YYYY-MM-DD format)
    session_pattern = r"(### Session: \d{4}-\d{2}-\d{2}.*?)(?=\n### Session: \d{4}-\d{2}-\d{2}|\Z)"
    sessions = re.findall(session_pattern, sessions_content, re.DOTALL)

    keep_sessions = []
    archive_sessions = []

    for session in sessions:
        # Extract date from session header
        date_match = re.match(r"### Session: (\d{4}-\d{2}-\d{2})", session)
        if date_match:
            try:
                session_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                if session_date < cutoff_date:
                    archive_sessions.append(session)
                    print(f"  DEVLOG.md: {date_match.group(1)} - archive")
                else:
                    keep_sessions.append(session)
            except ValueError:
                keep_sessions.append(session)
        else:
            keep_sessions.append(session)

    if not archive_sessions:
        print("  DEVLOG.md: No sessions to archive")
        return 0

    if execute:
        # Write archived sessions to archive file
        archive_content = ""
        if archive_file.exists():
            archive_content = archive_file.read_text(encoding="utf-8", errors="replace")
            if not archive_content.endswith("\n\n"):
                archive_content += "\n\n"

        if not archive_content:
            archive_content = "# DEVLOG.md Archive\n\n"
            archive_content += f"Sessions archived on {datetime.now().strftime('%Y-%m-%d')}\n\n"
            archive_content += "---\n\n"

        archive_content += "\n".join(archive_sessions)
        archive_file.write_text(archive_content, encoding="utf-8")

        # Update DEVLOG.md with only kept sessions
        new_sessions = sessions_header + "\n".join(keep_sessions)
        new_content = content[:sessions_match.start()] + new_sessions + content[sessions_match.end():]
        devlog_file.write_text(new_content, encoding="utf-8")

        print(f"  Archived {len(archive_sessions)} sessions to DEVLOG_ARCHIVE.md")

    return len(archive_sessions)


if __name__ == "__main__":
    main()
