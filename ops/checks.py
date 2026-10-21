#!/usr/bin/env python3
"""Repository consistency checks for php2shell (stdlib only, read-only).

Run from anywhere:  python3 ops/checks.py [--only NAME[,NAME...]]
Checks: facts, ledger, parity, paths, secrets.  Exit code 0 = all PASS, 1 = at least one FAIL.

This is NOT the box validator (site/validate.py, not in the repo yet, see ops/MISSING_FROM_REPO.md).
It re-implements the invariants that the docs promise, so a fresh clone can check them without the box.
"""
import csv, json, re, subprocess, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONF = {"confirmed", "reported", "estimate"}
LEDGER_STATUS = {"confirmed", "partially_confirmed", "conflicting", "unverified", "refuted"}
LANGS = ("pl", "en", "de")
# Files that may contain owner-box paths (/workspace/..., file://) ON PURPOSE: operational handover docs
# and ops templates. Everything else is public content and must not leak local paths (CHANGELOG v1.4 rule).
PATH_ALLOWLIST = ("HANDOVER.md", "AGENTS.md", "NEXT_TASK.md", "ops/")
SECRET_RE = re.compile(r"ghp_[A-Za-z0-9]{20,}|gh[ousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|rnd_[A-Za-z0-9]{10,}"
                       r"|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|xox[abprs]-[A-Za-z0-9-]{10,}"
                       r"|(?:SURGE_TOKEN|SURGE_PASSWORD|RENDER_PASSWORD|GITHUB_PAGES_TOKEN)\s*=\s*['\"]?[A-Za-z0-9_\-]{8,}")

results = []
def report(name, ok, msg):
    results.append((name, ok)); print(f"{'PASS' if ok else 'FAIL'}  {name}: {msg}")

def tracked():
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True)
    return [l for l in out.stdout.splitlines() if l] if out.returncode == 0 else [
        str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]

