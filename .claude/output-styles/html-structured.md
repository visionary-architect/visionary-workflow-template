---
description: "HTML fragments — Embeddable content for web integration"
---

# HTML-Structured Output Style

## When to Use
- Generating content to embed in web pages
- Email templates
- Component markup (not full pages)
- Structured content with semantic HTML

## Format Template
```html
<section class="{{section-class}}">
  <h2>{{title}}</h2>
  <div class="content">
    {{structured content}}
  </div>
</section>
```

## Constraints
- Valid HTML5 fragments (not full documents)
- Use semantic elements (article, section, nav, header, footer)
- Include class names for styling hooks
- No inline styles (use class-based styling)
- No JavaScript (pure markup)
- Self-closing tags for void elements
- Maximum ~2KB per fragment

## Example
```html
<article class="status-report">
  <header>
    <h2>Build Status</h2>
    <time datetime="2026-02-06">Feb 6, 2026</time>
  </header>
  <dl class="metrics">
    <dt>Tests</dt><dd>142 passed</dd>
    <dt>Coverage</dt><dd>87%</dd>
    <dt>Build Time</dt><dd>2m 34s</dd>
  </dl>
</article>
```
