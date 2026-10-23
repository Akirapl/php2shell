# Changelog

## v1.7 (23.10.2026)

Case study 1.4: new subsection 7.6 (PL/EN/DE) as of 23 Oct, 18:20 UTC: PHP's informational advisory on the unpatched CVE-2026-115560 (mitigation `session.upload_progress.enabled=0`), Mirai/Potassium botnet attempts (blocked), VulnCheck's ASLR-bypass claim (vendor claim), still no confirmed compromise, Censys exposure (41 million services, different unit from hosts), mood and media review #2 (X counts peaked on 22 Oct; alarm reflex vs technical cooling). Ledger CLM-0113…CLM-0119.

Studium 1.4: nowy podrozdział 7.6 (PL/EN/DE), stan na 23.10, 18:20 UTC: komunikat PHP o niezałatanej CVE-2026-115560 (łagodzenie `session.upload_progress.enabled=0`), próby botnetu Mirai/Potassium (zatrzymane), deklaracja obejścia ASLR przez VulnCheck, nadal brak potwierdzonych włamań, ekspozycja wg Censys (41 mln usług), przegląd nastrojów i mediów #2. Rejestr CLM-0113…CLM-0119.

Fallstudie 1.4: neuer Abschnitt 7.6 (PL/EN/DE), Stand 23.10., 18:20 UTC: PHP-Hinweis zur ungepatchten CVE-2026-115560 (Mitigation `session.upload_progress.enabled=0`), Mirai/Potassium-Botnetzversuche (abgewehrt), VulnCheck-Behauptung einer ASLR-Umgehung, weiterhin keine bestätigte Kompromittierung, Censys-Exposition (41 Mio. Dienste), Stimmungs- und Medienschau Nr. 2. Ledger CLM-0113…CLM-0119.

## v1.6 (22.10.2026)

