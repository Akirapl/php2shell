# PHP2Shell

Sourced public record of CVE-2026-109618 and CVE-2026-109619, patched in PHP 8.5.12 / 8.4.27 / 8.3.36 / 8.2.35 on 21.10.2026. The live center built on this data is at <https://akirapl.github.io/php2shell/>. The old address php2shell-live.surge.sh only redirects there.

## About / O projekcie / Über

Niezależny, niekomercyjny projekt użytkownika [@Akirapl](https://github.com/Akirapl). [ABOUT.md](ABOUT.md).

Independent, non-commercial project by [@Akirapl](https://github.com/Akirapl). [ABOUT.md](ABOUT.md).

Unabhängiges, nicht-kommerzielles Projekt von [@Akirapl](https://github.com/Akirapl). [ABOUT.md](ABOUT.md).

## Polski

To repozytorium trzyma obronne studium przypadku PHP2Shell oraz dane, na których działa centrum na żywo. Tekst jest źródłowy: każde twierdzenie w studium ma przypis, a każdy fakt w zbiorze danych ma adres źródła i poziom pewności.

- Studium: [polski](case-study/pl.md) · [English](case-study/en.md) · [Deutsch](case-study/de.md)
- Diagramy (PNG i źródła Mermaid): [case-study/diagrams/](case-study/diagrams/)
- Centrum na żywo: <https://akirapl.github.io/php2shell/>
- Dane centrum na żywo: [data/facts.json](data/facts.json)
- Checker API: pasywne sprawdzenie banera, zobacz [checker-api/README.md](checker-api/README.md)

W `data/facts.json` każdy fakt niesie `source_url` oraz `confidence`: `confirmed` (potwierdzone), `reported` (relacjonowane) albo `estimate` (szacunek). Z założenia nie ma tu kodu exploita ani instrukcji ataku.

Jak śledzić zmiany:

- historia commitów: <https://github.com/Akirapl/php2shell/commits/main>
- historia jednego pliku, np. <https://github.com/Akirapl/php2shell/commits/main/case-study/pl.md>
- widok blame (kto zmienił daną linię): <https://github.com/Akirapl/php2shell/blame/main/case-study/pl.md>
- obserwowanie repozytorium (Watch) w GitHubie
- kanał Atom commitów: <https://github.com/Akirapl/php2shell/commits/main.atom>

Kod pozostaje na licencji MIT ([LICENSE](LICENSE)). Tekst studium, diagramy i dane są na licencji CC BY 4.0 ([LICENSE-CONTENT](LICENSE-CONTENT)).

## English

This repository holds a sourced, defensive case study of the PHP2Shell incident and the dataset behind the live center. Every claim in the study is footnoted. Every fact in the dataset carries a source URL and a confidence level.

- Case study: [Polish](case-study/pl.md) · [English](case-study/en.md) · [German](case-study/de.md)
- Diagrams (PNG renders and Mermaid sources): [case-study/diagrams/](case-study/diagrams/)
- Live center: <https://akirapl.github.io/php2shell/>
- Live-center data: [data/facts.json](data/facts.json)
- Checker API: passive banner check, see [checker-api/README.md](checker-api/README.md)

In `data/facts.json` each fact has a `source_url` and a `confidence` of `confirmed`, `reported`, or `estimate`. By design the repository contains no exploit code and no attack instructions.

How to follow changes:

- Commit history: <https://github.com/Akirapl/php2shell/commits/main>
- Per-file history, for example <https://github.com/Akirapl/php2shell/commits/main/case-study/pl.md>
- Blame view (who changed a given line): <https://github.com/Akirapl/php2shell/blame/main/case-study/pl.md>
- Watch the repository on GitHub
- Commits Atom feed: <https://github.com/Akirapl/php2shell/commits/main.atom>

Any code stays under the MIT License ([LICENSE](LICENSE)). The case-study text, diagrams, and data are under CC BY 4.0 ([LICENSE-CONTENT](LICENSE-CONTENT)).

## Deutsch

Dieses Repository enthält eine quellengestützte, defensive Fallstudie zum PHP2Shell-Vorfall und den Datensatz hinter dem Live-Center. Jede Aussage in der Studie ist belegt. Jeder Fakt im Datensatz trägt eine Quellen-URL und eine Vertrauensstufe.

- Fallstudie: [Polnisch](case-study/pl.md) · [English](case-study/en.md) · [Deutsch](case-study/de.md)
- Diagramme (PNG und Mermaid-Quellen): [case-study/diagrams/](case-study/diagrams/)
- Live-Center: <https://akirapl.github.io/php2shell/>
- Daten des Live-Centers: [data/facts.json](data/facts.json)
- Checker API: passive Banner-Prüfung, siehe [checker-api/README.md](checker-api/README.md)

In `data/facts.json` hat jeder Fakt eine `source_url` und ein `confidence` von `confirmed` (bestätigt), `reported` (berichtet) oder `estimate` (Schätzung). Das Repository enthält absichtlich keinen Exploit-Code und keine Angriffsanleitungen.

Änderungen verfolgen:

- Commit-Historie: <https://github.com/Akirapl/php2shell/commits/main>
- Historie einer Datei, z. B. <https://github.com/Akirapl/php2shell/commits/main/case-study/pl.md>
- Blame-Ansicht (wer eine Zeile geändert hat): <https://github.com/Akirapl/php2shell/blame/main/case-study/pl.md>
- Repository auf GitHub beobachten (Watch)
- Atom-Feed der Commits: <https://github.com/Akirapl/php2shell/commits/main.atom>

Code bleibt unter der MIT-Lizenz ([LICENSE](LICENSE)). Text der Fallstudie, Diagramme und Daten stehen unter CC BY 4.0 ([LICENSE-CONTENT](LICENSE-CONTENT)).

## How to cite / Jak cytować / Zitieren

Machine-readable metadata: [CITATION.cff](CITATION.cff). GitHub shows it as "Cite this repository" in the sidebar.

> Kulik, Dawid (@Akirapl). *PHP2Shell (CVE-2026-109618 / CVE-2026-109619): a sourced, trilingual live case study and passive banner checker.* Version v1.0, 21 October 2026. <https://akirapl.github.io/php2shell/> · <https://github.com/Akirapl/php2shell>

- Cite a version: the [v1.0 release](https://github.com/Akirapl/php2shell/releases/tag/v1.0), or a specific commit for later corrections.
- Link a specific claim: the case-study file and section, for example `case-study/en.md#5-the-leak-and-the-name-php2shell`. For the dataset, use `data/facts.json` together with the item id.
- Licences: text, diagrams and data are CC BY 4.0 ([LICENSE-CONTENT](LICENSE-CONTENT)). Code is MIT ([LICENSE](LICENSE)).
