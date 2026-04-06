# app/scoring/score.py
from app.schemas import Finding

def compute_score(findings: list[Finding]) -> int:
    """
    Assigns a numerical quality score (0–100) based on severity of findings.
    High = -10 points, Medium = -5 points, Low = -2 points.
    Never drops below 0.
    """
    score = 100
    for f in findings:
        sev = f.severity.lower()
        if sev == "high":
            score -= 10
        elif sev == "medium":
            score -= 5
        elif sev == "low":
            score -= 2
    return max(score, 0)


def score_findings(findings: list[Finding]) -> dict:
    """
    Returns a dictionary summary of counts per severity and total score.
    Useful for debugging or visualization.
    """
    counts = {"low": 0, "medium": 0, "high": 0}
    for f in findings:
        sev = f.severity.lower()
        if sev in counts:
            counts[sev] += 1

    return {
        "counts": counts,
        "score": compute_score(findings),
    }
