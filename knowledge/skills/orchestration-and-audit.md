---
type: Skill
title: Orchestration and Audit Skills
description: Audit waves, converge-until-clean audits, work-package merges, track orchestrator prompts, session handoffs, app kickoff, and vendoring with license checks
tags: [orchestration, audit, review, handoff, merge, kickoff, vendoring]
timestamp: 2026-10-13
domains: [orchestration, process, code-review, engineering]
depth: rich
related: [agents/custom.md, conventions/workflow.md]
---

# Orchestration and Audit Skills

<!-- Structure example: one concept file per skill domain. The table rows are
     what drift_check.py looks for (the skill name in backticks), and the
     frontmatter above is what build_routing.py turns into CONTEXT.md rows. -->

Skills live at `~/.claude/skills/<name>/SKILL.md`. Invoke with `/<name>`.

| Skill | Invoke | Purpose |
|-------|--------|---------|
| `audit-wave` | `/audit-wave` | Fan-out audit wave: audit skills across a scope with parallel subagents, fix every finding, commit granularly, merge |
| `converge-audit` | `/converge-audit` | Loop an audit until a full pass yields zero new findings, verifying every claim against raw sources |
| `merge-wp` | `/merge-wp` | Checkpoint-merge checklist for a finished work-package branch, then prune its worktree |
| `orchestrate-track` | `/orchestrate-track` | Render the track-orchestrator boot prompt for track N from the live `_PARALLEL_TRACKS.md` |
| `handoff` | `/handoff` | Write `{NN}-handoff.md` and the next session's one-line opener at a phase or wave boundary |
| `app-kickoff` | `/app-kickoff` | App kickoff or redirect pipeline: one clarification round, grounded research, spec-driven doc suite, human-review gate |
| `vendor-sweep` | `/vendor-sweep` | Vendor code from external repositories verbatim with license gates, provenance headers, and a second-agent verification |

## How they fit together

- A multi-track build starts with `/orchestrate-track N` in each orchestrator session, merges each finished package with `/merge-wp`, and closes each wave with `/handoff`.
- `/audit-wave` is the fix-everything loop for code; `converge-audit` is the same discipline for claims checked against an external source.
- The prompt shapes these skills encode are in [../conventions/templates/07-PROMPT-TEMPLATES.md](../conventions/templates/07-PROMPT-TEMPLATES.md).
