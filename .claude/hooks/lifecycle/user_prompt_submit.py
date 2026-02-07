#!/usr/bin/env python3
"""
UserPromptSubmit lifecycle hook — prompt logging, agent naming, validation.

Fires on: UserPromptSubmit (NO matcher support — always fires)
Sync: YES (must be sync to enable prompt blocking via exit code 2)

CLI flags:
  --log-only          Append prompt to session JSON prompts array
  --store-last-prompt Store prompt text in session JSON last_prompt field
  --name-agent        On FIRST prompt, generate agent codename
  --validate          Reject empty prompts (exit 2), warn on very short

Blocking protocol:
  Exit code 2 + stderr = block (erases prompt from Claude's context)
  Exit code 0 = pass through
"""
import json
import sys
import time
from pathlib import Path

# Shared utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.constants import SESSION_DATA_DIR
from utils.stdin_parser import parse_hook_input, get_session_id


def load_session(session_id: str) -> dict:
    """Load session JSON. Returns empty dict on failure."""
    session_file = SESSION_DATA_DIR / f"{session_id}.json"
    try:
        if session_file.exists():
            return json.loads(session_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def save_session(session_id: str, data: dict) -> None:
    """Save session JSON."""
    SESSION_DATA_DIR.mkdir(parents=True, exist_ok=True)
    session_file = SESSION_DATA_DIR / f"{session_id}.json"
    try:
        session_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except OSError:
        pass


def main():
    # Parse CLI flags
    flags = set(sys.argv[1:])
    do_log = "--log-only" in flags
    do_store = "--store-last-prompt" in flags
    do_name = "--name-agent" in flags
    do_validate = "--validate" in flags

    input_data = parse_hook_input()
    prompt = input_data.get("prompt", "")
    session_id = get_session_id(input_data)

    # --- Validation (exit 2 to block) ---
    if do_validate:
        if not prompt.strip():
            print("Empty prompt rejected. Please enter a message.", file=sys.stderr)
            sys.exit(2)

    # --- Load session data ---
    session_data = load_session(session_id)
    if not session_data:
        # Session not initialized yet (SessionStart may not have run)
        session_data = {
            "session_id": session_id,
            "started_at": time.time(),
            "last_seen": time.time(),
            "prompts": [],
        }

    # --- Log prompt ---
    if do_log:
        session_data.setdefault("prompts", []).append({
            "text": prompt[:500],  # Cap at 500 chars for storage
            "timestamp": time.time(),
        })

    # --- Store last prompt ---
    if do_store:
        session_data["last_prompt"] = prompt[:500]

    # --- Agent naming (first prompt only) ---
    if do_name and not session_data.get("agent_name"):
        try:
            from utils.llm.anthropic_client import get_agent_name
            agent_name = get_agent_name(prompt[:200])
            session_data["agent_name"] = agent_name
        except Exception:
            import random
            session_data["agent_name"] = f"agent-{random.randint(1000, 9999)}"

    # --- Update last_seen ---
    session_data["last_seen"] = time.time()

    # --- Save ---
    save_session(session_id, session_data)


if __name__ == "__main__":
    main()
