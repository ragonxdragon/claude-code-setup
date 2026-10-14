---
type: Convention
title: Prompt Template Library
description: Fill-in-the-blank prompts for orchestration, review and verification, research, product and docs, and ops hygiene
tags: [template, prompts, orchestration, review, research]
timestamp: 2026-10-13
---

# Prompt Template Library

Every template below was distilled from prompts that worked well in real sessions. They are fill-in-the-blank; {braces} mark the variables. The most-used ones are promoted to skills in this setup (orchestrate-track, converge-audit, vendor-sweep, handoff, audit-wave, runner-setup); the rest are kept here to paste.

The principle behind them: **the repository docs are the prompt; your messages are clock signals.** Terse steering works when standing artifacts carry the spec, and fails exactly where they do not: cold sessions, missing plan files, destructive operations on ambiguous referents. So use templates for launches and anything destructive, and one-liners for everything else.

---

## A. Orchestration

### A1. Track or wave orchestrator boot

Rendered from live docs by the orchestrate-track skill; shown here for reference.

```text
You are the ORCHESTRATOR for TRACK {N} of the {project} build. Up to {K} other sessions are running
the OTHER tracks in this same repo AT THE SAME TIME. You do NOT write feature code yourself:
dispatch one background subagent per work package, review at a checkpoint, then merge.

READ FIRST (in order):
0. Project memory {MEMORY.md path} (load: {rule names})
1. {plans-dir}/_PARALLEL_TRACKS.md - YOUR queue, barriers, surface ownership, migration block,
   operating rules. This is your playbook.
2. _STATUS.md - current state; confirm what other tracks have merged.
3. _BUILD_ORDER.md - dependencies + SEC-GATE definitions.
4. {plan files}

TRACK RULES (binding): work the queue top-to-bottom; barrier items verified ON MAIN via git log,
never from memory; touch ONLY your owned surface - STOP and flag foreign files; migrations ONLY
from block {NN0-NN9}; one WP per background subagent, own worktree, branch track{N}/{plan-name};
ONE WORKTREE PER LIVE AGENT - never two agents in one tree; never commit to main; before ANY git
write run git status and WAIT on a foreign MERGE_HEAD; git commit always with explicit pathspecs;
union-merge shared files keeping BOTH sides; explicit -m on merge commits (never --no-edit).

PIPELINE (every WP, no shortcuts): TDD -> domain review -> simplify -> code review ->
false-positive check -> FULL security battery with REAL tools ({exact scanner invocation + env})
-> perf review -> FIX EVERY FLAG (HIGH down to nit; "documented" or "deferred" does not count as
fixed; only confirmed false positives may be skipped; pre-existing findings in touched files are
IN scope) -> verify end-to-end -> doc sync -> verification before completion (paste passing output).

CIRCUIT BREAKER: if a WP's error count is not decreasing after 2 fix attempts, stop it and escalate.
BUDGET: before dispatching heavy WPs, check proximity to session/weekly limit resets; stagger.
AUTO-RESUME: if a task notification reports an agent died on an API/limit error, resume it yourself
via SendMessage once, without waiting for me.

CHECKPOINT each WP: review diff (lead with net diffstat), assert SEC-GATEs, merge, tick own
_STATUS.md rows only, prune the worktree, run the doc-drift pass after any doc-bearing WP AND
APPLY its findings. Post a one-line status after every checkpoint without being asked.
STOP when the queue drains or every item waits on a barrier - report which and why, and end with
SAFE-TO-CLOSE: yes/no.
```

### A2. Single work-package dispatch brief

```text
You are the subagent for WP {n} ({name}). Worktree {path}, branch track{T}/{plan}. Plan: {plan file}.
Surface: touch ONLY {owned paths}; anything else: flag, do not edit. Migration block: {decade}.
Pipeline: run {pipeline doc} section {s} in full - no shortcuts. Fix every flag; never defer.
Commits: granular type(scope), ASCII subject, no AI attribution, explicit pathspecs, commit
incrementally (the network can drop). Never touch _STATUS.md (orchestrator-owned).
REPORT FORMAT (mandatory): 1 Diff summary table (commit -> files -> why) 2 Checkbox deltas
3 Gate table with pasted evidence 4 Review-pipeline notes incl. non-applicable skills and why
5 Flags found AND fixed 6 Flagged hand-offs (outside surface: flag, don't edit) 7 Deferred-not-
dropped seams 8 Migration numbers used 9 git log --oneline main..HEAD 10 STATUS: DONE|BLOCKED.
If BLOCKED: stop with zero edits and propose 2 unblock paths.
```

### A3. Execute a deferred or approved plan (riskiest unknown first)

