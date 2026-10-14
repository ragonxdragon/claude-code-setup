#!/usr/bin/env python3
"""PreToolUse (Bash|PowerShell) guard for the few actions that must never run
without an explicit, per-command opt-in.

Blocked by default:
  - force-push to main or master
  - deleting the main or master branch (never allowed, no opt-in)
  - any push to the `origin` remote or a GitHub URL (policy: land work on a
    local branch and let a human push; see ORIGIN PUSH POLICY below)
  - recursive deletes of a drive root, the home directory, or a .git folder
    (never allowed, no opt-in)
  - a credential file (.credentials.json, SSH keys, AWS config, gh hosts.yml)
    combined with a network tool in one command
  - a network fetch piped straight into a shell (curl | sh, iwr | iex)
  - deleting settings.json, settings.local.json, CLAUDE.md, CONTEXT.md, or
    MEMORY.md

Everything else in a git safety protocol (reset --hard, --no-verify, rm -rf on
an ordinary directory) stays a matter of model judgment plus user
confirmation, because a hook cannot tell whether the user already approved it.

Opt-in prefixes. Each one is a per-command permission signal: the model adds
it only after the user has authorized that exact command in the session. An
accidental command never carries the prefix, so it is still refused.

    ALLOW_FORCE_PUSH_MAIN=1    force-push to main/master
    SKIP_ORIGIN_PUSH=1         push to origin
    ALLOW_CREDENTIAL_ACCESS=1  credential file plus network tool
    ALLOW_REMOTE_PIPE=1        fetch piped into a shell
    ALLOW_CONFIG_DELETE=1      delete a Claude config file

ORIGIN PUSH POLICY. The origin-push block is on by default. To allow session
pushes everywhere, set CLAUDE_GUARD_ORIGIN_PUSH=allow in the environment that
launches Claude Code (or in the "env" block of settings.json). Force-push to
main stays blocked either way.

Exit 2 blocks the tool call; exit 0 allows it. Fails open on malformed input.
"""

from __future__ import annotations

import os
import re
import sys

from hookutil import block, read_payload, shell_command, strip_quoted_strings

# Matches an explicit `origin` remote or a GitHub URL on a `git push`. Unlike a
# git pre-push hook, `--no-verify` cannot skip this check.
ORIGIN_PUSH = re.compile(
    r"git\s+push\b.*(\borigin\b|github\.com|github\.io)",
    re.IGNORECASE,
)

PROTECTED_BRANCHES = {"main", "master"}
SEGMENT_SPLIT = re.compile(r"&&|\|\||[;|\n]")


def is_protected_ref(ref: str) -> bool:
    """True when ref names main or master itself (main, refs/heads/main,
    origin/main, remotes/origin/main). A branch that only contains the word,
    such as fix/main-diag-stall, is not protected."""
    ref = ref.strip().lstrip("+")
    for prefix in ("refs/heads/", "refs/remotes/origin/", "remotes/origin/", "origin/"):
        if ref.lower().startswith(prefix):
            ref = ref[len(prefix) :]
    return ref.lower() in PROTECTED_BRANCHES


def git_args(segment: str) -> list[str] | None:
    """The arguments after `git` in one command segment, skipping env prefixes
    and git's own options (-C dir, -c key=val), or None if it is not a git call."""
    tokens = segment.split()
    while tokens and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[0]):
        tokens = tokens[1:]
    if not tokens or not re.search(r"(^|[\\/])git(\.exe)?$", tokens[0]):
        return None
    args = tokens[1:]
    while args and args[0] in ("-C", "-c", "--git-dir", "--work-tree"):
        args = args[2:]
    return args


def deletes_protected_branch(check: str) -> bool:
    """git branch -d/-D/--delete, or git push --delete / :ref, naming main or master."""
    for segment in SEGMENT_SPLIT.split(check):
        args = git_args(segment)
        if not args:
            continue
        if args[0] == "branch" and any(a in ("-d", "-D", "--delete") for a in args[1:]):
            if any(is_protected_ref(a) for a in args[1:] if not a.startswith("-")):
                return True
        if args[0] == "push":
            rest = [a for a in args[1:] if not a.startswith("-")]
            deleting = any(a in ("-d", "--delete") for a in args[1:])
            for spec in rest[1:]:
                if deleting and is_protected_ref(spec):
                    return True
                if spec.startswith(":") and is_protected_ref(spec[1:]):
                    return True
    return False


def force_pushes_protected_branch(check: str) -> bool:
    """git push with -f, --force, --force-with-lease, --force-if-includes, or a
    +refspec, whose destination or lease ref is main or master."""
    for segment in SEGMENT_SPLIT.split(check):
        args = git_args(segment)
        if not args or args[0] != "push":
            continue
        opts = [a for a in args[1:] if a.startswith("-")]
        refspecs = [a for a in args[1:] if not a.startswith("-")][1:]
        forced = any(
            o in ("-f", "--force") or o.startswith(("--force-with-lease", "--force-if-includes")) for o in opts
        )
        if not (forced or any(s.startswith("+") for s in refspecs)):
            continue
        for o in opts:
            if o.startswith("--force-with-lease=") and is_protected_ref(o.split("=", 1)[1].split(":", 1)[0]):
                return True
        for spec in refspecs:
            if is_protected_ref(spec.split(":", 1)[1] if ":" in spec else spec):
                return True
    return False


