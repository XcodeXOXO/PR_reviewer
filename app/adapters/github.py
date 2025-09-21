import os
import requests
from typing import Union
from .base import PullRequestClient, PRMeta  # PRMeta is either TypedDict or Pydantic model

class GitHubAdapter(PullRequestClient):
    def __init__(self, token: str | None = None):
        # call authenticate in ctor so the adapter is ready to use
        self.token: str | None = None
        self.headers: dict[str, str] = {}
        self.authenticate(token)

    # >>> This method was missing <<<
    def authenticate(self, token: str | None = None) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError(
                "GITHUB_TOKEN not set. Put it in your .env or set $env:GITHUB_TOKEN in PowerShell."
            )
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json",
        }

    def get_pr_meta(self, repo: str, pr_number: Union[str, int]) -> PRMeta:
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
        res = requests.get(url, headers=self.headers, timeout=15)
        res.raise_for_status()
        data = res.json()
        return PRMeta(
            title=data.get("title", ""),
            author=data.get("user", {}).get("login", ""),
            branch=data.get("head", {}).get("ref", ""),
            created_at=data.get("created_at", ""),
            description=data.get("body", ""),
        )

    def get_pr_diff(self, repo: str, pr_number: Union[str, int]) -> str:
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
        headers = {**self.headers, "Accept": "application/vnd.github.v3.diff"}
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        return res.text

    def post_inline_comment(self, *args, **kwargs) -> None:
        raise NotImplementedError("Inline comments not yet supported.")
