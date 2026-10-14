---
last_verified: 2026-10-13
name: audit-wave
description: "Run a fan-out audit wave: audit skill(s) across a scope via parallel subagents, fix every finding (never defer), granular commits, changelog sync, merge. Use when the user says /audit-wave {skills} {scope}, 'run an audit wave', 'audit the repo with X and fix everything', or any audit-then-fix-all request."
domains:
  - review
  - audit
  - workflow
metadata:
  trigger: /audit-wave {skill|battery} {scope}; fan-out audit with fix-all-never-defer
---

# Audit Wave

The audit loop: fan out the audit, collect findings, fix them ALL, commit granularly, sync the changelog and docs, merge. Inputs: `{skills}` (one audit skill, a list, or `battery` for the full review battery) and `{scope}` (paths, a diff, or the whole repository).

## Phase 1: Fan-out audit (read-only)

1. Partition `{scope}` by area across parallel subagents. Size the fleet to the scope: a 600-line low-risk diff does not need a dozen workers. State the sizing judgment.
2. Model tiering: mechanical scans on the cheap tier; judgment audits (security, architecture) on the strong tier.
3. Each auditor is READ-ONLY and returns structured findings: what, where (file:line), severity, suggested replacement, and coverage notes naming what was checked and deliberately not flagged.
4. If `{skills}` is `battery`: run every applicable installed review skill and emit a per-skill coverage table (skill: filed or cleared, per bug class) so nothing is skipped silently.

## Phase 2: Project-context corrections

5. Before fixing, filter findings against project context. Run a false-positive check on suspected false positives (a dedicated skill if you have one, else a second agent with the finding and the code); only confirmed false positives may be skipped, each named with its verdict. Findings that contradict documented repository policy (for example, a deliberately committed test key) are marked corrected-not-fixed with the doc citation.

## Phase 3: Fix all, never defer

6. Fix EVERY confirmed finding, from high severity down to nit. "Documented", "deferred", and "tracked as follow-up" do not count as fixed. Pre-existing findings in touched files are IN scope. Future work that is genuinely out of scope gets a plan doc now, never a loose note.
7. Fixer agents get file-cluster ownership (no two fixers in one file) and a skip-and-why ledger. One worktree per live agent if any of them write.
8. Circuit breaker: if the error count on one finding is not decreasing after 2 attempts, halt that finding and escalate. Do not thrash.

## Phase 4: Commits and sync

9. Granular commits: one logical fix per commit, `type(scope): subject`, explicit pathspecs, no AI attribution, `git diff --cached` first.
10. Verify the changelog hook fired, if the repository has one; fix and re-run if not. If any doc-bearing file changed, run a doc-drift pass (a docs-audit agent or template B3 in the prompt library) and apply its findings.

## Phase 5: Re-audit and merge

11. A final re-audit agent covers the changed files only and returns clean or not clean. Not clean means back to Phase 3.
12. Merge per the merge-wp skill checklist (fresh git status, wait on a foreign MERGE_HEAD, union-merge shared files, explicit -m, prune worktrees).

## Report

End with: findings found, fixed, and false-positive skips (named); the commit list; the coverage table; the clean-verdict evidence; SAFE-TO-CLOSE: yes/no.
