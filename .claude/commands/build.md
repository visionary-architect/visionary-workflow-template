---
description: "Execute an implementation plan by deploying team agents"
model: opus
arguments:
  - name: plan
    description: "Path to the plan file"
---

# Build — Execute Plan with Team Agents

Execute an implementation plan by deploying builder and validator agents.

## Usage

```
/build .planning/my-plan.md
```

## Workflow

1. **Load the plan**: Read the plan file at `$arguments.plan`
2. **Parse tasks**: Extract all tasks, their dependencies, and team assignments
3. **Create task items**: Use TaskCreate for each task, setting `blockedBy` for dependencies
4. **Deploy builders**: Launch builder agents (via Task tool) for implementation tasks
5. **Deploy validators**: Launch validator agents for verification tasks after builders complete
6. **Monitor progress**: Track task completion and report status

## Guard Clause

If no plan path is provided (`$arguments.plan` is empty):

1. List available plans in `.planning/`
2. Ask the user which plan to execute
3. Do NOT proceed without a plan file

## Agent Deployment

For each implementation task:
```
Launch Task with agent: .claude/agents/team/builder.md
Prompt: "Complete task T1: [description]. Files: [list]. Criteria: [acceptance criteria]."
```

For each validation task:
```
Launch Task with agent: .claude/agents/team/validator.md
Prompt: "Validate task T1: [description]. Check files: [list]. Criteria: [validation criteria]."
```

## Dependency Handling

- Tasks with no dependencies: launch immediately (in parallel if possible)
- Tasks with dependencies: wait until all `blockedBy` tasks are complete
- Failed tasks: report failure and skip dependent tasks

## Completion

When all tasks are done:
1. Run the test suite (`uv run pytest` or equivalent)
2. Generate a summary of what was built
3. List any failed or skipped tasks
