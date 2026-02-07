"""
Project Invariant Validator
Purpose: Validates that code changes don't violate your project's defined invariants
Triggers: Called after Write/Edit tools on code files, or manually via /check-invariants

CONFIGURATION:
Edit the INVARIANTS list below to define your project's invariants.
Each invariant should have:
  - id: Unique identifier (e.g., "INV-1")
  - name: Human-readable name
  - description: What this invariant protects
  - patterns: List of (regex, violation_message) tuples to detect violations
  - components: List of directory patterns where this applies (["*"] for all)
  - severity: "error" (blocks) or "warning" (informational)

USAGE:
  Manual:   python invariant_validator.py <file_path>
  All:      python invariant_validator.py --all
  Hook:     Add to .claude/settings.json hooks for automatic checking

EXAMPLE INVARIANTS:
  - No debug statements in production code
  - No raw SQL queries (use ORM)
  - No hardcoded secrets
  - Component isolation rules
"""

import sys
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Log file for this validator
LOG_FILE = ".claude/hooks/validators/invariant_validator.log"

# =============================================================================
# CONFIGURE YOUR INVARIANTS HERE
# =============================================================================

# Example invariants - customize or replace for your project
INVARIANTS: List[Dict[str, Any]] = [
    # {
    #     "id": "INV-1",
    #     "name": "No Debug Statements",
    #     "description": "Debug statements should not be in production code",
    #     "patterns": [
    #         (r"console\.log\(", "console.log found - use logger instead"),
    #         (r"debugger;", "debugger statement found"),
    #         (r"\bprint\s*\(", "print() found - use logger instead"),
    #     ],
    #     "components": ["src/*"],  # Only check src directory
    #     "file_extensions": [".js", ".ts", ".py"],
    #     "severity": "error",
    # },
    # {
    #     "id": "INV-2",
    #     "name": "No Hardcoded Secrets",
    #     "description": "Secrets should come from environment variables",
    #     "patterns": [
    #         (r"['\"]sk-[a-zA-Z0-9]{20,}['\"]", "Possible API key found"),
    #         (r"password\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password found"),
    #         (r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]", "Hardcoded API key found"),
    #     ],
    #     "components": ["*"],
    #     "file_extensions": [".py", ".js", ".ts", ".json", ".yaml", ".yml"],
    #     "severity": "error",
    # },
]

# File extensions to validate (if not specified per-invariant)
DEFAULT_EXTENSIONS = {'.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java'}

# Directories to skip
SKIP_DIRS = {'node_modules', 'venv', '.venv', '__pycache__', '.git', 'dist', 'build', 'target', '.next'}


# =============================================================================
# VALIDATION LOGIC (Usually no need to modify below this line)
# =============================================================================

def find_project_root() -> Path:
    """Find the project root by looking for common markers."""
    current = Path(__file__).resolve()
    markers = ['pyproject.toml', 'package.json', 'Cargo.toml', 'go.mod', '.git']

    for parent in [current] + list(current.parents):
        for marker in markers:
            if (parent / marker).exists():
                return parent
    return Path.cwd()


PROJECT_ROOT = find_project_root()


def matches_component(file_path: str, components: List[str]) -> bool:
    """Check if a file path matches any of the component patterns."""
    if not components or "*" in components:
        return True

    path_str = str(file_path).replace("\\", "/")

    for component in components:
        # Convert glob-like pattern to regex
        pattern = component.replace("*", ".*").replace("/", r"[\\/]")
        if re.search(pattern, path_str, re.IGNORECASE):
            return True

    return False


def get_file_extension(file_path: str) -> str:
    """Get the file extension."""
    return os.path.splitext(file_path)[1].lower()


def check_invariant(content: str, lines: List[str], invariant: Dict, file_path: str) -> List[str]:
    """Check a single invariant against file content."""
    issues = []

    # Check file extension
    file_ext = get_file_extension(file_path)
    allowed_extensions = invariant.get("file_extensions", DEFAULT_EXTENSIONS)
    if file_ext not in allowed_extensions:
        return issues

    # Check component match
    if not matches_component(file_path, invariant.get("components", ["*"])):
        return issues

    # Check patterns
    for pattern, message in invariant.get("patterns", []):
        for i, line in enumerate(lines, 1):
            # Skip comments (basic detection)
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("/*"):
                continue

            if re.search(pattern, line, re.IGNORECASE):
                severity = invariant.get("severity", "error")
                inv_id = invariant.get("id", "INV-?")
                issues.append(f"{inv_id} (Line {i}, {severity}): {message}")

    return issues


