---
type: Convention
title: Memory-Write Policy
description: Rules for curated memory files, covering one fact per file, format, size cap, banned content, supersession, and an optional full-text backing store
tags: [memory, policy, supersession, curation]
timestamp: 2026-10-13
---

# Memory-Write Policy

Rules for the curated memory layer: the per-fact `.md` files that Claude Code's auto-memory keeps for each project, indexed by `MEMORY.md`. Skeleton for a new entry: [templates/04-memory-entry-and-plan-doc.md](templates/04-memory-entry-and-plan-doc.md).

## One fact per file

Each memory file holds exactly one durable fact. A file that needs a second, unrelated fact is two files.

## Format: Fact / Why / How to apply

- **Fact:** the rule or fact, stated so a cold session can apply it.
- **Why:** the dated incident, with the exact error text or quote.
- **How to apply:** exact commands or behavior, including NEGATIVE knowledge: what was tried and failed, with error codes. This is the part that saves the next session from repeating the attempt.

## Size: about 2 KB, soft cap

Past 2 KB a memory is usually carrying status, narrative, or a postmortem. Compress it to the durable lines and move the rest to where it belongs.

## Banned content (write a pointer instead)

- **Config state.** settings.json owns it. A memory may point at the setting, never copy it.
- **Repository status.** The repo's status and plan docs own it. A memory that narrates build progress goes stale within days. Point at the doc: "For live status read {doc}; it supersedes this snapshot."
- Anything git history already records.

## Naming

The `name` field is kebab-case and matches the file name. `[[links]]` resolve on this name, so a mismatch is a dead link.

## Incident postmortems

A postmortem lives INSIDE the reference file it concerns, as a clearly marked section (for example `## Postmortem (2026-07-06, resolved)`), not as a standalone memory file. The durable rule stays in the body; the marked section carries the incident detail and can be pruned once it no longer matters.

## Supersession

When a fact changes, never overwrite it silently. Edit the file in place with a dated note that says what changed and why, and update the index line. If you keep a separate knowledge-graph store, use its own primitives for their distinct meanings: supersede a single-valued fact that changed, invalidate a fact that ended with no successor, add a new fact that is independent.

## Optional: a full-text backing store

If you run a verbatim memory store alongside the curated files (MemPalace is one; see the optional `hooks/mempalace_wakeup.py`), split the work:

- **Curated files plus the MEMORY.md index** are the always-loaded pointer layer: small, one fact each, index lines of 120 characters or fewer (a locator, not a copy).
- **The backing store** holds verbatim text and is queried on demand. Facts that are not promoted to a curated file are recalled through search.
- A curated fact points INTO the store rather than duplicating it.
