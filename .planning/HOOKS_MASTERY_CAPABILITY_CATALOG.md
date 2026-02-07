# hooks-mastery: Complete Capability Catalog (Revised)

> **Source:** <https://github.com/disler/claude-code-hooks-mastery.git>
> **Total:** 106 capabilities across 13 categories
> **LLM policy:** Anthropic only — no OpenAI, Ollama, Gemini, Groq, Deepseek
> **TTS policy:** pyttsx3 (zero-cost, offline) only — no ElevenLabs, no OpenAI TTS

---

## I. Architectural Patterns (9)

1. **Template meta-prompting** — /plan_w_team is a prompt that generates prompts in a specific format, using `<requested content>` markers as micro-prompts for replacement. A reusable formula that produces consistent plans every time.
2. **Plan-then-execute separation** — /plan_w_team produces a spec file in specs/, /build executes it. Clean boundary between planning and doing. Plans are artifacts you can review, edit, and re-execute.
3. **Orchestrator-never-builds pattern** — The primary agent in /plan_w_team "NEVER operates directly on the codebase" — only deploys team members via Task tools. Enforced via disallowed-tools: Task, EnterPlanMode on the planner.
4. **Builder/Validator role separation** — Builder (all tools, cyan) builds; Validator (read-only via disallowedTools: Write, Edit, NotebookEdit, yellow) verifies. Architecturally enforced at the agent definition level, not just convention.
5. **Two-agent trust escalation** — 2x compute per task to increase confidence the work was delivered correctly. Every build task is followed by an independent validation task.
6. **Task dependency DAGs** — Tasks with blockedBy fields, parallel/sequential flags, explicit dependency chains (e.g., tasks 7-12 depend on 1-6, task 13 depends on all validations). Prevents out-of-order execution.
7. **UV single-file scripts** — Every Python hook uses `#!/usr/bin/env -S uv run --script` with PEP 723 inline metadata. Zero venv management, per-script dependency isolation. Dependencies declared inline, resolved per-script.
8. **Graceful degradation everywhere** — Every hook wrapped in try/except with sys.exit(0). Hooks never crash Claude Code. TTS and LLM chains have fallbacks. Progressive enhancement based on available configuration.
9. **$CLAUDE_PROJECT_DIR for portable paths** — All hook paths in settings.json use this variable so hooks work regardless of working directory.

---

## II. Self-Validation System (6)

10. **Command-level hooks in YAML frontmatter** — Commands can embed their own Stop hooks, making them self-validating before completion. The command isn't "done" until its validators pass.
11. **validate_new_file.py** — Stop-hook validator ensuring a file of specific type was created in a specific directory. Dual detection via git status + file modification time. Actionable error messages tell Claude exactly what to do.
12. **validate_file_contains.py** — Stop-hook validator ensuring a file contains specific sections. Multi-string case-sensitive checks. Lists every missing section with remediation instructions.
13. **Per-edit code quality (builder agent)** — ruff_validator.py and ty_validator.py fire on every Write/Edit via the builder's frontmatter PostToolUse hooks. Code is validated before the agent moves on.
14. **Stop hook as acceptance test** — Exit code 2 in a Stop hook forces Claude to continue working instead of finishing. Used by validators to force the agent to fix issues before it can stop.
15. **Block/allow JSON protocol** — Validators return structured `{"decision": "block", "reason": "..."}` for PostToolUse, `{"result": "block", "reason": "..."}` for Stop. Matches the Claude Code hook output specification.

---

## III. Full Hook Lifecycle Coverage — 13 of 13 (13)

