---
type: Convention
title: CI and Enforcement
description: How the global config is enforced (git, CI on the template, a scheduled drift check) and the per-repo pre-commit and PR gate rules
tags: [ci, enforcement, pre-commit, drift-check, pr-gate]
timestamp: 2026-10-13
---

# CI and Enforcement

## Global config enforcement

Three mechanisms, each catching a different kind of drift:

1. **~/.claude is a git repository.** Every change to CLAUDE.md, knowledge/, hooks/, scripts/, and settings.json is committed, so drift is diffable and revertible. Keep secrets and machine state out of it with the provided `.gitignore`.
2. **CI on the template.** This repository's workflow runs ruff, `hooks/hooks_selftest.py`, and the validators on every push and pull request, so a broken hook or a stale routing table cannot land.
3. **A scheduled drift check.** Run `/drift-check` weekly (a scheduled session, a cron job, or a calendar reminder). It runs `scripts/drift_check.py` (installed skills against the knowledge index, plus routing staleness) and `hooks/hooks_selftest.py --installed` (every registered hook, run exactly as wired). Fix findings in that session rather than logging them.

If routing seems to miss a skill between runs, run `python scripts/check_routing.py`. The table is generated, so the fix belongs in the concept file's `domains` field, not in the table.

## Per-repo pre-commit hooks

Project repositories (not ~/.claude) install their own git hooks, for example through an `install-hooks.sh`:

- Commit format: `type(scope): subject`, no AI attribution trailers.
- Changelog sync on post-commit, if the repo keeps one. Verify it fired after each commit.
- Optional: large-diff rejection, a secret scanner (gitleaks), and the same writing-style gate as `hooks/humanizer_editgate.py`.

## PR gate rules (repos with CI)

- A PR produced with Claude includes a short summary of the change (50 words or fewer) and at least one test.
- A non-compliant PR is rejected and redone from the right template (see [templates.md](templates.md)).

## Emergency bypass

```bash
git commit --no-verify -m "emergency: <reason>"
```

Use it only when required, and record the reason in the commit message.
