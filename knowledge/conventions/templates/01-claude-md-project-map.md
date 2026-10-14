---
type: Convention
title: "Template: Project CLAUDE.md (map style)"
description: A 25 to 40 line map-style project CLAUDE.md template, plus a filled example for a fictional service
tags: [template, claude-md, project-map]
timestamp: 2026-10-13
---

# Template: Project CLAUDE.md (map style)

Rule: a project CLAUDE.md is a MAP plus hard rules, 25 to 40 lines, and nothing else. Content that changes weekly lives in the docs it points at, never here. Below are the template and a filled example for a fictional service.

## Template

```markdown
# {Repo} - Claude Code Map

## What this is
{One sentence: product, stack, deployment target.}

## Read order for any new task
1. {status or tracks doc} - current state, resume point
2. {build order or plan register} - dependencies, gates
3. {architecture doc}
(Do not re-derive state from code when these docs answer it.)

## Commands
- Build: `{cmd}`   - Test: `{cmd}`   - Lint: `{cmd}`   - Run: `{cmd}`
- {Environment gotchas: which shell, which env vars, what needs WSL or admin}

## Hard rules (non-negotiable)
- {Push policy: "land on a local branch, never push origin" OR "origin push allowed"}
- {Commit format, no AI attribution; hooks enforce}
- {Concurrency rules: explicit pathspecs, one worktree per agent, migration number blocks}
- {Domain rules: color space, i18n helper, accessibility floor}
- {Deployment model, so agents never propose the wrong kind of fix: e.g. "manually shipped,
   no fleet; never defer a finding for staged-rollout reasons"}

## Project facts agents get wrong without this
- {hardware names, network addresses, secrets policy, licensing posture, tier model: the
   facts you have retyped more than once}

## Escalation
- {When to stop and ask; which decisions are yours alone}
```

## Filled example (fictional)

```markdown
# ledger-api - Claude Code Map

## What this is
Double-entry ledger HTTP API for an internal billing team. Python 3.12, FastAPI, Postgres 16,
deployed as one container to a managed Kubernetes cluster.

## Read order
1. README.md (layout table + local setup) 2. CONTRIBUTING.md (hooks, commit rules)
3. docs/ARCHITECTURE.md 4. docs/plans/_STATUS.md 5. docs/RUNBOOK.md

## Commands
- Test: `uv run pytest -q`  - Lint: `uv run ruff check .`  - Types: `uv run mypy src`
- Local stack: `docker compose up -d db` then `uv run uvicorn ledger.app:app --reload`
- Migrations: `uv run alembic upgrade head`; never edit an applied migration.

## Hard rules
- Money is integer minor units end to end; never a float, never a Decimal in JSON.
- Every write goes through ledger/postings.py; no direct INSERT into entries.
- Origin push is allowed for feature branches; main only through a reviewed PR.
- Conventional commits, no AI attribution; the changelog hook must fire (verify it).
- GPL or other copyleft code is banned; check the license of anything vendored.

## Project facts
- Postgres runs with SERIALIZABLE isolation; retry on serialization failure (40001), never
  downgrade the isolation level to make a test pass.
- The staging database is a nightly copy of production with PII scrubbed; do not load
  fixtures into it.
- Rate limits live in the gateway, not in this service.

## Escalation
- Schema changes to entries or accounts, anything that touches posting rules, and any change
  to retention: stop and ask.
```
