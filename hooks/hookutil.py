"""Shared helpers for the hook scripts in this directory.

Not a hook. Python puts a script's own directory first on sys.path, so every
hook here can `import hookutil` as long as the hooks/ directory is copied as a
whole.
"""

from __future__ import annotations

import json
import re
import sys

SHELL_TOOLS = ("Bash", "PowerShell", "mcp__bash__bash")


def read_payload() -> dict:
    """Parse the hook payload from stdin as UTF-8.

    Reads raw bytes so the result does not depend on the console code page.
    On Windows, stdin defaults to cp1252, which turns the UTF-8 bytes of
    Cyrillic or Hebrew text into phantom dashes and quotes. Returns an empty
    dict on any parse failure so callers fail open.
    """
    try:
        raw = sys.stdin.buffer.read()
        data = json.loads(raw.decode("utf-8", errors="replace") or "{}")
    except Exception:  # noqa: BLE001 - a hook must never crash the session
        return {}
    return data if isinstance(data, dict) else {}


def utf8_stdio() -> None:
    """Make stdout and stderr write UTF-8 so echoed text survives on Windows."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            pass


def shell_command(data: dict) -> str:
    """The command string of a shell tool call, or "" for any other tool."""
    if data.get("tool_name", "") not in SHELL_TOOLS:
        return ""
    tool_input = data.get("tool_input") or {}
    return tool_input.get("command", "") or ""


def strip_quoted_strings(cmd: str) -> str:
    """Blank out quoted contents but keep the quotes.

    Text inside a commit message or an echoed argument, such as
    `git commit -m "revert git push --force main"`, then cannot match a
    pattern meant for a real invocation, and a quoted path still counts as one
    token.
    """
    cmd = re.sub(r"'[^']*'", "''", cmd)
    cmd = re.sub(r'"(?:[^"\\]|\\.)*"', '""', cmd)
    return cmd


def block(reason: str) -> None:
    """Refuse the tool call. Claude Code reads stderr as the reason on exit 2."""
    print(f"BLOCKED: {reason}", file=sys.stderr)
    sys.exit(2)


def additional_context(event: str, text: str) -> None:
    """Print a hookSpecificOutput block that adds text to the model's context."""
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))
