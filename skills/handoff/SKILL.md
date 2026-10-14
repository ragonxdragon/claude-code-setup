---
last_verified: 2026-10-13
name: handoff
description: "Generate the next session's opening prompt and write the NN-handoff.md file at a phase/wave boundary. Use when the user says /handoff, 'write the handoff', 'prompt for the next session', 'close out this wave', or when an orchestrator session reaches its wave/track boundary."
domains:
  - orchestration
  - workflow
  - docs
metadata:
  trigger: /handoff; phase or wave boundary; generating the next session's opening prompt
---

# Handoff

Two outputs, produced together at every phase or wave boundary: (1) the `{NN}-handoff.md` file, and (2) the one-line opener for the next session. The next session opens with ONLY the handoff file's path; a bare path is enough when the file carries verified state.

## Step 1: Verify state (evidence, not assumption)

Before writing anything:

- `git log --oneline -20` on main: confirm which work packages and SHAs actually landed.
- Test count: run the suite command and record the real number.
- `git worktree list` and `git branch -a`: list open worktrees and branches, or confirm "none, pruned".
- `_STATUS.md`: confirm the rows are current, and as of which SHA.
- Unanswered questions and half-applied fixes in this session: enumerate them. They become open items or landmines.

## Step 2: Write the handoff file

Path: the next free `{NN}-handoff.md` in the repository's handoff location (match where earlier handoffs live; else `artifacts/`). Every section is mandatory:

```markdown
# Handoff: {phase/wave} complete -> next: {next phase}
Date: {date}. Written by: {session role}. Model tier for next session: {tier}.

## State (verified, not assumed)
- Merged on main: {WPs + SHAs}  - _STATUS.md rows current as of {SHA}
- Tests: {count} green ({command})  - Open branches/worktrees: {list or "none - pruned"}

## Next task
{Single sentence.} Plan: {path}. Preconditions verified: {list}.

## Open items (binds "fix the remaining items" after any compaction)
1. {item - file:line - owner}

## Landmines
- {in-flight migrations, foreign MERGE_HEAD risk, environment blockers such as an expired gh
  token, half-applied fixes - anything the next session will step on}

## Pipeline version
{pipeline doc + version/date so process upgrades reach new sessions}
```

## Step 3: Generate the opener

One paste-ready block for the next session:

```text
Read {absolute path to NN-handoff.md}. Confirm the State section against main (evidence, not
checkboxes) before starting. Model: {tier} - switch if not on it. Then: {next task, one sentence}.
Stop after {boundary}; do not start {the phase after that}.
```

If the next session is a track orchestrator, generate its opener with the orchestrate-track skill instead, and list the handoff file in its READ FIRST section.

## Rules

- Every claim in State carries its evidence (SHA, count, command). A handoff with unverified claims carries drift into the next session.
- Open items bind across compaction: "fix the remaining items" always resolves to this list.
- The writing session CLOSES after the handoff lands. Long-lived orchestrator sessions accumulate context cost and stale assumptions; a fresh session from a verified handoff is cheaper and safer.
- ASCII only; no AI attribution if the handoff is committed.
