#!/usr/bin/env python3
"""
v8 Token Stats Status Line — Detailed token and cache usage.

Output: project-name | In: 15.2k | Out: 4.5k | Cache: 2.1k/1.8k | 42% ctx | $0.12

Shows input tokens, output tokens, cache creation/read stats, context percentage, and cost.
"""
import json
import os
import sys


def format_tokens(count: int) -> str:
    """Format token count with k/M suffix."""
    if count >= 1_000_000:
        return f"{count / 1_000_000:.2f}M"
    if count >= 1000:
        return f"{count / 1000:.1f}k"
    return str(count)


def format_cost(usd: float) -> str:
    if usd < 0.01:
        return f"${usd:.4f}"
    return f"${usd:.2f}"


def main():
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        data = {}

    project_dir = (data.get("workspace") or {}).get("project_dir", os.getcwd())
    project = os.path.basename(project_dir)
    ctx = data.get("context_window") or {}
    input_tokens = ctx.get("total_input_tokens", 0)
    output_tokens = ctx.get("total_output_tokens", 0)
    cache_creation = ctx.get("cache_creation_input_tokens", 0)
    cache_read = ctx.get("cache_read_input_tokens", 0)
    used_pct = ctx.get("used_percentage", 0)
    cost = (data.get("cost") or {}).get("total_cost_usd", 0)

    parts = [
        project,
        f"In: {format_tokens(input_tokens)}",
        f"Out: {format_tokens(output_tokens)}",
    ]

    # Only show cache stats if there's cache activity
    if cache_creation or cache_read:
        parts.append(f"Cache: {format_tokens(cache_creation)}/{format_tokens(cache_read)}")

    parts.append(f"{used_pct}% ctx")
    parts.append(format_cost(cost))

    print(" | ".join(parts))


if __name__ == "__main__":
    main()
