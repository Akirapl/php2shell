#!/usr/bin/env bash
# verify_handover.sh — read-only reconstruction check for a fresh clone of Akirapl/php2shell.
#
#   bash ops/verify_handover.sh            # prerequisites, data checks, checker tests (creates a venv in /tmp)
#   bash ops/verify_handover.sh --live     # + at most 6 read-only GETs against the live site and checker
#   bash ops/verify_handover.sh --no-install   # do not pip install; skip checker tests if fastapi is missing
#   VENV=/path/to/venv bash ops/verify_handover.sh
#
# It never pushes, deploys, writes outside the venv/tmp, or prints secrets (it only tests whether they exist).
# Exit code: 0 = no FAIL, 1 = at least one FAIL. MISSING/WARN lines are expected gaps, not failures.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
LIVE=0; INSTALL=1
for a in "$@"; do case "$a" in --live) LIVE=1;; --no-install) INSTALL=0;; -h|--help) sed -n 2,11p "$0"; exit 0;; *) echo "unknown arg $a"; exit 2;; esac; done
VENV="${VENV:-${TMPDIR:-/tmp}/php2shell-verify-venv}"
PASS=0; FAILN=0; WARN=0
pass() { echo "PASS  $*"; PASS=$((PASS+1)); }
fail() { echo "FAIL  $*"; FAILN=$((FAILN+1)); }
warn() { echo "WARN  $*"; WARN=$((WARN+1)); }
miss() { echo "MISSING  $*"; WARN=$((WARN+1)); }
ver()  { "$@" 2>&1 | head -1 | cut -c1-70; }

echo "== php2shell handover verification — $(date -u +%Y-%m-%dT%H:%M:%SZ) — $(git rev-parse --short HEAD 2>/dev/null || echo 'no git')"

echo "-- 1. prerequisites"
if command -v python3 >/dev/null && python3 -c 'import sys; sys.exit(sys.version_info < (3,10))'; then
  pass "python3 $(python3 -c 'import platform;print(platform.python_version())') (need >= 3.10; checker container uses 3.12, box 3.13)"
else fail "python3 >= 3.10 not found"; fi
command -v git >/dev/null && pass "$(ver git --version)" || fail "git not found"
for t in curl rg node npm flock docker; do
  if command -v "$t" >/dev/null; then pass "$t: $(ver "$t" --version)"; else
    case "$t" in curl) warn "curl missing (needed only for --live)";; rg) warn "ripgrep missing (optional; ops/checks.py does not need it)";;
      node|npm) warn "$t missing (needed only for the case-study renderer, which is not in the repo yet — NEXT_TASK/MISSING)";;
      flock) warn "flock missing (needed only on the box for facts.json writes)";; docker) warn "docker missing (optional: build checker-api/Dockerfile)";; esac
  fi
done

echo "-- 2. repository data checks (ops/checks.py)"
python3 ops/checks.py | while IFS= read -r l; do echo "      $l"; done
if python3 ops/checks.py >/dev/null; then pass "ops/checks.py: facts, ledger, parity, paths, secrets"; else fail "ops/checks.py reported FAIL (see lines above)"; fi

echo "-- 3. checker-api unit tests"
PY=python3
if [ "$INSTALL" = 1 ]; then
  if [ ! -x "$VENV/bin/python" ]; then python3 -m venv "$VENV" >/dev/null 2>&1 || fail "could not create venv at $VENV"; fi
  if [ -x "$VENV/bin/python" ] && "$VENV/bin/pip" install -q -r checker-api/requirements.txt >/tmp/php2shell-pip.log 2>&1; then
    PY="$VENV/bin/python"; pass "pip install -r checker-api/requirements.txt in $VENV ($("$PY" -m pip freeze 2>/dev/null | grep -Ei '^(fastapi|uvicorn|pydantic|starlette)==' | tr '\n' ' '))"
  else fail "pip install failed (no network?) — see /tmp/php2shell-pip.log"; fi
fi
if "$PY" -c 'import fastapi, uvicorn' 2>/dev/null; then
  OUT="$(cd checker-api && "$PY" test_classify.py 2>&1)"; RC=$?
  NOK=$(printf '%s\n' "$OUT" | grep -c '^OK' || true); NFAIL=$(printf '%s\n' "$OUT" | grep -c '^FAIL' || true)
  # test_classify.py currently exits 0 even when a case FAILs (known defect, NEXT_TASK.md), so count lines.
  if [ "$RC" = 0 ] && [ "$NFAIL" = 0 ] && [ "$NOK" -ge 15 ]; then pass "test_classify.py: $NOK OK, $NFAIL FAIL, exit $RC"
  else fail "test_classify.py: $NOK OK, $NFAIL FAIL, exit $RC"; printf '%s\n' "$OUT" | grep -v '^OK' | sed 's/^/      /'; fi
  # local smoke test: loopback only, no outbound request (the 127.0.0.1 target is refused before any fetch)
  PORT=$(( 20000 + RANDOM % 20000 ))
  (cd checker-api && exec "$PY" -m uvicorn app:app --host 127.0.0.1 --port "$PORT" --no-access-log >/tmp/php2shell-uvicorn.log 2>&1) & UPID=$!
  for _ in $(seq 1 40); do curl -fs "http://127.0.0.1:$PORT/health" >/dev/null 2>&1 && break; sleep 0.25; done
  if command -v curl >/dev/null; then
    H=$(curl -s "http://127.0.0.1:$PORT/health"); C=$(curl -s -o /tmp/php2shell-blk.json -w '%{http_code}' "http://127.0.0.1:$PORT/check?url=http://127.0.0.1")
    if printf '%s' "$H" | grep -q '"ok":true' && [ "$C" = 400 ] && grep -q blocked_ip /tmp/php2shell-blk.json; then
      pass "local uvicorn smoke: /health ok, /check?url=http://127.0.0.1 -> 400 blocked_ip"
    else fail "local uvicorn smoke: health='$H' check_code=$C (log /tmp/php2shell-uvicorn.log)"; fi
  else warn "curl missing: local smoke test skipped"; fi
  kill "$UPID" 2>/dev/null; wait "$UPID" 2>/dev/null
