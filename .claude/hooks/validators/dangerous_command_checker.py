#!/usr/bin/env python3
"""
Check for dangerous Bash commands and warn before execution.

This PreToolUse hook runs before Bash commands and checks for potentially
destructive operations that could cause data loss.

Exit codes:
  0 - Command is safe, proceed
  2 - Command is dangerous, blocked (Claude Code will show warning)

Environment variables (set by Claude Code):
  CLAUDE_TOOL_NAME - The tool being used (we check for "Bash")
  CLAUDE_BASH_COMMAND - The command about to be executed (via stdin or env)
"""
import json
import os
import re
import sys

# Dangerous command patterns
DANGEROUS_PATTERNS = [
    # Git destructive operations
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard discards all uncommitted changes"),
    (r"\bgit\s+clean\s+-[fd]+\b", "git clean removes untracked files permanently"),
    (r"\bgit\s+checkout\s+\.\b", "git checkout . discards all working directory changes"),
    (r"\bgit\s+push\s+.*--force\b", "git push --force can overwrite remote history"),
    (r"\bgit\s+push\s+.*-f\b", "git push -f can overwrite remote history"),
    (r"\bgit\s+branch\s+-D\b", "git branch -D force-deletes branches"),
    (r"\bgit\s+stash\s+drop\b", "git stash drop permanently removes stashed changes"),
    (r"\bgit\s+stash\s+clear\b", "git stash clear removes all stashed changes"),

    # File deletion
    (r"\brm\s+-rf?\s+/\b", "rm -rf / is catastrophically dangerous"),
    (r"\brm\s+-rf?\s+\*\b", "rm -rf * removes all files in current directory"),
    (r"\brm\s+-rf?\s+\.\.\b", "rm -rf .. removes parent directory"),
    (r"\brm\s+-rf?\s+~\b", "rm -rf ~ removes entire home directory"),
    (r"\bdel\s+/[sq]\s+", "del /s /q recursively deletes files on Windows"),
    (r"\brmdir\s+/[sq]\s+", "rmdir /s /q recursively removes directories on Windows"),

    # Database operations
    (r"\bDROP\s+DATABASE\b", "DROP DATABASE permanently removes database", re.IGNORECASE),
    (r"\bDROP\s+TABLE\b", "DROP TABLE permanently removes table", re.IGNORECASE),
    (r"\bTRUNCATE\s+TABLE\b", "TRUNCATE TABLE removes all data from table", re.IGNORECASE),
    (r"\bDELETE\s+FROM\s+\w+\s*;", "DELETE without WHERE removes all rows", re.IGNORECASE),

    # System operations
    (r"\bsudo\s+rm\b", "sudo rm can remove protected system files"),
    (r"\bchmod\s+777\b", "chmod 777 makes files world-writable (security risk)"),
    (r"\bchmod\s+-R\s+777\b", "chmod -R 777 recursively makes everything writable"),

    # Docker/Container operations
    (r"\bdocker\s+system\s+prune\s+-a\b", "docker system prune -a removes all unused images"),
    (r"\bdocker\s+rm\s+-f\b", "docker rm -f force-removes running containers"),
    (r"\bdocker\s+rmi\s+-f\b", "docker rmi -f force-removes images"),

    # Pip/Package operations that might break environment
    (r"\bpip\s+uninstall\s+.*-y\b", "pip uninstall -y removes packages without confirmation"),
]


def main():
    """Check if the Bash command is dangerous."""
    # Get command from environment or stdin
    command = os.environ.get("CLAUDE_BASH_COMMAND", "")

    if not command:
        # Try reading from stdin (hook input format)
        try:
            stdin_data = sys.stdin.read()
            if stdin_data:
                data = json.loads(stdin_data)
                command = data.get("tool_input", {}).get("command", "")
        except Exception:
            pass

    if not command:
        # No command to check
        sys.exit(0)

    # Check against dangerous patterns
    warnings = []
    for pattern_tuple in DANGEROUS_PATTERNS:
        if len(pattern_tuple) == 3:
            pattern, description, flags = pattern_tuple
        else:
            pattern, description = pattern_tuple
            flags = 0

        if re.search(pattern, command, flags):
            warnings.append(description)

    if warnings:
        print("=" * 60)
        print("DANGEROUS COMMAND DETECTED")
        print("=" * 60)
        print()
        print(f"Command: {command[:200]}")
        print()
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
        print()
        print("This command may cause irreversible data loss.")
        print("=" * 60)

        # Exit with code 2 to block the command
        # Claude Code will show this output as a warning
        sys.exit(2)

    # Command is safe
    sys.exit(0)


if __name__ == "__main__":
    main()
