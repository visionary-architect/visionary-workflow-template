#!/usr/bin/env python3
"""
Integration test script for hooks-mastery integration.

Verifies:
1. All hook scripts exist at expected paths
2. Each script is syntactically valid Python
3. pyttsx3 graceful degradation
4. anthropic SDK graceful degradation
5. Cross-platform locking detection
6. settings.json references only existing hook files
7. settings.json is valid JSON
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CLAUDE_DIR = PROJECT_ROOT / ".claude"
SETTINGS_FILE = CLAUDE_DIR / "settings.json"

# Expected files from the integration
EXPECTED_HOOKS = [
    # Phase 1: Utility subsystems
    "hooks/utils/constants.py",
    "hooks/utils/platform_compat.py",
    "hooks/utils/stdin_parser.py",
    "hooks/utils/tts/pyttsx3_tts.py",
    "hooks/utils/tts/tts_queue.py",
    "hooks/utils/llm/anthropic_client.py",
    "hooks/utils/llm/task_summarizer.py",
    # Phase 2: Lifecycle hooks
    "hooks/lifecycle/session_start.py",
    "hooks/lifecycle/session_end.py",
    "hooks/lifecycle/user_prompt_submit.py",
    "hooks/lifecycle/notification.py",
    "hooks/lifecycle/permission_request.py",
    "hooks/lifecycle/pre_compact.py",
    "hooks/lifecycle/post_tool_use_failure.py",
    "hooks/lifecycle/subagent_start.py",
    "hooks/lifecycle/subagent_stop.py",
    "hooks/lifecycle/stop_completion.py",
    # Phase 6: Validators
    "hooks/validators/validate_new_file.py",
    "hooks/validators/validate_file_contains.py",
    "hooks/validators/ruff_validator.py",
    "hooks/validators/ty_validator.py",
]

EXPECTED_STATUS_LINES = [
    "status_lines/v1_basic.py",
    "status_lines/v2_smart_prompts.py",
    "status_lines/v3_agent_sessions.py",
    "status_lines/v5_cost_tracking.py",
    "status_lines/v6_context_bar.py",
    "status_lines/v7_duration.py",
    "status_lines/v8_token_stats.py",
    "status_lines/v9_powerline.py",
]

EXPECTED_OUTPUT_STYLES = [
    "output-styles/genui.md",
    "output-styles/ultra-concise.md",
    "output-styles/tts-summary.md",
    "output-styles/table-based.md",
    "output-styles/yaml-structured.md",
    "output-styles/bullet-points.md",
    "output-styles/html-structured.md",
    "output-styles/markdown-focused.md",
]

EXPECTED_AGENTS = [
    "agents/team/builder.md",
    "agents/team/validator.md",
    "agents/meta-agent.md",
    "agents/work-completion.md",
    "agents/greeting.md",
    "agents/research.md",
]

EXPECTED_COMMANDS = [
    "commands/plan-w-team.md",
    "commands/build.md",
    "commands/cook.md",
    "commands/prime.md",
    "commands/question.md",
]


def test_files_exist():
    """Verify all expected files exist."""
    all_files = (
        EXPECTED_HOOKS + EXPECTED_STATUS_LINES +
        EXPECTED_OUTPUT_STYLES + EXPECTED_AGENTS + EXPECTED_COMMANDS
    )
    missing = []
    for rel_path in all_files:
        full_path = CLAUDE_DIR / rel_path
        if not full_path.exists():
            missing.append(rel_path)
    return missing


def test_python_syntax():
    """Verify all Python scripts are syntactically valid."""
    py_files = EXPECTED_HOOKS + EXPECTED_STATUS_LINES
    errors = []
    for rel_path in py_files:
        full_path = CLAUDE_DIR / rel_path
        if not full_path.exists():
            continue
        try:
            source = full_path.read_text(encoding="utf-8")
            compile(source, str(full_path), "exec")
        except SyntaxError as e:
            errors.append(f"{rel_path}: {e}")
    return errors


def test_settings_json():
    """Verify settings.json is valid and references existing files."""
    if not SETTINGS_FILE.exists():
        return ["settings.json not found"]

    errors = []
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"settings.json is not valid JSON: {e}"]

    # Check hooks section
    hooks = data.get("hooks", {})
    for event_name, event_groups in hooks.items():
        if not isinstance(event_groups, list):
            continue
        for group in event_groups:
            for hook in group.get("hooks", []):
                cmd = hook.get("command", "")
                # Extract the Python script path from the command
                match = re.search(r"python[3]?\s+(.+?)(?:\s|$)", cmd)
                if match:
                    script_path = match.group(1).split()[0]
                    # Skip paths with variables like $CLAUDE_FILE_PATH or $CLAUDE_PROJECT_DIR
                    if "$" in script_path:
                        continue
                    full_path = PROJECT_ROOT / script_path
                    if not full_path.exists():
                        errors.append(f"{event_name}: {script_path} not found")

    # Check statusLine
    status_line = data.get("statusLine", {})
    if status_line:
        cmd = status_line.get("command", "")
        match = re.search(r"python[3]?\s+(.+?)(?:\s|$)", cmd)
        if match:
            script_path = match.group(1)
            full_path = PROJECT_ROOT / script_path
            if not full_path.exists():
                errors.append(f"statusLine: {script_path} not found")

    # Check required lifecycle events
    expected_events = [
        "SessionStart", "UserPromptSubmit", "PreToolUse", "PermissionRequest",
        "PostToolUse", "PostToolUseFailure", "Notification", "SubagentStart",
        "SubagentStop", "Stop", "PreCompact", "SessionEnd",
    ]
    for event in expected_events:
        if event not in hooks:
            errors.append(f"Missing lifecycle event: {event}")

    return errors


def test_graceful_degradation():
    """Verify TTS and LLM modules degrade gracefully."""
    errors = []

    # Test pyttsx3 wrapper handles missing import
    tts_path = CLAUDE_DIR / "hooks" / "utils" / "tts" / "pyttsx3_tts.py"
    if tts_path.exists():
        source = tts_path.read_text(encoding="utf-8")
        if "except ImportError" not in source:
            errors.append("pyttsx3_tts.py missing ImportError handling")
        if "TTS_AVAILABLE" not in source:
            errors.append("pyttsx3_tts.py missing TTS_AVAILABLE flag")

    # Test anthropic wrapper handles missing import
    llm_path = CLAUDE_DIR / "hooks" / "utils" / "llm" / "anthropic_client.py"
    if llm_path.exists():
        source = llm_path.read_text(encoding="utf-8")
        if "except ImportError" not in source:
            errors.append("anthropic_client.py missing ImportError handling")
        if "ANTHROPIC_AVAILABLE" not in source:
            errors.append("anthropic_client.py missing ANTHROPIC_AVAILABLE flag")

    return errors


def test_cross_platform():
    """Verify cross-platform patterns are used."""
    errors = []

    # Check tts_queue.py for platform-aware locking
    tts_queue_path = CLAUDE_DIR / "hooks" / "utils" / "tts" / "tts_queue.py"
    if tts_queue_path.exists():
        source = tts_queue_path.read_text(encoding="utf-8")
        if "msvcrt" not in source:
            errors.append("tts_queue.py missing msvcrt (Windows locking)")
        if "fcntl" not in source:
            errors.append("tts_queue.py missing fcntl (Unix locking)")

    # Check platform_compat.py exists and has key functions
    compat_path = CLAUDE_DIR / "hooks" / "utils" / "platform_compat.py"
    if compat_path.exists():
        source = compat_path.read_text(encoding="utf-8")
        for func in ("which", "python_executable", "atomic_write", "is_pid_alive"):
            if f"def {func}" not in source:
                errors.append(f"platform_compat.py missing {func}()")

    return errors


def main():
    print("=" * 60)
    print("Hooks-Mastery Integration Test")
    print("=" * 60)
    print()

    total_errors = 0

    # 1. File existence
    print("[1/5] Checking file existence...")
    missing = test_files_exist()
    if missing:
        print(f"  FAIL: {len(missing)} files missing:")
        for f in missing:
            print(f"    - {f}")
        total_errors += len(missing)
    else:
        print(f"  PASS: All {len(EXPECTED_HOOKS) + len(EXPECTED_STATUS_LINES) + len(EXPECTED_OUTPUT_STYLES) + len(EXPECTED_AGENTS) + len(EXPECTED_COMMANDS)} files found")

    # 2. Python syntax
    print("[2/5] Checking Python syntax...")
    syntax_errors = test_python_syntax()
    if syntax_errors:
        print(f"  FAIL: {len(syntax_errors)} syntax errors:")
        for e in syntax_errors:
            print(f"    - {e}")
        total_errors += len(syntax_errors)
    else:
        print(f"  PASS: All Python files are syntactically valid")

    # 3. Settings.json
    print("[3/5] Checking settings.json...")
    settings_errors = test_settings_json()
    if settings_errors:
        print(f"  FAIL: {len(settings_errors)} settings issues:")
        for e in settings_errors:
            print(f"    - {e}")
        total_errors += len(settings_errors)
    else:
        print(f"  PASS: settings.json is valid with all 12 lifecycle events")

    # 4. Graceful degradation
    print("[4/5] Checking graceful degradation...")
    degradation_errors = test_graceful_degradation()
    if degradation_errors:
        print(f"  FAIL: {len(degradation_errors)} degradation issues:")
        for e in degradation_errors:
            print(f"    - {e}")
        total_errors += len(degradation_errors)
    else:
        print(f"  PASS: TTS and LLM modules degrade gracefully")

    # 5. Cross-platform
    print("[5/5] Checking cross-platform support...")
    platform_errors = test_cross_platform()
    if platform_errors:
        print(f"  FAIL: {len(platform_errors)} platform issues:")
        for e in platform_errors:
            print(f"    - {e}")
        total_errors += len(platform_errors)
    else:
        print(f"  PASS: Cross-platform patterns verified")

    # Summary
    print()
    print("=" * 60)
    if total_errors == 0:
        print("ALL TESTS PASSED")
    else:
        print(f"FAILED: {total_errors} total issues found")
    print("=" * 60)

    sys.exit(1 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()
