#!/usr/bin/env python3
"""
Pre-compile context cache for fast resume.

This hook runs asynchronously on the first tool use in a session, pre-parsing
STATE.md and DEVLOG.md to build a JSON cache that /resume-work can read quickly.

Output: .claude/session/context_cache.json
"""
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

CACHE_DIR = Path(".claude/session")
CACHE_FILE = CACHE_DIR / "context_cache.json"
LOCK_FILE = CACHE_DIR / "warmup.lock"
HASH_FILE = CACHE_DIR / "source_hash.txt"

# Session duration in seconds (5 minutes) - prevents repeated runs in same session
SESSION_DURATION = 300

# Cache TTL in seconds (4 hours) - invalidate stale cache regardless of hash
CACHE_TTL = 4 * 60 * 60  # 14400 seconds


def main():
    """Build context cache if needed."""
    # Only run once per session (check lock file age)
    if LOCK_FILE.exists():
        try:
            lock_age = datetime.now().timestamp() - LOCK_FILE.stat().st_mtime
            if lock_age < SESSION_DURATION:
                return  # Already warming/warmed this session
        except Exception:
            pass  # Lock file corrupted, continue

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Touch lock file to claim this session
    try:
        LOCK_FILE.touch()
    except Exception:
        return  # Can't acquire lock, skip

    try:
        # Check cache TTL first - invalidate if older than 4 hours
        if CACHE_FILE.exists():
            try:
                cache_age = datetime.now().timestamp() - CACHE_FILE.stat().st_mtime
                if cache_age > CACHE_TTL:
                    print(f"Cache expired ({cache_age/3600:.1f}h old, TTL={CACHE_TTL/3600}h)")
                    # Continue to rebuild
                else:
                    # Check if sources changed (skip if cache is fresh and within TTL)
                    current_hash = compute_source_hash()
                    if HASH_FILE.exists():
                        if HASH_FILE.read_text().strip() == current_hash:
                            return  # Cache is still valid and within TTL
            except Exception:
                pass  # Cache file issue, rebuild

        # Compute hash for new cache
        current_hash = compute_source_hash()

        # Build cache
        cache = {
            "generated_at": datetime.now().isoformat(),
            "handoff": extract_handoff_notes(),
            "active_issues": extract_active_issues(),
            "recent_commits": get_recent_commits(),
            "current_phase": extract_current_phase(),
            "uncommitted_files": get_uncommitted_files(),
            "active_tasks": get_active_tasks(),
            "task_claims": get_task_claims(),
            "active_sessions": get_active_sessions(),
            "file_locks": get_file_locks(),
            "work_queue": get_work_queue_summary(),
            "startup_context": get_startup_context(),
        }

        # Atomic write
        temp_file = CACHE_DIR / "context_cache.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
        temp_file.replace(CACHE_FILE)
        HASH_FILE.write_text(current_hash)

        print(f"Context cache built: {CACHE_FILE}")

    except Exception as e:
        print(f"Warning: Failed to build context cache: {e}")


def compute_source_hash():
    """Compute hash of source files to detect changes."""
    files = ["STATE.md", "DEVLOG.md"]
    content = ""
    for f in files:
        path = Path(f)
        if path.exists():
            try:
                content += path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                pass
    return hashlib.md5(content.encode()).hexdigest()[:16]


def extract_handoff_notes():
    """Extract Handoff Notes section from STATE.md."""
    state_file = Path("STATE.md")
    if not state_file.exists():
        return None

    try:
        content = state_file.read_text(encoding="utf-8", errors="replace")
        # Find Handoff Notes section
        match = re.search(
            r"## Handoff Notes\n(.*?)(?=\n## |\Z)", content, re.DOTALL
        )
        if match:
            notes = match.group(1).strip()
            # Extract key fields
            return {
                "raw": notes[:2000],  # Truncate for cache size
                "last_updated": extract_field(notes, r"\*\*Last Updated:\*\*\s*(.+)"),
                "session_ended": extract_field(notes, r"\*\*Session Ended:\*\*\s*(.+)"),
            }
        return None
    except Exception:
        return None


def extract_field(text, pattern):
    """Extract a field value using regex pattern."""
    match = re.search(pattern, text)
    return match.group(1).strip() if match else None


def extract_active_issues():
    """Extract Active Issues table from DEVLOG.md."""
    devlog_file = Path("DEVLOG.md")
    if not devlog_file.exists():
        return []

    try:
        content = devlog_file.read_text(encoding="utf-8", errors="replace")
        # Find active issues table (look for ID | Description | Status pattern)
        match = re.search(
            r"\| ID \| Description \| Status \|.*?\n\|[-| ]+\|\n((?:\|.*\n)*)",
            content,
        )
        if not match:
            return []

        issues = []
        for line in match.group(1).strip().split("\n"):
            if "|" in line:
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 3:
                    status = parts[2].lower() if len(parts) > 2 else ""
                    # Only include non-fixed issues
                    if "fixed" not in status:
                        issues.append({
                            "id": parts[0],
                            "description": parts[1][:100],  # Truncate
                            "status": parts[2] if len(parts) > 2 else "unknown",
                        })
        return issues
    except Exception:
        return []


