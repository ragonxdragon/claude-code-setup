---
type: Convention
title: Routing Audit Procedure
description: How to audit the CONTEXT.md routing table against the real knowledge inventory, with the three defect classes and a report format
tags: [audit, routing, defects]
timestamp: 2026-10-13
---

# Routing Audit Procedure

`check_routing.py` proves the generated table matches the frontmatter. It cannot prove the frontmatter is right. A routing audit checks the second thing: does each concept file route to the domains a task would actually come from, and does its table row carry enough to pick it?

Run one when you add a skill bundle, when a request lands on the wrong skill, or as part of a quarterly config review.

## Defect classes

- **MISSING:** a skill, agent, or plugin that exists but appears in no concept file, so no route reaches it. `drift_check.py` finds installed skills that are missing; the audit also catches planned or plugin-provided ones.
- **MISCATEGORIZED:** a concept filed under too few domains, or the wrong ones. Example: a platform design-guidelines bundle filed only under its platform, when it governs visual and interaction design too and belongs under `ui` and `ux` as well.
- **UNDERSPECIFIED:** the routing row loses context the file body holds. Example: a bundle of eleven skills whose description names two, so the other nine are invisible when the model scans the table.

## Procedure

1. List every concept file under `knowledge/skills/`, `knowledge/agents/`, and `knowledge/marketplaces/` and report the count.
2. For each file, record: the domains it is routed under, the domains its content actually serves, its depth (single or rich, with the sub-skill count), and which of its members the description names.
3. Classify each gap as MISSING, MISCATEGORIZED, or UNDERSPECIFIED.
4. Fix in the frontmatter: add `domains`, set `depth: rich` where the file lists sub-skills, and rewrite `description` so the row names what a task would search for.
5. Run `python scripts/build_routing.py`, then `python scripts/check_routing.py` and `python scripts/frontmatter_audit.py`.

## Report format

```markdown
### knowledge/skills/{file}.md
- Routed under: {domains}
- Serves: {domains the content covers}
- Depth: {single | rich (N skills: a, b, c)}
- Defects:
  - MISCATEGORIZED: {what and why}
  - UNDERSPECIFIED: {row names 2 of N members}
- Fix: {frontmatter change}
```

## Worked example (this template)

The template's own `knowledge/skills/orchestration-and-audit.md` lists nine skills. Routed only under `process`, a request about merging a work-package branch (an orchestration task) would not reach it, so it is also routed under `orchestration` and `code-review`. Its description names the members a request would search for (audit, merge, handoff, kickoff) so the row is not underspecified.
