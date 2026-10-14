---
last_verified: 2026-10-13
name: legal-doc-pass
description: "Update a product's legal document set (terms of service, privacy policy, DPA, BAA, marketplace terms) with standard header rules and consistent data-handling wording across documents. Use when the user says 'legal doc pass', 'update the ToS/privacy policy', 'sync the legal docs', or any change touching docs/legal."
domains:
  - legal
  - docs
  - compliance
metadata:
  trigger: updating ToS, Privacy Policy, DPA, BAA, or other docs/legal files
---

# Legal Doc Pass

The recurring update flow for a set of legal drafts, so the rules do not need re-explaining each time. Configure the three settings below in the project's CLAUDE.md or in a `docs/legal/README.md`, and the skill reads them from there.

## Project settings (read these first)

- **Document set and location:** for example `docs/legal/` holding TERMS-OF-SERVICE.md, PRIVACY-POLICY.md, DATA-PROCESSING-AGREEMENT.md, and any sector documents (BAA, GLBA safeguards program, marketplace terms).
- **Governing entity:** the legal entity's exact name and form. Check the company docs; never assert an entity form from memory.
- **Data-posture model:** the product's tiers and what each does with user data (see "Data-posture wording" below). This is the part most likely to drift between documents.

## Header rules (every document, every pass)

1. Every document carries a "not legal advice" header block stating that it was drafted with AI assistance, is NOT legal advice, and must be reviewed by qualified counsel before commercial use. Never remove or soften it; add it where it is missing.
2. Every document carries an effective-date placeholder (`Effective: [DATE - set at launch]`), a version or revision line, and the governing entity's name.
3. Counsel review is a hard gate before commercial launch. A legal doc pass never marks that gate satisfied.

## Data-posture wording (consistent across ALL documents)

The legal text must describe data handling exactly as the product does it, everywhere it is described. Typical tier shapes to model:

- **Local or free tier:** processing happens on the user's device; no user content leaves it.
- **Cloud tier (consumer):** cloud processing is opt-in per subscription; state what is transmitted, how long it is kept, and the user's deletion rights.
- **Business tier:** the DPA governs. Its processor and subprocessor language must name the cloud vendors actually in use; verify against the current architecture docs, not memory.
- Tier names are defined once and used identically in every document; never mix them.

## Procedure

1. Read the product or architecture fact that triggered the pass (plan doc, ADR, or user statement) and identify which documents it touches. A data-flow change usually touches the privacy policy and the DPA together; keep them consistent.
2. Edit every affected document in ONE pass. Cross-document checks:
   - Tier names and data-posture claims are identical across terms, privacy policy, and DPA.
   - Defined terms match across documents (each capitalized term defined once and used identically).
   - A BAA or GLBA document claims only the compliance posture the product actually has. Never upgrade a compliance claim without an architecture citation.
3. Verify every factual claim (what data goes where, which subprocessors) against the current architecture and plan docs. Legal text that asserts a stale architecture is a defect.
4. Update the inventory in `docs/legal/README.md` (document list and gap analysis) if the set changed.
5. Commit granularly as `docs(legal): {what changed}`, with no AI attribution. Run a doc-drift pass afterward.

## Hard rules

- Never delete a legal document or a clause because it "seems unused"; flag it for the user.
- Jurisdiction, arbitration, and liability-cap choices are decisions for the user. Mark them `DECISION-NEEDED` with the options; never pick one silently.
- Use ASCII punctuation in edits (many repositories' hooks reject curly quotes and em dashes).
