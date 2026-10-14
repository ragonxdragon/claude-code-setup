#!/usr/bin/env python3
"""Audit installed skills against the knowledge index.

Checks:
  1. Orphaned skills: a skill installed under skills/ or inside a plugin
     under plugins/ that no knowledge/ concept file mentions. A skill counts
     as indexed when its name appears in backticks (`name` or `/name`) in any
     knowledge/ file. A plugin skill also counts when its plugin or
     marketplace name does, since packs are usually documented as a whole.
  2. Routing staleness: CONTEXT.md out of sync with knowledge/ frontmatter.

Skills that are deliberately left out of the index (meta utilities, aliases)
go one per line in knowledge/drift-skip.txt; lines starting with # are
comments.

Usage:
    python scripts/drift_check.py          # report only
    python scripts/drift_check.py --fix    # also rebuild routing when stale
"""

from __future__ import annotations

import argparse
import re
import sys

import build_routing
import check_routing
from claude_home import CLAUDE_DIR, KNOWLEDGE_DIR, SKILLS_DIR, utf8_stdout

SKIP_FILE = KNOWLEDGE_DIR / "drift-skip.txt"
INDEXED_NAME_RE = re.compile(r"`/?([a-z][a-z0-9]*(?:-[a-z0-9]+)*)`")


def skip_names() -> set[str]:
    if not SKIP_FILE.exists():
        return set()
    names = set()
    for line in SKIP_FILE.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            names.add(line)
    return names


def installed_global() -> set[str]:
    """Skill directories under skills/ that contain a SKILL.md."""
    if not SKILLS_DIR.exists():
        return set()
    return {d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()}


def installed_plugin_skills() -> dict[str, set[str]]:
    """Plugin skills mapped to the names that can cover them in the index.

    Scans plugins/marketplaces/<mkt>/**/skills/<skill>/SKILL.md and
    plugins/cache/<mkt>/<plugin>/<version>/skills/<skill>/SKILL.md.
    """
    skills: dict[str, set[str]] = {}
    plugins_dir = CLAUDE_DIR / "plugins"
    for root_name in ("marketplaces", "cache"):
        root = plugins_dir / root_name
        if not root.is_dir():
            continue
        for mkt in root.iterdir():
            if not mkt.is_dir() or mkt.name.startswith("."):
                continue
            for skill_md in mkt.glob("**/skills/*/SKILL.md"):
                rel = skill_md.relative_to(mkt)
                if ".git" in rel.parts or "node_modules" in rel.parts:
                    continue
                skill = skill_md.parent.name
                plugin = rel.parts[0] if len(rel.parts) > 3 else mkt.name
                skills.setdefault(skill, set()).update({skill, plugin, mkt.name})
    return skills


def indexed_names() -> set[str]:
    """Names that appear in backticks anywhere under knowledge/."""
    names: set[str] = set()
    for f in KNOWLEDGE_DIR.rglob("*.md"):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        names.update(m.group(1) for m in INDEXED_NAME_RE.finditer(text) if len(m.group(1)) >= 2)
    return names


def routing_current() -> bool:
    entries = build_routing.collect_entries()
    errors = check_routing.check_domains() + check_routing.check_context(entries) + check_routing.check_indexes(entries)
    return not errors


def main() -> None:
    utf8_stdout()
    parser = argparse.ArgumentParser(description="Audit installed skills against the knowledge index.")
    parser.add_argument("--fix", action="store_true", help="rebuild routing when stale")
    args = parser.parse_args()

    print("=== Skill Drift Check ===\n")
    skip = skip_names()
    global_skills = installed_global()
    plugin_skills = installed_plugin_skills()
    indexed = indexed_names()

    orphaned: dict[str, str] = {}
    for skill in global_skills:
        if skill not in indexed and skill not in skip:
            orphaned[skill] = "global"
    for skill, covers in plugin_skills.items():
        if skill in global_skills or skill in skip:
            continue
        if not covers & indexed:
            orphaned[skill] = "plugin"

    if orphaned:
        print(f"ORPHANED ({len(orphaned)}): installed but not referenced in any concept file:")
        for skill in sorted(orphaned):
            print(f"  [{orphaned[skill]}]  {skill}")
        print()
    else:
        total = len(global_skills | set(plugin_skills))
        print(f"OK  All {total} installed skills are referenced in knowledge/\n")

    routing_ok = routing_current()
    if not routing_ok:
        print("STALE: routing files are out of sync with knowledge/ frontmatter")
        if args.fix:
            print("  rebuilding...")
            build_routing.main()
            routing_ok = routing_current()
            print("  done\n" if routing_ok else "  rebuild did not fix it; run check_routing.py\n")
        else:
            print("  run with --fix, or: python scripts/build_routing.py\n")
    else:
        print("OK  Routing table is current\n")

    print(
        f"Summary: {len(global_skills)} global skills | {len(plugin_skills)} plugin skills | "
        f"{'routing OK' if routing_ok else 'routing STALE'}"
    )
    if orphaned or not routing_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
