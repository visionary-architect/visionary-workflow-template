#!/usr/bin/env python3
"""
SubagentStart lifecycle hook — subagent spawn tracking.

Fires on: SubagentStart
Sync: NO (async — logging only)

What it does:
1. Log spawn event to session JSON subagents array
2. Increment active subagent counter
3. Debug log to stderr (visible in verbose mode)
"""
import json
import sys
import time
from pathlib import Path

# Shared utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.constants import SESSION_DATA_DIR
from utils.stdin_parser import parse_hook_input, get_session_id


def log_subagent_start(session_id: str, agent_id: str, agent_type: str) -> None:
    """Record subagent spawn in session JSON."""
    session_file = SESSION_DATA_DIR / f"{session_id}.json"
    try:
        if session_file.exists():
            data = json.loads(session_file.read_text(encoding="utf-8"))
        else:
            data = {"session_id": session_id, "subagents": []}

        data.setdefault("subagents", []).append({
            "agent_id": agent_id,
            "agent_type": agent_type,
            "started_at": time.time(),
            "completed_at": None,
            "summary": None,
        })

        # Track active count
        active = sum(
            1 for s in data["subagents"] if s.get("completed_at") is None
        )
        data["active_subagents"] = active

        session_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except (json.JSONDecodeError, OSError):
        pass


def main():
    input_data = parse_hook_input()
    session_id = get_session_id(input_data)
    agent_id = input_data.get("agent_id", "unknown")
    agent_type = input_data.get("agent_type", "unknown")

    log_subagent_start(session_id, agent_id, agent_type)

    # Debug log (visible in verbose mode only)
    print(
        f"Subagent spawned: {agent_type} ({agent_id[:12]}...)",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