```text
Execute the plan in {PLAN_PATH}: {one-line goal}.
Context already done (do NOT redo): {shipped pieces with file paths}.
CRITICAL, do this FIRST: {the one unknown that can invalidate the whole approach}.
Prove it in isolation with {minimal throwaway probe}. If it fails, STOP and report back; the rest
is moot. Only after it passes, do the rest: {steps}.
Budget awareness: {cost tradeoff to call out before committing}.
Verify each stage actually works ({commands}) rather than assuming.
Commit conventions per repo; confirm before pushing to {main}.
```

### A4. Cross-session sync brief or barrier broadcast

```text
Sync first: main is at {SHA}. Rebase/verify before continuing.
WHAT LANDED: {decisions/commits with SHAs and paths}
WHAT THIS MEANS FOR YOUR WORK: {keep/change/drop per task}
MERGE NOTE: {files that diverged, expected conflict regions}
SCOPE GUARD: only {X, Y} are live work. Do NOT touch {Z} (owned by {other}). {WP-N} is DONE on
main - verify-only, do not redo.
```

### A5. Cross-session incident notice

```text
Cross-session notice from {sender} - action needed on {topic}.
What happened (root cause): {...}
Your files affected: {list}
Critical facts: {nothing lost? history rewritten? unreviewed code on main?}
What you need to do: 1... 2...
Full write-ups: {commits/docs}
Fix on my side: {behavior change}
```

### A6. Resume after an interruption (replaces a bare "continue")

```text
Resume after the interruption. Before continuing: (1) git status in every active worktree; report
anything unstaged/uncommitted. (2) Check every background agent's last state; re-dispatch any that
died mid-task. (3) Re-state any question I never answered. (4) Re-run the last verify command.
Then continue from the plan checklist. End with: work lost yes/no.
```

### A7. Status query (replaces "is it done" polling)

```text
From _STATUS.md and _PARALLEL_TRACKS.md only (no fresh audit): which tracks are done, stalled,
in-flight, almost done; what share of the current release is not yet built; what the current waves
complete when done. One table. End with SAFE-TO-CLOSE per session: yes/no.
```

### A8. Generate a prompt for another session

```text
Generate the full orchestrator prompt for a NEW session to run {plan/wave} in parallel with
{current scope}. Use template A1. Verify dependency independence and file-surface disjointness
against _BUILD_ORDER.md before including each WP; reserve non-colliding migration numbers.
Output one paste-ready block.
```

### A9. Promote an idea to a plan or track

```text
Capture this product goal verbatim: {run-on allowed}.
Decompose into requirements; write {plans-dir}/{date}-{name}.md (TDD tasks, DECISION blocks,
migration block from a free decade, SEC-GATE mapping); register it as its own track/queue row in
_PARALLEL_TRACKS.md with barriers. Do not start execution until I confirm.
```

---

## B. Review and verification

### B1. Converge-loop audit (canonized as the converge-audit skill)

```text
Audit {scope} against {source}. First enumerate the sources/files/links and REPORT THE COUNT, then
check each off. Verify every claim against the source (file/URL/raw code), never from model memory.
Report findings; then loop: re-run the full pass until a pass produces ZERO new findings. Check for
accuracy and hallucinations. Then fix everything found and run the doc-drift pass.
```

### B2. Review battery, fix everything

```text
Run the full review battery on {scope}: simplicity + FULL security battery (every installed
security skill - emit a per-skill coverage table so I can see nothing was skipped) + performance +
correctness. {language-specific reviewers as applicable}. Check every finding for false positives.
Fix every true positive no matter how small - "documented"/"tracked as follow-up" does not count as
fixed. Re-run until clean. Then add hooks/tests/memory so this class cannot recur, and update docs.
```

### B3. Doc-drift audit, fix, and verify in ONE dispatch

```text
Run a doc-drift audit over {scope}. For every finding: classify DRIFT (doc now false: file:line +
exact fix) vs GAP (doc silent); fix it; then re-verify your own fix (grep the exact line). Output a
per-finding table: finding / fix commit / verified-at line. End with a "Looks current (checked,
matched)" list. Zero residuals - a residual means you did not finish.
```

### B4. Coverage-checklist audit

```text
Audit plans/docs/code against the checklist at {file path - save pastes to artifacts/reference/
first, then reference the path}. For each item: COVERED (where), PARTIAL (gap), MISSING. Add every
MISSING/PARTIAL to the right plan/phase with model + skills assigned. Loop until no new findings.
Then run the doc-drift pass.
```

### B5. Parallel matrix audit

