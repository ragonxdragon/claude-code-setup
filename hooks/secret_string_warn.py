#!/usr/bin/env python3
"""UserPromptSubmit hook: warn, never block, when the submitted prompt contains
a credential-shaped string.

A pasted credential leaks into the transcript and the model's context, and
from there can reach files, commands, and commits. The warning goes into the
model's context so it flags the paste, avoids echoing the value anywhere
durable, and suggests rotating it.

Always exits 0. Fails open. ASCII-only output.
"""

from __future__ import annotations

import re
import sys

from hookutil import read_payload

KEY_PATTERNS = [
    ("Anthropic API key", re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}")),
    ("OpenAI-style secret key", re.compile(r"sk-(proj-)?[A-Za-z0-9]{20,}")),
    ("Google API key", re.compile(r"AIza[0-9A-Za-z_-]{30,}")),
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}")),
    ("GitHub fine-grained token", re.compile(r"github_pat_[A-Za-z0-9_]{30,}")),
    ("Slack token", re.compile(r"xox[abprs]-[A-Za-z0-9-]{10,}")),
    ("AWS access key id", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY")),
]


def main() -> None:
    prompt = read_payload().get("prompt", "") or ""
    if not prompt:
        return
    hits = [label for label, pattern in KEY_PATTERNS if pattern.search(prompt)]
    if hits:
        print(
            "WARNING: the prompt appears to contain credential-shaped strings ("
            + ", ".join(hits)
            + "). Do not echo the value into files, commits, or command lines; "
            "treat it as leaked and suggest the user rotate it."
        )


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - an advisory hook must never crash the session
        pass
    sys.exit(0)
