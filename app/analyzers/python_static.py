"""
Python-specific static checks over PR diffs.

Design goals:
- Fast, dependency-free.
- Works on DIFF ONLY (no full repo). We scan *added* lines because those are
  the changes being introduced by this PR.
- Complements heuristics/secrets with Python-flavored issues that an AI model
  can elaborate on (readability, standards, potential bugs).

Limitations:
- We don't have full-file context/AST; added-line scanning is heuristic.
- Some checks may be noisy in partial hunks; keep severities conservative.

Usage:
    from app.analyzers.python_static import run_python_static
    findings = run_python_static(diff_files)

Where `diff_files` is the parsed output from app.diff.parser.parse_unified_diff().
"""

import re
from typing import List

from app.schemas import Finding

# --- Lightweight patterns that are useful in PR reviews ---

_RE_BROAD_EXCEPT = re.compile(r"^\s*except\s*:?(\s*Exception)?\s*:?\s*$", re.IGNORECASE)
_RE_EVAL = re.compile(r"\beval\s*\(", re.IGNORECASE)
_RE_EXEC = re.compile(r"\bexec\s*\(", re.IGNORECASE)
_RE_PRINT = re.compile(r"(^|\s)print\s*\(", re.IGNORECASE)  # basic signal for stray prints
_RE_PASSWD = re.compile(r"(?i)\bpassword\b\s*[:=]\s*['\"].+['\"]")
_RE_TODO_DOC = re.compile(r'^\s*(def|class)\s+[A-Za-z_][A-Za-z0-9_]*\s*\(?.*\)?:\s*$')
_RE_TRIPLE_QUOTE = re.compile(r'^\s*(?:[ru]|[fF][rR]|[rR][fF])?(?:"""|\'\'\')')

_TEST_HINTS = ("test/", "tests/", "_test.", ".spec.", ".test.")

def _looks_like_test(path: str) -> bool:
    p = path.lower()
    return any(h in p for h in _TEST_HINTS)

def _is_python_file(path: str) -> bool:
    return path.lower().endswith(".py")

def run_python_static(diff_files) -> List[Finding]:
    """
    Scan *added* Python lines for common issues:
      - broad `except:` or `except Exception:`
      - use of eval()/exec()
      - stray print() in non-test code
      - def/class missing immediate docstring (best-effort on added lines)
      - hardcoded password assignments
    """
    findings: List[Finding] = []

    for f in diff_files:
        if not _is_python_file(f.path) or getattr(f, "is_binary", False):
            continue

        # Heuristic: track whether the next added line after a def/class is a docstring
        pending_doc_check_line = None

        for ln in f.added:
            text = ln.text

            # 1) Broad except
            if _RE_BROAD_EXCEPT.match(text):
                findings.append(Finding(
                    file=f.path, line=ln.num, type="security", severity="medium",
                    message="Broad exception handler detected.",
                    suggestion="Catch specific exception types to avoid masking errors."
                ))

            # 2) eval / exec
            if _RE_EVAL.search(text) or _RE_EXEC.search(text):
                findings.append(Finding(
                    file=f.path, line=ln.num, type="security", severity="high",
                    message="Use of eval()/exec() detected.",
                    suggestion="Avoid dynamic code execution. Consider safer alternatives (mapping functions, parsers)."
                ))

            # 3) print() in non-test code (could be leftover debugging)
            if _RE_PRINT.search(text) and not _looks_like_test(f.path):
                findings.append(Finding(
                    file=f.path, line=ln.num, type="style", severity="low",
                    message="print() call found in production code.",
                    suggestion="Use structured logging instead of print statements."
                ))

            # 4) Hardcoded password assignment (very rough signal)
            if _RE_PASSWD.search(text):
                findings.append(Finding(
                    file=f.path, line=ln.num, type="security", severity="medium",
                    message="Hardcoded password detected.",
                    suggestion="Store secrets in environment variables or a secret manager."
                ))

            # 5) Missing docstring (best effort on a def/class line)
            if _RE_TODO_DOC.match(text):
                # Next *added* line should be a triple-quoted string to count as a docstring
                pending_doc_check_line = ln.num
                continue

            # If we were expecting a docstring, check this added line
            if pending_doc_check_line is not None:
                if not _RE_TRIPLE_QUOTE.match(text.strip()):
                    findings.append(Finding(
                        file=f.path, line=pending_doc_check_line, type="style", severity="low",
                        message="Function/class appears to be missing a docstring.",
                        suggestion="Add a short docstring describing purpose and parameters."
                    ))
                # Reset regardless; only check immediately following added line
                pending_doc_check_line = None

        # Edge case: file ends right after a def/class line in added code
        if pending_doc_check_line is not None:
            findings.append(Finding(
                file=f.path, line=pending_doc_check_line, type="style", severity="low",
                message="Function/class appears to be missing a docstring.",
                suggestion="Add a short docstring describing purpose and parameters."
            ))

    return findings
