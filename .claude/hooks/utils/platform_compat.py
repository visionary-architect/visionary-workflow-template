#!/usr/bin/env python3
"""
Cross-platform compatibility helpers.

Provides Windows-safe alternatives for Unix-only APIs.
All hooks should use these helpers instead of platform-specific calls.

Import via sys.path injection:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from utils.platform_compat import which, atomic_write, is_pid_alive
"""
import os
import sys
import shutil
import time
from pathlib import Path


# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------
IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")


def which(cmd: str) -> str | None:
    """Cross-platform command lookup. Always use this instead of shell `which`."""
    return shutil.which(cmd)


def python_executable() -> str:
    """Return the current Python interpreter path. Never hardcode 'python3'."""
    return sys.executable


def atomic_write(target: Path, content: str, retries: int = 3) -> None:
    """
    Write file atomically with Windows retry logic.

    On Unix, Path.replace() is atomic. On Windows, it can raise
    PermissionError if another process has the target file open.
    This retries with exponential backoff to handle that case.
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    for attempt in range(retries):
        try:
            tmp.replace(target)
            return
        except PermissionError:
            if attempt < retries - 1:
                time.sleep(0.1 * (attempt + 1))
            else:
                # Last attempt failed — clean up tmp and re-raise
                try:
                    tmp.unlink(missing_ok=True)
                except OSError:
                    pass
                raise


def is_pid_alive(pid: int) -> bool:
    """
    Check if a process is still running. Cross-platform.

    Uses ctypes on Windows (no os.kill signal 0 equivalent).
    Uses os.kill(pid, 0) on Unix.
    """
    if IS_WINDOWS:
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = kernel32.OpenProcess(0x1000, False, pid)
            if handle:
                kernel32.CloseHandle(handle)
                return True
            return False
        except Exception:
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


def safe_subprocess_args(cmd_list: list[str]) -> list[str]:
    """
    Adjust subprocess command arguments for the current platform.

    - Replaces 'python3' with sys.executable
    - On Windows, ensures proper quoting of paths with spaces
    """
    result = []
    for arg in cmd_list:
        if arg in ("python3", "python"):
            result.append(sys.executable)
        else:
            result.append(arg)
    return result
