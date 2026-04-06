# app/diff/fetcher.py
from __future__ import annotations

import os
from typing import Union

from app.adapters.base import PullRequestClient
from app.adapters.github import GitHubAdapter
from app.schemas import PRMeta as PRMetaModel


def get_adapter(provider: str, token: str | None = None) -> PullRequestClient:
    """
    Return a concrete adapter for the given provider.
    Currently supports: github
    """
    provider = (provider or "").lower()
    token = token or os.getenv("GITHUB_TOKEN")

    if provider == "github":
        return GitHubAdapter(token=token)  # adapter handles auth headers internally

    raise NotImplementedError(f"Provider '{provider}' is not supported yet.")


def fetch_pr_meta(provider: str, repo: str, pr_number: Union[str, int]) -> PRMetaModel:
    """
    Fetch PR metadata via the provider adapter and normalize it
    into the schemas.PRMeta shape expected by the API.
    """
    adapter = get_adapter(provider)
    raw = adapter.get_pr_meta(repo, pr_number)  # likely raw GitHub JSON

    # Normalize to your API model
    title = raw.get("title", "")
    author = raw.get("author") or (raw.get("user", {}) or {}).get("login", "")
    branch = raw.get("branch") or (raw.get("head", {}) or {}).get("ref", "")
    created_at = raw.get("created_at", "")
    description = raw.get("description") or raw.get("body", "") or ""

    return PRMetaModel(
        title=title,
        author=author,
        branch=branch,
        created_at=created_at,
        description=description,
    )


def fetch_pr_diff(provider: str, repo: str, pr_number: Union[str, int]) -> str:
    """
    Fetch the unified diff text of a PR via the provider adapter.
    """
    adapter = get_adapter(provider)
    return adapter.get_pr_diff(repo, pr_number)
