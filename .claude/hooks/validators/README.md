# Validators Folder

> Self-validating agents use Python scripts to programmatically verify their output

## What Are Validators?

Validators are Python scripts that check whether agent/command output meets specific criteria. They provide **deterministic validation** - clear pass/fail results with detailed feedback.

**Think of validators as:**
- Quality gates that code must pass through
- Automated reviewers that never get tired
- Consistency enforcers for team standards
- Audit trails for compliance

---

## When to Use Validators

### ✅ Good Use Cases

**Use validators when you need:**
- **Consistency** - Enforce formatting standards (conventional commits, code style)
- **Compliance** - Ensure required elements are present (licenses, headers, Co-Authored-By)
- **Correctness** - Verify syntax and structure (valid JSON, proper markdown)
- **Quality gates** - Block progression if criteria aren't met
- **Audit trails** - Log validation history for review

### ❌ When Validators Are Overkill

**Skip validators for:**
- One-off tasks that won't be repeated
- Exploratory coding where rules aren't established
- Simple projects where manual review is sufficient
- Cases where flexibility is more important than consistency

---

## How Validators Work

### 1. **Hook Triggers Validator**

When you add a hook to a command/agent:
```yaml
hooks:
  post_tool_use:
    - tools: ["write"]
      command: "python ${CLAUDE_PROJECT_DIR}/.claude/hooks/validators/my_validator.py $CLAUDE_TOOL_INPUT_PATH"
```

### 2. **Validator Checks Output**

The Python script receives the file path and validates it:
```python
def validate(target_path: str) -> dict:
    issues = []

    # Your validation logic here
    if not meets_criteria(target_path):
        issues.append("Description of problem")

    return {"valid": len(issues) == 0, "message": "..."}
```

### 3. **Returns Structured Result**

```json
{
  "valid": true,  // or false
  "message": "Validation passed"  // or error details
}
```

### 4. **Logs for Observability**

All validation attempts are logged to `.log` files with timestamps for debugging and auditing.

---

## Example Validators Included

This folder includes three example validators:

### 1. `json_validator.py`
**Purpose:** Validates JSON files
**Checks:**
- Valid JSON syntax
- No duplicate keys
- File is not empty

**Use for:** Configuration files, API responses, data files

