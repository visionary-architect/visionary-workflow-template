---
description: "Interactive wizard to set up your project with the Visionary workflow"
---

# Initialize Project

> Interactive wizard to set up your project with the Visionary workflow.

---

## Purpose

This command helps you configure your project and define its vision, requirements, and roadmap through a series of questions. It automatically replaces all template placeholders and populates planning files so you can immediately start the Visionary workflow.

---

## Instructions

You are helping me initialize a new project. Guide me through:

0. **Project Configuration** - Replace template placeholders
1. **PROJECT.md** - Vision and goals
2. **REQUIREMENTS.md** - What needs to be built
3. **ROADMAP.md** - Delivery plan with phases
4. **STATE.md** - Initial state

---

### Step 0: Project Configuration

**First, configure the template by asking these questions:**

1. **What is your project name?** (e.g., "My Awesome App", "Task Manager Pro")

2. **What should the project slug be?**
   - Suggest a slug based on their project name (lowercase, hyphens, no spaces)
   - Example: "My Awesome App" → `my-awesome-app`
   - Let them confirm or provide a custom slug

**After getting answers, automatically:**

1. **Generate today's date** in YYYY-MM-DD format
2. **Replace ALL placeholders** in these files:
   - `CLAUDE.md`
   - `STATE.md`
   - `DEVLOG.md`
   - `PROJECT.md`
   - `SETUP.md`
   - `.claude/settings.json`
   - `.claude/scripts/launch-worker.py`

**Placeholder replacement:**
| Placeholder | Replace With |
|-------------|--------------|
| `{{PROJECT_NAME}}` | User's project name (e.g., "My Awesome App") |
| `{{PROJECT_SLUG}}` | URL-safe identifier (e.g., "my-awesome-app") |
| `{{DATE}}` | Today's date (e.g., "2026-01-24") |

**Use these commands to perform the replacement:**

For each file, read it, replace all placeholders with the user's values, and write it back.

**After replacement, confirm:**
```
✅ Project configured!

Project Name: [name]
Project Slug: [slug]
Date: [date]

Updated 7 files with your project information.
```

Then proceed to Step 1.

---

### Step 1: Project Vision

Ask me these questions one at a time, waiting for my response:

1. **What are you building?** (Describe your project in 2-3 sentences)
2. **Why are you building it?** (What problem does it solve?)
3. **What are your top 3 goals for this project?**
4. **What is explicitly OUT of scope?** (What are you NOT building?)
5. **What constraints do you have?** (Time, technical, resources?)
6. **How will you know when you're done?** (Success criteria)

### Step 2: Requirements Scoping

Now let's scope the requirements:

1. **What MUST be in v1.0?** (List the critical features - can't ship without these)
2. **What SHOULD be in v1.0 if possible?** (Important but not critical)
3. **What can wait for v2.0?** (Future features)

### Step 3: Tech Stack

Ask about the technical foundation:

1. **What language/framework will you use?**
   - Examples: "Node.js with Express", "Python with FastAPI", "React + TypeScript"

2. **What's your package manager?**
   - Examples: npm, yarn, pnpm, pip, uv, cargo

3. **What commands will you use?**
   - Run the project? (e.g., `npm start`, `python main.py`)
   - Run tests? (e.g., `npm test`, `pytest`)
   - Lint/format? (e.g., `npm run lint`, `ruff check`)

**After getting answers, automatically configure:**

1. **Update `.claude/settings.json`** - Add permissions for their tech stack:

   | Tech Stack | Add These Permissions |
   |------------|----------------------|
   | Node.js | `Bash(npm *)`, `Bash(npx *)`, `Bash(node *)` |
   | Yarn | `Bash(yarn *)` |
   | pnpm | `Bash(pnpm *)` |
   | Python (pip) | `Bash(python *)`, `Bash(python3 *)`, `Bash(pip *)` |
   | Python (uv) | `Bash(uv *)`, `Bash(python *)` |
   | Python (pytest) | `Bash(pytest*)` |
   | Rust | `Bash(cargo *)`, `Bash(rustc *)` |
   | Go | `Bash(go *)` |
   | Docker | `Bash(docker *)`, `Bash(docker-compose *)` |

2. **Update `CLAUDE.md`** - Fill in the Tech Stack section with their choices

**Confirm:**
```
✅ Tech stack configured!

Language: [language]
Package Manager: [package manager]
Commands: run=[cmd], test=[cmd], lint=[cmd]

Updated settings.json with permissions for your stack.
Updated CLAUDE.md with tech stack details.
```

### Step 4: Phase Breakdown

Based on the requirements, I'll help you break the work into phases:

- Each phase should deliver something usable
- Phases should be small enough to complete in 1-3 sessions
- Each phase has clear deliverables

**Suggest 2-5 phases** and ask for my approval or adjustments.

### Step 5: Generate Files

Once I've approved the plan, generate/update:

1. **PROJECT.md** - Fill in all sections based on my answers
2. **REQUIREMENTS.md** - List all requirements with phase mappings
3. **ROADMAP.md** - Create the phase structure
4. **STATE.md** - Initialize with "Project initialized" entry
5. **CLAUDE.md** - Update the `[PROJECT NAME]` and tech stack sections if this is a fresh project

### Step 6: Confirm and Offer Next Step

After generating files, provide a summary and offer to continue:

```
✅ Project initialized!

Files created/updated:
- PROJECT.md - Your vision and goals
- REQUIREMENTS.md - What you're building
- ROADMAP.md - [N] phases planned
- STATE.md - Session tracking started
- CLAUDE.md - Tech stack configured
- settings.json - Permissions configured

Your project is ready! Phase 1 is: [Phase 1 name]
```

**Then ask:**
> "Would you like me to start Phase 1 now? I'll run `/discuss-phase 1` to capture implementation decisions before we start building."
>
> Or if you have a quick task first, just tell me what you need.

**If user says yes:** Immediately run the discuss-phase workflow for Phase 1.

**If user says no or wants something else:** Acknowledge and wait for their direction.

---

## Output Files

| File | What Gets Filled In |
|------|---------------------|
| PROJECT.md | Vision, goals, constraints, success criteria |
| REQUIREMENTS.md | v1.0 must/should/nice, v2.0, out of scope |
| ROADMAP.md | Phases with requirements and deliverables |
| STATE.md | Current focus, session log entry |

---

## Example Interaction

**Assistant:** What are you building? Describe your project in 2-3 sentences.

**User:** A CLI tool for managing my dotfiles across multiple machines.

**Assistant:** Great! Why are you building it? What problem does it solve?

**User:** I waste time setting up new machines and keeping configs in sync.

**Assistant:** What are your top 3 goals for this project?

**User:** 1) Easy setup on new machines, 2) Sync changes across machines, 3) Version history for configs

*(Continue through all questions, then generate files)*

---

## Important Notes

- Ask questions one at a time, don't overwhelm
- Summarize what you understood before generating files
- Keep phases small and achievable
- It's okay if the user doesn't have all answers - use reasonable defaults
- Always offer to continue to the next step (don't just tell them what to do)
- The goal is a seamless flow: init → discuss → plan → execute → verify → repeat
