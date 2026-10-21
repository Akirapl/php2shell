# Handover — php2shell (2026-10-21)

Handover for the next autonomous agent working on this repository.
Snapshot taken 2026-10-21 18:20–18:30 UTC against `main` @ `c23e976` and `gh-pages` @ `59bf473`.

Labels used throughout:

- **VERIFIED**: checked in this session; the command and a trimmed output are given.
- **REPORTED**: taken from the previous agent's notes and not re-checked. Treat it as a lead, not a fact.
- **ASSUMPTION**: my inference. Confirm it before you rely on it.

State moves every 30 minutes while the monitoring routine runs (see "Routine"). Re-run the checks below before you trust any number here.

---

## 1. Exact first action

Re-check that the build pipeline is still missing from the repo, then start NEXT_TASK.md step 1:

```bash
git clone https://github.com/Akirapl/php2shell.git /tmp/p2s && cd /tmp/p2s && git fetch origin gh-pages
git ls-tree -r --name-only origin/main | grep -E '^(site|case-study/build)/' || echo "build source NOT in repo"
```

If it prints `build source NOT in repo`, carry out NEXT_TASK.md. Work on a local branch only and do not push without the owner's approval.

---

## 2. Verified current state

### 2.1 Git (VERIFIED, fresh clone)

```
$ git log --oneline -30        # 27 commits on main, newest first
c23e976 Live update 2026-10-21 18:09 UTC: +2 events, sources 99→101, ...
67d1810 Live update 2026-10-21 17:40 UTC: +1 event, +1 agency response, ...
98f9a53 Add evidence ledger (CLM-IDs) for case-study claims
...
6ab1719 Docs: make the GitHub Pages URL canonical, add "How to cite" and CITATION.cff
5b3a74e Checker: ownership notice, global limit raised to 600/min ...
...
cc27ac0 Initial commit
$ git tag                      -> v1.0
$ git rev-list -n1 v1.0        -> 22112a0 (3rd commit "Add README, changelog and content licence")
$ git branch -a                -> main, origin/main, origin/gh-pages
$ git log --oneline origin/gh-pages | wc -l   -> 15 ; head 59bf473 "Live update 18:09 UTC: site rebuild"
```

`git ls-tree -r --name-only HEAD` on main gives 35 files:

- `.github/ISSUE_TEMPLATE/*` (4 files)
- `.gitignore`
- the top-level docs: ABOUT, ARCHIVE, CHANGELOG, CITATION.cff, CONTRIBUTING, LICENSE, LICENSE-CONTENT, README, SECURITY
- `case-study/{pl,en,de}.md`, `case-study/evidence-ledger.{jsonl,csv}`, `case-study/diagrams/*.{mmd,png}` (4 diagrams)
- `checker-api/{app.py,test_classify.py,requirements.txt,Dockerfile,fly.toml,README.md}`
- `data/facts.json`
- `render.yaml`

The tree has **no build scripts and no PDFs**.

`gh-pages` has 36 files of built output only:

- `index.html`, `info.html`, `methodology.html`, the feeds, `sitemap.xml`, `robots.txt`
- `bible/*.html` plus diagrams, `checker/*`
- `data/{facts,changelog,checker-config}.json`, `data/additions/*.json`
- `vendor/{mermaid,chart.umd}.min.js`, `.nojekyll`, the IndexNow key file

`git diff --stat main origin/gh-pages -- data/facts.json` prints nothing, so the two copies are identical.

### 2.2 Checker unit tests (VERIFIED)

```
$ python3 -m venv venv && . venv/bin/activate && pip install -r checker-api/requirements.txt
  fastapi==0.157.0 pydantic==2.14.1 starlette==1.9.0 uvicorn==0.54.0   (Python 3.13.5)
$ cd checker-api && python3 test_classify.py
OK  {'x-powered-by': 'PHP/8.3.10'} [] -> likely_vulnerable 8.3.10
... (11 classification cases, all OK)
OK  per-client limit: 10 allowed, then rate_limited (Retry-After 60s)
OK  global cap 600/min reached -> busy (Retry-After 15s)
OK  limits: per-client 10/min kept, global raised to 600
OK  ownership notice is the first caveat
exit=0      # 15 OK, 0 FAIL
```

