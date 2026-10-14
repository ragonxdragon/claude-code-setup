---
type: Convention
title: Engineering Preferences
description: DRY, test-first, edge-case handling, explicit over clever; the defaults behind every recommendation
tags: [engineering, testing, dry, code-quality]
timestamp: 2026-10-13
---

# Engineering Preferences

<!-- Edit these to match how you want code written. They are applied to every
     recommendation and review, so keep them short and concrete. -->

Use these to guide every recommendation:

- **DRY** matters: flag repetition aggressively.
- **Well-tested code** is non-negotiable; too many tests beats too few.
- Code should be **engineered enough**: not fragile or hacky, not over-engineered.
- Handle more edge cases, not fewer; thoughtfulness over speed.
- Prefer **explicit over clever**.

## Core principles

1. **Understand first.** Read before writing; grep before creating; check current docs before trusting remembered APIs.
2. **Prove it works.** Write tests first; run the quality gates (tests, linter, types, build) before every commit; add a regression test for every bug fix.
3. **Keep it safe.** No secrets in code; validate all input; use parameterized queries; apply least privilege; flag vulnerabilities immediately.
4. **Keep it simple.** Single responsibility; no premature abstraction; delete dead code; avoid untyped dynamic values; fix warnings before committing.
5. **Don't repeat yourself.** Check `~/.claude/skills/` before writing an ad hoc procedure; keep one source of truth.
6. **Ship it.** Work on a branch, commit in small units, push according to the repository's push policy.
7. **Leave a trail.** Artifacts in `./artifacts/`; decisions in ADRs; clear names.
