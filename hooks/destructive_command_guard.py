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

FORCE_PUSH = re.compile(
    r"git\s+push\b.*(--force(-with-lease)?\b|(?<!\w)-f(?!\w))",
    re.IGNORECASE,
)
MAIN_BRANCH_REF = re.compile(r"\b(origin[/\s]+)?(main|master)\b", re.IGNORECASE)

# Matches an explicit `origin` remote or a GitHub URL on a `git push`. Unlike a
# git pre-push hook, `--no-verify` cannot skip this check.
ORIGIN_PUSH = re.compile(
    r"git\s+push\b.*(\borigin\b|github\.com|github\.io)",
    re.IGNORECASE,
)

BRANCH_DELETE_MAIN = re.compile(
    r"git\s+(branch\s+(-D|-d\s+-f|--delete\s+--force)|push\s+\S+\s+--delete)\s+.*\b(main|master)\b",
    re.IGNORECASE,
)

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

    if FORCE_PUSH.search(check) and MAIN_BRANCH_REF.search(check) and "ALLOW_FORCE_PUSH_MAIN" not in cmd:
        block(
            "force-push to main/master is blocked by default. If the user has "
            "authorized this exact command, prefix it with ALLOW_FORCE_PUSH_MAIN=1 "
            "(add SKIP_ORIGIN_PUSH=1 for a push to origin)."
        )

    if BRANCH_DELETE_MAIN.search(check):
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
