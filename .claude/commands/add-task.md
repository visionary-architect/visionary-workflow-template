---
description: Add a task to the persistent work queue for multi-session execution
---

# Add Task to Work Queue

Add a new task that can be picked up by any worker session (via `/tandem`).

## Your Role

You are a task capture assistant. Your job is to help the user fully specify their task through a conversational interview process. Don't just accept vague descriptions - probe for specifics.

## Conversation Flow

### Step 1: Get Initial Task Description

If the user provided a description with the command, acknowledge it. Otherwise ask:
> "What task would you like to add to the work queue?"

### Step 2: Clarify and Expand (CRITICAL)

When the user provides a vague or incomplete description, ask follow-up questions to capture specifics. Use your knowledge of the project to ask relevant questions.

**Example clarification patterns:**

| User Says | Ask |
|-----------|-----|
| "update ui" | "Which UI component? (Main window, dashboard, admin panel, or all?)" |
| "fix bug" | "What's the bug? Where does it occur? What's the expected vs actual behavior?" |
| "add feature" | "What should this feature do? Which component should it go in?" |
| "improve performance" | "Which part is slow? Have you noticed any specific bottlenecks?" |
| "write tests" | "For which module? Unit tests, integration tests, or both?" |
| "refactor X" | "What's wrong with the current approach? What pattern do you want instead?" |

**Proactive suggestions:** Use project knowledge to suggest specifics:
- "Based on the current codebase, do you mean updating `window.html` or `dashboard.html`?"
- "I see there's an open TODO about X - is this related?"
- "The last session mentioned Y as a next step - is that what you want to capture?"

### Step 3: Confirm the Full Task Description

Once you have enough detail, present the fully specified task for confirmation:

> **Task to add:**
> "Wire up the Admin dashboard (`src/ui/admin.py`) to the live backend API endpoints, including authentication status, user list, and task queue views."
>
> Is this correct? Should I add any additional context?

### Step 4: Determine Priority

Ask about priority using the AskUserQuestion tool:

| Priority | When to Use |
|----------|-------------|
| High (1) | Blocking other work, urgent deadline, critical bug |
| Normal (2) | Regular feature work, standard priority (default) |
| Low (3) | Nice to have, do when available, cleanup tasks |

### Step 5: Capture Context (Optional)

Ask if there's additional context that would help a worker pick up this task:
- Related files or documentation
- Dependencies or prerequisites
- Links to issues or discussions
- Notes about approach or constraints

### Step 6: Add to Queue

Run:
```bash
python .claude/scripts/work_queue.py add "<fully specified description>" --priority <N> --context "<context>"
```

### Step 7: Confirm

Show confirmation and current queue status:

```
Added task to work queue:
  ID: task-a1b2c3d4
  Description: Wire up Admin dashboard to live backend API...
  Priority: Normal (2)
  Context: See src/api/admin.py...

Current queue: 3 available, 1 claimed

Use /tandem to launch a worker that can pick up this task.
```

## Implementation Details

The work queue is stored at `.claude/session/work_queue.json`.

Use the Python module:
```python
import sys
sys.path.insert(0, '.claude/scripts')
from work_queue import add_task, get_queue_stats

task = add_task(
    description="<fully specified description>",
    priority=2,  # 1=high, 2=normal, 3=low
    context="<additional context>"
)
```

## Examples

### Example 1: Vague input clarified

```
User: /add-task update ui

Claude: I'd like to capture this task in more detail so a worker can pick it up effectively.

Which UI would you like to update?
- Main application window
- Dashboard page
- Admin panel
- All UI components

User: the dashboard

Claude: Got it - the dashboard. What kind of updates are you looking for?
- Visual/styling changes (colors, fonts, spacing)
- New features (add sections, functionality)
- Bug fixes
- Content updates

User: i want to add a section that shows the current task status

Claude: **Task to add:**
"Add a task status section to the dashboard (`src/ui/dashboard.py`) that displays current progress, including completion count, estimated time remaining, and any errors."

Is this correct? Any additional context to add?

User: yes that's good

Claude: What priority should this task have?
[Uses AskUserQuestion with High/Normal/Low options]

User: normal

Claude: Added task to work queue:
  ID: task-7f8a9b2c
  Description: Add a task status section to the dashboard...
  Priority: Normal (2)

Use /tandem to launch a worker that can pick up this task.
```

### Example 2: Already specific

```
User: /add-task Implement retry logic for failed API calls in api/client.py with exponential backoff (max 3 retries, starting at 1s delay)

Claude: That's already well-specified! Let me confirm:

**Task to add:**
"Implement retry logic for failed API calls in `api/client.py` with exponential backoff (max 3 retries, starting at 1s delay)"

Is this correct? Any additional context?

User: add context that it should handle both connection errors and 5xx responses

Claude: What priority?

User: high

Claude: Added task to work queue:
  ID: task-3c4d5e6f
  Description: Implement retry logic for failed API calls in api/client.py...
  Priority: High (1)
  Context: Should handle both connection errors and 5xx responses
```

## Related Commands

- `/tandem` - Launch a new worker session that can claim tasks
- `/progress` - View current project status
