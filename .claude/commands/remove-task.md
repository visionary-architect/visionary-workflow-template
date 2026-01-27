---
description: Remove a task from the work queue (completed or not)
---

# Remove Task from Work Queue

Remove a task from the persistent work queue, regardless of its status.

## Usage

```
/remove-task [task-id]
```

If no task ID provided, show the current queue and prompt for selection.

## Steps

### Step 1: Show Current Queue

Run to see all tasks:
```bash
python .claude/scripts/work_queue.py list
```

### Step 2: Identify Task to Remove

If user provided a task ID, use that. Otherwise, show the list and ask:
> "Which task would you like to remove? Enter the task ID (e.g., `task-a1b2c3d4`)."

### Step 3: Confirm Removal

Before removing, confirm with the user:
> "Remove task `task-a1b2c3d4`: 'Wire up Admin dashboard...'? This cannot be undone."

Use AskUserQuestion with Yes/No options.

### Step 4: Remove Task

```bash
python .claude/scripts/work_queue.py remove <task-id>
```

### Step 5: Confirm

Show updated queue status:
```
Task removed: task-a1b2c3d4

Current queue: 2 available, 1 claimed
```

## Example

```
User: /remove-task

Claude: Here are the current tasks in the queue:

[ ] [NORM] task-a1b2c3d4: Wire up Admin dashboard to backend API
[ ] [NORM] task-e5f6g7h8: Add new dashboard CLI command
[->] [LOW] task-i9j0k1l2: Update documentation (claimed by @worker-2)

Which task would you like to remove? Enter the task ID.

User: task-e5f6g7h8

Claude: Remove task `task-e5f6g7h8`: "Add new dashboard CLI command"?

[Uses AskUserQuestion: Yes / No]

User: Yes

Claude: Task removed: task-e5f6g7h8

Current queue: 1 available, 1 claimed
```

## Related Commands

- `/add-task` - Add a task to the work queue
- `/complete-task` - Mark a claimed task as complete
- `/tandem` - Launch a worker to pick up tasks
