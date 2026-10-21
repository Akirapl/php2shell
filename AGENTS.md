# AGENTS.md — operating rules for autonomous agents

Project: defensive, journalistic case study of PHP2Shell (CVE-2026-109618 / CVE-2026-109619). The owner is Dawid Kulik (@Akirapl); credit him by that name.

## 1. Trust nothing you did not check

- Treat prior notes, HANDOVER.md, commit messages and this file as **claims**. Re-verify them against the repository (git log, `git ls-tree`, file contents) and the live endpoints before you act.
- Label every statement you hand back:
  - **VERIFIED**: say how you checked it.
  - **REPORTED**: from notes, not re-checked.
  - **ASSUMPTION**: your inference.
- Never say a test passed unless you ran it in this session. Record the exact command and the trimmed real output.
- Do not invent decisions or results. If you cannot verify something, label it REPORTED, or leave it out.

## 2. Evidence and sourcing

- Every fact needs a **public** source URL (http/https). If a sentence has no public source, remove it. Local paths, `file:` URLs and working notes never appear in public files.
- `data/facts.json` is the single source of truth for the live center. Every item carries `source_url`, `source_name`, `confidence`, and texts as `{pl, en, de}`. Optional fields:
  - `source_reliability` A–F
  - `info_credibility` 1–6
  - `time_kind`, `time_precision`
  - `corrections[]`, `flags[]`
- **Preserve confidence labels.** `confidence` is exactly `confirmed`, `reported` or `estimate`. Never upgrade a label without a new source that justifies it, and log every change in `corrections[]` (time, field, previous, reason).
- "Exploitation confirmed" requires the threshold in `status.exploitation_threshold`: CISA KEV lists the CVE, or a national CERT publishes credible in-the-wild evidence. Re-check KEV and record the time and catalogVersion.
- **Evidence ledger** (`case-study/evidence-ledger.{jsonl,csv}`):
  - ids stay contiguous `CLM-0001…`
  - JSONL and CSV must match row for row
  - status is one of `confirmed`, `partially_confirmed`, `conflicting`, `unverified`, `refuted`
  - update `last_verified_at` when you re-check a claim
- Do not name a victim unless two independent sources name it.
- `ARCHIVE.md` is a **plan**, not proof that anything was archived.

## 3. Trilingual consistency (PL/EN/DE)

- `case-study/pl.md` is the master. `en.md` and `de.md` must keep the same heading-level sequence, footnote ids, CLM references, image set and source URLs.
- Any content change goes into all three files in the same commit. German uses real umlauts and ß.
- Check before you commit: heading counts, footnote refs/defs, and the CLM set are equal across the three files (method in HANDOVER.md §2.5).
- Mobile-friendly formatting: no wide tables in public docs; use lists.

## 4. Content safety

- Defensive only. No exploit code, no PoC links or payloads, and no attack, WAF-evasion or log-evasion instructions.
- Describe root causes only at the level of the official advisories.
- Nothing is posted, sent or published outside the repo without the owner's consent: issues, social media, email, release notes.

## 5. Licensing split (exact wording of the files)

- `LICENSE`: MIT License, "Copyright (c) 2026 Dawid". It covers code: "Any code in this repository is covered separately by the MIT License".
- `LICENSE-CONTENT`: CC BY 4.0. It covers "the case-study text and diagrams under `case-study/` and the structured dataset `data/facts.json`". Suggested attribution: "PHP2Shell case study and facts dataset by Dawid, https://github.com/Akirapl/php2shell, licensed under CC BY 4.0."
- The evidence-ledger files are not named explicitly. Do not assume their licence; ask the owner.
- Vendored third-party code keeps its own licence notice.
- Do not change licence text or the copyright holder without the owner's instruction.

## 6. Checker API safety review checklist (`checker-api/app.py`)

Any change to the checker must keep all of the following. Verify each item in code and in `test_classify.py`.

