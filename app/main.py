import os
import app.config  # ensures .env is loaded
from typing import Union
from fastapi import FastAPI, HTTPException, Query
from app.schemas import ReviewRequest, ReviewResponse, PRMeta, Finding

from app.diff.fetcher import fetch_pr_meta, fetch_pr_diff
from app.diff.parser import parse_unified_diff

from app.analyzers.secrets import run_secrets
from app.analyzers.heuristics import run_heuristics
from app.analyzers.python_static import run_python_static
from app.analyzers.semgrep_runner import run_semgrep
from app.analyzers.ai_reviewer import run_ai_review

from app.scoring.score import compute_score
from app.writers.summary_md import render_markdown


app = FastAPI(
    title="PR Review Agent",
    description="Multi-Git Pull Request Analysis API",
    version="0.1.1",
)


@app.get("/", tags=["Health Check"])
def root():
    return {"status": "ok", "message": "PR Review Agent is running."}


@app.get("/meta", response_model=PRMeta, tags=["PR Metadata"])
def get_pr_metadata(
    provider: str = Query(...),
    repo: str = Query(...),
    pr_number: Union[str, int] = Query(...),
):
    try:
        return fetch_pr_meta(provider, repo, pr_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch PR metadata: {str(e)}")


@app.get("/diff", tags=["PR Diff"])
def get_pr_diff(
    provider: str = Query(...),
    repo: str = Query(...),
    pr_number: Union[str, int] = Query(...),
):
    try:
        diff = fetch_pr_diff(provider, repo, pr_number)
        return {"length": len(diff), "preview": diff[:1000], "truncated": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch PR diff: {str(e)}")


@app.post("/review", response_model=ReviewResponse, tags=["Review"])
def review_pr(req: ReviewRequest):
    """
    Main review endpoint:
    1. Fetches PR diff
    2. Parses diff files
    3. Runs static analyzers + AI reviewer
    4. Computes score
    5. Returns markdown summary
    """
    try:
        diff = fetch_pr_diff(req.provider, req.repo, req.pr_number)
        if not diff or diff.strip() == "":
            return ReviewResponse(
                score=100,
                summary_markdown="# No diff\nNo changes to review.",
                findings=[],
            )

        files = parse_unified_diff(diff)

        findings: list[Finding] = []
        findings += run_secrets(files)
        findings += run_heuristics(files)
        findings += run_python_static(files)
        findings += run_semgrep(files, repo_path=None, config=os.getenv("SEMGREP_CONFIG", "p/ci"))
        findings += run_ai_review(files)

        if len(findings) > req.max_findings:
            findings = findings[:req.max_findings]

        score = compute_score(findings)
        summary = render_markdown(req.repo, str(req.pr_number), score, findings)

        return ReviewResponse(score=score, summary_markdown=summary, findings=findings)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review failed: {str(e)}")
