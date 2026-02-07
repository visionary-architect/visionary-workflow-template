---
description: "Rich markdown — Documentation, reports, detailed explanations"
---

# Markdown-Focused Output Style

## When to Use
- Writing documentation or README content
- Detailed technical reports
- Architecture decision records
- Explanations requiring headings, code, and diagrams

## Format Template
```markdown
# {{Title}}

## Overview
Brief summary of the topic.

## Details
Extended explanation with:
- Bullet points for lists
- `inline code` for references
- Links to [related resources](url)

### Code Example
\```language
code here
\```

## Summary
Key takeaway in 1-2 sentences.
```

## Constraints
- Use ATX-style headers (`#` not underline)
- Maximum heading depth: H4 (####)
- Include a table of contents for documents > 200 lines
- Code blocks must specify language for syntax highlighting
- Use reference-style links for repeated URLs
- Maximum line length: 100 characters (for readability)
- One blank line between sections

## Example
A technical design document with overview, architecture diagram (Mermaid), API specification (table), implementation notes (code blocks), and next steps (checklist).
