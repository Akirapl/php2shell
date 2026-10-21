# Files the build and operations need that are NOT in the public repository

Manifest generated 2026-10-21 ~18:45 UTC on the owner box (`stat` + `sha256sum`). Status: **Verified (2026-10-21)** for existence, size and hash at that moment. Updated 2026-10-21 23:50 UTC for `site/build.py`, `site/template.html`, `bible/build/page-head.html` (diagram text descriptions).
Paths are relative to the box incident root `/workspace/php-incident/` unless they start with `/`.
None of the listed files contains a credential value (checked with a pattern scan; they reference credentials only by variable or file name).

`ops/verify_handover.sh` reports the site/ and case-study/build/ entries as `MISSING` until NEXT_TASK-style import happens.

## A. Site generator (box-only; NOT recoverable from any public source)

- `site/build.py` — 28012 B — sha256 `ae4e500c548f6317023e92c28029fc6be27a2b438409ed6d349a1ead7d14abbb` — renders index.html from template.html + data/facts.json; imports seo, info, methodology
- `site/template.html` — 44415 B — sha256 `ab56a70f50451085dcaff1a4c8df2d10ea96414206023e0b7e76d94f64061ea0` — live-center HTML/CSS/JS template; contains the mermaid reveal/.in fix (diagram cards rendered with class `reveal in`); since 2026-10-21 23:47 UTC also text equivalents for the diagram cards (role=img + aria-label, `<details class="dgtx">`, prerendered by build.py `prerender_diagrams()`)
- `site/seo.py` — 18403 B — sha256 `5af15d61916f3ab3ce3fe889271cb0c3d6dfa2828da34135869d718b24e8297d` — meta tags, JSON-LD, feeds (feed*.xml), sitemap.xml, robots.txt
- `site/info.py` — 18628 B — sha256 `518eb2da5ac31fe945571b12e33364b0c35d306391ace4154eab98b4cb01e92a` — info.html
- `site/methodology.py` — 27798 B — sha256 `82381e1da1150c66fd91ead122301bbb0f77cb6b6fa6c50deeb6fd65298c51b3` — methodology.html
- `site/validate.py` — 11848 B — sha256 `38d781a6ba02f8ade7d56668fe53e34e7a9f374fd936debdce854136876906a1` — facts.json validator, stdlib only; prints `Walidacja OK`
- `site/sync_bible.py` — 3669 B — sha256 `644535de6bcbf8f9a7593100f5600e37d41f0d25532a1c8e86a8b8ff7c22bf32` — copies ../bible/*.html + diagrams into site/bible/ and injects the live theme
- `site/pages_lib.py` — 6872 B — sha256 `0d06f69850d3e99b1044fb513c44aff0a16698ca6c8eb97a1e4e9c7d03c43413` — publish set + commit-message summary for publish_pages.sh
- `site/update_and_build.sh` — 1948 B — sha256 `fb9fdb631c2fed08c9f8c361b0b6a4378ecaf2a7bcb0126fdef7e9cf65237d47` — the pipeline entry point (lock, validate, sync, build, changelog, publish, Surge redirect)
- `site/publish_pages.sh` — 5799 B — sha256 `5114c5b7c37be3fb183539ea503cfb60b1f56e1bd3872e81063dddabac52cb80` — pushes built site to gh-pages and data/facts.json to main (token via in-memory extraheader)
- `site/enable_pages.sh` — 2060 B — sha256 `bf2a8378b0996f33a7926581c3791935e11397612cecdd1e1f17bc543b96ae5e` — one-off: enables GitHub Pages via API (needs Pages: write)
- `site/README.md` — 12994 B — sha256 `62835144db9c8805db6c57b79b14f0aac2f86fa80bae1a4e71f410ad5afafb86` — box operator manual for the live center (how to add facts, rebuild, publish)
- `site/.surgeignore` — 234 B — sha256 `b09d1bde9b3e32b8ba62e845bda8ea74a76d0581437d8afb971f807dbbc5770f` — publish exclude list (also used by pages_lib.py for the gh-pages set)

## B. Site assets (box copies are byte-identical to `origin/gh-pages`, so recoverable with `git show origin/gh-pages:<path>`)

- `site/checker/index.html` — 2877 B — sha256 `f7f18779c053cbb2b3a0ffc908436fd1bd7b9d81af27d2143ec5b223c780e088`
- `site/checker/section.html` — 235 B — sha256 `34ae07dbaf2c795d1cb8a43f9d06862eb4d5b9fbd511bcf8b9b386a74f09f9d1`
- `site/checker/checker.js` — 19239 B — sha256 `9f869c65f4fa89525d0c51d5cfae4960ea928a083980f17f3eb1a01b4dd13a3e`
- `site/checker/checker.css` — 3418 B — sha256 `f40f95f82c5a9a972e6110ae3ff16973bff1c01e6bfa4f79d27de55979c9cea8`
- `site/checker/INTEGRATE.md` — 3414 B — sha256 `75142e61c40495dee2704a5ceee38990445a7cb18ec84ec49af039209fe98721` — NOT on gh-pages (excluded by .surgeignore): box-only
- `site/assets/og-image.png` — 180379 B — sha256 `e603e279f706330bb56565d13edb9c63ac07d151f494faaf8d6895c77974e5d0`
- `site/data/checker-config.json` — 55 B — sha256 `ed6ca45d331c4b48fbb3f6a2693deca54c87e99e7823c5ef19272dc2d71b9dcf` — `{"api_base": "https://php2shell-checker.onrender.com"}`
- `site/vendor/mermaid.min.js` — 3335717 B — sha256 `61b335a46df05a7ce1c98378f60e5f3e77a7fb608a1056997e8a649304a936d6` — Mermaid 10.9.1 (version string inside the file), MIT
- `site/vendor/chart.umd.min.js` — 205749 B — sha256 `b38076762f7363bc9e912b68b8e034826798db5df26bb61f000ec2e7a3137bc7` — Chart.js v4.4.4, MIT

## C. Case-study renderer (box `bible/build/`; Node 20, npm; Chrome for PDF/diagrams)

- `bible/build/md2html.mjs` — 3141 B — sha256 `9768f61179af92c41a8ace31c9091c0fef7383b961f0df137f32ec0965789c94` — bible/<lang>.md -> bible/<lang>.html (markdown-it 14.3.3 + markdown-it-footnote 4.0.0)
- `bible/build/html-to-pdf.mjs` — 1612 B — sha256 `0d826aa671ee8e8afbfb3d938d9acaac8b385db28ed0e8677616bb70d66fe325` — HTML -> PDF via puppeteer-core 22.15.0 and `/usr/bin/google-chrome` (hard-coded)
- `bible/build/render-mmd.mjs` — 3422 B — sha256 `ed5f06741b1f1347011c9459316f13f7db376da11a10cc6e85e750d895e60226` — diagrams/*.mmd -> PNG; hard-codes `/workspace/php-incident/site/vendor/mermaid.min.js`; CHROME env overrides the browser
- `bible/build/page-head.html` — 6136 B — sha256 `0d9661ce88b1bd54dd4d93d64a0c04d9c8bfb1e70b0bee50b2b5a81fe7c52d87`
- `bible/build/page-script.html` — 1680 B — sha256 `956dd06078540bc462bc2437e88974604596f276b14a3cfcf8acd0b8266f92e0`
- `bible/build/package.json` — 410 B — sha256 `e9df7d748fb75f163f4209bd4a1b3a59a72e4bfa44bea6dabf6eb556cbc542b2` — deps: @mermaid-js/mermaid-cli ^11.17.0, markdown-it ^14.3.3, markdown-it-footnote ^4.0.0, puppeteer-core ^22.15.0
- `bible/build/package-lock.json` — 124029 B — sha256 `59821860c7439be5b491ab058af5ffbade9da1a81a3f48508e54b6b7bb1bed74`

## D. Surge redirect (box `staging/surge-redirect/`)

- `staging/surge-redirect/build_redirect.py` — 3416 B — sha256 `033a9d00536839788d59e8cc70d351bae9ed7589bd57608f058c6c7fb1dfe3f3` — builds public/ (moved pages + copies of feeds and facts.json); hard-codes SITE path
- `staging/surge-redirect/deploy_redirect.sh` — 655 B — sha256 `d688ce531cd54f0af2ad37bd9cbde64a615d6608ab2430841b8bc2bbd648a494` — sources .surge-credentials and runs the surge CLI 0.46.0

## E. Checker dev-only files (box `checker-api/`; app.py and test_classify.py are identical to the repo)

- `checker-api/DEV-NOTES.md` — 916 B — sha256 `78c7185bb806c39b634568792c6a05e67fd1f64962eab4fa8064e28cb0884254` — box DNS returns fake IPs 198.18/15 -> use CHECKER_RESOLVER=auto locally
- `checker-api/run.sh` — 243 B — sha256 `6ff5d4e9cd01ce1b0f5f0a323217088548861032d86cd525653efbf8977e26fa` — uvicorn on 127.0.0.1:8799 with proxy headers from 127.0.0.1
- `checker-api/uitest.py` — 1711 B — sha256 `24fa3890edbe6dd9f77d9034c5113f9bb70c2c64e36f2c62e67eba2e24869ba7` — browser UI test of the widget

## F. Evidence archive (box `evidence/`; 117 local copies in `evidence/copies/`, 26 MB)

- `evidence/archive.py` — 3925 B — sha256 `27e712e625747b8f761dc77e61107456f32dab015d5551774e7eba21342201a8` — fetches and hashes source copies, Wayback submission
- `evidence/index.csv` — 22540 B — sha256 `1ca446278ad2d0242380fb06fd2057baf996b7546860daa8c5980a84a690614f` — URL -> local copy -> sha256 -> Wayback status
- `evidence/urls.txt` — 3722 B — sha256 `dbe6d1cd5effd5ea2107f9fdc2d1dd504aa220e35996009a4947729589dd17f0`

## G. Monitor used by the meldunki routine (box `/workspace/nygus-monitor/`, outside the incident root)

- `/workspace/nygus-monitor/README.md` — 7414 B — sha256 `ffc331cb4c23518dd8daf02e43978bc621d5c427ccbfdf80ea5e30e17cf69f70`
- `/workspace/nygus-monitor/fetch_feeds.py` — 17425 B — sha256 `8a5a14f3a25ecf00e3a6a9874a591e73633eb0a20b4d9b23b8830fd1419df0d0` — needs feedparser 6.0.14, PyYAML 6.0.3, requests 2.34.2
- `/workspace/nygus-monitor/triggers.py` — 10652 B — sha256 `9e18e1c2dd89b6bf72f0d43a7e3b750450fa8df203739ad14a12d3d5b6546194`
- `/workspace/nygus-monitor/sources.yaml` — 11282 B — sha256 `505b71b3fbd170444e7296043c0b1c107b958747874305e802e06066ebd82ad5`
- `/workspace/nygus-monitor/triggers.yaml` — 3808 B — sha256 `9e39798203c296a00378c03f472bcebdc474436f4f35579b5e380c9fef2a119c` — php2shell trigger rules (to be disabled at the end of the watch)
- `/workspace/nygus-monitor/x_watchlist.yaml` — 3207 B — sha256 `0bf85f8925810c2a826597b90300070b62e31c7068a936ad86f7fe4983819c8e`

## H. Working notes (box-only on purpose; do not publish)

- `log.md` (timeline log, Polish), `case-study.md` (Polish working draft), `best-practices.md`, `staging/` (patch and test workspaces), `site/data/additions/` (per-run JSON snapshots; also on gh-pages), `site/data/changelog.json` (also on gh-pages).
- These are working notes: keep them separate from public docs. They may contain unverified leads and local paths.

## I. Credentials (never copy, never commit, never print)

- `/workspace/php-incident/.render-credentials` (key names: `RENDER_EMAIL`, `RENDER_PASSWORD`)
- `/workspace/php-incident/.surge-credentials` (key names: `SURGE_LOGIN`, `SURGE_PASSWORD`, `SURGE_TOKEN`)
- env `GITHUB_PAGES_TOKEN` (fine-grained PAT, see ops/env.example)

## Never import

- `site/CNAME` (contains the Surge domain; on gh-pages it would set a custom domain), `site/data/.lock`, `site/data/raw/`, `__pycache__/`, `node_modules/`, `.venv/`, generated `*.html`, feeds, `sitemap.xml`, `indexnow.json`, PDFs, `deploy.sh`, credential files, `pages-repo/`.

## How the owner can provide the missing pipeline (owner step)

Option 1 (preferred, on the box): let an agent import A–E into the repo as in NEXT_TASK's follow-up (`site/`, `case-study/build/`, `ops/surge-redirect/`) with paths parametrised.

Option 2 (tarball, shared privately, not via a public release):

```bash
cd /workspace/php-incident && tar czf /tmp/php2shell-pipeline-$(date -u +%Y%m%d).tgz \
  --exclude='__pycache__' --exclude='node_modules' --exclude='.venv' --exclude='*.pdf' --exclude='CNAME' --exclude='.lock' \
  site/build.py site/template.html site/seo.py site/info.py site/methodology.py site/validate.py site/sync_bible.py \
  site/pages_lib.py site/update_and_build.sh site/publish_pages.sh site/enable_pages.sh site/README.md site/.surgeignore \
  site/checker site/assets site/vendor site/data/checker-config.json \
  bible/build/md2html.mjs bible/build/html-to-pdf.mjs bible/build/render-mmd.mjs bible/build/page-head.html \
  bible/build/page-script.html bible/build/package.json bible/build/package-lock.json \
  staging/surge-redirect/build_redirect.py staging/surge-redirect/deploy_redirect.sh \
  checker-api/DEV-NOTES.md checker-api/run.sh checker-api/uitest.py evidence/archive.py evidence/index.csv evidence/urls.txt
tar tzf /tmp/php2shell-pipeline-*.tgz | grep -Ei 'credential|cname|\.lock' && echo 'STOP: forbidden file in tarball'
sha256sum /tmp/php2shell-pipeline-*.tgz   # then compare member hashes with this manifest
```

The successor unpacks it to a scratch dir and checks each file's sha256 against this list (files edited after 18:45 UTC on 21 Oct will differ; that is expected while the routine runs).
