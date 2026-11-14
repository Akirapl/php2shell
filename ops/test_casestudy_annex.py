#!/usr/bin/env python3
"""Tests for the deterministic case-study annex A.2 generator.

Run from a fresh clone:  python3 ops/test_casestudy_annex.py
Stdlib only. No GitHub API, no systemd install, no publish/ship.
"""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import casestudy_annex as annex

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "7e6e710964dc34d4464703d659de454d498dd22e"
LAST = "2026-11-10T18:05:02Z"
SOURCE_NAME = "CISA — Critical Vulnerabilities in PHP Require Immediate Patching"
SOURCE_URL = "https://www.cisa.gov/news-events/alerts/2026/10/21/critical-vulnerabilities-php-require-immediate-patching"
CISA_ID = "cisa-kev-php2shell"
BEGIN = "<!-- CASESTUDY-ANNEX-A2:BEGIN -->"
END = "<!-- CASESTUDY-ANNEX-A2:END -->"

SKELETONS = {
    "pl": """\
## 1. Rozdział

Tekst rozdziału zostaje.

## Spis treści

- [Aneks A: Oś czasu](#aneks-a-pelna-os-czasu)
- [Aneks B: Słowniczek](#aneks-b-slowniczek)

## Aneks A: Pełna oś czasu

UNIKALNY-TEKST-ANEKSU-A

---

## Aneks B: Słowniczek

| Termin | Znaczenie |
|---|---|
| **SAPI** | Server API |
""",
    "en": """\
## 1. Chapter

Chapter text stays.

## Contents

- [Appendix A: Full timeline](#appendix-a-full-timeline)
- [Appendix B: Glossary](#appendix-b-glossary)

## Appendix A: Full timeline

UNIQUE-APPENDIX-A

---

## Appendix B: Glossary

| Term | Meaning |
|---|---|
| **SAPI** | Server API |
""",
    "de": """\
## 1. Kapitel

Kapiteltext bleibt.

## Inhaltsverzeichnis

- [Anhang A: Zeitachse](#anhang-a-vollstandige-zeitachse)
- [Anhang B: Glossar](#anhang-b-glossar)

## Anhang A: Vollständige Zeitachse

EINZIGARTIGER-ANHANG-A

---

## Anhang B: Glossar

| Begriff | Bedeutung |
|---|---|
| **SAPI** | Server API |
""",
}

PL_REGION = f"""\
{BEGIN}
### Aneks A.2 — zdarzenia z facts.json od ostatniej aktualizacji studium

Ta lista jest generowana automatycznie z data/facts.json. Zawiera zdarzenia osi czasu, których id nie było w facts.json w commicie bazowym {BASELINE}. Nie zastępuje rozdziałów 1–12 ani ręcznego Aneksu A. Stan faktów: {LAST}. Pozycji: 1. Nie edytuj treści między markerami CASESTUDY-ANNEX-A2.

- **2026-10-26 UTC** — CISA dodaje PHP2Shell do katalogu KEV (`{CISA_ID}`) — pewność: `confirmed`, waga: `critical`, rodzaj czasu: `published` — [{SOURCE_NAME}]({SOURCE_URL})
{END}
"""

EN_REGION = f"""\
{BEGIN}
### Appendix A.2 — events from facts.json since the last case-study update

This list is generated automatically from data/facts.json. It contains timeline events whose ids were not present in facts.json at baseline commit {BASELINE}. It does not replace chapters 1–12 or the hand-written Appendix A. Facts as of: {LAST}. Entries: 1. Do not edit the content between the CASESTUDY-ANNEX-A2 markers.

- **2026-10-26 UTC** — CISA adds PHP2Shell to KEV Catalog (`{CISA_ID}`) — confidence: `confirmed`, importance: `critical`, time kind: `published` — [{SOURCE_NAME}]({SOURCE_URL})
{END}
"""

DE_REGION = f"""\
{BEGIN}
### Anhang A.2 — Ereignisse aus facts.json seit der letzten Aktualisierung der Fallstudie

Diese Liste wird automatisch aus data/facts.json erzeugt. Sie enthält Zeitachsen-Ereignisse, deren IDs in facts.json im Basis-Commit {BASELINE} noch nicht vorkamen. Sie ersetzt nicht die Kapitel 1–12 und nicht den handgeschriebenen Anhang A. Stand der Fakten: {LAST}. Einträge: {1}. Den Inhalt zwischen den CASESTUDY-ANNEX-A2-Markern nicht bearbeiten.

- **2026-10-26 UTC** — CISA fügt PHP2Shell zum KEV-Katalog hinzu (`{CISA_ID}`) — Sicherheit: `confirmed`, Gewichtung: `critical`, Zeitart: `published` — [{SOURCE_NAME}]({SOURCE_URL})
{END}
"""

