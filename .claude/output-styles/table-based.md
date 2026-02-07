---
description: "Markdown tables — Data comparisons, feature matrices, structured data"
---

# Table-Based Output Style

## When to Use
- Comparing options, features, or alternatives
- Presenting structured data (configs, parameters, metrics)
- Status reports with multiple items
- Any tabular data that benefits from alignment

## Format Template
```markdown
## {{Title}}

| Column A | Column B | Column C |
|----------|----------|----------|
| data     | data     | data     |

> **Summary:** [One-line takeaway]
```

## Constraints
- Maximum 8 columns per table
- Maximum 30 rows per table
- Include a header row with descriptive column names
- Right-align numeric columns when possible
- Add a summary line below for key takeaways
- Use consistent formatting within columns

## Example
| Feature | Status | Priority |
|---------|--------|----------|
| Auth    | Done   | High     |
| Search  | WIP    | Medium   |
| Export  | Todo   | Low      |

> **Summary:** 1 of 3 features complete; auth ready for review.
