#!/usr/bin/env python3
"""
Anthropic API wrapper for hook-time LLM calls.

Uses claude-3-5-haiku exclusively. All calls are cost-guarded:
  - max_tokens <= 100
  - temperature 0.7
  - Estimated cost: ~$0.001 per call

Graceful degradation: returns None / static fallback if API key is missing
or the anthropic SDK is not installed.

Import via sys.path injection:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from utils.llm.anthropic_client import get_completion, get_agent_name
"""
import os
import random
import sys
from pathlib import Path

# Ensure parent utils package is importable
_utils_dir = str(Path(__file__).resolve().parent.parent)
if _utils_dir not in sys.path:
    sys.path.insert(0, _utils_dir)

# Graceful import — anthropic SDK is optional
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Import shared constants (single source of truth)
from constants import LLM_MODEL as MODEL, LLM_MAX_TOKENS as MAX_TOKENS, LLM_TEMPERATURE as TEMPERATURE

# ---------------------------------------------------------------------------
# Wordlist fallback for agent naming (zero-cost, zero-latency)
# ---------------------------------------------------------------------------
ADJECTIVES = [
    "swift", "bright", "bold", "calm", "keen", "sage", "true", "warm",
    "clear", "sharp", "deep", "fair", "free", "glad", "pure", "rare",
]
NOUNS = [
    "phoenix", "cipher", "nexus", "pulse", "forge", "prism", "atlas", "spark",
    "crest", "drift", "gleam", "haven", "orbit", "quest", "ridge", "valor",
]

# Static completion messages (fallback when LLM unavailable)
STATIC_COMPLETIONS = [
    "Work complete!",
    "All done!",
    "Task finished!",
    "Ready for next task!",
    "Mission accomplished!",
    "Done and dusted!",
    "That's a wrap!",
    "Finished up!",
]


def get_completion(prompt: str, max_tokens: int = MAX_TOKENS) -> str | None:
    """
    Get a haiku completion. Returns None on any failure.

    This is the core LLM call — all other functions build on it.
    """
    if not ANTHROPIC_AVAILABLE:
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None

    try:
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            temperature=TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()
    except Exception:
        return None


def get_agent_name(session_context: str = "") -> str:
    """
    Generate a session codename. Anthropic haiku -> wordlist fallback.

    Returns a single word (LLM) or "adjective-noun" pair (fallback).
    """
    result = get_completion(
        "Generate a single abstract one-word codename for a coding session "
        "(like Phoenix, Cipher, Nova, Horizon, Prism). "
        f"Context: {session_context[:200]}. "
        "Reply with ONLY the single word, nothing else."
    )

    # Validate: must be a single alphabetic word, 3-20 chars
    if result and len(result.split()) == 1 and result.isalpha() and 3 <= len(result) <= 20:
        return result.capitalize()

    # Fallback: deterministic-ish wordlist combinator
    return f"{random.choice(ADJECTIVES)}-{random.choice(NOUNS)}"


def get_completion_message(engineer_name: str = "Developer") -> str:
    """
    Generate a friendly work completion message. LLM -> static fallback.

    30% chance of including the engineer's name for personalization.
    """
    use_name = random.random() < 0.3
    name_hint = f" Address {engineer_name} by name." if use_name else ""

    result = get_completion(
        f"Generate a friendly work completion message under 10 words.{name_hint} "
        "Reply with ONLY the message, no quotes."
    )

    if result and len(result) < 80:
        return result

    return random.choice(STATIC_COMPLETIONS)


def is_available() -> bool:
    """Check if the Anthropic SDK is installed and an API key is present."""
    return ANTHROPIC_AVAILABLE and bool(os.environ.get("ANTHROPIC_API_KEY", ""))