def walk(o, path=""):
    if isinstance(o, dict):
        yield path, o
        for k, v in o.items(): yield from walk(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from walk(v, f"{path}[{i}]")

def check_facts():
    p = ROOT / "data/facts.json"
    try: d = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e: return report("facts", False, f"data/facts.json does not parse: {e}")
    errs = []; conf = Counter(); n = 0
    for path, o in walk(d):
        if "confidence" in o:
            n += 1; conf[o["confidence"]] += 1
            if o["confidence"] not in CONF: errs.append(f"{path}: confidence={o['confidence']!r}")
            if not re.match(r"https?://", str(o.get("source_url", ""))): errs.append(f"{path}: no http(s) source_url")
    for i, s in enumerate(d.get("sources", [])):
        if not str(s.get("url", "")).startswith("https://"): errs.append(f"sources[{i}]: url not https")
    for path, o in walk(d):  # i18n objects must carry all three languages when one is present
        if path.endswith(".translations"): continue  # quote translations omit the original language by design
        if isinstance(o, dict) and set(o) & set(LANGS) and set(o) <= set(LANGS) | {"orig"}:
            miss = [l for l in LANGS if not o.get(l)]
            if miss: errs.append(f"{path}: missing {miss}")
    thr = d.get("status", {}).get("exploitation_threshold", {})
    if "KEV" not in str(thr.get("rule", "")): errs.append("status.exploitation_threshold.rule missing/unexpected")
    if d.get("status", {}).get("exploitation") == "confirmed" and not (thr.get("kev_listed") or thr.get("national_cert_itw")):
        errs.append("status.exploitation=confirmed but threshold (KEV or national CERT ITW) not met")
    if (ROOT / "data").exists() and any("/workspace" in json.dumps(o) for _, o in walk(d) if isinstance(o, dict) and "source_url" in o):
        errs.append("a source_url points at a local path")
    lists = {k: len(v) for k, v in d.items() if isinstance(v, list)}
    msg = (f"meta.last_updated={d.get('meta', {}).get('last_updated')} items with confidence={n} {dict(conf)} "
           f"exploitation={d.get('status', {}).get('exploitation')} kev_listed={thr.get('kev_listed')} lists={lists}")
    report("facts", not errs, msg if not errs else "; ".join(errs[:15]) + (f" (+{len(errs)-15} more)" if len(errs) > 15 else ""))

def check_ledger():
    j = ROOT / "case-study/evidence-ledger.jsonl"; c = ROOT / "case-study/evidence-ledger.csv"
    errs = []
    try: rows = [json.loads(l) for l in j.read_text(encoding="utf-8").splitlines() if l.strip()]
    except Exception as e: return report("ledger", False, f"JSONL does not parse: {e}")
    ids = [r.get("id") for r in rows]
    if ids != [f"CLM-{i:04d}" for i in range(1, len(ids) + 1)]: errs.append("ids not contiguous CLM-0001..")
    st = Counter(r.get("status") for r in rows)
    if set(st) - LEDGER_STATUS: errs.append(f"bad status values {set(st) - LEDGER_STATUS}")
    bad_url = [r["id"] for r in rows if not str(r.get("primary_source_url", "")).startswith("https://")]
    if bad_url: errs.append(f"non-https primary_source_url: {bad_url[:5]}")
    with c.open(encoding="utf-8", newline="") as f: crow = list(csv.DictReader(f))
    if [r.get("id") for r in crow] != ids: errs.append(f"CSV ids != JSONL ids (csv {len(crow)}, jsonl {len(rows)})")
    else:
        for a, b in zip(rows, crow):
            for k in ("claim", "status", "primary_source_url"):
                if str(a.get(k, "")) != b.get(k, ""): errs.append(f"{a['id']}.{k} differs CSV vs JSONL"); break
    gaps = sum(1 for r in rows if not r.get("claim_lang_source"))
    report("ledger", not errs, f"{len(rows)} rows {ids[0]}..{ids[-1]} status={dict(st)} csv_rows={len(crow)} "
           f"(info: claim_lang_source empty in {gaps})" if not errs else "; ".join(errs[:10]))

def md_profile(t):
    body = re.sub(r"```.*?```", "", t, flags=re.S)
    heads = [len(m.group(1)) for m in re.finditer(r"^(#{1,6}) ", body, re.M)]
    defs = re.findall(r"^\[\^([^\]]+)\]:", body, re.M)
    refs = re.findall(r"\[\^([^\]]+)\](?!:)", body)
    return {"lines": t.count("\n"), "heading_seq": heads, "fn_defs": sorted(defs), "fn_ref_count": len(refs),
            "fn_undefined": sorted(set(refs) - set(defs)), "fn_unused": sorted(set(defs) - set(refs)),
            "fn_dup": sorted(k for k, v in Counter(defs).items() if v > 1),
            "clm": sorted(set(re.findall(r"CLM-\d{4}", body))), "images": sorted(re.findall(r"!\[[^\]]*\]\(([^)\s]+)", body)),
            "urls": sorted(set(re.findall(r"https?://[^\s)\]>\"']+", body)))}

def check_parity():
    P = {l: md_profile((ROOT / f"case-study/{l}.md").read_text(encoding="utf-8")) for l in LANGS}
    errs = []
    for k in ("heading_seq", "fn_defs", "fn_ref_count", "clm", "images", "urls"):
        if not (P["pl"][k] == P["en"][k] == P["de"][k]): errs.append(f"{k} differs")
    for l in LANGS:
        for k in ("fn_undefined", "fn_unused", "fn_dup"):
            if P[l][k]: errs.append(f"{l}: {k}={P[l][k][:5]}")
    h = Counter(P["pl"]["heading_seq"])
    msg = (f"lines {[P[l]['lines'] for l in LANGS]} H1/H2/H3 {h[1]}/{h[2]}/{h[3]} fn refs/defs "
           f"{P['pl']['fn_ref_count']}/{len(P['pl']['fn_defs'])} CLM {len(P['pl']['clm'])} images {len(P['pl']['images'])} urls {len(P['pl']['urls'])}")
    report("parity", not errs, msg if not errs else "; ".join(errs))

def check_paths():
    hits = []
    for f in tracked():
        if f.startswith(PATH_ALLOWLIST) or f.endswith((".png", ".jpg")): continue
        try: t = (ROOT / f).read_text(encoding="utf-8")
        except Exception: continue
        for i, line in enumerate(t.splitlines(), 1):
            if "/workspace" in line or "file://" in line: hits.append(f"{f}:{i}")
    report("paths", not hits, "no /workspace or file:// outside the allowlist " + str(PATH_ALLOWLIST) if not hits
           else "local paths in public files: " + ", ".join(hits[:20]))

def check_secrets():
    hits = []
    for f in tracked():
        try: t = (ROOT / f).read_text(encoding="utf-8", errors="ignore")
        except Exception: continue
        for i, line in enumerate(t.splitlines(), 1):
            if SECRET_RE.search(line): hits.append(f"{f}:{i}")   # location only, never the value
    report("secrets", not hits, "no token/key patterns in tracked files" if not hits else "possible secret at " + ", ".join(hits))

CHECKS = {"facts": check_facts, "ledger": check_ledger, "parity": check_parity, "paths": check_paths, "secrets": check_secrets}
if __name__ == "__main__":
    only = None
    if "--only" in sys.argv: only = sys.argv[sys.argv.index("--only") + 1].split(",")
    for name, fn in CHECKS.items():
        if only and name not in only: continue
        try: fn()
        except Exception as e: report(name, False, f"crashed: {type(e).__name__}: {e}")
    sys.exit(0 if all(ok for _, ok in results) else 1)
