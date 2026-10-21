# NEXT_TASK — make the site build reproducible from the repository

Priority: **highest**. Status: not started (2026-10-21 18:30 UTC).

## Why this task

The site generator and the case-study renderer exist only on the owner's box (VERIFIED, HANDOVER.md §2.1 and §8):

- `main` has no build scripts. `gh-pages` holds only built output.
- Whoever lacks box access cannot fix a typo in the site template, rebuild after a facts.json correction, or regenerate the case-study HTML/PDF.
- The live routine ends on 23 Oct 2026. After that the box may not be maintained.

Every other open item depends on this one or is owner-only: Zenodo, topics, Search Console, licence wording.

## Scope

Bring the build source into the repo **on a local branch**, prepared for the owner to review. In this document `$BOX` means the owner's incident directory (path in HANDOVER.md §8).

- **`site/`** (new) is copied from `$BOX/site/`. It holds:
  - `build.py`, `template.html`, `seo.py`, `info.py`, `methodology.py`, `validate.py`, `sync_bible.py`, `pages_lib.py`
  - `update_and_build.sh`, `publish_pages.sh`, `enable_pages.sh`, `README.md`
  - `checker/` (widget source), `assets/`, `.surgeignore` (publish list)
  - the static `data/checker-config.json`
- **`case-study/build/`** (new) is copied from `$BOX/bible/build/`: `md2html.mjs`, `html-to-pdf.mjs`, `render-mmd.mjs`, `page-head.html`, `page-script.html`, `package.json`, `package-lock.json`. Do not copy `node_modules/`.
- **Vendor JS.** Either commit `vendor/mermaid.min.js` and `vendor/chart.umd.min.js` together with their upstream licence notices (both MIT), or replace them with a pinned download plus a SHA-256 check in the build. Record which option you chose.
- **Path parametrisation.** Replace the hard-coded box paths with variables that default to repo-relative paths:
  - in `update_and_build.sh`, the redirect deploy step becomes optional or off by default
  - the `WORK` default in `publish_pages.sh`
  - `../bible` in `sync_bible.py`, which should read `case-study/`
- **Docs.** A `site/README.md` section "Build from a fresh clone" with the exact commands.

Must NOT be included:

- `CNAME` (the Surge domain; it would set a custom domain on Pages)
- `__pycache__/`, `data/.lock`, `data/raw/`
- generated `*.html`, feeds, `sitemap.xml`, PDFs, `indexnow.json`
- any credentials file, token, or `$BOX` path

`data/facts.json` stays where it is: the repo root `data/` is the single source of truth.

## Acceptance criteria

1. These commands run in a fresh clone of the branch with no box access:
   - `python3 site/validate.py data/facts.json` prints `Walidacja OK`, exit 0
   - the documented build command writes the site into a temp dir
2. Diff the generated site with `origin/gh-pages` (`diff -r` minus `.git`). It shows no differences except build timestamps and `changelog.json`. List every residual difference in the PR notes.
3. `npm ci && node case-study/build/md2html.mjs …` regenerates `bible/{pl,en,de}.html`, and the output matches gh-pages apart from timestamps. Producing PDFs is optional; if you do, note the renderer used.
4. These checks find nothing:
   - `rg -n '/workspace|file://' -g '!HANDOVER.md' -g '!AGENTS.md' -g '!NEXT_TASK.md'`
   - `rg -n 'ghp_|github_pat_|SURGE_TOKEN='`
   - `git ls-files | rg -i 'cname$|credentials|\.lock$'`
5. `python3 checker-api/test_classify.py | grep -c FAIL` prints 0, and the existing data checks from HANDOVER.md §2.3–2.5 still pass.
6. One readable commit (or a small series) on a local branch with author `Nygus (bot for @Akirapl) <akira3179082@gmail.com>`. CHANGELOG gets an entry for the next version (owner picks the number). It is **not pushed**; you deliver a `git format-patch` for review.

## Verification procedure

```bash
git clone <patched branch or apply patch> /tmp/verify && cd /tmp/verify
python3 site/validate.py data/facts.json
OUT=$(mktemp -d) && <documented build command> --out "$OUT"
git fetch origin gh-pages && git worktree add /tmp/ghp origin/gh-pages
diff -r -x .git "$OUT" /tmp/ghp | head -50
```

Record the outputs in the hand-back report, in the format given in AGENTS.md.

## Dependencies

- Read access to `$BOX/site/` and `$BOX/bible/build/`. If you have no box access, stop and ask the owner for a tarball of exactly those paths, minus the excluded files.
- Python 3 (stdlib only, VERIFIED for validate.py). Node and npm for the case-study renderer.
- The owner's approval before any push. The routine pushes to `main` and `gh-pages` every 30 minutes until 23 Oct 2026, 21:00 UTC.

## Risks

- **Two sources of truth.** If the box `site/` keeps being edited after the copy, the repo copy goes stale. Mitigation: keep the box pipeline authoritative until the routine ends, then switch publish to the repo copy, with owner approval.
- **Lock conflicts.** Do not write to the box `facts.json`. If you must, hold `flock $BOX/site/data/.lock`.
- **An accidental custom domain or credential leak** through the copied files. The acceptance check 4 guards against this.
- **Copying a script that publishes.** `publish_pages.sh` pushes when `GITHUB_PAGES_TOKEN` is set. Never run it, `update_and_build.sh`, or `$BOX/deploy.sh` during this task.
- **Vendor licence obligations.** Keep the upstream MIT notices if you commit the minified files.

## Rollback

- Until the owner pushes, the work is a local branch plus a patch file: delete the branch and nothing changes.
- After a push to `main`: `git revert <sha>`, a new commit with no force-push. Neither the live site nor gh-pages is affected, because the box pipeline still publishes.