Caveat: the script always exits 0. Grep its output for `FAIL`.

### 2.3 data/facts.json (VERIFIED)

```
$ python3 -c 'import json;json.load(open("data/facts.json"))'   -> parses
meta.last_updated = 2026-10-21T18:12:00Z ; tlp = CLEAR
items: status.sources 4, key_numbers 10, timeline 78, actors 11, versions 6, sapi_risk 4,
       agency_responses 13, sites_offline 16, quotes 13, trivia 10, historical 4,
       open_questions 10, sources 101
```

- **Confidence values:** across all objects that carry `confidence` (182, including `web_share`, `exposure` and `exploitation_data`) the counts are confirmed 135, reported 45, estimate 2. No other values occur.
- **Source URLs:** all 182 have an http(s) `source_url`. All 101 `sources[]` entries have an https `url`. No URL field uses `http://`.
- **Validator:** the box validator `validate.py data/facts.json` prints `Walidacja OK`, exit 0.
- **Local paths:** `rg -n '/workspace|file://'` over the repo before this handover commit had 0 hits. After this commit it matches HANDOVER.md, on purpose; see section 7.

### 2.4 Evidence ledger (VERIFIED)

```
case-study/evidence-ledger.jsonl: 89 lines, all parse; ids unique and contiguous CLM-0001..CLM-0089
status: confirmed 79, partially_confirmed 4, conflicting 2, unverified 1, refuted 3   (= REPORTED numbers)
case-study/evidence-ledger.csv: 90 lines = header + 89 rows; id order identical to JSONL
primary_source_url: 89/89 https ; last_verified_at: 2026-10-21T17:30:00Z for all rows
```

Minor gaps:

- `claim_lang_source` is empty in all 89 rows.
- `label_in_text` is empty for CLM-0027.

### 2.5 PL/EN/DE consistency (VERIFIED)

- pl / en / de lines: 558 / 558 / 558
- headings H1/H2/H3: 1/19/37 in all three
- footnote refs / defs: 172 / 64 in all three
- CLM ids cited: 4, images: 4, in all three

- The heading-level sequence, the footnote-definition ids and the URL sets are identical across the three files.
- There are no undefined, unused or duplicate footnotes.
- No differences were found. Word counts differ only through language (4776/5001/4541).

### 2.6 Live endpoints (VERIFIED, 18:22–18:25 UTC)

```
curl -sI https://akirapl.github.io/php2shell/        -> HTTP/2 200, last-modified 18:09:41 GMT, max-age=600
curl https://akirapl.github.io/                      -> 404 (normal: project site lives under /php2shell/)
live data/facts.json meta.last_updated               -> 2026-10-21T18:12:00Z (= main), sources 101, timeline 78
/bible/en.html 200 · /methodology.html 200 · /info.html 200 · /checker/index.html 200 · /feed.xml 200
/bible/en.pdf 404   (PDFs are not published at all; see 4.2)
robots.txt: "User-agent: * / Allow: /" + sitemap
feed.xml entry <id>s: tag:php2shell-live.surge.sh,2026:...  (permanent IDs, intentional per REPORTED notes)
https://php2shell-live.surge.sh/  -> 200 "live center has moved" page, JS + meta refresh + canonical to Pages
https://php2shell-live.surge.sh/robots.txt -> "Disallow: /"
```

Checker on Render (`https://php2shell-checker.onrender.com`). The first `/health` call took 13.4 s (cold start); later calls took under 1 s.

```
/health                                  -> 200 {"ok":true,"service":"PHP2Shell-Live-Checker","version":"1.0"}
/check?url=https://www.php.net           -> 200 no_php_detected, server BunnyCDN-DE1-1329, 1 hop;
                                            caveats[0] = "Check only systems you own or are authorised to test."
?url=http://127.0.0.1                    -> 400 blocked_ip
?url=http://169.254.169.254              -> 400 blocked_ip
?url=http://[::1]                        -> 400 blocked_ip
?url=http://localhost                    -> 400 blocked_host
?url=https://www.php.net:8443            -> 400 bad_port
?url=file:///etc/passwd                  -> 400 bad_scheme
OPTIONS /check, Origin https://akirapl.github.io -> 200, ACAO https://akirapl.github.io, methods GET, max-age 600
OPTIONS /check, Origin https://evil.example      -> 400, no ACAO
GET response headers include: server: cloudflare, x-render-origin-server: uvicorn
```

