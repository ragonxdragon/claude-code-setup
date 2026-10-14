---
last_verified: 2026-10-13
name: vendor-sweep
description: "Vendor code from external repos verbatim with license checks, provenance headers, and pass-one completeness rules. Use when the user says 'vendor sweep', 'vendor this repo/org', 'pull in code from these repos with licenses', or any bulk code-vendoring request."
domains:
  - engineering
  - licensing
  - research
metadata:
  trigger: vendor-sweep {org-or-repo URLs}; bulk vendoring external code with provenance
---

# Vendor Sweep

Bulk vendoring with the pass-one completeness rules that make a re-sweep unnecessary. A second sweep costs far more than a complete first one, because it has to re-read everything the first pass already opened.

## Inputs

`{org-or-repo URLs}`, plus the current and future build plans. The plans define what "relevant" means, so read them first.

## Phase 1: Enumerate

1. List EVERY repository in scope (an org listing through `gh api`, not memory) and report the count.
2. Pin a SHA per repository (the default branch HEAD at sweep time). Every read happens at that SHA.

## Phase 2: License gate (per repository, before any copying)

3. Read the license file RAW at the pinned SHA (`gh api repos/{o}/{r}/contents/LICENSE?ref={sha}` or the raw URL), never through a summarizing fetch.
4. Permissive (MIT, BSD, Apache-2.0, zlib, ISC): vendoring allowed. Copyleft (GPL, AGPL, LGPL): BANNED; inspiration only, zero code copied, and verify that any replacement code does not match the copyleft original. No license found: inspiration only, zero code copied, recorded as such.

## Phase 3: Vendor verbatim (pass-one completeness rules)

5. **Open EVERY directory** in the repository tree: no sampling, no "this looks like the interesting directory". Record explicit not-found gaps ("checked {dir}, nothing relevant because {reason}") so no re-sweep is ever needed.
6. Copy relevant files VERBATIM (no reformatting, no trimming) with a provenance header on each:

   ```text
   // SOURCE: {repo URL}
   // REPO FILE: {path in source repo}
   // COMMIT: {pinned SHA}
   // LICENSE: {SPDX id}
   // IMPROVES: {what in our codebase this is better than / feeds}
   ```

7. Append the FULL license text of every vendored repository to `LICENSES.md`.

## Phase 4: Findings file

8. Write `FINDINGS-{cluster}.md`: per repository, what was taken (file list), what was deliberately not taken and why, the not-found gaps from rule 5, and the license verdicts.

## Phase 5: Verify (separate agent)

9. The sweep agent COMMITS NOTHING.
10. A second, independent agent byte-verifies a weighted sample of vendored files against the pinned-SHA raw source and re-checks every license claim. Any discrepancy makes the sweep agent's whole report untrusted: re-verify everything it touched.

## Hard rules

- Accuracy over speed: never invent file contents or license terms. Every claim traces to a raw read at the pinned SHA.
- No license means no code, ever, however useful.
- Provenance headers are not optional; a vendored file without one is a finding.
