"""
Markdown Validator
Purpose: Validates markdown files for formatting, structure, and common issues
Triggers: Called after Write/Edit tools on .md files

USAGE IN YAML FRONTMATTER:
hooks:
  post_tool_use:
    - tools: ["write", "edit"]
      command: "python ${CLAUDE_PROJECT_DIR}/.claude/hooks/validators/markdown_validator.py $CLAUDE_TOOL_INPUT_PATH"
"""

import sys
import os
import re
from datetime import datetime

LOG_FILE = ".claude/hooks/validators/markdown_validator.log"

def validate(target_path: str) -> dict:
    """
    Validate markdown file for formatting and structure.

    Args:
        target_path: Path to markdown file being validated

    Returns:
        dict with 'valid' (bool) and 'message' (str)
    """
    # Skip non-markdown files silently
    if not target_path.lower().endswith('.md'):
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
            issues.append("Markdown file is empty")

        # Check 3: Read content
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()

        # Check 4: Headers follow convention
        # Valid: # Title, ## Section, ### Subsection
        # Invalid: #Title (no space), ######### (too many)
        header_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
        invalid_headers = []
        for i, line in enumerate(lines, 1):
            if line.startswith('#'):
                if not header_pattern.match(line):
                    invalid_headers.append(f"Line {i}: '{line.strip()}'")

        if invalid_headers:
            issues.append(f"Invalid header format (need space after #):\n  " + "\n  ".join(invalid_headers[:3]))
            if len(invalid_headers) > 3:
                issues.append(f"... and {len(invalid_headers) - 3} more")

        # Check 5: Code blocks are properly closed
        code_block_pattern = re.compile(r'^```')
        code_blocks = [i + 1 for i, line in enumerate(lines) if code_block_pattern.match(line)]
        if len(code_blocks) % 2 != 0:
            issues.append(f"Unclosed code block (found {len(code_blocks)} ``` markers, expected even number)")

        # Check 6: Check for broken internal links (basic check)
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        internal_links = []
        for i, line in enumerate(lines, 1):
            matches = link_pattern.findall(line)
            for text, url in matches:
                # Check if it's an internal link (not http/https)
                if not url.startswith(('http://', 'https://', '#', 'mailto:')):
                    internal_links.append((i, url))

        # Check if internal link files exist (relative to markdown file)
        broken_links = []
        base_dir = os.path.dirname(target_path)
        for line_num, link_url in internal_links:
            # Remove anchor if present
            link_path = link_url.split('#')[0]
            if link_path:  # Skip pure anchors
                full_path = os.path.normpath(os.path.join(base_dir, link_path))
                if not os.path.exists(full_path):
                    broken_links.append(f"Line {line_num}: {link_url}")

        if broken_links:
            issues.append(f"Broken internal links:\n  " + "\n  ".join(broken_links[:3]))
            if len(broken_links) > 3:
                issues.append(f"... and {len(broken_links) - 3} more")

        # Check 7: No trailing whitespace
        trailing_whitespace = [i + 1 for i, line in enumerate(lines) if line and line[-1] in (' ', '\t')]
        if trailing_whitespace:
            issues.append(f"Lines with trailing whitespace: {trailing_whitespace[:5]}")

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
        "message": f"Markdown validation passed for {os.path.basename(target_path)}"
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
        print("Usage: python markdown_validator.py <path_to_markdown_file>")
        sys.exit(1)

    target = sys.argv[1]
    result = validate(target)
    print(result["message"])
    sys.exit(0 if result["valid"] else 1)
