#!/usr/bin/env python3
"""PostToolUse (Edit|Write) hook: rebuild the CONTEXT.md routing table when a
knowledge/*.md concept file changes, so the generated table never drifts from
the frontmatter it is built from.

The config root is CLAUDE_HOME when set, else the parent of this hooks/
directory (for example ~/.claude). Only .md files under <root>/knowledge/
trigger a rebuild. Silent on success; a failed rebuild prints a warning to
stderr. Never exits non-zero.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from hookutil import read_payload


def config_root() -> Path:
    env = os.environ.get("CLAUDE_HOME")
    return Path(env).expanduser().resolve() if env else Path(__file__).resolve().parent.parent


def main() -> None:
    file_path = (read_payload().get("tool_input") or {}).get("file_path", "")
    if not file_path.endswith(".md"):
        return
    root = config_root()
    knowledge = (root / "knowledge").as_posix().lower() + "/"
    if not Path(file_path).resolve().as_posix().lower().startswith(knowledge):
        return

    result = subprocess.run(
        [sys.executable, str(root / "scripts" / "build_routing.py")],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        print(f"[routing_rebuild] WARN: build_routing.py failed:\n{result.stderr}", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - an advisory hook must never crash the session
        pass
    sys.exit(0)
