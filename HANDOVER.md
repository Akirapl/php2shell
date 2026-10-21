# HANDOVER — php2shell (reconstruction guide)

For the next autonomous agent (Claude Code, Codex, …) that starts with **only a fresh public clone** of
<https://github.com/Akirapl/php2shell>. Owner: **Dawid Kulik** (GitHub `@Akirapl`). Rewritten 2026-10-21 ~18:50 UTC
on the owner's box against `main` @ `da7f470` (+ this commit) and `gh-pages` @ `1c94005`.

Every statement carries one tag:

- **[V]** Verified on 2026-10-21 (18:20–18:55 UTC) by running or reading the thing named.
- **[C]** Recovered-from-config: read from a file (script, config, exported routine), not executed.
- **[U]** Unverified assumption or second-hand report. Confirm before you rely on it.

Numbers that the 30-minute routine changes (sources, events, timestamps) are snapshots. Re-run `ops/verify_handover.sh`.

---

## 0. First command for a successor

```bash
git clone https://github.com/Akirapl/php2shell.git && cd php2shell && bash ops/verify_handover.sh --live
```

Expected on a fresh machine [V, fresh clone in /tmp, see §11]: all checks `PASS`, `0 FAIL`, plus `MISSING` lines for the
box-only build pipeline and `WARN` lines for optional tools. Then read `AGENTS.md` (rules) and do `NEXT_TASK.md`.

---

## 1. What this project is and what ran where

- **Public repo `main`** [V]: trilingual case study (`case-study/{pl,en,de}.md`, diagrams, evidence ledger),
  the live-center dataset `data/facts.json`, the checker API source (`checker-api/`), docs, `render.yaml`, and `ops/` (handover tooling).
- **Public repo `gh-pages`** [V]: built static site only (37 files), served by GitHub Pages at
  **<https://akirapl.github.io/php2shell/>** (canonical). Overwritten by every publish.
- **Owner box** (one Linux machine, Debian 13, user `box`) [V]: the build pipeline, working notes, evidence archive, monitor and
  credentials live under `/workspace/php-incident/` and `/workspace/nygus-monitor/`. **Not in the repo.** See §5 and `ops/MISSING_FROM_REPO.md`.
- **Grok Bot server-side scheduler** [C: routine export]: ran the `php2shell-meldunki` routine every 30 min. Not cron on the box.
  A successor does not have it (§7).
- **Render** (free plan, service `php2shell-checker`) [V live, C config]: runs `checker-api/` from `render.yaml` (Docker), at
  <https://php2shell-checker.onrender.com>. Cloudflare sits in front (`server: cloudflare` header) [V].
- **Surge** `php2shell-live.surge.sh` [V]: legacy host, now serves only "moved" redirect pages (+ copies of feeds and facts.json), `robots.txt: Disallow: /`.
- **Fly.io** `checker-api/fly.toml` [C]: alternative config, not in use [U].

---

## 2. Directory tree

### 2.1 Public repo (main) [V, `git ls-files`]

```
.github/ISSUE_TEMPLATE/{config,correction,new-source,translation}.yml
ABOUT.md ARCHIVE.md(plan only) CHANGELOG.md CITATION.cff CONTRIBUTING.md SECURITY.md README.md
LICENSE (MIT, code)  LICENSE-CONTENT (CC BY 4.0, text/diagrams/facts.json)
HANDOVER.md AGENTS.md NEXT_TASK.md          <- operational docs; may contain box paths on purpose
case-study/{pl,en,de}.md                     <- pl.md is the master
case-study/diagrams/{actors,disclosure,lifecycle,timeline}.{mmd,png}
case-study/evidence-ledger.{jsonl,csv}       <- CLM-0001..CLM-0089
checker-api/{app.py,test_classify.py,requirements.txt,Dockerfile,fly.toml,README.md}
data/facts.json                              <- single source of truth of the live center (copy pushed by the routine)
render.yaml                                  <- Render blueprint for checker-api
ops/verify_handover.sh ops/checks.py         <- fresh-clone verification (this handover)
ops/env.example ops/MISSING_FROM_REPO.md ops/README.md
ops/routines/{README.md,php2shell-meldunki.prompt.md,meldunki.crontab.example,meldunki.github-actions.yml.example}
```

