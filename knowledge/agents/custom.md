---
type: Agent
title: Custom Agents
description: Agent definitions that ship in agents/, starting with wave-babysitter for hands-off monitoring of background subagent waves
tags: [agent, custom, orchestration, monitoring]
timestamp: 2026-10-13
domains: [orchestration, process]
depth: single
model: sonnet
related: [skills/orchestration-and-audit.md]
---

# Custom Agents

Agent definitions live at `~/.claude/agents/<name>.md` and are invoked as a subagent type.

| Type | Purpose |
|------|---------|
| `wave-babysitter` | Watches a wave of background agents through their output files, resumes an agent killed by an API or usage-limit error once, appends heartbeats to `_MAILBOX.md`, and sends a notification when the queue drains |

## Notes

- Task notifications go to the session that spawned an agent, never to a sibling, so the babysitter watches each agent's output file or worktree instead. The dispatching orchestrator must pass those paths.
- One resume per agent, ever. A second death escalates to the human.
- Add your own agents here, one row each, and give each a `model` in its definition that matches [../conventions/model-policy.md](../conventions/model-policy.md).
