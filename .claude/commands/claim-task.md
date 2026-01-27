---
description: Claim a task from the work queue for the current session
---

# Claim Task

Claim a task from the work queue without launching a new worker session. Use this when you want to work on a queued task in your current session.

## Usage

```
/claim-task [task-id]
```

If no task ID provided, show available tasks and prompt for selection.

## Steps

### Step 1: Show Available Tasks (if no ID provided)

```bash
python .claude/scripts/work_queue.py list available
```

### Step 2: Get Session Tag

Get current session tag from environment or session coordinator:

```python
import os
session_tag = os.environ.get("CLAUDE_SESSION_TAG", "main")
```

### Step 3: Claim the Task

```bash
python .claude/scripts/work_queue.py claim <task-id> <session-tag>
```

Or use Python:

```python
import sys
import os
sys.path.insert(0, '.claude/scripts')
from work_queue import claim_task, get_task

session_tag = os.environ.get("CLAUDE_SESSION_TAG", "main")
success, message = claim_task(task_id, session_tag)
```

### Step 4: Confirm and Show Task Details

If successful, show the full task details:

```
Task claimed successfully!

TASK DETAILS:
================================================================
ID:          task-a1b2c3d4
Description: Wire up Admin dashboard to backend API
Priority:    Normal (2)
Context:     See src/api/admin.py
Depends on:  (none)
================================================================

You are now working on this task as @{session_tag}.
When finished, use /complete-task to mark it done.
```

If failed, explain why:
- "Task already claimed by @worker-2"
- "Task already completed"
- "Task not found"

## Example

```
User: /claim-task

Claude: Here are the available tasks:

  [1] [HIGH] task-abc123: Wire up Admin dashboard...
  [2] [NORM] task-def456: Add CLI command...
  [3] [LOW]  task-ghi789: Update docs...

Which task would you like to claim? Enter the number or task ID.

User: 1

Claude: Task claimed successfully!

TASK DETAILS:
================================================================
ID:          task-abc123
Description: Wire up Admin dashboard to backend API
Priority:    High (1)
Context:     See src/api/admin.py
================================================================

You are now working on this task as @main.
When finished, use /complete-task to mark it done.
```

## Notes

- A session can claim multiple tasks (but should complete one before starting another)
- Claimed tasks auto-release after 30 minutes of inactivity
- Use /complete-task when done, not /remove-task

## Related Commands

- `/list-tasks` - View all tasks in the queue
- `/complete-task` - Mark your claimed task as done
- `/tandem` - Launch a new worker to claim a task
