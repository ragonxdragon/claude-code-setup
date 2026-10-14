#!/usr/bin/env python3
"""Report knowledge/ files whose last change is older than a threshold.

Age comes from the file's last git commit when the config root is a git
repository, else from the file's modification time. Exit 1 when any file is
stale, so a scheduled maintenance run surfaces it.

Usage:
    python scripts/check_stale.py [--days 180]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from claude_home import CLAUDE_DIR, KNOWLEDGE_DIR, utf8_stdout


def last_change(path: Path) -> float:
    """Epoch seconds of the file's last commit, falling back to mtime."""
    try:
        out = subprocess.run(
            ["git", "-C", str(CLAUDE_DIR), "log", "-1", "--format=%ct", "--", str(path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if out.returncode == 0 and out.stdout.strip().isdigit():
            return float(out.stdout.strip())
    except (OSError, subprocess.TimeoutExpired):
        pass
    return path.stat().st_mtime


def main() -> None:
    utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=180, help="age threshold in days")
    args = parser.parse_args()

    now = time.time()
    files = sorted(KNOWLEDGE_DIR.rglob("*.md"))
    stale = []
    for f in files:
        age_days = int((now - last_change(f)) / 86400)
        if age_days > args.days:
            stale.append((f.relative_to(KNOWLEDGE_DIR).as_posix(), age_days))

    if stale:
        print(f"Stale check: {len(stale)} file(s) older than {args.days} days")
        for rel, age in stale:
            print(f"  {rel}  ({age}d)")
        sys.exit(1)
    print(f"Stale check: all {len(files)} files fresh (under {args.days} days)")


if __name__ == "__main__":
    main()
