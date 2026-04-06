"""
Semgrep integration for PR diffs.

Two modes:
1) Repository mode (recommended)
   - You pass a local repo path (already checked out by CI or developer).
   - We run `semgrep` against that repo, filtered to changed files.

2) Diff-only mode (fallback)
   - No repo path? We reconstruct minimal temp files containing only *added*
     lines and run semgrep over those. Results are limited (no full context),
     but still catch many simple rules.

Prereqs:
- `semgrep` CLI installed and available in PATH.
  Install: `pip install semgrep` or see https://semgrep.dev/docs/getting-started/

Usage:
    from app.analyzers.semgrep_runner import run_semgrep
    findings = run_semgrep(diff_files, repo_path=".", config="p/ci")

Returned findings are compatible with the pipeline (List[Finding]).
"""

import json
import os
import shutil
import subprocess
import tempfile
from typing import Iterable, List, Optional

from app.schemas import Finding

# Default Semgrep config:
# - "p/ci" is a good general-purpose ruleset. You can change via env or parameter.
_DEFAULT_CONFIG = os.getenv("SEMGREP_CONFIG", "p/ci")
# Floor helps reduce noise; INFO|WARNING|ERROR. Map to low/med/high later.
_DEFAULT_SEVERITY_FLOOR = os.getenv("SEMGREP_SEVERITY", "INFO")

def _map_semgrep_severity(sev: str) -> str:
    """
    Map Semgrep severities (INFO/WARNING/ERROR) to our Severity.
    """
    s = (sev or "").upper()
    if s == "ERROR":
        return "high"
    if s == "WARNING":
        return "medium"
    return "low"  # INFO or unknown

def _which_semgrep() -> Optional[str]:
    return shutil.which("semgrep")

def _write_temp_files_from_diff(diff_files) -> str:
    """
    Create a temp directory with minimal files constructed from *added lines*.
    This enables a rough semgrep scan without a full repo checkout.
    """
    tmpdir = tempfile.mkdtemp(prefix="pr_semgrep_")
    for f in diff_files:
        # Only scan text-like files; `.py`, `.js`, etc. — here we keep it simple:
        if getattr(f, "is_binary", False):
            continue
        if not f.added:
            continue

        # Create any necessary directories
        abs_path = os.path.join(tmpdir, f.path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)

        # Write just the added lines; semgrep can still catch many patterns
        with open(abs_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(ln.text for ln in f.added))
    return tmpdir

def _run_semgrep_json(target_path: str, include_paths: Iterable[str], config: str, severity_floor: str) -> dict:
    """
    Execute semgrep and return the parsed JSON.
    We pass --include to reduce scanning surface to changed files (repo mode).
    """
    cmd = [
        _which_semgrep(), "scan",
        "--json",
        "--config", config,
        "--severity", severity_floor,
        "--timeout", "120",
    ]

    # Restrict scope when possible; in diff-only mode include_paths are relative to temp root.
    for p in include_paths:
        # Semgrep supports multiple --include patterns.
        cmd += ["--include", p]

    # Target
    cmd.append(target_path)

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode not in (0, 1):  # 1 means findings found; not an execution failure
        raise RuntimeError(f"Semgrep failed: rc={proc.returncode}, stderr={proc.stderr[:4000]}")
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        raise RuntimeError(f"Semgrep returned non-JSON output. stderr={proc.stderr[:4000]}")

def run_semgrep(
    diff_files,
    repo_path: Optional[str] = None,
    config: str = _DEFAULT_CONFIG,
    severity_floor: str = _DEFAULT_SEVERITY_FLOOR,
) -> List[Finding]:
    """
    Run Semgrep and convert results to our Finding objects.

    Args:
      diff_files: parsed diff (List[DiffFile]) from parser.parse_unified_diff()
      repo_path: optional local repo root to scan (preferred). If None, we create temp files from added lines only.
      config: semgrep config id or rules path (e.g., "p/ci", "p/security-audit", or a local YAML)
      severity_floor: "INFO" | "WARNING" | "ERROR"
    """
    semgrep_bin = _which_semgrep()
    if not semgrep_bin:
        # Semgrep not installed; skip gracefully.
        return []

    # Decide scanning target and the file scope to include:
    temp_dir = None
    include_paths = []

    try:
        if repo_path and os.path.isdir(repo_path):
            # REPOSITORY MODE: scan the local checkout, but only include changed files for speed.
            target = repo_path
            include_paths = [f.path for f in diff_files if not getattr(f, "is_binary", False)]
        else:
            # DIFF-ONLY MODE: construct minimal files with *added* lines into a temp dir.
            temp_dir = _write_temp_files_from_diff(diff_files)
            target = temp_dir
            include_paths = [f.path for f in diff_files if f.added and not getattr(f, "is_binary", False)]

        # Run semgrep with JSON output
        result = _run_semgrep_json(target, include_paths, config=config, severity_floor=severity_floor)

        # Convert semgrep findings to our schema
        findings: List[Finding] = []
        for r in result.get("results", []):
            path = r.get("path", "")
            start = (r.get("start", {}) or {}).get("line")
            extra = r.get("extra", {}) or {}
            message = extra.get("message", "Semgrep finding")
            sev = _map_semgrep_severity(extra.get("severity", "INFO"))
            check_id = extra.get("check_id", "")
            # Prefer classifying as "security" if severity >= medium; otherwise "style"
            ftype = "security" if sev in ("medium", "high") else "style"

            # Keep messages small but informative
            final_msg = f"[{check_id}] {message}" if check_id else message

            findings.append(Finding(
                file=path,
                line=start,
                type=ftype,
                severity=sev,
                message=final_msg,
                suggestion=extra.get("metavars", {}).get("suggestion") if isinstance(extra.get("metavars"), dict) else None,
            ))

        return findings

    finally:
        # Clean up temporary directory in diff-only mode
        if temp_dir and os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
