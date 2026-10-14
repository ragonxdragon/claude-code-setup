#!/usr/bin/env python3
"""Verify that the generated routing files match knowledge/ frontmatter.

Fails (exit 1) when:
  - a concept file under knowledge/<bundle>/ (not conventions/, not index.md)
    has no `domains` field, so it is invisible to routing;
  - the generated block in CONTEXT.md differs from what build_routing.py would
    write now;
  - a bundle index.md differs from what build_routing.py would write now.

Usage:
    python scripts/check_routing.py

If routing seems to miss a skill, the fix is in the concept file's `domains`
field; then run build_routing.py. Never hand-edit the generated block.
"""

from __future__ import annotations

import sys

import build_routing as br
from claude_home import CLAUDE_DIR, CONTEXT_FILE, KNOWLEDGE_DIR, as_list, parse_frontmatter, utf8_stdout


def check_domains() -> list[str]:
    errors: list[str] = []
    for subdir in sorted(KNOWLEDGE_DIR.iterdir()):
        if not subdir.is_dir() or subdir.name in br.SKIP_DIRS:
            continue
        for f in sorted(subdir.glob("*.md")):
            if f.name in br.SKIP_NAMES:
                continue
            if not as_list(parse_frontmatter(f).get("domains")):
                errors.append(f"MISSING domains field: {f.relative_to(CLAUDE_DIR).as_posix()}")
    return errors


def check_context(entries: list[dict]) -> list[str]:
    if not CONTEXT_FILE.exists():
        return ["STALE: CONTEXT.md does not exist; run build_routing.py"]
    current = CONTEXT_FILE.read_text(encoding="utf-8")
    if br.MARKER_START not in current or br.MARKER_END not in current:
        return ["STALE: CONTEXT.md has no generated block; run build_routing.py"]
    start = current.index(br.MARKER_START)
    end = current.index(br.MARKER_END) + len(br.MARKER_END)
    if current[start:end].strip() != br.build_routing_block(entries).strip():
        return ["STALE: CONTEXT.md generated block is out of sync; run build_routing.py"]
    return []


def check_indexes(entries: list[dict]) -> list[str]:
    errors: list[str] = []
    for bundle in br.BUNDLES:
        index_path = KNOWLEDGE_DIR / bundle / "index.md"
        if not index_path.exists():
            continue
        existing = index_path.read_text(encoding="utf-8")
        expected = br.bundle_index(bundle, [e for e in entries if e["bundle"] == bundle], existing)
        if expected is not None and expected != existing:
            errors.append(f"STALE: knowledge/{bundle}/index.md is out of sync; run build_routing.py")
    return errors


def main() -> None:
    utf8_stdout()
    entries = br.collect_entries()
    errors = check_domains() + check_context(entries) + check_indexes(entries)
    if errors:
        print("check_routing.py FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        sys.exit(1)
    print("check_routing.py PASSED: routing table is current and every concept file has domains")


if __name__ == "__main__":
    main()
