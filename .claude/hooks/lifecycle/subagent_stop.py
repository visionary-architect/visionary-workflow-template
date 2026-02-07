#!/usr/bin/env python3
"""
SubagentStop lifecycle hook — TTS summary and audit logging.

Fires on: SubagentStop
Sync: NO (async — TTS is fire-and-forget)

CLI flags:
  --notify      Speak summary via TTS
  --summarize   Use LLM to summarize what the subagent did

What it does:
1. Read subagent transcript from agent_transcript_path
2. Extract task context (first user prompt)
3. Summarize via task_summarizer (Anthropic haiku -> truncation fallback)
4. Speak summary via TTS queue
5. Update session JSON subagent entry with completion data
"""
import json
import sys
import time
from pathlib import Path

# Shared utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.constants import (
    SESSION_DATA_DIR, TTS_RATE, TTS_VOLUME, TTS_LOCK_TIMEOUT,
)
from utils.stdin_parser import parse_hook_input, get_session_id


def update_subagent_completion(
    session_id: str, agent_id: str, summary: str
) -> None:
    """Mark subagent as completed in session JSON."""
    session_file = SESSION_DATA_DIR / f"{session_id}.json"
    try:
        if not session_file.exists():
            return
        data = json.loads(session_file.read_text(encoding="utf-8"))

        # Find and update the matching subagent entry
        for entry in data.get("subagents", []):
            if entry.get("agent_id") == agent_id and entry.get("completed_at") is None:
                entry["completed_at"] = time.time()
                entry["summary"] = summary
                break

        # Update active count
        active = sum(
            1 for s in data.get("subagents", []) if s.get("completed_at") is None
        )
        data["active_subagents"] = active

        session_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except (json.JSONDecodeError, OSError):
        pass


def main():
    flags = set(sys.argv[1:])
    do_notify = "--notify" in flags
    do_summarize = "--summarize" in flags

    input_data = parse_hook_input()
    session_id = get_session_id(input_data)
    agent_id = input_data.get("agent_id", "unknown")
    agent_type = input_data.get("agent_type", "unknown")
    transcript_path = input_data.get("agent_transcript_path", "")

    # --- Extract and summarize ---
    summary = "Subagent completed."

    if do_summarize and transcript_path:
        try:
            from utils.llm.task_summarizer import extract_task_context, summarize_task
            context = extract_task_context(transcript_path)
            if context:
                summary = summarize_task(context)
        except Exception:
            pass

    # --- Update session JSON ---
    update_subagent_completion(session_id, agent_id, summary)

    # --- TTS notification ---
    if do_notify:
        speak_text = f"{agent_type} agent finished. {summary}"
        try:
            from utils.tts.tts_queue import speak_with_lock
            speak_with_lock(
                text=speak_text,
                agent_id=f"subagent-{agent_id[:8]}",
                timeout=TTS_LOCK_TIMEOUT,
                rate=TTS_RATE,
                volume=TTS_VOLUME,
            )
        except Exception:
            pass

    # Debug log
    print(
        f"Subagent stopped: {agent_type} ({agent_id[:12]}...) — {summary}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
