---
description: Launch an additional worker session for parallel task execution
---

# Launch Tandem Worker

Start an additional AI session to work on tasks in parallel with the current session.

## What This Does

1. Shows current session status (active workers, claimed tasks)
2. Shows available tasks from the work queue
3. Launches a new terminal with a worker session
4. The new worker prompts for task selection or custom task entry

## Usage

```
/tandem
```

No arguments needed - just run the command.

## Steps

1. **Show current status** by running session-status.py
2. **Show work queue** with available tasks
3. **Launch new terminal** with the worker launcher script
4. **Inform user** that the new worker will prompt for task selection

## Implementation

### Step 1: Show Status

```bash
python .claude/scripts/session-status.py
```

### Step 2: Show Work Queue

```bash
python .claude/scripts/work_queue.py list available
```

### Step 3: Launch Worker (Windows)

```bash
start cmd /k "cd /d %CD% && python .claude\scripts\launch-worker.py"
```

For PowerShell:
```powershell
Start-Process cmd -ArgumentList '/k', "cd /d $PWD && python .claude\scripts\launch-worker.py"
```

### Step 3: Launch Worker (macOS/Linux)

```bash
# Open new terminal (adjust for your terminal emulator)
gnome-terminal -- bash -c "cd $(pwd) && python .claude/scripts/launch-worker.py; exec bash"
# or for macOS:
osascript -e "tell app \"Terminal\" to do script \"cd $(pwd) && python .claude/scripts/launch-worker.py\""
```

## Example Output

```
Launching tandem worker...

CURRENT STATUS:
----------------------------------------------------------------------
  Active workers: 1 (@worker-1)
  Claimed tasks: 1
  Available tasks: 3

WORK QUEUE:
----------------------------------------------------------------------
  [1] [NORM] Wire up Admin dashboard to backend API
  [2] [NORM] Add new dashboard CLI command
  [3] [LOW]  Update documentation for new hooks

[Opening new terminal...]

The new worker will prompt you to:
  - Select a task from the queue (enter number)
  - Enter a custom task (press C)
  - Skip task selection (press S)

You can continue working in this session while the new worker runs.
```

## What Happens in the New Terminal

The new worker sees:

```
================================================================
  MULTI-SESSION WORKER
================================================================

ACTIVE SESSIONS:
  @worker-1     | 45 tools | 1 task claimed

AVAILABLE TASKS:
  [1] [NORM] Wire up Admin dashboard to backend API
      Context: See src/api/admin.py
  [2] [NORM] Add new dashboard CLI command
  [3] [LOW]  Update documentation for new hooks

  [C] Custom task (enter your own description)
  [S] Skip (start without assigned task)
================================================================

Select task [1-3/C/S]: _
```

## Related Commands

- `/add-task` - Add tasks to the work queue
- `/pause-work` - Pause this session with handoff notes

## Notes

- Each worker gets an auto-assigned tag (@worker-1, @worker-2, etc.)
- Workers coordinate via session registry to avoid conflicts
- File locks prevent simultaneous edits to the same file
- Task claims prevent duplicate work on same task
