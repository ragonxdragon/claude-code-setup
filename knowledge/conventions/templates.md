---
type: Convention
title: Templates Index
description: Index over knowledge/conventions/templates/, covering the prompt library, proven prompt shapes, and document templates
tags: [templates, prompts, workflow, orchestration, handoff]
timestamp: 2026-10-13
---

# Templates

All templates live in [templates/](templates/). They were distilled from real working sessions: the prompt shapes that ran with the least rework, and the document formats that agents had already converged on.

| File | Use when |
|------|----------|
| [templates/07-PROMPT-TEMPLATES.md](templates/07-PROMPT-TEMPLATES.md) | The full fill-in-the-blank prompt library: A. orchestration (track boot A1, work-package dispatch A2, plan execution A3, sync, incident, resume, status, and handoff A4 to A9), B. review and verification (converge loop B1, battery fix-all B2, doc drift B3, checklist, matrix, and repo-wide audits B4 to B8), C. research, D. product and docs, E. ops and hygiene, F. micro-habits |
| [templates/07B-PROVEN-PROMPTS.md](templates/07B-PROVEN-PROMPTS.md) | High-stakes work: ten prompt shapes (P1 to P10) modeled on the cleanest runs, the clean-run checklist, and the anti-patterns list. Use these shapes as written when a mistake is expensive |
| [templates/01-claude-md-project-map.md](templates/01-claude-md-project-map.md) | Writing or reviewing a project CLAUDE.md: a map-style template (25 to 40 lines) and a filled example |
| [templates/02-wp-dispatch-and-report-contract.md](templates/02-wp-dispatch-and-report-contract.md) | Dispatching a work-package subagent or reviewing its return: dispatch brief, ten-section report contract, orchestrator checkpoint checklist |
| [templates/03-session-handoff-and-notices.md](templates/03-session-handoff-and-notices.md) | Phase or wave boundaries and cross-session communication: handoff file, sync brief, incident notice, `_MAILBOX.md` protocol |
| [templates/04-memory-entry-and-plan-doc.md](templates/04-memory-entry-and-plan-doc.md) | Writing a memory entry, plan doc, or ADR (see also [memory-policy.md](memory-policy.md)) |

## Picking a template

- Launching anything parallel or destructive: use a template. One-liners are fine for everything else, because the repository docs are the prompt and messages are clock signals.
- High stakes: start from 07B (proven shapes) and fall back to 07 (full library) for coverage.
- Documents (CLAUDE.md, handoffs, memory entries, plans, ADRs): files 01 to 04.
