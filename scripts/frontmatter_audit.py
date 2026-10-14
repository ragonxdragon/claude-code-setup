#!/usr/bin/env python3
"""Audit skill and knowledge frontmatter.

Skills (skills/*/SKILL.md):
  - missing frontmatter or an empty description (invisible to skill discovery)
  - a `name` that differs from the directory name (breaks /name invocation)
  - no `domains` field
  - a description without a when-clause ("use when" or "when the user"),
    which is what the model matches a request against
Knowledge files (knowledge/<bundle>/*.md, not conventions/):
  - missing or empty `tags`
  - missing `domains` (index.md excepted), or a domain outside the routing
    taxonomy defined in build_routing.DOMAIN_LABELS (its rows would be
    filed under an unlabeled section)

Usage:
    python scripts/frontmatter_audit.py
"""

from __future__ import annotations

import re
import sys

from build_routing import DOMAIN_LABELS
from claude_home import KNOWLEDGE_DIR, SKILLS_DIR, as_list, as_str, parse_frontmatter, utf8_stdout

WHEN_CLAUSE_RE = re.compile(
    r"\buse when\b|\bwhen the user\b|\buse (?:this )?(?:proactively )?whenever\b", re.IGNORECASE
)


def audit_skills() -> tuple[int, dict[str, list[str]]]:
    findings: dict[str, list[str]] = {
        "NO FRONTMATTER": [],
        "EMPTY DESCRIPTION (invisible to skill discovery)": [],
        "NAME != DIRECTORY (breaks /name invocation)": [],
        "MISSING domains field": [],
        "DESCRIPTION MISSING WHEN-CLAUSE ('use when' / 'when the user')": [],
    }
    keys = list(findings)
    count = 0
    if not SKILLS_DIR.is_dir():
        return count, findings
    for d in sorted(SKILLS_DIR.iterdir()):
        md = d / "SKILL.md"
        if not (d.is_dir() and md.exists()):
            continue
        count += 1
        fm = parse_frontmatter(md)
        if not fm:
            findings[keys[0]].append(d.name)
            continue
        desc = as_str(fm.get("description")).strip()
        if not desc:
            findings[keys[1]].append(d.name)
        name = as_str(fm.get("name"))
        if name and name != d.name:
            findings[keys[2]].append(f"{d.name} (frontmatter name: {name})")
        if not as_list(fm.get("domains")):
            findings[keys[3]].append(d.name)
        if desc and not WHEN_CLAUSE_RE.search(desc):
            findings[keys[4]].append(d.name)
    return count, findings


def audit_knowledge() -> tuple[int, dict[str, list[str]]]:
    findings: dict[str, list[str]] = {
        "MISSING tags": [],
        "MISSING domains (excluded from routing)": [],
        "DOMAINS OUTSIDE TAXONOMY (add them to build_routing.DOMAIN_LABELS)": [],
    }
    keys = list(findings)
    count = 0
    if not KNOWLEDGE_DIR.is_dir():
        return count, findings
    for sub in sorted(KNOWLEDGE_DIR.iterdir()):
        # conventions/ is outside routing on purpose; CLAUDE.md links it.
        if not sub.is_dir() or sub.name == "conventions":
            continue
        for f in sorted(sub.glob("*.md")):
            count += 1
            fm = parse_frontmatter(f)
            rel = f.relative_to(KNOWLEDGE_DIR).as_posix()
            if not as_list(fm.get("tags")):
                findings[keys[0]].append(rel)
            if f.name == "index.md":
                continue
            domains = as_list(fm.get("domains"))
            if not domains:
                findings[keys[1]].append(rel)
            else:
                bad = [d for d in domains if d not in DOMAIN_LABELS]
                if bad:
                    findings[keys[2]].append(f"{rel}: {bad}")
    return count, findings


def report(findings: dict[str, list[str]]) -> int:
    issues = 0
    for label, items in findings.items():
        if items:
            issues += len(items)
            print(f"\n{label} ({len(items)}):")
            for item in items:
                print(f"  {item}")
    return issues


def main() -> None:
    utf8_stdout()
    print("=== Frontmatter Audit ===")
    skill_count, skill_findings = audit_skills()
    print(f"\nSkills scanned: {skill_count}")
    issues = report(skill_findings)
    knowledge_count, knowledge_findings = audit_knowledge()
    print(f"\nKnowledge files scanned: {knowledge_count}")
    issues += report(knowledge_findings)
    print(f"\nSummary: {issues} actionable issues")
    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
