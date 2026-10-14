---
type: Agent
title: Explore Agent
description: Built-in read-only search agent for finding files, symbols, and patterns
tags: [agent, explore, search, read-only]
timestamp: 2026-10-13
domains: [engineering, process]
depth: single
model: haiku
related: []
---

# Explore Agent

**Type:** `Explore` (built into Claude Code)

Read-only search agent. Use it for:

- finding files by pattern (for example `src/components/**/*.tsx`)
- searching for symbols or keywords
- answering "where is X defined" or "which files reference Y"

**Do not use it for** code review, design-doc audits, cross-file consistency checks, or open-ended analysis: it reads excerpts, not whole files.

**State the search breadth:** quick (a single lookup), medium (moderate exploration), or very thorough (several locations and naming conventions).

**Tools:** read and search only; no edits.