### 2. `markdown_validator.py`
**Purpose:** Validates markdown formatting
**Checks:**
- Headers follow convention (# Title, ## Section)
- No broken internal links
- Code blocks are properly closed

**Use for:** Documentation, README files, guides

### 3. `commit_validator.py`
**Purpose:** Validates git commit messages
**Checks:**
- Follows conventional commits format
- Has Co-Authored-By line
- Message length is appropriate

**Use for:** Ensuring consistent commit history

---

## Creating Your Own Validator

### Step 1: Copy the Template

```bash
cp TEMPLATE_validator.py my_validator.py
```

### Step 2: Define Validation Criteria

Ask yourself:
1. What makes the output "correct"?
2. What common mistakes should I catch?
3. What's required vs. optional?

### Step 3: Implement Checks

```python
def validate(target_path: str) -> dict:
    issues = []

    # Check 1: File exists
    if not os.path.exists(target_path):
        issues.append(f"File not found: {target_path}")
        return {"valid": False, "message": issues[0]}

    # Check 2: Read content
    with open(target_path, 'r') as f:
        content = f.read()

    # Check 3: Your validation logic
    if "TODO" in content:
        issues.append("File contains unresolved TODO comments")

    if not content.strip():
        issues.append("File is empty")

    # Return result
    if issues:
        return {
            "valid": False,
            "message": f"Validation failed:\\n" + "\\n".join(f"- {i}" for i in issues)
        }

    return {"valid": True, "message": "All checks passed"}
```

### Step 4: Test Manually

```bash
python my_validator.py path/to/test/file.txt
```

### Step 5: Add to Command/Agent

```yaml
---
hooks:
  post_tool_use:
    - tools: ["write", "edit"]
      command: "python ${CLAUDE_PROJECT_DIR}/.claude/hooks/validators/my_validator.py $CLAUDE_TOOL_INPUT_PATH"
---
```

---

## Validator Best Practices

### DO ✅

- **Be specific** - Clear error messages help fix issues fast
- **Log everything** - Helps debug when things go wrong
- **Handle errors gracefully** - Don't crash, return validation failure
- **Keep it focused** - One validator = one concern
- **Make it fast** - Validators run often, don't slow down workflows

### DON'T ❌

- **Over-validate** - Don't check things that don't matter
- **Be vague** - "Invalid file" doesn't help; "Missing header on line 1" does
- **Crash** - Always return a result, even if validation fails
- **Mix concerns** - Don't validate JSON *and* markdown in the same validator
- **Hardcode paths** - Use the provided `target_path` parameter

---

## Troubleshooting

### Validator Not Running

**Check:**
1. Is Python installed? `python --version`
2. Is the hook syntax correct in YAML frontmatter?
3. Did you restart the session after adding the hook?
4. Is the validator script executable?

**Fix:**
```bash
# Make sure Python works
python .claude/hooks/validators/my_validator.py test.txt

# Check file permissions (Unix/Mac)
chmod +x .claude/hooks/validators/my_validator.py
```

### Validation Always Fails

**Check:**
1. Run validator manually to see actual error
2. Check log file: `cat my_validator.log`
3. Verify file path is correct
4. Ensure validation logic is correct

### Validator Errors

**Common issues:**
- **File not found** - Check `$CLAUDE_TOOL_INPUT_PATH` is being passed correctly
- **Python syntax errors** - Test script manually
- **Missing imports** - Ensure required modules are installed
- **Permission denied** - Check file permissions

---

## Environment Variables Available

When validators run via hooks, these variables are available:

- `${CLAUDE_PROJECT_DIR}` - Absolute path to project root
- `$CLAUDE_TOOL_INPUT_PATH` - Path to file that was written/edited

**Example usage:**
```bash
python ${CLAUDE_PROJECT_DIR}/.claude/hooks/validators/my_validator.py $CLAUDE_TOOL_INPUT_PATH
```

---

## Validation Levels

### Level 1: No Validation (Beginner)
Use commands/agents as-is. Manual review of outputs.

### Level 2: Example Validators (Intermediate)
Use the provided validators for common tasks. Learn the pattern.

### Level 3: Custom Validators (Advanced)
Create validators for your specific needs and standards.

### Level 4: Full Framework (Expert)
Build pipelines with multi-stage validation, custom skills, and comprehensive logging.

---

## Log Files

Each validator creates a `.log` file tracking all validation attempts:

```
[2026-01-20 12:34:56] Target: src/app.json
Result: PASS
----------------------------------------

[2026-01-20 12:35:12] Target: src/config.json
Result: FAIL
Issues: ['Missing required field: version', 'Invalid port number']
----------------------------------------
```

**Log files are:**
- Ignored by git (see `.gitignore`)
- Useful for debugging
- Historical audit trail
- Helpful for understanding patterns

---

## Advanced: Validator Composition

You can chain validators or create validators that call other validators:

```python
def validate(target_path: str) -> dict:
    # First check syntax
    syntax_result = validate_syntax(target_path)
    if not syntax_result["valid"]:
        return syntax_result

    # Then check content
    content_result = validate_content(target_path)
    if not content_result["valid"]:
        return content_result

    return {"valid": True, "message": "All validations passed"}
```

---

## Resources

- **Template:** `TEMPLATE_validator.py` - Copy this to create new validators
- **Examples:** `json_validator.py`, `markdown_validator.py`, `commit_validator.py`
- **Full Guide:** `../../docs/self-validating-agents-guide.md`
- **Levels Guide:** `../../docs/validation-levels-guide.md`

---

## Quick Start

1. **See it in action:** Run an example validator
   ```bash
   python json_validator.py ../../settings.json
   ```

2. **Create your own:** Copy the template
   ```bash
   cp TEMPLATE_validator.py my_validator.py
   ```

3. **Add validation logic:** Edit `my_validator.py`

4. **Test it:** Run manually first
   ```bash
   python my_validator.py /path/to/test/file
   ```

5. **Hook it up:** Add to command/agent YAML frontmatter

6. **Use it:** Let the AI run your command/agent and see validation in action

---

*Validators are optional but powerful. Start simple and add validation as you identify patterns worth enforcing.*
