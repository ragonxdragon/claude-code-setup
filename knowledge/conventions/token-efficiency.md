---
type: Convention
title: Token Efficiency Rules
description: Context management, subagent delegation, shell and polling discipline, and output compression
tags: [token-efficiency, subagents, context]
timestamp: 2026-10-13
---

# Token Efficiency Rules

Context is the scarce resource, not response length. Quality degrades as the context window fills, so the goal is to keep the *active* context on the current task, not to minimize tokens in isolation.

## Delegate investigation and verification to subagents

Subagents are the main lever. A subagent explores in its own context window and reports back a summary, which keeps the main conversation clean.

- Use a subagent for open-ended exploration ("investigate how X works", "find every caller of Y") so the main context receives the answer, not every file read along the way.
- Use a subagent for independent verification after implementing something. A fresh context is not biased toward code it just wrote.
- Do not scope an investigation so loosely that the subagent reads hundreds of files anyway. Narrow the ask.
- Multi-lens reviews (security, performance, correctness, simplicity) are exactly the case for parallel subagents.

## Do not pay for the same content twice

- If a file will need editing, `Read` it once rather than `grep` or `cat` it now and `Read` it in full later.
- For pure inspection with no planned edit, `grep` stays cheaper than `Read`. Do not `Read` everything just in case.
- Batch the reads, then batch the edits, rather than interleaving file by file.

## Manage context, not response length

- Run `/clear` between genuinely unrelated tasks, not on every task switch. A long session deep in one problem is fine while the history stays relevant.
- After two failed corrections on the same issue, `/clear` and restart with a more specific prompt instead of arguing with a polluted context.
- Prefer file:line references over pasting file contents when a reference will do.
- Scope skills and reviews to the files or diff in play unless the user asked for a full-project pass.

## Shell, runtime, and polling discipline

- **Ad hoc Python:** use `uv run python` when the interpreter is ambiguous (several environments, a dependency needed); plain `python` otherwise. Record any machine quirk here (a missing launcher, a shimmed interpreter) so no session rediscovers it.
- **Pick the shell by the binary, not by habit.** Keep a lookup table for your machine, for example:

| Binary or task | Shell |
|----------------|-------|
| node, npx, pnpm, dotnet | PowerShell (on Windows) |
| coreutils (ls, find, cp, tar), jq | Bash |
| HTTP or JSON scripting | whichever has the better client on this machine |

- **Never poll with sleep and cat.** Use `run_in_background` and its completion notification, or Monitor with an until-condition. A sleep loop burns a turn per poll and blocks the session.
- **Check the size before a Read** of any file that may exceed about 80 KB (`ls -la` first), then Read with `offset` and `limit`.

## Output

- Match response length to the task: a direct question gets a direct answer; a multi-file change gets a summary of what changed and what is next.
- No fixed token cap. Compress by cutting restatement and narration, not by dropping substance the user asked for.
- State results directly; skip preambles that restate the request.

## Thinking versus writing

Split by whether the text outlives the session, not by artifact type:

- **Persists or represents the work to others** (commit messages, PR descriptions, documentation, code comments): full writing standard, plain and professional, active voice. No exceptions.
- **Working text** (extended thinking, subagent prompts, scratch notes, intermediate analysis, and the chat reply itself): terse and fragmentary is fine. It is billed as output either way.

Write in full sentences, even in working text, for security warnings, irreversible-action confirmations, and any multi-step sequence where a dropped word could cause a misread.
