#!/usr/bin/env python3
"""
Shared constants for all hooks.

Import via sys.path injection:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from utils.constants import PROJECT_DIR, ENGINEER_NAME, LLM_MODEL
"""
import os
from pathlib import Path


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))
SESSION_DATA_DIR = PROJECT_DIR / ".claude" / "data" / "sessions"
SESSION_STATE_DIR = PROJECT_DIR / ".claude" / "session"
HOOKS_DIR = PROJECT_DIR / ".claude" / "hooks"
TTS_QUEUE_DIR = PROJECT_DIR / ".claude" / "data" / "tts_queue"

# ---------------------------------------------------------------------------
# External configuration
# ---------------------------------------------------------------------------
ENGINEER_NAME = os.environ.get("ENGINEER_NAME", "Developer")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ---------------------------------------------------------------------------
# LLM defaults (Anthropic haiku — cheapest model, cost-guarded)
# ---------------------------------------------------------------------------
LLM_MODEL = "claude-3-5-haiku-20241022"
LLM_MAX_TOKENS = 100
LLM_TEMPERATURE = 0.7

# ---------------------------------------------------------------------------
# TTS defaults (pyttsx3)
# ---------------------------------------------------------------------------
TTS_RATE = 180      # words per minute
TTS_VOLUME = 0.8    # 0.0 to 1.0

# ---------------------------------------------------------------------------
# Session defaults
# ---------------------------------------------------------------------------
STALE_LOCK_SECONDS = 60.0       # locks older than this are considered stale
TTS_LOCK_TIMEOUT = 30.0         # max seconds to wait for TTS lock
PERSONALIZATION_CHANCE = 0.3    # probability of using ENGINEER_NAME in messages
