---
description: "TTS-optimized — Short spoken summaries without markdown formatting"
---

# TTS Summary Output Style

## When to Use
- Generating text meant to be spoken aloud via TTS
- Audio summaries of completed work
- Notification messages
- Subagent completion announcements

## Format Template
```
[Plain text sentence. No markdown. No special characters.]
```

## Constraints
- Maximum 20 words per sentence
- No markdown formatting (no **, no ##, no ```)
- No special characters, URLs, or file paths
- No abbreviations (say "Python" not "py", "repository" not "repo")
- Use natural speech patterns
- Avoid lists — use flowing sentences
- Numbers spelled out when under 10 ("three files" not "3 files")

## Example
Finished updating the authentication module. Added two new test cases. All tests passing.