def validate(target_path: str) -> dict:
    """
    Validate a file against all defined invariants.

    Args:
        target_path: Path to file being validated

    Returns:
        dict with 'valid' (bool) and 'message' (str)
    """
    issues = []

    # Check if we have any invariants defined
    if not INVARIANTS:
        return {
            "valid": True,
            "message": f"No invariants configured. See invariant_validator.py to add project invariants."
        }

    # Skip files in excluded directories
    path_str = str(target_path).replace("\\", "/")
    for skip_dir in SKIP_DIRS:
        if f"/{skip_dir}/" in path_str or path_str.startswith(f"{skip_dir}/"):
            return {
                "valid": True,
                "message": f"Skipped (excluded directory): {os.path.basename(target_path)}"
            }

    # Skip test files
    if "/tests/" in path_str or "/test/" in path_str or "_test." in path_str or ".test." in path_str:
        return {
            "valid": True,
            "message": f"Skipped (test file): {os.path.basename(target_path)}"
        }

    try:
        # Check file exists
        if not os.path.exists(target_path):
            issues.append(f"File not found: {target_path}")
            log_result(target_path, issues)
            return {"valid": False, "message": f"Validation failed: {issues[0]}"}

        # Read content
        with open(target_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        lines = content.splitlines()

        # Check each invariant
        for invariant in INVARIANTS:
            inv_issues = check_invariant(content, lines, invariant, target_path)
            issues.extend(inv_issues)

    except Exception as e:
        issues.append(f"Validation error: {str(e)}")

    # Log results
    log_result(target_path, issues)

    # Return result
    if issues:
        # Separate errors from warnings
        errors = [i for i in issues if "error" in i.lower()]
        warnings = [i for i in issues if "warning" in i.lower()]

        message = f"Invariant violations in {os.path.basename(target_path)}:\n"
        if errors:
            message += "\n".join(f"  [ERROR]{i}" for i in errors)
        if warnings:
            message += "\n".join(f"  [WARN]{i}" for i in warnings)

        # Only fail on errors, not warnings
        return {
            "valid": len(errors) == 0,
            "message": message
        }

    return {
        "valid": True,
        "message": f"All invariants satisfied: {os.path.basename(target_path)}"
    }


def validate_all() -> dict:
    """Validate all source files in the project."""
    all_issues = []
    files_checked = 0
    files_passed = 0

    if not INVARIANTS:
        return {
            "valid": True,
            "message": "No invariants configured. Edit invariant_validator.py to add project invariants."
        }

    # Find all source files
    for ext in DEFAULT_EXTENSIONS:
        for source_file in PROJECT_ROOT.rglob(f"*{ext}"):
            # Skip excluded directories
            path_str = str(source_file).replace("\\", "/")
            if any(f"/{skip}/" in path_str for skip in SKIP_DIRS):
                continue

            result = validate(str(source_file))
            files_checked += 1

            if result["valid"]:
                files_passed += 1
            else:
                all_issues.append(result["message"])

    # Summary
    if all_issues:
        summary = f"Invariant Check: {files_passed}/{files_checked} files passed\n\n"
        summary += "\n\n".join(all_issues)
        return {"valid": False, "message": summary}

    return {
        "valid": True,
        "message": f"All invariants satisfied across {files_checked} files"
    }


def log_result(target_path: str, issues: list):
    """Log validation results for observability."""
    try:
        log_path = PROJECT_ROOT / LOG_FILE
        os.makedirs(log_path.parent, exist_ok=True)

        with open(log_path, "a", encoding='utf-8') as f:
            f.write(f"\n[{datetime.now()}] Target: {target_path}\n")
            f.write(f"Result: {'FAIL' if issues else 'PASS'}\n")
            if issues:
                for issue in issues:
                    f.write(f"  - {issue}\n")
            f.write("-" * 60 + "\n")
    except Exception as e:
        print(f"Warning: Could not write to log file: {e}", file=sys.stderr)


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    # Fix Windows console encoding
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    if len(sys.argv) < 2:
        print("Project Invariant Validator")
        print("=" * 40)
        print("\nUsage:")
        print("  python invariant_validator.py <file_path>  - Check single file")
        print("  python invariant_validator.py --all        - Check all source files")
        print("\nConfiguration:")
        print("  Edit the INVARIANTS list at the top of this file")
        print("  to define your project's invariants.")
        print("\nCurrent Status:")
        if INVARIANTS:
            print(f"  {len(INVARIANTS)} invariant(s) configured:")
            for inv in INVARIANTS:
                print(f"    - {inv.get('id', '?')}: {inv.get('name', 'Unnamed')}")
        else:
            print("  No invariants configured yet.")
        sys.exit(1)

    target = sys.argv[1]

    if target == "--all":
        result = validate_all()
    else:
        result = validate(target)

    # Output structured JSON for PostToolUse hook protocol
    import json
    if result["valid"]:
        print(json.dumps({"decision": "approve", "reason": result["message"]}))
    else:
        print(json.dumps({"decision": "block", "reason": result["message"]}))
    sys.exit(0)