### 2.2 gh-pages [V, `git ls-tree -r origin/gh-pages`]

`index.html info.html methodology.html feed.xml feed-pl.xml feed-de.xml sitemap.xml robots.txt .nojekyll`
`dbc98eb4bceea3f0edf36cc6769afd2b.txt` (IndexNow key file; keep published), `assets/og-image.png`,
`bible/{pl,en,de}.html bible/diagrams/*.png`, `checker/{index.html,section.html,checker.js,checker.css}`,
`data/{facts.json,changelog.json,checker-config.json}`, `data/additions/2026-10-21-HHMM.json` (10 per-run snapshots),
`vendor/mermaid.min.js` (Mermaid 10.9.1), `vendor/chart.umd.min.js` (Chart.js 4.4.4).

### 2.3 Owner box [V, `ls`]

```
/workspace/php-incident/
  .render-credentials .surge-credentials   <- secrets (mode 600). Never read/print/copy.
  deploy.sh                                <- legacy full-site Surge deploy. NEVER RUN.
  log.md case-study.md best-practices.md   <- working notes (Polish), never publish
  site/            build pipeline + generated site (see ops/MISSING_FROM_REPO.md §A–B)
    data/facts.json data/.lock data/changelog.json data/additions/ data/raw/ data/checker-config.json
    CNAME          <- Surge domain; must never reach gh-pages
  bible/           case-study masters {pl,en,de}.md + .html + .pdf, diagrams/, evidence-ledger.*, build/ (Node renderer)
  checker-api/     same app.py/test_classify.py as repo + DEV-NOTES.md run.sh uitest.py .venv/
  evidence/        archive.py index.csv (59 URLs, 58 local copies with sha256, 21 Wayback URLs) copies/ (26 MB)
  staging/         patch/test workspaces; surge-redirect/{build_redirect.py,deploy_redirect.sh,public/}; handover/
  pages-repo/{gh-pages,main}   <- temporary clones used by publish_pages.sh. Do not use or modify.
/workspace/nygus-monitor/      fetch_feeds.py triggers.py sources.yaml triggers.yaml x_watchlist.yaml notes/ seen.db
```

---

## 3. Data flow and publication pipeline

```
 monitor (nygus-monitor) ─┐
 web search / X tools ────┼─> agent run (meldunki routine) ──> log.md (working notes)
                          │        │
                          │        └─ flock site/data/.lock ─> site/data/facts.json  (single source of truth)
                          │
 bible/{pl,en,de}.md ─(bible/build/md2html.mjs, manual)─> bible/*.html ─┐
 bible/diagrams/*.mmd ─(render-mmd.mjs, manual)─> *.png                  │
                                                                         v
 site/update_and_build.sh:  validate.py ─> sync_bible.py ─> build.py (+seo/info/methodology) ─> changelog.json
        ├─ publish_pages.sh ─> gh-pages (whole built site)  and  main:data/facts.json  (no force, pull --rebase on reject)
        └─ staging/surge-redirect/deploy_redirect.sh ─> php2shell-live.surge.sh (moved pages + feeds + facts.json)
 case-study md + ledger ─> repo main: committed MANUALLY (e.g. 98f9a53); publish_pages.sh only pushes data/facts.json
 checker-api/ on main ─> Render (Docker) ─> site widget reads data/checker-config.json {"api_base": ...}
```

- [C] `update_and_build.sh`: `exec 9>data/.lock; flock -w 120 9`, then `validate.py [--relaxed]`, `sync_bible.py`, `build.py`,
  changelog append, `publish_pages.sh` only if `GITHUB_PAGES_TOKEN` is set (a failure is a WARNING, not fatal), then the Surge redirect deploy (hard-coded path, line 33).
- [C] `publish_pages.sh`: auth via `GIT_CONFIG_*` env → `http.https://github.com/.extraheader` (Bearer, fallback Basic `x-access-token`);
  author `Nygus (bot for @Akirapl) <akira3179082@gmail.com>`; message `Live update <UTC>: <diff summary> — <hint>`; publish set = `.surgeignore` minus `CNAME` plus `.nojekyll`.
