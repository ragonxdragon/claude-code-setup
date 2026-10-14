---
last_verified: 2026-10-13
name: runner-setup
description: "Register a GitHub Actions self-hosted runner for a repo using a gh-api-minted token, never pasting tokens into chat. Use when the user says 'set up the runner', 'add a self-hosted runner', 'register this repo on my runner', or 'runner setup for {repo}'."
domains:
  - ci
  - devops
metadata:
  trigger: installing or registering a GitHub Actions self-hosted runner for a repo
---

# Runner Setup

Self-hosted runner registration. The registration token is minted with `gh api` and consumed in the same shell command; it never appears in the conversation, in a file, or in an environment variable that outlives the command.

## Token rules (non-negotiable)

- Mint with `gh api -X POST repos/{owner}/{repo}/actions/runners/registration-token --jq .token` INSIDE the same command that consumes it. Never echo it, never write it to a file, never ask the user to paste one.
- Registration tokens expire after an hour and have one purpose. If registration fails, mint a fresh token; never retry with a value that was logged.
- If `gh auth status` fails, stop and report. Do not fall back to a personal access token in chat.

## Procedure

1. **Preconditions:** `gh auth status` succeeds; the user is an admin on `{repo}`; decide the runners root directory (reuse an existing one if this machine already hosts runners; one runner process serves one repository, so per-repository runners live in sibling directories).
2. **Download or reuse the runner binary:** if `{runners-root}/{repo-slug}/` does not exist, create it, download the current actions-runner release for this OS from GitHub's runner releases page, verify its SHA-256 against the published checksum, and extract it.
3. **Register in a single command so the token never rests.** PowerShell on Windows:

   ```powershell
   $t = gh api -X POST repos/{owner}/{repo}/actions/runners/registration-token --jq .token
   .\config.cmd --url https://github.com/{owner}/{repo} --token $t --name {machine}-{repo-slug} --labels self-hosted,windows,x64 --unattended
   Remove-Variable t
   ```

   Bash on Linux or macOS:

   ```bash
   ./config.sh --url "https://github.com/{owner}/{repo}" \
     --token "$(gh api -X POST "repos/{owner}/{repo}/actions/runners/registration-token" --jq .token)" \
     --name "{machine}-{repo-slug}" --labels "self-hosted,linux,x64" --unattended
   ```

4. **Startup:** make the runner survive reboots. Either install it as a service (`./svc.sh install` on Linux or macOS, `.\svc install` on Windows) or add it to the machine's runner startup script alongside existing entries. Use the repository's CI doc to find which convention applies.
5. **Wire workflows:** set `runs-on: [self-hosted, {os}]` (or the chosen label set) on every workflow meant for this runner. Keep least-privilege `permissions:` blocks and concurrency groups intact.
6. **Verify:** push or dispatch a trivial job; confirm the runner picks it up (`gh run watch`), then confirm it shows Idle under the repository's Settings, Actions, Runners page.
7. **Document:** record the runner name, labels, directory, and startup wiring in the repository's CI doc (for example `docs/ci-and-runner.md`) so the setup outlives the session.

## Known gotchas

- Shell mismatches between the runner's default shell and the scripts a workflow calls (for example WSL bash against Windows paths), and out-of-memory failures on large Node builds (raise the heap with `NODE_OPTIONS`). Copy mitigations from any existing runner doc rather than rediscovering them.
- Do not run local builds of the same workspace while the runner builds it; file locks collide.
- Removal: mint a REMOVE token the same way (`.../actions/runners/remove-token`) and run `config remove --token` with it, under the same never-in-chat rule.
