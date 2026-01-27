"""
Validator Template
Purpose: [Describe what this validates - e.g., "Validates JSON files for syntax and required fields"]
Triggers: [When should this run - e.g., "Called after Write/Edit tools on .json files"]

USAGE:
1. Copy this file to [name]_validator.py
2. Fill in the validation logic section
3. Update the Purpose and Triggers above
4. Reference in command/agent YAML frontmatter:

   hooks:
     post_tool_use:
       - tools: ["write", "edit"]
         command: "python ${CLAUDE_PROJECT_DIR}/.claude/hooks/validators/[name]_validator.py $CLAUDE_TOOL_INPUT_PATH"

STRUCTURE:
- validate(target_path) - Main validation logic, returns {"valid": bool, "message": str}
- log_result() - Logs validation attempts for debugging
- __main__ - Command-line interface

BEST PRACTICES:
- Be specific in error messages
- Always return a result, never crash
- Log everything for debugging
- Handle edge cases gracefully
- Keep validation focused (one concern per validator)
"""

import sys
import os
from datetime import datetime

# Log file for this validator (will be gitignored)
LOG_FILE = ".claude/hooks/validators/TEMPLATE_validator.log"

def validate(target_path: str) -> dict:
    """
    Validate the target and return results.

    Args:
        target_path: Path to file/resource being validated

    Returns:
        dict with 'valid' (bool) and 'message' (str)
    """
    issues = []

    # ============================================
    # ADD YOUR VALIDATION LOGIC HERE
    # ============================================

    # Example validation structure:
    try:
        # Check 1: File exists
        if not os.path.exists(target_path):
            issues.append(f"File not found: {target_path}")
            # Return early if file doesn't exist
            log_result(target_path, issues)
            return {
                "valid": False,
                "message": f"Validation failed: {issues[0]}"
            }

        # Check 2: File is not empty
        if os.path.getsize(target_path) == 0:
            issues.append("File is empty")

        # Check 3: Read content
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check 4: Example - no TODO comments
        if "TODO" in content.upper():
            issues.append("File contains unresolved TODO comments")

        # Check 5: Example - no trailing whitespace
        lines_with_trailing = [
            i + 1 for i, line in enumerate(content.splitlines())
            if line and line[-1].isspace()
        ]
        if lines_with_trailing:
            issues.append(f"Lines with trailing whitespace: {lines_with_trailing}")

        # Add more validation checks here...
        # if not some_condition:
        #     issues.append("Description of what's wrong")

    except Exception as e:
        # Don't crash - return validation failure
        issues.append(f"Validation error: {str(e)}")

    # ============================================
    # END VALIDATION LOGIC
    # ============================================

    # Log results for debugging
    log_result(target_path, issues)

    # Return structured result
    if issues:
        return {
            "valid": False,
            "message": f"Validation failed for {os.path.basename(target_path)}:\n" + "\n".join(f"- {i}" for i in issues)
        }

    return {
        "valid": True,
        "message": f"Validation passed for {os.path.basename(target_path)}"
    }

def log_result(target_path: str, issues: list):
    """Log validation results for observability and debugging."""
    try:
        # Create log directory if it doesn't exist
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

        with open(LOG_FILE, "a", encoding='utf-8') as f:
            f.write(f"\n[{datetime.now()}] Target: {target_path}\n")
            f.write(f"Result: {'FAIL' if issues else 'PASS'}\n")
            if issues:
                f.write(f"Issues: {issues}\n")
            f.write("-" * 40 + "\n")
    except Exception as e:
        # Logging failure shouldn't break validation
        print(f"Warning: Could not write to log file: {e}", file=sys.stderr)

if __name__ == "__main__":
    # Command-line interface for manual testing
    if len(sys.argv) < 2:
        print("Usage: python TEMPLATE_validator.py <target_path>")
        print("Example: python TEMPLATE_validator.py path/to/file.txt")
        sys.exit(1)

    target = sys.argv[1]
    result = validate(target)

    # Print result message
    print(result["message"])

    # Exit with appropriate code
    sys.exit(0 if result["valid"] else 1)
