#!/usr/bin/env python3
"""PreToolUse (Bash|PowerShell) guard: block `git commit` invocations that
carry no explicit pathspec.

Why: when two Claude sessions work in one checkout they share one git index.
A bare `git commit` records everything staged, including files the other
session staged for its own commit. Staging and committing explicit paths keeps
each session's commits to its own files.

Allowed:
  - `git commit -m "msg" path/to/file`          (pathspec present)
  - `git commit -F msg.txt -- src/lib.rs`       (pathspec after --)
  - a bare `git commit` while a merge is being concluded (MERGE_HEAD exists):
    git refuses pathspecs there, and the commit only records the merged index
  - any command prefixed with AI_ALLOW_BARE_COMMIT=1 (per-command opt-in after
    the user authorizes it)
Blocked:
  - `git commit -m "msg"` with no path arguments, including -a and --amend

Exit 2 blocks the tool call; exit 0 allows it. Fails open on malformed input.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

from hookutil import read_payload, shell_command, strip_quoted_strings

# Long options to `git commit` that consume the NEXT token as their value
# (the `--opt=value` form is a single token and needs no entry).
VALUE_LONG_OPTS = {
    "--message",
    "--file",
    "--template",
    "--reuse-message",
    "--reedit-message",
    "--fixup",
    "--squash",
    "--author",
    "--date",
    "--cleanup",
    "--pathspec-from-file",
    "--trailer",
}
# Short options that take a value. In a cluster such as `-am`, the value is
# the next token when the option letter comes last.
VALUE_SHORT_OPTS = set("mFtCc")


def consumes_next(tok: str) -> bool:
    if tok.startswith("--"):
        return tok in VALUE_LONG_OPTS
    letters = tok[1:]
    for i, letter in enumerate(letters):
        if letter in VALUE_SHORT_OPTS:
            # `-mmsg` carries its value inline; `-am` takes the next token.
            return i == len(letters) - 1
    return False


def commit_has_pathspec(segment: str) -> bool:
    """segment is the quote-stripped text after `git commit`."""
    tokens = segment.split()
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == "--":
            return i + 1 < len(tokens)  # anything after -- is a pathspec
        if tok.startswith("-"):
            i += 2 if consumes_next(tok) else 1
            continue
        return True  # a bare non-option token is a pathspec
    return False


def concluding_merge(cwd: str) -> bool:
    """True when the repository at cwd has a MERGE_HEAD.

    Uses `git rev-parse --git-path`, which also resolves inside worktrees.
    Any failure returns False, so the caller falls back to blocking.
    """
    try:
        out = subprocess.run(
            ["git", "-C", cwd or ".", "rev-parse", "--git-path", "MERGE_HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode != 0:
            return False
        path = out.stdout.strip()
        if not os.path.isabs(path):  # --git-path answers relative to cwd
            path = os.path.join(cwd or ".", path)
        return os.path.isfile(path)
    except Exception:  # noqa: BLE001
        return False


def main() -> None:
    data = read_payload()
    cmd = shell_command(data)
    if not cmd or "AI_ALLOW_BARE_COMMIT" in cmd:
        sys.exit(0)

    stripped = strip_quoted_strings(cmd)
    # Check each `git commit` in a compound command line.
    for match in re.finditer(r"\bgit\s+commit\b([^|;&]*)", stripped):
        if commit_has_pathspec(match.group(1)):
            continue
        if concluding_merge(data.get("cwd", "")):
            continue
        print(
            "BLOCKED: bare `git commit` with no explicit pathspec. A concurrent "
            "session may share this index, so commit explicit paths only, e.g. "
            '`git commit -m "msg" -- path/one path/two`. If the user has '
            "authorized a bare commit, prefix the command with AI_ALLOW_BARE_COMMIT=1.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