PL_EMPTY = f"""\
{BEGIN}
### Aneks A.2 — zdarzenia z facts.json od ostatniej aktualizacji studium

Ta lista jest generowana automatycznie z data/facts.json. Zawiera zdarzenia osi czasu, których id nie było w facts.json w commicie bazowym {BASELINE}. Nie zastępuje rozdziałów 1–12 ani ręcznego Aneksu A. Stan faktów: {LAST}. Pozycji: 0. Nie edytuj treści między markerami CASESTUDY-ANNEX-A2.

_Brak zdarzeń w facts.json nowszych niż commit bazowy._
{END}
"""


def cisa_event(**overrides):
    event = {
        "id": CISA_ID,
        "time_utc": "2026-10-26T12:00:00Z",
        "time_precision": "day",
        "importance": "critical",
        "confidence": "confirmed",
        "time_kind": "published",
        "source_name": SOURCE_NAME,
        "source_url": SOURCE_URL,
        "title": {
            "pl": "CISA dodaje PHP2Shell do katalogu KEV",
            "en": "CISA adds PHP2Shell to KEV Catalog",
            "de": "CISA fügt PHP2Shell zum KEV-Katalog hinzu",
        },
        "description": {
            "pl": "NIE-WOLNO-OPISU",
            "en": "DO-NOT-INCLUDE-DESCRIPTION",
            "de": "BESCHREIBUNG-NICHT-AUSGEBEN",
        },
        "actors": ["NIE-WOLNO-AKTOR"],
        "flags": ["needs_second_source"],
        "flag_note": {"pl": "NIE-WOLNO-FLAGI", "en": "NO-FLAG", "de": "KEINE-FLAGGE"},
    }
    event.update(overrides)
    return event


def facts(events, last_updated=LAST):
    return {"meta": {"last_updated": last_updated}, "timeline": events}


def old_event():
    return cisa_event(id="wiz-discovery", time_utc="2026-08-19", time_precision="day",
                      title={"pl": "Stare", "en": "Old", "de": "Alt"})


