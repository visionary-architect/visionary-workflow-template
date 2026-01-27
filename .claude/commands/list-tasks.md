---
description: View the current work queue without launching a new worker
---

# List Work Queue Tasks

Quickly view all tasks in the work queue without launching a new worker session.

## Usage

```
/list-tasks [filter]
```

Filters:
- (none) - Show all non-completed tasks
- `all` - Show all tasks including completed
- `available` - Show only available tasks
- `claimed` - Show only claimed tasks
- `completed` - Show only completed tasks

## Steps

### Step 1: Get Tasks

Run the work queue list command:

```bash
python .claude/scripts/work_queue.py list [filter]
```

Or use Python directly for richer output:

```python
import sys
sys.path.insert(0, '.claude/scripts')
from work_queue import list_tasks, get_queue_stats

# Get stats
stats = get_queue_stats()

# Get tasks (no filter = all non-completed)
all_tasks = list_tasks()
available = [t for t in all_tasks if t['status'] == 'available']
claimed = [t for t in all_tasks if t['status'] == 'claimed']
```

### Step 2: Display Results

Format output as a clear table:

```
WORK QUEUE STATUS
================================================================
Available: 3  |  Claimed: 1  |  Completed: 5 (all-time)
================================================================

AVAILABLE TASKS:
  [HIGH] task-abc123: Wire up Admin dashboard to API
         Context: See src/api/admin.py
         Added: 2h ago

  [NORM] task-def456: Add new dashboard CLI command
         Added: 1d ago

  [LOW]  task-ghi789: Update documentation for hooks
         Added: 3d ago

CLAIMED TASKS:
  [NORM] task-jkl012: Implement retry logic
         Claimed by: @worker-2 (45m ago)
         Context: Handle connection errors and 5xx

================================================================
Use /add-task to add new tasks
Use /tandem to launch a worker and claim a task
```

### Step 3: Show Recommendations (Optional)

Based on queue state, suggest actions:

- If many available tasks: "Consider launching a /tandem worker"
- If tasks stuck claimed >1h: "Task X has been claimed for 2h - may be stale"
- If queue empty: "No tasks in queue. Use /add-task to add some."

## Example Output

```
User: /list-tasks

Claude:
WORK QUEUE STATUS
================================================================
Available: 2  |  Claimed: 1  |  Completed: 8 (all-time)
================================================================

AVAILABLE TASKS:
  [HIGH] task-a1b2c3d4: Wire up Admin dashboard to backend API
         Context: See src/api/admin.py
         Added: 2 hours ago
         Depends on: (none)

  [NORM] task-e5f6g7h8: Add new dashboard CLI command
         Added: 1 day ago
         Depends on: (none)

CLAIMED TASKS:
  [NORM] task-i9j0k1l2: Implement retry logic for API calls
         Claimed by: @worker-1 (32 minutes ago)
         Context: Handle connection errors and 5xx responses

================================================================
Tip: Use /tandem to launch a worker and pick up a task
```

## Related Commands

- `/add-task` - Add a new task to the queue
- `/remove-task` - Remove a task from the queue
- `/complete-task` - Mark a task as complete
- `/claim-task` - Claim a task without launching new session
- `/tandem` - Launch a new worker session