16. **Setup hook** — Dependency checking (node, python3, uv, git with version capture), project type detection (6 types: Node.js, Python, Rust, Go, Makefile, requirements.txt), optional --install-deps with fallback chains, environment persistence via CLAUDE_ENV_FILE, maintenance mode (log size warnings, git health checks).
17. **SessionStart hook** — Context injection with git branch, uncommitted changes count, .claude/CONTEXT.md, .claude/TODO.md, TODO.md, .github/ISSUE_TEMPLATE.md, recent GitHub issues (via gh issue list). Uses additionalContext for system prompt injection. Handles "startup", "resume", "clear" sources.
18. **SessionEnd hook** — Cleanup of .tmp files from logs, stale chat.json older than 24 hours. Audit trail to logs/cleanup.json.
19. **UserPromptSubmit hook** — Prompt logging, session data management (per-session JSON), agent naming, prompt validation framework with extensible blocked pattern list. Exit code 2 blocks the prompt entirely.
20. **PreToolUse hook** — Security blocking: 6 regex patterns for rm -rf variants (including split flags, --recursive --force), dangerous path detection (only blocks recursive rm on /, ~, $HOME, .., *), .env file access blocking (allows .env.sample). Append-only audit log.
21. **PostToolUse hook** — Completion logging to logs/post_tool_use.json. Consistent read-array -> append -> write-back pattern.
22. **PostToolUseFailure hook** — Structured error entries with tool_name, tool_use_id, error object, session_id, transcript_path, enriched with logged_at timestamp.
23. **Notification hook** — TTS via pyttsx3 (zero-cost, offline) with 30% personalization rate using ENGINEER_NAME env var. Filters generic "Claude is waiting for your input" messages. (REVISED -- pyttsx3 only)
24. **Stop hook** — LLM-generated completion messages via Anthropic (claude-3-5-haiku), falling back to random predefined list ("Work complete!", "All done!", "Task finished!", "Job complete!", "Ready for next task!"). JSONL-to-JSON transcript conversion via --chat flag. TTS announcement via pyttsx3. (REVISED -- Anthropic + random fallback only, pyttsx3 TTS)
25. **SubagentStart hook** — Spawn tracking with agent_id, agent_type. Debug logging to logs/subagent_debug.log with [START] prefix. Optional TTS via pyttsx3. (REVISED -- pyttsx3 only)
26. **SubagentStop hook** — The most sophisticated hook. Transcript parsing for context extraction (reads JSONL, finds first user message, truncates to 200 chars). LLM-powered task summarization via Anthropic Haiku. TTS queue with file locking to prevent audio overlap (pyttsx3). --summarize / --no-summarize flags. Graceful fallback imports with no-op functions. Try/finally lock release. (REVISED -- Anthropic summarization, pyttsx3 TTS)
27. **PreCompact hook** — Transcript backup to logs/transcript_backups/ with structured filenames: `{session_name}_pre_compact_{trigger}_{timestamp}.jsonl`. Differentiates between manual and auto compaction triggers. Optional verbose feedback.
28. **PermissionRequest hook** — Auto-allow for 26 safe bash command patterns + all Read/Glob/Grep operations. Structured allow/deny JSON with updatedInput support for modifying tool inputs before allowing. --auto-allow and --log-only composable modes.

---

## IV. Status Lines (9)

29. **Status line system** — Persistent terminal UI element rendering on every response via statusLine in settings.json.
30. **v1: Basic MVP** — ANSI-colored model name, directory, git branch. 2-second timeouts on git commands.
31. **v2: Smart prompt display** — Color-coded by prompt type: 6 categories (commands=yellow, questions=blue, creation=green, fix=red, refactor=magenta, default=white) with matching icons (lightning, question mark, lightbulb, bug, recycle, speech bubble).
32. **v3: Agent sessions** — Shows agent name in bright red. Last 3 prompts with recency-based truncation (75/50/40 chars). Reads from per-session JSON.
33. **v5: Cost tracking** — Total cost in USD, lines added/removed.
34. **v6: Context window usage (default)** — Visual progress bar `[###---]` (15-char width). Color transitions at 50% (green), 75% (yellow), 90% (red). Remaining token count in human-readable format ("42.5k", "1.23M"). Session ID in dim gray.
35. **v7: Session duration** — Timer with start time tracking.
36. **v8: Token/cache stats** — Input tokens, output tokens, cache creation/read stats.
37. **v9: Powerline style** — Unicode powerline separators (`\ue0b0`, `\ue0b1`). Background color segments: blue (model) -> green (git branch) -> magenta (path) -> cyan (context %). Smart path shortening: home -> ~, long paths -> first/.../last. Fallback git detection (reads .git/HEAD directly if command fails).

---

## V. Agent System (10)

