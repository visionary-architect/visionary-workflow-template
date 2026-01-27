---
description: Mark a claimed task as complete in the work queue
---

# Complete Task

Mark a task as complete in the work queue. Use this when you've finished working on a claimed task.

## Usage

```
/complete-task [task-id]
```

If no task ID provided, check if this session has a claimed task and offer to complete it.

## Steps

### Step 1: Identify Task

Check for claimed tasks in order of priority:

1. **Check startup context** - Was this session launched with a claimed task?
   Read `.claude/session/worker_startup_context.json` if it exists and is recent.

2. **Check session's claimed tasks** - Look in `.claude/session/work_queue.json` for tasks claimed by this session tag.

3. **User-provided ID** - If user specified a task ID, use that.

If no task found:
> "No claimed task found for this session. To complete a specific task, run `/complete-task <task-id>`."

### Step 2: Confirm Completion

Show the task and ask for confirmation:
> **Task to complete:**
> `task-a1b2c3d4`: "Wire up Admin dashboard to backend API"
>
> Mark this task as complete?

Use AskUserQuestion with:
- Yes, mark complete
- No, still working on it
- Remove it instead (didn't complete)

### Step 3: Mark Complete

Get session tag from environment or startup context:
```bash
python .claude/scripts/work_queue.py complete <task-id> <session-tag>
```

### Step 4: Confirm and Suggest Next

```
Task completed: task-a1b2c3d4

Current queue: 2 available, 0 claimed

Would you like to:
- Pick up another task from the queue?
- Add a follow-up task?
- End this session?
```

## Auto-Prompting for Completion

When working on a claimed task, you (Claude) should proactively ask about completion when you notice:

1. **Commit made** - After committing code related to the task
2. **User says "done"** - Keywords like "done", "finished", "complete", "that's it"
3. **Natural pause** - After completing a significant piece of work
4. **Session ending** - Before user ends the session

**Prompt template:**
> "It looks like you may have finished the task: '{task description}'. Would you like to mark it as complete?"

## Implementation

```python
import sys
import os
sys.path.insert(0, '.claude/scripts')
from work_queue import complete_task, get_task

session_tag = os.environ.get("CLAUDE_SESSION_TAG", "main")
success, message = complete_task(task_id, session_tag)
print(message)
```

## Example

```
User: /complete-task

Claude: You're currently working on:
  task-a1b2c3d4: "Wire up Admin dashboard to backend API"

Mark this task as complete?

[AskUserQuestion: Yes, mark complete / No, still working / Remove instead]

User: Yes, mark complete

Claude: Task completed: task-a1b2c3d4

Current queue: 2 available, 0 claimed

Would you like to pick up another task? Use /tandem to see available tasks, or I can show you the queue here.
```

## Related Commands

- `/remove-task` - Remove a task without marking complete
- `/add-task` - Add a new task to the queue
- `/tandem` - Launch a worker to pick up tasks
