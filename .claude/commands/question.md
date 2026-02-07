---
description: "Research-only mode — answer questions without modifying code"
allowed-tools:
  - "Bash(git ls-files*)"
  - Read
  - Glob
  - Grep
---

# Question — Read-Only Research Mode

Answer questions about the codebase without modifying anything.

## Rules

1. **No Write tool** — Never create or modify files
2. **No Edit tool** — Never edit existing files
3. **No code suggestions** — Don't suggest code changes unless explicitly asked "how would I..."
4. **Just answer the question** — Focus on explaining, not implementing

## What You Can Do

- Read files to understand the codebase
- Search for patterns across files
- List files with `git ls-files`
- Explain how things work
- Trace code paths
- Identify where functionality lives
- Compare approaches

## Bash Restrictions

The only Bash command allowed is `git ls-files` (for listing tracked files). All other file operations should use Read, Glob, or Grep.

## Response Format

Answer directly and concisely. Use code references like `file.py:42` when pointing to specific locations. Structure longer answers with headers if they cover multiple aspects.
