#!/usr/bin/env python3
"""PostToolUse (Bash) advisory: after one of this setup's validator scripts
runs green, note that the session is at a clean boundary and a good place to
wrap up or start a fresh session.

Prints to stderr, which Claude Code shows in the transcript view. Always exits
0. Never blocks.
"""

from __future__ import annotations

import sys

from hookutil import read_payload

CHECKER_SCRIPTS = (
    "validate_okf.py",
    "check_links.py",
    "check_stale.py",
    "check_routing.py",
    "build_routing.py",
    "frontmatter_audit.py",
    "drift_check.py",
    "hooks_selftest.py",
)

SUCCESS_MARKERS = ("Done.", "OK", "PASSED", "No issues", "0 errors", "0 warnings", "all links valid")
FAIL_MARKERS = ("ERROR", "FAIL", "error:", "Warning:", "STALE", "stale", "broken", "ORPHANED")


def is_checker_run(data: dict) -> bool:
    if data.get("tool_name", "") not in ("Bash", "PowerShell", "mcp__bash__bash"):
        return False
    cmd = (data.get("tool_input") or {}).get("command", "") or ""
    return any(script in cmd for script in CHECKER_SCRIPTS)


def looks_green(output: str) -> bool:
    return any(m in output for m in SUCCESS_MARKERS) and not any(m in output for m in FAIL_MARKERS)


def main() -> None:
    data = read_payload()
    if not is_checker_run(data):
        return

    response = data.get("tool_response", {})
    if isinstance(response, dict):
        output = (response.get("stdout", "") or "") + (response.get("stderr", "") or "")
        # Some tool responses carry no exit code; the markers decide then.
        exit_code = response.get("exit_code", response.get("exitCode"))
    else:
        output = str(response)
        exit_code = None

    if exit_code in (0, None) and looks_green(output):
        print("Checks green: clean boundary. Good place to wrap this session.", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - an advisory hook must never crash the session
        pass
    sys.exit(0)