38. **Meta-agent (agent factory)** — Scrapes live Anthropic documentation at runtime (docs.anthropic.com), generates complete agent files from natural language descriptions. Infers minimal tool sets, selects terminal colors from 8 options, generates kebab-case names, writes YAML frontmatter + full system prompt to .claude/agents/. Uses opus model.
39. **Builder agent** — Single-task focus: "You are assigned ONE task. Focus entirely on completing it." Per-edit validation hooks (ruff + ty). Uses TaskGet to read assignments, TaskUpdate to mark completed. Structured completion report template.
40. **Validator agent** — Architecturally read-only (disallowedTools: Write, Edit, NotebookEdit). 4-step workflow: understand -> inspect -> verify -> report. Pass/fail reports with checkboxes, files inspected, commands run, issues found.
41. **Work-completion-summary agent** — TTS audio summaries via pyttsx3 (Bash invocation of pyttsx3_tts.py). Ultra-concise: 1 sentence summary + 1 next step. Personalized with user name variable. Tool-restricted to Bash + Read only. (REVISED -- pyttsx3 via Bash instead of ElevenLabs MCP)
42. **Research agent** — Date-aware (runs date first, discards content >1 week old). Multi-source: WebSearch + Firecrawl MCP (web scraping, not LLM). Structured 6-section report with emoji headers. Focuses on actionable engineering insights, not academic theory.
43. **Hello-world agent** — Demonstrates proactive trigger pattern and minimal agent definition. WebSearch only. Shows the agent-to-orchestrator response protocol.
44. **Consistent agent prompt format** — Every agent follows: Purpose -> Variables -> Instructions (numbered steps) -> Best Practices -> Report/Response template. The meta-agent generates this format automatically, ensuring all generated agents are structurally consistent.
45. **Agent response directed at primary agent** — Agents format output as instructions to the orchestrator: "Claude - respond to the user with this message: ...". Subagents don't talk to the user directly; they return structured output to the parent. This is a delegation protocol.
46. **Agent subdirectory organization** — Agents organized by purpose: team/ (builder, validator), top-level for general-purpose. Scalable pattern for adding team/qa-tester.md, team/deploy-agent.md, etc.
47. **Multi-model agent variants pattern** — Same agent logic at different quality/cost tiers via model: field (haiku for fast/cheap, sonnet for balanced, opus for best). User picks the speed/quality tradeoff per task.

---

## VI. Output Styles (8)

48. **genui** — Generates standalone HTML5 with embedded CSS. Full design system (8 colors, typography, 900px max-width layout). Component library (info/success/warning/error sections). Interactive elements (copy-to-clipboard, collapsible sections). Auto-opens in browser at /tmp/cc_genui_<description>_YYYYMMDD_HHMMSS.html. Zero external dependencies.
49. **ultra-concise** — Aggressive brevity: "We are not in a conversation", "We DO NOT like WASTING TIME", "We're here to FOCUS, BUILD, and SHIP".
50. **tts-summary** — Every response ends with audio summary via pyttsx3. Under 20 words, outcome-focused. (REVISED -- pyttsx3 only)
51. **table-based** — All information in markdown tables. Comparison, step, information, and analysis patterns.
52. **yaml-structured** — All responses as valid, parseable YAML with typed sections: task, details, files, commands, status, next_steps, notes.
53. **bullet-points** — 4-level hierarchical nesting with ACTION/TODO prefixes. Ordered vs unordered rules.
54. **html-structured** — Semantic HTML5 with data attributes: data-file, data-line, data-type, data-action. Uses `<article>`, `<header>`, `<main>`, `<section>`, `<aside>`, `<nav>`.
55. **markdown-focused** — Task lists (`- [ ]`/`- [x]`), blockquotes for callouts, horizontal rules for section breaks. Full markdown feature set.

---

## VII. TTS Subsystem (5) (REVISED -- pyttsx3 only)

56. **Zero-cost offline TTS via pyttsx3** — No API keys required. 180 WPM, volume 0.8. Works offline, cross-platform. Single provider, no chain needed. (REVISED -- single provider replaces 3-tier chain)
57. **TTS queue with file locking** — fcntl.flock cross-process synchronization at .claude/data/tts_queue/tts.lock. Contains JSON with agent_id, timestamp, pid. Prevents overlapping audio from parallel subagents. Still needed even with pyttsx3 -- parallel agents can still overlap.
58. **Stale lock cleanup** — Checks both timestamp age (>60s) AND whether PID is still running (os.kill(pid, 0)). CLI interface: status, acquire <id>, release <id>, cleanup.
59. **Exponential backoff retry** — TTS lock acquisition starts at 100ms, multiplies by 1.5, caps at 1.0s. 30-second total timeout. Falls back to announcing without lock on timeout.
60. **Personalized notifications** — 30% chance of including ENGINEER_NAME env var in TTS messages (random.random() < 0.3). "Dan, your agent needs your input" vs generic. Works with pyttsx3.

---

## VIII. LLM Subsystem -- Inside Hooks (4) (REVISED -- Anthropic only)

