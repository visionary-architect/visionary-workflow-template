"""
JSON Validator
Purpose: Validates JSON files for syntax errors, duplicate keys, and structure
Triggers: Called after Write/Edit tools on .json files

USAGE IN YAML FRONTMATTER:
hooks:
  post_tool_use:
    - tools: ["write", "edit"]
      command: "python ${CLAUDE_PROJECT_DIR}/.claude/hooks/validators/json_validator.py $CLAUDE_TOOL_INPUT_PATH"
"""

import sys
import os
import json
from datetime import datetime
from collections import Counter

LOG_FILE = ".claude/hooks/validators/json_validator.log"

def validate(target_path: str) -> dict:
    """
    Validate JSON file for syntax and common issues.

    Args:
        target_path: Path to JSON file being validated

    Returns:
        dict with 'valid' (bool) and 'message' (str)
    """
    # Skip non-JSON files silently
    if not target_path.lower().endswith('.json'):
        return {"valid": True, "message": ""}

    issues = []

    try:
        # Check 1: File exists
        if not os.path.exists(target_path):
            issues.append(f"File not found: {target_path}")
            log_result(target_path, issues)
            return {
                "valid": False,
                "message": issues[0]
            }

        # Check 2: File is not empty
        if os.path.getsize(target_path) == 0:
            issues.append("JSON file is empty")
            log_result(target_path, issues)
            return {
                "valid": False,
                "message": "Resolve these errors:\n- JSON file is empty"
            }

        # Check 3: Valid JSON syntax
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            issues.append(f"Invalid JSON syntax at line {e.lineno}, column {e.colno}: {e.msg}")
            log_result(target_path, issues)
            return {
                "valid": False,
                "message": f"Resolve these errors in {os.path.basename(target_path)}:\n- {issues[0]}"
            }

        # Check 4: Detect duplicate keys (re-parse with object_pairs_hook)
        def check_duplicate_keys(pairs):
            keys = [key for key, value in pairs]
            duplicates = [key for key, count in Counter(keys).items() if count > 1]
            if duplicates:
                issues.append(f"Duplicate keys found: {', '.join(duplicates)}")
            return dict(pairs)

        with open(target_path, 'r', encoding='utf-8') as f:
            json.load(f, object_pairs_hook=check_duplicate_keys)

        # Check 5: Warn if file is very large
        if os.path.getsize(target_path) > 1_000_000:  # 1MB
            issues.append(f"Warning: Large JSON file ({os.path.getsize(target_path) // 1024} KB)")

    except Exception as e:
        issues.append(f"Validation error: {str(e)}")

    # Log results
    log_result(target_path, issues)

    # Return structured result
    if issues:
        return {
            "valid": False,
            "message": f"Resolve these errors in {os.path.basename(target_path)}:\n" + "\n".join(f"- {i}" for i in issues)
        }

    return {
        "valid": True,
        "message": f"JSON validation passed for {os.path.basename(target_path)}"
    }

def log_result(target_path: str, issues: list):
    """Log validation results for observability."""
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a", encoding='utf-8') as f:
            f.write(f"\n[{datetime.now()}] Target: {target_path}\n")
            f.write(f"Result: {'FAIL' if issues else 'PASS'}\n")
            if issues:
                f.write(f"Issues: {issues}\n")
            f.write("-" * 40 + "\n")
    except Exception:
        pass  # Don't break validation if logging fails

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python json_validator.py <path_to_json_file>")
        sys.exit(1)

    target = sys.argv[1]
    result = validate(target)
    print(result["message"])
    sys.exit(0 if result["valid"] else 1)
