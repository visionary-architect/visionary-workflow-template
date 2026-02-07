#!/usr/bin/env python3
"""
Command-level Stop hook validator: verify file contains required sections.

Used by plan-w-team and other self-validating commands to ensure
output files contain all required content sections.

CLI arguments:
  -d/--directory   Directory to check (default: specs)
  -e/--extension   File extension (default: .md)
  --max-age        Max file age in minutes (default: 5)
  --contains STR   Required string (can be repeated)

Exit code 0 = pass (all strings found)
Exit code 1 = BLOCK (missing strings)
"""
import argparse
import json
import sys
import time
from pathlib import Path


def find_newest_file(directory: str, extension: str, max_age_minutes: float) -> Path | None:
    """Find the newest file in directory matching extension and age."""
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
            newest = f
            newest_mtime = mtime

    return newest


def main():
    parser = argparse.ArgumentParser(description="Validate file contains required sections")
    parser.add_argument("-d", "--directory", default="specs", help="Directory to check")
    parser.add_argument("-e", "--extension", default=".md", help="File extension")
    parser.add_argument("--max-age", type=float, default=5, help="Max file age in minutes")
    parser.add_argument("--contains", action="append", default=[], help="Required string (repeatable)")
    args = parser.parse_args()

    if not args.contains:
        # No requirements specified — pass
        print(json.dumps({"decision": "continue", "message": "No content requirements specified"}))
        sys.exit(0)

    # Find newest file
    target = find_newest_file(args.directory, args.extension, args.max_age)
    if not target:
        output = {
            "decision": "block",
            "reason": (
                f"VALIDATION FAILED: No recent file found in {args.directory}/*{args.extension}.\n\n"
                f"ACTION REQUIRED: Create the file first."
            ),
        }
        print(json.dumps(output))
        sys.exit(1)

    # Read file content
    try:
        content = target.read_text(encoding="utf-8")
    except OSError as e:
        output = {
            "decision": "block",
            "reason": f"VALIDATION FAILED: Cannot read {target}: {e}",
        }
        print(json.dumps(output))
        sys.exit(1)

    # Check for required strings
    missing = [s for s in args.contains if s not in content]

    if not missing:
        output = {
            "decision": "continue",
            "message": f"All {len(args.contains)} required sections found in {target.name}",
        }
        print(json.dumps(output))
        sys.exit(0)
    else:
        missing_list = "\n  - ".join(missing)
        output = {
            "decision": "block",
            "reason": (
                f"VALIDATION FAILED: Missing {len(missing)} required section(s) in {target.name}.\n\n"
                f"MISSING:\n  - {missing_list}\n\n"
                f"ACTION REQUIRED: Add the missing sections to the file."
            ),
        }
        print(json.dumps(output))
        sys.exit(1)


if __name__ == "__main__":
    main()
