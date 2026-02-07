#!/usr/bin/env python3
"""
Cross-platform TTS queue with file locking.

Prevents audio overlap when multiple subagents try to speak simultaneously.
Uses fcntl on Unix and msvcrt on Windows for cross-process locking.

Import via sys.path injection:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from utils.tts.tts_queue import acquire_tts_lock, release_tts_lock, cleanup_stale_locks
"""
import json
import os
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Platform-specific locking
# ---------------------------------------------------------------------------
_IS_WINDOWS = sys.platform == "win32"

if _IS_WINDOWS:
    import msvcrt
else:
    import fcntl

# ---------------------------------------------------------------------------
# Paths (relative to project root)
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))
LOCK_DIR = _PROJECT_ROOT / ".claude" / "data" / "tts_queue"
LOCK_FILE = LOCK_DIR / "tts.lock"
LOCK_INFO_FILE = LOCK_DIR / "tts_lock_info.json"

# ---------------------------------------------------------------------------
# Global lock state
# ---------------------------------------------------------------------------
_lock_fd = None


def _ensure_lock_dir() -> None:
    """Create the lock directory if it doesn't exist."""
    LOCK_DIR.mkdir(parents=True, exist_ok=True)


def _write_lock_info(agent_id: str) -> None:
    """Write lock owner info for stale detection."""
    try:
        LOCK_INFO_FILE.write_text(
            json.dumps({
                "agent_id": agent_id,
                "pid": os.getpid(),
                "timestamp": time.time(),
            }),
            encoding="utf-8",
        )
    except OSError:
        pass


def _read_lock_info() -> dict:
    """Read lock info. Returns empty dict on failure."""
    try:
        if LOCK_INFO_FILE.exists():
            return json.loads(LOCK_INFO_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def _clear_lock_info() -> None:
    """Clear the lock info file."""
    try:
        LOCK_INFO_FILE.write_text("{}", encoding="utf-8")
    except OSError:
        pass


def acquire_tts_lock(agent_id: str = "main", timeout: float = 30.0) -> bool:
    """
    Acquire cross-process TTS lock with exponential backoff.

    Args:
        agent_id: Identifier of the agent acquiring the lock.
        timeout: Maximum seconds to wait for the lock.

    Returns:
        True if lock acquired, False if timed out.
    """
    global _lock_fd
    _ensure_lock_dir()

    deadline = time.monotonic() + timeout
    backoff = 0.1  # start at 100ms

    while time.monotonic() < deadline:
        fd = None
        try:
            fd = os.open(str(LOCK_FILE), os.O_RDWR | os.O_CREAT)

            if _IS_WINDOWS:
                # msvcrt.locking locks byte ranges — seek to start, lock 1 byte
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                # fcntl.flock locks the entire file descriptor
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

            # Lock acquired
            _lock_fd = fd
            _write_lock_info(agent_id)
            return True

        except (OSError, IOError):
            # Lock held by another process — close fd and retry
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
            time.sleep(backoff)
            backoff = min(backoff * 1.5, 1.0)  # cap at 1 second

    return False


def release_tts_lock(agent_id: str = "main") -> None:
    """
    Release the TTS lock.

    Args:
        agent_id: Identifier of the agent releasing the lock.
    """
    global _lock_fd

    if _lock_fd is not None:
        try:
            if _IS_WINDOWS:
                # Seek to beginning before unlocking
                os.lseek(_lock_fd, 0, os.SEEK_SET)
                msvcrt.locking(_lock_fd, msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(_lock_fd, fcntl.LOCK_UN)
            os.close(_lock_fd)
        except OSError:
            pass
        _lock_fd = None

    _clear_lock_info()


def cleanup_stale_locks(max_age_seconds: float = 60.0) -> bool:
    """
    Remove stale locks from dead processes.

    A lock is considered stale if:
      1. The lock info file is older than max_age_seconds, AND
      2. The owning process (PID) is no longer alive.

    Args:
        max_age_seconds: Threshold in seconds for stale detection.

    Returns:
        True if a stale lock was cleaned up.
    """
    # Import here to avoid circular dependency
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from platform_compat import is_pid_alive

    info = _read_lock_info()
    if not info:
        return False

    timestamp = info.get("timestamp", 0)
    pid = info.get("pid", 0)
    age = time.time() - timestamp

    if age < max_age_seconds:
        return False  # Not stale yet

    if pid and is_pid_alive(pid):
        return False  # Process still alive — lock is valid

    # Stale lock — clean up
    try:
        LOCK_FILE.unlink(missing_ok=True)
    except OSError:
        pass
    _clear_lock_info()
    return True


def speak_with_lock(
    text: str,
    agent_id: str = "main",
    timeout: float = 30.0,
    rate: int = 180,
    volume: float = 0.8,
) -> bool:
    """
    Convenience: acquire lock, speak, release.

    Cleans up stale locks before attempting to acquire.

    Args:
        text: Text to speak.
        agent_id: Identifier for lock ownership.
        timeout: Max seconds to wait for lock.
        rate: TTS words per minute.
        volume: TTS volume (0.0-1.0).

    Returns:
        True if spoken successfully, False otherwise.
    """
    # Robust import — ensure utils/ is on sys.path regardless of call context
    _utils_dir = str(Path(__file__).resolve().parent.parent)
    if _utils_dir not in sys.path:
        sys.path.insert(0, _utils_dir)
    from tts.pyttsx3_tts import speak

    cleanup_stale_locks()

    if acquire_tts_lock(agent_id, timeout):
        try:
            return speak(text, rate=rate, volume=volume)
        finally:
            release_tts_lock(agent_id)
    else:
        # Timeout — try speaking anyway (may overlap, better than silence)
        return speak(text, rate=rate, volume=volume)
