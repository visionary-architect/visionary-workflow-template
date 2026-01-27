# Planning Directory

This directory contains planning artifacts for the Visionary workflow.

## Directory Structure

```
.planning/
├── README.md           # This file
├── intel/              # Auto-populated codebase intelligence
│   ├── index.json      # File exports/imports index
│   ├── conventions.json # Detected naming patterns
│   └── summary.md      # Human-readable summary
├── quick/              # Ad-hoc task tracking
├── todos/              # Captured ideas for later
└── research/           # Research and investigation artifacts
```

## Artifact Naming Conventions

### Phase Artifacts

| Pattern | Purpose | Example |
|---------|---------|---------|
| `{N}-CONTEXT.md` | Implementation decisions | `1-CONTEXT.md` |
| `{N}-RESEARCH.md` | Research findings | `1-RESEARCH.md` |
| `{N}-{M}-PLAN.md` | Atomic task plan | `1-A-PLAN.md` |
| `{N}-{M}-SUMMARY.md` | Execution summary | `1-A-SUMMARY.md` |
| `{N}-UAT.md` | User acceptance testing | `1-UAT.md` |

Where:
- `{N}` = Phase number (1, 2, 3, ...)
- `{M}` = Plan group letter (A, B, C, ...)

### Quick Tasks

Files in `quick/` follow the pattern:
```
quick/{N}-{description}/
├── task.md      # Task description
└── notes.md     # Implementation notes
```

## Workflow Commands

| Command | Creates |
|---------|---------|
| `/discuss-phase N` | `{N}-CONTEXT.md` |
| `/plan-phase N` | `{N}-RESEARCH.md`, `{N}-{M}-PLAN.md` |
| `/execute-phase N` | `{N}-{M}-SUMMARY.md` |
| `/verify-work N` | `{N}-UAT.md` |
| `/quick` | Files in `quick/` |
| `/add-todo` | Files in `todos/` |
| `/analyze-codebase` | Files in `intel/` |

## Research Directory

The `research/` directory is for standalone research artifacts that aren't tied to a specific phase:

- Library evaluations and comparisons
- API documentation notes
- Architecture pattern research
- Technology spikes and proofs-of-concept

**Note:** Phase-specific research goes in `{N}-RESEARCH.md` at the `.planning/` root (e.g., `1-RESEARCH.md`), not in the `research/` subdirectory.

## Intel Directory

The `intel/` directory is auto-populated by the codebase indexer hook. It contains:

- **index.json** - Machine-readable index of all file exports and imports
- **conventions.json** - Detected naming conventions (function, class, file naming)
- **summary.md** - Human-readable summary for the AI context injection

This runs automatically on every Write/Edit operation.

## Best Practices

1. **Don't manually edit `intel/`** - It's auto-generated
2. **Keep phase artifacts organized** - Use the naming conventions
3. **Archive completed phases** - After verification, consider moving to an `archive/` subdirectory
4. **Use `todos/` liberally** - Capture ideas without interrupting flow
5. **Reference summaries** - Execution summaries contain valuable context for future phases

---

*Part of visionary_template_1*
