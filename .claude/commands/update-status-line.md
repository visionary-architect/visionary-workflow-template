---
description: "Write custom key-value pairs to status extras for status line display"
allowed-tools:
  - Bash
  - Read
  - Write
arguments:
  - name: key_value
    description: "Key and value to set, e.g. 'phase 3' or 'focus auth-module'"
    argument-hint: "<key> <value>"
---

# Update Status Line

Write a custom key-value pair to `.claude/session/status_extras.json`. Status line scripts read this file to display runtime context.

## Arguments

`$ARGUMENTS` should be in the format: `<key> <value>`

Examples:
- `/update-status-line phase 3`
- `/update-status-line focus auth-module`
- `/update-status-line sprint v1.2`
- `/update-status-line status reviewing`

## Instructions

1. Parse `$ARGUMENTS` — first word is the key, remainder is the value
2. If no arguments provided, read the current extras and display them as a table
3. Read the extras JSON at `.claude/session/status_extras.json` (create if missing, default `{}`)
4. Set `<key> = <value>` in the extras object
5. Write back the updated JSON
6. Confirm what was set: `Set {key} = {value} in status extras`

## Guard Clause

If `$ARGUMENTS` is empty:
1. Read and display any existing extras from `.claude/session/status_extras.json`
2. Show usage: `/update-status-line <key> <value>`
3. Do NOT make any changes

## Extras File Structure

The extras live in a dedicated file at `.claude/session/status_extras.json`:
```json
{
  "phase": "3",
  "focus": "auth-module",
  "sprint": "v1.2"
}
```

Status line scripts (e.g., v6_context_bar.py) read this file to display custom values.
This file is session-independent — extras persist until explicitly changed.