def extract_current_phase():
    """Extract current phase from STATE.md."""
    state_file = Path("STATE.md")
    if not state_file.exists():
        return None

    try:
        content = state_file.read_text(encoding="utf-8", errors="replace")
        # Try different patterns
        patterns = [
            r"\*\*Phase:\*\*\s*(\d+)",
            r"Phase\s+(\d+)",
            r"Phase (\d+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return int(match.group(1))
        return None
    except Exception:
        return None


def get_recent_commits():
    """Get last 5 commit messages."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        commits = result.stdout.strip()
        return commits.split("\n") if commits else []
    except Exception:
        return []


def get_uncommitted_files():
    """Get list of uncommitted files."""
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        status = result.stdout.strip()
        return status.split("\n") if status else []
    except Exception:
        return []


def get_active_tasks():
    """Get active tasks from the persistent task list."""
    try:
        # Task list location based on CLAUDE_CODE_TASK_LIST_ID
        import os
        task_list_id = os.environ.get("CLAUDE_CODE_TASK_LIST_ID", "my-project")
        tasks_dir = Path.home() / ".claude" / "tasks" / task_list_id

        if not tasks_dir.exists():
            return []

        tasks = []
        for task_file in tasks_dir.glob("*.json"):
            try:
                with open(task_file, encoding="utf-8") as f:
                    task = json.load(f)
                tasks.append({
                    "id": task.get("id"),
                    "subject": task.get("subject", "")[:80],
                    "status": task.get("status", "unknown"),
                    "activeForm": task.get("activeForm", ""),
                })
            except Exception:
                pass

        # Sort by status: in_progress first, then pending
        status_order = {"in_progress": 0, "pending": 1, "completed": 2}
        tasks.sort(key=lambda t: status_order.get(t.get("status"), 99))

        return tasks[:20]  # Limit to 20 tasks
    except Exception:
        return []


def get_task_claims():
    """Get current task claims from session coordination."""
    locks_file = CACHE_DIR / "task_locks.json"
    if not locks_file.exists():
        return []

    try:
        with open(locks_file, encoding="utf-8") as f:
            locks = json.load(f)

        claims = []
        for task_id, lock in locks.items():
            claims.append({
                "task_id": task_id[:12],
                "session_tag": lock.get("session_tag", "unknown"),
                "claimed_at": lock.get("claimed_at", "unknown"),
                "content": lock.get("task_content", "")[:50],
            })

        return claims
    except Exception:
        return []


def get_active_sessions():
    """Get currently active sessions."""
    sessions_file = CACHE_DIR / "sessions.json"
    if not sessions_file.exists():
        return []

    try:
        with open(sessions_file, encoding="utf-8") as f:
            sessions = json.load(f)

        now = datetime.now()
        active = []
        for session_id, session in sessions.items():
            try:
                last_seen = datetime.fromisoformat(session.get("last_seen", ""))
                # Active if seen within last 5 minutes
                if (now - last_seen).total_seconds() < 300:
                    active.append({
                        "id": session_id[:8],
                        "tag": session.get("tag", "unknown"),
                        "tool_count": session.get("tool_count", 0),
                        "claimed_tasks": len(session.get("claimed_tasks", [])),
                    })
            except Exception:
                pass

        return active
    except Exception:
        return []


def get_file_locks():
    """Get current file locks."""
    file_locks_file = CACHE_DIR / "file_locks.json"
    if not file_locks_file.exists():
        return []

    try:
        with open(file_locks_file, encoding="utf-8") as f:
            locks = json.load(f)

        now = datetime.now()
        active = []
        for file_key, lock in locks.items():
            try:
                last_touched = datetime.fromisoformat(lock.get("last_touched", ""))
                # Only include active locks (touched within 10 minutes)
                if (now - last_touched).total_seconds() < 600:
                    active.append({
                        "file": lock.get("file_path", file_key)[-50:],  # Last 50 chars
                        "session_tag": lock.get("session_tag", "unknown"),
                    })
            except Exception:
                pass

        return active
    except Exception:
        return []


def get_work_queue_summary():
    """Get summary of work queue status."""
    work_queue_file = CACHE_DIR / "work_queue.json"
    if not work_queue_file.exists():
        return {"available": 0, "claimed": 0, "tasks": []}

    try:
        with open(work_queue_file, encoding="utf-8") as f:
            queue = json.load(f)

        tasks = queue.get("tasks", [])
        available = [t for t in tasks if t.get("status") == "available"]
        claimed = [t for t in tasks if t.get("status") == "claimed"]

        # Sort available by priority
        available.sort(key=lambda t: (t.get("priority", 2), t.get("created_at", "")))

        # Return summary with top 5 available tasks
        return {
            "available": len(available),
            "claimed": len(claimed),
            "total_completed": queue.get("metadata", {}).get("total_completed", 0),
            "tasks": [
                {
                    "id": t.get("id"),
                    "priority": t.get("priority", 2),
                    "description": t.get("description", "")[:60],
                    "status": t.get("status"),
                    "claimed_by": t.get("claimed_by"),
                }
                for t in available[:5]
            ],
        }
    except Exception:
        return {"available": 0, "claimed": 0, "tasks": []}


def get_startup_context():
    """Get worker startup context if this session was launched with a task."""
    startup_file = CACHE_DIR / "worker_startup_context.json"
    if not startup_file.exists():
        return None

    try:
        with open(startup_file, encoding="utf-8") as f:
            context = json.load(f)

        # Only return if recent (within last 5 minutes)
        timestamp = context.get("timestamp")
        if timestamp:
            ctx_time = datetime.fromisoformat(timestamp)
            if (datetime.now() - ctx_time).total_seconds() > 300:
                return None  # Stale context

        return {
            "session_tag": context.get("session_tag"),
            "assigned_task": context.get("selected_task"),
            "custom_task": context.get("custom_task"),
            "timestamp": timestamp,
        }
    except Exception:
        return None


if __name__ == "__main__":
    main()
