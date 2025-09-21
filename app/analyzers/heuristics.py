from typing import List
from app.schemas import Finding

TEST_HINTS = ("test/", "tests/", "_test.", "test_", ".spec.", ".test.")
DOC_HINTS = ("/docs/", ".md", ".rst", ".adoc")

def _is_test(path: str) -> bool:
    p = path.lower()
    return any(h in p for h in TEST_HINTS)

def _is_doc(path: str) -> bool:
    p = path.lower()
    return any(h in p for h in DOC_HINTS)

def run_heuristics(diff_files) -> List[Finding]:
    findings: List[Finding] = []
    total_added = 0
    any_src_changed = False
    any_test_changed = False

    for f in diff_files:
        if getattr(f, "is_binary", False):
            continue

        added_count = len(f.added)
        removed_count = len(f.removed)
        total_added += added_count

        # track test vs src changes
        if _is_test(f.path):
            if added_count or removed_count:
                any_test_changed = True
        elif not _is_doc(f.path):
            if added_count or removed_count:
                any_src_changed = True

        # TODO/FIXME
        for ln in f.added:
            t = ln.text.lower()
            if "todo" in t or "fixme" in t:
                findings.append(Finding(
                    file=f.path, line=ln.num, type="style", severity="low",
                    message="Found TODO/FIXME in added code.",
                    suggestion="Convert into a tracked issue/reference or resolve before merge."
                ))

        # Very large single-file change
        if added_count >= 400:
            findings.append(Finding(
                file=f.path, line=None, type="complexity", severity="medium",
                message=f"Large change: {added_count} added lines.",
                suggestion="Split into smaller PRs or add more tests for safer review."
            ))

        # File added with a lot of code, but no tests touched
        if f.status == "added" and added_count >= 150 and not any_test_changed:
            findings.append(Finding(
                file=f.path, line=None, type="test", severity="medium",
                message="New file with substantial code but no tests changed.",
                suggestion="Add unit tests that cover key paths."
            ))

    # big PR signal
    if total_added >= 1000:
        findings.append(Finding(
            file="*",
            line=None,
            type="complexity",
            severity="high",
            message=f"Very large PR: {total_added} total added lines.",
            suggestion="Split into smaller PRs for faster, safer review."
        ))

    # logic without tests
    if any_src_changed and not any_test_changed:
        findings.append(Finding(
            file="*",
            line=None,
            type="test",
            severity="medium",
            message="Source files changed but no tests were updated.",
            suggestion="Add or update tests that cover the modified logic."
        ))

    return findings
