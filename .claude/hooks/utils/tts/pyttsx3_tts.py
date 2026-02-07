#!/usr/bin/env python3
"""
pyttsx3 TTS wrapper with graceful degradation.

Can be used as:
  1. Imported function:  from utils.tts.pyttsx3_tts import speak
  2. CLI subprocess:     python pyttsx3_tts.py "Hello world"

If pyttsx3 is not installed, all calls silently return False.
"""
import sys

# Graceful import — TTS is optional
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


_engine = None


def _get_engine():
    """Get or create the singleton pyttsx3 engine."""
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
    return _engine


def speak(text: str, rate: int = 180, volume: float = 0.8) -> bool:
    """
    Speak text via pyttsx3.

    Args:
        text: Text to speak
        rate: Words per minute (default: 180)
        volume: Volume level 0.0-1.0 (default: 0.8)

    Returns:
        True if spoken successfully, False if degraded/failed.
    """
    if not TTS_AVAILABLE or not text:
        return False
    try:
        engine = _get_engine()
        engine.setProperty("rate", rate)
        engine.setProperty("volume", volume)
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception:
        return False


def is_available() -> bool:
    """Check if TTS is available."""
    return TTS_AVAILABLE


# ---------------------------------------------------------------------------
# CLI mode: python pyttsx3_tts.py "text to speak"
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not text:
        print("Usage: python pyttsx3_tts.py <text>", file=sys.stderr)
        sys.exit(1)
    success = speak(text)
    sys.exit(0 if success else 1)
