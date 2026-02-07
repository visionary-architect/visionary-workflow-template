# Hooks-Mastery → Visionary Template Integration Plan

> **Created:** 2026-02-06
> **Revised:** 2026-02-06 (second-pass audit — 23 corrections applied)
> **Source:** 106-item capability catalog (Anthropic-only LLM, pyttsx3-only TTS)
> **Target:** visionary_template_1
> **Strategy:** Additive integration — preserve all existing visionary systems

---

## Second-Pass Audit: Issues Found & Resolved

Before the phase-by-phase plan, here are the 23 issues found during the second-pass review and how each was resolved:

| # | Finding | Severity | Resolution |
|---|---------|----------|------------|
| 1 | `Setup` is NOT an official Claude Code lifecycle event (only 12 exist, not 13) | **CRITICAL** | Removed Setup hook entirely; folded project detection + dep checking into SessionStart |
| 2 | PreToolUse uses `hookSpecificOutput.permissionDecision` (allow/deny/ask), NOT top-level `decision` | **CRITICAL** | Fixed all PreToolUse hook output specs |
| 3 | PermissionRequest uses `hookSpecificOutput.decision.behavior` (allow/deny), a THIRD distinct protocol | **CRITICAL** | Fixed PermissionRequest output spec |
| 4 | Async hooks CANNOT return decisions — stdout JSON is ignored until next turn | **CRITICAL** | Changed all decision-returning hooks to sync; added async/sync decision matrix |
| 5 | `UserPromptSubmit` and `Stop` do NOT support matchers (silently ignored) | **HIGH** | Removed matchers from these events in settings.json spec |
| 6 | Stop hook `stop_hook_active` field MUST be checked to prevent infinite loops | **HIGH** | Added guard clause requirement to all Stop hooks |
| 7 | Command-level Stop hook validators use exit code 1 to block (not exit code 2) | **HIGH** | Fixed validator exit code spec |
| 8 | PostToolUse validators use `{"decision":"block","reason":"..."}` — different from Stop validators `{"result":"block","reason":"..."}` | **HIGH** | Documented both protocols explicitly |
| 9 | StatusLine receives rich JSON on stdin (cost, context_window, model, etc.) — does NOT need session files | **HIGH** | Rewrote status line implementation approach |
| 10 | `__init__.py` files break visionary convention (hooks are standalone scripts) | **MEDIUM** | Replaced with `sys.path` injection pattern |
| 11 | `CLAUDE_ENV_FILE` only available in SessionStart hooks (not other events) | **MEDIUM** | Moved env persistence to SessionStart only |
| 12 | Visionary's existing hooks output plain text, not JSON — new hooks using JSON will be the first to do so | **MEDIUM** | Noted as deliberate protocol upgrade; documented both patterns |
| 13 | `fcntl` is Unix-only — TTS queue needs Windows-compatible locking | **MEDIUM** | Added cross-platform locking pattern with msvcrt + PID-based stale detection |
| 14 | `which` command doesn't exist on Windows — `session_start.py` must use `shutil.which()` | **MEDIUM** | Standardized on `shutil.which()` for all tool detection |
| 15 | `python3` doesn't exist on Windows — must use `python` or `sys.executable` | **MEDIUM** | Standardized on `sys.executable` for subprocess calls |
| 16 | `Path.replace()` can raise PermissionError on Windows when target is open | **MEDIUM** | Added retry-with-backoff pattern for atomic writes |
| 17 | warmup_cache.py conflict with SessionStart context injection — both try to inject context | **MEDIUM** | Separated concerns: SessionStart handles `additionalContext` JSON; warmup_cache handles file-based cache |
| 18 | Stop hook ordering — session_cleanup.py deletes session ID files; new hooks must run before it | **MEDIUM** | Specified exact insertion point in Stop hooks array |
| 19 | auto_devlog.py has same-day session marker bug (second session won't log) | **LOW** | Noted as pre-existing bug; fix included in Phase 9 |
| 20 | Multiple hooks write to sessions.json without cross-process locking (last writer wins) | **LOW** | Accepted: atomic write pattern prevents corruption; lost updates are recoverable |
| 21 | Timeout units: visionary uses milliseconds; documented "seconds" in some places | **LOW** | Standardized all timeout values to milliseconds |
| 22 | Hook handler types `prompt` and `agent` exist but plan only uses `command` | **LOW** | Noted as future enhancement opportunity; `command` type is correct for our needs |
| 23 | Subagent Stop hooks auto-convert to SubagentStop in agent frontmatter | **LOW** | Documented in Phase 6 command-level hooks section |

---

## Table of Contents

1. [Architecture Decisions](#architecture-decisions)
2. [Hook Protocol Reference](#hook-protocol-reference)
3. [Phase Overview](#phase-overview)
4. [Phase 0: Foundation Infrastructure](#phase-0-foundation-infrastructure)
5. [Phase 1: Utility Subsystems](#phase-1-utility-subsystems)
6. [Phase 2: Lifecycle Hook Expansion](#phase-2-lifecycle-hook-expansion)
7. [Phase 3: Status Line System](#phase-3-status-line-system)
8. [Phase 4: Output Styles](#phase-4-output-styles)
9. [Phase 5: Agent Enhancements](#phase-5-agent-enhancements)
10. [Phase 6: Command Enhancements](#phase-6-command-enhancements)
11. [Phase 7: Security & Validation Merge](#phase-7-security--validation-merge)
12. [Phase 8: Autonomous Behaviors](#phase-8-autonomous-behaviors)
13. [Phase 9: Polish & Documentation](#phase-9-polish--documentation)
14. [Catalog → Task Mapping](#catalog--task-mapping)
15. [Risk Register](#risk-register)

---

## Architecture Decisions

### AD-1: Script Format — Standard Python (NOT UV single-file)

**Decision:** Use standard Python scripts matching visionary's existing convention.

**Rationale:** Visionary has 17 hook scripts using `#!/usr/bin/env python3` with stdlib-only imports. The hooks-mastery `-S uv run --script` shebang doesn't work on Windows natively. We'll use standard Python invoked as `python .claude/hooks/...`. External deps (pyttsx3, anthropic) are installed once via pip/uv and imported with graceful fallback.

### AD-2: Hook Dispatch — Preserve Matcher-Based Routing

**Decision:** Keep visionary's granular matcher-based hook dispatch for tool events. New lifecycle events use omitted matchers (match all).

**Rationale:** Visionary routes `PostToolUse` to different validators based on `Write|Edit`, `Bash`, `TodoWrite` matchers. New lifecycle events like `SessionStart`, `Notification`, etc. don't need routing and will omit the `matcher` field (matches all). Two events (`UserPromptSubmit`, `Stop`) don't support matchers at all — any matcher specified is silently ignored.

### AD-3: Overlapping Features — Merge, Don't Duplicate

| Feature | Visionary Has | Hooks-Mastery Has | Resolution |
|---------|--------------|-------------------|------------|
| Dangerous command blocking | `dangerous_command_checker.py` (30+ patterns) | `pre_tool_use.py` (6 rm-rf patterns + .env blocking) | **Keep visionary's**, add .env blocking |
| Session management | Full multi-session coordinator (sessions.json) | `user_prompt_submit.py` session data (.claude/data/sessions/) | **Keep both** — different scopes. Visionary's manages multi-session coordination; new session JSON tracks per-session audit data |
| Commit validation | `commit_validator.py` (conventional + Co-Authored-By) | None | **Keep as-is** |
| Codebase indexing | `codebase_indexer.py` (634 lines, 8 parsers) | None | **Keep as-is** |
| File conflict detection | `file_conflict_checker.py` | None | **Keep as-is** |
| Context injection | `warmup_cache.py` writes `.claude/session/context_cache.json` | `session_start.py` outputs `additionalContext` JSON | **Complementary:** warmup_cache handles file-based context caching for fast resume; SessionStart handles `additionalContext` injection via Claude Code's official protocol. No conflict — they use different mechanisms |

### AD-4: TTS Dependency Strategy

**Decision:** pyttsx3 installed via `pip install pyttsx3`. Graceful degradation if unavailable.

**Pattern (used in ALL TTS-consuming hooks):**
```python
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    # Silently degrade — TTS is optional enhancement
```

### AD-5: LLM-in-Hooks Policy

**Decision:** Anthropic-only via `anthropic` SDK. Model: `claude-3-5-haiku-20241022`.

**Fallback chain:** Anthropic API → random wordlist (for naming) or static message (for completions).

**Cost guard:** All LLM calls use haiku, max_tokens ≤ 100, temperature 0.7.

### AD-6: Shared Utility Import Pattern (NO __init__.py)

**Decision:** Use `sys.path` injection, NOT Python packages with `__init__.py`.

**Rationale:** Visionary's hooks are standalone scripts invoked as separate processes. There are zero `__init__.py` files under `.claude/hooks/`. Adding them would break this convention. Instead, each hook that needs utilities does:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # adds .claude/hooks/
from utils.tts.pyttsx3_tts import speak       # now resolvable
from utils.llm.anthropic_client import get_completion
```

### AD-7: Cross-Platform Compatibility (Windows-First)

**Decision:** All hooks must work on Windows. Unix-only APIs get platform-aware fallbacks.

**Patterns:**

| Unix API | Windows Replacement | Implementation |
|----------|-------------------|----------------|
| `fcntl.flock()` | `msvcrt.locking()` | try/except ImportError with platform dispatch |
| `which` command | `shutil.which()` | Always use Python stdlib, never shell `which` |
| `python3` command | `sys.executable` | Always use `sys.executable` for subprocess Python calls |
| `os.kill(pid, 0)` for PID check | `ctypes.windll.kernel32.OpenProcess()` | Platform-aware PID liveness check |
| `Path.replace()` atomic write | Add retry loop with 100ms backoff | Handles Windows PermissionError when target is open |

### AD-8: Timeout Units — Milliseconds

**Decision:** All timeout values in settings.json are in **milliseconds**, matching visionary's existing convention.

**Evidence:** Visionary's current settings.json uses `"timeout": 5000` (5 seconds), `"timeout": 10000` (10 seconds), etc. The default Claude Code timeout is 600,000ms (10 minutes).

---

## Hook Protocol Reference

This section documents the EXACT stdin/stdout/exit-code protocol for each lifecycle event. Every hook implementation MUST follow these protocols precisely.

### Universal Stdin Fields (ALL events receive these)

```json
{
  "session_id": "string",
  "transcript_path": "string (path to conversation .jsonl)",
  "cwd": "string (current working directory)",
  "permission_mode": "default|plan|acceptEdits|dontAsk|bypassPermissions",
  "hook_event_name": "string (name of event that fired)"
}
```

### Universal Exit Code Behavior

| Exit Code | Meaning | Behavior |
|-----------|---------|----------|
| **0** | Success | stdout parsed for JSON; for SessionStart/UserPromptSubmit, plain text also added as context |
| **2** | Blocking error | stderr text fed back as error to Claude; stdout JSON IGNORED |
| **Other** | Non-blocking error | stderr shown in verbose mode only; execution continues |

### Universal JSON Output Fields (exit 0 only)

```json
{
  "continue": true,          // false = stop Claude entirely
  "stopReason": "message",   // shown to user when continue=false
  "suppressOutput": false,   // true = hide stdout from verbose mode
  "systemMessage": "warning" // warning shown to user
}
```

### Per-Event Protocol Matrix

| Event | Supports Matcher? | Matches On | Can Block? | Decision Protocol | Async Safe? |
|-------|-------------------|------------|------------|-------------------|-------------|
| `SessionStart` | YES | `source` (startup/resume/clear/compact) | NO | `hookSpecificOutput.additionalContext` | YES (but context delayed to next turn) |
| `UserPromptSubmit` | **NO** | — | YES (exit 2 erases prompt) | Top-level `decision: "block"` + `reason` | NO (must be sync to block) |
| `PreToolUse` | YES | `tool_name` | YES (exit 2 blocks tool) | `hookSpecificOutput.permissionDecision` (allow/deny/ask) | NO (must be sync to block) |
| `PermissionRequest` | YES | `tool_name` | YES (exit 2 denies) | `hookSpecificOutput.decision.behavior` (allow/deny) | NO (must be sync) |
| `PostToolUse` | YES | `tool_name` | NO (tool already ran) | Top-level `decision: "block"` + `reason` (tells Claude to fix) | YES for logging; NO for validators |
| `PostToolUseFailure` | YES | `tool_name` | NO | `hookSpecificOutput.additionalContext` | YES |
| `Notification` | YES | `notification_type` | NO | `hookSpecificOutput.additionalContext` | YES |
| `SubagentStart` | YES | `agent_type` | NO | `hookSpecificOutput.additionalContext` | YES |
| `SubagentStop` | YES | `agent_type` | YES (blocks subagent stop) | Top-level `decision: "block"` + `reason` | YES for TTS; NO for blocking |
| `Stop` | **NO** | — | YES (forces continuation) | Top-level `decision: "block"` + `reason` | NO (must be sync to block) |
| `PreCompact` | YES | `trigger` (manual/auto) | NO | Universal fields only | YES |
| `SessionEnd` | YES | `reason` | NO | None (cleanup only) | YES |

### Critical Protocol Details

**1. PreToolUse output format (DIFFERENT from other events):**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Read-only operation, auto-approved",
    "updatedInput": {},
    "additionalContext": ""
  }
}
```

**2. PermissionRequest output format (DIFFERENT from both PreToolUse and top-level):**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow",
      "updatedInput": {},
      "updatedPermissions": []
    }
  }
}
```
For deny: `{"behavior": "deny", "message": "reason", "interrupt": false}`

**3. PostToolUse validator output format:**
```json
{"decision": "block", "reason": "Lint check failed:\n<ruff output>"}
```
Or empty `{}` for pass.

**4. Command-level Stop hook validator format (DIFFERENT exit codes):**
```json
{"result": "block", "reason": "VALIDATION FAILED: missing required sections..."}
```
Exit code **1** = block (force Claude to continue and fix). Exit code **0** = pass.

**5. Stop hook infinite loop prevention:**
```python
input_data = json.load(sys.stdin)
if input_data.get("stop_hook_active", False):
    sys.exit(0)  # MUST exit cleanly to prevent infinite loop
```

**6. Async hooks CANNOT return decisions:**
When `"async": true`, the hook runs in background. By the time it completes, the triggering action has already proceeded. Fields like `decision`, `permissionDecision`, `continue` have **no effect**. Only `systemMessage` and `additionalContext` are delivered (on the next turn).

---

## Phase Overview

| Phase | Name | New Files | Modified Files | Catalog Items | Depends On |
|-------|------|-----------|----------------|---------------|------------|
| 0 | Foundation Infrastructure | 6 | 2 | 6 | — |
| 1 | Utility Subsystems | 4 | 0 | 8 | Phase 0 |
| 2 | Lifecycle Hook Expansion | 9 | 1 | 26 | Phase 0, 1 |
| 3 | Status Line System | 8 | 1 | 10 | Phase 0 |
| 4 | Output Styles | 8 | 0 | 8 | — |
| 5 | Agent Enhancements | 6 | 0 | 16 | Phase 1, 2 |
| 6 | Command Enhancements | 7 | 0 | 14 | Phase 2, 5 |
| 7 | Security & Validation Merge | 2 | 2 | 8 | Phase 2 |
| 8 | Autonomous Behaviors | 1 | 1 | 18 | Phase 1, 2 |
| 9 | Polish & Documentation | 2 | 4 | ~6 | All |
| **Total** | | **~53** | **~11** | **106** | |

**Critical Path:** Phase 0 → Phase 1 → Phase 2 → Phase 5 → Phase 6 → Phase 9

**Parallelizable:** Phase 3, Phase 4, and Phase 7 can run in parallel after Phase 0.

---

## Phase 0: Foundation Infrastructure

**Goal:** Create directory structure, env template, shared utilities scaffolding, and cross-platform helpers.

### Task 0-1: Create new directories

```
.claude/hooks/lifecycle/
.claude/hooks/utils/
.claude/hooks/utils/tts/
.claude/hooks/utils/llm/
.claude/output-styles/
.claude/status_lines/
.claude/data/sessions/
.claude/agents/team/
```

### Task 0-2: Create .env.sample

```env
# Required for LLM-in-hooks features (agent naming, completion messages, task summaries)
ANTHROPIC_API_KEY=sk-ant-...

# Your name (used in TTS greetings and personalized notifications)
ENGINEER_NAME=Developer

# Optional: for meta-agent web scraping of Anthropic docs
FIRECRAWL_API_KEY=
```

### Task 0-3: Create shared constants module

**File:** `.claude/hooks/utils/constants.py`

```python
"""Shared constants for all hooks. Import via sys.path injection."""
import os
import sys
from pathlib import Path

# Project root detection
PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))
SESSION_DATA_DIR = PROJECT_DIR / ".claude" / "data" / "sessions"
SESSION_STATE_DIR = PROJECT_DIR / ".claude" / "session"
HOOKS_DIR = PROJECT_DIR / ".claude" / "hooks"

# External config
ENGINEER_NAME = os.environ.get("ENGINEER_NAME", "Developer")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# LLM defaults
LLM_MODEL = "claude-3-5-haiku-20241022"
LLM_MAX_TOKENS = 100
LLM_TEMPERATURE = 0.7

# TTS defaults
TTS_RATE = 180
TTS_VOLUME = 0.8
```

### Task 0-4: Create cross-platform helpers module

**File:** `.claude/hooks/utils/platform_compat.py`

```python
"""Cross-platform compatibility helpers."""
import os
import sys
import shutil
import time
from pathlib import Path

# Platform detection
IS_WINDOWS = sys.platform == "win32"

def which(cmd: str) -> str | None:
    """Cross-platform command lookup. Never use shell `which`."""
    return shutil.which(cmd)

def python_executable() -> str:
    """Always use sys.executable, never hardcode python3."""
    return sys.executable

def atomic_write(target: Path, content: str, retries: int = 3) -> None:
    """Write file atomically with Windows retry logic."""
    tmp = target.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    for attempt in range(retries):
        try:
            tmp.replace(target)
            return
        except PermissionError:
            if attempt < retries - 1:
                time.sleep(0.1 * (attempt + 1))
            else:
                raise

def is_pid_alive(pid: int) -> bool:
    """Check if a process is still running. Cross-platform."""
    if IS_WINDOWS:
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
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
```

### Task 0-5: Create stdin parser utility

**File:** `.claude/hooks/utils/stdin_parser.py`

```python
"""Standardized stdin JSON parsing for all hooks."""
import json
import sys

def parse_hook_input() -> dict:
    """Read and parse JSON from stdin. Returns empty dict on failure."""
    try:
        data = sys.stdin.read()
        if data.strip():
            return json.loads(data)
    except (json.JSONDecodeError, EOFError, OSError):
        pass
    return {}
```

### Task 0-6: Update .gitignore

Add to `.gitignore`:
```
.claude/data/sessions/*.json
.claude/data/tts_queue/
.claude/session/
.claude/hooks/**/__pycache__/
*.lock
```

**Estimated effort:** Small — 6 files, ~200 lines total.

---

## Phase 1: Utility Subsystems

**Goal:** Build the TTS and LLM utility modules that hooks in Phase 2+ depend on.

### Task 1-1: Create pyttsx3 TTS wrapper

**File:** `.claude/hooks/utils/tts/pyttsx3_tts.py`

```python
"""pyttsx3 TTS wrapper with graceful degradation."""
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

def speak(text: str, rate: int = 180, volume: float = 0.8) -> bool:
    """Speak text via pyttsx3. Returns True if spoken, False if degraded."""
    if not TTS_AVAILABLE or not text:
        return False
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', rate)
        engine.setProperty('volume', volume)
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception:
        return False
```

- Callable as a function (imported via sys.path) OR as a subprocess (`python pyttsx3_tts.py "text"`)
- Returns boolean success indicator
- Never raises — always gracefully degrades

### Task 1-2: Create TTS queue with cross-platform file locking

**File:** `.claude/hooks/utils/tts/tts_queue.py`

Cross-platform locking strategy:
```python
import os
import sys
import time
import json
from pathlib import Path

# Platform-specific locking
_IS_WINDOWS = sys.platform == "win32"
if _IS_WINDOWS:
    import msvcrt
else:
    import fcntl

LOCK_DIR = Path(".claude/data/tts_queue")
LOCK_FILE = LOCK_DIR / "tts.lock"
LOCK_INFO_FILE = LOCK_DIR / "tts_lock_info.json"

_lock_fd = None

def acquire_tts_lock(agent_id: str = "main", timeout: float = 30.0) -> bool:
    """Acquire cross-process TTS lock. Returns True on success."""
    global _lock_fd
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout
    backoff = 0.1

    while time.monotonic() < deadline:
        try:
            fd = os.open(str(LOCK_FILE), os.O_RDWR | os.O_CREAT)
            if _IS_WINDOWS:
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            _lock_fd = fd
            # Write lock info
            LOCK_INFO_FILE.write_text(json.dumps({
                "agent_id": agent_id,
                "pid": os.getpid(),
                "timestamp": time.time()
            }))
            return True
        except (OSError, IOError):
            try:
                os.close(fd)
            except Exception:
                pass
            time.sleep(backoff)
            backoff = min(backoff * 1.5, 1.0)

    return False

def release_tts_lock(agent_id: str = "main") -> None:
    """Release TTS lock."""
    global _lock_fd
    if _lock_fd is not None:
        try:
            if _IS_WINDOWS:
                msvcrt.locking(_lock_fd, msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(_lock_fd, fcntl.LOCK_UN)
            os.close(_lock_fd)
        except Exception:
            pass
        _lock_fd = None
    # Clear lock info
    try:
        LOCK_INFO_FILE.write_text("{}")
    except Exception:
        pass

def cleanup_stale_locks(max_age_seconds: float = 60.0) -> None:
    """Remove stale locks from dead processes."""
    # Uses platform_compat.is_pid_alive() for cross-platform PID checking
    ...
```

- **Exponential backoff:** 100ms → 150ms → 225ms → ... → cap at 1000ms
- **Stale lock detection:** Check lock info file age + PID liveness
- **Windows `msvcrt.locking()`** locks byte ranges (we lock 1 byte)
- **Unix `fcntl.flock()`** locks the entire file descriptor

### Task 1-3: Create Anthropic LLM client wrapper

**File:** `.claude/hooks/utils/llm/anthropic_client.py`

```python
"""Anthropic API wrapper for hook-time LLM calls. Haiku only, cost-guarded."""
import os
import random

# Graceful import
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

MODEL = "claude-3-5-haiku-20241022"
MAX_TOKENS = 100

# Wordlist fallback for agent naming
ADJECTIVES = ["swift", "bright", "bold", "calm", "keen", "sage", "true", "warm"]
NOUNS = ["phoenix", "cipher", "nexus", "pulse", "forge", "prism", "atlas", "spark"]

def get_completion(prompt: str, max_tokens: int = MAX_TOKENS) -> str | None:
    """Get haiku completion. Returns None on any failure."""
    if not ANTHROPIC_AVAILABLE:
        return None
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    try:
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model=MODEL, max_tokens=max_tokens, temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text.strip()
    except Exception:
        return None

def get_agent_name(session_context: str = "") -> str:
    """Generate agent codename. Anthropic → wordlist fallback."""
    result = get_completion(
        f"Generate a single abstract one-word codename (like Phoenix, Cipher, Nova). "
        f"Context: {session_context[:200]}. Reply with ONLY the single word."
    )
    if result and len(result.split()) == 1 and result.isalpha() and 3 <= len(result) <= 20:
        return result
    return f"{random.choice(ADJECTIVES)}-{random.choice(NOUNS)}"

def get_completion_message(engineer_name: str = "Developer") -> str:
    """Generate friendly completion message. LLM → static fallback."""
    STATIC = ["Work complete!", "All done!", "Task finished!", "Ready for next task!"]
    # 30% chance to include engineer name
    name_hint = f" Address {engineer_name} by name." if random.random() < 0.3 else ""
    result = get_completion(
        f"Generate a friendly <10-word work completion message.{name_hint} Reply with ONLY the message."
    )
    return result if result else random.choice(STATIC)
```

### Task 1-4: Create task summarizer

**File:** `.claude/hooks/utils/llm/task_summarizer.py`

```python
"""Subagent task summarization via Anthropic haiku."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from llm.anthropic_client import get_completion

def summarize_task(transcript_excerpt: str) -> str:
    """Summarize what a subagent did in under 20 words."""
    result = get_completion(
        f"Summarize this task in under 20 words: {transcript_excerpt[:500]}. "
        f"Reply with ONLY the summary."
    )
    return result if result else transcript_excerpt[:50].strip() + "..."
```

**Estimated effort:** Medium — 4 files, ~450 lines total.

---

## Phase 2: Lifecycle Hook Expansion

**Goal:** Add 9 new lifecycle hooks to settings.json (12 official events - 3 existing = 9 new).

### Official Lifecycle Events: Current vs Target

| # | Event | Visionary Has? | Action |
|---|-------|---------------|--------|
| 1 | `SessionStart` | NO | **ADD** |
| 2 | `UserPromptSubmit` | NO | **ADD** |
| 3 | `PreToolUse` | YES (3 scripts) | Keep existing |
| 4 | `PermissionRequest` | NO | **ADD** |
| 5 | `PostToolUse` | YES (8 scripts) | Keep existing + add validators (Phase 7) |
| 6 | `PostToolUseFailure` | NO | **ADD** |
| 7 | `Notification` | NO | **ADD** |
| 8 | `SubagentStart` | NO | **ADD** |
| 9 | `SubagentStop` | NO | **ADD** |
| 10 | `Stop` | YES (5 scripts) | Keep existing + add completion hook (Phase 8) |
| 11 | `PreCompact` | NO | **ADD** |
| 12 | `SessionEnd` | NO | **ADD** |

**NOTE:** `Setup` is NOT an official event. Project detection logic is folded into `SessionStart` (runs on `source: "startup"` only).

### Task 2-1: SessionStart hook

**File:** `.claude/hooks/lifecycle/session_start.py`
**Event:** `SessionStart`
**Sync/Async:** sync (outputs `additionalContext` that must be available immediately)

**Stdin fields:** `source` (startup/resume/clear/compact), `model`, `agent_type`

**What it does:**
1. On `source: "startup"` ONLY — run first-time project detection:
   - Detect project type from files present (pyproject.toml, package.json, Cargo.toml, etc.)
   - Check for optional deps (pyttsx3, anthropic) and log their availability
   - Create `.claude/data/sessions/` directory if missing
   - Persist env vars via `$CLAUDE_ENV_FILE` (ONLY available in SessionStart)
2. On ALL sources — inject context via `additionalContext`:
   - Recent git log (5 commits) via `subprocess.run(["git", "log", "--oneline", "-5"])`
   - Modified files via `subprocess.run(["git", "status", "--porcelain"])`
   - Open GitHub issues if `shutil.which("gh")` is available
   - Session metadata (ID, source, model)
3. Initialize session JSON at `.claude/data/sessions/{session_id}.json`

**Stdout format:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Git branch: main\nRecent commits:\n- abc1234 feat: ...\nModified: 3 files\n..."
  }
}
```

**Coordination with warmup_cache.py:** No conflict. warmup_cache writes to `.claude/session/context_cache.json` (a file read by the Claude Code template at session start). SessionStart's `additionalContext` is injected via Claude Code's official hook protocol. Different mechanisms, complementary purposes.

### Task 2-2: SessionEnd hook

**File:** `.claude/hooks/lifecycle/session_end.py`
**Event:** `SessionEnd`
**Sync/Async:** async (cleanup only, cannot block)

**Stdin fields:** `reason` (clear/logout/prompt_input_exit/bypass_permissions_disabled/other)

**What it does:**
1. Finalize session JSON with end timestamp, duration, reason
2. Write audit summary (total prompts, tools used, errors encountered)
3. Complement (not replace) visionary's existing Stop hooks

**Stdout format:** None required. Fire-and-forget cleanup.

**Ordering note:** SessionEnd fires AFTER Stop hooks. No conflict with visionary's existing Stop hook chain.

### Task 2-3: UserPromptSubmit hook

**File:** `.claude/hooks/lifecycle/user_prompt_submit.py`
**Event:** `UserPromptSubmit` (**NO matcher support** — always fires)
**Sync/Async:** **sync** (must be sync to enable prompt blocking via exit code 2)

**Stdin fields:** `prompt` (the user's submitted text)

**What it does (controlled via CLI flags):**
- `--log-only`: Append prompt to session JSON `prompts` array
- `--store-last-prompt`: Store prompt text in session JSON `last_prompt` field
- `--name-agent`: On FIRST prompt only, generate agent codename via Anthropic → wordlist fallback. Store in session JSON `agent_name` field
- `--validate`: Reject empty prompts (exit code 2 + stderr message). Warn on very short prompts (< 5 chars)

**Blocking protocol:** Exit code 2 + stderr message to block. This erases the prompt from Claude's context.
```python
if not prompt.strip():
    print("Empty prompt rejected. Please enter a message.", file=sys.stderr)
    sys.exit(2)
```

**Stdout format:** Plain text context (if any) is added to Claude's context. For normal operation, no stdout needed.

### Task 2-4: Notification hook

**File:** `.claude/hooks/lifecycle/notification.py`
**Event:** `Notification`
**Sync/Async:** async (TTS is fire-and-forget; cannot block notifications)

**Stdin fields:** `message`, `title`, `notification_type` (permission_prompt/idle_prompt/auth_success/elicitation_dialog)

**What it does:**
1. Read notification message from stdin
2. Personalize: 30% chance of prepending ENGINEER_NAME
3. Speak via pyttsx3 TTS queue (acquire lock, speak, release)
4. Log to session JSON `notifications` array

**Stdout format:** None required.

### Task 2-5: PermissionRequest hook

**File:** `.claude/hooks/lifecycle/permission_request.py`
**Event:** `PermissionRequest`
**Sync/Async:** **sync** (MUST be sync — returns allow/deny decisions)

**Stdin fields:** `tool_name`, `tool_input`, `permission_suggestions`

**IMPORTANT:** Does NOT fire in headless mode (`-p` flag). Use PreToolUse for automated permission decisions in headless mode.

**What it does:**
1. Auto-allow read-only tools: `Read`, `Glob`, `Grep` → immediate allow
2. Auto-allow safe Bash patterns (26+ patterns):
   - `ls`, `pwd`, `cat` (without redirect), `head`, `tail`, `wc`
   - `git status`, `git log`, `git diff`, `git branch`, `git tag`
   - `npm list`, `pip list`, `uv run pytest`, `uv run ruff`
   - `python .claude/hooks/*`, `dir`, `type`, `find`
3. All other operations: exit silently (let user decide)
4. Log all decisions to session JSON `permissions` array

**Stdout format (auto-allow):**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow"
    }
  }
}
```

**Stdout format (deny — rarely used, for dangerous patterns only):**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "deny",
      "message": "Blocked: rm -rf with wildcard detected",
      "interrupt": false
    }
  }
}
```

**Stdout format (no decision — let user decide):** Exit 0 with no stdout.

### Task 2-6: PreCompact hook

**File:** `.claude/hooks/lifecycle/pre_compact.py`
**Event:** `PreCompact`
**Sync/Async:** async (backup is fire-and-forget)

**Stdin fields:** `trigger` (manual/auto), `custom_instructions`, `transcript_path`

**What it does:**
1. Copy transcript file to `.claude/data/sessions/{session_id}_pre_compact_{trigger}_{timestamp}.jsonl`
2. Log compaction event to session JSON

**Stdout format:** None required.

### Task 2-7: PostToolUseFailure hook

**File:** `.claude/hooks/lifecycle/post_tool_use_failure.py`
**Event:** `PostToolUseFailure`
**Sync/Async:** async (logging only, cannot change failure outcome)

**Stdin fields:** `tool_name`, `tool_input`, `tool_use_id`, `error`, `is_interrupt`

**What it does:**
1. Log error to session JSON `errors` array: `{tool, error, timestamp}`
2. Track repeat failures: if same tool_name fails 3+ times in session, add `additionalContext` warning
3. Log to `.claude/data/sessions/{session_id}_errors.jsonl`

**Stdout format (on repeat failure detection):**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUseFailure",
    "additionalContext": "Warning: Bash has failed 3 times this session. Consider a different approach."
  }
}
```

### Task 2-8: SubagentStart hook

**File:** `.claude/hooks/lifecycle/subagent_start.py`
**Event:** `SubagentStart`
**Sync/Async:** async (logging only)

**Stdin fields:** `agent_id`, `agent_type`

**What it does:**
1. Log spawn event to session JSON `subagents` array: `{agent_id, agent_type, started_at}`
2. Increment active subagent counter
3. Debug log to stderr (visible in verbose mode)

**Stdout format:** None required (or optional `additionalContext` injected into subagent's context).

### Task 2-9: SubagentStop hook

**File:** `.claude/hooks/lifecycle/subagent_stop.py`
**Event:** `SubagentStop`
**Sync/Async:** async (TTS is fire-and-forget)

**Stdin fields:** `agent_id`, `agent_type`, `agent_transcript_path`, `stop_hook_active`

**What it does:**
1. Read subagent transcript from `agent_transcript_path`
2. Extract task context (first user prompt from transcript JSONL)
3. Summarize via task_summarizer (Anthropic haiku → truncation fallback)
4. Speak summary via TTS queue (acquire lock → speak → release)
5. Update session JSON subagent entry with `{completed_at, summary}`
6. Decrement active subagent counter

**Transcript parsing:**
```python
# Transcript is JSONL, each line is a JSON object
# Look for entries with type="user" → message.content
for line in open(agent_transcript_path):
    entry = json.loads(line)
    if entry.get("type") == "user":
        content = entry.get("message", {}).get("content", "")
        if isinstance(content, list):
            content = " ".join(c.get("text", "") for c in content if c.get("type") == "text")
        return content[:200]
```

### Task 2-10: Update settings.json with new lifecycle events

**CRITICAL:** Exact settings.json additions. Note which events have matchers vs don't.

```json
{
  "SessionStart": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python .claude/hooks/lifecycle/session_start.py",
          "timeout": 15000
        }
      ]
    }
  ],
  "UserPromptSubmit": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python .claude/hooks/lifecycle/user_prompt_submit.py --log-only --store-last-prompt --name-agent --validate",
          "timeout": 10000
        }
      ]
    }
  ],
  "PermissionRequest": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python .claude/hooks/lifecycle/permission_request.py --auto-allow",
          "timeout": 3000
        }
      ]
    }
  ],
  "PostToolUseFailure": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python .claude/hooks/lifecycle/post_tool_use_failure.py",
          "async": true,
          "timeout": 5000
        }
      ]
    }
  ],
  "Notification": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python .claude/hooks/lifecycle/notification.py",
          "async": true,
          "timeout": 5000
        }
      ]
    }
  ],
  "SubagentStart": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python .claude/hooks/lifecycle/subagent_start.py",
          "async": true,
          "timeout": 5000
        }
      ]
    }
  ],
  "SubagentStop": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python .claude/hooks/lifecycle/subagent_stop.py --notify --summarize",
          "async": true,
          "timeout": 15000
        }
      ]
    }
  ],
  "PreCompact": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python .claude/hooks/lifecycle/pre_compact.py --backup",
          "async": true,
          "timeout": 10000
        }
      ]
    }
  ],
  "SessionEnd": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python .claude/hooks/lifecycle/session_end.py",
          "async": true,
          "timeout": 5000
        }
      ]
    }
  ]
}
```

**Key design choices in this config:**
- `UserPromptSubmit`: NO matcher field (doesn't support it). Sync (no `async` field) because it blocks on empty prompts.
- `PermissionRequest`: NO matcher field (matches all tools). Sync because it returns allow/deny decisions.
- `PostToolUseFailure`, `Notification`, `SubagentStart`, `SubagentStop`, `PreCompact`, `SessionEnd`: All async because they perform logging/TTS and don't need to block.
- `SessionStart`: Sync (no `async`) because `additionalContext` must be injected before Claude processes.

**Estimated effort:** Large — 9 new hook scripts + settings.json update. ~1200-1500 lines total.

---

## Phase 3: Status Line System

**Goal:** Add 8 status line script variants and configure the default.

### Key Finding: StatusLine Receives Rich JSON on stdin

Status line scripts do NOT need to read session files. Claude Code pipes comprehensive JSON on stdin:

```json
{
  "session_id": "abc123",
  "model": {"id": "claude-opus-4-6", "display_name": "Opus"},
  "cost": {
    "total_cost_usd": 0.01234,
    "total_duration_ms": 45000,
    "total_lines_added": 156,
    "total_lines_removed": 23
  },
  "context_window": {
    "total_input_tokens": 15234,
    "total_output_tokens": 4521,
    "context_window_size": 200000,
    "used_percentage": 8,
    "remaining_percentage": 92
  },
  "workspace": {"current_dir": "/cwd", "project_dir": "/original"},
  "version": "1.0.80",
  "vim": {"mode": "NORMAL"},
  "agent": {"name": "security-reviewer"}
}
```

Each script reads this from stdin, formats a single line, and prints to stdout. ANSI color codes are supported.

### Task 3-1: v1_basic.py — Minimal status

Output: `project-name | main | Opus`

### Task 3-2: v2_smart_prompts.py — With prompt counter

Output: `project-name | main | Opus | 12 prompts`

Reads prompt count from `.claude/data/sessions/{session_id}.json` (written by user_prompt_submit.py).

### Task 3-3: v3_agent_sessions.py — With agent codename

Output: `project-name | main | Opus | Agent: Phoenix`

Reads agent name from session JSON.

### Task 3-4: v5_cost_tracking.py — With cost

Output: `project-name | main | $0.12 | 45s`

Uses `cost.total_cost_usd` and `cost.total_duration_ms` from stdin JSON.

### Task 3-5: v6_context_bar.py — Context window visualization (DEFAULT)

Output: `project-name | main | Opus | [████████░░░░░░░░] 42% | $0.12`

Uses `context_window.used_percentage` from stdin JSON to draw visual bar.

### Task 3-6: v7_duration.py — Session duration

Output: `project-name | main | 12m 34s | $0.12`

Uses `cost.total_duration_ms` from stdin JSON.

### Task 3-7: v8_token_stats.py — Token detail

Output: `project-name | In: 15.2k | Out: 4.5k | 42% ctx | $0.12`

Uses `context_window.total_input_tokens`, `total_output_tokens` from stdin JSON.

### Task 3-8: v9_powerline.py — Powerline-style with Unicode

Output: ` main  Opus  ████░░ 42%  $0.12 ` (with Powerline glyphs and ANSI colors)

### Task 3-9: Add statusLine to settings.json

```json
{
  "statusLine": {
    "type": "command",
    "command": "python .claude/status_lines/v6_context_bar.py",
    "timeout": 3000
  }
}
```

**Debouncing:** Claude Code debounces at 300ms and cancels in-flight executions.

**Estimated effort:** Medium — 8 scripts (~40-60 lines each) + settings update. ~400 lines total.

---

## Phase 4: Output Styles

**Goal:** Add 8 response format template files.

### Task 4-1 through 4-8: Create output style files

| File | Style | Use Case |
|------|-------|----------|
| `genui.md` | Standalone HTML5 | Rich visual presentations |
| `ultra-concise.md` | Minimal text | Quick answers, status checks |
| `tts-summary.md` | TTS-optimized | Spoken summaries (short, no markdown) |
| `table-based.md` | Markdown tables | Data comparisons |
| `yaml-structured.md` | YAML blocks | Configuration output |
| `bullet-points.md` | Bullet lists | Action items, checklists |
| `html-structured.md` | HTML fragments | Embeddable content |
| `markdown-focused.md` | Rich markdown | Documentation, reports |

Each file contains:
- Description of when to use the style
- Format template with placeholders
- Example output
- Constraints (max length, allowed elements)

**Estimated effort:** Small — 8 markdown files, ~30-50 lines each. Pure content, no logic.

---

## Phase 5: Agent Enhancements

**Goal:** Add 6 new agents including the team orchestration pair.

### Task 5-1: Create builder agent

**File:** `.claude/agents/team/builder.md`

```yaml
---
description: "Builder agent for implementing code changes. Receives a single task, implements it, validates with ruff/ty, and marks complete."
model: opus
color: cyan
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "python $CLAUDE_PROJECT_DIR/.claude/hooks/validators/ruff_validator.py"
          timeout: 120000
        - type: command
          command: "python $CLAUDE_PROJECT_DIR/.claude/hooks/validators/ty_validator.py"
          timeout: 120000
---
```

Body instructions:
- Single-task focus: `TaskGet` your assigned task → implement → `TaskUpdate` to complete
- All tools available (Write, Edit, Bash, Read, Glob, Grep)
- On validation failure: fix the issue and re-save
- When done: mark task complete with summary of changes

### Task 5-2: Create validator agent

**File:** `.claude/agents/team/validator.md`

```yaml
---
description: "Validator agent for reviewing code changes. Read-only — cannot modify files. Reports pass/fail with detailed findings."
model: opus
color: yellow
disallowedTools:
  - Write
  - Edit
  - NotebookEdit
---
```

Body instructions:
- 4-step workflow: understand → inspect → verify → report
- `TaskGet` assigned task → read all relevant files → verify correctness
- Pass/fail report template:
  ```
  ## Validation Report
  **Status:** PASS / FAIL
  **Task:** [task description]
  **Files Reviewed:** [list]
  **Findings:** [bullet list]
  **Verdict:** [summary]
  ```
- `TaskUpdate` with pass/fail result

### Task 5-3: Create meta-agent (agent factory)

**File:** `.claude/agents/meta-agent.md`

- Scrapes Anthropic docs for latest Claude Code features (via WebFetch/WebSearch)
- Generates new agent `.md` files with proper YAML frontmatter
- Infers appropriate tools, model, color from agent purpose
- Kebab-case naming convention for generated files
- Color selection from palette: cyan, yellow, green, magenta, red, blue

### Task 5-4: Create work-completion summary agent

**File:** `.claude/agents/work-completion.md`

```yaml
---
description: "Generates a TTS summary when work is completed. Proactively invoked on significant task completion."
model: haiku
color: green
---
```

- Ultra-concise format: 1 sentence summary + 1 next step
- Speaks via pyttsx3 (Bash call to TTS wrapper)
- Uses ENGINEER_NAME from env for personalization

### Task 5-5: Create greeting agent

**File:** `.claude/agents/greeting.md`

```yaml
---
description: "If they say 'hi claude' or 'hi cc', respond with a personalized greeting."
model: haiku
color: green
---
```

- Proactive trigger via `description` field
- Response directed at primary agent (the greeting text is returned to the orchestrating agent, which relays it)
- Personalized using ENGINEER_NAME

### Task 5-6: Create research agent

**File:** `.claude/agents/research.md`

```yaml
---
description: "Deep web research agent for technical questions. Date-aware, multi-source."
model: sonnet
color: magenta
allowed-tools:
  - WebSearch
  - WebFetch
  - Read
  - Glob
  - Grep
  - Bash
---
```

- Date-aware: always includes current year in search queries
- Multi-source strategy (official docs, GitHub, Stack Overflow, blogs)
- 6-section report: summary, key findings, sources, limitations, recommendations, next steps

**Estimated effort:** Medium — 6 markdown files, ~150-250 lines each. ~1200 lines total.

---

## Phase 6: Command Enhancements

**Goal:** Add 5 new commands + 2 self-validating hook scripts.

### Task 6-1: Create plan-w-team command

**File:** `.claude/commands/plan-w-team.md`

This is the meta-prompting orchestrator:

```yaml
---
description: "Create a team-orchestrated implementation plan"
model: opus
arguments:
  - name: prompt
    description: "What to plan"
  - name: orchestration
    description: "Optional orchestration instructions"
disallowed-tools:
  - Task
  - EnterPlanMode
hooks:
  Stop:
    - hooks:
        - type: command
          command: "python $CLAUDE_PROJECT_DIR/.claude/hooks/validators/validate_new_file.py -d .planning -e .md"
          timeout: 10000
        - type: command
          command: "python $CLAUDE_PROJECT_DIR/.claude/hooks/validators/validate_file_contains.py -d .planning -e .md --contains '## Summary' --contains '## Tasks' --contains '## Team' --contains '## Dependencies' --contains '## Validation' --contains '## Success Criteria' --contains '## Notes'"
          timeout: 10000
---
```

**NOTE on command-level Stop hooks:** When this command runs as the main agent, Stop hooks fire normally. When invoked as a subagent (via Task tool), Stop hooks are **automatically converted to SubagentStop**. Exit code 1 from validators = block (force Claude to continue fixing the plan).

Body includes:
- Complete Task system documentation (TaskCreate, TaskUpdate, TaskList, TaskGet)
- Task dependency DAG patterns (`blockedBy` field)
- 7-section plan format template with `<requested content>` markers
- Orchestrator-never-builds pattern: "You create the plan. You NEVER write code directly."
- Team member auto-discovery: reads `.claude/agents/team/*.md`
- Variables: `$1` = user prompt, `$2` = orchestration prompt

### Task 6-2: Create build command

**File:** `.claude/commands/build.md`

```yaml
---
description: "Execute an implementation plan by deploying team agents"
arguments:
  - name: plan
    description: "Path to the plan file"
---
```

- Guard clause: if no `$1` provided, list available plans in `.planning/`
- Reads plan → creates Task items with blockedBy dependencies
- Deploys builder agents for implementation tasks
- Deploys validator agents for verification tasks

### Task 6-3: Create cook command

**File:** `.claude/commands/cook.md`

```yaml
---
description: "Launch parallel subagents for independent tasks"
---
```

- Launches N parallel subagents simultaneously via Task tool
- Each subagent gets a different task
- Useful for multi-file changes that don't depend on each other

### Task 6-4: Create prime command

**File:** `.claude/commands/prime.md`

```yaml
---
description: "Load project context into the conversation"
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
---
```

- Read-only context loader: CLAUDE.md, STATE.md, DEVLOG.md, recent git history, open tasks
- Cannot modify files (no Write/Edit in allowed-tools)

### Task 6-5: Create question command

**File:** `.claude/commands/question.md`

```yaml
---
description: "Research-only mode — answer questions without modifying code"
allowed-tools:
  - "Bash(git ls-files:*)"
  - Read
  - Glob
  - Grep
---
```

- 4 anti-coding rules in body: no Write, no Edit, no code suggestions, just answer the question
- Bash restricted to `git ls-files` only

### Task 6-6: Create validate_new_file.py validator

**File:** `.claude/hooks/validators/validate_new_file.py`

Used by command-level Stop hooks to verify expected output files were created.

```python
# CLI arguments (NOT stdin — this is args-driven):
# -d/--directory: Directory to check (default: specs)
# -e/--extension: File extension (default: .md)
# --max-age: Max file age in minutes (default: 5)

# Detection: git status --porcelain {directory}/ for new files
# OR: file modification time within --max-age minutes

# Exit code 0 = pass (file found)
# Exit code 1 = BLOCK (no file found — force Claude to create it)

# Stdout on pass:
# {"result": "continue", "message": "New file found: .planning/team-plan.md"}

# Stdout on fail:
# {"result": "block", "reason": "VALIDATION FAILED: No new file found in .planning/*.md.\n\nACTION REQUIRED: Create the plan file."}
```

### Task 6-7: Create validate_file_contains.py validator

**File:** `.claude/hooks/validators/validate_file_contains.py`

Used by command-level Stop hooks to verify output contains required sections.

```python
# CLI arguments:
# -d/--directory, -e/--extension, --max-age: same as validate_new_file
# --contains STRING: Required string (can be repeated)

# Finds newest file in directory, reads content, checks for each --contains string

# Exit code 0 = pass (all strings found)
# Exit code 1 = BLOCK (missing strings)

# Stdout on fail:
# {"result": "block", "reason": "VALIDATION FAILED: Missing 2 required sections.\n\nMISSING:\n  - ## Tasks\n  - ## Dependencies\n\nACTION REQUIRED: Add the missing sections."}
```

**Estimated effort:** Large — 7 files. plan-w-team alone is ~500 lines. Total ~1200 lines.

---

## Phase 7: Security & Validation Merge

**Goal:** Merge hooks-mastery's security patterns with visionary's existing validators.

### Task 7-1: Enhance dangerous_command_checker.py

**Modify:** `.claude/hooks/validators/dangerous_command_checker.py`

Add from hooks-mastery:
- `.env` file blocking: block `cat .env`, `type .env`, `echo > .env`, etc. Allow `.env.sample`, `.env.example`, `.env.template`
- Dangerous path detection: block operations targeting paths outside project root (`../../../etc/passwd`, etc.)
- Keep all 30+ existing visionary patterns unchanged

### Task 7-2: Create ruff_validator.py

**File:** `.claude/hooks/validators/ruff_validator.py`
**Used by:** PostToolUse (Write|Edit matcher) in settings.json AND builder agent frontmatter

**Stdin format (PostToolUse provides):**
```json
{
  "tool_name": "Write",
  "tool_input": {"file_path": "/path/to/file.py", "content": "..."},
  "tool_response": {"filePath": "/path/to/file.py", "success": true}
}
```

**Implementation:**
1. Extract `file_path` from `tool_input`
2. Skip non-`.py` files (output `{}` and exit 0)
3. Run `subprocess.run([sys.executable, "-m", "ruff", "check", file_path], timeout=120)`
   - If ruff not found: pass silently (`{}`)
   - If ruff returns 0: pass (`{}`)
   - If ruff returns non-zero: block with output

**Stdout on block (PostToolUse protocol):**
```json
{"decision": "block", "reason": "Ruff lint failed:\n<first 500 chars of ruff output>"}
```

**Stdout on pass:** `{}`

### Task 7-3: Create ty_validator.py

**File:** `.claude/hooks/validators/ty_validator.py`

Same architecture as ruff_validator but runs type checking:
- `subprocess.run([sys.executable, "-m", "ty", "check", file_path], timeout=120)`
- Or falls back to `mypy` if `ty` not available
- Same `{"decision": "block", "reason": "..."}` protocol

### Task 7-4: Wire validators into settings.json

Add to existing `PostToolUse` → `Write|Edit` matcher's hooks array:
```json
{
  "type": "command",
  "command": "python .claude/hooks/validators/ruff_validator.py",
  "async": false,
  "timeout": 120000
},
{
  "type": "command",
  "command": "python .claude/hooks/validators/ty_validator.py",
  "async": false,
  "timeout": 120000
}
```

**IMPORTANT:** These MUST be `"async": false` (sync) because they need to return `{"decision": "block"}` to Claude Code. If async, the decision would be ignored.

### Task 7-5: Update permissions allow list

Add to `permissions.allow`:
```json
"Bash(ruff *)",
"Bash(uv run ruff*)",
"Bash(uv run mypy*)",
"Bash(uv run pytest*)"
```

**Note:** We do NOT add `Read(*)`, `Glob(*)`, `Grep(*)` to the permissions allow list. These are handled by the PermissionRequest hook (Phase 2-5) which auto-allows them programmatically. The `permissions.allow` list is for static rules; PermissionRequest is for dynamic rules.

**Estimated effort:** Medium — 2 new scripts, 2 modified files. ~400 lines total.

---

## Phase 8: Autonomous Behaviors

**Goal:** Wire up 16+ automatic behaviors and add the completion TTS stop hook.

These are mostly behaviors embedded in Phase 2 hooks. This phase ensures they're correctly configured and adds the one new Stop hook.

### Tasks 8-1 through 8-15: Verification of Phase 2 behaviors

| # | Behavior | Implemented By | Verification |
|---|----------|---------------|--------------|
| 8-1 | Auto prompt logging | user_prompt_submit.py `--log-only` | Check session JSON has `prompts` array |
| 8-2 | Auto agent naming | user_prompt_submit.py `--name-agent` | Check session JSON has `agent_name` on first prompt |
| 8-3 | Auto prompt validation | user_prompt_submit.py `--validate` | Submit empty prompt → blocked with stderr |
| 8-4 | Auto session persistence | session_start.py + session_end.py | Check `.claude/data/sessions/{id}.json` exists with timestamps |
| 8-5 | Auto context injection | session_start.py `additionalContext` | Verify git log and status appear in Claude's context |
| 8-6 | Auto transcript backup | pre_compact.py `--backup` | Trigger `/compact` → check backup file created |
| 8-7 | Auto permission handling | permission_request.py `--auto-allow` | Read/Glob/Grep auto-allowed without prompt |
| 8-8 | Auto error pattern detection | post_tool_use_failure.py | Fail same tool 3x → check `additionalContext` warning |
| 8-9 | Auto subagent tracking | subagent_start.py | Launch Task → check session JSON `subagents` array |
| 8-10 | Auto subagent TTS | subagent_stop.py `--notify` | Complete Task → hear TTS summary |
| 8-11 | Auto notification personalization | notification.py | Check ENGINEER_NAME appears in ~30% of TTS |
| 8-12 | Auto project detection | session_start.py (startup source) | First session → check project type detected |
| 8-13 | Auto session cleanup | session_end.py + existing session_cleanup.py | End session → check audit finalized |
| 8-14 | Auto stale lock cleanup | tts_queue.py `cleanup_stale_locks()` | Kill process holding lock → lock cleaned within 60s |
| 8-15 | Auto session audit trail | All hooks append to session JSON | Check session JSON has all event types logged |

### Task 8-16: Create stop completion TTS hook

**File:** `.claude/hooks/lifecycle/stop_completion.py`
**Event:** `Stop` (added to EXISTING Stop hooks array)
**Sync/Async:** async (TTS is fire-and-forget)

**CRITICAL: Infinite loop prevention:**
```python
input_data = json.load(sys.stdin)
if input_data.get("stop_hook_active", False):
    sys.exit(0)  # Already continuing from a previous stop hook — do NOT block
```

**What it does:**
1. Check `stop_hook_active` — exit immediately if True
2. Generate completion message via `get_completion_message()` (Anthropic → static fallback)
3. Speak via TTS queue
4. Log to session JSON

**Stdout format:** None (side-effect only — TTS).

### Task 8-17: Add stop_completion.py to Stop hooks in settings.json

**Insert BEFORE `session_cleanup.py`** (which deletes session ID files):

```json
"Stop": [
  {
    "hooks": [
      {"type": "command", "command": "python .claude/hooks/session/task_completion_reminder.py", "timeout": 3000},
      {"type": "command", "command": "python .claude/hooks/session/auto_snapshot.py", "timeout": 5000},
      {"type": "command", "command": "python .claude/hooks/session/auto_devlog.py", "timeout": 5000},
      {"type": "command", "command": "python .claude/hooks/lifecycle/stop_completion.py", "async": true, "timeout": 10000},
      {"type": "command", "command": "python .claude/hooks/session/session_cleanup.py", "timeout": 5000},
      {"type": "command", "command": "python .claude/hooks/session/session_maintenance.py", "timeout": 10000}
    ]
  }
]
```

**Ordering rationale:**
1. `task_completion_reminder` — read-only, first
2. `auto_snapshot` — writes `last_snapshot.json`
3. `auto_devlog` — reads `last_snapshot.json` (depends on #2)
4. `stop_completion` — **NEW** — needs session ID (still available), async TTS
5. `session_cleanup` — deletes session ID files (everything after this loses session identity)
6. `session_maintenance` — archives old sessions (doesn't need session ID)

**Estimated effort:** Small — 1 new file, 1 settings.json modification. ~100 lines.

---

## Phase 9: Polish & Documentation

**Goal:** Update documentation, fix known bugs, finalize settings, verify everything works.

### Task 9-1: Update CLAUDE.md template

Add new sections:
- **Lifecycle Hooks:** List all 12 events and what each hook does
- **Status Line:** How to switch between 8 versions
- **Output Styles:** Available styles and when to use each
- **Team Agents:** Builder/validator pair, meta-agent, work-completion, greeting, research
- **New Commands:** plan-w-team, build, cook, prime, question
- **TTS & LLM Features:** Configuration, optional deps, graceful degradation
- **Environment Variables:** ANTHROPIC_API_KEY, ENGINEER_NAME, FIRECRAWL_API_KEY

### Task 9-2: Fix auto_devlog.py session marker bug

**Modify:** `.claude/hooks/session/auto_devlog.py`

The `was_session_logged()` function currently checks if the marker file was modified today. Two sessions on the same day = second session won't log. Fix: use session ID instead of date for the marker.

### Task 9-3: Create integration test script

**File:** `.claude/scripts/test_hooks.py`

Smoke test that:
- Verifies all hook scripts exist at expected paths
- Checks each script is syntactically valid (`python -c "compile(open(f).read(), f, 'exec')"`)
- Verifies pyttsx3 graceful degradation (import fails → TTS_AVAILABLE = False)
- Verifies anthropic SDK graceful degradation (import fails → ANTHROPIC_AVAILABLE = False)
- Verifies cross-platform locking (msvcrt on Windows, fcntl on Unix)
- Verifies settings.json is valid JSON and references only existing hook files

### Task 9-4: Update .gitignore (final)

Ensure all runtime/generated files are excluded:
```
.claude/data/sessions/*.json
.claude/data/sessions/*_pre_compact_*.jsonl
.claude/data/sessions/*_errors.jsonl
.claude/data/tts_queue/
.claude/session/
.claude/hooks/**/__pycache__/
*.lock
.env
```

### Task 9-5: Final settings.json review

Checklist:
- [ ] All 12 lifecycle events have hooks configured (3 existing + 9 new)
- [ ] `statusLine` configured pointing to v6_context_bar.py
- [ ] All hook paths are correct and files exist
- [ ] All timeout values are in milliseconds
- [ ] Sync/async assignments match the protocol matrix
- [ ] UserPromptSubmit and Stop have NO matcher fields
- [ ] Permissions allow list includes all necessary patterns
- [ ] Stop hooks are in correct order (completion before cleanup)
- [ ] env section has CLAUDE_CODE_ENABLE_TASKS and CLAUDE_SESSION_TAG

**Estimated effort:** Medium — 5 tasks, mostly documentation and verification.

---

## Catalog → Task Mapping

All 106 catalog items mapped to implementation tasks.

### Category 1: Hook Lifecycle Coverage (10 items)
| # | Capability | Phase.Task | Note |
|---|-----------|------------|------|
| 1 | 12 lifecycle events configured (not 13 — Setup doesn't exist) | 2-10 | Corrected from "13" |
| 2 | Project detection + dep checking (was "Setup hook") | 2-1 | Folded into SessionStart (source: "startup") |
| 3 | SessionStart hook (context injection) | 2-1 | |
| 4 | SessionEnd hook (cleanup + audit) | 2-2 | |
| 5 | UserPromptSubmit hook (prompt logging) | 2-3 | |
| 6 | Notification hook (TTS) | 2-4 | |
| 7 | PermissionRequest hook (auto-allow) | 2-5 | |
| 8 | PreCompact hook (transcript backup) | 2-6 | |
| 9 | SubagentStart/Stop hooks | 2-8, 2-9 | |
| 10 | PostToolUseFailure hook | 2-7 | |

### Category 2: Meta-Prompting & Orchestration (8 items)
| # | Capability | Phase.Task |
|---|-----------|------------|
| 11 | plan_w_team command | 6-1 |
| 12 | Stop hooks validate plan output | 6-1, 6-6, 6-7 |
| 13 | 7-section plan format template | 6-1 |
| 14 | Task system documentation in prompt | 6-1 |
| 15 | Orchestrator-never-builds pattern | 6-1 |
| 16 | Variable injection ($1, $2) | 6-1 |
| 17 | Team member auto-discovery | 6-1 |
| 18 | Task dependency DAGs (blockedBy) | 6-1 |

### Category 3: Self-Validating Commands (6 items)
| # | Capability | Phase.Task |
|---|-----------|------------|
| 19 | validate_new_file.py | 6-6 |
| 20 | validate_file_contains.py | 6-7 |
| 21 | Dual detection (git status + mod time) | 6-6 |
| 22 | Multi-string content validation | 6-7 |
| 23 | Actionable error messages | 6-6, 6-7 |
| 24 | Command-level Stop hooks in frontmatter (exit 1 = block) | 6-1 |

### Category 4: Builder/Validator Agent Pair (8 items)
| # | Capability | Phase.Task |
|---|-----------|------------|
| 25 | Builder agent (full tools + validators) | 5-1 |
| 26 | Validator agent (read-only enforced) | 5-2 |
| 27 | Per-edit ruff validation | 7-2 |
| 28 | Per-edit type checking | 7-3 |
| 29 | Role separation via disallowedTools | 5-2 |
| 30 | Single-task focus with TaskGet/TaskUpdate | 5-1 |
| 31 | Pass/fail report template | 5-2 |
| 32 | Agent color differentiation | 5-1, 5-2 |

### Category 5: Agent Patterns (10 items)
| # | Capability | Phase.Task |
|---|-----------|------------|
| 33 | Meta-agent (agent factory) | 5-3 |
| 34 | Work-completion summary agent | 5-4 |
| 35 | Greeting agent (proactive) | 5-5 |
| 36 | Research agent (date-aware) | 5-6 |
| 37 | Agent color system | 5-1 through 5-6 |
| 38 | Proactive trigger via description | 5-4, 5-5 |
| 39 | Response-directed-at-primary pattern | 5-5 |
| 40 | Per-agent tool scoping | 5-1, 5-2, 5-6 |
| 41 | Model selection per agent | 5-1 through 5-6 |
| 42 | Anthropic doc scraping (meta-agent) | 5-3 |

### Category 6: Command Patterns (8 items)
| # | Capability | Phase.Task |
|---|-----------|------------|
| 43 | build command (execute from plan) | 6-2 |
| 44 | cook command (parallel subagents) | 6-3 |
| 45 | prime command (context loader) | 6-4 |
| 46 | question command (read-only) | 6-5 |
| 47 | Guard clauses (missing args check) | 6-2 |
| 48 | Argument variables ($1) | 6-1, 6-2 |
| 49 | Tool scoping in commands | 6-4, 6-5 |
| 50 | allowed-tools / disallowed-tools | 6-1, 6-4, 6-5 |

### Category 7: Status Line System (10 items)
| # | Capability | Phase.Task |
|---|-----------|------------|
| 51 | v1 basic status | 3-1 |
| 52 | v2 smart prompts | 3-2 |
| 53 | v3 agent sessions | 3-3 |
| 54 | v5 cost tracking | 3-4 |
| 55 | v6 context window bar (default) | 3-5 |
| 56 | v7 duration tracking | 3-6 |
| 57 | v8 token stats | 3-7 |
| 58 | v9 powerline | 3-8 |
| 59 | statusLine in settings.json | 3-9 |
| 60 | Rich JSON data from stdin (not session files) | 3-1 through 3-8 |

### Category 8: Output Styles (8 items)
| # | Capability | Phase.Task |
|---|-----------|------------|
| 61 | genui (standalone HTML5) | 4-1 |
| 62 | ultra-concise | 4-2 |
| 63 | tts-summary | 4-3 |
| 64 | table-based | 4-4 |
| 65 | yaml-structured | 4-5 |
| 66 | bullet-points | 4-6 |
| 67 | html-structured | 4-7 |
| 68 | markdown-focused | 4-8 |

### Category 9: TTS Subsystem (6 items)
| # | Capability | Phase.Task |
|---|-----------|------------|
| 69 | pyttsx3 wrapper | 1-1 |
| 70 | TTS queue with cross-platform file locking | 1-2 |
| 71 | Cross-process audio sync | 1-2 |
| 72 | Stale lock cleanup | 1-2 |
| 73 | Graceful degradation (TTS_AVAILABLE flag) | 1-1 |
| 74 | Personalized notifications (ENGINEER_NAME) | 2-4, 8-11 |

### Category 10: LLM-in-Hooks Subsystem (6 items)
| # | Capability | Phase.Task |
|---|-----------|------------|
| 75 | Anthropic haiku client | 1-3 |
| 76 | Agent naming (Anthropic → wordlist fallback) | 1-3, 2-3 |
| 77 | Task summarization | 1-4, 2-9 |
| 78 | Completion messages | 8-16 |
| 79 | Cost-guarded calls (max_tokens ≤ 100) | 1-3 |
| 80 | Graceful fallback chain | 1-3 |

### Category 11: Security & Permissions (8 items)
| # | Capability | Phase.Task |
|---|-----------|------------|
| 81 | .env file blocking | 7-1 |
| 82 | Dangerous path detection (outside project root) | 7-1 |
| 83 | Auto-allow read-only tools (via PermissionRequest hook) | 2-5 |
| 84 | 26+ safe bash patterns (in PermissionRequest hook) | 2-5 |
| 85 | Structured JSON permission responses (hookSpecificOutput.decision.behavior) | 2-5 |
| 86 | Permission decision logging | 2-5 |
| 87 | Per-edit ruff linting (PostToolUse validator) | 7-2 |
| 88 | Per-edit type checking (PostToolUse validator) | 7-3 |

### Category 12: Autonomous Behaviors (16 items)
| # | Capability | Phase.Task |
|---|-----------|------------|
| 89 | Auto prompt logging | 8-1 |
| 90 | Auto agent naming | 8-2 |
| 91 | Auto prompt validation | 8-3 |
| 92 | Auto session persistence | 8-4 |
| 93 | Auto context injection (additionalContext) | 8-5 |
| 94 | Auto transcript backup (pre-compact) | 8-6 |
| 95 | Auto permission handling | 8-7 |
| 96 | Auto error pattern detection (3x threshold) | 8-8 |
| 97 | Auto subagent tracking | 8-9 |
| 98 | Auto subagent TTS | 8-10 |
| 99 | Auto notification personalization | 8-11 |
| 100 | Auto project detection (SessionStart startup) | 8-12 |
| 101 | Auto session cleanup | 8-13 |
| 102 | Auto stale lock cleanup | 8-14 |
| 103 | Auto session audit trail | 8-15 |
| 104 | Auto completion TTS | 8-16 |

### Category 13: Infrastructure (6 items)
| # | Capability | Phase.Task |
|---|-----------|------------|
| 105 | .env.sample (3 keys: ANTHROPIC_API_KEY, ENGINEER_NAME, FIRECRAWL_API_KEY) | 0-2 |
| 106 | Session data directory structure (.claude/data/sessions/) | 0-1 |

**Total mapped: 106/106** — all items accounted for.

---

## Risk Register

| # | Risk | Impact | Likelihood | Mitigation |
|---|------|--------|------------|------------|
| 1 | Windows `fcntl` unavailable | TTS locking fails | HIGH on Windows | Cross-platform lock in Task 1-2: `msvcrt.locking` fallback |
| 2 | pyttsx3 not installed | TTS features silent | MEDIUM | Graceful `TTS_AVAILABLE` flag (AD-4) |
| 3 | Anthropic API key missing | LLM features fail | MEDIUM | Static fallbacks: wordlist naming, canned completion messages (AD-5) |
| 4 | Async hooks returning decisions silently ignored | Permission/blocking hooks don't work | **CRITICAL if misconfigured** | All decision-returning hooks explicitly marked sync in plan (Finding #4) |
| 5 | Stop hook infinite loop | Claude loops forever | **CRITICAL if unchecked** | `stop_hook_active` guard clause in ALL Stop hooks (Finding #6) |
| 6 | UserPromptSubmit/Stop with matchers (silently ignored) | Hooks fire when unexpected or vice versa | MEDIUM | Plan explicitly omits matchers for these events (Finding #5) |
| 7 | Three different decision protocols confused | Hook returns wrong JSON, silently fails | HIGH | Protocol Reference section documents all three patterns explicitly |
| 8 | PostToolUse ruff/ty validator slows editing | Every file save takes 2+ seconds | MEDIUM | Validators skip non-.py files; 120s timeout; fail-open on error |
| 9 | `Path.replace()` PermissionError on Windows | Atomic writes fail intermittently | MEDIUM | Retry-with-backoff pattern in `platform_compat.py` (AD-7) |
| 10 | warmup_cache.py and SessionStart double context injection | Duplicate context in Claude's context window | LOW | Different mechanisms: warmup_cache writes file cache; SessionStart uses additionalContext JSON (AD-3) |
| 11 | Stop hook ordering — new hook after session_cleanup loses session ID | stop_completion.py can't read session data | HIGH if misordered | Explicit insertion point documented: BEFORE session_cleanup (Task 8-17) |
| 12 | auto_devlog.py same-day marker bug | Second session on same day won't log | LOW (pre-existing) | Fix included in Phase 9-2 |

---

## New Directory Structure (Final)

```
.claude/
├── agents/
│   ├── team/                     ← NEW (Phase 5)
│   │   ├── builder.md
│   │   └── validator.md
│   ├── meta-agent.md             ← NEW (Phase 5)
│   ├── work-completion.md        ← NEW (Phase 5)
│   ├── greeting.md               ← NEW (Phase 5)
│   ├── research.md               ← NEW (Phase 5)
│   ├── code-simplifier.md        (existing)
│   ├── debug-helper.md           (existing)
│   └── verify-app.md             (existing)
├── commands/                      (28 existing + 5 new)
│   ├── plan-w-team.md            ← NEW (Phase 6)
│   ├── build.md                  ← NEW (Phase 6)
│   ├── cook.md                   ← NEW (Phase 6)
│   ├── prime.md                  ← NEW (Phase 6)
│   ├── question.md               ← NEW (Phase 6)
│   └── ... (28 existing)
├── hooks/
│   ├── lifecycle/                 ← NEW (Phase 2, 8)
│   │   ├── session_start.py      (also handles project detection — no Setup event)
│   │   ├── session_end.py
│   │   ├── user_prompt_submit.py
│   │   ├── notification.py
│   │   ├── permission_request.py
│   │   ├── pre_compact.py
│   │   ├── post_tool_use_failure.py
│   │   ├── subagent_start.py
│   │   ├── subagent_stop.py
│   │   └── stop_completion.py
│   ├── utils/                     ← NEW (Phase 0, 1)
│   │   ├── constants.py
│   │   ├── platform_compat.py
│   │   ├── stdin_parser.py
│   │   ├── tts/
│   │   │   ├── pyttsx3_tts.py
│   │   │   └── tts_queue.py
│   │   └── llm/
│   │       ├── anthropic_client.py
│   │       └── task_summarizer.py
│   ├── validators/                (existing + 4 new)
│   │   ├── ruff_validator.py      ← NEW (Phase 7)
│   │   ├── ty_validator.py        ← NEW (Phase 7)
│   │   ├── validate_new_file.py   ← NEW (Phase 6)
│   │   ├── validate_file_contains.py ← NEW (Phase 6)
│   │   ├── dangerous_command_checker.py (MODIFIED Phase 7)
│   │   ├── invariant_validator.py (existing)
│   │   ├── json_validator.py      (existing)
│   │   ├── markdown_validator.py  (existing)
│   │   ├── commit_validator.py    (existing)
│   │   ├── TEMPLATE_validator.py  (existing)
│   │   └── README.md              (existing)
│   ├── intel/                     (existing, unchanged)
│   └── session/                   (existing, auto_devlog.py MODIFIED Phase 9)
├── output-styles/                 ← NEW (Phase 4)
│   ├── genui.md
│   ├── ultra-concise.md
│   ├── tts-summary.md
│   ├── table-based.md
│   ├── yaml-structured.md
│   ├── bullet-points.md
│   ├── html-structured.md
│   └── markdown-focused.md
├── status_lines/                  ← NEW (Phase 3)
│   ├── v1_basic.py
│   ├── v2_smart_prompts.py
│   ├── v3_agent_sessions.py
│   ├── v5_cost_tracking.py
│   ├── v6_context_bar.py         (DEFAULT)
│   ├── v7_duration.py
│   ├── v8_token_stats.py
│   └── v9_powerline.py
├── data/                          ← NEW (Phase 0)
│   ├── sessions/                  (runtime, gitignored)
│   └── tts_queue/                 (runtime, gitignored)
├── scripts/                       (existing + 1 new)
│   └── test_hooks.py             ← NEW (Phase 9)
├── session/                       (existing runtime dir)
├── skills/                        (existing, unchanged)
├── settings.json                  (MODIFIED Phases 2, 3, 7, 8)
└── .env.sample                    ← NEW (Phase 0)
```

---

## Execution Order Summary

```
Phase 0 (Foundation) ─────────────────────────────┐
    │                                              │
    ├── Phase 1 (Utility Subsystems) ──┐           │
    │       │                          │           │
    │       ├── Phase 2 (Lifecycle) ───┤           ├── Phase 3 (Status Lines)
    │       │       │                  │           │
    │       │       ├── Phase 5 (Agents)           ├── Phase 4 (Output Styles)
    │       │       │       │          │           │
    │       │       │       └── Phase 6 (Commands) │
    │       │       │                  │           │
    │       │       ├── Phase 7 (Security)         │
    │       │       │                  │           │
    │       │       └── Phase 8 (Autonomous) ──────┘
    │       │                          │
    └───────┴── Phase 9 (Polish) ──────┘
```

**Critical path:** 0 → 1 → 2 → 5 → 6 → 9 (6 phases sequential)
**Parallelizable after Phase 0:** Phases 3 and 4
**Parallelizable after Phase 2:** Phase 7

---

## Estimated Total Scope

| Metric | Count |
|--------|-------|
| New files | ~53 |
| Modified files | ~11 |
| New Python code | ~3,000-4,000 lines |
| New Markdown content | ~2,500-3,000 lines |
| Total new lines | ~5,500-7,000 |
| Catalog items covered | 106/106 |
| Architecture decisions | 8 |
| Lifecycle events (official) | 12/12 |
| Risk items tracked | 12 |
| Second-pass corrections | 23 |
