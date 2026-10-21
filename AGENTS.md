# AGENTS.md — durable instructions for autonomous agents

Project: defensive, journalistic case study and live center for PHP2Shell (CVE-2026-109618 / CVE-2026-109619).
Owner: **Dawid Kulik** (`@Akirapl`); credit him by that name. Start with `HANDOVER.md` §0, then `NEXT_TASK.md`.

## 1. How to work

- **Inspect before you modify.** Read the relevant files, `git log`, and run `bash ops/verify_handover.sh` before changing anything.
- **Work autonomously** through implementation *and* verification. Do not stop at the first error: diagnose it, fix the cause, re-run.
- **Run real tests and report actual results** (exact command, trimmed real output, PASS/FAIL). Never claim a test passed that you did not run in this session.
- **Separate facts from assumptions.** Tag hand-back statements **[V]** verified (how), **[C]** read from config/notes, **[U]** unverified assumption. Prior notes, HANDOVER.md and commit messages are claims until you re-check them.
- **Preserve functionality and evidence provenance.** No unrelated refactors. Do not drop sources, confidence labels, ledger rows, corrections history or operational detail (including real box paths in the operational docs).
- **Stop only** when genuinely blocked (missing files/credentials/access) or before a destructive or irreversible operation (§7). Then report exactly what is missing and the owner step that unblocks it.
- One logical change per commit, descriptive message. Bot commits use author `Nygus (bot for @Akirapl) <akira3179082@gmail.com>`.

## 2. Evidence and sourcing invariants

- Every public claim needs a **public** http(s) source. Local paths, `file:` URLs and working notes never appear in public content.
  Exception, decided by the owner: the operational docs `HANDOVER.md`, `AGENTS.md`, `NEXT_TASK.md` and `ops/` may name box paths; `ops/checks.py` enforces the rule for everything else.
- `data/facts.json` is the **single source of truth** of the live center. Items carry `source_url`, `source_name`, `confidence`, texts as `{pl,en,de}`;
  optional `source_reliability` (A–F), `info_credibility` (1–6), `time_kind`, `time_precision`, `corrections[]`, `flags[]`.
- **confirmed / reported / estimate** are distinct and exact. Never upgrade a label without a new source; log every change in `corrections[]` (time, field, previous, reason).
- "Exploitation confirmed" only at the threshold in `status.exploitation_threshold.rule`: CISA KEV lists the CVE **or** a national CERT publishes credible in-the-wild evidence. Record KEV check time and catalogVersion.
- Evidence ledger `case-study/evidence-ledger.{jsonl,csv}`: contiguous `CLM-0001…`, JSONL and CSV row-for-row identical, status ∈ {confirmed, partially_confirmed, conflicting, unverified, refuted}, update `last_verified_at` when re-checked.
- Do not name a victim unless two independent sources name it.
- `ARCHIVE.md` is a **plan only**, not proof that anything was archived.
- Working notes (`log.md`, drafts, staging) stay in separate files from public docs and never get committed as public content.

## 3. Trilingual consistency (PL/EN/DE)

- `case-study/pl.md` is the master; `en.md` and `de.md` keep the same heading sequence, footnote ids, CLM references, image set and source URLs. `python3 ops/checks.py --only parity` checks this.
- Content changes go into all three languages in the same commit. German uses real umlauts and ß. facts.json texts need all of pl/en/de.
- Mobile-friendly: card/list layouts, **no wide tables** in public docs or site sections.

## 4. Content safety

- Defensive only: no exploit code, no PoC links or payloads, no attack, WAF-evasion or log-evasion instructions. Root causes only at the level of official advisories.
- Nothing is posted, sent or published outside the repo (issues, social, email, release notes) without the owner's consent.

## 5. Licensing

- `LICENSE` (MIT) covers code; `LICENSE-CONTENT` (CC BY 4.0) covers case-study text, diagrams and `data/facts.json`. Keep code licence separate from content/diagram/dataset licence.
- Both currently read "Copyright (c) 2026 Dawid" without surname; the ledger is not named in LICENSE-CONTENT. Both are **owner decisions** — do not edit licence text or holder unasked.
- Vendored third-party code (Mermaid, Chart.js, both MIT) keeps its own notice.

## 6. Checker API (`checker-api/app.py`) — keep all of these

- Passive, banner-only: one GET per hop, hop 0 forced to `/` (no user path/query), ≤ 2 redirects (each re-validated), 8 s total, ≤ 4 KB body read and never parsed.
- Only http/https, ports 80/443, no URL credentials; refuse `localhost`, `*.local`, `*.internal`, `*.lan`, `*.home.arpa`, `*.onion`.
- All resolved IPs must be global (private, loopback, link-local, multicast, reserved, CGNAT, doc ranges, 6to4, Teredo, NAT64, v4-mapped refused); connection pinned to the validated IP.
- Limits: 10/min per client IP (`429 rate_limited`, the abuse control); 600/min global (`429 busy`, Retry-After ≤ 15). Client IP = rightmost XFF hop (open risk, HANDOVER §10.6).
- `CAVEATS[0]` is the ownership notice "Check only systems you own or are authorised to test."
- CORS: GET only; currently broader than needed (HANDOVER §10.4). Logs: hashed client IP, host, result only.
- Live smoke tests: < 10 requests per minute total, expect a cold start; **never load-test production**.
- Render needs a **Manual Deploy** after checker changes (auto-deploy unreliable); that is an owner action.

## 7. Approvals and things you must not do

- **Without explicit owner approval for that specific action:** no push to `main`/`gh-pages`, no deploy (Render, Surge, Pages), no tag or release, no repo-setting change, no freeze/final release/archive, no history rewrite or force-push, no credential rotation, no deletion of resources.
- **Never** run `/workspace/php-incident/deploy.sh` (overwrites the Surge redirects). Do not run `site/update_and_build.sh` or `publish_pages.sh` to "test" — they publish when the token is set.
- Every write to the box `site/data/facts.json` holds `flock /workspace/php-incident/site/data/.lock`. Do not use `/workspace/php-incident/pages-repo/`. The 30-min routine pushes to main until **2026-10-23 21:00 UTC**: `git fetch && git rebase origin/main` right before any approved push.
- Never print, echo, copy or commit secrets (`GITHUB_PAGES_TOKEN`, `.render-credentials`, `.surge-credentials`). Check existence only (`test -f`, `test -n`).

## 8. Checks before hand-back

```bash
bash ops/verify_handover.sh            # must end with "0 FAIL"; add --live for ≤ 6 read-only GETs
python3 ops/checks.py                  # facts, ledger, parity, paths, secrets
git diff --stat origin/main            # only the files your task needs
```

Hand-back report: what changed (files, branch, SHA or patch path); every check with command, trimmed output and PASS/FAIL;
[V]/[C]/[U] lists; discrepancies against earlier notes; what still needs the owner; explicit statement of what was **not** pushed or deployed.
