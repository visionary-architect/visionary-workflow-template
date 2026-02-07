#!/usr/bin/env python3
"""
Notification lifecycle hook — TTS announcements for notifications.

Fires on: Notification (notification_type: permission_prompt/idle_prompt/auth_success/elicitation_dialog)
Sync: NO (async — TTS is fire-and-forget, cannot block notifications)

What it does:
1. Read notification message from stdin
2. Personalize: 30% chance of prepending ENGINEER_NAME
3. Speak via TTS queue (acquire lock, speak, release)
4. Log to session JSON notifications array
"""
import json
import random
import sys
import time
from pathlib import Path

# Shared utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.constants import (
    SESSION_DATA_DIR, ENGINEER_NAME, PERSONALIZATION_CHANCE,
    TTS_RATE, TTS_VOLUME, TTS_LOCK_TIMEOUT,
)
from utils.stdin_parser import parse_hook_input, get_session_id


def log_notification(session_id: str, message: str, notification_type: str) -> None:
    """Append notification to session JSON."""
    session_file = SESSION_DATA_DIR / f"{session_id}.json"
    try:
        if session_file.exists():
            data = json.loads(session_file.read_text(encoding="utf-8"))
        else:
            data = {"session_id": session_id, "notifications": []}

        data.setdefault("notifications", []).append({
            "message": message[:200],
            "type": notification_type,
            "timestamp": time.time(),
        })
        session_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except (json.JSONDecodeError, OSError):
        pass


def speak_notification(message: str, session_id: str) -> None:
    """Speak the notification via TTS queue."""
    try:
        from utils.tts.tts_queue import speak_with_lock
        speak_with_lock(
            text=message,
            agent_id=f"notification-{session_id[:8]}",
            timeout=TTS_LOCK_TIMEOUT,
            rate=TTS_RATE,
            volume=TTS_VOLUME,
        )
    except Exception:
        pass


def main():
    input_data = parse_hook_input()
    message = input_data.get("message", "")
    title = input_data.get("title", "")
    notification_type = input_data.get("notification_type", "unknown")
    session_id = get_session_id(input_data)

    if not message:
        return

    # Personalize: 30% chance of prepending engineer name
    speak_text = message
    if random.random() < PERSONALIZATION_CHANCE and ENGINEER_NAME != "Developer":
        speak_text = f"{ENGINEER_NAME}, {message}"

    # Add title prefix if present
    if title:
        speak_text = f"{title}: {speak_text}"

    # Speak via TTS
    speak_notification(speak_text, session_id)

    # Log to session JSON
    log_notification(session_id, message, notification_type)


if __name__ == "__main__":
    main()
