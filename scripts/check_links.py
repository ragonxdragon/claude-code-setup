#!/usr/bin/env python3
"""Find broken relative markdown links and leftover [[name]] placeholders.

Scans the root markdown files, _config/, knowledge/, skills/, agents/, and
commands/. Links inside fenced code blocks and inline code are ignored, as are
absolute URLs, mail links, pure #anchors, and ~/ paths (which point into the
installed config, not this tree). A [[name]] placeholder is a warning, not a
failure, so planned links stay visible without blocking CI.

Usage:
    python scripts/check_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from claude_home import CLAUDE_DIR, utf8_stdout

SCAN_DIRS = ("_config", "knowledge", "skills", "agents", "commands")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "#", "~/")


def strip_code(text: str) -> str:
    """Remove fenced code blocks and inline code so example links are skipped."""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    return re.sub(r"`[^`\n]+`", "", text)


def markdown_files() -> list[Path]:
    files = sorted(CLAUDE_DIR.glob("*.md"))
    for name in SCAN_DIRS:
        directory = CLAUDE_DIR / name
        if directory.is_dir():
            files += sorted(directory.rglob("*.md"))
    return files


def check_file(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    text = strip_code(path.read_text(encoding="utf-8", errors="replace"))
    rel = path.relative_to(CLAUDE_DIR).as_posix()

    for match in LINK_RE.finditer(text):
        href = match.group(2)
        if href.startswith(SKIP_PREFIXES) or href.startswith("<"):
            continue
        target_part = href.split("#", 1)[0]
        if not target_part:
            continue
        if not (path.parent / target_part).exists():
            errors.append(f"  BROKEN [{match.group(1)}]({href}) in {rel}")

    for match in WIKILINK_RE.finditer(text):
        warnings.append(f"  WARN [[{match.group(1).strip()}]] placeholder in {rel}")

    return errors, warnings


def main() -> None:
    utf8_stdout()
    files = markdown_files()
    all_errors: list[str] = []
    all_warnings: list[str] = []
    for f in files:
        errors, warnings = check_file(f)
        all_errors += errors
        all_warnings += warnings

    if all_warnings:
        print(f"Link check: {len(all_warnings)} [[name]] placeholder(s) to convert:")
        print("\n".join(all_warnings))
    if all_errors:
        print(f"Link check: {len(all_errors)} broken link(s)")
        print("\n".join(all_errors))
        sys.exit(1)
    print(f"Link check: all links valid across {len(files)} files")


if __name__ == "__main__":
    main()
