---
last_verified: 2026-10-13
name: merge-wp
description: "Run the checkpoint-merge checklist for a finished work-package branch, then prune its worktree. Use when merging a WP branch, at any orchestrator checkpoint, or when the user says /merge-wp {branch}, 'merge the WP', 'checkpoint merge', or 'land this work package'."
domains:
  - orchestration
  - git-workflow
metadata:
  trigger: /merge-wp {branch}; merging a completed work-package branch at a checkpoint
---

# Merge WP

The checkpoint-merge checklist. Input: `{branch}` (for example `track3/payments-retry`). Concurrent sessions may share this repository, so every step that reads git state runs FRESH, immediately before the write it guards.

## Pre-merge gates (all must pass before any git write)

1. **Report contract complete:** the work package's report has all ten sections with pasted evidence (diff summary with net diffstat, checkbox deltas, gate table with tool output, review notes, flags fixed, hand-offs, deferred-not-dropped, migrations used, `git log --oneline main..{branch}`, artifacts). Claims without pasted output do not count. Contract: `knowledge/conventions/templates/02-wp-dispatch-and-report-contract.md`.
2. **Diff reviewed against the plan:** lead with the net diffstat; name each deviation from the plan and accept or reject it.
3. **Spot-check:** re-run any gate the report abbreviated (a spot-check, not a full re-suite).
4. **SEC-GATE rows asserted** for every gate the package claims.

## Merge sequence

5. Fresh `git status` in the MAIN checkout, immediately before merging. If `.git/MERGE_HEAD` exists from another session, WAIT and re-check; do not proceed until it clears.
6. Verify the branch is what you think it is: `git log --oneline main..{branch}`, and name the SHAs you are about to land.
7. Union-merge shared files (CHANGELOG, `_MAILBOX.md`, any file listed as shared surface), keeping BOTH sides.
8. Merge with an explicit `-m "merge(track{T}): {wp-name}"`; never `--no-edit`, never a default message.
9. On conflicts: resolve only in files this package owns. A conflict in a file another track owns means STOP, post to `_MAILBOX.md`, and wait.

## Post-merge steps

10. Tick only your own `_STATUS.md` rows, and only after verifying each row's claims with evidence (not on the package's say-so).
11. **Prune the worktree:**
    - Verify it merged first: `git branch --merged main` must list the branch.
    - On Windows, stop any process holding files in the worktree (language servers, build daemons) first, or the removal fails with a permission error.
    - `git worktree remove {path}`, then `git branch -d {branch}`.
    - Leave other sessions' worktrees alone; prune only the merged package's tree.
12. If the package touched docs, run a doc-drift pass and APPLY its findings in the same pass (audit, fix, and self-verify in one dispatch).
13. Verify the changelog hook fired on the merge commit, if the repository has one; fix and re-run if not.
14. Post a one-line status; append to `_MAILBOX.md` if other tracks are affected (a barrier cleared, a shared file changed).

## Hard rules

- Explicit pathspecs on every commit; check `git diff --cached` before committing, because other sessions stage files too.
- Never merge into a dirty main checkout you did not dirty yourself.
- Never delete a branch that `git branch --merged main` does not list.
- No AI attribution in the merge commit.
