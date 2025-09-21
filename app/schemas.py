# app/schemas.py
from typing import Optional, List, Literal, Union
from pydantic import BaseModel, Field, constr, field_validator
import re

Provider = Literal["github", "gitlab", "bitbucket"]

# ---- PR metadata (used by GET /meta) ----
class PRMeta(BaseModel):
    title: str
    author: str
    branch: str
    created_at: str
    description: Optional[str] = ""

# ---- Findings & review I/O ----
# If you separated AI findings, add "ai" here; otherwise keep as-is.
FindingType = Literal["secret", "security", "style", "test", "complexity"]
Severity = Literal["low", "medium", "high"]

REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")

class Finding(BaseModel):
    file: str = Field(..., description="Relative path of the file in the repo")
    line: Optional[int] = Field(None, ge=1, description="1-based line number (if applicable)")
    type: FindingType
    severity: Severity
    message: constr(min_length=3)
    suggestion: Optional[constr(min_length=3)] = None

class ReviewResponse(BaseModel):
    score: int = Field(..., ge=0, le=100)
    summary_markdown: str
    findings: List[Finding]

class ReviewRequest(BaseModel):
    provider: Provider
    repo: constr(min_length=3) = Field(..., description="Format: owner/repo")
    pr_number: Union[str, int]
    max_findings: int = Field(200, ge=1, le=1000)

    @field_validator("repo")
    @classmethod
    def _validate_repo(cls, v: str) -> str:
        if not REPO_PATTERN.match(v):
            raise ValueError("repo must be in 'owner/repo' format")
        return v

    @field_validator("pr_number")
    @classmethod
    def _validate_pr_number(cls, v: Union[str, int]) -> Union[str, int]:
        if isinstance(v, int):
            if v <= 0:
                raise ValueError("pr_number must be a positive integer")
            return v
        v_str = v.strip()
        if not v_str.isdigit():
            raise ValueError("pr_number must be numeric (e.g., 1)")
        return v_str
