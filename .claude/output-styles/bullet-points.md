---
description: "Bullet lists — Action items, checklists, step-by-step instructions"
---

# Bullet Points Output Style

## When to Use
- Action items and checklists
- Step-by-step instructions
- Listing requirements or findings
- Quick summaries of multiple items

## Format Template
```markdown
## {{Title}}

- **Item 1:** Description
- **Item 2:** Description
  - Sub-item if needed
- **Item 3:** Description

### Next Steps
- [ ] Actionable checkbox item
- [ ] Another action
```

## Constraints
- Maximum 10 top-level bullets
- Bold the key term at the start of each bullet
- Use sub-bullets sparingly (max 3 levels)
- For checklists, use `- [ ]` syntax
- Keep each bullet to 1-2 lines
- Group related items under sub-headers

## Example
- **Authentication:** JWT tokens with 1-hour expiry
- **Authorization:** Role-based access (admin, user, viewer)
- **Rate limiting:** 100 requests/minute per API key
  - Burst: 20 requests/second
  - Headers: `X-RateLimit-Remaining`
