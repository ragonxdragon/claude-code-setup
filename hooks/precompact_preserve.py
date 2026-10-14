#!/usr/bin/env python3
"""PreCompact hook: add preservation instructions so compaction keeps the
working state that matters (open todos, in-progress plan checkboxes, user
corrections, touched paths, test results) instead of summarizing it away.

Repeats the "Compact instructions" section of the global CLAUDE.md, so the
rule also holds in sessions where that file is not loaded.

Always exits 0. Fails open. ASCII-only output.
"""

from __future__ import annotations

import sys

INSTRUCTIONS = (
    "COMPACTION INSTRUCTIONS: preserve verbatim (1) every open or incomplete "
    "todo item and its status, (2) in-progress plan checkboxes and which boxes "
    "are still open, (3) every explicit user correction or decision made this "
    "session, (4) every file path touched (created, edited, deleted), and (5) "
    "the exact test and build commands run and their pass/fail results. Drop "
    "tool-call noise and superseded intermediate reasoning."
)


def main() -> None:
    try:
        sys.stdin.read()  # consume the payload; its content is not needed
    except Exception:  # noqa: BLE001
        pass
    print(INSTRUCTIONS)


if __name__ == "__main__":
    main()
    sys.exit(0)
