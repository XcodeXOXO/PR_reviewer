import re
from dataclasses import dataclass, field
from typing import List, Optional

# Matches: @@ -12,5 +12,7 @@ optional heading
HUNK_RE = re.compile(r"^@@ -(?P<old_start>\d+)(?:,(?P<old_len>\d+))? \+(?P<new_start>\d+)(?:,(?P<new_len>\d+))? @@")

@dataclass
class Line:
    num: int
    text: str

@dataclass
class DiffFile:
    path: str
    old_path: Optional[str] = None
    status: str = "modified"   # modified|added|deleted|renamed|binary
    is_binary: bool = False
    added: List[Line] = field(default_factory=list)
    removed: List[Line] = field(default_factory=list)

_IGNORE_PATH_HINTS = (
    "/dist/", "/build/", "/.next/", "/out/", "/vendor/", "/third_party/",
)
_IGNORE_FILE_SUFFIXES = (
    ".min.js", ".lock", ".map", ".zip", ".tar", ".gz", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf"
)

def _strip_ab_prefix(p: str) -> str:
    if p.startswith("a/") or p.startswith("b/"):
        return p[2:]
    return p

def should_ignore_path(path: str) -> bool:
    lp = path.lower()
    if any(h in lp for h in _IGNORE_PATH_HINTS):
        return True
    if any(lp.endswith(s) for s in _IGNORE_FILE_SUFFIXES):
        return True
    return False

def parse_unified_diff(diff_text: str, max_bytes_per_file: int = 2_000_000) -> List[DiffFile]:
    """
    Parse a git unified diff (like GitHub's pull diff) into DiffFile entries.
    Supports added/deleted/renamed/binary files, multiple hunks, and CRLF/LF.
    """
    files: List[DiffFile] = []
    current: DiffFile | None = None
    old_line = new_line = None

    # Normalize newlines early
    lines = diff_text.replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]

        # Start of a file block
        if line.startswith("diff --git "):
            if current:
                files.append(current)
                current = None
            i += 1
            continue

        # Index / mode hints (optional informative lines)
        if line.startswith("new file mode "):
            if current:
                current.status = "added"
            i += 1; continue
        if line.startswith("deleted file mode "):
            if current:
                current.status = "deleted"
            i += 1; continue
        if line.startswith("rename from "):
            if current:
                current.status = "renamed"
                current.old_path = line[len("rename from "):].strip()
            i += 1; continue
        if line.startswith("rename to "):
            # next line sets new path via +++ typically; keep status
            i += 1; continue
        if line.startswith("Binary files ") and " differ" in line:
            if current:
                current.is_binary = True
                current.status = "binary"
            i += 1; continue

        # --- old, +++ new
        if line.startswith("--- "):
            old_path = line[4:].strip()
            i += 1
            if i < len(lines) and lines[i].startswith("+++ "):
                new_path = lines[i][4:].strip()
                # Determine path, including /dev/null cases
                if new_path == "/dev/null":
                    # file deleted
                    path = _strip_ab_prefix(old_path)
                    current = DiffFile(path=_strip_ab_prefix(path), status="deleted")
                elif old_path == "/dev/null":
                    # file added
                    path = _strip_ab_prefix(new_path)
                    current = DiffFile(path=_strip_ab_prefix(path), status="added")
                else:
                    path = _strip_ab_prefix(new_path)
                    current = DiffFile(path=_strip_ab_prefix(path))
                old_line = None
                new_line = None
                i += 1
                continue
            else:
                continue  # malformed header; skip

        # Hunk header
        m = HUNK_RE.match(line)
        if m and current:
            # Skip ignored paths entirely to reduce noise
            if should_ignore_path(current.path):
                # fast-forward to next file block
                i += 1
                while i < len(lines) and not lines[i].startswith("diff --git "):
                    i += 1
                continue

            old_line = int(m.group("old_start"))
            new_line = int(m.group("new_start"))
            i += 1
            added_bytes = 0

            while i < len(lines):
                ln = lines[i]

                # Breakout conditions
                if ln.startswith("diff --git ") or ln.startswith("--- ") or HUNK_RE.match(ln):
                    break

                if ln.startswith("\\ No newline at end of file"):
                    i += 1; continue

                if current.is_binary:
                    i += 1; continue

                if ln.startswith("+"):
                    text = ln[1:]
                    added_bytes += len(text.encode("utf-8"))
                    if added_bytes <= max_bytes_per_file and new_line is not None:
                        current.added.append(Line(num=new_line, text=text))
                    if new_line is not None:
                        new_line += 1
                    i += 1; continue

                if ln.startswith("-"):
                    text = ln[1:]
                    if old_line is not None:
                        current.removed.append(Line(num=old_line, text=text))
                        old_line += 1
                    i += 1; continue

                # Context line (space or empty)
                if ln.startswith(" ") or ln == "":
                    if old_line is not None: old_line += 1
                    if new_line is not None: new_line += 1
                    i += 1; continue

                # Unknown line kinds; advance
                i += 1
            continue

        i += 1

    if current:
        files.append(current)
    return files
