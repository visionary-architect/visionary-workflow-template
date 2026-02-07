#!/usr/bin/env python3
"""
Log significant project events for lifetime tracking.

This async hook runs after Write/Edit, Bash, and TodoWrite operations to detect and log:
- Git tags (milestone releases)
- Commits with feat:/fix: prefixes
- Phase command completions
- Test pass/fail transitions
- Task completions (via TodoWrite)

Output:
- .claude/session/events.jsonl (machine-readable JSONL)
- Updates TIMELINE.md Recent Events section (human-readable)

Event format:
{"timestamp": "...", "type": "...", "summary": "...", "details": {...}}
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.file_lock import locked_json_rw

SESSION_DIR = Path(".claude/session")
EVENTS_FILE = SESSION_DIR / "events.jsonl"
TIMELINE_FILE = Path("TIMELINE.md")

# Track last known state to detect transitions
STATE_FILE = SESSION_DIR / "event_state.json"


def main():
    """Detect and log significant events."""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    # Get tool context from stdin
    tool_name = os.environ.get("CLAUDE_TOOL_NAME", "")

    try:
        stdin_data = sys.stdin.read()
        if stdin_data:
            data = json.loads(stdin_data)
            tool_input = data.get("tool_input", {}) or {}
            tool_result = data.get("tool_result", {}) or {}
            if not isinstance(tool_input, dict):
                return
        else:
            tool_input = {}
            tool_result = {}
    except Exception:
        tool_input = {}
        tool_result = {}

    events = []

    # Detect git tag creation
    if tool_name == "Bash":
        command = tool_input.get("command", "") or ""
        if not isinstance(command, str):
            command = ""
        if "git tag" in command and "-a" in command:
            tag_match = re.search(r'git tag -a\s+(\S+)', command)
            if tag_match:
                tag = tag_match.group(1)
                events.append({
                    "type": "milestone",
                    "summary": f"Created tag {tag}",
                    "details": {"tag": tag, "command": command[:200]}
                })

    # Detect git commits with feat:/fix:
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if "git commit" in command:
            # Extract commit message
            msg_match = re.search(r'-m\s+["\']([^"\']+)["\']', command)
            if not msg_match:
                msg_match = re.search(r'-m\s+"([^"]+)"', command)

            if msg_match:
                msg = msg_match.group(1)
                commit_type = None

                if msg.startswith("feat"):
                    commit_type = "feature"
                elif msg.startswith("fix"):
                    commit_type = "fix"
                elif msg.startswith("refactor"):
                    commit_type = "refactor"

                if commit_type:
                    events.append({
                        "type": commit_type,
                        "summary": msg[:80],
                        "details": {"full_message": msg}
                    })

    # Detect phase command completions
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        stdout = tool_result.get("stdout", "") if isinstance(tool_result, dict) else ""

        # Check for phase completion markers
        if "complete-milestone" in command or ("Phase" in stdout and "Complete" in stdout):
            phase_match = re.search(r'[Pp]hase\s*(\d+)', command + stdout)
            if phase_match:
                phase = phase_match.group(1)
                events.append({
                    "type": "phase_complete",
                    "summary": f"Completed Phase {phase}",
                    "details": {"phase": phase}
                })

    # Detect test pass/fail transitions
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if "pytest" in command or "npm run test" in command:
            stdout = tool_result.get("stdout", "") if isinstance(tool_result, dict) else ""
            stderr = tool_result.get("stderr", "") if isinstance(tool_result, dict) else ""
            output = stdout + stderr

            # Load previous state
            prev_state = load_state()

            # Determine current test state
            if "passed" in output and "failed" not in output.lower():
                current_state = "passing"
            elif "failed" in output.lower() or "error" in output.lower():
                current_state = "failing"
            else:
                current_state = "unknown"

            # Detect transitions
            prev_test_state = prev_state.get("test_state", "unknown")
            if prev_test_state == "failing" and current_state == "passing":
                events.append({
                    "type": "test_transition",
                    "summary": "Tests now passing",
                    "details": {"from": "failing", "to": "passing"}
                })
            elif prev_test_state == "passing" and current_state == "failing":
                events.append({
                    "type": "test_transition",
                    "summary": "Tests now failing",
                    "details": {"from": "passing", "to": "failing"}
                })

            # Save current state
            save_state({"test_state": current_state})

    # Detect task completions (TodoWrite)
    if tool_name == "TodoWrite":
        todos = tool_input.get("todos", [])
        prev_state = load_state()
        prev_tasks = prev_state.get("task_statuses", {})

        completed_tasks = []
        for todo in todos:
            content = todo.get("content", "")
            status = todo.get("status", "")
            task_id = content[:50]  # Use first 50 chars as ID

            # Check if this task just became completed
            if status == "completed":
                if prev_tasks.get(task_id) != "completed":
                    completed_tasks.append(content)

            # Update tracked status
            prev_tasks[task_id] = status

        # Save updated task statuses
        save_state({"task_statuses": prev_tasks})

        # Log significant task completions (skip trivial ones)
        for task in completed_tasks:
            # Only log tasks that look like plan steps or milestones
            if re.match(r'\[[\d\w-]+\]', task) or "Phase" in task or "milestone" in task.lower():
                events.append({
                    "type": "task_complete",
                    "summary": task[:60],
                    "details": {"full_task": task}
                })

    # Write events to JSONL
    for event in events:
        log_event(event)


def load_state():
    """Load previous event state."""
    if not STATE_FILE.exists():
        return {}
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state):
    """Save event state atomically with file locking."""
    with locked_json_rw(STATE_FILE, default={}) as (existing, save):
        existing.update(state)
        save(existing)


def log_event(event):
    """Log event to JSONL file and update TIMELINE.md."""
    timestamp = datetime.now().isoformat()
    event["timestamp"] = timestamp

    # Append to JSONL
    try:
        with open(EVENTS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        print(f"Warning: Failed to write event to JSONL: {e}")

    # Update TIMELINE.md Recent Events section
    try:
        update_timeline(event)
    except Exception as e:
        print(f"Warning: Failed to update TIMELINE.md: {e}")


def update_timeline(event):
    """Update TIMELINE.md Recent Events table."""
    if not TIMELINE_FILE.exists():
        return

    content = TIMELINE_FILE.read_text(encoding="utf-8", errors="replace")

    # Find Recent Events section
    pattern = r'(## Recent Events\n\n\| Date \| Type \| Summary \| Details \|\n\|------|------|---------|---------|)\n((?:\|.*\n)*)'
    match = re.search(pattern, content)

    if not match:
        return

    header = match.group(1)
    existing_rows = match.group(2)

    # Create new row
    date = datetime.now().strftime("%Y-%m-%d")
    event_type = event.get("type", "unknown")
    summary = event.get("summary", "")[:50]
    details = event.get("details", {})
    details_str = ", ".join(f"{k}={v}" for k, v in list(details.items())[:2])[:40]

    new_row = f"| {date} | {event_type} | {summary} | {details_str} |\n"

    # Keep only last 10 events (including new one)
    rows = existing_rows.strip().split("\n") if existing_rows.strip() else []
    rows = [new_row.strip()] + rows[:9]
    new_rows = "\n".join(rows) + "\n"

    # Replace in content
    new_section = header + "\n" + new_rows
    new_content = content[:match.start()] + new_section + content[match.end():]

    TIMELINE_FILE.write_text(new_content, encoding="utf-8")


def get_recent_events(count=10):
    """Get recent events from JSONL file (utility function)."""
    if not EVENTS_FILE.exists():
        return []

    events = []
    try:
        with open(EVENTS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
    except Exception:
        return []

    return events[-count:]


if __name__ == "__main__":
    main()
