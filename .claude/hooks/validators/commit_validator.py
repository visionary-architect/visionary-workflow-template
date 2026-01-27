"""
Git Commit Validator
Purpose: Validates git commit messages for conventional commits format and required elements
Triggers: Called during commit operations (via commit-push-pr command)

USAGE IN YAML FRONTMATTER:
hooks:
  post_tool_use:
    - tools: ["bash"]
      command: "python ${CLAUDE_PROJECT_DIR}/.claude/hooks/validators/commit_validator.py"

This validator checks the most recent commit message after a commit is created.
"""

import sys
import os
import re
import subprocess
from datetime import datetime

LOG_FILE = ".claude/hooks/validators/commit_validator.log"

# Conventional commit types
VALID_TYPES = [
    'feat', 'fix', 'docs', 'style', 'refactor',
    'perf', 'test', 'build', 'ci', 'chore', 'revert'
]

def validate(target_path: str = None) -> dict:
    """
    Validate the most recent git commit message.

    Args:
        target_path: Not used for commit validation (validates latest commit)

    Returns:
        dict with 'valid' (bool) and 'message' (str)
    """
    issues = []

    try:
        # Get the most recent commit message
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=%B'],
            capture_output=True,
            text=True,
            check=True
        )
        commit_message = result.stdout.strip()

        if not commit_message:
            issues.append("Commit message is empty")
            log_result("latest commit", issues)
            return {
                "valid": False,
                "message": "Resolve these errors:\n- Commit message is empty"
            }

        lines = commit_message.split('\n')
        subject = lines[0]
        body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ""

        # Check 1: Conventional commit format
        # Format: type(scope): description
        # or: type: description
        # Scope can contain: letters, numbers, hyphens, commas (e.g., 1-A, 2-B,2-C, control-plane)
        conventional_pattern = re.compile(r'^([a-z]+)(\([a-zA-Z0-9,\-]+\))?: .+')
        match = conventional_pattern.match(subject)

        if not match:
            issues.append(
                f"Subject line doesn't follow conventional commits format\n"
                f"  Expected: 'type(scope): description' or 'type: description'\n"
                f"  Got: '{subject}'\n"
                f"  Valid types: {', '.join(VALID_TYPES)}"
            )
        else:
            commit_type = match.group(1)
            if commit_type not in VALID_TYPES:
                issues.append(
                    f"Invalid commit type '{commit_type}'\n"
                    f"  Valid types: {', '.join(VALID_TYPES)}"
                )

        # Check 2: Subject line length (recommended: 50 chars, max: 72)
        if len(subject) > 72:
            issues.append(f"Subject line too long ({len(subject)} chars, max 72)")
        elif len(subject) > 50:
            # Warning, not an error
            issues.append(f"Warning: Subject line is {len(subject)} chars (recommended: ≤50)")

        # Check 3: Subject line should not end with period
        if subject.endswith('.'):
            issues.append("Subject line should not end with a period")

        # Check 4: Subject should be in imperative mood (basic check)
        # Common non-imperative patterns
        non_imperative_patterns = [
            r': (added|updated|fixed|removed|changed|created|deleted)',
            r': (adding|updating|fixing|removing|changing|creating|deleting)'
        ]
        for pattern in non_imperative_patterns:
            if re.search(pattern, subject.lower()):
                issues.append(
                    "Subject should use imperative mood\n"
                    "  Use 'add' not 'added/adding', 'fix' not 'fixed/fixing', etc."
                )
                break

        # Check 5: Co-Authored-By line present (required for this template)
        if 'Co-Authored-By:' not in commit_message:
            issues.append(
                "Missing 'Co-Authored-By:' line\n"
                "  Add: Co-Authored-By: visionary-architect"
            )

        # Check 6: If body exists, check for blank line after subject
        if len(lines) > 1 and lines[1] != '':
            issues.append("Missing blank line between subject and body")

        # Check 7: Body lines should be wrapped at 72 characters
        if body:
            long_lines = []
            for i, line in enumerate(body.split('\n'), 2):
                # Skip Co-Authored-By and other trailers
                if line.startswith('Co-Authored-By:') or line.startswith('Signed-off-by:'):
                    continue
                if len(line) > 72 and line.strip():
                    long_lines.append(f"Line {i}: {len(line)} chars")

            if long_lines:
                issues.append(f"Body lines too long (max 72 chars):\n  " + "\n  ".join(long_lines[:3]))

    except subprocess.CalledProcessError:
        issues.append("No git repository or no commits found")
    except Exception as e:
        issues.append(f"Validation error: {str(e)}")

    # Log results
    log_result("latest commit", issues)

    # Return structured result
    if issues:
        return {
            "valid": False,
            "message": f"Commit message validation failed:\n" + "\n".join(f"- {i}" for i in issues)
        }

    return {
        "valid": True,
        "message": "Commit message validation passed"
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
    # Can optionally pass target_path, but not used for commit validation
    target = sys.argv[1] if len(sys.argv) > 1 else None
    result = validate(target)
    print(result["message"])
    sys.exit(0 if result["valid"] else 1)
