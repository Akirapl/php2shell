# ops/ — handover and operations tooling

Operational files for maintainers and agents (not part of the published case study). These files may name owner-box
paths on purpose (see HANDOVER.md §10.10); `ops/checks.py` keeps all other files free of local paths.

- `verify_handover.sh` — read-only fresh-clone check: prerequisites, data checks, checker tests + local smoke, missing-file report, optional `--live` (≤ 6 GETs).
- `checks.py` — stdlib checks: `facts`, `ledger`, `parity`, `paths`, `secrets` (`--only a,b`). Exit 1 on any FAIL.
- `env.example` — variable and credential **names** with scopes. Never put values in the repo.
- `MISSING_FROM_REPO.md` — box-only files the build needs (size + sha256) and how the owner can provide them.
- `routines/` — export of the server-side routine (verbatim prompt), disabled cron / GitHub Actions templates, and the uninstalled annex A.2 user timer.
- `casestudy_annex.py` — deterministic annex A.2 generator (`python3 ops/test_casestudy_annex.py`). It only opens or updates branch `auto/casestudy-annex-a2`.
