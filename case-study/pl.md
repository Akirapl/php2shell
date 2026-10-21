---
title: "PHP2Shell — studium przypadku"
subtitle: "Pogłębione, długoterminowe studium przypadku CVE-2026-109618 i CVE-2026-109619"
lang: pl
version: "1.0"
asof: "2026-10-21 14:05 UTC (16:05 CEST)"
---

# PHP2Shell — studium przypadku

**Pogłębione studium przypadku krytycznych podatności CVE-2026-109618 i CVE-2026-109619 w rdzeniu PHP**

- **Wersja dokumentu:** 1.0 (wersja wzorcowa — polska; EN i DE to adaptacje naturalne, nie dosłowne)
- **Stan na:** 21.10.2026, 14:05 UTC (16:05 CEST) — ok. 30 minut po publikacji poprawek
- **Charakter:** analiza obronna i historyczna; **bez** kodu exploitów, payloadów, PoC ani instrukcji ataku
- **Konwencja:** **[P]** źródło pierwotne · **[D]** doniesienie strony trzeciej · **[?]** otwarte / sprzeczne · **[A]** analiza autorów
- **Rejestr dowodów (evidence ledger):** każde istotne twierdzenie ma identyfikator (CLM-…) w [`case-study/evidence-ledger.jsonl`](https://github.com/Akirapl/php2shell/blob/main/case-study/evidence-ledger.jsonl) (także [CSV](https://github.com/Akirapl/php2shell/blob/main/case-study/evidence-ledger.csv)) — ze źródłem pierwotnym, dokładnym miejscem w nim, czasem publikacji i zdarzenia, statusem weryfikacji i dowodami przeciwnymi
- **Strefy czasowe:** UTC; w nawiasie czas warszawski. 20–21.10.2026: **CEST = UTC+2**

> **Uwaga redakcyjna.** Dokument powstał w dniu publikacji poprawek. Pakiety dystrybucyjne, potwierdzona eksploatacja i pełne write-upy odkrywców dopiero się ustalają. Każde twierdzenie ma przypis; rozdział 12 i dziennik zmian mówią, co może zmienić obraz.

## Dziennik zmian

- **1.0.1** (2026-10-21 17:30 UTC) — Dodany rejestr dowodów (CLM-0001…). Poprawki z weryfikacji: commit poprawki zmienia 423 pliki, nie 300 (API commitów GitHuba pokazuje tylko pierwsze 300); dodany pierwotny termin wg PHP Foundation (22.10, 14:00 UTC) jako trzecia, sprzeczna wersja embarga; dodane źródła: watchTowr Active Defense, „15 minut” Sansec (SecurityWeek), ostrzeżenie o Remi (PHP Foundation na X), listy NU.nl/BBC, Patchstack/Firsov; doprecyzowany cytat BSI; poprawiona data Huntress; testy Log4Shell według Cloudflare były 8 dni (nie 9) przed ujawnieniem; usunięta niepotwierdzona uwaga o Aikido „od czerwca 2026” i złagodzone nieweryfikowalne „at scale” Hadrian.
- **1.0** (2026-10-21 14:05 UTC) — Pierwsze wydanie. Źródła: php.net, GHSA, commit poprawki, Wiz, watchTowr, BSI, NCSC UK, NCSC-NL, CERT-EU, CERT.at, CERT Polska, CERT-FR, NOS, W3Techs, Modat, heise, SecurityWeek, Huntress, Tenable, Cloudflare, Docker PR, Ubuntu tracker, HN, Mastodon; plus porównania historyczne (Log4Shell, Heartbleed, CVE-2024-4577, OpenSSL 3.0.7).

## Spis treści

0. [TL;DR i przegląd](#0-tldr-i-przeglad-na-jednej-stronie)
1. [Tło: PHP i cykl życia żądania](#1-tlo-php-w-sieci-i-cykl-zycia-zadania)
2. [Podatności — w głąb](#2-podatnosci-wyjasnione-w-glab)
3. [Odkrycie i AI](#3-odkrycie-wiz-calif-openai-i-badania-wspomagane-ai)
4. [Skoordynowane ujawnienie](#4-skoordynowane-ujawnienie-podstawy-i-przebieg)
5. [Wyciek i nazwa PHP2Shell](#5-wyciek-i-nazwa-php2shell)
6. [Dzień poprawki](#6-dzien-poprawki)
7. [Wyścig o exploit](#7-wyscig-o-exploit)
8. [Reakcja obrońców](#8-reakcja-obroncow)
9. [Ekspozycja i skutki](#9-ekspozycja-i-skutki)
10. [Porównanie historyczne](#10-porownanie-historyczne)
11. [Wnioski](#11-wnioski)
12. [Pytania otwarte](#12-pytania-otwarte)
- [Aneks A: Oś czasu](#aneks-a-pelna-os-czasu)
- [Aneks B: Słowniczek](#aneks-b-slowniczek)
- [Aneks C: Lista kontrolna](#aneks-c-lista-kontrolna-dla-obroncow)
- [Aneks D: Źródła](#aneks-d-zrodla)

---

## 0. TL;DR i przegląd na jednej stronie

**W jednym akapicie.** 21 października 2026 około **13:34 UTC** zespół bezpieczeństwa PHP opublikował wydania **8.5.12, 8.4.27, 8.3.36 i 8.2.35** oraz dwa biuletyny GitHub opisujące krytyczne podatności w samym silniku PHP: **CVE-2026-109618** („RCE via OOM corruption”) i **CVE-2026-109619** („RCE via stale global state”), obie z oceną **CVSS v4.0 9.2** [P][^ghsa618][^ghsa619][^phpadv]. Obie wynikają z tego samego wzorca: gdy PHP przerywa obsługę żądania w trybie awaryjnym (zwłaszcza przy wyczerpaniu pamięci), może zostawić wewnętrzny stan wskazujący na pamięć, która już nie istnieje — a kolejny krok lub kolejne żądanie na tym samym procesie potrafi z tego „ducha” skorzystać. W konfiguracji **Apache + mod_php** wykazano **nieuwierzytelnione** zdalne wykonanie kodu **zanim uruchomi się kod aplikacji** [P][^phpadv]. Odkrycie przypisuje sobie Wiz Research we współpracy z Calif i OpenAI, z intensywnym użyciem modeli AI [D][^wiz]. Embargo na czwartek 22.10 zostało złamane wyciekiem 20.10, co zmusiło PHP do zapowiedzi i przyspieszenia wydania o dobę [P][^wtx][^phppre]. W Holandii, Belgii, Francji i Finlandii część stron wyłączono profilaktycznie [P][^nos]. Na moment zamknięcia tej wersji brak niezależnie potwierdzonej eksploatacji „w dziczy”; doniesienia są sprzeczne [?].

> ### Najważniejsze fakty
>
> - **Identyfikatory:** CVE-2026-109618 (GHSA-w8hw-w9fx-j79w), CVE-2026-109619 (GHSA-6wmf-4rv5-p3rp) [P]
> - **CVSS v4.0:** 9.2 · `AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N` (oba) [P]
> - **CWE:** 416, 755, 824, 1325, 1419 [P]
> - **Wpływ:** unauth RCE (worker WWW); 619: także ujawnienie pamięci [P]
> - **Najgorszy SAPI:** Apache mod_php (przed kodem aplikacji) [P]
> - **Poprawione:** 8.5.12, 8.4.27, 8.3.36, 8.2.35; backporty źródłowe 7.4/8.0/8.1 [P]
> - **Publikacja:** GHSA 13:34 UTC; tarball 8.5.12 `Last-Modified` 13:33:59 GMT [P]
> - **Embargo pierwotne:** 22.10.2026 11:00 ET (15:00 UTC = 17:00 CEST; przeciek z HN podawał 18:00 CEST, zob. 5.1) [P]; PHP Foundation podała później pierwotny termin wydania 22.10 **14:00 UTC** — relacje są sprzeczne [?][^phpfback]
> - **Credits GHSA:** sagitzadik-wiz, tomash-areion, lcfr-hax, amyb-oai [P]
> - **Poprawka:** Arnaud Le Blanc (+ Tovilo, Zelenka, Dossche, Grekas); +11 556/−1 017, 423 pliki [P]
> - **Udział PHP:** 69,3% stron o znanym języku serwerowym (W3Techs 21.10) [P]
> - **Ekspozycja:** 4,38 mln usług / 1,89 mln hostów; ~79% EOL (Modat 20.10) [D]
> - **Pełna ochrona:** tylko aktualizacja [P]
>
> *Rejestr: kluczowe fakty = CLM-0001…CLM-0014; status eksploatacji = CLM-0054…CLM-0065.*

**Co jest nowe** [A]: (1) błąd w *runtime*, nie w aplikacji; (2) AI w odkryciu i — wg badaczy — w uczynieniu exploitu praktycznym; (3) wyciek embarga → 22-godzinny wyścig; (4) profilaktyczne wyłączenia stron w kilku krajach UE przed poprawką.

*Oś czasu*

```mermaid
flowchart TB
  subgraph D[Discovery Aug 2026]
    d1[19 Aug: Wiz first bug]
    d2[20-21 Aug: RCE Drupal and WordPress]
    d3[24 Aug: Report to PHP]
  end
  subgraph R[Remediation]
    r1[21 Sep: PHP confirms]
    r2[14 Oct: Daybreak triage blog]
    r3[18 Oct: Bailout fix commit]
    r4[19 Oct: Annotated tags 8.2.35 to 8.5.12]
  end
  subgraph L[Leak 20 Oct]
    l1[15:20 UTC: Tell HN CVE numbers]
    l2[18:26: watchTowr confirms embargo]
    l3[19:33: PHP announce Wed 14:00 UTC]
    l4[20:27: php2shell video]
  end
  subgraph P[Patch day 21 Oct]
    p1[Morning: mass offline NL BE FR FI]
    p2[07:43: Cloudflare early attacks]
    p3[13:34: GHSA and tarballs]
    p4[13:43: Wiz blog]
  end
  d1 --> d2 --> d3 --> r1 --> r2 --> r3 --> r4 --> l1 --> l2 --> l3 --> l4 --> p1 --> p2 --> p3 --> p4
```

---

## 1. Tło: PHP w sieci i cykl życia żądania

### 1.1 Jak duży jest PHP

PHP stworzył Rasmus Lerdorf w 1994 r. (jako „Personal Home Page Tools”); kod źródłowy udostępnił publicznie w czerwcu 1995 r. [P][^phphist]. Według W3Techs (21.10.2026) PHP używa **69,3%** stron o znanym języku serwerowym; wśród nich **65,2%** to wersja 8, **27,0%** wersja 7, **7,7%** wersja 5, **0,1%** wersja 4 [P][^w3t]. Na PHP działają m.in. WordPress, Drupal, Joomla, Magento i MediaWiki [D][^wiz].

**Zgodnie z metodologią** [A]: „69,3%” to odsetek stron *o rozpoznanym* języku, nie „całego Internetu”. Nagłówki w stylu „70% of the Internet” (Wiz) to uproszczenia [D][^wiz].

### 1.2 Cykl życia żądania (dla nie-ekspertów)

PHP zwykle nie „stoi samotnie”: jest wbudowany w serwer WWW albo działa jako pula procesów. Interfejs nazywa się **SAPI** (Server API).

- **Apache mod_php**
  - *Jak działa:* PHP w procesach Apache (prefork: wiele procesów, każdy obsługuje żądania kolejno).
  - *Znaczenie dla PHP2Shell:* Najgorszy przypadek: shutdown jest wywoływany **zawsze**, nawet gdy start się nie powiódł [P][^ghsa618].
- **PHP-FPM**
  - *Jak działa:* Osobna pula; nginx/Apache przez FastCGI.
  - *Znaczenie dla PHP2Shell:* Przy nieudanym starcie FPM kończy childa — przerywa najprostszą ścieżkę; inne pozostają [P][^ghsa618][^ghsa619].
- **CGI / php-cgi**
  - *Jak działa:* Klasycznie proces na żądanie (lub FastCGI).
  - *Znaczenie dla PHP2Shell:* Wymieniony jako podatny [P][^phpadv].
- **FrankenPHP**
  - *Jak działa:* Nowoczesny serwer aplikacji.
  - *Znaczenie dla PHP2Shell:* Analiza kodu: prawdopodobnie jak mod_php przy shutdown [P][^ghsa618].
- **LiteSpeed LSAPI**
  - *Jak działa:* Model zbliżony do FPM.
  - *Znaczenie dla PHP2Shell:* Aplikacyjnie zależne ścieżki „prawdopodobne, nie zwalidowane” [P][^ghsa618].

**Analogia** [A]: worker PHP to biurko urzędnika. Każde żądanie to sprawa na biurku. Po sprawie urzędnik powinien schować wszystkie teczki. Jeśli gasi światło w panice (OOM / fatal), może zostawić kartkę z adresem teczki, której już nie ma. Następny petent — to samo biurko — widzi adres i traktuje go jak ważny. Stąd „stale global state” i „OOM corruption”.

*Cykl życia żądania*

```mermaid
flowchart TB
  subgraph Client
    B[Przeglądarka / klient HTTP]
  end
  subgraph WebServer[Serwer WWW]
    WS[Apache / nginx / LiteSpeed]
  end
  subgraph SAPI[SAPI — warstwa łącząca]
    MP[mod_php w procesie Apache]
    FPM[PHP-FPM — pula workerów]
    CGI[php-cgi / CGI]
  end
  subgraph Engine[Silnik PHP — jeden worker]
    ST[1. Start żądania<br/>parsowanie ciała multipart]
    IN[2. Inicjalizacja modułów / executor]
    APP[3. Kod aplikacji]
    SH[4. Shutdown żądania<br/>zwalnianie pamięci]
    GL[(Stan globalny workera<br/>error / session / object)]
  end
  B -->|HTTP| WS
  WS --> MP
  WS --> FPM
  WS --> CGI
  MP --> ST
  FPM --> ST
  CGI --> ST
  ST --> IN --> APP --> SH
  ST -.->|może zapisać stan przed init| GL
  SH -.->|musi wyczyścić| GL
  SH -->|kolejne żądanie tego samego workera| ST
  classDef risk fill:#3d1f1f,stroke:#f85149,color:#fff
  class ST,GL,SH risk
```

### 1.3 Dlaczego to ma znaczenie

Większość krytycznych luk w ekosystemie PHP dotyczy *aplikacji* (WordPress, wtyczki). Tu podatność jest w **silniku** [P][^phpadv]. Aplikacja „Hello World” na podatnej wersji też jest narażona [D][^wiz]. Stąd skala: inventory obejmuje CMS-y, panele (cPanel/Plesk), appliances z PHP w firmware i ukryte `php.exe` [D][^huntress][^heise].

---

## 2. Podatności — wyjaśnione w głąb

### 2.1 Wspólny wzorzec

Oficjalne biuletyny i blog Wiz opisują wariant tego samego problemu pamięciowego na granicy żądań [P][^ghsa618][^ghsa619][^wiz]:

1. Operacja zapisuje stan należący do żądania w lokalizacji globalnej workera (**producent**).
2. Fatal / OOM / diagnostyka przerywa ścieżkę przed resetem.
3. Pamięć żądania jest zwalniana; global nadal wskazuje na nią.
4. To samo worker obsługuje kolejne żądanie.
5. Operacja przed normalną inicjalizacją czyta ten wskaźnik (**konsument**) → use-after-free → przy odpowiednim układzie sterty: RCE.

**Dlaczego błędy memory-safety w runtime są trudne** [A]: nie są „jedną dziurą w funkcji X”, lecz własnością interakcji alokatora, obsługi błędów (`longjmp` / bailout), wielu rozszerzeń i wielu SAPI. Poprawka musiała zmienić strategię OOM i zresetować szeroki zestaw globali (~400 plików) [P][^commit].

### 2.2 CVE-2026-109618 — RCE via OOM corruption

**Co było nie tak.** PHP używał `longjmp()` przy OOM, by wyjść z kontekstu i przerwać żądanie. Gdy pamięć żądania była tylko częściowo zainicjalizowana, early-exit zostawiał invalid state; shutdown mógł go potraktować jak poprawny [P][^ghsa618].

**Strategie OOM** (koncepcyjnie, bez przepisów) [P][^ghsa618]: multipart bez użytecznego Content-Length; nieograniczona liczba nagłówków części (więcej pamięci niż na przewodzie); puste kontrolki plików nie liczą się do `max_file_uploads`, ale tworzą metadane. OOM może też wynikać z zachowania aplikacji.

**Dlaczego mod_php jest najgorszy.** Apache mod_php **bezwarunkowo** woła request shutdown, nawet gdy startup się nie udał. Body parsing przy starcie może wyczerpać `memory_limit` w oknie invalid state — **zanim uruchomi się aplikacja** [P][^ghsa618][^phpadv]. FPM kończy childa przy nieudanym starcie; źródłowa analiza uznaje FPM za podatny, ale pełnego exploitu FPM dla 618 nie wykazano [P][^ghsa618].

**Poprawka.** Usunięcie `longjmp()` dla OOM → soft OOM na VM safe point + hard OOM z `_exit()` przy drugim progu [P][^ghsa618][^commit].

### 2.3 CVE-2026-109619 — RCE via stale global state

**Co było nie tak.** Globalny stan workera (error / session / object / extension) może wskazywać na pamięć żądania. Fatal, OOM lub diagnostyka zostawia stale pointer; kolejne żądanie konsumuje go **przed** normalną inicjalizacją [P][^ghsa619].

**Potwierdzeni konsumenci** [P][^ghsa619]:

- **Diagnostyki INI przed init** — ostrzeżenia/deprecacje przy stosowaniu ustawień (`.htaccess` / `php_value` w mod_php; `PHP_VALUE` w FPM) zanim executor się zainicjalizuje. Ukrycie diagnostyk (`error_reporting`, `@`) **nie chroni**.
- **Session upload progress** — może sięgnąć sesji przed zwykłą inicjalizacją; niezależny od ścieżki INI.

**Najsilniejszy wykazany przypadek:** `fatal_error_backtraces` (PHP 8.5) + diagnostyka → potwierdzone RCE na mod_php. Session upload progress RCE: potwierdzone na mod_php **i** FPM [P][^ghsa619].

**Wiz o czterech klasach** (zgrupowanych pod dwoma CVE) [D][^wiz]: upload-progress unserializer UAF; ujawnienie pamięci przez PHPSESSID; fatal backtrace UAF; OPcache type confusion. Kierunkowo zgodne z GHSA; szczegóły łańcuchów pochodzą od Wiz.

### 2.4 CVSS v4.0 — wektor pole po polu

Oba CVE: `CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N` → **9.2** [P][^ghsa618][^ghsa619].

| Pole | Wartość | Znaczenie |
|---|---|---|
| AV:N | Network | Atak przez sieć |
| AC:H | High | Wysoka złożoność (układ sterty, warunki) |
| AT:P | Present | Wymagane warunki w systemie |
| PR:N | None | Bez uwierzytelnienia |
| UI:N | None | Bez interakcji użytkownika |
| VC/VI/VA:H | High | Pełny wpływ na poufność, integralność, dostępność **podatnego** systemu |
| SC/SI/SA:N | None | Brak ocenionego wpływu na systemy **następne** w łańcuchu |

Wczesne doniesienia mówiły o „CVSS 10.0” [D][^hnleak][^wtx] — oficjalna ocena PHP to 9.2 z AC:H i AT:P.

### 2.5 Wersje: poprawione, EOL, backporty

| Gałąź | Status wsparcia PHP | Poprawka |
|---|---|---|
| 8.5 | wspierana | **8.5.12** |
| 8.4 | wspierana | **8.4.27** |
| 8.3 | wspierana | **8.3.36** |
| 8.2 | security do 31.12.2026 | **8.2.35** |
| 8.1 / 8.0 / 7.4 | EOL | minimalne **backporty źródłowe**; brak oficjalnych wydań |
| ≤ 7.3 / 5.x | EOL | brak oficjalnego fix; dystrybucje LTS mogą backportować |

[P][^phpadv]. Zakres „od 5.4” / „od PHP 5” pochodzi z Wiz, CERT-EU, NCSC-NL i podobnych — nie z tabeli `vulnerable_version_range` w GHSA (tam widać tylko gałęzie z fix) [P/D][^ghsa618][^wiz][^certeu][^ncscnl].

### 2.6 Mitigacje niepełne

PHP i core developerzy podkreślają: **jedyna pełna ochrona to update** [P][^phpadv][^girgias]. Środki tymczasowe (np. `memory_limit=-1`, `session.upload_progress.enabled=0`, na 8.5 `fatal_error_backtraces=0`) zmniejszają konkretne ścieżki, nie czynią instalacji bezpieczną [P][^phpadv]. Nie używać `RLIMIT_AS`/`RLIMIT_DATA` jako substytutu — mogą wymusić podatną ścieżkę `mmap`→`longjmp` [P][^ghsa618].

---

## 3. Odkrycie: Wiz, Calif, OpenAI i badania wspomagane AI

### 3.1 Oś czasu według Wiz (doniesienie)

| Data | Zdarzenie | Status |
|---|---|---|
| 19.08.2026 | Pierwsza podatność z Wiz Atlas, „Gemini 4 Argon”, „GPT-5.6 Sol” | [D][^wiz] |
| 20.08.2026 | Unauth RCE na Drupal | [D][^wiz] |
| 21.08.2026 | Unauth RCE na WordPress | [D][^wiz] |
| 24.08.2026 | Zgłoszenie do PHP | [D][^wiz] |
| 21.09.2026 | PHP potwierdza i zaczyna skoordynowaną poprawkę | [D][^wiz] |
| 21.10.2026 | Patche publiczne + blog Wiz | [P][^wiz][^phpadv] |

Credits w GHSA: `sagitzadik-wiz`, `tomash-areion`, `lcfr-hax`, `amyb-oai` [P][^ghsa618]. Wiz dziękuje Calif i OpenAI; heise opisuje audit Calif z PHP Ecosystem Security Team w ramach OpenAI „Patch the Planet” [D][^wiz][^heise]. Calif wcześniej (01.05.2026) publikował osobny research o 21-letnim UAF w PHP [P][^califmad].

### 3.2 Co AI zmienia w bug huntingu

Wiz: podatny kod był obecny ponad dekadę; zbudowanie działającego łańcucha wymagało łączenia wielu błędów i adaptacji do układów pamięci — frontier models „substantially reduced that barrier” [D][^wiz]. BSI spodziewa się masowej eksploatacji „w ciągu kilku godzin” od wydania poprawek, bo atakujący mogą je szybko przeanalizować narzędziami AI [P][^bsipresse].

**[A]** To nie znaczy, że „AI znalazło CVE sama”. Znaczy, że koszt przejścia od „trudnego błędu memory-safety” do wiarygodnego RCE na wielu targetach spadł. Ta sama ekonomia działa po stronie ataku (reverse patchy) i obrony (triage).

PHP Foundation (14.10.2026) opisała użycie **Daybreak Red** (OpenAI) do walidacji raportów i sortowania kolejki — kontekst rosnącej liczby zgłoszeń pisanych z pomocą AI [P][^phpfound].

### 3.3 Audyt 2024 i Ecosystem Security Team

W 2024 Quarkslab (zlecenie Sovereign Tech Agency / OSTIF) znalazło 17 findings z implikacjami bezpieczeństwa; heise zauważa, że podobny problem był przedmiotem sporów o remediację [P/D][^audit2024][^heise]. W maju 2026 PHP Foundation ogłosiła Ecosystem Security Team [D][^heise]. Incydent PHP2Shell pokazuje zarówno inwestycję w security, jak i długi ogon długu architektonicznego wokół bailout/OOM [A].

---

## 4. Skoordynowane ujawnienie: podstawy i przebieg

### 4.1 Coordinated disclosure 101

Typowy przebieg [A]: (1) prywatne zgłoszenie; (2) potwierdzenie i poprawka; (3) embargowane powiadomienie dystrybucji/LTS i wybranych partnerów; (4) jednoczesna publikacja advisories + wydań; (5) komunikacja ekosystemu. Cel: zminimalizować okno między wiedzą atakujących a dostępnością patchy.

### 4.2 Jak poszło tutaj

*Przepływ disclosure*

```mermaid
flowchart LR
  subgraph Private[Faza prywatna]
    D[Odkrycie<br/>Wiz / Calif / OpenAI<br/>VIII 2026]
    R[Zgłoszenie do PHP<br/>24.08.2026]
    F[Potwierdzenie i poprawka<br/>od 21.09.2026]
    EA[Early access<br/>dystrybucje LTS + partnerzy]
  end
  subgraph Break[Zerwanie embarga]
    L[Wyciek HN<br/>20.10 15:20 UTC]
    V[Wideo PHP2Shell<br/>20.10 20:27 UTC]
  end
  subgraph Public[Faza publiczna]
    A[Zapowiedź PHP<br/>20.10 19:33 UTC<br/>przesunięcie na 21.10 14:00]
    P[Release + GHSA<br/>21.10 ~13:34 UTC]
    W[WAF / agencje / hosty]
  end
  D --> R --> F --> EA
  EA -.->|plan: 22.10| A
  L --> A
  V --> A
  A --> P --> W
  F --> P
```

1. **Zgłoszenie i remediacja** (VIII–X 2026) — wg Wiz [D][^wiz]. Commit „Avoid state corruption via bailout” 18.10.2026; annotated tagi 19.10 [P][^commit][^tags].
2. **Early access.** php.net: „Linux distributions and LTS vendors received the patches in advance” [P][^phpadv]. Wiz wymienia Automattic, Akamai, AWS, Cloudflare, Fastly, Google, Imperva, Microsoft, Vercel i innych przy mitigacjach przed dniem zero [D][^wiz]. watchTowr wdrożył mitigacje Active Defense dla klientów platformy watchTowr przed patchem [P][^wtxad].
3. **Embargo.** watchTowr: pierwotnie **czwartek 22.10, 11:00 ET** (= 15:00 UTC) [P][^wtx].
4. **Pre-announcement po wycieku.** 20.10 19:33 UTC Jakub Zelenka (`bukka`) ogłasza wydanie **środa 21.10 14:00 UTC**, z prawem do wcześniejszego wydania przy wycieku szczegółów lub eksploatacji [P][^announce].
5. **Trade-off** [A]: zapowiedź dała ~18 h na inventory i okna patchowe, ale też potwierdziła realność CVE i przyciągnęła uwagę atakujących. OpenSSL 3.0.7 (2022) pokazał inny wariant: preannounce CRITICAL, potem obniżenie do HIGH po feedbacku prenotyfikowanych [P][^openssl307]. Tu ocena 9.2 utrzymała się.

Krytyka procesu (Kevin Beaumont, 21.10, 08:07 UTC): firmy cyberbezpieczeństwa, które dostały wcześniejsze powiadomienie, „przekazały klientom szczegóły” — według niego to „w praktyce odsprzedawanie dla zysku wiedzy projektów open source” („Protecting the ivory tower sucks”) [P][^beaumont2]. To napięcie wraca przy każdym embargu infrastrukturalnym [A].

---

## 5. Wyciek i nazwa „PHP2Shell”

### 5.1 Co wyciekło, kiedy i gdzie

*Czasy w UTC.*

- **20.10 15:20** — „Tell HN: 2x PHP RCE CVEs with CVSS 10.0 Incoming” (petecooper) — numery CVE, termin „22 Oct 18:00 CEST”; post później usunięty [P][^hnleak]. Uwaga o czasach: wpis pojawił się 20.10 o 15:20 UTC (17:20 CEST) i podawał 22.10 **18:00 CEST** (= 16:00 UTC), a watchTowr podał koniec embarga 22.10 o **11:00 ET** (EDT, = 15:00 UTC = **17:00 CEST**) — dwie relacje sprzed ujawnienia różnią się o godzinę; nie wiemy, która odpowiadała faktycznemu embargu [?][^wtx]. PHP Foundation podała później trzecią wartość: 22.10, 14:00 UTC [P][^phpfback]
- **20.10 16:39** — Kevin Beaumont (Mastodon): potwierdzenie wycieku numerów [P][^beaumont]
- **20.10 18:26** — watchTowr: „supposed to wait until Thursday 11am ET… We can confirm that they're real.” [P][^wtx]
- **20.10 19:33** — Oficjalna zapowiedź PHP [P][^announce]
- **20.10 20:27** — Kirill Firsov: wideo „php2shell” (~1,7 mln wyśw.); baner narzędzia „PHP2SHELL — PHP >= 5.4.0 RCE by Calif.IO” (zrzuty Dormanna) [P][^firsov][^dormann]
- **21.10 00:30** — J4ck3LSyN ogłasza „odtworzenie”; później sam odwołuje główną ścieżkę RCE [P/D][^jackal]

Komentarz HN „bwoebi” (tożsamość niezweryfikowana): wideo było powodem ogłoszenia „w tym momencie” [D][^bwoebi]. Znaczniki czasu temu przeczą: ogłoszenie wyszło o 19:33 UTC, wideo o 20:27 UTC, a PHP Foundation pisze, że wideo pojawiło się po zapowiedzi [P][^announce][^firsov][^phpfback].

### 5.2 Nazwa

„PHP2Shell” **nie** pochodzi z oficjalnego komunikatu PHP. Wzięła się z banera narzędzia w wyciekłym demo (Calif.IO) i rozeszła się w mediach; BSI odnotowuje porównanie marketingowe do Log4Shell [P/D][^bsipdf][^sansec]. PHP używa tytułów opisowych CVE/GHSA [P][^phpadv].

### 5.3 Skutek wycieku

PHP przesunął dzień z czwartku na środę i zastrzegł wcześniejsze wydanie [P][^announce][^phppre]. Finalnie tarballe i GHSA wyszły ~26 min przed zapowiedzianym 14:00 UTC (Last-Modified tarballi 13:33:59 UTC, pierwszy GHSA 13:34:13 UTC) [P][^tarball][^ghsa619]. Embargo dało dystrybucjom czas, ale nie ochroniło przed publicznym „poczuciem zero-day” przez ~22 h [A].

---

## 6. Dzień poprawki

### 6.1 Mechanika wydania

- Annotated tagi `php-8.2.35`…`php-8.5.12` utworzone **19.10** (Panteleev, Mann, Buckley, Scherzer) — przygotowanie przed dniem zero [P][^tags].
- Tarball `php-8.5.12.tar.xz`: `Last-Modified: Wed, 21 Oct 2026 13:33:59 GMT` [P][^tarball].
- GHSA-6wmf-4rv5-p3rp: **13:34:13Z**; GHSA-w8hw-w9fx-j79w: **13:34:25Z**; publisher: `bukka` [P][^ghsa618][^ghsa619].
- Feed Atom php.net stempluje `T00:00:00Z` w dniu wydania — to **konwencja daty dnia**, nie godzina publikacji [P][^atom].

### 6.2 Rozmiar poprawki

Commit `31c0ea7` „Avoid state corruption via bailout”: **+11 556 / −1 017** w **423** plikach (API commitów GitHuba pokazuje tylko pierwsze 300; commit na gałęzi 8.2 zmienia 389); UnwindExit zamiast bailout OOM + reset globali [P][^commit]. To nie „kilka linijek” — stąd opóźnienie dystrybucji i ryzyko regresji przy pośpiesznym backportowaniu [A].

### 6.3 „Patch released” ≠ „patched”

*Stan ~14:00 UTC 21.10:*

- **php.net source / Windows binaries** — dostępne [P][^phpadv]
- **Docker official `library/php`** — PR #1694 otwarty 13:44; po merge jeszcze oficjalne-images + buildy [P][^docker]
- **Remi (`rpms.remirepo.net`)** — **brak update „dziś”** — ostrzeżenie PHP Foundation [P][^phpfremi]
- **Ubuntu tracker** — wpisy CVE, status „Needs evaluation” na wielu release [P][^ubuntu]
- **Debian/RHEL paczki** — w toku / nie zweryfikowane w tym researchu [?]
- **Shared hosting** — zależy od hosta (heise: Uberspace planował czasowe wyłączenie PHP) [D][^heise]

Dopóki worker nie działa na binariach z poprawką, system jest podatny — niezależnie od komunikatu prasowego [A].

---

## 7. Wyścig o exploit

### 7.1 Jak atakujący „czytają” poprawki (koncepcyjnie)

Bez podawania przepisów [A]: przy dużym, publicznym diffie (tu: setki plików wokół OOM i resetu globali) analitycy porównują „przed/po”, lokalizują zmienione ścieżki błędów i rekonstruują warunki wejścia. BSI wprost wiąże tempo z narzędziami AI [P][^bsipresse]. CERT.at: pojawienie się kodu w sieci + ułatwienie reverse patcha → eksploatacja „zeitnah” po publikacji [P][^certat]. Sansec spodziewał się mass attacks w 15 min po release (cytowany przez SecurityWeek) [D][^secweek].

### 7.2 Fałszywe i odwołane PoC — sygnał vs szum

- Wideo Firsova / zrzuty Dormann (Calif.IO / `lcfr`) — **niezweryfikowane niezależnie w tym researchu** [P/D].
- jackalsyn.com: autor **odwołał** ścieżkę „cached-pointer” jako DEAD; ocenił realny bug na CVSS 5.3 / „NOT RCE” — **nie pokrywa się** z oficjalnym 9.2 [D][^jackal]. Traktować jako szum / częściową rekonstrukcję.
- GitHub: liczne repo „php2shell”/CVE (m.in. ikow/php2shell-poc) — Tenable ostrzega przed niezweryfikowanym kodem (ryzyko malware) [D][^tenable].

### 7.3 Telemetria eksploatacji (rozbieżna)

- **Cloudflare Knecht 07:43 UTC** — „early attacks emerging”; WAF stopgap [P][^knecht]
- **Huntress (stan na 21.10, 10:00 ET)** — brak w partner environments [P][^huntress]
- **watchTowr FAQ** — brak ITW (stan FAQ) [P][^wtxfaq]
- **NCSC-NL / BSI v1.0** — brak potwierdzonego misbruik / keine bestätigten Ausnutzungen [P][^ncscnl][^bsipdf]
- **Zespół PHP → ANP** — brak indikacji aktywnego abuse [D][^nu]
- **Patchstack (NBC), Firsov** — „reports of active exploitation” / „in the wild” [D][^nbc][^firsovitw] bez IoC; przytoczone przez Mattiasa Geniara „at scale” Hadrian nie występuje już w jego zaktualizowanym wpisie [?]
- **CISA KEV** — brak wpisu (stan researchu ~13:46 UTC) [P][^kev]

**Wniosek [A]:** do rozstrzygnięcia „czy ITW” potrzeba IoC od dużych sensorów (Cloudflare szczegóły, GreyNoise, Shadowserver) lub wpisu KEV — na razie komunikaty są sprzeczne.

---

## 8. Reakcja obrońców

*Mapa aktorów*

```mermaid
flowchart TB
  subgraph Discovery[Odkrycie]
    Wiz[Wiz Research]
    Calif[Calif / lcfr-hax / tomash-areion]
    OAI[OpenAI / amyb-oai]
  end
  subgraph PHPTeam[Zespół PHP]
    Bukka[Jakub Zelenka — publisher GHSA]
    Arnaud[Arnaud Le Blanc — autor poprawki]
    Co[Tovilo / Dossche / Grekas]
    RM[Release managerzy tagów]
  end
  subgraph Amplify[Wyciek i amplifikacja]
    HN[petecooper — Tell HN]
    WT[watchTowr]
    Beaumont[Kevin Beaumont]
    Firsov[Kirill Firsov — wideo]
  end
  subgraph Defenders[Obrońcy]
    CERT[CERT-EU / BSI / NCSC / CERT.at / CERT.pl / CERT-FR]
    CF[Cloudflare WAF]
    Host[Hosty / CMS / dystrybucje]
  end
  Wiz --> PHPTeam
  Calif --> PHPTeam
  OAI --> PHPTeam
  PHPTeam --> Defenders
  HN --> Amplify
  Amplify --> Defenders
  Amplify --> PHPTeam
```

### 8.1 Agencje

- **CERT-EU 2026-018** — Patch ASAP lub izolacja; „all from PHP 5”; CVSS→unauth RCE [P][^certeu]
- **BSI** — BITS-H Orange/3 + prasa Caspers: „großflächige Ausnutzung innerhalb weniger Stunden”; AI przyspiesza reverse [P][^bsipdf][^bsipresse]
- **CERT-Bund** — WID-SEC-2026-4055 (treść za logowaniem — nieodczytana tu) [P/?]
- **NCSC UK** — Identify PHP; patch; hardening; rozważyć offline; inventory bundled PHP [P][^ncscuk]
- **NCSC-NL** — Komunikat; ncsc.nl offline; repo NCSC-NL/php2shell (lista produktów); brak aktywnego misbruik [P][^ncscnl]
- **CERT.at** — Update #1: exploit w sieci, funkcjonalność niepotwierdzona [P][^certat]
- **CERT Polska 195/2026** — Inventory; rozważyć wyłączenie usług PHP z Internetu [P][^certpl]
- **CERT-FR ALE-014** — Obejścia upload_progress/multipart **niekwalifikowane** [P][^certfr]
- **ACSC (ASD, Australia) / IPA (Japonia)** — alerty przed wydaniem łatki (21.10): zinwentaryzować PHP i przygotować aktualizację; ACSC w chwili publikacji nie wiedziało o eksploatacji [P][^acsc][^ipa]
- **CISA** — Brak KEV na PHP2Shell w momencie researchu [P][^kev]

### 8.2 WAF, hosty, CMS

- **Cloudflare:** Emergency Managed Ruleset — 7 reguł „Anomalous Execution”; dostępne także Free; Knecht: stopgap only [P][^cfwaf][^knecht].
- **CloudLinux Imunify360:** zestaw reguł WAF 8.83 blokuje krążący wzorzec żądań na ModSecurity/Coraza (na LiteSpeed tylko logowanie); producent nazywa to wirtualną łatką, nie poprawką [P][^imunify]. **bunny.net:** zarządzane reguły WAF Bunny Shield, blokujące tylko w trybie blokowania; rozwiązanie doraźne — trzeba załatać PHP [P][^bunny].
- **Sansec (Magento):** mass attacks w 15 min (wg SecurityWeek); aktualizacja na poziomie infrastruktury, nie sklepu [D][^secweek][^sansec].
- **Wordfence / shared WP:** fix nie idzie auto-updatem WordPressa — zależy od hosta [D][^verge].

### 8.3 Holenderska (i sąsiednia) fala wyłączeń

NOS/NU i komunikat NCSC-NL dokumentują profilaktyczne offline m.in.: DigiD.nl (strona; logowanie DigiD w innych systemach częściowo działało), MijnOverheid, Tweede Kamer, RIVM, ANWB, RTL, szpitale, SURF, partie, UWV (wybrane aplikacje), NCSC.nl, NotuBiz, KNVB, dobre cele (KWF, Amnesty…) [P][^nos][^nu][^bbc][^ncscnl]. Belgia: flamandzkie strony rządowe (Diependaele); Francja: prefektury; Finlandia: strony rządowe [P][^nos].

**Analiza komunikacji [A]:** to klasyczny trade-off *availability vs confidentiality/integrity*. Przy CVSS 9.2, braku pewnego workaroundu i publicznej PoC-narracji agencje wybrały „lepiej ciemna strona niż przejęty serwer”. Koszt: utrata usług publicznych w dzień roboczy. Precedent Log4Shell też widział radykalne izolacje, ale rzadko tak skoordynowane wyłączenia krajowych IDP/portali w godzinach przed patchem.

---

## 9. Ekspozycja i skutki

### 9.1 Co wiemy

- **W3Techs 21.10.2026:** 69,3% / wersje 8·7·5 jak wyżej [P][^w3t].
- **Modat 20.10:** 4 384 302 usług / 1 886 612 hostów; **79%** usług ze znaną wersją na EOL (4/5/7/8.0/8.1); największa grupa **7.4** (878 761); USA/Chiny/Japonia/Niemcy na czele hostów [D][^modat].
- **Mallory/THN:** ~884 tys. hostów z banerem PHP ≤8.1 — banery, nie potwierdzona podatność [D][^thn].
- **Tenable/Cutler/Poley:** szacunki 1,3–1,9 mln hostów [D][^tenable].

### 9.2 Czego nie wiemy

- Ile hostów faktycznie podatnych *i* osiągalnych ścieżką RCE (SAPI, konfiguracja, WAF).
- Ile zostało skompromitowanych przed lub tuż po patchu.
- Kiedy paczki LTS dotrą do Remi / Docker Hub / shared hosting.
- Czy CISA wpisze KEV i jakie IoC opublikują vendorzy.

---

## 10. Porównanie historyczne

- **Log4Shell** (CVE-2021-44228), XII 2021 [P][^cflog4][^cplog4]
  - *Podobieństwa:* Masowa ekspozycja „niewidzialnej” zależności; WAF stopgap; nazwa-mem
  - *Tempo / różnice:* Cloudflare: testy 8 dni przed disclosure; exploity **9 min** po; Check Point: **>800k** ataków / 72 h
- **Heartbleed**, IV 2014 [P][^heartbleed]
  - *Podobieństwa:* Krytyczny bug w fundamencie; early notify wybranych
  - *Tempo / różnice:* Google/Cloudflare wiedzieli przed public; CRA CA: ~900 SIN
- **PHP-CGI CVE-2024-4577**, VI 2024 [P][^akamai4577][^imperva4577]
  - *Podobieństwa:* RCE w PHP; szybka broń
  - *Tempo / różnice:* Akamai: eksploatacja **w 24 h**; Imperva: TellYouThePass **<48 h**
- **OpenSSL 3.0.7 pre-announce**, X–XI 2022 [P][^openssl307]
  - *Podobieństwa:* Publiczna zapowiedź CRITICAL przed detalami
  - *Tempo / różnice:* Po prenotyfikacji **obniżono** do HIGH

**Wzorzec 24–72 h [A]:** po publicznym patchu spodziewać się (1) masowego skanowania, (2) PoC w godzinach, (3) ransomware/botów w 1–2 doby jeśli RCE jest wiarygodne. Przy AI BSI i Sansec zakładają **godziny**, nie dni [P/D][^bsipresse][^sansec].

---

## 11. Wnioski

### Dla developerów aplikacji
Nie zakładajcie, że „bezpieczny kod aplikacji” chroni przed luką w runtime. Testujcie na wspieranych PHP; unikajcie polegania na rzadko używanych feature’ach pre-init (upload progress) bez potrzeby [A][^phpadv].

### Dla ops / SRE
Inventory PHP **włącznie z bundled** (appliances, panele, kontenery). Patch window ≠ komunikat prasowy — weryfikujcie `php -v` / pakiet na każdym hoście. Plan B: izolacja internet-facing przy braku patcha [P][^ncscuk][^certeu].

### Dla maintainerów OSS
Duże poprawki memory-safety potrzebują czasu i prenotyfikacji dystrybucji; jednocześnie wyciek embarga jest realnym scenariuszem — miejcie plan „release earlier” (PHP go miał i użył) [P][^announce].

### Dla rządów / CERT
Profilaktyczne wyłączenia działają jako hamulec, ale kosztują zaufanie do usług publicznych. Listy zależności (NCSC-NL/php2shell) wzorem Log4Shell są wartościowe [P][^ncscnl].

### Dla mediów
Rozróżniajcie: oficjalne CVSS 9.2 vs plotki o 10.0; „early attacks” od CDN vs „brak misbruik” od CERT; nazwa społecznościowa vs komunikat vendora. Nie linkujcie niezweryfikowanych PoC jako „exploit” [A].

---

## 12. Pytania otwarte i co zaktualizuje ten dokument

1. Paczki Ubuntu/Debian/RHEL/Remi/Docker Hub — kiedy „Needs evaluation” → fixed.
2. CISA KEV / EPSS / niezależne IoC.
3. Rozstrzygnięcie Knecht vs NCSC-NL/BSI co do ITW.
4. Oficjalne write-upy Calif / OpenAI (Wiz zapowiedział ich blogi) [D][^wiz].
5. Los hostów EOL (5.x–8.1) bez backportu.
6. Warianty — Wiz: „other tracked and likely untracked variants” [D][^wiz].
7. Powrót stron NL/BE/FR/FI.
8. CMS/appliance firmware (Nextcloud, pfSense, cPanel…) [D][^heise].
9. Ewolucja bypassów WAF.
10. Hunting kompromisów wstecz — nadal nie wiadomo, jak daleko wstecz szukać.

---

## Aneks A: Pełna oś czasu

*Czas UTC; w nawiasie czas warszawski (CEST).*

- **2026-05-01** — Calif: „MAD Bugs” (osobny UAF) [P]
- **2026-08-19…24** — Wiz: discover → RCE Drupal/WP → report [D]
- **2026-09-21** — PHP zaczyna skoordynowaną poprawkę [D]
- **2026-10-14** — Blog PHP Foundation (Daybreak Red) [P]
- **2026-10-18 15:46** (17:46) — Commit bailout fix [P]
- **2026-10-19 07:30–17:04** (09:30–19:04) — Annotated tagi wydań [P]
- **2026-10-20 15:20** (17:20) — Tell HN — wyciek CVE [P]
- **2026-10-20 16:39** (18:39) — Beaumont [P]
- **2026-10-20 18:26** (20:26) — watchTowr — embargo Thursday 11am ET [P]
- **2026-10-20 19:33** (21:33) — PHP ANNOUNCE — Wed 14:00 UTC [P]
- **2026-10-20 19:35** (21:35) — watchTowr FAQ [P]
- **2026-10-20 20:27** (22:27) — Wideo php2shell [P]
- **2026-10-20 20:33** (strefa na stronie niejednoznaczna) — CERT-EU 2026-018 [P/?]
- **2026-10-20 21:20** (23:20) — CERT.at ostrzeżenie [P]
- **2026-10-21 02:13** (04:13) — Girgias: only mitigation is patching [P]
- **2026-10-21 07:43** (09:43) — Knecht: early attacks + WAF [P]
- **2026-10-21 rano–południe** — Masowe offline NL/BE/FR/FI [P]
- **2026-10-21 11:59** (13:59) — NCSC-NL komunikat [P]
- **2026-10-21 13:33:59** (15:33:59) — Last-Modified tarballa 8.5.12 [P]
- **2026-10-21 13:34** (15:34) — Publikacja obu GHSA [P]
- **2026-10-21 ~13:35** (~15:35) — php.net advisory [P]
- **2026-10-21 13:43** (15:43) — Blog Wiz [P]
- **2026-10-21 13:44** (15:44) — Docker PR #1694 [P]

---

## Aneks B: Słowniczek

| Termin | Znaczenie |
|---|---|
| **SAPI** | Server API — warstwa między serwerem WWW a silnikiem PHP |
| **Worker** | Proces PHP obsługujący wiele żądań kolejno |
| **OOM** | Out of memory — wyczerpanie limitu pamięci |
| **Bailout / longjmp** | Awaryjne wyjście z kontekstu C bez normalnego stack unwinding |
| **Use-after-free (UAF)** | Użycie pamięci po zwolnieniu |
| **Stale pointer / global** | Wskaźnik/global wskazujący na nieaktualną pamięć żądania |
| **mod_php** | PHP jako moduł Apache |
| **PHP-FPM** | FastCGI Process Manager |
| **CVSS v4.0** | Common Vulnerability Scoring System, wersja 4 |
| **Embargo** | Okres poufności przed publicznym disclosure |
| **KEV** | CISA Known Exploited Vulnerabilities catalog |
| **EOL** | End of life — brak oficjalnych update’ów |

---

## Aneks C: Lista kontrolna dla obrońców

*Jak sprawdzić, że jesteście załatani — nie jak atakować.*

1. **Zidentyfikujcie PHP:** `php -v` na hostach; obrazy Docker; panele; appliances; Windows `php.exe` / `php-cgi.exe` [D][^huntress].
2. **Docelowe wersje:** ≥ 8.5.12 / 8.4.27 / 8.3.36 / 8.2.35; dla EOL — vendor LTS lub upgrade [P][^phpadv].
3. **Po update:** restart **wszystkich** workerów (FPM reload/restart, Apache graceful/restart); sprawdźcie wersję w faktycznym SAPI, nie tylko CLI.
4. **Kontenery:** po pojawieniu się tagów na Docker Hub — `pull` + redeploy; PR #1694 to dopiero początek łańcucha [P][^docker].
5. **Remi:** nie czekajcie na dzisiejszy update Remi — dystrybucja lub build ze źródeł [P][^phpfremi].
6. **Tymczasowo (nie zamiast patcha):** środki z advisories; WAF vendorów jako stopgap [P][^phpadv][^cfwaf].
7. **Hunting po fakcie:** nietypowe child processy PHP (shell, curl, wget); webshelle; nowe pliki w docroot; worker churn; nietypowe multipart + 500 [D][^huntress][^wiz].
8. **EOL wystawione do Internetu:** upgrade, VPN, lub offline [P][^ncscuk][^certeu].

---

## Aneks D: Źródła

### Pierwotne
[^phpadv]: https://www.php.net/index.php#2026-10-21-5
[^phppre]: https://www.php.net/archive/2026.php#2026-10-20-1
[^ghsa618]: https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w
[^ghsa619]: https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp
[^commit]: https://github.com/php/php-src/commit/31c0ea7d7ff1d1fccb6492e52dab544011628065
[^announce]: https://discourse.thephp.foundation/t/announce-upcoming-critical-php-security-release/6251
[^phpfound]: https://thephp.foundation/blog/2026/10/14/how-the-php-security-team-handles-your-reports/
[^audit2024]: https://thephp.foundation/blog/2025/04/10/php-core-security-audit-results/
[^tarball]: https://www.php.net/distributions/php-8.5.12.tar.xz (nagłówek Last-Modified)
[^atom]: https://www.php.net/releases/feed.php
[^tags]: https://api.github.com/repos/php/php-src/git/tags/c96586077b050b362744ba295f97f6395f58a75a (annotated tag php-8.5.12, data tagger 2026-10-19; tagi 8.4.27/8.3.36/8.2.35: https://github.com/php/php-src/tags)
[^girgias]: https://phpc.social/@Girgias/117476477429221001

### Odkrycie / research
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

### Agencje i media
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

### Historyczne
[^cflog4]: https://blog.cloudflare.com/exploitation-of-cve-2021-44228-before-public-disclosure-and-evolution-of-waf-evasion-patterns/
[^cplog4]: https://blog.checkpoint.com/security/the-numbers-behind-a-cyber-pandemic-detailed-dive/
[^akamai4577]: https://www.akamai.com/blog/security-research/2024-php-exploit-cve-one-day-after-disclosure
[^imperva4577]: https://www.imperva.com/blog/update-cve-2024-4577-quickly-weaponized-to-distribute-tellyouthepass-ransomware/
[^heartbleed]: https://www.smh.com.au/technology/heartbleed-disclosure-timeline-who-knew-what-and-when-20140414-zqurk.html
[^openssl307]: https://openssl-library.org/post/2022-11-01-email-address-overflows/

---

*Koniec wersji 1.0 (PL). Dokument do aktualizacji wraz z paczkami dystrybucyjnymi, IoC i write-upami Calif/OpenAI.*
