---
type: Convention
title: Proven Prompt Shapes
description: Ten prompt shapes modeled on the runs that finished with the fewest mistakes, the clean-run checklist, and the anti-patterns that preceded the messiest runs
tags: [template, prompts, high-stakes]
timestamp: 2026-10-13
---

# Proven Prompt Shapes

Different from [07-PROMPT-TEMPLATES.md](07-PROMPT-TEMPLATES.md), the full library: this file holds only shapes modeled on tasks that completed with the fewest mistakes and the least rework. Each entry gives why it worked and a ready-to-fill version. Use these shapes as written when the stakes are high.

What every clean run had in common (a checklist for any prompt you write):

1. Preconditions stated and checked before work starts.
2. A done-work fence ("do NOT redo X").
3. The riskiest unknown goes FIRST, with an explicit STOP condition.
4. Exact file paths, line anchors, and numeric acceptance thresholds.
5. Collision avoidance spelled out (who owns which files, worktree rules).
6. A required report format, so completion is verifiable rather than a feeling.
7. Constraints restated inline (commit format, no AI attribution, model tier).

Mistakes came almost entirely from prompts missing items 1, 3, 4, or 6.

---

## P1. The worktree work-package launch

Why it works: the agent knows what runs beside it, which files it may touch, and what "done" means in numbers. Runs launched this way finished with full test suites green, explicit-path commits, and no collisions with concurrent worktrees.

```text
Implement {PHASE/WP-ID} ({name}) from {plan path}. It is {fresh: 0/N tasks | resuming at task K}.
Dependencies ({list}) are merged and verified.

WHY NOW / PARALLELISM: runs concurrently with {other waves/worktrees and the files they own}.
This WP touches {area} specifically because it avoids those files. Work in your own git worktree/
branch off current main (NOT on main, NOT in any other wave's worktree); stay inside {allowed
paths}. Before committing: git diff --cached and stage explicit paths only - concurrent sessions
share this repo.

SCOPE: {exact deliverables}. Do NOT {exclusions}.

HARD ACCEPTANCE CRITERIA (non-negotiable, CI-enforced): {e.g. color tokens only / every string
through the i18n helper / WCAG 2.2 AA / exact-pinned dependencies / shared constants, no literals}.

PROCESS: subagent-driven per the plan header; TDD ({runner}: {N} tests green now, keep green and
add coverage). After each task: simplify, code review, security + accessibility passes; FIX every
flag. After any status/plan doc edit, run the doc-drift pass.

COMMITS (hook-enforced): type(scope): lowercase subject; types feat|fix|refactor|test|docs|chore|
perf; granular; no AI attribution.

FIRST STEP: read the full plan file, then check whether a worktree/branch for {WP} already exists
(git branch -a | grep -i {slug}) before creating one.
```

## P2. The de-risked plan execution (riskiest unknown first)

Why it works: a deferred plan executed in one pass because the structure ruled out "built everything, then found the premise was wrong".

```text
Execute the plan in {PLAN_PATH}: {one-line goal}.
Context already done (do NOT redo): {shipped pieces, with file paths}.
CRITICAL, do this FIRST - the one unknown that can invalidate the whole approach: {unknown}.
Prove it in isolation with {minimal throwaway probe}. If it fails on {environment}, STOP and
report back; the rest of the plan is moot.
Only after that passes: {remaining steps in order}.
Budget awareness: {the cost tradeoff to surface before committing}.
Verify each stage actually works ({exact commands}) rather than assuming.
Follow repo commit conventions; confirm before pushing to {main}.
```

## P3. The zero-ambiguity precision dispatch

Why it works: exact files, line anchors, and a numeric threshold leave nothing to clarify, so it lands on the first pass.

```text
Do exactly this:
#1 {task}: {N} mechanical edits ({file A} {what}, {file B} {what}, {hook point} before
   {file:line}), then verify with {check} ({numeric threshold}).
#2 {task}: {build/config step with exact flags}; without {precondition} it must return a real
   {error code}, never fabricated output.
Report per item: commit SHA + the verification output pasted.
```

## P4. The data-dense research application

Why it works: findings arrive as numbers and quotes with a named landing module, and the decision that is not the agent's to make is fenced off as DECISION-NEEDED.

```text
Apply verified research findings ({date}, {artifact path} - read it first) to {targets}.
FINDING 1 - {name}: {claims with exact numbers/rate limits/ToS quotes}. Lands in {module/service}.
FINDING 2 - {name}: CRITICAL: {the assumption it breaks}. Options: (a).. (b).. (c). Mark
DECISION-NEEDED with the cost data attached - do not decide for me.
Enforce in code AND record in docs/DECISIONS.md (ADR). Update {docs} where affected.
Negative constraints: {hard prohibitions, verbatim - e.g. "no paid vendor key ever ships in the
free tier"}. Match repo conventions ({examples}). Run tests; fix all errors and warnings.
```