- [V] Box `bible/{pl,en,de}.md`, `evidence-ledger.jsonl`, `checker-api/app.py`, `test_classify.py` are byte-identical to the repo; box `site/data/facts.json` == `main` == `gh-pages` copy (18:41 UTC, `cmp`).
- [V] Box PDFs (16:16 UTC) are older than the md/html (17:07 UTC) and are excluded from publishing (`bible/*.pdf` in `.surgeignore`): `/bible/en.pdf` → 404.
- [V] The 4 PNG diagrams in `case-study/diagrams/` are rendered by `render-mmd.mjs` with the vendored Mermaid 10.9.1 (not the 11.x mermaid-cli in package.json) [C].

---

## 4. Dependencies and versions

Public repo (what a fresh clone needs):

- Python **≥ 3.10** for `ops/checks.py` (stdlib) [V: ran on 3.13.5]. Checker container: `python:3.12-slim` [C Dockerfile].
- Checker pins [C requirements.txt, V installed]: `fastapi==0.157.0 pydantic==2.14.1 starlette==1.9.0 uvicorn==0.54.0`
  (resolved extras: pydantic_core 2.50.1, anyio 4.15.1, h11 0.16.0, click 8.5.0, idna 3.20) [V `pip freeze`].
- `git`, `curl` (for `--live`); optional `rg`, `docker` [V].

Box-only pipeline [V versions on the box]:

- Python 3.13.5 (site/*.py are stdlib only [C imports]); bash; `flock` (util-linux 2.41.5); git 2.47.3; jq 1.7; ripgrep 14.1.1.
- Node v20.19.2, npm 11.21.0; `bible/build` deps installed: `@mermaid-js/mermaid-cli 11.17.0`, `markdown-it 14.3.3`,
  `markdown-it-footnote 4.0.0`, `puppeteer-core 22.15.0`; Google Chrome 155.0.8059.84 at `/usr/bin/google-chrome` (PDF/diagrams).
- Surge CLI 0.46.0 at `/home/box/.local/bin/surge`.
- Monitor: feedparser 6.0.14, PyYAML 6.0.3, requests 2.34.2.
- Not used: pandoc (not installed) [V].

---

## 5. Install, configure, build, test, run

### 5.1 From a fresh clone (works without the box) [V §11]

```bash
bash ops/verify_handover.sh            # creates ${TMPDIR:-/tmp}/php2shell-verify-venv, installs checker deps, runs everything
python3 ops/checks.py                  # facts / ledger / parity / paths / secrets only, no deps
python3 -m venv .venv && . .venv/bin/activate && pip install -r checker-api/requirements.txt
cd checker-api && python test_classify.py | tee /tmp/t.txt; grep -c '^FAIL' /tmp/t.txt   # expect 0 (script exits 0 even on FAIL)
cd checker-api && uvicorn app:app --host 127.0.0.1 --port 8799   # local API; CHECKER_RESOLVER=auto if DNS returns 198.18/15
docker build -t p2s-checker checker-api && docker run -p 8080:8080 p2s-checker   # [U] not run (no docker on the box)
```

### 5.2 Site and case-study build (box only, until the pipeline is imported)

```bash
cd /workspace/php-incident/site
python3 validate.py data/facts.json          # [V] "Walidacja OK", exit 0; read-only
# DO NOT run update_and_build.sh while testing: it PUBLISHES (gh-pages, main, Surge) when the token is present.
cd ../bible/build && npm ci && node md2html.mjs [pl en de]    # [C] md -> ../{lang}.html
node render-mmd.mjs                                            # [C] ../diagrams/*.mmd -> png (needs Chrome)
node html-to-pdf.mjs                                           # [C] ../{lang}.html -> pdf (hard-coded Chrome path)
```

A build-only run without publishing is not supported by `update_and_build.sh` [C]; run `validate.py`, `sync_bible.py`, `build.py` by hand
in a **copy** of `site/` (they write into their own directory) [C: paths derived from `__file__`].

---

## 6. Environment variables, credentials, external services (names only; values never)

Full list with scopes: `ops/env.example`.

- `GITHUB_PAGES_TOKEN` [V set on box; C scopes from scripts]: fine-grained PAT, repo Akirapl/php2shell, **Contents: read & write**
  (publish), **Pages: read & write** (only `enable_pages.sh`). Lacks **Administration: write** (repo homepage/topics → 403) [U, reported].
  Workflows: write unknown [U]. Used by `publish_pages.sh`, `enable_pages.sh`, and manual pushes like this handover.
- `.render-credentials` [V exists; key names RENDER_EMAIL, RENDER_PASSWORD]: Render dashboard login for account `akira3179082@gmail.com`. No API key in use.
- `.surge-credentials` [V exists; key names SURGE_LOGIN, SURGE_PASSWORD, SURGE_TOKEN]: sourced by `deploy_redirect.sh` (and `deploy.sh`).
- Optional knobs: `PAGES_REPO_URL`, `PAGES_WORK`, `RELAXED`, `CHECKER_RESOLVER`, `PORT`, `CHROME` [C].
- External services: GitHub (repo + Pages) [V], Render free plan [V], Cloudflare in front of Render [V header], Surge [V],
  CISA KEV JSON feed (exploitation threshold check), IndexNow (Bing submission, reported done) [U], Wayback Machine (evidence) [C index.csv],
  Google Search Console verification pending [U]. Zenodo DOI not set up [U].

---

## 7. Automated tasks and triggers

- `php2shell-meldunki` [C `ops/routines/`]: `CRON_TZ=Europe/Warsaw 0,30 8-22 * * *` (±15 min; ran at :11/:41), on the Grok Bot server scheduler.
  [V] main has `Live update …` commits roughly every 30 min (15:03–18:37 UTC on 21 Oct).
  **Ends 23:00 Europe/Warsaw, 23.10.2026 (21:00 UTC)**: closing note to Dawid, disable php2shell rules in `triggers.yaml`, routine deletes itself; the website stays up.
- Its saved prompt (`ops/routines/php2shell-meldunki.prompt.md`, verbatim) still names Surge as the public host; canonical is GitHub Pages [V].
- Re-creation templates (disabled): `ops/routines/meldunki.crontab.example`, `ops/routines/meldunki.github-actions.yml.example`.
- No GitHub Actions workflows exist in the repo [V]. Render "auto-deploy on commit" is configured in `render.yaml` [C] but did not fire reliably (§9).
- While the routine runs, **every ~30 min** `main` (facts.json) and `gh-pages` move: always `git fetch && git rebase origin/main` before pushing; never force.

---

## 8. Live state (2026-10-21 18:40–18:43 UTC) [V, read-only GETs]

- `https://akirapl.github.io/php2shell/` → 200, `cache-control: max-age=600`; live `data/facts.json` meta.last_updated `2026-10-21T18:42:00Z`, 103 sources, 78 events (= main).
- `/bible/en.pdf` → 404 (PDFs unpublished). Surge `robots.txt` → `Disallow: /`.
- Checker `/health` → `{"ok":true,"service":"PHP2Shell-Live-Checker","version":"1.0"}` after a 12.4 s cold start;
  `/check?url=https://example.com` → 200 `no_php_detected`, 1 hop, `caveats[0]` = ownership notice; `?url=http://127.0.0.1` → 400.
  Earlier the same day the previous handover saw 400 for 169.254.169.254, `[::1]`, `localhost`, port 8443, `file://`, and CORS allowing only `https://akirapl.github.io` of the tested origins [V by previous agent, not repeated].
- Exploitation status in facts.json: `status.exploitation = "reported"`; `exploitation_threshold.kev_listed = false`, `kev_checked_utc 18:40`, catalogVersion `2026.10.21` [V file].
- Deployed checker commit on Render: unknown [U]; it includes the ownership-caveat change (`5b3a74e`+) [V by behaviour].
- GitHub repo: homepage null, topics empty, release `v1.0` without assets [V by previous agent, unauthenticated API].

---

## 9. Known failure modes

- **Render auto-deploy unreliable** [U, reported twice]: the service was created from the public repo URL without a GitHub connection.
  After changing `checker-api/` the owner must press **Manual Deploy → Deploy latest commit** in the dashboard. Verify with `/health` and a behaviour that only the new code has.
- **Lock rule**: every write to `/workspace/php-incident/site/data/facts.json` must hold `flock /workspace/php-incident/site/data/.lock`
  (`update_and_build.sh` takes it itself, `-w 120`) [C]. Without it a routine run can clobber your edit or publish a half-written file.
- **Mermaid lazy-load reveal bug** (fixed) [V template.html lines ~331–334]: a second `renderDiagrams()` after Mermaid loaded replaced
  `.reveal` cards without `observe()`, leaving them `opacity:0` (black gap on mobile). Fix: diagram cards are rendered as `card reveal in`.
  The fix exists only in the box `template.html` (and its output on gh-pages); keep it when importing.
- **Poll/grep false negatives** [V mechanics; original incident U]: checking "is my change live?" with `curl … | grep` fails spuriously because
  Pages caches 10 min (`max-age=600`) and `facts.json` is pretty-printed (`"key": "value"` with a space), and `grep -c` exits 1 when the count is 0
  (aborts `set -e` scripts on the *good* result). Use `?t=$(date +%s)`, parse JSON, and `|| true` around `grep -c` — as `ops/verify_handover.sh` does.
- **`test_classify.py` exits 0 on FAIL** [V by reading]: CI or scripts must count `^FAIL` lines. Fixing it is NEXT_TASK.
- **`update_and_build.sh` publishes** whenever `GITHUB_PAGES_TOKEN` is set; there is no dry-run flag [C].
- **`deploy.sh` would overwrite the Surge redirects** with the full site [C]. Never run it.
- **Box DNS returns fake IPs (198.18.0.0/15)** [C DEV-NOTES]: local checker tests of real hosts need `CHECKER_RESOLVER=auto`.
- **Checker cold start** 12–50 s on Render free plan [V 12.4 s]: do not treat the first slow response as an outage.

---

## 10. Known discrepancies and open owner decisions (do not change silently)

1. **v1.0 tag → `22112a0`** [V], the 3rd commit; predates CITATION.cff (which says `version: v1.0`), the checker and the ledger. Re-tagging/new release = owner.
2. **LICENSE and LICENSE-CONTENT say `Copyright (c) 2026 Dawid `** (no surname, trailing space in LICENSE) [V]; CITATION.cff says Dawid Kulik.
   The owner is fine with the real name "Dawid Kulik", but changing licence files is his decision: listed, not changed.
3. **LICENSE-CONTENT scope** names case-study text/diagrams and `data/facts.json`, not the evidence ledger [V]. Owner to decide.
4. **CORS too broad** [V app.py:50–51]: allows `https://[a-z0-9-]+\.surge\.sh` (any Surge site) and `http://127.0.0.1:8765`/`localhost:8765`. Read-only GET, low impact.
5. **Checker README says "only the root path `/`" / "no other paths"** [V]: hop 0 is forced to `/`, but up to 2 redirect hops request the `Location` path (each re-validated, IP-pinned, 80/443, 4 KB cap).
6. **Per-IP limit keys on the rightmost `X-Forwarded-For` hop** [V app.py:81–87]. Behind Cloudflare→Render this may be a proxy address, so all users could share one 10/min bucket [U]. Do not load-test production; check Render logs (owner) or a staging service.
7. **Exploitation threshold** [V facts.json]: "confirmed only if CISA KEV lists a CVE **or a national CERT publishes credible in-the-wild evidence**" — broader than "KEV only" in older notes. The file is authoritative.
8. **PDFs not published and older than markdown** [V].
9. **Repo homepage/topics empty**; token lacks Administration: write [U for the scope, V for the empty fields]. Owner sets them in the UI.
10. **Local-path check vs. this file**: public docs must not contain `/workspace` or `file://` (CHANGELOG v1.4 rule, ledger builder assertion). The owner decided
    (2026-10-21) that the operational docs keep real box paths. Resolution: `ops/checks.py` (`paths` check) allowlists exactly
    `HANDOVER.md`, `AGENTS.md`, `NEXT_TASK.md` and `ops/`; every other tracked file must stay free of local paths.
11. **Ledger metadata gaps** [V]: `claim_lang_source` empty in all 89 rows; `label_in_text` empty for CLM-0027.
12. Zenodo DOI, Search Console, GitHub private vulnerability reporting: owner-only, not done [U].

---

## 11. Verification record (this handover)

- [V 18:42 UTC, box clone] `bash ops/verify_handover.sh --live` → `28 PASS, 0 FAIL, 9 WARN/MISSING`
  (test_classify 15 OK / 0 FAIL; local uvicorn smoke OK; box `validate.py` exit 0; 6 live GETs OK).
- [V 18:47 UTC, fresh clone] `git clone https://github.com/Akirapl/php2shell /tmp/fresh-20261021T184739Z`, fast-forwarded to this
  commit, fresh venv under a fresh `TMPDIR`, `GITHUB_PAGES_TOKEN` unset, `P2S_BOX=/nonexistent`:
  `bash ops/verify_handover.sh --live` → `18 PASS, 0 FAIL, 11 WARN/MISSING` (pip install of the 4 pins OK; test_classify 15 OK / 0 FAIL;
  local uvicorn smoke OK; facts/ledger/parity/paths/secrets PASS; 7 MISSING box-pipeline/PDF files; box absent; token unset; docker absent; PDF 404).
- [V] negative tests in that clone (reverted afterwards): a bad `confidence` value, a deleted ledger row, a `/workspace` line in README.md,
  a fake `ghp_` token in CONTRIBUTING.md and a demoted heading in `de.md` each made `ops/checks.py` FAIL (exit 1). One broken checker test case made
  `test_classify.py` print 1 `FAIL` and **exit 0**, and `verify_handover.sh` still reported it as FAIL (counts lines).
- [V] secret scan: no token/key patterns in tracked files on main, nor in `git log -p` of main and gh-pages. Two pattern hits are
  false positives (`checker-api/app.py:159` `u.password` check; a regex in docs).

---

## 12. Fallback procedures

- **No box** (most likely for you): everything in §5.1 works. To rebuild the site you need the pipeline: ask the owner for the
  tarball in `ops/MISSING_FROM_REPO.md`. Until then, small site fixes can be made by editing built files from `origin/gh-pages`
  — **only with owner approval**, because the routine overwrites gh-pages every 30 min until 23 Oct 21:00 UTC.
  Vendor JS, checker widget and og-image are byte-identical on gh-pages and can be recovered with `git show origin/gh-pages:<path>` [V].
- **No `GITHUB_PAGES_TOKEN`**: `update_and_build.sh` prints one line and skips Pages (live site NOT updated) [C]. Hand back a
  `git format-patch` for the owner to push.
- **Render down / account unavailable**: the site degrades (widget cannot reach the API) but stays up. Re-deploy `checker-api/`
  anywhere that runs Docker (`render.yaml` or `fly.toml`), then the owner changes `data/checker-config.json` `api_base` (box `site/data/`, rebuild). Keep SSRF guards and limits (AGENTS.md §6).
- **Surge unavailable**: only old links/feeds are affected; Pages is canonical. Remove or skip the last line of `update_and_build.sh` (owner decision).
- **Scheduler unavailable / routine gone**: nothing breaks; the site simply stops updating. Re-create from `ops/routines/` only with owner approval and before the end date.
- **GitHub Pages down**: no hot standby. Surge could host the full site again via `deploy.sh`, but that is an owner decision (it undoes the redirects).

---

## 13. Unfinished work

- Build pipeline not in the repo (`ops/MISSING_FROM_REPO.md`) — the biggest gap; requires the owner's files.
- `test_classify.py` exit code + CI checks — `NEXT_TASK.md`.
- PDFs stale/unpublished; ledger metadata gaps; CORS narrowing after the Surge redirect period; XFF keying verification.
- End-of-watch steps on 23 Oct (routine does them itself); `ARCHIVE.md` is **only a plan** — freezing, final release and archiving need owner approval.