I sent 9 requests in total and ran no load test. The deployed code includes the ownership-caveat change (`5b3a74e` or later), but I could not confirm the exact deployed commit. The previous agent reported `6ab1719`.

Exploitation status (VERIFIED 18:2x UTC): the CISA KEV JSON feed (catalogVersion 2026.10.21, 1754 entries) contains neither CVE-2026-109618 nor CVE-2026-109619. `facts.json` has `status.exploitation = "reported"` and `kev_listed: false`.

### 2.7 GitHub API, unauthenticated (VERIFIED)

```
description: "Evidence-based security case studies and structured datasets for human and AI analysis. ..."
homepage: null · topics: [] · default_branch main · archived false · license detected: MIT
open issues/PRs: 0 · stars 0 · forks 0 · pushed_at 2026-10-21T18:09:21Z
releases: v1.0 "v1.0", published 2026-10-21T16:22:03Z, not draft, no assets
GET /repos/Akirapl/php2shell/pages -> 404 unauthenticated (site itself is live, so this is an API visibility issue)
```

---

## 3. Architecture

- **`main` branch (GitHub):** case study (md, diagrams, ledger), `data/facts.json`, checker API source, docs. The routine commits only `data/facts.json` here.
- **`gh-pages` branch (GitHub → Pages):** the built static site at https://akirapl.github.io/php2shell/. Overwritten by every publish.
- **Build pipeline (owner box only):** generates gh-pages from facts.json and the case-study markdown (section 8).
- **Checker API (Render free plan, service `php2shell-checker`):** built from `checker-api/` via `render.yaml` (Docker). The site reads `data/checker-config.json` → `{"api_base":"https://php2shell-checker.onrender.com"}`.
- **Surge (php2shell-live.surge.sh):** the legacy address. It now serves only the "moved" redirect pages (plus feeds and facts.json, REPORTED).
- **`checker-api/fly.toml`:** an alternative Fly.io config, present but not in use (ASSUMPTION).

---

## 4. Known defects, open questions, outstanding tasks

### 4.1 Defects and risks (VERIFIED unless marked)

1. **The build is not reproducible from the repo.** main contains no site generator, template or validator, and no case-study md→html/pdf tooling. Both exist only on the owner's box (section 8). Without the box nobody can rebuild gh-pages. This is the subject of NEXT_TASK.md.
2. **The case-study PDFs are stale and unpublished.**
   - The box PDFs date from 16:16 UTC; the md/html date from 17:07 UTC, after the ledger edits.
   - The PDFs are excluded from publishing (`bible/*.pdf` in the publish ignore list) and are not in the repo, so `/bible/en.pdf` returns 404.
   - The REPORTED claim that "PDFs in repo/gh-pages lag" is therefore moot: they are not in either place.
3. **The v1.0 tag points to `22112a0`, the 3rd commit.** That commit predates CONTRIBUTING, SECURITY, ARCHIVE, the checker, CITATION.cff and the ledger. `CITATION.cff` says `version: v1.0`. Releases have no assets.
4. **The copyright line reads `Copyright (c) 2026 Dawid `** in both LICENSE and LICENSE-CONTENT, with no surname and a trailing space. CITATION.cff credits "Dawid Kulik (@Akirapl)". The owner should decide whether to change it; do not edit it unasked.
5. **The scope of LICENSE-CONTENT does not name the evidence ledger.** It names "case-study text and diagrams under `case-study/`" and `data/facts.json`. The ledger files sit in `case-study/` but are neither text nor diagrams. The README says "text, diagrams and data". Open question for the owner.
6. **The checker docs overstate one guarantee.** The README says "only the root path `/`" and "no other paths". In code, hop 0 is forced to `/`, but redirect hops (max 2) request the `Location` path. Every hop is still re-validated, IP-pinned, limited to ports 80/443 and http(s), and capped at 4 KB.
7. **CORS is broader than needed.** It allows `https://[a-z0-9-]+\.surge\.sh` (any Surge subdomain) and `http://127.0.0.1:8765` / `localhost:8765`. The API is read-only GET, so the impact is low. Consider narrowing it after the Surge redirect period.
8. **Rate-limit keying is unverified.** `_client_ip` takes the rightmost `X-Forwarded-For` hop. Live responses show `server: cloudflare` in front of Render. If that rightmost hop is a proxy address, all users share one per-IP bucket (10/min). This is untested; do not load-test production. Verify by reading Render's logs (owner access) or with a staging service.
9. **test_classify.py always exits 0** (see 2.2).
10. **Ledger metadata gaps** (see 2.4).

