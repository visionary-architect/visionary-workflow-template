---
description: "Standalone HTML5 — Rich visual presentations with embedded CSS/JS"
---

# GenUI Output Style

## When to Use
- Creating visual dashboards, reports, or presentations
- Building standalone HTML artifacts that can be opened in a browser
- Generating interactive visualizations

## Format Template
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <style>
        /* Embedded styles — no external dependencies */
        :root { --primary: #6366f1; --bg: #0f172a; --surface: #1e293b; --text: #e2e8f0; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: system-ui, sans-serif; background: var(--bg); color: var(--text); padding: 2rem; }
    </style>
</head>
<body>
    {{content}}
    <script>
        // Optional interactivity
    </script>
</body>
</html>
```

## Constraints
- Self-contained: no external CDN links, no external CSS/JS
- Max file size: ~50KB
- Must be valid HTML5
- Dark theme by default, legible in both light and dark
- Responsive layout (works on mobile)

## Example
A single-file dashboard showing project metrics with CSS Grid layout and inline SVG charts.
