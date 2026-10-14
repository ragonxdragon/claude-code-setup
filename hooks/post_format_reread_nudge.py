#!/usr/bin/env python3
"""PostToolUse (Edit|Write) advisory: detect when something rewrote the file
after the model's edit landed (a formatter hook, a changelog sync, an editor
on save) and tell the model to re-Read before its next Edit.

Without the nudge the model keeps editing from its stale in-memory copy, and
the next Edit fails on a mismatched old_string or silently reverts the
formatter's work.

Detection: after an Edit the file on disk must still contain new_string; after
a Write it must equal content. The comparison normalizes newlines, so a CRLF
conversion alone never triggers the nudge. Files over 2 MB are skipped.

Always exits 0. Fails open. ASCII-only output.
"""

from __future__ import annotations

import sys
from pathlib import Path

from hookutil import additional_context, read_payload

MAX_BYTES = 2 * 1024 * 1024


def normalize(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def main() -> None:
    data = read_payload()
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path", "")
    if not file_path or tool_name not in ("Edit", "Write"):
        return

    path = Path(file_path)
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        return
    on_disk = normalize(path.read_text(encoding="utf-8", errors="replace"))

    if tool_name == "Edit":
        expected = tool_input.get("new_string", "")
        rewritten = bool(expected) and normalize(expected) not in on_disk
    else:
        expected = tool_input.get("content", "")
        rewritten = bool(expected) and normalize(expected) != on_disk

    if rewritten:
        additional_context(
            "PostToolUse",
            f"NOTE: something rewrote {file_path} after your edit landed (a "
            "formatter or sync hook). The file on disk no longer matches what you "
            "wrote. Re-Read it before making any further Edit to it.",
        )


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - an advisory hook must never crash the session
        pass
    sys.exit(0)
