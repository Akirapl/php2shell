#!/usr/bin/env python3
"""Deterministic case-study annex A.2 from data/facts.json.

The annex is rebuilt from scratch on every run. No language model is called.
The daily job may open or update the single branch ``auto/casestudy-annex-a2``
and its pull request. It does not merge, it does not push ``main`` or
``gh-pages``, and it does not run the site publisher.

Heading anchors follow the live case-study renderer (verified against the
published bible HTML): Unicode letters are kept, and the spaces left behind
when punctuation such as an em dash is removed collapse to one hyphen.

    python3 ops/casestudy_annex.py
    python3 ops/test_casestudy_annex.py
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOG_PATH = Path("/home/akira/php2shell/logs/casestudy-annex.log")
BRANCH = "auto/casestudy-annex-a2"
ALLOWED_PUSH_REF = f"refs/heads/{BRANCH}"
AUTHOR_NAME = "Nygus (bot for @Akirapl)"
AUTHOR_EMAIL = "akira3179082@gmail.com"
MARKER_BEGIN = "<!-- CASESTUDY-ANNEX-A2:BEGIN -->"
MARKER_END = "<!-- CASESTUDY-ANNEX-A2:END -->"
LANGS = ("pl", "en", "de")
MD_PATHS = {lang: f"case-study/{lang}.md" for lang in LANGS}
BERLIN = ZoneInfo("Europe/Berlin")

HEADINGS = {
    "pl": "### Aneks A.2 \u2014 zdarzenia z facts.json od ostatniej aktualizacji studium",
    "en": "### Appendix A.2 \u2014 events from facts.json since the last case-study update",
    "de": "### Anhang A.2 \u2014 Ereignisse aus facts.json seit der letzten Aktualisierung der Fallstudie",
}
INTRO = {
    "pl": (
        "Ta lista jest generowana automatycznie z data/facts.json. Zawiera zdarzenia osi czasu, "
        "kt\u00f3rych id nie by\u0142o w facts.json w commicie bazowym {baseline}. Nie zast\u0119puje rozdzia\u0142\u00f3w "
        "1\u201312 ani r\u0119cznego Aneksu A. Stan fakt\u00f3w: {last_updated}. Pozycji: {count}. "
        "Nie edytuj tre\u015bci mi\u0119dzy markerami CASESTUDY-ANNEX-A2."
    ),
    "en": (
        "This list is generated automatically from data/facts.json. It contains timeline events whose "
        "ids were not present in facts.json at baseline commit {baseline}. It does not replace chapters "
        "1\u201312 or the hand-written Appendix A. Facts as of: {last_updated}. Entries: {count}. "
        "Do not edit the content between the CASESTUDY-ANNEX-A2 markers."
    ),
    "de": (
        "Diese Liste wird automatisch aus data/facts.json erzeugt. Sie enth\u00e4lt Zeitachsen-Ereignisse, "
        "deren IDs in facts.json im Basis-Commit {baseline} noch nicht vorkamen. Sie ersetzt nicht die "
        "Kapitel 1\u201312 und nicht den handgeschriebenen Anhang A. Stand der Fakten: {last_updated}. "
        "Eintr\u00e4ge: {count}. Den Inhalt zwischen den CASESTUDY-ANNEX-A2-Markern nicht bearbeiten."
    ),
}
EMPTY = {
    "pl": "_Brak zdarze\u0144 w facts.json nowszych ni\u017c commit bazowy._",
    "en": "_No facts.json events newer than the baseline commit._",
    "de": "_Keine facts.json-Ereignisse, die neuer als der Basis-Commit sind._",
}
FIELD_LABELS = {
    "pl": ("pewno\u015b\u0107", "waga", "rodzaj czasu"),
    "en": ("confidence", "importance", "time kind"),
    "de": ("Sicherheit", "Gewichtung", "Zeitart"),
}
ANNEX_B = {
    "pl": "## Aneks B: S\u0142owniczek",
    "en": "## Appendix B: Glossary",
    "de": "## Anhang B: Glossar",
}
TOC_A2_PREFIX = {
    "pl": "- [Aneks A.2:",
    "en": "- [Appendix A.2:",
    "de": "- [Anhang A.2:",
}
TOC_A_PREFIX = {
    "pl": "- [Aneks A:",
    "en": "- [Appendix A:",
    "de": "- [Anhang A:",
}
TOC_LABEL = {
    "pl": "Aneks A.2: Zdarzenia z facts.json",
    "en": "Appendix A.2: Events from facts.json",
    "de": "Anhang A.2: Ereignisse aus facts.json",
}
SECRET_RE = re.compile(r"ghp_[A-Za-z0-9]+|gh[ousr]_[A-Za-z0-9]+|github_pat_[A-Za-z0-9_]+")


class AnnexError(Exception):
    def __init__(self, message, code="fail"):
        super().__init__(message)
        self.code = code


def slugify_heading(text):
    """Slug used by the published case-study HTML.

    Lowercase, drop characters that are not Unicode letters, numbers or
    hyphens, then collapse the remaining whitespace to a single hyphen.
    """
    buf = []
    for ch in text.lower():
        if ch.isalnum() or ch == "-":
            buf.append(ch)
        elif ch.isspace():
            buf.append(" ")
    return re.sub(r"[ -]+", "-", "".join(buf)).strip("-")


def heading_slug(lang):
    return slugify_heading(HEADINGS[lang][4:])


def _parse_time(value):
    if not isinstance(value, str):
        raise AnnexError(f"invalid time_utc {value!r}")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return datetime.fromisoformat(value + "T00:00:00+00:00")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AnnexError(f"invalid time_utc {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def format_event_time(time_utc, precision):
    if isinstance(time_utc, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", time_utc):
        return f"{time_utc} UTC"
    parsed = _parse_time(time_utc)
    if precision == "day":
        return parsed.strftime("%Y-%m-%d UTC")
    if precision == "hour":
        return parsed.strftime("%Y-%m-%d %H:00 UTC")
    if precision == "minute":
        return parsed.strftime("%Y-%m-%d %H:%M UTC")
    return parsed.strftime("%Y-%m-%d %H:%M:%S UTC")


def _require_event(event):
    event_id = event.get("id")
    title = event.get("title")
    if not isinstance(title, dict):
        raise AnnexError(f"incomplete i18n for {event_id}: title")
    for lang in LANGS:
        if not title.get(lang):
            raise AnnexError(f"incomplete i18n for {event_id}: {lang}")
    for field in ("id", "time_utc", "confidence", "importance", "time_kind", "source_name", "source_url"):
        if not event.get(field):
            raise AnnexError(f"missing {field} for {event_id}")


def _timeline_ids(facts, label):
    timeline = facts.get("timeline")
    if not isinstance(timeline, list):
        raise AnnexError(f"{label} timeline is missing")
    ids = []
    for event in timeline:
        if not isinstance(event, dict) or not event.get("id"):
            raise AnnexError(f"{label} timeline item is missing id")
        ids.append(event["id"])
    if len(ids) != len(set(ids)):
        raise AnnexError(f"duplicate timeline id in {label}")
    return timeline


def annex_events(current, baseline):
    current_items = _timeline_ids(current, "current")
    baseline_items = _timeline_ids(baseline, "baseline")
    base_ids = {event["id"] for event in baseline_items}
    chosen = []
    for event in current_items:
        if event["id"] in base_ids:
            continue
        _require_event(event)
        chosen.append(event)
    chosen.sort(key=lambda event: (_parse_time(event["time_utc"]), event["id"]))
    return chosen


def render_event_line(lang, event):
    _require_event(event)
    when = format_event_time(event["time_utc"], event.get("time_precision"))
    confidence, importance, kind = FIELD_LABELS[lang]
    return (
        f"- **{when}** \u2014 {event['title'][lang]} (`{event['id']}`) \u2014 "
        f"{confidence}: `{event['confidence']}`, {importance}: `{event['importance']}`, "
        f"{kind}: `{event['time_kind']}` \u2014 "
        f"[{event['source_name']}]({event['source_url']})"
    )


def render_region(lang, events, baseline, last_updated):
    if lang not in INTRO:
        raise AnnexError(f"unknown language {lang}")
    ordered = sorted(events, key=lambda event: (_parse_time(event["time_utc"]), event["id"]))
    lines = [
        MARKER_BEGIN,
        HEADINGS[lang],
        "",
        INTRO[lang].format(baseline=baseline, last_updated=last_updated, count=len(ordered)),
        "",
    ]
    if ordered:
        lines.extend(render_event_line(lang, event) for event in ordered)
    else:
        lines.append(EMPTY[lang])
    lines.append(MARKER_END)
    return "\n".join(lines) + "\n"


def _line_ending(line):
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    return ""


def _toc_target(line):
    match = re.search(r"\]\(#([^)]*)\)", line)
    return match.group(1) if match else None


def _ensure_toc(text, lang, slug):
    lines = text.splitlines(keepends=True)
    a2 = [i for i, line in enumerate(lines) if line.startswith(TOC_A2_PREFIX[lang])]
    if len(a2) > 1:
        raise AnnexError("multiple annex A.2 contents lines")
    if len(a2) == 1:
        line = lines[a2[0]]
        if _toc_target(line) == slug:
            return text
        new_line, count = re.subn(r"\]\(#[^)]*\)", f"](#{slug})", line, count=1)
        if count != 1:
            raise AnnexError("annex A.2 contents line has no anchor")
        lines[a2[0]] = new_line
        return "".join(lines)
    appendix_a = [i for i, line in enumerate(lines) if line.startswith(TOC_A_PREFIX[lang])]
    if len(appendix_a) != 1:
        raise AnnexError("missing Appendix A contents line")
    index = appendix_a[0]
    canon = f"- [{TOC_LABEL[lang]}](#{slug})" + _line_ending(lines[index] or "\n")
    lines.insert(index + 1, canon)
    return "".join(lines)


def _replace_or_insert_region(text, lang, region):
    begins = [match.start() for match in re.finditer(re.escape(MARKER_BEGIN), text)]
    ends = [match.start() for match in re.finditer(re.escape(MARKER_END), text)]
    if not begins and not ends:
        matches = list(re.finditer("^" + re.escape(ANNEX_B[lang]) + "$", text, re.M))
        if len(matches) != 1:
            raise AnnexError(f"expected exactly one {ANNEX_B[lang]!r} heading")
        at = matches[0].start()
        return text[:at] + region + text[at:]
    if len(begins) != 1 or len(ends) != 1 or ends[0] < begins[0]:
        raise AnnexError("unpaired CASESTUDY-ANNEX-A2 markers")
    end = ends[0] + len(MARKER_END)
    if text[end:end + 1] == "\n":
        end += 1
    return text[:begins[0]] + region + text[end:]


def apply_document(text, lang, region):
    if lang not in LANGS:
        raise AnnexError(f"unknown language {lang}")
    if not region.endswith("\n"):
        region += "\n"
    return _ensure_toc(_replace_or_insert_region(text, lang, region), lang, heading_slug(lang))


def assert_push_destination(refspec):
    dest = refspec.split(":")[-1]
    if dest.startswith("+"):
        dest = dest[1:]
    if dest != ALLOWED_PUSH_REF:
        raise AnnexError(f"refusing to push {dest}")
    return dest


def checks_argv(worktree):
    return [sys.executable, str(Path(worktree) / "ops" / "checks.py"), "--only", "parity,paths,secrets,facts"]


def default_checks(worktree):
    result = subprocess.run(checks_argv(worktree), cwd=worktree, capture_output=True, text=True, encoding="utf-8")
    return result.returncode


def scrub(text):
    cleaned = SECRET_RE.sub("[redacted]", str(text)).replace("\n", " ")
    return cleaned[:240]


def _log_stamp(now):
    local = now.astimezone(BERLIN)
    offset = local.strftime("%z")
    offset = offset[:3] + ":" + offset[3:]
    return f"{local.strftime('%Y-%m-%dT%H:%M:%S')}{offset} Europe/Berlin"


class _Log:
    def __init__(self, path, now):
        self.path = Path(path)
        self.now = now

    def write(self, event):
        line = f"{_log_stamp(self.now)} {scrub(event)}\n"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line)


def _git_env():
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
    env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
    return env


def _git(repo, args, runner, check=True):
    cmd = ["git", "-C", str(repo), *args]
    result = runner(cmd, capture_output=True, text=True, encoding="utf-8", env=_git_env())
    if check and result.returncode != 0:
        raise AnnexError("git " + " ".join(args) + " failed")
    return result


def _git_show(repo, spec, runner):
    result = _git(repo, ["show", spec], runner, check=False)
    if result.returncode != 0:
        return None
    return result.stdout


def _parse_baseline(text):
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(stripped)
    if not lines:
        raise AnnexError("baseline file is empty", code="baseline-missing")
    if len(lines) != 1 or not re.fullmatch(r"[0-9a-f]{40}", lines[0]):
        raise AnnexError("baseline is not a full sha", code="baseline-invalid")
    return lines[0]


def _branch_exists(repo, runner):
    result = _git(repo, ["rev-parse", "--verify", "--quiet", f"refs/remotes/origin/{BRANCH}"], runner, check=False)
    return result.returncode == 0


def _event_lines(text):
    if MARKER_BEGIN not in text or MARKER_END not in text:
        return {}
    region = text.split(MARKER_BEGIN, 1)[1].split(MARKER_END, 1)[0]
    found = {}
    for line in region.splitlines():
        match = re.search(r"\(`([^`]+)`\)", line)
        if match:
            found[match.group(1)] = line
    return found


def _id_delta(old, new):
    added = [item for item in new if item not in old]
    removed = [item for item in old if item not in new]
    changed = [item for item in new if item in old and old[item] != new[item]]
    return added, removed, changed


def _bullet(ids):
    if not ids:
        return "- (brak)"
    return "\n".join(f"- `{item}`" for item in ids)


def _pr_title(baseline):
    return f"case-study: aneks A.2 z facts.json (baseline {baseline[:12]})"


def _pr_body(baseline, last_updated, added, removed):
    return (
        "Automatyczny aneks A.2 studium przypadku (generator deterministyczny, bez LLM).\n\n"
        f"Baseline: `{baseline}`\n"
        f"Stan fakt\u00f3w (`meta.last_updated`): `{last_updated}`\n\n"
        "Id dodane wzgl\u0119dem aneksu na `main`:\n"
        f"{_bullet(added)}\n\n"
        "Id usuni\u0119te wzgl\u0119dem aneksu na `main`:\n"
        f"{_bullet(removed)}\n\n"
        "Uwaga: nie scala\u0107 automatycznie; recenzja @Akirapl; nie publikowa\u0107 z tego PR-a.\n\n"
        "Aktor GitHub: Akira0bot. Autor commita: Nygus (bot for @Akirapl).\n"
    )


def _delta_comment(added, removed, changed):
    return (
        "Aktualizacja aneksu A.2 wzgl\u0119dem poprzedniej wersji ga\u0142\u0119zi.\n\n"
        "Dodane:\n"
        f"{_bullet(added)}\n\n"
        "Usuni\u0119te:\n"
        f"{_bullet(removed)}\n\n"
        "Zmienione:\n"
        f"{_bullet(changed)}\n"
    )


def _reject_foreign_branch(repo, runner):
    if not _branch_exists(repo, runner):
        return
    result = _git(repo, ["diff", "--name-only", f"origin/main...origin/{BRANCH}"], runner)
    foreign = [name for name in result.stdout.splitlines() if name and name not in MD_PATHS.values()]
    if foreign:
        raise AnnexError("annex branch changes files outside case-study pl/en/de: " + ", ".join(foreign))


def _branch_matches(repo, desired, runner):
    if not _branch_exists(repo, runner):
        return False
    for path in MD_PATHS.values():
        if _git_show(repo, f"origin/{BRANCH}:{path}", runner) != desired[path]:
            return False
    parent = _git(repo, ["rev-parse", f"origin/{BRANCH}^"], runner, check=False)
    main = _git(repo, ["rev-parse", "origin/main"], runner).stdout.strip()
    return parent.returncode == 0 and parent.stdout.strip() == main


def _push(repo, sha, runner, update):
    refspec = f"{sha}:{ALLOWED_PUSH_REF}"
    assert_push_destination(refspec)
    cmd = ["git", "-C", str(repo), "push"]
    if update:
        cmd.append(f"--force-with-lease={ALLOWED_PUSH_REF}")
    cmd.extend(["origin", refspec])
    result = runner(cmd, capture_output=True, text=True, encoding="utf-8", env=_git_env())
    if result.returncode != 0:
        raise AnnexError("git push failed")


def _commit_desired(repo, desired, baseline, checks, runner):
    parent = Path(tempfile.mkdtemp(prefix="casestudy-annex-"))
    worktree = parent / "wt"
    try:
        _git(repo, ["worktree", "add", "--detach", str(worktree), "origin/main"], runner)
        for path, text in desired.items():
            target = worktree / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        status = (checks or default_checks)(worktree)
        if status != 0:
            raise AnnexError("ops/checks.py failed; not pushing")
        _git(worktree, ["add", "--", *MD_PATHS.values()], runner)
        commit = runner(
            [
                "git", "-C", str(worktree),
                "-c", f"user.name={AUTHOR_NAME}",
                "-c", f"user.email={AUTHOR_EMAIL}",
                "-c", "commit.gpgsign=false",
                "commit", "-m", _pr_title(baseline),
            ],
            capture_output=True, text=True, encoding="utf-8", env=_git_env(),
        )
        if commit.returncode != 0:
            raise AnnexError("git commit failed")
        names = _git(worktree, ["diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"], runner).stdout.splitlines()
        extra = [name for name in names if name not in MD_PATHS.values()]
        if extra:
            raise AnnexError("commit includes unexpected files: " + ", ".join(extra))
        return _git(worktree, ["rev-parse", "HEAD"], runner).stdout.strip()
    finally:
        try:
            runner(
                ["git", "-C", str(repo), "worktree", "remove", "--force", str(worktree)],
                capture_output=True, text=True, encoding="utf-8", env=_git_env(),
            )
        except Exception:
            pass
        shutil.rmtree(parent, ignore_errors=True)


def _open_or_update(github, log, *, title, body, comment):
    prs = github.open_prs(BRANCH)
    if len(prs) > 1:
        raise AnnexError("more than one open annex pull request")
    if prs:
        number = prs[0]["number"]
        github.update_pr(number, title=title, body=body)
        github.comment(number, comment)
        log.write(f"pr-updated #{number}")
        return
    number = github.create_pr(title=title, body=body, head=BRANCH, base="main", reviewer="Akirapl")
    log.write(f"pr-opened #{number}")


def _run_job(repo, github, checks, runner, log):
    _git(repo, ["fetch", "origin", "main"], runner)
    _git(
        repo,
        ["fetch", "origin", f"refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}"],
        runner,
        check=False,
    )
    baseline_text = _git_show(repo, "origin/main:case-study/annex-baseline", runner)
    if baseline_text is None:
        raise AnnexError("baseline file missing on origin/main", code="baseline-missing")
    baseline = _parse_baseline(baseline_text)
    baseline_facts_text = _git_show(repo, f"{baseline}:data/facts.json", runner)
    if baseline_facts_text is None:
        raise AnnexError("baseline sha does not contain data/facts.json", code="baseline-invalid")
    current_text = _git_show(repo, "origin/main:data/facts.json", runner)
    if current_text is None:
        raise AnnexError("origin/main has no data/facts.json")
    try:
        baseline_facts = json.loads(baseline_facts_text)
        current_facts = json.loads(current_text)
    except json.JSONDecodeError as exc:
        raise AnnexError("facts.json does not parse") from exc
    last_updated = current_facts.get("meta", {}).get("last_updated")
    if not last_updated:
        raise AnnexError("meta.last_updated missing")
    events = annex_events(current_facts, baseline_facts)
    originals = {}
    for lang, path in MD_PATHS.items():
        text = _git_show(repo, f"origin/main:{path}", runner)
        if text is None:
            raise AnnexError(f"missing {path} on origin/main")
        originals[lang] = text
    desired_by_lang = {}
    for lang, text in originals.items():
        desired_by_lang[lang] = apply_document(text, lang, render_region(lang, events, baseline, last_updated))
    desired = {MD_PATHS[lang]: text for lang, text in desired_by_lang.items()}
    original_paths = {MD_PATHS[lang]: text for lang, text in originals.items()}
    if desired == original_paths:
        log.write("no-change")
        return 0

    _reject_foreign_branch(repo, runner)
    main_ids = _event_lines(originals["pl"])
    new_ids = _event_lines(desired_by_lang["pl"])
    added, removed, _changed = _id_delta(main_ids, new_ids)
    title = _pr_title(baseline)
    body = _pr_body(baseline, last_updated, added, removed)

    if _branch_matches(repo, desired, runner):
        prs = github.open_prs(BRANCH)
        if len(prs) > 1:
            raise AnnexError("more than one open annex pull request")
        if prs:
            log.write("no-change")
            return 0
        number = github.create_pr(title=title, body=body, head=BRANCH, base="main", reviewer="Akirapl")
        log.write(f"pr-opened #{number}")
        return 0

    previous = {}
    if _branch_exists(repo, runner):
        for path in MD_PATHS.values():
            shown = _git_show(repo, f"origin/{BRANCH}:{path}", runner)
            if shown is not None:
                previous[path] = shown
    else:
        previous = dict(original_paths)
    old_ids = _event_lines(previous.get(MD_PATHS["pl"], ""))
    branch_added, branch_removed, branch_changed = _id_delta(old_ids, new_ids)
    sha = _commit_desired(repo, desired, baseline, checks, runner)
    _push(repo, sha, runner, update=_branch_exists(repo, runner))
    _open_or_update(
        github,
        log,
        title=title,
        body=body,
        comment=_delta_comment(branch_added, branch_removed, branch_changed),
    )
    return 0


def run_job(repo, *, log_path, github, now=None, checks=None, run=None):
    moment = now or datetime.now(timezone.utc)
    log = _Log(log_path, moment)
    runner = run or subprocess.run
    code = 1
    try:
        log.write("start")
        code = _run_job(Path(repo), github, checks, runner, log)
    except AnnexError as exc:
        if exc.code == "baseline-missing":
            log.write("baseline-missing")
        elif exc.code == "baseline-invalid":
            log.write("baseline-invalid")
        else:
            log.write("fail " + str(exc))
        code = 1
    except Exception as exc:
        log.write("fail " + str(exc))
        code = 1
    log.write(f"end exit={code}")
    return code


class GhClient:
    """Pull-request client for the logged-in ``gh`` user. Never merges."""

    def __init__(self, repo):
        self.repo = Path(repo)

    def _run(self, args):
        result = subprocess.run(["gh", *args], cwd=self.repo, capture_output=True, text=True, encoding="utf-8")
        if result.returncode != 0:
            raise AnnexError(scrub(result.stderr.strip() or "gh failed"))
        return result.stdout

    def open_prs(self, head):
        raw = self._run([
            "pr", "list", "--head", head, "--base", "main", "--state", "open", "--json", "number,title",
        ])
        data = json.loads(raw or "[]")
        return [
            {"number": item["number"], "title": item.get("title", ""), "head": head, "base": "main", "state": "open"}
            for item in data
        ]

    def _body_file(self, body):
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False)
        try:
            handle.write(body)
            handle.close()
            return handle.name
        except Exception:
            handle.close()
            os.unlink(handle.name)
            raise

    def create_pr(self, *, title, body, head, base, reviewer):
        path = self._body_file(body)
        try:
            raw = self._run([
                "pr", "create", "--base", base, "--head", head, "--title", title,
                "--body-file", path, "--reviewer", reviewer,
            ])
        finally:
            os.unlink(path)
        match = re.search(r"/pull/(\d+)", raw)
        if not match:
            raise AnnexError("gh pr create returned no pull request number")
        return int(match.group(1))

    def comment(self, number, body):
        path = self._body_file(body)
        try:
            self._run(["pr", "comment", str(number), "--body-file", path])
        finally:
            os.unlink(path)

    def update_pr(self, number, *, title, body):
        path = self._body_file(body)
        try:
            self._run(["pr", "edit", str(number), "--title", title, "--body-file", path])
        finally:
            os.unlink(path)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Rebuild case-study annex A.2 and open or update one PR.")
    parser.add_argument("--repo", default=str(ROOT))
    parser.add_argument("--log", default=str(DEFAULT_LOG_PATH))
    args = parser.parse_args(argv)
    return run_job(Path(args.repo), log_path=Path(args.log), github=GhClient(Path(args.repo)))


if __name__ == "__main__":
    sys.exit(main())
