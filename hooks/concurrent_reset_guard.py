#!/usr/bin/env python3
"""PreToolUse (Bash|PowerShell) guard: block `git reset` invocations that move
a branch pointer to a ref (HEAD~N, HEAD^, a SHA, a branch or tag name) rather
than only unstaging paths.

Why: when several sessions share a repository, `git reset --soft HEAD~1` is
computed against whatever HEAD is at the moment it runs. Another session can
land a commit between your last `git log` and the reset, and the reset then
un-commits THEIR work instead of yours, with no error.

Not blocked (these never move HEAD):
  - `git reset` and `git reset HEAD`        (unstage everything)
  - `git reset -- path/to/file`             (pathspec form)
  - `git reset HEAD -- path/to/file`        (pathspec form)
  - any command prefixed with AI_ALLOW_HEAD_RESET=1 (per-command opt-in)

Blocked by default:
  - `git reset --soft HEAD~1`, `git reset --hard <sha>`, `git reset origin/main`,
    and any other `git reset` whose target is a commit-ish.

To restructure history safely in a shared repository, do not reset relative to
HEAD. Build the new commits with `git commit-tree` (which never touches the
working tree or index) and move the branch with a compare-and-swap:
`git update-ref refs/heads/<branch> <new-sha> <old-sha>`. It fails with nothing
changed if another session moved the ref first.

Exit 2 blocks the tool call; exit 0 allows it. Fails open on malformed input.
"""

from __future__ import annotations

import re
import sys

from hookutil import read_payload, shell_command, strip_quoted_strings

# `git reset` flags are all standalone; none consumes the next token.
RESET_FLAGS = {
    "--soft",
    "--mixed",
    "--hard",
    "--merge",
    "--keep",
    "--quiet",
    "-q",
    "-p",
    "--patch",
    "-N",
    "--intent-to-add",
}


def reset_moves_head(segment: str) -> bool:
    """segment is the quote-stripped text after `git reset`.

    True when the invocation targets a ref (unsafe under concurrency), False
    for the pathspec-only and no-target forms.
    """
    tokens = segment.split()
    if "--" in tokens:
        return False  # pathspec form never moves HEAD

    target = None
    for tok in tokens:
        if tok in RESET_FLAGS or tok.startswith("-"):
            continue
        target = tok  # the first non-flag token is the reset target
        break

    return target not in (None, "HEAD")


def main() -> None:
    cmd = shell_command(read_payload())
    if not cmd or "AI_ALLOW_HEAD_RESET" in cmd:
        sys.exit(0)

    stripped = strip_quoted_strings(cmd)
    for match in re.finditer(r"\bgit\s+reset\b([^|;&]*)", stripped):
        if reset_moves_head(match.group(1)):
            print(
                "BLOCKED: `git reset` to a ref (HEAD~N, a SHA, a branch) is refused "
                "by default. In a shared repository a reset computed against a "
                "stale HEAD un-commits whatever another session just landed. To "
                "restructure history, build commits with `git commit-tree` and "
                "move the branch with `git update-ref refs/heads/<branch> <new> "
                "<old>`, which fails cleanly if the ref moved. `git reset -- <path>` "
                "(unstage only) is never blocked. If the user has authorized this "
                "exact reset, prefix the command with AI_ALLOW_HEAD_RESET=1.",
                file=sys.stderr,
            )
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
