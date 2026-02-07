#!/usr/bin/env python3
"""
Command-level Stop hook validator: verify a new file was created.

Used by plan-w-team and other self-validating commands to ensure
expected output files were actually created.

CLI arguments (NOT stdin — this is args-driven):
  -d/--directory   Directory to check (default: specs)
  -e/--extension   File extension (default: .md)
  --max-age        Max file age in minutes (default: 5)

Exit code 0 = pass (file found)
Exit code 1 = BLOCK (no file found — force Claude to create it)
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def find_new_file_git(directory: str, extension: str) -> str | None:
    """Check git status for new files in directory."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", f"{directory}/"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            return None

        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            # New/untracked files start with ?? or A
            status = line[:2].strip()
            filepath = line[3:].strip().strip('"')
            if status in ("??", "A", "AM") and filepath.endswith(extension):
                return filepath
    except Exception:
        pass
    return None


def find_new_file_mtime(directory: str, extension: str, max_age_minutes: float) -> str | None:
    """Check for recently modified files in directory."""
    dir_path = Path(directory)
    if not dir_path.exists():
        return None

    now = time.time()
    max_age_seconds = max_age_minutes * 60

    newest = None
    newest_mtime = 0

    for f in dir_path.glob(f"*{extension}"):
        mtime = f.stat().st_mtime
        age = now - mtime
        if age < max_age_seconds and mtime > newest_mtime:
            newest = str(f)
            newest_mtime = mtime

    return newest


def main():
    parser = argparse.ArgumentParser(description="Validate new file creation")
    parser.add_argument("-d", "--directory", default="specs", help="Directory to check")
    parser.add_argument("-e", "--extension", default=".md", help="File extension")
    parser.add_argument("--max-age", type=float, default=5, help="Max file age in minutes")
    args = parser.parse_args()

    # Try git status first, then fall back to mtime
    found = find_new_file_git(args.directory, args.extension)
    if not found:
        found = find_new_file_mtime(args.directory, args.extension, args.max_age)

    if found:
        output = {
            "decision": "continue",
            "message": f"New file found: {found}",
        }
        print(json.dumps(output))
        sys.exit(0)
    else:
        output = {
            "decision": "block",
            "reason": (
                f"VALIDATION FAILED: No new file found in {args.directory}/*{args.extension}.\n\n"
                f"ACTION REQUIRED: Create the plan file in the {args.directory}/ directory."
            ),
        }
        print(json.dumps(output))
        sys.exit(1)


if __name__ == "__main__":
    main()