class TimeSortRenderTests(unittest.TestCase):
    def test_day_precision_drops_clock_even_when_time_is_present(self):
        self.assertEqual(annex.format_event_time("2026-10-26T12:00:00Z", "day"), "2026-10-26 UTC")

    def test_hour_minute_second_and_unknown_precision(self):
        stamp = "2026-10-26T15:45:30Z"
        self.assertEqual(annex.format_event_time(stamp, "hour"), "2026-10-26 15:00 UTC")
        self.assertEqual(annex.format_event_time(stamp, "minute"), "2026-10-26 15:45 UTC")
        self.assertEqual(annex.format_event_time(stamp, "second"), "2026-10-26 15:45:30 UTC")
        self.assertEqual(annex.format_event_time(stamp, "week"), "2026-10-26 15:45:30 UTC")
        self.assertEqual(annex.format_event_time(stamp, None), "2026-10-26 15:45:30 UTC")

    def test_date_only_value_stays_a_date_for_any_precision(self):
        self.assertEqual(annex.format_event_time("2026-08-19", "minute"), "2026-08-19 UTC")
        self.assertEqual(annex.format_event_time("2026-08-19", "second"), "2026-08-19 UTC")

    def test_invalid_time_is_an_error(self):
        with self.assertRaises(annex.AnnexError):
            annex.format_event_time("yesterday", "day")

    def test_sorts_by_utc_then_id_and_treats_a_bare_date_as_midnight(self):
        events = [
            cisa_event(id="late", time_utc="2026-10-27T00:00:00Z"),
            cisa_event(id="zzz", time_utc="2026-10-26T00:00:00Z"),
            cisa_event(id="aaa", time_utc="2026-10-26"),
        ]
        chosen = annex.annex_events(facts(events), facts([]))
        self.assertEqual([e["id"] for e in chosen], ["aaa", "zzz", "late"])

    def test_polish_region_matches_golden_fragment(self):
        region = annex.render_region("pl", [cisa_event()], BASELINE, LAST)
        self.assertEqual(region, PL_REGION)

    def test_english_and_german_regions_match_golden_fragments(self):
        self.assertEqual(annex.render_region("en", [cisa_event()], BASELINE, LAST), EN_REGION)
        self.assertEqual(annex.render_region("de", [cisa_event()], BASELINE, LAST), DE_REGION)

    def test_languages_share_order_ids_and_urls_but_use_their_own_titles(self):
        events = annex.annex_events(
            facts([
                cisa_event(id="b", time_utc="2026-10-27T01:00:00Z", time_precision="hour"),
                cisa_event(),
            ]),
            facts([old_event()]),
        )
        regions = {lang: annex.render_region(lang, events, BASELINE, LAST) for lang in ("pl", "en", "de")}
        ids = {lang: re.findall(r"\(`([^`]+)`\)", text) for lang, text in regions.items()}
        self.assertEqual(ids["pl"], ids["en"])
        self.assertEqual(ids["en"], ids["de"])
        self.assertEqual(ids["pl"], [CISA_ID, "b"])
        urls = {lang: sorted(set(re.findall(r"https?://[^\s)]+", text))) for lang, text in regions.items()}
        self.assertEqual(urls["pl"], urls["en"])
        self.assertEqual(urls["en"], urls["de"])
        self.assertIn("CISA dodaje PHP2Shell do katalogu KEV", regions["pl"])
        self.assertIn("CISA adds PHP2Shell to KEV Catalog", regions["en"])
        self.assertIn("CISA fügt PHP2Shell zum KEV-Katalog hinzu", regions["de"])
        self.assertIn("Sicherheit: `confirmed`", regions["de"])

    def test_omits_description_actors_flags_and_job_clock(self):
        region = annex.render_region("pl", [cisa_event()], BASELINE, LAST)
        for banned in ("NIE-WOLNO-OPISU", "NIE-WOLNO-AKTOR", "NIE-WOLNO-FLAGI", "needs_second_source"):
            self.assertNotIn(banned, region)
        self.assertNotIn("T07:", region)
        self.assertIn(LAST, region)

    def test_empty_annex_keeps_heading_intro_and_placeholder(self):
        region = annex.render_region("pl", [], BASELINE, LAST)
        self.assertEqual(region, PL_EMPTY)
        self.assertNotRegex(region, r"(?m)^- \*\*")
        self.assertIn("_No facts.json events newer than the baseline commit._",
                      annex.render_region("en", [], BASELINE, LAST))
        self.assertIn("_Keine facts.json-Ereignisse, die neuer als der Basis-Commit sind._",
                      annex.render_region("de", [], BASELINE, LAST))

    def test_two_renders_are_byte_identical(self):
        events = [cisa_event()]
        self.assertEqual(
            annex.render_region("pl", events, BASELINE, LAST),
            annex.render_region("pl", events, BASELINE, LAST),
        )

    def test_title_or_source_change_rewrites_the_line(self):
        updated = cisa_event(
            title={"pl": "Nowy tytuł", "en": "New title", "de": "Neuer Titel"},
            source_name="Inne źródło",
            source_url="https://example.com/inne",
        )
        before = annex.render_region("pl", [cisa_event()], BASELINE, LAST)
        after = annex.render_region("pl", [updated], BASELINE, LAST)
        self.assertIn("Nowy tytuł", after)
        self.assertIn("https://example.com/inne", after)
        self.assertNotIn("CISA dodaje PHP2Shell do katalogu KEV", after)
        self.assertNotEqual(before, after)
        self.assertIn(f"(`{CISA_ID}`)", after)

    def test_removing_an_id_from_facts_drops_its_line(self):
        base = facts([old_event()])
        with_new = facts([old_event(), cisa_event()])
        present = annex.render_region("pl", annex.annex_events(with_new, base), BASELINE, LAST)
        self.assertIn(CISA_ID, present)
        gone = annex.render_region("pl", annex.annex_events(base, base), BASELINE, LAST)
        self.assertNotIn(CISA_ID, gone)
        self.assertIn("_Brak zdarzeń", gone)

    def test_baseline_ids_are_excluded_even_if_still_present(self):
        base = facts([old_event()])
        current = facts([old_event(), cisa_event()])
        chosen = annex.annex_events(current, base)
        self.assertEqual([e["id"] for e in chosen], [CISA_ID])

    def test_missing_title_language_is_an_error(self):
        broken = cisa_event(title={"pl": "Tylko polski", "en": "English only"})
        with self.assertRaises(annex.AnnexError) as caught:
            annex.render_region("de", [broken], BASELINE, LAST)
        self.assertIn(CISA_ID, str(caught.exception))
        self.assertIn("de", str(caught.exception))

    def test_duplicate_ids_are_an_error(self):
        with self.assertRaises(annex.AnnexError):
            annex.annex_events(facts([cisa_event(), cisa_event()]), facts([]))


