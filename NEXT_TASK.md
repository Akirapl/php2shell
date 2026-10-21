# NEXT_TASK — make the checks fail loudly and run them in CI

Priority: high. Doable from a **fresh public clone alone** (no box, no credentials needed to implement and test).
Status: not started (2026-10-21 ~18:55 UTC).

## Why

- `checker-api/test_classify.py` prints `FAIL` but always exits 0 [V HANDOVER §9], so any automation treats a broken checker as green.
- The repo has no CI [V: no `.github/workflows/`]. `ops/checks.py` (facts, ledger, PL/EN/DE parity, local paths, secrets) and the
  checker tests only run when someone remembers to run them. The 30-min routine edits `data/facts.json` on `main` until 2026-10-23 21:00 UTC.
- The bigger gap — the site build pipeline being box-only — needs the owner's files (see "Follow-up" below), so it cannot be the next task for an agent without the box.

## Prerequisites

- `git`, Python ≥ 3.10, network for `pip` (checker deps pinned in `checker-api/requirements.txt`).
- `bash ops/verify_handover.sh` passes on an untouched clone (`0 FAIL`) — run it first and keep the output.

## Steps

1. **test_classify.py exit code.** Count failures and end with `sys.exit(1 if failures else 0)`; keep every existing case and output line format
   (`OK …` / `FAIL …`). Do not change `app.py`. Prove the negative path: temporarily break one expectation, run, see exit 1, revert.
2. **verify script.** In `ops/verify_handover.sh` §3, trust the exit code (keep the `^FAIL` count as a second guard) and update the comment that says it always exits 0.
3. **CI workflow** `.github/workflows/checks.yml`: on `push` and `pull_request` to `main` (+ `workflow_dispatch`); `ubuntu-latest`;
   `actions/checkout@v4` with `fetch-depth: 0`; `actions/setup-python@v5` with Python 3.12; run `bash ops/verify_handover.sh` (no `--live`, no secrets,
   `permissions: contents: read`). The routine's facts.json commits will trigger it — that is the point.
4. **Docs.** Update HANDOVER.md §9 (test exit code) and §7 (CI exists), AGENTS.md §8 if commands change, and add a CHANGELOG entry
   (version number is the owner's choice; write "Unreleased").

## Commands

```bash
git clone https://github.com/Akirapl/php2shell.git /tmp/p2s && cd /tmp/p2s && git checkout -b ci/checks
bash ops/verify_handover.sh                                  # baseline, expect 0 FAIL
# … edit checker-api/test_classify.py, ops/verify_handover.sh, add .github/workflows/checks.yml, docs …
VENV=/tmp/php2shell-verify-venv; cd checker-api && $VENV/bin/python test_classify.py; echo "exit=$?"; cd ..     # expect exit=0, 15 OK
sed -i '0,/"likely_patched"),/s//"likely_vulnerable"),/' checker-api/test_classify.py   # GNU sed: breaks exactly ONE case
cd checker-api && $VENV/bin/python test_classify.py; echo "exit=$?"; cd .. && git checkout checker-api/test_classify.py   # expect exit=1, then revert
$VENV/bin/pip install -q pyyaml && $VENV/bin/python -c 'import yaml;yaml.safe_load(open(".github/workflows/checks.yml"))'   # syntax check
bash ops/verify_handover.sh && python3 ops/checks.py
```

[V 2026-10-21] the `sed` line breaks exactly one case: the current script then prints 1 `FAIL` line and still exits 0.

## Acceptance criteria

1. `python test_classify.py` exits 0 with all 15 `OK` lines on the unmodified tests, and exits 1 when any case fails.
2. `bash ops/verify_handover.sh` ends with `0 FAIL` on the branch; its §3 relies on the exit code.
3. `.github/workflows/checks.yml` parses as YAML, uses only `contents: read`, needs no secrets, and runs `ops/verify_handover.sh`.
4. `python3 ops/checks.py` passes (no local paths outside the allowlist, no secrets).
5. `git diff --stat origin/main` lists only: `checker-api/test_classify.py`, `ops/verify_handover.sh`, `.github/workflows/checks.yml`, `HANDOVER.md`, `AGENTS.md` (if changed), `CHANGELOG.md`. No `app.py` change.
6. Commit author `Nygus (bot for @Akirapl) <akira3179082@gmail.com>`, one commit or a short series with clear messages.

## Verification and delivery

- Fresh-clone re-run: `git clone <your branch or apply the patch> /tmp/verify && cd /tmp/verify && bash ops/verify_handover.sh`.
- Delivery: `git format-patch origin/main` unless the owner has explicitly approved a push for this task.
  Pushing a file under `.github/workflows/` needs a token with **Workflows: write**; `GITHUB_PAGES_TOKEN` is not known to have it [U].
  If a push is rejected for that reason, push nothing else in its place: hand back the patch and say the owner must push it or widen the token.
- After an approved push: the Actions tab shows a green run for the commit (owner or `gh run list` with read access); a later routine facts.json commit also runs green.

## Expected outcome

A failing checker test or a broken facts.json/ledger/translation parity turns `main` red within minutes instead of going unnoticed.

## Follow-up (needs the owner): import the build pipeline

Bring box `site/` generator, `bible/build/` renderer and the Surge redirect builder into the repo (list, sizes and sha256 in
`ops/MISSING_FROM_REPO.md`), parametrising the hard-coded paths (`update_and_build.sh` line 33, `publish_pages.sh` `WORK`,
`sync_bible.py` `../bible` → `case-study/`, `render-mmd.mjs` Mermaid path), never importing `CNAME`, credentials, `.lock`, generated output.
Acceptance: the generated site diffs clean against `origin/gh-pages` except timestamps and `changelog.json`.
Recovery path without the box: the owner runs the tarball command in `ops/MISSING_FROM_REPO.md` and shares the file privately.
Keep the box pipeline authoritative until the routine ends (2026-10-23 21:00 UTC); switching publishing to the repo copy is an owner decision.