```text
Fan out {N} parallel subagents, each auditing {slice} against {source of truth}. Read-only first
pass. Report per item: `{file}.{key}: current="..." issue: ... suggest="..."` plus per-file totals
and cross-file patterns. Then ONE fix pass applying all confirmed items; then re-audit changed
items only. One worktree per agent if any writes occur.
```

### B6. Repository-wide standards audit

```text
Audit the entire codebase for {hardcoded values / single source of truth and DRY /
over-engineering / perf / a11y}. Partition by area across parallel subagents; findings as
structured JSON (what / replacement / locations / severity) with coverage notes naming what was
checked and deliberately not flagged. Then partitioned fixer agents (file-cluster ownership,
skip-and-why ledger), gates, doc-drift pass, and a final re-audit agent for a clean/not-clean
verdict. Continue until nothing is left. Nothing deleted unless proven unneeded; future work
needed = write the plan, never defer.
```

### B7. Accuracy and hallucination pass

```text
Double-check {output just produced} for accuracy and hallucinations: every file/line/API claim
verified against the actual tree; every external claim verified against a raw source. List
everything corrected.
```

### B8. Repository-state claim verification

```text
I need to confirm {claim} before {finalizing X}. Verify against current main and answer precisely.
My read: {your hypothesis with the file:line evidence you already have}. Questions: (1)... (2)...
If you believe {alternative}: give the file:line call chain from {entry point} to {sink}.
Answer with file:line evidence, not a summary. Never assert absence without pasting the failing
git log / grep output.
```

---

## C. Research

### C1. Deep research wave

```text
Do deep research on {sources} for {goal}. Look for algorithms, practices, and tested code that is
BETTER than what we do here. Use subagents with the right model per task. Read every source RAW
(curl / gh api raw - never summarized fetches). Each subagent returns: current-state summary +
prioritized findings table (Issue | Current | Recommended + source | Why better | Effort | Risk),
written to a FILE with a 10-line inline summary. Then YOU judge which findings beat our current
code - do not just relay.
```

### C2. Research, then apply (two stages)

```text
Apply verified research findings ({date}, {artifact path}, read it first) to {targets}.
FINDING 1 - {name}: {data-dense claims with exact rates/limits/quotes}. Lands in {module}.
FINDING 2 - {name}: CRITICAL: {the finding that breaks an assumption}; options (a)/(b)/(c). Mark
DECISION-NEEDED with the cost data attached.
Enforce in code AND record in docs/DECISIONS.md. Match repo conventions. Add an ADR. Run tests;
fix all errors. No code changes to shipped surfaces without a plan doc.
```

### C3. Vendor sweep (canonized as the vendor-sweep skill)

```text
Vendor-sweep {org-or-repo URLs}. Enumerate every repo; license-check each at a pinned SHA; vendor
VERBATIM (headers: SOURCE/REPO FILE/COMMIT/LICENSE/IMPROVES) everything relevant to current and
future build plans. No license = inspiration only, zero code copied. Append full license texts to
LICENSES.md. Open EVERY directory; record not-found gaps explicitly so no re-sweep is needed.
Write FINDINGS-{name}.md. Nothing committed. Then a second agent byte-verifies a weighted sample
and the license claims. Be accurate; do not hallucinate.
```

### C4. Gap analysis of external resources

```text
Read every link in {list} with subagents - raw content, no summaries. For each return JSON:
{"name","url","whatItIs","usableHere":"yes|no|maybe","weAlreadyHave":"yes|no|partial",
"gap":"valuable|nice|skip","note"}. We judge relevance together afterward.
```

### C5. Competitive benchmark

```text
Deep research the top {N} {category} known for {dimension}. What is our gap from them, what do
they have, what could we do better, what should we adopt so users get {outcome}. Keep refuted
claims in the report with a note on how each could still be implemented. Add it all to {plan}.
```

### C6. Compliance or legal research

```text
Research: is {feature/behavior} compliant with {regulation}? Must {control} be always on, or may it
be gated on {toggle/geo}? Cite the article/guidance, state the obligation type (provider vs
deployer), then implement the compliant behavior and record decision + citation in _STATUS.md and
docs/compliance.md. Verify against current sources, not memory.
```

---

## D. Product and docs

### D1. Product kickoff with a conflict check

```text
New product exploration: {name, one line}.
STEP 0 - CONFLICTS: grep the company docs + all plan docs for prior decisions about this product
or space; list every conflict with locked decisions BEFORE brainstorming.
Relationship to the existing portfolio: {which products it shares principles with}.
Tiers: {free/individual/team/pro}; moat = {what}.
Deep research: competitors, pricing, top complaints, where large incumbents are weak, monetization.
Output: versioned roadmap with infrastructure gates, feature inventory (table stakes vs
differentiator vs moat), doc decomposition plan. Ask me questions if you need to.
```

