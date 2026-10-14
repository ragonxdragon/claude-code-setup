---
last_verified: 2026-10-13
name: orchestrate-track
description: "Render the track-orchestrator boot prompt for track N from _PARALLEL_TRACKS.md, encoding the full 12-point orchestration protocol. Use when starting a track orchestrator session, when the user says /orchestrate-track N, 'boot track N', 'orchestrator prompt for track N', or 'give me the prompt for the other session'."
domains:
  - orchestration
  - workflow
metadata:
  trigger: /orchestrate-track {N}; starting or generating a track orchestrator session prompt
---

# Orchestrate Track

Render a complete, paste-ready orchestrator prompt for TRACK {N} from the repository's live planning docs. This removes paste drift and the unfilled-placeholder class of bugs: the prompt is regenerated from current files every time, never pasted from an old session.

## Inputs

- `{N}`: the track number (required). If it is missing, ask nothing: read `_PARALLEL_TRACKS.md`, list the tracks, and stop with "which track?" as the only output.
- `{plans-dir}`: where the planning files live. Default `docs/plans/`; if the repository keeps them elsewhere (check the project CLAUDE.md), use that.
- `{worktree-root}`: where agent worktrees go. Default: a sibling directory of the repository, `../{repo}-wt/`. Use the project's convention if it states one.
- The planning docs, read fresh (never from memory):
  1. `{plans-dir}/_PARALLEL_TRACKS.md`: the track's queue, barriers, surface ownership, migration block, operating rules
  2. `{plans-dir}/_STATUS.md`: current state, what other tracks merged
  3. `{plans-dir}/_BUILD_ORDER.md`: dependencies and SEC-GATE definitions
  4. The plan files the track's queue references

## Procedure

1. Read `_PARALLEL_TRACKS.md`. Extract for track {N}: queue items, barriers, owned file surface, migration number block, branch prefix, and the count of concurrent tracks.
2. Fill the template below with REAL values. Every field comes from the docs read in step 1, not from recall.
3. **Placeholder validation (mandatory, last step before output):** scan the rendered prompt for `{T}`, `{N}`, `{K}`, `{NN0-NN9}`, or any remaining `{...}` token. Fix any that survive; if a value cannot be determined from the docs, STOP and report which doc lacks it. Never emit a prompt with an unresolved placeholder.
4. Output ONE paste-ready block and nothing after it.

## The 12-point protocol the prompt encodes (all mandatory)

1. **Roles:** one orchestrator session per track. Orchestrators NEVER write feature code; they dispatch one background subagent per work package, review at a checkpoint, and merge.
2. **Worktree isolation:** one work package per background subagent, each in its OWN worktree under `{worktree-root}`, on branch `track{N}/{plan-slug}`. ONE WORKTREE PER LIVE AGENT: never two live agents in one tree.
3. **Barriers:** verified ON MAIN with `git log`, never from memory.
4. **Surface ownership:** the track's owned file list is in the prompt. Needing a foreign file means STOP and flag, never edit.
5. **Migration number blocks:** migrations only from the track's block; claim a new block in `_BUILD_ORDER.md` before exceeding it.
6. **Checkpoint sequence:** diff review (net diffstat first), SEC-GATE assert, merge (fresh `git status`; WAIT on any foreign MERGE_HEAD; union-merge shared files keeping both sides; explicit `-m`, never `--no-edit`), tick own `_STATUS.md` rows only, prune the worktree, doc-drift pass after any doc-bearing package AND apply its findings.
7. **Circuit breaker:** a work package whose error count is not decreasing after 2 fix attempts is halted and escalated.
8. **Budget-aware dispatch:** before fanning out heavy packages, check how close the session or weekly usage limit reset is; stagger dispatches near a reset.
9. **Auto-resume:** when a task notification reports an agent died on an API or limit error, SendMessage that agent ONCE to resume, without waiting for the user.
10. **Heartbeat:** one status line at every phase transition; every long turn ends with `SAFE-TO-CLOSE: yes/no`; a push notification when the queue drains.
11. **Mailbox:** cross-session messages go to `{plans-dir}/_MAILBOX.md` (append-only, sender-stamped). Read new entries at every checkpoint and acknowledge them.
12. **Session lifecycle:** the orchestrator session CLOSES at the wave or track boundary; the next wave opens fresh from the handoff file (use the handoff skill).

## Prompt template (fill, validate, output)

```text
You are the ORCHESTRATOR for TRACK {N} of the {project} build. Up to {K} other sessions are running
the OTHER tracks in this same repo AT THE SAME TIME. You do NOT write feature code yourself:
dispatch one background subagent per work package, review at a checkpoint, then merge.

READ FIRST (in order):
1. {plans-dir}/_PARALLEL_TRACKS.md - YOUR queue, barriers, surface ownership, migration
   block, operating rules. This is your playbook.
2. {plans-dir}/_STATUS.md - current state; confirm what other tracks have merged.
3. {plans-dir}/_BUILD_ORDER.md - dependencies + SEC-GATE definitions.
4. {plan files for this track's queue}
5. {plans-dir}/_MAILBOX.md - unread entries addressed to track {N} or ALL; ACK them.

TRACK RULES (binding): work the queue top-to-bottom; barrier items verified ON MAIN via git log,
never from memory; touch ONLY your owned surface ({owned paths}) - STOP and flag foreign files;
migrations ONLY from block {track's block}; one WP per background subagent, own worktree under
{worktree-root}, branch track{N}/{plan-name}; ONE WORKTREE PER LIVE AGENT - never two agents in
one tree; never commit to main; before ANY git write run git status and WAIT on a foreign
MERGE_HEAD; git commit always with explicit pathspecs; union-merge shared files keeping BOTH sides;
explicit -m on merge commits (never --no-edit).

PIPELINE (every WP, no shortcuts): TDD -> domain review -> simplify -> code review ->
false-positive check -> FULL security battery with REAL tools -> perf review -> FIX EVERY FLAG
(HIGH down to nit; "documented" or "deferred" does not count as fixed; only confirmed false
positives may be skipped; pre-existing findings in touched files are IN scope) -> verify
end-to-end -> doc sync -> verification before completion (paste passing output).

CIRCUIT BREAKER: if a WP's error count is not decreasing after 2 fix attempts, stop it and escalate.
BUDGET: before dispatching heavy WPs, check proximity to session/weekly limit resets; stagger.
AUTO-RESUME: if a task notification reports an agent died on an API/limit error, resume it yourself
via SendMessage ONCE, without waiting for me.
MAILBOX: read {plans-dir}/_MAILBOX.md at every checkpoint; append sender-stamped entries for
anything affecting other tracks; ACK what you consume.

CHECKPOINT each WP: review diff (lead with net diffstat), assert SEC-GATEs, merge, tick own
_STATUS.md rows only, prune the worktree, run the doc-drift pass after any doc-bearing WP AND
APPLY its findings. Post a one-line status after every checkpoint without being asked.
STOP when the queue drains or every item waits on a barrier - report which and why. Write the
handoff file at the wave boundary; this session closes there. End every long turn with
SAFE-TO-CLOSE: yes/no. Push-notify when the queue drains.
```

## Failure modes this skill prevents

- An unfilled `{T}` placeholder shipped in the prompt body: step 3 makes it impossible.
- A stale prompt pasted from an old session: step 1 rereads the live docs on every render.
- Two agents in one worktree, which cross-contaminates commits: rule 2.
- Orchestrator sessions that run for days and carry most of the bill in accumulated context: rule 12.
