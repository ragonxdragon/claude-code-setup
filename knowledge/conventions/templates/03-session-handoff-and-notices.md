---
type: Convention
title: "Templates: Session Handoff, Sync Brief, Incident Notice, Mailbox"
description: The handoff file written at every phase boundary, plus the cross-session sync brief, incident notice, and mailbox protocol
tags: [template, handoff, mailbox, orchestration]
timestamp: 2026-10-13
---

# Templates: Session Handoff, Sync Brief, Incident Notice, Mailbox

## 1. Session handoff file ({NN}-handoff.md, written at every phase or wave boundary)

The new session opens with ONLY this file's path. A bare path is enough when the file carries verified state.

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
2. ...

## Landmines
- {anything the next session will step on: in-flight migrations, foreign MERGE_HEAD risk,
  environment blockers such as an expired gh token, half-applied fixes}

## Pipeline version
{pipeline doc + version/date so process upgrades reach new sessions}
```

## 2. Cross-session sync brief (small routine updates)

```text
Sync first: main is at {SHA}. WHAT LANDED: {commits/decisions}. WHAT THIS MEANS FOR YOUR WORK:
{keep/change/drop}. MERGE NOTE: {conflict regions}. SCOPE GUARD: only {X,Y} live; do NOT touch
{Z}; {WP-N} is DONE - verify-only.
```

## 3. Incident notice (for anything that crossed session boundaries)

Use it whenever one session's action affected another's work, for example a bare commit that swept up files another session had staged.

```text
Cross-session notice from {sender} - action needed on {surface}.
WHAT HAPPENED (root cause): {mechanism, not blame}
YOUR FILES AFFECTED: {list}
CRITICAL FACTS: {lost? history rewritten? unreviewed code on main?}
WHAT YOU NEED TO DO: 1... 2...
WRITE-UPS: {commits/docs}
FIX ON MY SIDE: {behavior change so it cannot recur}
```

## 4. _MAILBOX.md (replaces the human as the message bus)

One file in the plans directory (default `docs/plans/_MAILBOX.md`). Append-only. Every orchestrator reads new entries at every checkpoint and marks them consumed.

```markdown
## {timestamp} FROM track-{N} TO {track-M|ALL} [UNREAD|ACK:{who}]
{sync brief or incident notice, inline}
```

Rules: the sender appends and never edits old entries; the reader appends `ACK:{track} {timestamp}` to the header line. A barrier-cleared message reads: "BARRIER {Bn} CLEARED: {WPs} on main (verify git log). Re-read your queue; dispatch newly unblocked items; report or state why still blocked."
