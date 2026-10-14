#!/usr/bin/env python3
"""Stop hook, advisory: warn once per session when the transcript file grows
past a size that corresponds to a large share of the context window.

Transcript size is a cheap proxy for context use. Rough calibration: about
6.3 MB of transcript JSONL per 1M tokens of context, or about 1.26 MB per 200k
tokens. The default threshold (3.8 MB) is about 60 percent of a 1M-token
window. For a 200k-token window, set SESSION_WARN_MB=0.75.

Reads transcript_path from the payload; never scans directories. Writes a
marker file in the temp directory so it warns only once per session.

Environment:

    SESSION_WARN_MB   warning threshold in megabytes (default 3.8)

Always exits 0. Fails open. ASCII-only output.
"""

from __future__ import annotations

import os
import re
import sys
import tempfile
from pathlib import Path

from hookutil import read_payload

DEFAULT_MB = 3.8


def threshold_bytes() -> int:
    try:
        mb = float(os.environ.get("SESSION_WARN_MB", DEFAULT_MB))
    except ValueError:
        mb = DEFAULT_MB
    return int(mb * 1024 * 1024)


def main() -> None:
    data = read_payload()
    transcript_path = data.get("transcript_path")
    if not transcript_path:
        return
    transcript = Path(transcript_path)
    if not transcript.is_file():
        return
    session_id = str(data.get("session_id") or transcript.stem)
    safe_id = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id)
    marker = Path(tempfile.gettempdir()) / f"claude-lenwarn-{safe_id}"
    if marker.exists():
        return  # already warned in this session
    size = transcript.stat().st_size
    if size >= threshold_bytes():
        marker.touch()
        print(
            f"NOTE: the session transcript is {size / (1024 * 1024):.1f} MB, a large "
            "share of the context window. Finish the current task and start a fresh "
            "session; the files hold the state.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - an advisory hook must never crash the session
        pass
    sys.exit(0)
