---
description: "YAML blocks — Configuration output, structured key-value data"
---

# YAML-Structured Output Style

## When to Use
- Outputting configuration files or snippets
- Structured key-value data
- Infrastructure definitions
- Environment variable documentation

## Format Template
````markdown
```yaml
# {{Section description}}
key: value
nested:
  child_key: child_value
  list:
    - item_1
    - item_2
```
````

## Constraints
- Valid YAML syntax (parseable)
- Include comments for non-obvious values
- Use 2-space indentation
- Quote strings that could be misinterpreted (yes/no, true/false, numbers)
- Group related keys under nested structures
- Maximum 50 lines per block

## Example
```yaml
# Database configuration
database:
  host: "localhost"
  port: 5432
  name: "field_control"
  pool:
    min_connections: 2
    max_connections: 10
    timeout_seconds: 30
```