CATASTROPHIC_DELETE_PATTERNS = [
    re.compile(r"rm\s+-rf\s+/\s*($|[;&|])"),
    re.compile(r"rm\s+-rf\s+/\*"),
    re.compile(r"rm\s+-rf\s+~\s*($|[;&|])"),
    re.compile(r"rm\s+-rf\s+[A-Za-z]:[\\/]?\s*($|[;&|])"),
    re.compile(r"rm\s+-rf\s+.*[\\/]\.git\b"),
    re.compile(r"Remove-Item\s+.*-Recurse.*[A-Za-z]:\\?\s*($|[;&|])", re.IGNORECASE),
    re.compile(r"Remove-Item\s+.*-Recurse.*\\\.git\b", re.IGNORECASE),
]

# Credential surfaces whose contents must never flow to a network tool.
# Matched against the RAW command, not the quote-stripped one, because real
# invocations usually quote these paths.
CREDENTIAL_PATH = (
    r"(\.credentials\.json|\.ssh[\\/]|id_rsa|id_ed25519|id_ecdsa|id_dsa"
    r"|\.aws[\\/](credentials|config)|hosts\.yml)"
)
NETWORK_TOOL = r"(curl|wget|nc|ncat|iwr|Invoke-WebRequest|Invoke-RestMethod|scp|ftp)"

CREDENTIAL_EXFIL_PATTERNS = [
    # a credential file read and piped into a network tool
    re.compile(CREDENTIAL_PATH + r"[^|;&]*\|\s*" + NETWORK_TOOL + r"\b", re.IGNORECASE),
    # a network tool given a credential file as an argument (curl -d @file, scp)
    re.compile(NETWORK_TOOL + r"\b[^;&|]*" + CREDENTIAL_PATH, re.IGNORECASE),
]

# A fetch piped straight into an interpreter. Checked on the quote-stripped
# text so a commit message that mentions "curl | bash" does not match.
REMOTE_CODE_PIPE_PATTERNS = [
    re.compile(r"\b(curl|wget)\b[^|;&]*\|\s*(ba|z|da)?sh\b", re.IGNORECASE),
    re.compile(
        r"\b(iwr|Invoke-WebRequest|Invoke-RestMethod|irm)\b[^|;&]*\|\s*(iex|Invoke-Expression)\b",
        re.IGNORECASE,
    ),
]

# Claude configuration files. Matched on the RAW command because these paths
# are usually quoted.
CONFIG_FILE_DELETE = re.compile(
    r"\b(rm|del|erase|Remove-Item|ri)\b[^|;&]*\b(settings\.json|settings\.local\.json"
    r"|CLAUDE\.md|CONTEXT\.md|MEMORY\.md)\b",
    re.IGNORECASE,
)


def origin_push_blocked() -> bool:
    return os.environ.get("CLAUDE_GUARD_ORIGIN_PUSH", "block").strip().lower() != "allow"


def main() -> None:
    cmd = shell_command(read_payload())
    if not cmd:
        sys.exit(0)

    check = strip_quoted_strings(cmd)

    if force_pushes_protected_branch(check) and "ALLOW_FORCE_PUSH_MAIN" not in cmd:
        block(
            "force-push to main/master is blocked by default. If the user has "
            "authorized this exact command, prefix it with ALLOW_FORCE_PUSH_MAIN=1 "
            "(add SKIP_ORIGIN_PUSH=1 for a push to origin)."
        )

    if deletes_protected_branch(check):
        block("deleting the main/master branch is never allowed.")

    if origin_push_blocked() and ORIGIN_PUSH.search(check) and "SKIP_ORIGIN_PUSH" not in cmd:
        block(
            "pushing to origin is disabled for sessions: land work on a local "
            "branch. If the user has authorized this push, prefix the command "
            "with SKIP_ORIGIN_PUSH=1."
        )

    for pattern in CATASTROPHIC_DELETE_PATTERNS:
        if pattern.search(check):
            block("recursive delete targets a drive root, the home directory, or a .git folder.")

    if "ALLOW_CREDENTIAL_ACCESS" not in cmd:
        for pattern in CREDENTIAL_EXFIL_PATTERNS:
            if pattern.search(cmd):
                block(
                    "command pairs a credential file (.credentials.json, SSH keys, "
                    ".aws, gh hosts.yml) with a network tool. If the user has "
                    "authorized this exact command, prefix it with "
                    "ALLOW_CREDENTIAL_ACCESS=1."
                )

    if "ALLOW_REMOTE_PIPE" not in cmd:
        for pattern in REMOTE_CODE_PIPE_PATTERNS:
            if pattern.search(check):
                block(
                    "piping a network fetch straight into a shell is blocked. "
                    "Download to a file, read it, then run it. If the user has "
                    "authorized this exact install, prefix it with ALLOW_REMOTE_PIPE=1."
                )

    if CONFIG_FILE_DELETE.search(cmd) and "ALLOW_CONFIG_DELETE" not in cmd:
        block(
            "deleting settings.json, CLAUDE.md, CONTEXT.md, or MEMORY.md is "
            "blocked. If the user has authorized this removal, prefix the command "
            "with ALLOW_CONFIG_DELETE=1."
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
