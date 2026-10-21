---
title: "PHP2Shell — die Fallstudie"
subtitle: "Langfristige Tiefenanalyse von CVE-2026-109618 und CVE-2026-109619"
lang: de
version: "1.0"
asof: "2026-10-21 14:05 UTC (16:05 CEST)"
---

# PHP2Shell — die Fallstudie

**Tiefenanalyse der kritischen Schwachstellen CVE-2026-109618 und CVE-2026-109619 im PHP-Kern**

- **Dokumentversion:** 1.0 (deutsche Adaptation der polnischen Masterfassung)
- **Stand:** 21.10.2026, 14:05 UTC (16:05 CEST) — ca. 30 Minuten nach Veröffentlichung der Patches
- **Charakter:** Defensive, historische Analyse — **kein** Exploit-Code, keine Payloads, keine PoCs, keine Angriffsanleitungen
- **Kennzeichnung:** **[P]** Primärquelle · **[D]** Drittbericht · **[?]** offen / widersprüchlich · **[A]** Analyse der Autoren
- **Evidence Ledger:** Jede wesentliche Aussage hat eine ID (CLM-…) in [`case-study/evidence-ledger.jsonl`](https://github.com/Akirapl/php2shell/blob/main/case-study/evidence-ledger.jsonl) (auch als [CSV](https://github.com/Akirapl/php2shell/blob/main/case-study/evidence-ledger.csv)) — mit Primärquelle, genauer Fundstelle, Veröffentlichungs- und Ereigniszeit, Prüfstatus und Gegenbelegen
- **Zeitzonen:** UTC; in Klammern Warschauer Zeit. 20.–21.10.2026: **CEST = UTC+2**

> **Redaktionelle Hinweis.** Am Patch-Tag verfasst. Distributionspakete, bestätigte Ausnutzung und vollständige Discoverer-Write-ups stehen noch aus. Jede Aussage ist belegt; Kapitel 12 und das Änderungsprotokoll nennen, was das Bild ändern würde.

## Änderungsprotokoll

- **1.0.1** (2026-10-21 17:30 UTC) — Evidence Ledger (CLM-0001…) ergänzt. Korrekturen aus der Prüfung: Der Fix-Commit ändert 423 Dateien, nicht 300 (die Commit-API von GitHub listet nur die ersten 300); ursprünglicher Termin laut PHP Foundation (22.10., 14:00 UTC) als dritte, widersprüchliche Embargo-Angabe ergänzt; Quellen ergänzt für watchTowr Active Defense, Sansecs „15 Minuten“ (SecurityWeek), die Remi-Warnung (PHP Foundation auf X), NU.nl/BBC-Offline-Listen und Patchstack/Firsov; BSI-Zitat präzisiert; Huntress-Datum korrigiert; Log4Shell-Probes laut Cloudflare 8 (nicht 9) Tage vor der Disclosure; unbelegte Aikido-Angabe „seit Juni 2026“ entfernt, nicht mehr prüfbares Hadrian-„at scale“ abgeschwächt.
- **1.0** (2026-10-21 14:05 UTC) — Erstveröffentlichung. Quellen: php.net, GHSA, Fix-Commit, Wiz, watchTowr, BSI, NCSC UK, NCSC-NL, CERT-EU, CERT.at, CERT Polska, CERT-FR, NOS, W3Techs, Modat, heise, SecurityWeek, Huntress, Tenable, Cloudflare, Docker-PR, Ubuntu-Tracker, HN, Mastodon; historische Vergleiche (Log4Shell, Heartbleed, CVE-2024-4577, OpenSSL 3.0.7).

## Inhaltsverzeichnis

0. [TL;DR und Ein-Seiten-Überblick](#0-tldr-und-ein-seiten-uberblick)
1. [Hintergrund: PHP und Request-Lebenszyklus](#1-hintergrund-php-im-netz-und-der-request-lebenszyklus)
2. [Die Schwachstellen — tief erklärt](#2-die-schwachstellen-tief-erklart)
3. [Entdeckung und KI-gestützte Forschung](#3-entdeckung-wiz-calif-openai-und-ki-gestutzte-forschung)
4. [Koordinierte Offenlegung](#4-koordinierte-offenlegung-grundlagen-und-ablauf)
5. [Das Leak und der Name PHP2Shell](#5-das-leak-und-der-name-php2shell)
6. [Patch-Tag](#6-patch-tag)
7. [Das Exploit-Rennen](#7-das-exploit-rennen)
8. [Reaktion der Verteidiger](#8-reaktion-der-verteidiger)
9. [Exposition und Auswirkungen](#9-exposition-und-auswirkungen)
10. [Historischer Vergleich](#10-historischer-vergleich)
11. [Lehren](#11-lehren)
12. [Offene Fragen](#12-offene-fragen)
- [Anhang A: Zeitachse](#anhang-a-vollstandige-zeitachse)
- [Anhang B: Glossar](#anhang-b-glossar)
- [Anhang C: Checkliste](#anhang-c-defensive-checkliste)
- [Anhang D: Quellen](#anhang-d-quellen)

---

## 0. TL;DR und Ein-Seiten-Überblick

**In einem Absatz.** Am 21. Oktober 2026 gegen **13:34 UTC** veröffentlichte das PHP-Sicherheitsteam die Versionen **8.5.12, 8.4.27, 8.3.36 und 8.2.35** sowie zwei GitHub-Advisories zu kritischen Engine-Schwachstellen: **CVE-2026-109618** („RCE via OOM corruption“) und **CVE-2026-109619** („RCE via stale global state“), beide **CVSS v4.0 9.2** [P][^ghsa618][^ghsa619][^phpadv]. Beide folgen demselben Muster: Wenn PHP eine Anfrage im Notfall abbricht (besonders bei Speichermangel), kann interner Zustand auf Speicher zeigen, der nicht mehr existiert — und ein späterer Schritt oder eine spätere Anfrage desselben Workers kann diesen „Geist“ nutzen. Unter **Apache + mod_php** wurde unauthentifizierte Remote Code Execution **bevor Anwendungscode läuft** nachgewiesen [P][^phpadv]. Wiz Research beansprucht die Entdeckung gemeinsam mit Calif und OpenAI unter starker Nutzung von Frontier-KI [D][^wiz]. Ein Embargo bis Donnerstag, 22.10., brach durch ein Leak am 20.10.; PHP zog die Freigabe um einen Tag vor [P][^wtx][^phppre]. In den Niederlanden, Belgien, Frankreich und Finnland gingen Sites vorsorglich offline [P][^nos]. Zum Redaktionsschluss dieser Fassung gibt es keine unabhängig bestätigte Ausnutzung „in the wild“; die Berichte widersprechen sich [?].

> ### Schlüsselfakten
>
> - **IDs:** CVE-2026-109618 (GHSA-w8hw-w9fx-j79w), CVE-2026-109619 (GHSA-6wmf-4rv5-p3rp) [P]
> - **CVSS v4.0:** 9.2 · `AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N` (beide) [P]
> - **CWE:** 416, 755, 824, 1325, 1419 [P]
> - **Impact:** unauth RCE als Web-Worker; 619 auch Memory Disclosure [P]
> - **Schlechtester SAPI:** Apache mod_php (vor Anwendungscode) [P]
> - **Behoben:** 8.5.12, 8.4.27, 8.3.36, 8.2.35; minimale Source-Backports für 7.4/8.0/8.1 [P]
> - **Veröffentlichung:** GHSA 13:34 UTC; Tarball 8.5.12 `Last-Modified` 13:33:59 GMT [P]
> - **Ursprüngliches Embargo:** 22.10.2026 11:00 ET (15:00 UTC = 17:00 MESZ; der HN-Leak nannte 18:00 MESZ, siehe 5.1) [P]; die PHP Foundation nannte später als ursprünglichen Termin 22.10. **14:00 UTC** — die Angaben widersprechen sich [?][^phpfback]
> - **GHSA-Credits:** sagitzadik-wiz, tomash-areion, lcfr-hax, amyb-oai [P]
> - **Fix:** Arnaud Le Blanc (+ Tovilo, Zelenka, Dossche, Grekas); +11.556/−1.017 in 423 Dateien [P]
> - **PHP-Anteil:** 69,3 % der Sites mit bekannter serverseitiger Sprache (W3Techs 21.10.) [P]
> - **Exposition:** 4,38 Mio. PHP-Dienste / 1,89 Mio. Hosts; ~79 % EOL (Modat 20.10.) [D]
> - **Vollständiger Schutz:** nur Update [P]
>
> *Ledger: Kernfakten = CLM-0001…CLM-0014; Ausnutzungsstatus = CLM-0054…CLM-0065.*

**Was neu ist** [A]: (1) Bug in der *Runtime*, nicht in der App; (2) KI bei Entdeckung und — laut Forschern — bei praktikabler Ausnutzung; (3) Embargo-Leak → ~22-Stunden-Rennen; (4) vorsorgliche Abschaltungen öffentlicher Sites in mehreren EU-Staaten vor dem Patch.

![Zeitachse](diagrams/timeline.png)

---

## 1. Hintergrund: PHP im Netz und der Request-Lebenszyklus

### 1.1 Wie groß PHP ist

Rasmus Lerdorf schuf PHP 1994 (als „Personal Home Page Tools“) und veröffentlichte den Quellcode im Juni 1995 [P][^phphist]. Laut W3Techs (21.10.2026) nutzen **69,3 %** der Websites mit bekannter Server-Sprache PHP; darunter **65,2 %** Version 8, **27,0 %** Version 7, **7,7 %** Version 5, **0,1 %** Version 4 [P][^w3t]. WordPress, Drupal, Joomla, Magento und MediaWiki laufen auf PHP [D][^wiz].

**Methodischer Hinweis** [A]: „69,3 %“ bezieht sich auf Sites *mit erkannter* Server-Sprache, nicht auf „das ganze Internet“. Schlagzeilen wie „70 % of the Internet“ (Wiz) sind Vereinfachungen [D][^wiz].

### 1.2 Was passiert, wenn der Browser eine Seite anfordert

PHP steckt üblicherweise im Webserver oder läuft als Worker-Pool. Die Schnittstelle heißt **SAPI** (Server API).

- **Apache mod_php**
  - *Funktionsweise:* PHP in Apache-Prozessen (typisch Prefork).
  - *Bedeutung für PHP2Shell:* Schlimmster Fall: Request-Shutdown läuft **immer**, auch wenn der Start scheiterte [P][^ghsa618].
- **PHP-FPM**
  - *Funktionsweise:* Eigener Pool; nginx/Apache per FastCGI.
  - *Bedeutung für PHP2Shell:* Bei Startfehler beendet FPM den Child — unterbricht den einfachsten Pfad; andere bleiben [P][^ghsa618][^ghsa619].
- **CGI / php-cgi**
  - *Funktionsweise:* Klassisch ein Prozess pro Request (oder FastCGI).
  - *Bedeutung für PHP2Shell:* Als betroffen genannt [P][^phpadv].
- **FrankenPHP**
  - *Funktionsweise:* Moderner PHP-Application-Server.
  - *Bedeutung für PHP2Shell:* Codeanalyse: wahrscheinlich wie mod_php beim Shutdown [P][^ghsa618].
- **LiteSpeed LSAPI**
  - *Funktionsweise:* FPM-ähnliches Modell.
  - *Bedeutung für PHP2Shell:* App-spezifische Pfade „wahrscheinlich, nicht validiert“ [P][^ghsa618].

**Analogie** [A]: Ein PHP-Worker ist der Schreibtisch eines Sachbearbeiters. Jede Anfrage ist ein Vorgang. Danach müssen alle Akten weg. Geht das Licht in Panik aus (OOM / Fatal), bleibt vielleicht ein Zettel mit einer Adresse einer Akte, die schon geschreddert wurde. Der nächste Besucher — derselbe Schreibtisch — behandelt die Adresse als gültig. Das ist „stale global state“ und „OOM corruption“.

![Request-Lebenszyklus](diagrams/lifecycle.png)

### 1.3 Warum das zählt

Die meisten kritischen Lücken im PHP-Ökosystem sitzen in *Anwendungen*. Hier sitzt der Bug in der **Engine** [P][^phpadv]. Eine „Hello World“-App auf betroffener Version ist ebenfalls exponiert [D][^wiz]. Inventar muss CMSe, Control Panels, Appliances mit PHP im Firmware und versteckte `php.exe` umfassen [D][^huntress][^heise].

---

## 2. Die Schwachstellen — tief erklärt

### 2.1 Gemeinsames Muster

Offizielle Advisories und der Wiz-Blog beschreiben Varianten desselben speicherbezogenen Fehlers an der Request-Grenze [P][^ghsa618][^ghsa619][^wiz]:

1. Eine Operation speichert request-eigenen Zustand in einer Worker-Globalen (**Producer**).
2. Fatal / OOM / Diagnose bricht ab, bevor der passende Reset läuft.
3. Request-Speicher wird freigegeben; die Globale zeigt weiter darauf.
4. Derselbe Worker bedient eine weitere Anfrage.
5. Eine Operation vor der normalen Initialisierung liest den Zeiger (**Consumer**) → Use-after-free → bei passendem Heap-Layout: RCE.

**Warum Memory-Safety-Bugs in einer Runtime schwer sind** [A]: Sie sind keine „eine Lücke in Funktion X“, sondern eine Wechselwirkung aus Allocator, Fehlerbehandlung (`longjmp` / Bailout), vielen Extensions und vielen SAPIs. Der Fix musste die OOM-Strategie ändern und ein breites Set von Globalen zurücksetzen (~400 Dateien) [P][^commit].

### 2.2 CVE-2026-109618 — RCE via OOM corruption

**Was falsch war.** PHP nutzte `longjmp()` bei OOM, um den Kontext zu verlassen und die Anfrage abzubrechen. War der Request-Speicher nur teilweise initialisiert, hinterließ der Early-Exit ungültigen Zustand; der Shutdown konnte ihn als gültig behandeln [P][^ghsa618].

**OOM-Strategien** (nur Konzepte) [P][^ghsa618]: Multipart ohne nutzbare Content-Length; unbegrenzte Part-Header (mehr Speicher als auf dem Draht); leere File-Controls zählen nicht zu `max_file_uploads`, erzeugen aber Metadaten. Auch Anwendungslogik kann OOM auslösen.

**Warum mod_php am schlimmsten ist.** Apache mod_php ruft den Request-Shutdown **bedingungslos** auf, auch wenn der Start scheiterte. Body-Parsing beim Start kann `memory_limit` im Fenster ungültigen Zustands erschöpfen — **bevor die Anwendung läuft** [P][^ghsa618][^phpadv]. FPM beendet den Child bei Startfehler; die Quellanalyse hält FPM dennoch für anfällig, ein vollständiger FPM-Exploit für 618 wurde nicht gezeigt [P][^ghsa618].

**Der Fix.** Entfernen von `longjmp()` für OOM → Soft-OOM am VM-Safe-Point + Hard-OOM mit `_exit()` bei einer zweiten Schwelle [P][^ghsa618][^commit].

### 2.3 CVE-2026-109619 — RCE via stale global state

**Was falsch war.** Worker-globaler Zustand (Error / Session / Object / Extension) kann auf Request-Speicher zeigen. Fatal, OOM oder Diagnose hinterlässt einen stale Pointer; eine spätere Anfrage konsumiert ihn **vor** der normalen Initialisierung [P][^ghsa619].

**Bestätigte Consumer** [P][^ghsa619]:

- **INI-Diagnosen vor Init** — Warnungen/Deprecations beim Anwenden von Settings (`.htaccess` / `php_value` bei mod_php; `PHP_VALUE` bei FPM), bevor der Executor startet. Diagnosen zu verstecken hilft **nicht**.
- **Session Upload Progress** — kann Session-Handling vor gewöhnlicher Initialisierung erreichen; unabhängig vom INI-Pfad.

**Stärkster nachgewiesener Fall:** `fatal_error_backtraces` (PHP 8.5) + Diagnose → bestätigtes RCE auf mod_php. Session-Upload-Progress-RCE: bestätigt auf mod_php **und** FPM [P][^ghsa619].

**Wiz zu vier Klassen** (unter zwei CVEs gruppiert) [D][^wiz]: Upload-Progress-Unserializer-UAF; Memory Disclosure über PHPSESSID; Fatal-Backtrace-UAF; OPcache-Type-Confusion. Richtungsgemäß im Einklang mit den GHSA; Kettendetails stammen von Wiz.

### 2.4 CVSS v4.0 Feld für Feld

Beide CVEs: `CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N` → **9.2** [P][^ghsa618][^ghsa619].

| Feld | Wert | Bedeutung |
|---|---|---|
| AV:N | Network | Über das Netz erreichbar |
| AC:H | High | Hohe Angriffskomplexität (Heap-Layout, Bedingungen) |
| AT:P | Present | Voraussetzungen im System |
| PR:N | None | Keine Authentifizierung |
| UI:N | None | Keine Benutzerinteraktion |
| VC/VI/VA:H | High | Voller Impact auf Vertraulichkeit, Integrität, Verfügbarkeit des **verletzlichen** Systems |
| SC/SI/SA:N | None | Kein bewerteter Impact auf **nachfolgende** Systeme |

Frühe Gerüchte sprachen von „CVSS 10.0“ [D][^hnleak][^wtx] — die offizielle PHP-Bewertung ist 9.2 mit AC:H und AT:P.

### 2.5 Versionen: behoben, EOL, Backports

| Branch | PHP-Support | Fix |
|---|---|---|
| 8.5 | unterstützt | **8.5.12** |
| 8.4 | unterstützt | **8.4.27** |
| 8.3 | unterstützt | **8.3.36** |
| 8.2 | Security bis 31.12.2026 | **8.2.35** |
| 8.1 / 8.0 / 7.4 | EOL | minimale **Source-Backports**; keine offiziellen Releases |
| ≤ 7.3 / 5.x | EOL | kein offizieller Fix; LTS-Vendoren können backporten |

[P][^phpadv]. „Ab 5.4“ / „ab PHP 5“ kommt von Wiz, CERT-EU, NCSC-NL u. a. — nicht aus den GHSA-`vulnerable_version_range`-Tabellen (dort nur behobene Branches) [P/D][^ghsa618][^wiz][^certeu][^ncscnl].

### 2.6 Unvollständige Mitigations

PHP und Core-Entwickler betonen: **der einzige vollständige Schutz ist das Update** [P][^phpadv][^girgias]. Temporäre Maßnahmen (z. B. `memory_limit=-1`, `session.upload_progress.enabled=0`, unter 8.5 `fatal_error_backtraces=0`) verkleinern konkrete Pfade; sie machen eine Installation nicht sicher [P][^phpadv]. `RLIMIT_AS`/`RLIMIT_DATA` nicht als Ersatz nutzen — sie können den verwundbaren `mmap`→`longjmp`-Pfad erzwingen [P][^ghsa618].

---

## 3. Entdeckung: Wiz, Calif, OpenAI und KI-gestützte Forschung

### 3.1 Zeitachse laut Wiz (Drittbericht)

| Datum | Ereignis | Status |
|---|---|---|
| 19.08.2026 | Erste Schwachstelle mit Wiz Atlas, „Gemini 4 Argon“, „GPT-5.6 Sol“ | [D][^wiz] |
| 20.08.2026 | Unauth-RCE gegen Drupal | [D][^wiz] |
| 21.08.2026 | Unauth-RCE gegen WordPress | [D][^wiz] |
| 24.08.2026 | Meldung an PHP | [D][^wiz] |
| 21.09.2026 | PHP bestätigt und beginnt koordinierten Fix | [D][^wiz] |
| 21.10.2026 | Öffentliche Patches + Wiz-Blog | [P][^wiz][^phpadv] |

GHSA-Credits: `sagitzadik-wiz`, `tomash-areion`, `lcfr-hax`, `amyb-oai` [P][^ghsa618]. Wiz dankt Calif und OpenAI; heise beschreibt ein Calif-Audit mit dem PHP Ecosystem Security Team im Rahmen von OpenAIs „Patch the Planet“ [D][^wiz][^heise]. Calif hatte zuvor (01.05.2026) separat zu einem 21 Jahre alten PHP-UAF publiziert [P][^califmad].

### 3.2 Was KI am Bug Hunting ändert

Wiz: Der verwundbare Code war über ein Jahrzehnt präsent; eine funktionierende Kette erforderte das Verketten mehrerer Bugs und Anpassungen an Speicherlayouts — Frontier-Modelle „substantially reduced that barrier“ [D][^wiz]. Das BSI hält eine „großflächige Ausnutzung innerhalb weniger Stunden“ nach Erscheinen der Updates für wahrscheinlich, weil Angreifer sie mit KI-gestützten Werkzeugen schnell analysieren können [P][^bsipresse].

**[A]** Das heißt nicht „KI fand die CVE allein“. Es heißt, die Kosten vom schweren Memory-Safety-Bug zum glaubwürdigen RCE auf vielen Targets sanken. Dieselbe Ökonomie gilt für Angreifer (Patch-Reverse) und Verteidiger (Triage).

Die PHP Foundation (14.10.2026) beschrieb den Einsatz von **Daybreak Red** (OpenAI) zur Validierung von Reports und Sortierung der Queue — Kontext einer Welle KI-gestützter Meldungen [P][^phpfound].

### 3.3 Audit 2024 und Ecosystem Security Team

2024 fand Quarkslab (Sovereign Tech Agency / OSTIF) 17 sicherheitsrelevante Findings; heise erwähnt, dass eine ähnliche Klasse schon Remediationsdebatten ausgelöst hatte [P/D][^audit2024][^heise]. Im Mai 2026 kündigte die PHP Foundation ein Ecosystem Security Team an [D][^heise]. PHP2Shell zeigt sowohl Security-Investitionen als auch eine lange architektonische Spur um Bailout/OOM [A].

---

## 4. Koordinierte Offenlegung: Grundlagen und Ablauf

### 4.1 Coordinated Disclosure 101

Typischer Ablauf [A]: (1) private Meldung; (2) Bestätigung und Fix; (3) embargierte Benachrichtigung von Distros/LTS und ausgewählten Partnern; (4) gleichzeitige Advisories + Releases; (5) Ökosystem-Kommunikation. Ziel: Fenster zwischen Angreiferwissen und Patch-Verfügbarkeit minimieren.

### 4.2 Wie es hier lief

![Disclosure-Ablauf](diagrams/disclosure.png)

1. **Meldung und Remediierung** (VIII–X 2026) — laut Wiz [D][^wiz]. Commit „Avoid state corruption via bailout“ am 18.10.2026; annotated Tags am 19.10. [P][^commit][^tags].
2. **Early Access.** php.net: „Linux distributions and LTS vendors received the patches in advance“ [P][^phpadv]. Wiz nennt Automattic, Akamai, AWS, Cloudflare, Fastly, Google, Imperva, Microsoft, Vercel u. a. für Mitigations vor Day Zero [D][^wiz]. watchTowr rollte Active-Defense-Mitigations für Kunden der watchTowr-Plattform vor dem Patch aus [P][^wtxad].
3. **Embargo.** watchTowr: ursprünglich **Donnerstag, 22.10., 11:00 ET** (= 15:00 UTC) [P][^wtx].
4. **Vorankündigung nach dem Leak.** Am 20.10. um 19:33 UTC kündigte Jakub Zelenka (`bukka`) **Mittwoch, 21.10., 14:00 UTC** an, mit dem Recht auf frühere Freigabe bei Leak oder Ausnutzung [P][^announce].
5. **Trade-off** [A]: Die Ankündigung gab ~18 h für Inventar und Patch-Fenster, bestätigte aber auch die Realität der CVEs. OpenSSL 3.0.7 (2022) zeigte eine andere Variante: CRITICAL-Preannounce, später auf HIGH abgestuft [P][^openssl307]. Hier hielt die 9.2.

Prozesskritik (Kevin Beaumont, 21.10., 08:07 UTC): Cyber-Anbieter mit Vorabinformation hätten Kunden „Details mitgeteilt“ – für ihn „faktisch ein gewinnorientierter Weiterverkauf von Wissen aus Open-Source-Projekten“ („Protecting the ivory tower sucks“) [P][^beaumont2]. Diese Spannung kehrt bei jedem Infrastruktur-Embargo wieder [A].

---

## 5. Das Leak und der Name „PHP2Shell“

### 5.1 Was leakte, wann und wo

*Zeiten in UTC.*

- **20.10. 15:20** — „Tell HN: 2x PHP RCE CVEs with CVSS 10.0 Incoming“ (petecooper) — CVE-Nummern, Termin „22 October 2026 at 18:00 CEST“; später gelöscht [P][^hnleak]. Zeitabgleich: Der Beitrag erschien am 20.10. um 15:20 UTC (17:20 MESZ) und nannte den 22.10. **18:00 MESZ** (= 16:00 UTC), watchTowr dagegen 22.10. **11:00 ET** (EDT, = 15:00 UTC = **17:00 MESZ**) – zwei Angaben vor der Offenlegung, eine Stunde auseinander; welche dem tatsächlichen Embargo entsprach, ist offen [?][^wtx]. Die PHP Foundation nannte später einen dritten Wert: 22.10., 14:00 UTC [P][^phpfback]
- **20.10. 16:39** — Kevin Beaumont (Mastodon): Leak der CVE-Nummern [P][^beaumont]
- **20.10. 18:26** — watchTowr: „supposed to wait until Thursday 11am ET… We can confirm that they're real.“ [P][^wtx]
- **20.10. 19:33** — Offizielle PHP-Ankündigung [P][^announce]
- **20.10. 20:27** — Kirill Firsov: Video „php2shell“ (~1,7 Mio. Views); Tool-Banner „PHP2SHELL — PHP >= 5.4.0 RCE by Calif.IO“ (Screenshots Dormann) [P][^firsov][^dormann]
- **21.10. 00:30** — J4ck3LSyN meldet „Reproduktion“; widerruft später den Haupt-RCE-Pfad [P/D][^jackal]

HN-Kommentar „bwoebi“ (Identität unverifiziert): Das Video sei der Grund für die Ankündigung „in diesem Moment“ gewesen [D][^bwoebi]. Die Zeitstempel widersprechen dem: Die Ankündigung kam um 19:33 UTC, das Video um 20:27 UTC, und laut PHP Foundation folgte das Video auf die Vorankündigung [P][^announce][^firsov][^phpfback].

### 5.2 Der Name

„PHP2Shell“ stammt **nicht** aus der offiziellen PHP-Mitteilung. Er kam vom Tool-Banner im geleakten Demo (Calif.IO) und verbreitete sich medial; das BSI notiert den Marketing-Vergleich zu Log4Shell [P/D][^bsipdf][^sansec]. PHP nutzt beschreibende CVE-/GHSA-Titel [P][^phpadv].

### 5.3 Wirkung des Leaks

PHP verschob den Tag von Donnerstag auf Mittwoch und behielt sich frühere Freigabe vor [P][^announce][^phppre]. Tarbälle und GHSA erschienen schließlich ~26 Minuten vor den angekündigten 14:00 UTC (Last-Modified der Tarbälle 13:33:59 UTC, erstes GHSA 13:34:13 UTC) [P][^tarball][^ghsa619]. Das Embargo gab Distros Zeit, verhinderte aber kein öffentliches „Zero-Day-Gefühl“ für ~22 Stunden [A].

---

## 6. Patch-Tag

### 6.1 Release-Mechanik

- Annotated Tags `php-8.2.35`…`php-8.5.12` am **19.10.** (Panteleev, Mann, Buckley, Scherzer) — Vorbereitung vor Day Zero [P][^tags].
- Tarball `php-8.5.12.tar.xz`: `Last-Modified: Wed, 21 Oct 2026 13:33:59 GMT` [P][^tarball].
- GHSA-6wmf-4rv5-p3rp: **13:34:13Z**; GHSA-w8hw-w9fx-j79w: **13:34:25Z**; Publisher: `bukka` [P][^ghsa618][^ghsa619].
- Der php.net-Atom-Feed stempelt `T00:00:00Z` am Release-Tag — eine **Datumskonvention**, keine Publikationsuhrzeit [P][^atom].

### 6.2 Größe des Fixes

Commit `31c0ea7` „Avoid state corruption via bailout“: **+11.556 / −1.017** in **423** Dateien (die Commit-API von GitHub listet nur die ersten 300; der Commit auf dem 8.2-Branch ändert 389); UnwindExit statt OOM-Bailout + Global-Resets [P][^commit]. Keine „paar Zeilen“ — daher Distro-Lag und Regressionsrisiko bei hastigen Backports [A].

### 6.3 „Patch released“ ≠ „gepatcht“

*Stand ~14:00 UTC 21.10.:*

- **php.net Source / Windows-Binaries** — verfügbar [P][^phpadv]
- **Docker official `library/php`** — PR #1694 um 13:44 geöffnet; nach Merge noch official-images + Builds [P][^docker]
- **Remi (`rpms.remirepo.net`)** — **kein Update „heute“** — Warnung der PHP Foundation [P][^phpfremi]
- **Ubuntu-Tracker** — CVE-Einträge, „Needs evaluation“ auf vielen Releases [P][^ubuntu]
- **Debian/RHEL-Pakete** — in Arbeit / hier nicht verifiziert [?]
- **Shared Hosting** — hängt vom Hoster ab (heise: Uberspace plante zeitweilige PHP-Abschaltung) [D][^heise]

Solange Worker nicht auf Binaries mit dem Fix laufen, ist das System verwundbar — ungeachtet der Pressemitteilung [A].

---

## 7. Das Exploit-Rennen

### 7.1 Wie Angreifer Patches reverse-engineeren (konzeptuell)

Ohne Rezepte [A]: Bei großem öffentlichem Diff (hier: Hunderte Dateien um OOM und Global-Resets) vergleichen Analysten Vorher/Nachher, lokalisieren geänderte Fehlerpfade und rekonstruieren Eingangsbedingungen. Das BSI knüpft das Tempo ausdrücklich an KI-Werkzeuge [P][^bsipresse]. CERT.at: Exploit-Code im Netz + erleichtertes Patch-Reversing → Ausnutzung „zeitnah“ nach Veröffentlichung [P][^certat]. Sansec erwartete Mass Attacks binnen 15 Minuten nach Release (zitiert von SecurityWeek) [D][^secweek].

### 7.2 Falsche und zurückgezogene PoCs — Signal versus Rauschen

- Firsov-Video / Dormann-Screenshots (Calif.IO / `lcfr`) — **in dieser Research nicht unabhängig verifiziert** [P/D].
- jackalsyn.com: Autor **widerruft** den „Cached-Pointer“-Pfad als DEAD; bewertet den realen Bug mit CVSS 5.3 / „NOT RCE“ — **stimmt nicht** mit offiziellen 9.2 überein [D][^jackal]. Als Rauschen / partielle LLM-Rekonstruktion behandeln.
- GitHub: zahlreiche „php2shell“-/CVE-Repos (z. B. ikow/php2shell-poc) — Tenable warnt vor unverifiziertem Exploit-Code (Malware-Risiko) [D][^tenable].

### 7.3 Ausnutzungs-Telemetrie (widersprüchlich)

- **Cloudflare Knecht 07:43 UTC** — „early attacks emerging“; WAF-Stopgap [P][^knecht]
- **Huntress (Stand 21.10., 10:00 ET)** — keine in Partner-Umgebungen [P][^huntress]
- **watchTowr-FAQ** — keine ITW (Stand FAQ) [P][^wtxfaq]
- **NCSC-NL / BSI v1.0** — kein bestätigter Missbrauch / keine bestätigten Ausnutzungen [P][^ncscnl][^bsipdf]
- **PHP-Team → ANP** — keine Indikation aktiven Abuse [D][^nu]
- **Patchstack (NBC), Firsov** — „reports of active exploitation“ / „in the wild“ [D][^nbc][^firsovitw] ohne IoCs; eine von Mattias Geniar weitergegebene Hadrian-Aussage „at scale“ steht nicht mehr in seinem aktualisierten Beitrag [?]
- **CISA KEV** — kein Eintrag (Research ~13:46 UTC) [P][^kev]

**Fazit [A]:** Für „ist es ITW?“ braucht es IoCs großer Sensoren oder einen KEV-Eintrag — die Botschaften widersprechen sich noch.

---

## 8. Reaktion der Verteidiger

![Akteurskarte](diagrams/actors.png)

### 8.1 Behörden

- **CERT-EU 2026-018** — Sofort patchen oder isolieren; „all from PHP 5“; CVSS → unauth RCE [P][^certeu]
- **BSI** — BITS-H Orange/3 + Presse Caspers: „großflächige Ausnutzung innerhalb weniger Stunden“; KI beschleunigt Reverse [P][^bsipdf][^bsipresse]
- **CERT-Bund** — WID-SEC-2026-4055 (Inhalt hinter Login — hier ungelesen) [P/?]
- **NCSC UK** — PHP finden; patchen; härten; Offline erwägen; gebündeltes PHP inventarisieren [P][^ncscuk]
- **NCSC-NL** — Mitteilung; ncsc.nl offline; Repo NCSC-NL/php2shell; kein aktiver Missbrauch [P][^ncscnl]
- **CERT.at** — Update #1: Exploit im Netz, Funktionalität unbestätigt [P][^certat]
- **CERT Polska 195/2026** — Inventar; Internet-facing PHP ggf. abschalten [P][^certpl]
- **CERT-FR ALE-014** — Workarounds upload_progress/multipart **nicht qualifiziert** [P][^certfr]
- **ACSC (ASD, Australien) / IPA (Japan)** — Warnungen vor dem Release (21.10.): PHP inventarisieren und Update vorbereiten; dem ACSC war bei Veröffentlichung keine Ausnutzung bekannt [P][^acsc][^ipa]
- **CISA** — Kein KEV zu PHP2Shell zum Research-Zeitpunkt [P][^kev]

### 8.2 WAFs, Hoster, CMSe

- **Cloudflare:** Emergency Managed Ruleset — sieben Regeln „Anomalous Execution“; auch Free; Knecht: nur Stopgap [P][^cfwaf][^knecht].
- **CloudLinux Imunify360:** WAF-Ruleset 8.83 blockiert das kursierende Anfragemuster auf ModSecurity/Coraza (auf LiteSpeed nur Logging); laut Hersteller ein virtueller Patch, kein Fix [P][^imunify]. **bunny.net:** verwaltete WAF-Regeln in Bunny Shield, die nur im Blocking-Modus blockieren; ein Notbehelf – PHP muss gepatcht werden [P][^bunny].
- **Sansec (Magento):** Mass Attacks in 15 Minuten (laut SecurityWeek); Fix auf Infrastruktur-Ebene, nicht im Shop [D][^secweek][^sansec].
- **Wordfence / Shared WP:** Fix kommt nicht per WordPress-Auto-Update — hängt vom Hoster ab [D][^verge].

### 8.3 Die niederländische (und benachbarte) Abschaltwelle

NOS/NU und die NCSC-NL-Mitteilung dokumentieren vorsorgliches Offline u. a. für DigiD.nl (Site; DigiD-Login anderswo teils weiter), MijnOverheid, Tweede Kamer, RIVM, ANWB, RTL, Krankenhäuser, SURF, Parteien, UWV (gewählte Apps), NCSC.nl, NotuBiz, KNVB, Wohltätige [P][^nos][^nu][^bbc][^ncscnl]. Belgien: flämische Regierungsseiten (Diependaele); Frankreich: Präfekturen; Finnland: Regierungsseiten [P][^nos].

**Kommunikationsanalyse [A]:** Klassischer Trade-off Verfügbarkeit versus Vertraulichkeit/Integrität. Bei CVSS 9.2, ohne zuverlässigen Workaround und mit öffentlicher PoC-Erzählung wählten Behörden „lieber dunkle Site als übernommener Server“. Kosten: ausgefallene öffentliche Dienste an einem Werktag.

---

## 9. Exposition und Auswirkungen

### 9.1 Was wir wissen

- **W3Techs 21.10.2026:** 69,3 % / Versionsverteilung wie oben [P][^w3t].
- **Modat 20.10.:** 4.384.302 Dienste / 1.886.612 Hosts; **79 %** der versionierten Dienste auf EOL (4/5/7/8.0/8.1); größte Gruppe **7.4** (878.761); USA/China/Japan/Deutschland führen bei Hosts [D][^modat].
- **Mallory/THN:** ~884.000 Hosts mit PHP-≤8.1-Banner — Banner, nicht bestätigte Verwundbarkeit [D][^thn].
- **Tenable/Cutler/Poley:** Schätzungen 1,3–1,9 Mio. Hosts [D][^tenable].

### 9.2 Was wir nicht wissen

- Wie viele Hosts tatsächlich verwundbar *und* über einen funktionierenden RCE-Pfad erreichbar sind.
- Wie viele vor oder kurz nach dem Patch kompromittiert wurden.
- Wann LTS-Pakete Remi / Docker Hub / Shared Hosting erreichen.
- Ob CISA KEV einträgt und welche IoCs Vendoren publizieren.

---

## 10. Historischer Vergleich

- **Log4Shell** (CVE-2021-44228), XII 2021 [P][^cflog4][^cplog4]
  - *Ähnlichkeiten:* Massive Exposition einer „unsichtbaren“ Abhängigkeit; WAF-Stopgap; Mem-Name
  - *Tempo / Unterschiede:* Cloudflare: Probes 8 Tage vor Disclosure; Exploits **9 Minuten** danach; Check Point: **>800k** Angriffe / 72 h
- **Heartbleed**, IV 2014 [P][^heartbleed]
  - *Ähnlichkeiten:* Kritischer Bug in Internet-Fundamenten; Early Notify Ausgewählter
  - *Tempo / Unterschiede:* Google/Cloudflare wussten vor Public; CRA Kanada: ~900 SIN
- **PHP-CGI CVE-2024-4577**, VI 2024 [P][^akamai4577][^imperva4577]
  - *Ähnlichkeiten:* RCE in PHP; schnelle Bewaffnung
  - *Tempo / Unterschiede:* Akamai: Ausnutzung **binnen 24 h**; Imperva: TellYouThePass **<48 h**
- **OpenSSL 3.0.7 Pre-Announce**, X–XI 2022 [P][^openssl307]
  - *Ähnlichkeiten:* Öffentliche CRITICAL-Ankündigung vor Details
  - *Tempo / Unterschiede:* Nach Prenotification auf HIGH **abgestuft**

**Muster 24–72 h [A]:** Nach öffentlichem Patch erwarten (1) Massenscans, (2) PoCs binnen Stunden, (3) Ransomware/Bots in 1–2 Tagen, wenn RCE glaubwürdig ist. Mit KI gehen BSI und Sansec von **Stunden** aus, nicht Tagen [P/D][^bsipresse][^sansec].

---

## 11. Lehren

### Für Anwendungsentwickler
Nicht annehmen, „sicherer Anwendungscode“ schütze vor einem Runtime-Bug. Auf unterstütztem PHP bleiben; selten genutzte Pre-Init-Features (Upload Progress) nicht ohne Bedarf voraussetzen [A][^phpadv].

### Für Ops / SRE
PHP inventarisieren **einschließlich gebündelter** Kopien (Appliances, Panels, Container). Patch-Fenster ≠ Pressemitteilung — `php -v` / Paket auf jedem Host prüfen. Plan B: Internet-facing Systeme isolieren, wenn kein Patch da ist [P][^ncscuk][^certeu].

### Für Open-Source-Maintainer
Große Memory-Safety-Fixes brauchen Zeit und Distro-Prenotification; Embargo-Leaks sind real — „release earlier“-Plan bereithalten (PHP hatte einen und nutzte ihn) [P][^announce].

### Für Regierungen / CERTs
Vorsorgliche Abschaltungen bremsen Risiko, kosten aber Vertrauen in öffentliche Dienste. Abhängigkeitslisten (NCSC-NL/php2shell) im Stil von Log4Shell sind wertvoll [P][^ncscnl].

### Für Medien
Offizielles CVSS 9.2 von „CVSS 10“-Gerüchten trennen; CDN-„early attacks“ von CERT-„kein Missbrauch“; Community-Namen von Vendor-Mitteilungen. Unverifizierte PoCs nicht als „den Exploit“ verkaufen [A].

---

## 12. Offene Fragen

1. Ubuntu-/Debian-/RHEL-/Remi-/Docker-Hub-Pakete — wann „Needs evaluation“ zu fixed wird.
2. CISA KEV / EPSS / unabhängige IoCs.
3. Klärung Knecht versus NCSC-NL/BSI zu ITW.
4. Offizielle Calif-/OpenAI-Write-ups (Wiz kündigte ihre Blogs an) [D][^wiz].
5. Schicksal von EOL-Hosts (5.x–8.1) ohne Backport.
6. Varianten — Wiz: „other tracked and likely untracked variants“ [D][^wiz].
7. Rückkehr der NL-/BE-/FR-/FI-Sites.
8. CMS-/Appliance-Firmware (Nextcloud, pfSense, cPanel…) [D][^heise].
9. Evolution von WAF-Bypasses.
10. Compromise-Hunting rückwärts — wie weit zurück, ist weiterhin unklar.

---

## Anhang A: Vollständige Zeitachse

*Zeiten in UTC; in Klammern Warschauer Zeit (CEST).*

- **2026-05-01** — Calif: „MAD Bugs“ (separater UAF) [P]
- **2026-08-19…24** — Wiz: Discover → RCE Drupal/WP → Report [D]
- **2026-09-21** — PHP beginnt koordinierten Fix [D]
- **2026-10-14** — PHP-Foundation-Blog (Daybreak Red) [P]
- **2026-10-18 15:46** (17:46) — Bailout-Fix-Commit [P]
- **2026-10-19 07:30–17:04** (09:30–19:04) — Annotated Release-Tags [P]
- **2026-10-20 15:20** (17:20) — Tell HN — CVE-Leak [P]
- **2026-10-20 16:39** (18:39) — Beaumont [P]
- **2026-10-20 18:26** (20:26) — watchTowr — Embargo Thursday 11am ET [P]
- **2026-10-20 19:33** (21:33) — PHP ANNOUNCE — Wed 14:00 UTC [P]
- **2026-10-20 19:35** (21:35) — watchTowr-FAQ [P]
- **2026-10-20 20:27** (22:27) — php2shell-Video [P]
- **2026-10-20 20:33** (Zeitzone auf Seite mehrdeutig) — CERT-EU 2026-018 [P/?]
- **2026-10-20 21:20** (23:20) — CERT.at-Warnung [P]
- **2026-10-21 02:13** (04:13) — Girgias: only mitigation is patching [P]
- **2026-10-21 07:43** (09:43) — Knecht: early attacks + WAF [P]
- **2026-10-21 Vormittag–Mittag** — Massives Offline NL/BE/FR/FI [P]
- **2026-10-21 11:59** (13:59) — NCSC-NL-Mitteilung [P]
- **2026-10-21 13:33:59** (15:33:59) — 8.5.12-Tarball Last-Modified [P]
- **2026-10-21 13:34** (15:34) — Beide GHSA veröffentlicht [P]
- **2026-10-21 ~13:35** (~15:35) — php.net-Advisory [P]
- **2026-10-21 13:43** (15:43) — Wiz-Blog [P]
- **2026-10-21 13:44** (15:44) — Docker-PR #1694 [P]

---

## Anhang B: Glossar

| Begriff | Bedeutung |
|---|---|
| **SAPI** | Server API — Schicht zwischen Webserver und PHP-Engine |
| **Worker** | PHP-Prozess, der viele Requests nacheinander bedient |
| **OOM** | Out of memory — Speichermangel |
| **Bailout / longjmp** | Notausstieg aus C-Kontext ohne normales Stack-Unwinding |
| **Use-after-free (UAF)** | Nutzung von Speicher nach Freigabe |
| **Stale Pointer / Global** | Zeiger/Globale auf veralteten Request-Speicher |
| **mod_php** | PHP als Apache-Modul |
| **PHP-FPM** | FastCGI Process Manager |
| **CVSS v4.0** | Common Vulnerability Scoring System, Version 4 |
| **Embargo** | Vertraulichkeitsphase vor öffentlicher Offenlegung |
| **KEV** | CISA Known Exploited Vulnerabilities Catalog |
| **EOL** | End of life — keine offiziellen Updates |

---

## Anhang C: Defensive Checkliste

*Wie prüfen, dass Sie gepatcht sind — nicht, wie man angreift.*

1. **PHP finden:** `php -v` auf Hosts; Docker-Images; Panels; Appliances; Windows `php.exe` / `php-cgi.exe` [D][^huntress].
2. **Zielversionen:** ≥ 8.5.12 / 8.4.27 / 8.3.36 / 8.2.35; bei EOL — Vendor-LTS oder Upgrade [P][^phpadv].
3. **Nach dem Update:** **alle** Worker neu starten (FPM Reload/Restart, Apache Graceful/Restart); Version im echten SAPI prüfen, nicht nur CLI.
4. **Container:** sobald Hub-Tags existieren — `pull` + Redeploy; PR #1694 ist erst der Anfang der Kette [P][^docker].
5. **Remi:** nicht auf Remis „heute“-Update warten — Distro-Pakete oder Build aus Source [P][^phpfremi].
6. **Vorübergehend (nicht statt Patch):** Maßnahmen aus den Advisories; Vendor-WAFs als Stopgap [P][^phpadv][^cfwaf].
7. **Hunting danach:** ungewöhnliche PHP-Child-Prozesse (Shell, curl, wget); Webshells; neue Docroot-Dateien; Worker-Churn; seltsames Multipart + 500 [D][^huntress][^wiz].
8. **Internet-facing EOL:** Upgrade, VPN oder Offline [P][^ncscuk][^certeu].

---

## Anhang D: Quellen

### Primär
[^phpadv]: https://www.php.net/index.php#2026-10-21-5
[^phppre]: https://www.php.net/archive/2026.php#2026-10-20-1
[^ghsa618]: https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w
[^ghsa619]: https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp
[^commit]: https://github.com/php/php-src/commit/31c0ea7d7ff1d1fccb6492e52dab544011628065
[^announce]: https://discourse.thephp.foundation/t/announce-upcoming-critical-php-security-release/6251
[^phpfound]: https://thephp.foundation/blog/2026/10/14/how-the-php-security-team-handles-your-reports/
[^audit2024]: https://thephp.foundation/blog/2025/04/10/php-core-security-audit-results/
[^tarball]: https://www.php.net/distributions/php-8.5.12.tar.xz (Last-Modified-Header)
[^atom]: https://www.php.net/releases/feed.php
[^tags]: https://api.github.com/repos/php/php-src/git/tags/c96586077b050b362744ba295f97f6395f58a75a (annotated Tag php-8.5.12, Tagger-Datum 2026-10-19; Tags 8.4.27/8.3.36/8.2.35: https://github.com/php/php-src/tags)
[^girgias]: https://phpc.social/@Girgias/117476477429221001

### Entdeckung / Research
[^wiz]: https://www.wiz.io/blog/php2shell-php-rce
[^wtx]: https://x.com/watchtowrcyber/status/2112611507749982605
[^wtxfaq]: https://watchtowr.com/intelligence/php-cve-2026-109618-faq/
[^huntress]: https://www.huntress.com/blog/php2shell-leaked-critical-php-vulnerabilities
[^sansec]: https://sansec.io/research/php2shell
[^tenable]: https://www.tenable.com/blog/php2shell-cve-2026-109618-cve-2026-109619-frequently-asked-questions-about-critical-php-remote
[^heise]: https://www.heise.de/news/php2shell-Kritische-Sicherheitsluecken-erlauben-Codeeinschleusung-in-PHP-11492938.html
[^modat]: https://modat.io/blog/php-exposure-before-the-21-oct-2026-security-release/
[^califmad]: https://blog.calif.io/p/mad-bugs-finding-and-exploiting-a
[^jackal]: https://jackalsyn.com/posts/php-up-2026.html

### Behörden und Medien
[^certeu]: https://cert.europa.eu/publications/security-advisories/2026-018/
[^bsipdf]: https://www.bsi.bund.de/SharedDocs/Cybersicherheitswarnungen/DE/2026/2026-297981-1032.pdf?__blob=publicationFile&v=3
[^bsipresse]: https://www.bsi.bund.de/DE/Service-Navi/Presse/Pressemitteilungen/Presse2026/261021_PHP-kritische-Schwachstelle.html
[^ncscuk]: https://www.ncsc.gov.uk/news/critical-security-issue-affecting-php
[^ncscnl]: https://www.rijksoverheid.nl/actueel/nieuws/2026/10/21/ncsc-ernstige-kwetsbaarheden-in-php
[^certat]: https://www.cert.at/de/aktuelles/2026/10/bevorstehendes-kritisches-php-sicherheitsupdate
[^certpl]: https://moje.cert.pl/komunikaty/2026/195/krytyczne-podatnosci-w-php-umozliwiajace-zdalne-wykonanie-kodu/
[^certfr]: https://cert.cyber.gouv.fr/alerte/CERTFR-2026-ALE-014/
[^nos]: https://nos.nl/liveblog/2636066-websites-kwetsbaar-voor-softwarelek-digid-en-mijnoverheid-uit-de-lucht
[^w3t]: https://w3techs.com/technologies/details/pl-php
[^cfwaf]: https://developers.cloudflare.com/changelog/post/2026-10-21-emergency-waf-release-cfmr/
[^knecht]: https://x.com/dok2001/status/2112811965735202970
[^hnleak]: https://news.ycombinator.com/item?id=50167754
[^beaumont]: https://cyberplace.social/@GossiTheDog/117474220875882526
[^firsov]: https://x.com/k_firsov/status/2112641845926989944
[^dormann]: https://infosec.exchange/@wdormann/117475540081194496
[^docker]: https://github.com/docker-library/php/pull/1694
[^ubuntu]: https://ubuntu.com/security/CVE-2026-109618
[^kev]: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
[^thn]: https://thehackernews.com/2026/10/php2shell-two-unpatched-critical-php.html
[^verge]: https://www.theverge.com/tech/1015257/php-vulnerability-patch-website-security-wordpress
[^bwoebi]: https://news.ycombinator.com/item?id=50175654
[^beaumont2]: https://cyberplace.social/@GossiTheDog/117477870253346830
[^imunify]: https://blog.imunify360.com/php-cve-2026-109618-cve-2026-109619/
[^bunny]: https://bunny.net/blog/cve-2026-109618-and-cve-2026-109619/
[^acsc]: https://www.cyber.gov.au/alert/critical-vulnerabilities-in-php
[^ipa]: https://www.ipa.go.jp/security/security-alert/2026/pre-alert20261021.html
[^phphist]: https://www.php.net/manual/en/history.php.php
[^wtxad]: https://watchtowr.com/intelligence/php-remote-code-execution-php2shell/
[^phpfback]: https://thephp.foundation/blog/2026/10/21/todays-php-security-release-and-how-were-strengthening-php-security/
[^phpfremi]: https://x.com/ThePHPF/status/2112828424486056183
[^secweek]: https://www.securityweek.com/php2shell-mass-exploitation-looms-for-leaked-critical-php-flaws/
[^nu]: https://www.nu.nl/tech/6413897/live-grote-nederlandse-sites-uit-voorzorg-offline-wegens-kwetsbaarheid-php.html
[^bbc]: https://www.bbc.com/news/articles/cmly0lg3w5x2o
[^nbc]: https://www.nbcnews.com/tech/security/critical-vulnerabilities-php-update-systems-rcna604751
[^firsovitw]: https://x.com/k_firsov/status/2112714573287698763

### Historisch
[^cflog4]: https://blog.cloudflare.com/exploitation-of-cve-2021-44228-before-public-disclosure-and-evolution-of-waf-evasion-patterns/
[^cplog4]: https://blog.checkpoint.com/security/the-numbers-behind-a-cyber-pandemic-detailed-dive/
[^akamai4577]: https://www.akamai.com/blog/security-research/2024-php-exploit-cve-one-day-after-disclosure
[^imperva4577]: https://www.imperva.com/blog/update-cve-2024-4577-quickly-weaponized-to-distribute-tellyouthepass-ransomware/
[^heartbleed]: https://www.smh.com.au/technology/heartbleed-disclosure-timeline-who-knew-what-and-when-20140414-zqurk.html
[^openssl307]: https://openssl-library.org/post/2022-11-01-email-address-overflows/

---

*Ende Version 1.0 (DE). Aktualisieren mit Distributionspaketen, IoCs und Calif-/OpenAI-Write-ups.*