### 4.2 Open questions and outstanding tasks (REPORTED unless marked)

- Render auto-deploy did not trigger reliably; a manual "Deploy latest commit" was needed twice. The service is deployed from the public repo URL without a GitHub connection.
- Repo homepage and topics are empty (VERIFIED). The available token lacks Administration:write (403). The owner must set them.
- Zenodo DOI not done. The owner must enable the Zenodo GitHub integration and then publish a new release.
- Google Search Console verification is pending; the owner must supply the meta tag. IndexNow was submitted to Bing.
- `ARCHIVE.md` is a plan (VERIFIED: "These steps are not carried out"). The evidence archive on the box contains 56 local copies with SHA-256 hashes; 21 of 59 URLs are in Wayback.
- The diagram-card opacity fix exists only in the box `template.html`. It was published to gh-pages (VERIFIED: gh-pages commits `3d0b5d9` and `7097202` at 17:50 UTC).
- The GitHub private vulnerability reporting flag is disabled, per SECURITY.md (not re-checked).

---

## 5. Decisions not obvious from the code (REPORTED unless marked)

- **The GitHub Pages URL is canonical.** Surge forces `robots: Disallow` (VERIFIED), so it serves redirects only.
- **Atom `<id>`s keep the `tag:php2shell-live.surge.sh,…` prefix on purpose,** so feed entries keep permanent IDs (VERIFIED present).
- **Exploitation threshold.** The previous agent reported that "confirmed" is used only at the CISA KEV threshold. VERIFIED: `status.exploitation_threshold.rule` in facts.json reads "confirmed only if CISA KEV lists a CVE **or a national CERT publishes credible in-the-wild evidence**". The file is authoritative.
- **Global checker limit of 600/min with a friendly "busy" 429.** The per-IP limit of 10/min is the real abuse control (VERIFIED in code and tests).
- **Mobile-first case study.** Wide tables became lists (CHANGELOG v1.3, VERIFIED).
- **No local or working-draft sources in public text.** CHANGELOG v1.4, VERIFIED.

---

## 6. Routine schedule (REPORTED)

- Routine "PHP2Shell – meldunki" runs every 30 min, 08:00–22:30 Europe/Warsaw (06:00–20:30 UTC while CEST lasts, until 25 Oct).
- Each run edits facts.json and the working log, runs the build, and pushes `data/facts.json` to main and the built site to gh-pages.
- It **ends 23:00 Warsaw on 23 Oct 2026 (21:00 UTC)**. Planned shutdown: closing note, disable the php2shell triggers, delete the routine. The website stays up.
- VERIFIED consistent: main has "Live update" commits at 15:03–18:09 UTC, roughly every 30 min.
- Do not fight the routine. Never push to main or gh-pages while it can run unless the owner approves, and always hold the lock (section 8).

---

## 7. Secrets (names and paths only; never print or echo them)

- `GITHUB_PAGES_TOKEN` (env var): fine-grained token. Per the box script it has Contents read/write on Akirapl/php2shell (REPORTED). It lacks Administration:write. It is used only via an in-memory `http.extraheader`.
- `.render-credentials` (in the box incident root): Render account credentials.
- `.surge-credentials` (in the box incident root): Surge login and token, sourced by `deploy.sh` and the redirect deploy.

Do not copy any of these into the repo, logs, commits, or issue text.

