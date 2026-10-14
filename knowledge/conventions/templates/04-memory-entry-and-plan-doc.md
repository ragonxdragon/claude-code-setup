---
type: Convention
title: "Templates: Memory Entry, Plan Doc, ADR"
description: Exact skeletons for a curated memory entry, a TDD plan document, and an ADR
tags: [template, memory, plan, adr]
timestamp: 2026-10-13
---

# Templates: Memory Entry, Plan Doc, ADR

## 1. Memory entry

File: `{type}_{kebab_slug}.md` in the memory directory. Types: user, feedback, project, reference. Soft cap 2 KB. One fact per file. BANNED content: config state (settings.json owns it), repository status (the status doc owns it), anything git history records. Incident postmortems go to the repository's incidents doc; only the durable rule stays in memory. Full rules: [../memory-policy.md](../memory-policy.md).

```markdown
---
name: {type}-{kebab-slug}        # kebab-case = filename with hyphens; links resolve on this
description: "{one line, current - update it when the body changes}"
metadata:
  type: {feedback|project|reference|user}
---
**Fact:** {the rule/fact, stated so a cold session can apply it}

**Why:** {the dated incident, with exact error text or quote}

**How to apply:** {exact commands/behavior; include NEGATIVE knowledge - what was tried and
failed, with error codes: this is what saves future sessions retries}

{If adjacent to fast-moving state:} For live status read {doc} - it supersedes this snapshot.
Related: [[other-memory-name]]
```

Index line in MEMORY.md: 120 characters or fewer, a locator rather than a copy: `- [Title](file.md) - {hook}`. Supersession is an in-place edit with a dated note.

## 2. Plan doc skeleton ({plans-dir}/{YYYY-MM-DD}-{slug}.md)

```markdown
# {Title}
Status: DRAFT | APPROVED | IN-PROGRESS | DONE. Owner track: {N}. Migration block: {NN0-NN9}.
Naming: waves are integers, WPs are {W}.{n} - never "Wave 1.0".

## Goal
{2-3 sentences; the user-visible outcome}

## Non-goals / fences
{what is explicitly out of scope; done work that must NOT be redone}

## Riskiest unknown (do first)
{the one assumption that invalidates the plan if false + the isolation probe + STOP condition}

## Tasks (TDD; each independently reviewable; split plans over ~40 boxes into parts A/B)
- [ ] Task 1: {behavior} - test first: {test name} - files: {paths}
- [ ] ...
DECISION: {choice point} - options (a)/(b)/(c) with cost data - OWNER DECIDES.

## SEC-GATE mapping
| Gate | Assertion | Evidence required |

## Doc sync
{which docs this plan touches when done: _STATUS, _BUILD_ORDER, ARCHITECTURE, CHANGELOG}
```

## 3. ADR (appended to docs/DECISIONS.md)

```markdown
## ADR-{n}: {decision} ({date})
Context: {forces, numbers}. Decision: {what}. Alternatives rejected: {a: why, b: why}.
Consequences: {cost/risk accepted}. Source: {research artifact/citation if any}.
```