## P5. The autonomous implement and review ping-pong

Why it works: reviewers must prove findings with probes, implementers must fix every flag, and the human is interrupted only for scope. Runs of this shape went for hours without supervision and caught real vulnerabilities.

```text
Author the plan for {feature} ({N} tasks, TDD, each task independently reviewable). After my
approval, execute autonomously: alternate Implement-Task-N and Review-Task-N agents.
Reviewers: verify empirically - write throwaway probes/exploits, run them, delete them; read-only
review does not count. Implementers: fix EVERY flag, then the reviewer re-approves with fresh
probes before the next task starts.
When all tasks pass: run the whole-branch final battery (4 parallel lenses: performance,
simplicity/DRY, correctness, security), triage into fix batches - ONE WORKTREE PER LIVE AGENT -
then re-verify each fix commit, then merge to local main safely.
Only interrupt me for genuine scope decisions. End with: tasks done, commits, gate evidence,
SAFE-TO-CLOSE.
```

## P6. The parallel matrix audit

Why it works: a fixed per-item report format, a read-only first pass, one fix pass, and a targeted re-audit. A localization audit of this shape found over a hundred confirmed defects with no rework and no collisions.

```text
Fan out {N} parallel subagents, each auditing {slice: e.g. 5 locale files} against {source of
truth}. READ-ONLY first pass. Fixed report format per item:
  {file}.{key}: current="..." issue: ... suggest="..."
plus per-file totals and cross-file patterns. Then ONE fix pass applying all confirmed items;
then re-audit only what changed. No agent touches another agent's slice.
```

## P7. The session opener with preconditions

Why it works: the opener makes the new session confirm the prior state with evidence before acting, which makes session continuity a one-line cost.

```text
Read {PLAN_DOC} {section}. Confirm {preconditions: prior phases marked complete - evidence, not
checkboxes} before starting. Load the skills listed in the plan. Model: {tier} - switch if not on
it. Then {single task}. Output to {path}. Stop after {boundary}; do not start {next}.
```

## P8. The LLM judge with jurisdiction and confidence gates

Why it works: the judge has a narrow jurisdiction, defers to deterministic gates, stays silent when unsure, and returns machine-checkable JSON. It had the lowest false-positive rate of any judge design tried; use its skeleton for every LLM-as-judge gate.

```text
You are a fatal {X} reviewer. Judge ONLY the added lines below.
Report a violation ONLY when you are highly confident; when unsure, stay silent.
Do NOT flag {things a deterministic gate owns - name them}. Do NOT flag quoted/example text.
Return ONLY a JSON object: {"violations":[{"file","line","rule","quote"}]}. Empty list means clean.
```

## P9. The secure-architecture research brief

Why it works: a numbered coverage list prevents topic drift, and the security review happens before the research becomes the plan.

```text
We need {component}. This must be secure - security review of the architecture BEFORE the plan
ships. Use deep research. Cover, with current practice and concrete {free-tier} options:
1..{N} {numbered coverage list: custody, authn, rate limiting, streaming, caching, hosting,
standards}. Return a cited report with concrete recommendations and trade-offs, oriented to
{constraint}. Then have the security skills review the research before it becomes the plan.
```

## P10. The defensive history rewrite

Why it works: the backup exists and is verified before anything is rewritten, and the human confirms the exact targets.

```text
Before ANY history rewrite in {repo}: create a full backup bundle (git bundle create
{name}-backup-prewrite.bundle --all), verify it, and state the restore command. Echo the exact
target commits (SHA + first line) and wait for my confirm. Then {rewrite}. After: verify tree
state, run the changelog/doc sync, report what changed.
```

---

## Anti-patterns (the prompts that preceded the messiest runs)

- "Several bugs" plus a long log paste and no instruction: a crash-and-rebuild loop.
- "Fix the remote thing", then hours later "still crashes": a failed-fix cycle with zero diagnostics.
- "Rewrite your commit, it's too long" with no SHA: the wrong commit was rewritten.
- Unfenced audits during a cleanup: a mass-deletion scare, with parked features nearly lost.
- Parallel fix batches dispatched into ONE worktree: a near miss of cross-contaminated commits.
- A URL sent in a separate message after the dispatch: the agent failed mid-run against the wrong repository.