### D2. Vision intake (route a run-on vision through structure)

```text
Restate my goal as: users/machines in scope; the decision the system makes automatically; the
optimization target ({speed/cost/battery}); the constraints. Ask me max 3 questions. Then produce
the PRD and plan skeleton. My goal, verbatim: {paste run-on sentence}
```

### D3. Troubleshooting guide (FMEA style)

```text
Create a troubleshooting guide for all plausible issues with {device/system}. Audit code,
{indicators/telemetry}, hardware interfaces. For each failure mode: the tell/diagnostic, fix,
prevention, expected time to detect, likelihood/risk (S-O-D/RPN if warranted). Physical context:
{power topology, network topology, environment}. Recognized industry practice throughout.
```

### D4. Cross-repository plan re-base

```text
Re-base plan {file} into {target repo}. This is a PORT, not a re-author: carry task content onto
the target stack and EXPLICITLY list every stack correction (platform, credential store, UI
surface, CI). Land on a feature branch (NOT main), append an ADR, update ROADMAP/CHANGELOG, output
an "Owner decisions needed" list, and flag source-repo docs that now need supersession notes.
```

### D5. Legacy parity audit

```text
Read {legacy doc/README}. Build a feature-parity inventory: every legacy feature keep/drop/modify
with a one-line reason. Non-negotiables kept exactly as-is: {list}. Flag anything that runs counter
to current goals for MY decision instead of silently dropping it. Fold keeps into {plan}.
```

---

## E. Ops and hygiene

### E1. Bug report minimum (never go below this)

```text
BUG: {surface}. WHAT HAPPENS: {paste exact error text or last log lines}. WHEN: {trigger}.
LOG: {absolute path - READ all of it; it may loop, so dedupe and diagnose from the LAST distinct
iteration}. Expected: {one line}. Find the root cause BEFORE any rebuild - name the failing line
first. Fix, rebuild once, verify by LAUNCHING the app (not just building). End with the absolute
path of any artifact produced.
```

### E2. Housekeeping close-out

```text
Close out: commit uncommitted work (explicit paths, granular commits), delete backup/scratch files
(git is the backup), prune merged worktrees and stale branches (verify merged first), confirm main
has everything, verify the changelog hook fired (fix + re-run if not), update memory if needed.
Report SHAs. SAFE-TO-CLOSE: yes/no.
```

### E3. CI or ops cost investigation

```text
{Resource} budget problem: {symptom with numbers}. Compare (a) move it local vs (b) make it more
efficient, with concrete savings estimates. Implement the winner. Document the final setup in
docs/ so it survives this session.
```

### E4. Runner setup (canonized as the runner-setup skill)

```text
Install a GitHub Actions self-hosted runner for {repo}: mint the registration token via gh api
(NEVER paste tokens into chat), register, add to the runner startup script at {path} alongside the
others, add runs-on to all workflows, verify a job picks it up.
```

### E5. Repository bootstrap to a golden standard

```text
Bring this repo to parity with {golden repo}: CLAUDE.md map (template 01), commit-format +
changelog-sync git hooks, plans/docs decomposition, CI conventions (least-privilege permissions,
injection-safe inputs, pinned actions, concurrency, timeouts), review battery wiring,
.gitleaks.toml with a justified allowlist. Report copied / adapted / deliberately not ported.
```

### E6. Recurring automation request (a hook, not a memory note)

```text
Make it automatic: after {trigger}, {action}. Wire it as a hook in settings.json, not a memory
note. Hooks receive the tool input as JSON on stdin; filter inside the script rather than relying
on matcher tricks. Test it with a synthetic payload (add a case to hooks/hooks_selftest.py) before
calling it done.
```

---

## F. Micro-habits (one-line upgrades with a large payoff)

1. **Paste to a file.** Any paste over about 30 lines goes to `artifacts/reference/{name}.md` first, and the message references the path. Large pastes get re-billed every time compaction carries them forward.
2. **"Do this:" plus a paste-back.** Selecting Claude's own offer verbatim is the cheapest unambiguous instruction.
3. **Name referents on destructive operations.** A rewrite or delete names the SHA or path explicitly ("rewrite HEAD commit c3f12ab", not "rewrite your commit").
4. **Logs by path, never pasted.** "Read the whole log at {path}; it loops" beats 200 pasted lines and gets a better diagnosis.
5. **Number multi-part asks.** Run-on requests carry two to four asks, and agents drop the second clause. Number them (1) (2) (3) and ask for a todo item per clause.
6. **Typos are fine.** They rarely cause failures; under-specified REFERENTS do. Spend keystrokes on nouns, not spelling.