class SlugAndApplyTests(unittest.TestCase):
    def test_slug_matches_live_bible_renderer(self):
        # Published bible HTML (markdown-it / md2html.mjs) keeps Unicode letters
        # and collapses whitespace left by removed punctuation into one hyphen.
        samples = {
            "2. Podatności — wyjaśnione w głąb": "2-podatności-wyjaśnione-w-głąb",
            "Aneks A: Pełna oś czasu": "aneks-a-pełna-oś-czasu",
            "0. TL;DR und Ein-Seiten-Überblick": "0-tldr-und-ein-seiten-überblick",
            "8. Defenders’ response": "8-defenders-response",
            "Anhang A: Vollständige Zeitachse": "anhang-a-vollständige-zeitachse",
            "Aneks A.2 — zdarzenia z facts.json od ostatniej aktualizacji studium":
                "aneks-a2-zdarzenia-z-factsjson-od-ostatniej-aktualizacji-studium",
            "Appendix A.2 — events from facts.json since the last case-study update":
                "appendix-a2-events-from-factsjson-since-the-last-case-study-update",
            "Anhang A.2 — Ereignisse aus facts.json seit der letzten Aktualisierung der Fallstudie":
                "anhang-a2-ereignisse-aus-factsjson-seit-der-letzten-aktualisierung-der-fallstudie",
        }
        for text, slug in samples.items():
            self.assertEqual(annex.slugify_heading(text), slug)
        self.assertNotIn(
            "--",
            annex.slugify_heading("Aneks A.2 — zdarzenia z facts.json od ostatniej aktualizacji studium"),
        )

    def test_inserts_region_immediately_before_annex_b_and_leaves_annex_a(self):
        region = annex.render_region("pl", [cisa_event()], BASELINE, LAST)
        original = SKELETONS["pl"]
        out = annex.apply_document(original, "pl", region)
        annex_a = original[original.index("## Aneks A:"):original.index("## Aneks B:")]
        self.assertIn(annex_a, out)
        self.assertLess(out.index("UNIKALNY-TEKST-ANEKSU-A"), out.index(BEGIN))
        self.assertLess(out.index(END), out.index("## Aneks B: Słowniczek"))
        self.assertTrue(out.startswith("## 1. Rozdział\n\nTekst rozdziału zostaje.\n"))
        lines = out.splitlines()
        i = lines.index("- [Aneks A: Oś czasu](#aneks-a-pelna-os-czasu)")
        self.assertEqual(
            lines[i + 1],
            "- [Aneks A.2: Zdarzenia z facts.json](#aneks-a2-zdarzenia-z-factsjson-od-ostatniej-aktualizacji-studium)",
        )
        self.assertEqual(lines[i + 2], "- [Aneks B: Słowniczek](#aneks-b-slowniczek)")
        self.assertNotIn("a2--zdarzenia", out)

    def test_english_and_german_toc_use_renderer_slugs(self):
        for lang, expected in (
            ("en", "- [Appendix A.2: Events from facts.json](#appendix-a2-events-from-factsjson-since-the-last-case-study-update)"),
            ("de", "- [Anhang A.2: Ereignisse aus facts.json](#anhang-a2-ereignisse-aus-factsjson-seit-der-letzten-aktualisierung-der-fallstudie)"),
        ):
            out = annex.apply_document(SKELETONS[lang], lang, annex.render_region(lang, [cisa_event()], BASELINE, LAST))
            self.assertIn(expected, out)

    def test_second_apply_does_not_rewrite_an_unchanged_toc_line(self):
        first = annex.apply_document(
            SKELETONS["pl"], "pl", annex.render_region("pl", [cisa_event()], BASELINE, LAST))
        prefix = first.split(BEGIN)[0]
        custom = prefix.replace(
            "- [Aneks A.2: Zdarzenia z facts.json](#aneks-a2-zdarzenia-z-factsjson-od-ostatniej-aktualizacji-studium)",
            "- [Aneks A.2: Inna etykieta](#aneks-a2-zdarzenia-z-factsjson-od-ostatniej-aktualizacji-studium)",
        )
        doc = custom + BEGIN + first.split(BEGIN, 1)[1]
        changed = cisa_event(title={"pl": "Tytuł po zmianie", "en": "Changed", "de": "Geändert"})
        second = annex.apply_document(doc, "pl", annex.render_region("pl", [changed], BASELINE, LAST))
        self.assertEqual(second.split(BEGIN)[0], custom)
        self.assertIn("Tytuł po zmianie", second)
        self.assertNotIn("CISA dodaje PHP2Shell do katalogu KEV", second)
        self.assertIn("UNIKALNY-TEKST-ANEKSU-A", second)
        again = annex.apply_document(second, "pl", annex.render_region("pl", [changed], BASELINE, LAST))
        self.assertEqual(again, second)

    def test_wrong_toc_slug_is_corrected_without_rewriting_the_label(self):
        text = SKELETONS["pl"].replace(
            "- [Aneks A: Oś czasu](#aneks-a-pelna-os-czasu)\n",
            "- [Aneks A: Oś czasu](#aneks-a-pelna-os-czasu)\n"
            "- [Aneks A.2: Inna etykieta](#zly-slug)\n",
        )
        out = annex.apply_document(text, "pl", annex.render_region("pl", [], BASELINE, LAST))
        self.assertIn(
            "- [Aneks A.2: Inna etykieta](#aneks-a2-zdarzenia-z-factsjson-od-ostatniej-aktualizacji-studium)",
            out,
        )
        self.assertNotIn("zly-slug", out)
        self.assertEqual(out.count("- [Aneks A.2:"), 1)

    def test_unpaired_markers_raise_and_annex_b_or_toc_gaps_raise(self):
        region = annex.render_region("pl", [], BASELINE, LAST)
        broken = SKELETONS["pl"].replace("## 1. Rozdział", "## 1. Rozdział\n" + BEGIN)
        with self.assertRaises(annex.AnnexError):
            annex.apply_document(broken, "pl", region)
        swapped = END + "\n" + BEGIN + "\n" + SKELETONS["pl"]
        with self.assertRaises(annex.AnnexError):
            annex.apply_document(swapped, "pl", region)
        no_b = SKELETONS["pl"].replace("## Aneks B: Słowniczek\n", "## Aneks Z\n")
        with self.assertRaises(annex.AnnexError):
            annex.apply_document(no_b, "pl", region)
        no_toc = SKELETONS["pl"].replace("- [Aneks A: Oś czasu](#aneks-a-pelna-os-czasu)\n", "")
        with self.assertRaises(annex.AnnexError):
            annex.apply_document(no_toc, "pl", region)

    def test_existing_region_is_replaced_without_touching_the_chapter(self):
        first = annex.apply_document(SKELETONS["en"], "en", annex.render_region("en", [cisa_event()], BASELINE, LAST))
        second = annex.apply_document(first, "en", annex.render_region("en", [], BASELINE, LAST))
        self.assertTrue(second.startswith("## 1. Chapter\n\nChapter text stays.\n"))
        self.assertIn("_No facts.json events newer than the baseline commit._", second)
        self.assertNotIn(CISA_ID, second)
        self.assertEqual(second.count(BEGIN), 1)
        self.assertEqual(second.count(END), 1)


