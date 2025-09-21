# app/writers/summary_md.py
from collections import Counter
from typing import List
from app.schemas import Finding

def render_markdown(repo: str, pr: str, score: int, findings: List[Finding]) -> str:
    """
    Build a concise, readable Markdown summary for a PR review.
    Includes overall score, signal counts, and top findings.
    """
    header = f"# PR Review — {repo}#{pr}\n\n**Quality Score:** {score}/100\n\n"

    if not findings:
        return header + "_No issues detected in the analyzed changes._\n"

    # Tally by finding type
    by_type = Counter(f.type for f in findings)
    signals = "## Signals\n" + "\n".join(
        f"- **{t.title()}**: {count}" for t, count in by_type.items()
    ) + "\n\n"

    # Detailed list (cap to keep it readable)
    details = "## Findings\n"
    for f in findings[:100]:
        loc = f":{f.line}" if f.line else ""
        details += f"- `{f.file}{loc}` — **{f.type}/{f.severity}** — {f.message}"
        if f.suggestion:
            details += f" _(suggestion: {f.suggestion})_"
        details += "\n"

    # If more were truncated, mention it
    if len(findings) > 100:
        details += f"\n_+ {len(findings) - 100} more findings not shown._\n"

    return header + signals + details
