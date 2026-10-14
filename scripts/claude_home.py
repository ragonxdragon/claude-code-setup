"""Shared paths and frontmatter parsing for the scripts in this directory.

Not a command. The config root is CLAUDE_HOME when that variable is set, else
the parent of this scripts/ directory. That makes every script work the same
way from a clone of this repository, from ~/.claude after install, or against
any other directory you point CLAUDE_HOME at.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path


def _root() -> Path:
    env = os.environ.get("CLAUDE_HOME")
    if env:
        return Path(env).expanduser().resolve()
    return Path(__file__).resolve().parent.parent


CLAUDE_DIR = _root()
KNOWLEDGE_DIR = CLAUDE_DIR / "knowledge"
SKILLS_DIR = CLAUDE_DIR / "skills"
CONTEXT_FILE = CLAUDE_DIR / "CONTEXT.md"

LIST_FIELDS = {"domains", "tags", "related"}

_FRONTMATTER_RE = re.compile(r"^\ufeff?---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(\r?\n|$)", re.DOTALL)
_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):[ \t]*(.*)$")
_ITEM_RE = re.compile(r"^\s+-\s*(.*)$")


def utf8_stdout() -> None:
    """Write UTF-8 to stdout and stderr even on a cp1252 Windows console."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            pass


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def _inline_list(value: str) -> list[str]:
    inner = value.strip()[1:-1]
    return [_unquote(item) for item in inner.split(",") if item.strip()]


def frontmatter_text(text: str) -> str | None:
    """The raw frontmatter block of a markdown document, or None."""
    match = _FRONTMATTER_RE.match(text)
    return match.group(1) if match else None


def parse_frontmatter_text(text: str) -> dict[str, str | list[str]]:
    """Parse top-level frontmatter keys.

    Handles inline lists (`domains: [a, b]`), block lists (`domains:` followed
    by `  - a` lines), and folded or literal scalars (`description: >`).
    Indented sub-keys, such as those under `metadata:`, are skipped. Fields in
    LIST_FIELDS always come back as lists; everything else as a string.
    """
    block = frontmatter_text(text)
    if block is None:
        return {}
    lines = block.splitlines()
    fields: dict[str, str | list[str]] = {}
    i = 0
    while i < len(lines):
        match = _KEY_RE.match(lines[i])
        if not match:
            i += 1
            continue
        key, value = match.group(1).lower(), match.group(2).strip()
        i += 1
        if value in (">", "|", ">-", "|-", ">+", "|+"):
            parts = []
            while i < len(lines) and (not lines[i].strip() or lines[i][:1] in (" ", "\t")):
                if lines[i].strip():
                    parts.append(lines[i].strip())
                i += 1
            fields[key] = " ".join(parts)
        elif value == "":
            items = []
            while i < len(lines):
                item = _ITEM_RE.match(lines[i])
                if item:
                    items.append(_unquote(item.group(1)))
                elif lines[i].strip() and lines[i][:1] not in (" ", "\t"):
                    break
                i += 1
            fields[key] = items if items else ""
        elif value.startswith("[") and value.endswith("]"):
            fields[key] = _inline_list(value)
        else:
            fields[key] = _unquote(value)

    for key in LIST_FIELDS & fields.keys():
        value = fields[key]
        if isinstance(value, str):
            fields[key] = [part.strip() for part in value.split(",") if part.strip()]
    return fields


def parse_frontmatter(path: Path) -> dict[str, str | list[str]]:
    try:
        return parse_frontmatter_text(path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return {}


def as_list(value: str | list[str] | None) -> list[str]:
    if value is None or value == "":
        return []
    return value if isinstance(value, list) else [value]


def as_str(value: str | list[str] | None) -> str:
    if value is None:
        return ""
    return ", ".join(value) if isinstance(value, list) else value
