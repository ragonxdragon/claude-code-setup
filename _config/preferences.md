---
type: Convention
title: User Preferences
description: Set-once preferences for output detail level and response style
tags: [config, preferences, output]
timestamp: 2026-10-13
---

# User Preferences

<!--
Set-once preferences: how you want answers shaped, independent of any task.
CLAUDE.md links here. Keep rules that live elsewhere OUT of this file and
point to their single source of truth instead (model choice lives in
model-policy.md, session hygiene in token-efficiency.md), so there is never
a second, drifting copy.
-->

## Output detail level

Default: **<Minimal | Standard | Full>**. <!-- e.g. Minimal = about 200 tokens; ask before generating long output. -->
Override: say "Standard" or "Full" in the request.

## Code review

<!-- Example of a standing review rule. Edit to taste. -->
Fix every issue a review flags: high, medium, and low severity. Never defer a low-severity issue.

## Response style

<!-- Replace with your own style rules. These are the defaults this template ships with. -->
- Compact, structured responses
- No trailing summaries ("here's what I just did")
- No unrequested explanations
- Conclusion first, then a one or two line reason
- Bullet points over prose

## Writing standard

<!-- Applies to anything that outlives the session: commits, docs, comments. -->
- <LANGUAGE AND SPELLING, e.g. plain American English>
- No emoji; no em or en dashes (hooks/humanizer_editgate.py enforces the dashes)
- No marketing words; comments describe what the code does, not its history

## Model selection

Single source of truth: [knowledge/conventions/model-policy.md](../knowledge/conventions/model-policy.md). No model table lives here.

## Session hygiene

Single source of truth: [knowledge/conventions/token-efficiency.md](../knowledge/conventions/token-efficiency.md) (context management section). No session-hygiene rules live here.