else warn "fastapi/uvicorn not importable and --no-install given: checker tests SKIPPED"; fi

echo "-- 4. files the docs reference but the public repo does not contain (see ops/MISSING_FROM_REPO.md)"
for p in site/build.py site/template.html site/validate.py site/publish_pages.sh case-study/build/md2html.mjs case-study/build/package.json; do
  [ -e "$p" ] && pass "$p present" || miss "$p (box-only build pipeline; recovery path in ops/MISSING_FROM_REPO.md)"
done
for p in case-study/en.pdf; do [ -e "$p" ] && pass "$p present" || miss "$p (PDFs are not in the repo and not published)"; done
if git rev-parse -q --verify origin/gh-pages >/dev/null 2>&1 || git fetch -q origin gh-pages:refs/remotes/origin/gh-pages 2>/dev/null; then
  N=$(git ls-tree -r --name-only origin/gh-pages | wc -l)
  pass "origin/gh-pages fetched: $N files of built output (vendor JS, checker widget, built HTML are recoverable from here)"
  if git show origin/gh-pages:data/facts.json 2>/dev/null | cmp -s - data/facts.json; then pass "data/facts.json identical on HEAD and origin/gh-pages"
  else warn "data/facts.json differs between HEAD and origin/gh-pages (normal if the routine published in between, or you edited it)"; fi
else warn "could not fetch origin/gh-pages (offline or no remote)"; fi

echo "-- 5. owner-box environment (only meaningful on the original box; never prints values)"
BOX="${P2S_BOX:-/workspace/php-incident}"
if [ -d "$BOX/site" ]; then
  pass "box incident root found at $BOX"
  for f in site/validate.py site/build.py site/update_and_build.sh bible/build/package.json staging/surge-redirect/deploy_redirect.sh; do
    [ -f "$BOX/$f" ] && pass "box: $f" || fail "box: $f missing"; done
  for f in .render-credentials .surge-credentials; do [ -f "$BOX/$f" ] && pass "box: $f exists (contents not read)" || warn "box: $f absent"; done
  [ -f "$BOX/site/validate.py" ] && { python3 "$BOX/site/validate.py" data/facts.json >/dev/null 2>&1 && pass "box validate.py data/facts.json: exit 0" || fail "box validate.py rejected data/facts.json"; }
else miss "owner box not present ($BOX) — expected on a fresh machine"; fi
[ -n "${GITHUB_PAGES_TOKEN:-}" ] && pass "GITHUB_PAGES_TOKEN is set (value not shown)" || warn "GITHUB_PAGES_TOKEN not set (only needed to publish; see ops/env.example)"

if [ "$LIVE" = 1 ]; then
  echo "-- 6. live read-only checks (6 GETs, no load)"
  B=https://akirapl.github.io/php2shell
  c=$(curl -s -o /dev/null -w '%{http_code}' "$B/"); [ "$c" = 200 ] && pass "Pages $B/ -> 200" || fail "Pages $B/ -> $c"
  curl -s "$B/data/facts.json?t=$(date +%s)" -o /tmp/php2shell-live.json
  # compare parsed JSON, never grep raw bytes (CDN cache max-age=600 and key order/spacing caused false negatives)
  if python3 - "$ROOT/data/facts.json" /tmp/php2shell-live.json <<'PY'
import json,sys
a=json.load(open(sys.argv[1]));b=json.load(open(sys.argv[2]))
print("      live meta.last_updated", b["meta"]["last_updated"], "sources", len(b["sources"]), "| local", a["meta"]["last_updated"], len(a["sources"]))
PY
  then pass "live data/facts.json parses"; else fail "live data/facts.json did not parse"; fi
  c=$(curl -s "https://php2shell-live.surge.sh/robots.txt"); printf '%s' "$c" | grep -q 'Disallow: /' && pass "Surge redirect host robots: Disallow /" || warn "Surge robots unexpected: $c"
  H=$(curl -s -m 70 https://php2shell-checker.onrender.com/health); printf '%s' "$H" | grep -q '"ok":true' && pass "Render checker /health (cold start can take ~15-50 s)" || fail "Render checker /health: '$H'"
  c=$(curl -s -o /dev/null -w '%{http_code}' -m 30 "https://php2shell-checker.onrender.com/check?url=http://127.0.0.1"); [ "$c" = 400 ] && pass "Render checker SSRF guard: 127.0.0.1 -> 400" || fail "Render checker SSRF guard -> $c"
  c=$(curl -s -o /dev/null -w '%{http_code}' "$B/bible/en.pdf"); [ "$c" = 404 ] && warn "$B/bible/en.pdf -> 404 (known: PDFs unpublished)" || pass "$B/bible/en.pdf -> $c"
fi

echo "== summary: $PASS PASS, $FAILN FAIL, $WARN WARN/MISSING"
[ "$FAILN" = 0 ]
