#!/usr/bin/env python3
"""PostToolUse (Edit|Write) advisory: has finished work been sitting
uncommitted? Always exits 0. Never blocks a write.

Two triggers, because two different habits produce the same problem:

  volume  the working tree holds COMMIT_CADENCE_FILES or more changed files
  age     the tree is dirty and the last commit is older than
          COMMIT_CADENCE_MINUTES

Either one adds a line to the model's context naming the count, the age, and
the repository. The hook commits nothing itself. It cannot write a good commit
message, and a repository with commit-message, lint, or prose gates would
reject an automatic commit of half-finished work (or need --no-verify, which
turns those gates off).

It also never stages. A checkout shared with a concurrent session needs
explicit pathspecs, and `git add -A` from a hook would sweep up the other
session's files.

Rate limited per repository so a long editing run produces one reminder, not
one per write. State lives in a temp directory keyed by the repository path.

Environment:

    COMMIT_CADENCE_FILES     files before the volume trigger fires (default 5)
    COMMIT_CADENCE_MINUTES   minutes before the age trigger fires (default 20)
    COMMIT_CADENCE_QUIET     minutes between reminders per repo (default 10)
    COMMIT_CADENCE=0         turn the hook off
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from hookutil import additional_context, read_payload


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except ValueError:
        return default


PILE_THRESHOLD = _int_env("COMMIT_CADENCE_FILES", 5)
AGE_MINUTES = _int_env("COMMIT_CADENCE_MINUTES", 20)
QUIET_MINUTES = _int_env("COMMIT_CADENCE_QUIET", 10)

STATE_DIR = Path(tempfile.gettempdir()) / "claude-commit-cadence"


def git(root: str | Path, *args: str) -> str | None:
    """Run one git command; None when it fails or prints nothing useful."""
    try:
        done = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return done.stdout if done.returncode == 0 else None


def repo_root(path: Path) -> Path | None:
    start = path if path.is_dir() else path.parent
    out = git(start, "rev-parse", "--show-toplevel")
    return Path(out.strip()) if out and out.strip() else None


def recently_nudged(root: Path) -> bool:
    """True when this repository was nudged inside the quiet window."""
    key = hashlib.sha256(str(root).encode("utf-8")).hexdigest()[:16]
    stamp = STATE_DIR / f"{key}.stamp"
    now = time.time()
    try:
        if stamp.is_file() and now - stamp.stat().st_mtime < QUIET_MINUTES * 60:
            return True
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        stamp.write_text(str(now), encoding="utf-8")
    except OSError:
        # An unwritable state directory disables the rate limit, not the hook:
        # a repeated reminder is better than a silent one.
        return False
    return False


def main() -> int:
    if os.environ.get("COMMIT_CADENCE", "1") == "0":
        return 0

    data = read_payload()
    raw = (data.get("tool_input") or {}).get("file_path") or (data.get("tool_response") or {}).get("filePath")
    if not raw:
        return 0

    root = repo_root(Path(str(raw)))
    if root is None:
        return 0

    status = git(root, "status", "--porcelain")
    changed = [line for line in (status or "").splitlines() if line.strip()]
    if not changed:
        return 0

    last = git(root, "log", "-1", "--format=%ct")
    minutes = 0
    if last and last.strip().isdigit():
        minutes = int((time.time() - int(last.strip())) / 60)

    piled = len(changed) >= PILE_THRESHOLD
    stale = minutes >= AGE_MINUTES
    if not (piled or stale) or recently_nudged(root):
        return 0

    reasons = []
    if piled:
        reasons.append(f"{len(changed)} files are uncommitted")
    if stale:
        reasons.append(f"the last commit is {minutes} minutes old")

    additional_context(
        "PostToolUse",
        f"Commit cadence: {' and '.join(reasons)} in {root.name}. "
        "Commit the units that are finished now rather than at the end of the "
        "task, staging explicit paths. Where a concurrent session shares this "
        "checkout, some of those files belong to it: check `git status` before "
        "staging, and never `git add -A`.",
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 - an advisory hook must never crash the session
        sys.exit(0)
