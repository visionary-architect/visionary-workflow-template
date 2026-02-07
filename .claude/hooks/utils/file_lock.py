#!/usr/bin/env python3
"""
Cross-platform file locking for safe JSON read-modify-write operations.

Prevents race conditions when multiple Claude Code sessions concurrently
modify shared JSON files (sessions.json, task_locks.json, file_locks.json,
work_queue.json, event_state.json).

Usage (single file):
    from utils.file_lock import locked_json_rw

    with locked_json_rw(SESSIONS_FILE, default={}) as (data, save):
        data["new_key"] = "value"
        save(data)  # atomic write; skip save() to discard changes

Usage (multiple files):
    from utils.file_lock import locked_multi_json_rw

    with locked_multi_json_rw(
        (LOCKS_FILE, {}), (SESSIONS_FILE, {})
    ) as entries:
        locks, save_locks = entries[0]
        sessions, save_sessions = entries[1]
        # ... modify both ...
        save_locks(locks)
        save_sessions(sessions)
"""
import json
import os
import sys
import time
from contextlib import contextmanager
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
# Low-level lock acquire / release
# ---------------------------------------------------------------------------

def _acquire_lock(lock_path: Path, timeout: float = 4.0) -> int | None:
    """
    Acquire an OS-level file lock with exponential backoff.

    Returns the file descriptor on success, or None on timeout (fail-open).
    """
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout
    backoff = 0.05  # start at 50ms

    while time.monotonic() < deadline:
        fd = None
        try:
            fd = os.open(str(lock_path), os.O_RDWR | os.O_CREAT)

            if _IS_WINDOWS:
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

            return fd  # lock acquired

        except (OSError, IOError):
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
            time.sleep(backoff)
            backoff = min(backoff * 1.5, 1.0)

    # Timeout — fail open
    print(f"Warning: Could not acquire lock on {lock_path} within {timeout}s, proceeding without lock")
    return None


def _release_lock(fd: int | None) -> None:
    """Release a previously acquired file lock."""
    if fd is None:
        return
    try:
        if _IS_WINDOWS:
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# JSON read helpers
# ---------------------------------------------------------------------------

def _read_json(path: Path, default):
    """Read a JSON file, returning default on any error."""
    if not path.exists():
        return default() if callable(default) else (default.copy() if isinstance(default, (dict, list)) else default)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default() if callable(default) else (default.copy() if isinstance(default, (dict, list)) else default)


def _write_json(path: Path, data) -> None:
    """Write JSON atomically via temp file + replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_file = path.with_suffix(".tmp")
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        temp_file.replace(path)
    except Exception as e:
        print(f"Warning: Failed to write {path}: {e}")
        if temp_file.exists():
            temp_file.unlink()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@contextmanager
def locked_json_rw(path: Path, default=None, timeout: float = 4.0):
    """
    Context manager for locked JSON read-modify-write.

    Acquires an OS-level lock, reads the JSON file, and yields (data, save).
    Call save(data) to write back; if save() is never called, no write occurs.

    Args:
        path: Path to the JSON file.
        default: Default value if file doesn't exist (dict, list, or callable).
        timeout: Max seconds to wait for lock. Fails open on timeout.

    Yields:
        (data, save) — data is the parsed JSON; save is a callable to write back.
    """
    if default is None:
        default = {}

    lock_path = path.with_name(path.name + ".lock")
    fd = _acquire_lock(lock_path, timeout)

    try:
        data = _read_json(path, default)
        written = False

        def save(new_data):
            nonlocal written
            _write_json(path, new_data)
            written = True

        yield data, save
    finally:
        _release_lock(fd)


@contextmanager
def locked_multi_json_rw(*file_specs, timeout: float = 4.0):
    """
    Context manager for locked multi-file JSON read-modify-write.

    Acquires locks on all files in sorted path order (prevents deadlocks),
    reads each, and yields a list of (data, save) tuples.

    Args:
        *file_specs: Each is (path, default) — a Path and its default value.
        timeout: Max seconds to wait for each lock.

    Yields:
        List of (data, save) tuples, one per file_spec (in original order).
    """
    # Sort by path for consistent lock ordering, but track original indices
    indexed_specs = list(enumerate(file_specs))
    sorted_specs = sorted(indexed_specs, key=lambda x: str(x[1][0]))

    fds = []
    try:
        # Acquire all locks in sorted order
        for _, (path, _default) in sorted_specs:
            lock_path = path.with_name(path.name + ".lock")
            fd = _acquire_lock(lock_path, timeout)
            fds.append(fd)

        # Read all files (in original order for caller convenience)
        results = []
        for path, default in file_specs:
            if default is None:
                default = {}
            data = _read_json(path, default)

            def make_save(p):
                def save(new_data):
                    _write_json(p, new_data)
                return save

            results.append((data, make_save(path)))

        yield results

    finally:
        # Release all locks in reverse acquisition order
        for fd in reversed(fds):
            _release_lock(fd)
