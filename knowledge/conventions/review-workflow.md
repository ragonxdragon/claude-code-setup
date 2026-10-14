---
type: Convention
title: Review Workflow (Autonomous Full Battery)
description: Every review runs the full battery autonomously (simplicity, security, performance, correctness) and fixes every flag, with no pauses and no deferrals
tags: [review, workflow, security, autonomous, fix-all]
timestamp: 2026-10-13
---

# Review Workflow

Reviews run autonomously from start to finish, with no question pauses between sections. The user is not the message bus between review lenses.

## The battery (every task, every tier)

Every review gets all four lenses:

1. **Simplicity:** DRY violations, over- and under-engineering, dead code, premature abstraction. Delete before tuning, reuse before rewriting, standard library before custom code.
2. **Full security battery:** every installed security skill, not a subset. Emit a per-skill coverage table (skill: ran, or not applicable and why) so nothing is skipped silently. Use real tools (semgrep, CodeQL, a dependency scanner), not read-only opinions.
3. **Performance:** N+1 queries, memory use, caching opportunities, high-complexity paths.
4. **Correctness:** coverage gaps, assertion strength, untested failure modes, edge cases, error handling.

Run the lenses as parallel subagents when the diff is large enough to warrant it. Scale the fleet to the diff's size and risk: a small, safe diff does not need a dozen workers. State the judgment, then proceed.

## Fix everything, defer nothing

- Fix EVERY flag, from high severity down to nit. "Documented", "tracked as follow-up", and "deferred" do not count as fixed.
- The only findings you may skip: confirmed false positives (name each, with the verdict) and genuinely out-of-scope items (say why).
- Pre-existing findings in files the change touched are IN scope.
- Nothing is logged as tracked debt. Every finding is fixed, or the work it needs is planned and built in the same pass.
- Verify findings empirically where you can: write a throwaway probe or exploit, run it, delete it. A read-only review does not support a security claim.
- Re-run the battery until a full pass is clean, then verify end to end and paste the passing output.

## Reporting

For each issue: a concrete description with file:line, the fix applied (commit), and the evidence. Recommendations map to [engineering-prefs](engineering-prefs.md). A decision with a genuine owner-level tradeoff (scope, cost, product direction) gets a DECISION-NEEDED block with the data attached. That is the only thing that goes back to the user mid-review.

## Interactive variant (opt-in only)

If the user explicitly asks to walk through a review together, use the interactive pattern. For a big change, go one section at a time (architecture, code quality, tests, performance; at most four top issues per section). For a small change, ask one question per section. Present two or three options per issue and pause after each section. Never default to this mode.
