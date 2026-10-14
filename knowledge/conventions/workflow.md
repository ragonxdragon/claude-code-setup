---
type: Convention
title: Workflow
description: Branching, artifact naming, the planning flow, the orchestration command, skill, and agent set, and the new-skill policy
tags: [workflow, branching, artifacts, planning, commands, orchestration]
timestamp: 2026-10-13
---

# Workflow

## Branching

- Branch from `main`. Never commit directly to `main`.
- Branch naming: `<area>/feature/<ticket-id>-<short>` (for example `api/feature/PRJ-42-retry-backoff`). Orchestrated work packages use `track{N}/{plan-slug}`.

## Planning flow

PR-FAQ, then PRD, then ADR, then design spec, then plan, then implementation.

## Artifacts

Planning documents live in `./artifacts/`:

| Type | Pattern |
|------|---------|
| Vision | `pr_faq_[feature].md` |
| Requirements | `prd_[feature].md` |
| Architecture | `adr_[topic].md` |
| System design | `system_design_[component].md` |
| Design | `design_spec_[component].md` |
| Plan | `plan_[task].md` |
| Security audit | `security_audit_[date].md` |
| Post-mortem | `postmortem_[incident-id].md` |

## Working directories

| Directory | Purpose | Lifecycle |
|-----------|---------|-----------|
| `./artifacts/` | Durable documents | Committed to the repo |
| `./scratchpad/` | Ephemeral working notes | Gitignored, disposable |

## Multi-session orchestration files

Parallel work across several sessions in one repository coordinates through a small set of files in the plans directory (`docs/plans/` by default; pick one location and use it everywhere):

| File | Owner | Purpose |
|------|-------|---------|
| `_PARALLEL_TRACKS.md` | the human | Each track's queue, barriers, owned file surface, migration number block, branch prefix |
| `_STATUS.md` | each orchestrator, own rows only | Current state of every work package |
| `_BUILD_ORDER.md` | the human | Dependencies and SEC-GATE definitions |
| `_MAILBOX.md` | everyone, append-only | Cross-session messages, sender-stamped, acknowledged on read |

## Commands, skills, and agents

### /orchestrate-track {N} (skill)

Trigger: opening an orchestrator session for track N of a multi-track build. Renders the boot prompt (template A1 in [templates/07-PROMPT-TEMPLATES.md](templates/07-PROMPT-TEMPLATES.md)) from the live `_PARALLEL_TRACKS.md`, so there is no paste drift and the prompt is always current. The orchestrator never writes feature code; it dispatches one background subagent per work package, each in its own worktree.

### /merge-wp {branch} (skill)

Trigger: a work package's subagent reports DONE with a complete report contract. Runs the checkpoint sequence: review the diff (net diffstat first), assert SEC-GATEs, merge (fresh `git status`, wait on a foreign MERGE_HEAD, union-merge shared files, explicit `-m`), tick own `_STATUS.md` rows, prune the worktree, run the doc-drift pass if the package touched docs.

### /audit-wave {skill|battery} {scope} (skill)

Trigger: "audit X" work, one audit skill or the full battery over a scope. Bakes in the standing rules so they never need retyping: fix everything, model tier per subagent, granular commits, changelog and doc sync, project-context corrections, merge.

### /handoff (skill)

Trigger: a phase or wave boundary, before closing the session. Writes `{NN}-handoff.md` (verified state, next task, model tier, open items, landmines) from [templates/03-session-handoff-and-notices.md](templates/03-session-handoff-and-notices.md). The next session opens with only that file's path.

### /drift-check (command)

Trigger: scheduled weekly maintenance, or a suspicion that routing, skills, or hooks have drifted. Audits installed skills against the knowledge index, checks routing, and runs the hook self-test so a wiring bug surfaces in hours, not weeks.

### converge-audit (skill)

Trigger: "audit {scope} against {source}". Enumerates sources and reports the count first, reads raw sources (never summaries), verifies every claim against sources rather than model memory, and loops until a full pass yields zero new findings.

### vendor-sweep (skill)

Trigger: vendoring code from external repositories. Enumerates every repository, checks each license at a pinned SHA, copies verbatim with provenance headers, appends full license texts to `LICENSES.md`, opens every directory in pass one, commits nothing, and has a second agent byte-verify a sample plus the license claims.

### app-kickoff (skill)

Trigger: starting a new app or redirecting an off-track one. One clarification round, grounded research, a spec-driven document suite, tool-grounded verification, and a structured human-review gate.

### runner-setup and legal-doc-pass (skills)

Trigger: registering a self-hosted GitHub Actions runner without a token ever entering the chat; keeping a set of legal documents consistent after a product or data-flow change.

### wave-babysitter (agent)

Trigger: any long-running wave of background subagents. Watches each agent's output, resumes an agent killed by an API or usage-limit error once, posts heartbeats to the mailbox, and notifies when the queue drains.

## New skill policy

Install a new skill **per project** (in the repository's own `.claude/skills/`) by default, not globally in `~/.claude/skills/`. Promote it to the global directory only once it is used in **three or more repositories**. A global skill carries an ongoing cost (frontmatter checks, routing rows, audit and triage) that a per-project skill does not.
