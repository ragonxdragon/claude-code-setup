---
last_verified: 2026-10-13
name: converge-audit
description: "Loop an audit until a full pass yields zero new findings, verifying every claim against raw sources, never model memory. Use when the user says 'audit X against Y', 'loop until no new findings', 'converge audit', 'check for accuracy and hallucinations', or any audit-against-source request."
domains:
  - review
  - audit
  - docs
metadata:
  trigger: audit {scope} against {source}; convergence loop until zero new findings
---

# Converge Audit

Audit `{scope}` against `{source}` and LOOP until a complete pass produces zero new findings.

## Rules (all built in, none optional)

1. **Enumerate first.** List every source, file, or link in `{source}` and REPORT THE COUNT before checking anything. Then check each one off. The count is the completeness contract.
2. **Verify against sources, not memory.** Check every claim against the actual file, URL, or raw code. Read raw (`curl`, `gh api ... --jq`, a raw endpoint); never rely on a summarizing fetch for anything accuracy- or security-sensitive, because summaries drop the lines that matter. Never assert from model memory. If a source is unreachable, record "unverifiable: {reason}"; never guess.
3. **Never assert absence without evidence.** An "X is missing" finding pastes the grep or git log output that proves it.
4. **Report, then loop.** After fixing, re-run the FULL pass (not only the changed items) until one complete pass yields ZERO new findings. Each pass reports its number, the items checked, and the count of new findings.
5. **Hallucination check.** Every file, line, or API claim in the audit's own output is verified against the tree before the pass counts as complete.
6. **Fix everything found** in the same pass, never deferred. Only confirmed false positives may be skipped, each named with its verdict.
7. **Doc sync.** Run a doc-drift pass at convergence and apply its findings.

## Loop shape

```text
pass = 1
enumerate sources -> report count N
while true:
    check all N items against raw sources
    report: pass {p}: {N} checked, {k} new findings
    if k == 0: break
    fix all k (false-positive check first); re-verify each fix (grep the exact line)
    pass += 1
run the doc-drift pass; apply findings
```

## Anti-patterns this replaces

- Single-pass audits that miss residuals. When audit, fix, and verify run as separate dispatches, each extra pass pays the full context cost again; here they are ONE loop.
- "Verification" of source code through summarized fetches.
- "Looks complete" without an enumerated count.

## Report

Per pass: items checked, new findings, fixes with the verified file:line. Final: passes to converge, total findings, total fixed, false-positive skips named, and a "looks current (checked, matched)" list.
