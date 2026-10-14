---
description: Audit installed skills against the knowledge index, rebuild routing if stale, and self-test every registered hook
allowed-tools: Bash, Read, Edit
---

Run the drift check script and fix everything it finds:

```bash
cd "$HOME/.claude" && python3 scripts/drift_check.py --fix
```

After reading the output:

1. **If routing was stale:** confirm it was rebuilt and that `python3 scripts/check_routing.py` now passes.

2. **If orphaned skills are found** (installed but not indexed): for each one, pick the concept file under `knowledge/skills/` that matches its domain and add a one-line row to that file's table:

   ```text
   | `skill-name` | `/skill-name` | One-line description |
   ```

   Read the skill's `SKILL.md` (under `~/.claude/skills/<name>/` or its plugin directory) to write an accurate description. If no concept file fits, create one with OKF frontmatter (see `knowledge/conventions/okf-spec.md`). If the skill should stay out of the index on purpose, add its name to `knowledge/drift-skip.txt` instead. Then run `python3 scripts/build_routing.py`.

3. **Run the hook self-test** against the real install, to catch silent wiring breakage:

   ```bash
   python3 "$HOME/.claude/hooks/hooks_selftest.py" --installed
   ```

   Any FAIL line means a registered hook is broken (missing file, crash, timeout, wrong behavior). Fix it before finishing.

4. **Run the remaining validators:** `python3 scripts/validate_okf.py`, `python3 scripts/check_links.py`, and `python3 scripts/frontmatter_audit.py`. Fix every finding.

5. **Report the final status:** "Drift check complete. X global skills, Y plugin skills, Z orphans fixed, routing current, hooks self-test N/N, validators clean."
