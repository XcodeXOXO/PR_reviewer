#  Architecture Overview — AI PR Reviewer

## Overview
The system automates code reviews by combining static analysis tools and AI reasoning through OpenRouter’s Qwen-3-Coder model.

## Core Components
- **app/main.py:** FastAPI entrypoint exposing `/review` endpoint.
- **diff/**: Fetches PR diffs and parses file changes.
- **analyzers/**: Runs static, heuristic, and AI-based analysis.
- **scoring/**: Normalizes severity levels into a final score.
- **writers/**: Formats final output.
- **frontend/**: Interactive dashboard connected via API (Bolt-generated).

## Workflow
1. PR metadata is fetched via GitHub API.
2. Diff and static checks are parsed.
3. AI reviewer analyzes added lines using Qwen model.
4. Findings are merged, scored, and returned as JSON.

## Dependencies
- FastAPI, Requests, Semgrep, OpenRouter API.
- Qwen-3-Coder (via OpenRouter).