Note on paths: this file intentionally contains owner-box paths (section 8). The repo-wide `rg -n '/workspace|file://'` check will now match HANDOVER.md. The owner should decide before pushing whether HANDOVER.md belongs on public main.

---

## 8. Owner infrastructure (not in repo)

Everything here lives on the owner's box. A successor without box access cannot use it. All entries are VERIFIED by a directory listing unless marked.

**Incident root:** `/workspace/php-incident/`

**`site/` — the build that generates gh-pages:**

- `build.py`, `template.html`, `seo.py`, `info.py`, `methodology.py`, `validate.py`, `sync_bible.py`, `pages_lib.py`
- `update_and_build.sh`, `publish_pages.sh`, `enable_pages.sh`, `README.md`
- `data/facts.json`: byte-identical to main at 18:2x UTC (`cmp`)
- `data/changelog.json`, `data/additions/`, `data/checker-config.json`
- `checker/` (widget: `index.html`, `section.html`, `checker.js`, `checker.css`, `INTEGRATE.md`)
- `vendor/mermaid.min.js`, `vendor/chart.umd.min.js` (3.4 MB)
- `assets/`, `CNAME` (the Surge domain; must never go to Pages), `.surgeignore` (publish exclude list)
- Generated output: `index.html`, feeds, etc.

**`bible/` — case-study master copies:**

- `pl.md`, `en.md`, `de.md` and `evidence-ledger.jsonl` are byte-identical to the repo's `case-study/`.
- `pl|en|de.html` and `.pdf`, `diagrams/`.
- `build/` holds `md2html.mjs`, `html-to-pdf.mjs`, `render-mmd.mjs`, `page-head.html`, `page-script.html`, `package.json`, `package-lock.json` (Node). `bible/README.md` there is stale ("Not published", as of 14:05).

**`checker-api/`:** `app.py` is identical to the repo.

**`staging/surge-redirect/`:** `build_redirect.py`, `deploy_redirect.sh`, `public/`. These produce the Surge "moved" set.

**`pages-repo/{gh-pages,main}`:** temporary clones used by `publish_pages.sh` for pushing. **Do not use or modify them.**

**`evidence/`:** `archive.py`, `index.csv` and local source copies (REPORTED: 56 copies with SHA-256).

**`deploy.sh`:** the legacy full-site Surge deploy. **NEVER run it.** It would overwrite the Surge redirect set with the full site.

**Build flow** (`site/update_and_build.sh`, VERIFIED by reading):

1. Take the lock with `flock -w 120 data/.lock`.
2. Run `validate.py`, then `sync_bible.py` (copies `../bible/`), then `build.py`, then append to `data/changelog.json`.
3. If `GITHUB_PAGES_TOKEN` is set, run `publish_pages.sh`: it commits the built site to gh-pages and `data/facts.json` to main, with no force-push and `pull --rebase` on rejection.
4. Run `staging/surge-redirect/deploy_redirect.sh`.

**Hard-coded box paths:**

- `update_and_build.sh` line 33 (the redirect deploy)
- `publish_pages.sh` `WORK` default
- `sync_bible.py` `../bible`

**Lock rule:** any write to `site/data/facts.json` must hold `flock /workspace/php-incident/site/data/.lock`. `update_and_build.sh` takes the lock itself.

---

## 9. Summary: VERIFIED vs REPORTED vs ASSUMPTION

- **VERIFIED:**
  - git state, trees and tags
  - test results
  - facts.json and ledger integrity and counts
  - PL/EN/DE structural parity
  - live Pages, Surge, checker, SSRF and CORS behaviour
  - KEV absence
  - GitHub metadata and releases
  - licence texts
  - the build pipeline being box-only
  - box ↔ repo file identity
  - PDFs unpublished
- **REPORTED:**
  - routine schedule and end date
  - Render deploy history and the deployed commit
  - token permissions and the 403
  - Zenodo, Search Console and IndexNow status
  - evidence-archive counts
  - the private-reporting flag
  - owner preferences (see AGENTS.md)
- **ASSUMPTION:**
  - fly.toml is unused
  - the rightmost XFF hop may be a proxy
  - box timestamps are UTC (box `date` shows UTC)
