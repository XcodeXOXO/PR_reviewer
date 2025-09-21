"""
AI-powered reviewer that augments heuristic/static checks with LLM suggestions.

Provider: OpenRouter (https://openrouter.ai/)
Default Model: qwen/qwen3-coder:free  (set via env AI_MODEL)
Key: set OPENROUTER_API_KEY in your .env
Endpoint: https://openrouter.ai/api/v1/chat/completions

This module ALSO pulls in:
  - python_static.run_python_static(...)  -> Python-specific static checks
  - semgrep_runner.run_semgrep(...)       -> Security/style rules via Semgrep
"""

from __future__ import annotations

import json
import os
import re
from typing import List, Optional

import requests

from app.schemas import Finding
from app.analyzers.python_static import run_python_static
from app.analyzers.semgrep_runner import run_semgrep

# --------------------------
# Configuration via ENV VARS
# --------------------------
# Default to Qwen free coder model
AI_MODEL = os.getenv("AI_MODEL", "qwen/qwen3-coder:free")
AI_API_URL = os.getenv("AI_API_URL", "https://openrouter.ai/api/v1/chat/completions")
AI_KEY = os.getenv("OPENROUTER_API_KEY")
USE_AI = os.getenv("USE_AI", "true").lower() == "true"

MAX_FILES = int(os.getenv("AI_MAX_FILES", "12"))
MAX_ADDED_LINES_PER_FILE = int(os.getenv("AI_MAX_ADDED_LINES_PER_FILE", "60"))
MAX_PROMPT_CHARS = int(os.getenv("AI_MAX_PROMPT_CHARS", "9000"))
TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.2"))

SYSTEM_PROMPT = """You are a senior code reviewer.
You receive code diffs (added lines only) and a short list of static-analysis flags.
Give concise, actionable feedback focused on correctness, readability, maintainability, and standards.

OUTPUT FORMAT (STRICT JSON ONLY):
[
  { "file": "<relative/path>", "line": <int or null>, "message": "<what's wrong and why>",
    "suggestion": "<how to improve>", "severity": "low|medium|high" }
]
"""

USER_INSTRUCTIONS = """Review the following diffs and static signals.
Return STRICT JSON ONLY (no markdown fences, no commentary).
Prefer high-signal comments. Avoid nitpicks unless clarity/readability is poor.

=== STATIC SIGNALS ===
{static_summary}

=== DIFF SNIPPETS (added lines, first {max_added} per file) ===
{diff_snippets}
"""

# --- Utility functions (_truncate, _extract_json_block, _build_static_summary, _build_diff_snippets) ---
# Keep them exactly the same as in the last version I gave you.
# (Not repeating here for brevity, but they stay unchanged.)

# --------------------------
# Public entrypoint
# --------------------------
def run_ai_review(diff_files) -> List[Finding]:
    """
    Produce LLM-driven review comments via OpenRouter’s qwen/qwen3-coder:free model.
    Returns Finding objects with type="style".
    """
    if not USE_AI or not AI_KEY:
        return []

    static_summary = _build_static_summary(diff_files)
    diff_snippets = _build_diff_snippets(diff_files)

    user_msg = USER_INSTRUCTIONS.format(
        static_summary=static_summary,
        diff_snippets=diff_snippets,
        max_added=MAX_ADDED_LINES_PER_FILE,
    )

    payload = {
        "model": AI_MODEL,  # now defaults to qwen/qwen3-coder:free
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        "temperature": TEMPERATURE,
    }

    try:
        res = requests.post(
            AI_API_URL,
            headers={
                "Authorization": f"Bearer {AI_KEY}",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "PR Review Agent",
            },
            json=payload,
            timeout=45,
        )
        res.raise_for_status()
        content = res.json()["choices"][0]["message"]["content"].strip()

        candidate = _extract_json_block(content) or content
        data = json.loads(candidate)

        findings: List[Finding] = []
        for item in data:
            file = item.get("file") or "*"
            line = item.get("line")
            if isinstance(line, str) and line.isdigit():
                line = int(line)
            severity = (item.get("severity") or "low").lower()
            if severity not in ("low", "medium", "high"):
                severity = "low"

            findings.append(Finding(
                file=file,
                line=line if isinstance(line, int) else None,
                type="style",
                severity=severity,
                message=item.get("message", "").strip()[:500],
                suggestion=(item.get("suggestion") or "").strip()[:500] or None,
            ))
        return findings

    except Exception as e:
        print(f"[AI Reviewer] Failed: {e}")
        return []
