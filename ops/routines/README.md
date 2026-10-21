# Automation (routines) — export and re-creation templates

**Status: Recovered-from-config** (export made 2026-10-21 18:37 UTC from the Grok Bot "Nygus" server-side scheduler).
These routines did **not** run from cron on the box and are **not** part of this repository's runtime. A successor
does not inherit the scheduler, so anything still needed must be re-created. All templates here are **disabled by default**.

## Routines that existed

- `php2shell-meldunki` — schedule `CRON_TZ=Europe/Warsaw 0,30 8-22 * * *` (every 30 min, 08:00–22:30 Warsaw; the
  scheduler picked :11/:41 within a ±15 min window). Saved prompt: `php2shell-meldunki.prompt.md` (exact copy, unedited).
  Each run: run the security monitor (`/workspace/nygus-monitor/fetch_feeds.py --category security`), research,
  append to `/workspace/php-incident/log.md`, edit `site/data/facts.json` under `flock`, run `site/update_and_build.sh`
  (validate, build, publish gh-pages + facts.json to main, redeploy Surge redirect), report to Dawid in Polish.
  **The watch ends 23:00 Europe/Warsaw on 23.10.2026 (21:00 UTC).** After that the prompt tells the run to send a
  one-line closing note, disable the php2shell rules in `/workspace/nygus-monitor/triggers.yaml` and delete itself.
  The website stays up.
- `codzienny-artyku-ai-pl-de` (`0 8 * * 1-5` Warsaw) and `skan-r-de-ai-popo-udnie` (`0 15 * * 1-5` Warsaw) — not PHP2Shell related; listed only so nobody mistakes them for part of this project.

## Known stale detail in the saved prompt

The prompt still says the site is "publicly hosted at https://php2shell-live.surge.sh". Since 2026-10-21 the canonical
host is **GitHub Pages https://akirapl.github.io/php2shell/**; Surge only serves "moved" redirects (and copies of
feeds/facts.json). `update_and_build.sh` handles both, so the prompt still works. If you re-create the routine, replace
that sentence; the file here is kept verbatim as the record of what actually ran.

## Re-creating it (only with owner approval, only before the end date)

The meldunki routine is an **LLM agent task** (research + editorial judgement), not a plain script. It needs: an agent
CLI with web search, the box (or an equivalent machine with the files in `ops/MISSING_FROM_REPO.md`), the monitor,
`GITHUB_PAGES_TOKEN`, the Surge credentials, and a messaging channel to Dawid. Templates:

- `meldunki.crontab.example` — cron on the box, with an end-date guard and the flock rule.
- `meldunki.github-actions.yml.example` — GitHub Actions skeleton, manual trigger only and `if: false`. It can only do
  repo-side checks, because the build pipeline is box-only; it is a starting point for after NEXT_TASK-style import.

Neither is installed. Copying the Actions file into `.github/workflows/` needs a token with Workflows: write and owner approval.