61. **Anthropic LLM for completion messages** — claude-3-5-haiku generates contextual completion messages, falling back to random predefined list ("Work complete!", "All done!", "Task finished!", "Job complete!", "Ready for next task!"). Via subprocess with 10-second timeout. (REVISED -- single provider replaces 3-tier chain)
62. **Anthropic LLM for agent naming** — claude-3-5-haiku generates single-word agent names. Validates: single word, alphanumeric, 3-20 chars. Wordlist fallback if API call fails. (REVISED -- Anthropic only, wordlist fallback replaces Ollama-first chain)
63. **Task summarization via Anthropic** — task_summarizer.py using Haiku generates under-20-word natural-language summaries of subagent work. Called by subagent_stop.py. (REVISED -- explicitly Anthropic)
64. **Prompt engineering in hooks** — Explicit constraints: "Do NOT include quotes", "Return ONLY the completion message text", "single alphanumeric word". Prevents LLM formatting artifacts from breaking hook output parsing.

---

## IX. Slash Commands (11)

65. **/plan_w_team** — Template meta-prompt with self-validation, orchestration, and templating. Two variables ($1 user prompt, $2 orchestration prompt). Stop hooks validate output file exists and contains 7 required sections. model: opus. disallowed-tools: Task, EnterPlanMode. Inline documentation of TaskCreate, TaskUpdate, TaskList, TaskGet with TypeScript-style signatures. Resume pattern documented. Strict plan template with replacement markers.
66. **/build** — Executes generated plans at a given path. argument-hint: [path-to-plan]. Guard clause: stops and asks user if no path provided rather than proceeding blind.
67. **/cook** — Launches multiple subagents simultaneously in parallel. Demonstrates mass parallel deployment pattern including meta-agent invocations to create new agents on-the-fly. (REVISED -- removed crypto-specific agent references)
68. **/cook_research_only** — Research-only variant. No code-writing agents -- pure information gathering across multiple parallel subagents.
69. **/prime** — Quick context loading. allowed-tools: Bash, Read. Runs git ls-files, reads README.md + ai_docs reference files. Reports understanding of project.
70. **/prime_tts** — Context loading with ! prefix for inline shell execution (!git ls-files, !eza . --tree) and @ prefix for file references (@README.md). Triggers TTS summary agent (pyttsx3) on completion. (REVISED -- pyttsx3)
71. **/question** — Read-only question answering. Very narrow tool scope: allowed-tools: Bash(git ls-files:*), Read. 4 explicit anti-coding rules ("Do NOT write any code", "Do NOT edit any files", "Do NOT create any new files", "Do NOT use the Write or Edit tools"). Provably safe query-only command.
72. **/sentient** — Security test/demo. Intentionally tries rm -rf variations to prove PreToolUse blocking works. Ships as a command so users can verify their security boundaries.
73. **/all_tools** — Tool discovery. Asks Claude to list all available tools in TypeScript function signature format with purposes.
74. **/git_status** — Git info with restricted tools (Bash(git:*)). Runs git status, git diff HEAD origin/main, git branch --show-current. Reads README for context.
75. **/update_status_line** — Runtime status updates. Writes custom key-value pairs to session JSON extras object for status line display. Format: /update_status_line session_id key value.

---

## X. Autonomous Behaviors (16)

76. **Automatic prompt logging** — Every prompt logged to logs/user_prompt_submit.json. Always on via --log-only in settings.json. No user action needed.
77. **Automatic session prompt accumulation** — --store-last-prompt stores every prompt into .claude/data/sessions/{session_id}.json. Feeds status lines v2/v3 with prompt history. Always on.
78. **Automatic agent naming on first prompt** — --name-agent triggers Anthropic Haiku naming on first prompt of every session. Session gets a codename stored in session JSON. Always on. (REVISED -- Anthropic only)
79. **Automatic security scanning on every tool use** — pre_tool_use.py fires on every single tool call (empty matcher). Scans for rm -rf and .env access. No opt-in needed.
80. **Automatic tool completion logging** — post_tool_use.py logs every successful tool use. Always on.
81. **Automatic error logging** — post_tool_use_failure.py logs every failed tool use with full error context. Always on.
82. **Automatic transcript conversion** — stop.py --chat converts JSONL transcript to readable logs/chat.json on every stop event. Always on in settings.json.
83. **Automatic TTS on subagent completion** — subagent_stop.py --notify fires pyttsx3 TTS with Anthropic-generated summary whenever any subagent finishes. Always on. (REVISED -- pyttsx3 + Anthropic)
84. **Automatic TTS on notification** — notification.py --notify fires pyttsx3 TTS whenever Claude is waiting for input. Always on. (REVISED -- pyttsx3)
85. **Automatic subagent lifecycle tracking** — subagent_start.py and subagent_stop.py log every spawn and completion. Always on.
86. **Automatic context injection on session start** — session_start.py fires on every session start/resume/clear, injecting git branch, uncommitted changes, and project context files via additionalContext.
87. **Automatic session cleanup on end** — session_end.py fires on every session termination.
88. **Automatic pre-compaction logging** — pre_compact.py fires before every context compaction (manual or auto).
89. **Automatic setup on init** — setup.py fires on claude --init and --maintenance, checking dependencies and project type.
90. **Automatic status line rendering** — status_line_v6.py runs on every response, rendering the context window bar. Always on.
91. **Automatic permission request logging** — permission_request.py --log-only logs every permission dialog. Always on. (Auto-allow requires switching to --auto-allow flag.)

