# app/scoring/score.py
from __future__ import annotations

from typing import Dict, Tuple, List
from app.schemas import Finding

# Per-type base weights (tune as you like)
TYPE_WEIGHTS: Dict[str, float] = {
    "secret": 1.0,       # most severe if found
    "security": 0.9,
    "test": 0.5,
    "complexity": 0.4,
    "style": 0.3,
    # If you introduced a distinct "ai" type, add it here (often advisory):
    "ai": 0.2,
}

# Per-severity multipliers
SEVERITY_MULT: Dict[str, float] = {
    "high": 1.0,
    "medium": 0.6,
    "low": 0.3,
}

# Cap how much each category can penalize
CATEGORY_CAPS: Dict[str, float] = {
    "secret": 50.0,      # secrets should tank the score quickly
    "security": 35.0,
    "test": 20.0,
    "complexity": 15.0,
    "style": 12.0,
    "ai": 8.0,           # advisory
}

BASE_SCORE = 100.0

def score_findings(findings: List[Finding]) -> int:
    """
    Convert a set of findings into a single 0–100 score.
    We subtract penalties by type*severity, then clamp to [0, 100].
    """
    if not findings:
        return 100

    # accumulate penalties per category
    penalties: Dict[str, float] = {k: 0.0 for k in TYPE_WEIGHTS.keys()}

    for f in findings:
        ftype = getattr(f, "type", "style")
        sev = getattr(f, "severity", "low")
        tw = TYPE_WEIGHTS.get(ftype, 0.3)
        sv = SEVERITY_MULT.get(sev, 0.3)

        penalties[ftype] = penalties.get(ftype, 0.0) + (tw * sv * 10.0)

    # apply category caps
    total_penalty = 0.0
    for ctype, pen in penalties.items():
        cap = CATEGORY_CAPS.get(ctype, 10.0)
        total_penalty += min(pen, cap)

    score = BASE_SCORE - total_penalty
    if score < 0:
        score = 0
    if score > 100:
        score = 100
    return int(round(score))