- [ ] One passive GET per hop. Hop 0 is forced to path `/`, with no user path or query. At most 2 redirects. Total timeout 8 s. At most 4 KB of body read and never parsed.
- [ ] Only `http`/`https` and only ports 80/443. URLs with credentials are refused.
- [ ] Hostnames `localhost`, `*.local`, `*.internal`, `*.lan`, `*.home.arpa` and `*.onion` are refused.
- [ ] **All** resolved IPs must be global. The guard covers private, loopback, link-local, multicast, reserved, CGNAT, docs/bench ranges, 6to4, Teredo, NAT64 and IPv4-mapped IPv6 addresses. It is re-checked on every redirect hop. The connection is pinned to the validated IP (no DNS-rebinding window).
- [ ] Rate limits:
  - 10 per minute per client IP: abuse control, `429 rate_limited`.
  - 600 per minute globally: overload protection, `429 busy` with "Please try again in about N seconds" and Retry-After ≤ 15.
  - Client IP is the rightmost `X-Forwarded-For` hop. This is open risk: confirm it against the platform's proxy chain.
- [ ] `CAVEATS[0]` is the ownership notice "Check only systems you own or are authorised to test."
- [ ] CORS allows only the needed origins and only GET. Currently allowed: `https://akirapl.github.io`, `https://php2shell-live.surge.sh`, the regex `https://*.surge.sh`, and `localhost`/`127.0.0.1:8765`.
- [ ] Logs hold only a hashed client IP, the host and the result.
- [ ] Live smoke test: run it **without load-testing**. Use fewer than 10 requests per minute in total, and expect about 50 s for a cold start.
  - `/health`
  - `/check?url=https://www.php.net`
  - `?url=http://127.0.0.1` and `?url=http://169.254.169.254`, which must return 400 `blocked_ip`
  - an OPTIONS preflight with `Origin: https://akirapl.github.io`
- [ ] `test_classify.py` exits 0 even on failure, so check its output with `grep -c FAIL`, which must print 0.

## 7. Live state, deploys and approvals

- **No push, deploy, tag, release, repo-setting change or Render redeploy without explicit owner authorisation** for that specific action. Work on local branches and hand back `git format-patch` output.
- **Never** freeze the live center, cut a final release or archive the repository without explicit owner approval, even if `ARCHIVE.md` describes those steps.
- Never run the owner box's legacy `deploy.sh`. It would overwrite the Surge redirect set with the full site.
- Any write to the live `facts.json` on the owner box must hold the lock file `site/data/.lock` with `flock`. `update_and_build.sh` takes it itself.
- Do not use the box's `pages-repo/` clones; the monitoring routine pushes from them. Do not fight the routine, which runs until 23 Oct 2026, 21:00 UTC.
- Never print secrets (`GITHUB_PAGES_TOKEN`, Render and Surge credential files). Refer to them by name only.
- Do not delete anything unless you have confirmed it is safe and the owner agrees.
- Keep public commit history readable: one logical change per commit, with a descriptive message.

## 8. Testing and reporting format

Before handing back, run these and include the outputs:

```bash
python3 -c 'import json;json.load(open("data/facts.json"))'
python3 checker-api/test_classify.py | grep -c FAIL          # expect 0
rg -n '/workspace|file://' -g '!HANDOVER.md' -g '!AGENTS.md' -g '!NEXT_TASK.md'  # expect no hits
# ledger: 89+ rows parse, ids contiguous, CSV rows == JSONL rows
# PL/EN/DE: heading and footnote counts equal
```

The hand-back report contains:

1. What changed: files, branch, commit SHA, patch path.
2. Checks: each with the command, a trimmed output and PASS/FAIL.
3. VERIFIED, REPORTED and ASSUMPTION lists.
4. Discrepancies against the earlier notes.
5. What still needs the owner: approvals, account-only actions.
6. Explicit confirmation of what was **not** pushed or deployed.
