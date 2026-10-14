#!/usr/bin/env python3
"""Verify that every knowledge/**/*.md file has OKF frontmatter with a valid
`type` field. See knowledge/conventions/okf-spec.md for the schema.

Usage:
    python scripts/validate_okf.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from claude_home import KNOWLEDGE_DIR, as_str, frontmatter_text, parse_frontmatter_text, utf8_stdout

VALID_TYPES = {"Skill", "Agent", "Marketplace", "Convention"}


def check_file(path: Path) -> str | None:
    """An error string, or None when the file is valid."""
    rel = path.relative_to(KNOWLEDGE_DIR).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    if frontmatter_text(text) is None:
        stripped = text.lstrip("\ufeff")
        if stripped.startswith("---"):
            return f"UNCLOSED frontmatter: {rel}"
        return f"MISSING frontmatter: {rel}"
    value = as_str(parse_frontmatter_text(text).get("type"))
    if not value:
        return f"MISSING type field: {rel}"
    if value not in VALID_TYPES:
        return f"INVALID type '{value}': {rel}"
    return None


def main() -> None:
    utf8_stdout()
    files = sorted(KNOWLEDGE_DIR.rglob("*.md"))
    errors = [e for f in files if (e := check_file(f))]
    print(f"OKF validation: {len(files) - len(errors)}/{len(files)} files valid")
    for error in errors:
        print(f"  FAIL: {error}")
    if errors or not files:
        sys.exit(1)


if __name__ == "__main__":
    main()
