---
type: Convention
title: Model Tier Policy
description: Tier-to-work mapping for sessions and subagents, and when to pause for a /model switch
tags: [model, routing, tier, opus, sonnet, haiku, policy]
timestamp: 2026-10-13
---

# Model Tier Policy

<!-- Fill in your session default. Pick the strongest model you are willing to
     pay for in long interactive sessions; subagents drop below it. -->

## Session default

**`<SESSION DEFAULT MODEL>`** is the session default. Concept files without a `model` field inherit it. If your default supports a long-context variant, decide once whether sessions run with it and record that here.

## Tier mapping

| Tier | Use when | Examples |
|------|----------|----------|
| session default | Interactive sessions, orchestrators, and work that needs long context or top-tier judgment | Orchestration, planning, architecture, long multi-file sessions |
| `opus` | Subagent judgment with an asymmetric downside: a wrong call has serious downstream cost | Architecture decisions, threat modeling of a novel attack surface, novel design problems, high-effort code review |
| `sonnet` | Standard subagent work, the balance of quality and cost for fan-outs | Implementation work packages, debugging, routing, standard code review, doc audits |
| `haiku` | Purely mechanical work with no hidden judgment | Checker loops, build or generate scripts, format validation, spec-compliance checks, search tasks, templated pipeline stages |

## Subagent tiering

Subagent fan-outs start from a cold context and do not share the parent's prompt cache, so each one pays full price. Tier them per role: keep the session default for the orchestrator, and drop each subagent to the cheapest tier that fits its work. Sonnet for standard implementation and review, haiku for mechanical passes, opus only where a wrong call is expensive.

## Code review exception

Code review tier follows the requested **effort level**, not a static stamp:

- high or maximum effort: opus
- low or medium effort: sonnet

Leave the review concept file unstamped; the effort level is the signal.

## Security exception

Applying known security patterns is standard work, so the security concept file stays unstamped. Threat modeling of a new attack surface is opus work: say so when the task is clearly that kind, rather than stamping the whole domain.

## Switch rule

When routing a task or making a plan:

1. If the task's recommended tier differs from the current session model, **name the tier and pause**: "This task wants opus. Switch with `/model` before I proceed."
2. Proceed after the switch.
3. When the task closes, say so: "Task done; back to the session default." Stay on the switched tier when the next task needs the same tier.

## Scarcity rule

Stamp `model` only where the tier genuinely differs from the session default, and leave the middle unmarked. When most routing rows show a tier, the policy has drifted: a stamp should be the exception.

## Measuring it

`scripts/kpi_snapshot.py` reports the model mix over recent sessions and checks one family against a ceiling (for example `--gate-family opus --gate-max 40`). Run it weekly and watch the trend file.
