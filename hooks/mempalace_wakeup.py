#!/usr/bin/env python3
"""OPTIONAL SessionStart hook: inject recall context from MemPalace, a
third-party long-term memory tool, at the start of each session.

Not wired in settings.example.json. Wire it only if you use MemPalace; see
the README. Without MemPalace installed it does nothing: when the `mempalace`
executable is missing, the palace is empty, or the call fails or times out,
the hook prints nothing and exits 0, so session start is never blocked.

Lookup order for the executable: MEMPALACE_BIN, then PATH, then
~/.local/bin (the default install location for `uv tool install`).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys


def find_mempalace() -> str | None:
    explicit = os.environ.get("MEMPALACE_BIN")
    if explicit:
        return explicit if os.path.isfile(explicit) else None
    found = shutil.which("mempalace")
    if found:
        return found
    # PATH can be stale in some spawn contexts; fall back to the uv tool bin.
    local_bin = os.path.join(os.path.expanduser("~"), ".local", "bin")
    for name in ("mempalace.exe", "mempalace"):
        candidate = os.path.join(local_bin, name)
        if os.path.isfile(candidate):
            return candidate
    return None


def main() -> None:
    exe = find_mempalace()
    if not exe:
        return
    try:
        out = subprocess.run(
            [exe, "wake-up"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
        ).stdout.strip()
    except Exception:  # noqa: BLE001
        return
    if not out:
        return
    # Drop the decorative "Wake-up text (~N tokens):" header and its rule line.
    lines = out.splitlines()
    if lines and lines[0].lower().startswith("wake-up text"):
        lines = lines[1:]
    while lines and set(lines[0].strip()) <= {"="}:
        lines = lines[1:]
    context = "\n".join(lines).strip()
    if not context:
        return
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": "# MemPalace recall (auto-loaded)\n" + context,
                }
            }
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - never break session start
        pass
    sys.exit(0)
