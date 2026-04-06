# this file contains analyzer for finding secrets in code diffs


import re
from typing import List
from app.schemas import Finding

_PATTERNS = [
    ("AWS Access Key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("AWS Secret Key", re.compile(r"(?i)\baws_secret_access_key\b\s*[:=]\s*[A-Za-z0-9/+=]{30,}")),
    ("GitHub Token",   re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("Slack Token",    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,48}\b")),
    ("Google API Key", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")),
    ("Private Key",    re.compile(r"-----BEGIN (?:RSA|DSA|EC|OPENSSH) PRIVATE KEY-----")),
]

def run_secrets(diff_files) -> List[Finding]:
    findings: List[Finding] = []
    for f in diff_files:
        if getattr(f, "is_binary", False):  # skip binaries
            continue
        for line in f.added:  # only newly added lines
            for label, pat in _PATTERNS:
                if pat.search(line.text):
                    sev = "high" if label in ("Private Key", "AWS Access Key", "AWS Secret Key", "GitHub Token", "Slack Token") else "medium"
                    findings.append(Finding(
                        file=f.path,
                        line=line.num,
                        type="secret",
                        severity=sev,
                        message=f"Potential secret detected: {label}",
                        suggestion="Remove and rotate immediately. Use env vars or a secret manager; purge from history if committed."
                    ))
    return findings
