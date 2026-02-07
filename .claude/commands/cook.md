---
description: "Launch parallel subagents for independent tasks"
---

# Cook — Parallel Subagent Execution

Launch multiple subagents simultaneously to work on independent tasks.

## Usage

```
/cook
```

Then describe the independent tasks you want to parallelize.

## When to Use

- Multiple files need similar changes (e.g., "add logging to all API routes")
- Independent features can be built simultaneously
- Research tasks that don't depend on each other
- Batch operations across multiple components

## How It Works

1. **Parse the request**: Identify distinct, independent tasks from the user's description
2. **Verify independence**: Ensure tasks don't modify the same files or depend on each other's output
3. **Launch subagents**: Use the Task tool to launch one subagent per task, all simultaneously
4. **Collect results**: Report what each subagent accomplished

## Rules

- **Independence is critical**: Never launch parallel agents that modify the same file
- **Clear task boundaries**: Each subagent gets a self-contained task description
- **Maximum 5 parallel agents**: More than 5 risks system resource issues
- **Report conflicts**: If tasks aren't truly independent, explain why and suggest sequential execution

## Example

User: "Add error handling to the storage adapter, update the CLI help text, and write tests for the chunking module"

This launches 3 parallel subagents:
1. Storage adapter error handling
2. CLI help text updates
3. Chunking module tests

These are independent because they touch different files in different packages.