class FakeGitHub:
    def __init__(self):
        self.prs = []
        self.comments = []
        self.reviewers = []

    def open_prs(self, head):
        return [dict(p) for p in self.prs if p["head"] == head and p["base"] == "main" and p["state"] == "open"]

    def create_pr(self, *, title, body, head, base, reviewer):
        number = len(self.prs) + 1
        self.prs.append({"number": number, "title": title, "body": body, "head": head, "base": base, "state": "open"})
        self.reviewers.append((number, reviewer))
        return number

    def comment(self, number, body):
        self.comments.append((number, body))

    def update_pr(self, number, *, title, body):
        for pr in self.prs:
            if pr["number"] == number:
                pr["title"] = title
                pr["body"] = body
                return
        raise AssertionError(number)


def git(repo, *args, check=True):
    cmd = ["git", "-C", str(repo), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.com",
           "-c", "commit.gpgsign=false", *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise AssertionError(f"{cmd}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result


class JobTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.origin = self.root / "origin"
        self.clone = self.root / "clone"
        self.log_path = self.root / "casestudy-annex.log"
        self.github = FakeGitHub()
        self.now = datetime(2026, 11, 14, 6, 30, tzinfo=timezone.utc)
        self.commands = []

    def spy(self, cmd, **kwargs):
        self.commands.append([str(part) for part in cmd])
        return subprocess.run(cmd, **kwargs)

    def write_repo(self, *, events, docs_have_annex, baseline):
        self.origin.mkdir()
        git(self.origin, "init", "-b", "main")
        self._commit(facts([old_event()]), annex_docs=False, baseline_text=None, message="baseline facts")
        base_sha = git(self.origin, "rev-parse", "HEAD").stdout.strip()
        if baseline == "self":
            baseline_text = base_sha + "\n"
        elif baseline == "missing":
            baseline_text = None
        elif baseline == "bad-syntax":
            baseline_text = "not-a-sha\n"
        elif baseline == "unknown":
            baseline_text = "0123456789abcdef0123456789abcdef01234567\n"
        else:
            raise AssertionError(baseline)
        self._commit(facts(events), annex_docs=docs_have_annex, baseline_text=baseline_text,
                     baseline_sha=base_sha, message="current facts")
        subprocess.run(["git", "clone", str(self.origin), str(self.clone)], check=True, capture_output=True, text=True)
        return base_sha

    def _commit(self, payload, *, annex_docs, baseline_text, message, baseline_sha=None):
        data = self.origin / "data"
        case = self.origin / "case-study"
        data.mkdir(exist_ok=True)
        case.mkdir(exist_ok=True)
        (data / "facts.json").write_text(json.dumps(payload), encoding="utf-8")
        if annex_docs:
            regions = {
                lang: annex.render_region(lang, annex.annex_events(payload, facts([old_event()])), baseline_sha, LAST)
                for lang in ("pl", "en", "de")
            }
            docs = {lang: annex.apply_document(SKELETONS[lang], lang, regions[lang]) for lang in regions}
        else:
            docs = SKELETONS
        for lang, text in docs.items():
            (case / f"{lang}.md").write_text(text, encoding="utf-8")
        if baseline_text is None:
            baseline_path = case / "annex-baseline"
            if baseline_path.exists():
                baseline_path.unlink()
        else:
            (case / "annex-baseline").write_text(baseline_text, encoding="utf-8")
        git(self.origin, "add", "data/facts.json", "case-study")
        git(self.origin, "commit", "-m", message)

    def run_annex(self, checks=None):
        if checks is None:
            checks = lambda _path: 0
        return annex.run_job(
            self.clone,
            log_path=self.log_path,
            github=self.github,
            now=self.now,
            checks=checks,
            run=self.spy,
        )

    def log_text(self):
        return self.log_path.read_text(encoding="utf-8")

    def test_log_timestamp_uses_europe_berlin(self):
        self.write_repo(events=[old_event(), cisa_event()], docs_have_annex=True, baseline="self")
        code = self.run_annex()
        self.assertEqual(code, 0)
        text = self.log_text()
        self.assertIn("2026-11-14T07:30:00+01:00 Europe/Berlin start", text)
        self.assertIn("2026-11-14T07:30:00+01:00 Europe/Berlin no-change", text)
        self.assertIn("2026-11-14T07:30:00+01:00 Europe/Berlin end exit=0", text)

    def test_no_change_does_not_commit_or_open_a_pr(self):
        self.write_repo(events=[old_event(), cisa_event()], docs_have_annex=True, baseline="self")
        main_before = git(self.origin, "rev-parse", "main").stdout.strip()
        code = self.run_annex()
        self.assertEqual(code, 0)
        self.assertEqual(git(self.origin, "rev-parse", "main").stdout.strip(), main_before)
        self.assertNotEqual(git(self.origin, "rev-parse", "--verify", "refs/heads/auto/casestudy-annex-a2", check=False).returncode, 0)
        self.assertEqual(self.github.prs, [])
        self.assertEqual(git(self.clone, "status", "--porcelain").stdout, "")
        self.assertEqual(git(self.clone, "branch", "--show-current").stdout.strip(), "main")

    def test_change_opens_one_pr_and_leaves_main_untouched(self):
        base_sha = self.write_repo(events=[old_event(), cisa_event()], docs_have_annex=False, baseline="self")
        main_before = git(self.origin, "rev-parse", "main").stdout.strip()
        baseline_blob = git(self.origin, "rev-parse", "main:case-study/annex-baseline").stdout.strip()
        code = self.run_annex()
        self.assertEqual(code, 0)
        self.assertEqual(git(self.origin, "rev-parse", "main").stdout.strip(), main_before)
        self.assertEqual(git(self.origin, "rev-parse", "main:case-study/annex-baseline").stdout.strip(), baseline_blob)
        tip = git(self.origin, "rev-parse", "auto/casestudy-annex-a2").stdout.strip()
        names = git(self.origin, "diff", "--name-only", "main", tip).stdout.split()
        self.assertEqual(names, ["case-study/de.md", "case-study/en.md", "case-study/pl.md"])
        author = git(self.origin, "log", "-1", "--format=%an <%ae>", tip).stdout.strip()
        self.assertEqual(author, "Nygus (bot for @Akirapl) <akira3179082@gmail.com>")
        pushed = git(self.origin, "show", f"{tip}:case-study/pl.md").stdout
        self.assertIn(BEGIN, pushed)
        self.assertIn("UNIKALNY-TEKST-ANEKSU-A", pushed)
        self.assertIn("Tekst rozdziału zostaje.", pushed)
        self.assertLess(pushed.index("UNIKALNY-TEKST-ANEKSU-A"), pushed.index(BEGIN))
        self.assertEqual(len(self.github.prs), 1)
        pr = self.github.prs[0]
        self.assertEqual(pr["head"], "auto/casestudy-annex-a2")
        self.assertEqual(pr["base"], "main")
        self.assertIn(base_sha[:12], pr["title"])
        self.assertIn(base_sha, pr["body"])
        self.assertIn(CISA_ID, pr["body"])
        self.assertIn(LAST, pr["body"])
        self.assertIn("nie scalać automatycznie; recenzja @Akirapl; nie publikować z tego PR-a", pr["body"])
        self.assertIn("Akira0bot", pr["body"])
        self.assertEqual(self.github.reviewers, [(1, "Akirapl")])
        self.assertIn("pr-opened #1", self.log_text())
        pushes = [cmd for cmd in self.commands if "push" in cmd]
        self.assertTrue(pushes)
        for cmd in pushes:
            joined = " ".join(cmd)
            self.assertNotIn("refs/heads/main", joined)
            self.assertNotIn("gh-pages", joined)
            self.assertNotIn("publish.py", joined)
            self.assertNotIn("ship.py", joined)
            self.assertNotIn("--force", joined)
        again = self.run_annex()
        self.assertEqual(again, 0)
        self.assertEqual(len(self.github.prs), 1)
        self.assertEqual(self.github.comments, [])
        self.assertEqual(git(self.origin, "rev-parse", "auto/casestudy-annex-a2").stdout.strip(), tip)
        self.assertIn("no-change", self.log_text())

    def test_update_comments_on_the_same_pr_and_force_leases_only_the_annex_branch(self):
        base_sha = self.write_repo(events=[old_event(), cisa_event()], docs_have_annex=False, baseline="self")
        self.assertEqual(self.run_annex(), 0)
        self.commands.clear()
        payload = json.loads((self.origin / "data" / "facts.json").read_text(encoding="utf-8"))
        for event in payload["timeline"]:
            if event["id"] == CISA_ID:
                event["title"] = {"pl": "Tytuł zaktualizowany", "en": "Updated title", "de": "Aktualisierter Titel"}
        (self.origin / "data" / "facts.json").write_text(json.dumps(payload), encoding="utf-8")
        git(self.origin, "add", "data/facts.json")
        git(self.origin, "commit", "-m", "retitle")
        self.assertEqual(self.run_annex(), 0)
        self.assertEqual(len(self.github.prs), 1)
        self.assertEqual(len(self.github.comments), 1)
        number, comment = self.github.comments[0]
        self.assertEqual(number, 1)
        self.assertIn(CISA_ID, comment)
        self.assertIn("Tytuł zaktualizowany", git(self.origin, "show", "auto/casestudy-annex-a2:case-study/pl.md").stdout)
        self.assertIn("pr-updated #1", self.log_text())
        pushes = [cmd for cmd in self.commands if "push" in cmd]
        self.assertTrue(any("--force-with-lease=refs/heads/auto/casestudy-annex-a2" in " ".join(cmd) for cmd in pushes))
        for cmd in pushes:
            joined = " ".join(cmd)
            self.assertIn("refs/heads/auto/casestudy-annex-a2", joined)
            self.assertNotIn("refs/heads/main", joined)
            self.assertNotIn("gh-pages", joined)
        self.assertIn(base_sha, (self.origin / "case-study" / "annex-baseline").read_text(encoding="utf-8"))
        self.assertEqual(
            git(self.origin, "rev-parse", "main:case-study/annex-baseline").stdout,
            git(self.origin, "rev-parse", "auto/casestudy-annex-a2:case-study/annex-baseline").stdout,
        )

    def test_checks_failure_does_not_push(self):
        self.write_repo(events=[old_event(), cisa_event()], docs_have_annex=False, baseline="self")
        code = self.run_annex(checks=lambda _path: 1)
        self.assertNotEqual(code, 0)
        self.assertNotEqual(git(self.origin, "rev-parse", "--verify", "refs/heads/auto/casestudy-annex-a2", check=False).returncode, 0)
        self.assertEqual(self.github.prs, [])
        self.assertIn("fail", self.log_text())
        self.assertIn("end exit=", self.log_text())
        self.assertNotIn("pr-opened", self.log_text())

    def test_foreign_files_on_the_annex_branch_are_not_overwritten(self):
        self.write_repo(events=[old_event(), cisa_event()], docs_have_annex=False, baseline="self")
        git(self.clone, "checkout", "-b", "auto/casestudy-annex-a2")
        (self.clone / "README-ANNEX-EXTRA.txt").write_text("ręczna zmiana\n", encoding="utf-8")
        git(self.clone, "add", "README-ANNEX-EXTRA.txt")
        git(self.clone, "commit", "-m", "manual")
        git(self.clone, "push", "origin", "auto/casestudy-annex-a2")
        git(self.clone, "checkout", "main")
        tip = git(self.origin, "rev-parse", "auto/casestudy-annex-a2").stdout.strip()
        self.github.prs.append({
            "number": 7, "title": "stary", "body": "stary", "head": "auto/casestudy-annex-a2",
            "base": "main", "state": "open",
        })
        code = self.run_annex()
        self.assertNotEqual(code, 0)
        self.assertEqual(git(self.origin, "rev-parse", "auto/casestudy-annex-a2").stdout.strip(), tip)
        self.assertEqual(self.github.comments, [])
        self.assertIn("fail", self.log_text())

    def test_missing_baseline(self):
        self.write_repo(events=[old_event(), cisa_event()], docs_have_annex=False, baseline="missing")
        self.assertNotEqual(self.run_annex(), 0)
        self.assertIn("baseline-missing", self.log_text())
        self.assertNotIn("pr-opened", self.log_text())
        self.assertEqual(self.github.prs, [])

    def test_bad_syntax_baseline_is_invalid(self):
        self.write_repo(events=[cisa_event()], docs_have_annex=False, baseline="bad-syntax")
        self.assertNotEqual(self.run_annex(), 0)
        self.assertIn("baseline-invalid", self.log_text())
        self.assertEqual(self.github.prs, [])

    def test_unknown_baseline_object_is_invalid(self):
        self.write_repo(events=[cisa_event()], docs_have_annex=False, baseline="unknown")
        self.assertNotEqual(self.run_annex(), 0)
        self.assertIn("baseline-invalid", self.log_text())
        self.assertEqual(self.github.prs, [])

    def test_unpaired_markers_on_main_do_not_open_a_pr(self):
        self.write_repo(events=[old_event(), cisa_event()], docs_have_annex=False, baseline="self")
        path = self.origin / "case-study" / "pl.md"
        path.write_text(path.read_text(encoding="utf-8").replace("## 1. Rozdział", "## 1. Rozdział\n" + BEGIN), encoding="utf-8")
        git(self.origin, "add", "case-study/pl.md")
        git(self.origin, "commit", "-m", "broken markers")
        self.assertNotEqual(self.run_annex(), 0)
        self.assertEqual(self.github.prs, [])
        self.assertNotEqual(git(self.origin, "rev-parse", "--verify", "refs/heads/auto/casestudy-annex-a2", check=False).returncode, 0)
        self.assertIn("fail", self.log_text())

    def test_failure_log_does_not_keep_a_token(self):
        self.write_repo(events=[old_event(), cisa_event()], docs_have_annex=False, baseline="self")
        token = "ghp_" + ("a" * 30)

        def boom(_path):
            raise RuntimeError("upstream said " + token)

        self.assertNotEqual(self.run_annex(checks=boom), 0)
        text = self.log_text()
        self.assertNotIn(token, text)
        self.assertIn("fail", text)
        self.assertIn("end exit=", text)

    def test_push_helper_refuses_main_and_gh_pages(self):
        allowed = "refs/heads/auto/casestudy-annex-a2"
        self.assertEqual(annex.assert_push_destination(f"abcdef:{allowed}"), allowed)
        for refspec in ("abcdef:refs/heads/main", "abcdef:refs/heads/gh-pages", "main", "HEAD:gh-pages",
                        "abcdef:refs/heads/auto/casestudy-annex-a2-extra"):
            with self.assertRaises(annex.AnnexError):
                annex.assert_push_destination(refspec)


class RepoFileTests(unittest.TestCase):
    def test_baseline_file_holds_the_initial_full_sha(self):
        text = (ROOT / "case-study" / "annex-baseline").read_text(encoding="utf-8")
        lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
        self.assertEqual(lines, [BASELINE])

    def test_systemd_units_are_files_only(self):
        service = (ROOT / "ops" / "routines" / "php2shell-casestudy-annex.service").read_text(encoding="utf-8")
        timer = (ROOT / "ops" / "routines" / "php2shell-casestudy-annex.timer").read_text(encoding="utf-8")
        self.assertIn("Type=oneshot", service)
        self.assertIn("WorkingDirectory=%h/php2shell", service)
        self.assertIn("StandardOutput=append:%h/php2shell/logs/casestudy-annex.log", service)
        self.assertIn("StandardError=append:%h/php2shell/logs/casestudy-annex.log", service)
        self.assertIn("TimeoutStartSec=10min", service)
        self.assertIn("ops/casestudy_annex.py", service)
        self.assertNotIn("publish.py", service)
        self.assertNotIn("ship.py", service)
        self.assertNotIn("systemctl", service)
        self.assertIn("OnCalendar=*-*-* 07:30:00 Europe/Berlin", timer)
        self.assertIn("Persistent=true", timer)
        self.assertIn("php2shell-casestudy-annex.service", timer)
        self.assertNotIn("systemctl", timer)

    def test_checks_argv_covers_parity_paths_secrets_and_facts(self):
        argv = annex.checks_argv(Path("/tmp/annex-worktree"))
        self.assertEqual(argv[0], sys.executable)
        self.assertEqual(argv[1], "/tmp/annex-worktree/ops/checks.py")
        self.assertEqual(argv[-2:], ["--only", "parity,paths,secrets,facts"])

    def test_default_log_path(self):
        self.assertEqual(str(annex.DEFAULT_LOG_PATH), "/home/akira/php2shell/logs/casestudy-annex.log")


if __name__ == "__main__":
    unittest.main()