---

## XI. Proactive Agent Delegation (2)

92. **Proactive agent triggering via description field** — Agents with trigger phrases in their description are automatically selected by Claude without explicit user invocation:
    - hello-world-agent: "use proactively when greeting the user. If they say 'hi claude' or 'hi cc' or 'hi claude code'"
    - work-completion-summary: "Proactively triggered when work is completed" and "If they say 'tts' or 'tts summary' or 'audio summary'"
    - research agent: "Use for staying current with AI/ML innovations, finding actionable insights"
93. **Resume pattern for agent continuity** — plan_w_team.md documents resume: true in team member specs, enabling agents to be resumed with full previous context if they fail or need follow-up.

---

## XII. Configuration & Infrastructure (6) (REVISED -- simplified .env)

94. **Append-only JSON logging** — Consistent pattern across all 13 hooks: read existing JSON array -> append -> write back. Per-hook log files in logs/.
95. **CLI flag composition** — Hooks configurable via argparse flags in settings.json command strings. Same script supports --log-only, --validate, --notify, --backup, --verbose, --cleanup, --chat, --auto-allow, --summarize, --no-summarize, --name-agent, --store-last-prompt, --install-deps, --announce. Behavior composed at configuration time, not code time.
96. **Session data architecture** — Per-session JSON at .claude/data/sessions/{id}.json with accumulated prompt history, agent identity, and custom extras key-value pairs.
97. **.env.sample with progressive enhancement** — 2 keys: ANTHROPIC_API_KEY (for agent naming + completion messages + task summarization), ENGINEER_NAME (for personalized TTS). Optional: FIRECRAWL_API_KEY (web scraping for meta-agent/research agent, not LLM). System works with zero keys (no naming, random completion messages, unpersonalized TTS) and gets richer as keys are added. (REVISED -- removed OpenAI, Ollama, Gemini, Groq, Deepseek keys)
98. **ruff.toml and ty.toml** — Pre-configured Python linting and type checking rules consumed by the builder agent's per-edit validators.
99. **specs/ as generated artifact directory** — Plans generated by /plan_w_team land here. Serves as both output directory and example library (2 complete specs committed as reference).

---

## XIII. Small But Notable Details (7) (REVISED -- removed MCP sample)

100. **Per-agent tool scoping via tools field** — Positive tool grants give agents exactly what they need: tools: WebSearch (search only), tools: Bash, Read (bash + read only), tools: Write, WebFetch (write + scrape). Distinct from disallowedTools (the deny approach).
101. **Per-command tool scoping** — allowed-tools and disallowed-tools in command frontmatter. Examples: /prime allows only Bash, Read; /question allows only Bash(git ls-files:*), Read; /plan_w_team disallows Task, EnterPlanMode.
102. **$ARGUMENTS, $1, $2 variable system** — Commands accept positional arguments. $ARGUMENTS for full string, $1/$2 for individual args. argument-hint in frontmatter guides the user.
103. **Guard clause pattern** — /build checks if required argument was provided; if not, stops and asks via AskUserQuestion rather than proceeding with no input.
104. **Agent color system** — color field in frontmatter: cyan (builder), yellow (validator), green (hello-world, TTS summary). Visual differentiation in terminal when multiple agents run.
105. **Bundled Anthropic docs** — ai_docs/ with 94KB+ of scraped reference material (hooks docs, status line schema, subagents guide, UV scripts guide, slash commands reference). Available for agent consumption during /prime.
106. **Empty matcher "" catches all events** — Every hook in settings.json uses empty matcher for universal capture. Routing logic lives inside the Python scripts, not in settings.json configuration.