Case study 1.3: new subsection 7.5 (PL/EN/DE), the first twice-daily social and media review (as of 22 Oct, 18:30 UTC): X post counts and hashtags (#PHP2Shell 2,971 → 6,811 posts/day; about 40% of mentions in Japanese), Mastodon and Hacker News; dominant moods (PoC skepticism, alarm in PL/DE, humour, embargo and EOL frustration, scam warnings); international, German and Polish press angles; three contradictions between sources (exploitability, “70% of the internet”, “attacks have begun”). New label [O] = observation. Ledger CLM-0103…CLM-0112. The live site gained the sections “Social mood”, “Hashtags and keywords” and “Press review” (data: `social_mood`, `hashtags`, `press_review`, `media_contradictions` in `data/facts.json`).

Studium 1.3: nowy podrozdział 7.5 (PL/EN/DE), pierwszy przegląd nastrojów i mediów (dwa razy dziennie, stan na 22.10, 18:30 UTC): liczby wpisów i hashtagi na X (#PHP2Shell 2971 → 6811 wpisów dziennie; ok. 40% wzmianek po japońsku), Mastodon i Hacker News; dominujące nastroje (sceptycyzm wobec PoC, alarm w PL/DE, humor, frustracja embargiem i EOL, ostrzeżenia przed oszustwami); kąty prasy międzynarodowej, niemieckiej i polskiej; trzy sprzeczności między źródłami (wykonalność ataku, „70% internetu”, „ataki się zaczęły”). Nowa etykieta [O] = obserwacja. Rejestr CLM-0103…CLM-0112. Strona na żywo ma nowe sekcje „Nastroje w sieci”, „Hashtagi i słowa kluczowe” i „Przegląd prasy”.

Fallstudie 1.3: neuer Abschnitt 7.5 (PL/EN/DE), die erste der zweimal täglichen Stimmungs- und Medienschauen (Stand 22.10., 18:30 UTC): Beitragszahlen und Hashtags auf X (#PHP2Shell 2.971 → 6.811 Beiträge pro Tag; rund 40 % der Erwähnungen japanisch), Mastodon und Hacker News; vorherrschende Stimmungen (PoC-Skepsis, Alarm in PL/DE, Humor, Frust über Embargo und EOL, Warnungen vor Betrug); Blickwinkel der internationalen, deutschen und polnischen Presse; drei Widersprüche zwischen Quellen (Ausnutzbarkeit, „70 % des Internets“, „die Attacken haben begonnen“). Neue Kennzeichnung [O] = Beobachtung. Ledger CLM-0103…CLM-0112. Die Live-Seite hat neue Abschnitte „Stimmung im Netz“, „Hashtags und Stichwörter“ und „Presseschau“.

## v1.5 (22.10.2026)

Case study 1.1: new subsection 7.4 (PL/EN/DE) on the exploitation picture since disclosure: AWS MadPot attempt on 17 Oct during the embargo (single source), pre-patch attempts reported independently by AWS and Cloudflare, attempts versus breaches (VulnCheck, watchTowr, Recorded Future, heise: no confirmed compromise; not in CISA KEV), precautionary takedowns in Germany and Denmark, exposure estimates (Censys, Unit 42), vendor backports for end-of-life branches. Evidence ledger CLM-0090…CLM-0101.

Studium 1.1: nowy podrozdział 7.4 (PL/EN/DE) o obrazie eksploatacji po ujawnieniu: próba w MadPot (AWS) 17.10 w czasie embarga (jedno źródło), próby przed łatką potwierdzone niezależnie przez AWS i Cloudflare, próby a włamania (VulnCheck, watchTowr, Recorded Future, heise: brak potwierdzonych włamań; brak w CISA KEV), wyłączenia prewencyjne w Niemczech i Danii, szacunki ekspozycji (Censys, Unit 42), backporty dostawców dla gałęzi EOL. Rejestr CLM-0090…CLM-0101.

Fallstudie 1.1: neuer Abschnitt 7.4 (PL/EN/DE) zur Ausnutzungslage seit der Offenlegung: AWS-MadPot-Versuch am 17.10. während des Embargos (eine Quelle), Versuche vor dem Patch unabhängig von AWS und Cloudflare gemeldet, Versuche versus Einbrüche (VulnCheck, watchTowr, Recorded Future, heise: keine bestätigte Kompromittierung; nicht in CISA KEV), vorsorgliche Abschaltungen in Deutschland und Dänemark, Expositionsschätzungen (Censys, Unit 42), Hersteller-Backports für EOL-Zweige. Evidence Ledger CLM-0090…CLM-0101.

## v1.4 (21.10.2026)

Review fixes. Case study: a footnote that pointed to a local working draft is replaced with public sources (Kevin Beaumont's post; Imunify360 and bunny.net vendor posts). Other unsourced or internal notes are replaced with public sources: ACSC, IPA, php.net "History of PHP", and the GitHub tag API. The leak and embargo times are now stated with time zones. The release lead is corrected to ~26 min. "Attack bible" is renamed to "case study". Live-center links point to the canonical <https://akirapl.github.io/php2shell/>. Checker: ownership notice, a friendly "busy" 429 and a higher global cap (the per-client limit is unchanged). New `CITATION.cff` and a "How to cite" section.

Poprawki po recenzji. Studium: przypis wskazujący lokalny szkic roboczy zastąpiono źródłami publicznymi (wpis Kevina Beaumonta; wpisy producentów Imunify360 i bunny.net). Inne notatki bez źródła lub wewnętrzne zastąpiono źródłami publicznymi: ACSC, IPA, „History of PHP” z php.net i API tagów GitHuba. Czasy przecieku i embarga podano ze strefami czasowymi. Wyprzedzenie wydania poprawiono na ~26 min. „Biblię ataku” przemianowano na „studium przypadku”. Linki do centrum na żywo prowadzą na kanoniczny adres GitHub Pages. Sprawdzarka: ostrzeżenie o własnych systemach, przyjazny komunikat 429 „zajęte” i wyższy limit globalny (limit na klienta bez zmian). Nowy `CITATION.cff` i sekcja „Jak cytować”.

Korrekturen nach Review. Fallstudie: Eine Fußnote, die auf einen lokalen Arbeitsentwurf verwies, ist durch öffentliche Quellen ersetzt (Beitrag von Kevin Beaumont; Beiträge der Anbieter Imunify360 und bunny.net). Weitere unbelegte oder interne Notizen sind durch öffentliche Quellen ersetzt: ACSC, IPA, „History of PHP“ von php.net und die GitHub-Tag-API. Leak- und Embargozeiten stehen jetzt mit Zeitzone. Der Vorsprung des Releases ist auf ~26 Min. korrigiert. „Bibel des Angriffs“ heißt jetzt „Fallstudie“. Links zum Live-Center zeigen auf die kanonische GitHub-Pages-Adresse. Checker: Hinweis auf eigene Systeme, freundliche 429-Antwort „ausgelastet“ und ein höheres globales Limit (das Limit pro Client bleibt unverändert). Neu: `CITATION.cff` und ein Abschnitt „Zitieren“.

## v1.3 (21.10.2026)

Case study formatting for mobile: 10 wide tables per language turned into lists; content unchanged.

Formatowanie studium pod telefony: 10 szerokich tabel w każdym języku zamieniono na listy; treść bez zmian.

Formatierung der Fallstudie für Mobilgeräte: 10 breite Tabellen je Sprache in Listen umgewandelt; Inhalt unverändert.

## v1.2 (21.10.2026)

Passive PHP banner checker API in `checker-api/`. The root Render Blueprint `render.yaml` deploys the free Docker web service `php2shell-checker`.

Pasywne API sprawdzania banera PHP w `checker-api/`. Blueprint Render w `render.yaml` wdraża darmową usługę Docker `php2shell-checker`.

Passive PHP-Banner-Prüfung in `checker-api/`. Das Render-Blueprint `render.yaml` deployt den kostenlosen Docker-Webdienst `php2shell-checker`.

## v1.1 (21.10.2026)

Public contact point and archive plan: `ABOUT.md` (linked from the README), `CONTRIBUTING.md`, GitHub issue templates in `.github/ISSUE_TEMPLATE/`, `SECURITY.md`, and `ARCHIVE.md`.

Punkt kontaktu publicznego i plan archiwum: `ABOUT.md` (link w README), `CONTRIBUTING.md`, szablony Issues w `.github/ISSUE_TEMPLATE/`, `SECURITY.md` i `ARCHIVE.md`.

Öffentlicher Kontaktpunkt und Archivplan: `ABOUT.md` (Link in der README), `CONTRIBUTING.md`, Issue-Vorlagen in `.github/ISSUE_TEMPLATE/`, `SECURITY.md` und `ARCHIVE.md`.

## v1.0 (21.10.2026)

Initial publication of the case study in PL/EN/DE (`case-study/pl.md`, `case-study/en.md`, `case-study/de.md`, with diagrams) and the facts dataset (`data/facts.json`).
