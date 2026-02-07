#!/usr/bin/env python3
"""
Subagent task summarization via Anthropic haiku.

Generates ultra-concise (<20 word) summaries of what a subagent accomplished,
suitable for TTS announcements and session audit logs.

Import via sys.path injection:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from utils.llm.task_summarizer import summarize_task, extract_task_context
"""
import json
import sys
from pathlib import Path

# Ensure utils is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from llm.anthropic_client import get_completion


def summarize_task(transcript_excerpt: str) -> str:
    """
    Summarize what a subagent did in under 20 words.

    Args:
        transcript_excerpt: Excerpt from the subagent's transcript (first ~500 chars).

    Returns:
        A concise summary string. Falls back to truncation if LLM unavailable.
    """
    if not transcript_excerpt or not transcript_excerpt.strip():
        return "Subagent completed."

    result = get_completion(
        f"Summarize this completed task in under 20 words: "
        f"{transcript_excerpt[:500]}. "
        f"Reply with ONLY the summary, no quotes or prefix."
    )

    if result and len(result) < 120:
        return result

    # Fallback: truncate the excerpt
    clean = transcript_excerpt.strip().replace("\n", " ")[:80]
    return f"{clean}..." if len(transcript_excerpt) > 80 else clean


def extract_task_context(transcript_path: str) -> str:
    """
    Extract task context from a subagent transcript JSONL file.

    Looks for the first user prompt in the transcript to understand
    what the subagent was asked to do.

    Args:
        transcript_path: Path to the agent's transcript .jsonl file.

    Returns:
        The first user prompt text (up to 200 chars), or empty string.
    """
    try:
        path = Path(transcript_path)
        if not path.exists():
            return ""

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Check for user messages
                if entry.get("type") == "user":
                    content = entry.get("message", {}).get("content", "")
                    if isinstance(content, list):
                        # Content blocks format
                        texts = [
                            c.get("text", "")
                            for c in content
                            if isinstance(c, dict) and c.get("type") == "text"
                        ]
                        content = " ".join(texts)
                    if isinstance(content, str) and content.strip():
                        return content.strip()[:200]

                # Check for direct prompt field
                prompt = entry.get("prompt", "")
                if isinstance(prompt, str) and prompt.strip():
                    return prompt.strip()[:200]

    except (OSError, ValueError):
        pass

    return ""
