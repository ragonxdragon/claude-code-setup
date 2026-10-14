---
type: Convention
title: "Template: Work-Package Dispatch Brief and Report Contract"
description: The brief an orchestrator sends a work-package subagent, the ten-section report it must return, and the checkpoint checklist
tags: [template, orchestration, dispatch, report-contract]
timestamp: 2026-10-13
---

# Template: Work-Package Dispatch Brief and Report Contract

Two halves of one contract. The dispatch brief is what the orchestrator sends; the report contract is what every agent returns. Agents tend to converge on this report shape on their own; freezing it makes checkpoint review mechanical.

## Dispatch brief

```text
You are the subagent for WP {n} ({name}).
WORKSPACE: worktree {path}, branch track{T}/{plan-slug}. ONE agent per worktree - if this tree is
shared, STOP and report.
PLAN: {plan file}. It is the spec; deviations get flagged, not improvised.
SURFACE: touch ONLY {owned paths}. Foreign file needed = STOP and flag (do not edit).
MIGRATIONS: only from block {NN0-NN9}; report numbers used.
PIPELINE: {pipeline doc section} in full - no shortcuts. TDD first (confirm tests fail before
implementing). FULL security battery with real tools; emit the per-skill coverage table.
FIX EVERY FLAG: HIGH down to nit. "Documented", "deferred", "tracked as follow-up" DO NOT COUNT
as fixed. Only confirmed false positives may be skipped (name them). Pre-existing findings in
files you touched are IN scope.
CIRCUIT BREAKER: if your error count is not decreasing after 2 fix attempts, stop and report.
COMMITS: granular type(scope), ASCII subject, no AI attribution, EXPLICIT pathspecs, commit
incrementally (the network can drop). Never touch _STATUS.md (orchestrator-owned).
MODEL/EFFORT: {tier} - this WP is {mechanical|standard|judgment} work.
```

## Report contract (mandatory sections, in order)

```text
STATUS: DONE | BLOCKED
1 DIFF SUMMARY: table commit -> files -> why. Lead with net diffstat (files, +/- lines).
2 CHECKBOX DELTAS: plan boxes ticked, each with its evidence (test name / path:line).
3 GATE TABLE: each SEC-GATE / acceptance criterion with PASTED tool output (test counts, scanner
  findings count, linter result). Claims without pasted output do not count.
4 REVIEW PIPELINE NOTES: what ran, what was not applicable AND WHY (skill-to-diff fit).
5 FLAGS FOUND AND FIXED: every finding with its fix commit. False-positive skips named with verdicts.
6 FLAGGED HAND-OFFS: foreign-surface issues found (flag, don't edit) - file:line + suggested owner.
7 DEFERRED-NOT-DROPPED: seams intentionally left, with WHERE the follow-up plan is recorded.
8 MIGRATIONS USED: numbers claimed.
9 LANDED PROOF: git log --oneline main..HEAD (and after merge: the main log line).
10 ARTIFACTS: absolute path + timestamp of anything produced (installers, reports, docs).
If BLOCKED: zero edits made; the pre-flight condition that failed; 2 proposed unblock paths.
```

## Checkpoint checklist (orchestrator side)

```text
[] Report contract complete (all 10 sections, evidence pasted)
[] Diff reviewed against the plan; deviations acceptable
[] Re-run any abbreviated gate (spot-check, not a full re-suite)
[] SEC-GATE rows asserted
[] Merge: fresh git status; no foreign MERGE_HEAD; union-merge {shared file list}; explicit -m
[] Tick own _STATUS.md rows (verify each claim BEFORE flipping it to done)
[] Prune the worktree; verify the branch merged before deleting it
[] Doc-drift pass if docs were touched; APPLY its findings (B3 one-dispatch form)
[] Post a one-line status + update _MAILBOX.md if other tracks are affected
```
