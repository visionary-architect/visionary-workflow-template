---
description: "Validate that code doesn't violate project-defined invariants"
---

# Check Invariants

Validate that code doesn't violate your project's core invariants.

---

## Setup Required

Before using this command, configure your project's invariants in:
- `.claude/hooks/validators/invariant_validator.py`

See the INVARIANTS list at the top of that file for configuration instructions.

---

## Default Invariants

Your project should define invariants that are **non-negotiable rules** every code change must preserve. Examples:

| # | Invariant | Example |
|---|-----------|---------|
| 1 | [Your first invariant] | [What it means] |
| 2 | [Your second invariant] | [What it means] |
| 3 | [Your third invariant] | [What it means] |

Update these in `CONTEXT.md` and configure validation in `invariant_validator.py`.

---

## Usage

```
/check-invariants           # Check all source files
/check-invariants <file>    # Check specific file
```

---

## Instructions

When the user runs `/check-invariants`:

### If no argument provided

Run the validator on all source files:

```bash
python .claude/hooks/validators/invariant_validator.py --all
```

### If file path provided

Run the validator on that specific file:

```bash
python .claude/hooks/validators/invariant_validator.py <file_path>
```

### Report results clearly

1. List files that passed
2. List any violations found with line numbers
3. Suggest fixes for each violation

### If violations found

- Explain which invariant was violated and why it matters
- Suggest specific code changes to fix the violation
- Offer to make the fix if the user wants

---

## Configuring Invariants

Edit `.claude/hooks/validators/invariant_validator.py` to define your project's invariants:

```python
INVARIANTS = [
    {
        "id": "INV-1",
        "name": "No Debug Statements",
        "patterns": [
            (r"console\.log\(", "Use logger instead of console.log"),
            (r"debugger;", "Remove debugger statements"),
            (r"print\(", "Use logger instead of print"),
        ],
        "components": ["src/*"],  # Only check src directory
        "severity": "error",
    },
    {
        "id": "INV-2",
        "name": "No Raw SQL",
        "patterns": [
            (r"cursor\.execute\(", "Use ORM instead of raw SQL"),
            (r"\.raw\(", "Avoid raw SQL queries"),
        ],
        "components": ["*"],  # Check everywhere
        "severity": "error",
    },
]
```

---

## Enabling Auto-Validation

To run invariant checks automatically on every file edit, add to `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {"type": "command", "command": "python .claude/hooks/validators/invariant_validator.py $CLAUDE_FILE_PATH"}
        ]
      }
    ]
  }
}
```

---

## Related

- See `CONTEXT.md` for your project's invariant documentation
- See `.claude/hooks/validators/README.md` for validator guide
- See `.claude/hooks/validators/TEMPLATE_validator.py` for creating custom validators
