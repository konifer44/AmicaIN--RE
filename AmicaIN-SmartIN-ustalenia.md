---
title: "AmicaIN / SmartIN / SMART2 — ustalenia (pełny raport)"
author: "Jan Koneiczny"
date: "2026-10-29"
lang: pl
---

> **Przygotowane przez Jan Koneiczny.**

# AmicaIN / SmartIN / SMART2 — ustalenia (pełny raport)

**Pakiet:** `amica.com` · **Wersja:** 1.0.50 · **Evidence:** XAPK 2026-10-29, jadx, asset `DATA.zip`.

Ten dokument łączy komunikację z piekarnikiem (reverse APK) oraz analizę ekosystemu Geryco/MKSoft, obsługi i werdyktu custom firmware.

---


**Pakiet:** `amica.com` · **Wersja badging:** 1.0.50 (compile/target SDK 36)  
**Producent stacku:** [MKSoft](https://github.com/search?q=mksoft+smart2) — platforma **SMART2** (white-label: Amica, Hansa, SmartIN).  
**Entry:** `com.mksoft.smart2.MainActivity` · **Identyfikator klienta Amica:** `SMARTIN.ANDROID.LAN.` (ustawiany w `MainActivity`).

> **Uwaga:** folder `FOTO/FIRMWARE` w assetach to **tapety ekranu piekarnika**, nie pliki MCU. Prawdziwe OTA/USB opisane poniżej.

---

## 1. Architektura (warstwy)

```mermaid
flowchart TB
  subgraph ui [UI deklaratywne]
    DATA[DATA.zip smartobj.xml + smarttxt]
    USER[USER.zip przepisy/zdjęcia]
  end
  subgraph core [Rdzeń obfuskowany R8]
    k3[k3.a singleton stan aplikacji]
    o3f[o3.f router LAN/WAN/USB]
  end
  subgraph lan [LAN / AP WiFi piekarnika]
    udp[UDP discovery #SMT_AMC# / #PAE_AMC#]
    tcp[TCP :7776 protokół binarny q3.d]
  end
  subgraph wan [WAN relay]
    https[HTTPS POST /AMICASMART/@timestamp]
    p3[p3.a komendy LOGUJ / SMART2_* / MEILING_*]
  end
  subgraph usb [USB pendrive]
    amica[#AMICA#/DISO/*.cm2 + *.dat]
  end
  ui --> k3
  k3 --> o3f
  o3f -->|LAN| tcp
  o3f -->|WAN| https
  o3f -->|USB| amica
  udp --> tcp
```

| Warstwa | Klasa / plik | Rola |
|---------|----------------|------|
| Stan globalny | `k3.a` | Urządzenia, hasła, wątek TCP `q3.e`, mapa tekstów, `u()` = ID sesji |
| Konfig sieci | `u3.f` | Porty, URL-e HTTP, `comm_mode`, `application_version` |
| Router trybu | `o3.f` | `LAN` → socket; `WAN` → `p3.b` + relay; `USB` → zapis plików |
| TCP transfer | `q3.d` | Odkrywanie piekarnika, stan, **upload plików (firmware/recipe)** w chunkach 992 B |
| UDP broadcast | `q3.a`, `q3.b` | Szukanie urządzeń w LAN / konfiguracja |
| JSON WiFi→oven | `n3.c` | SSID/hasło, pola `M000`, `R001`…, `W001`… (sterowanie) |
| HTTP klient | `p3.a` | POST na 3 hosty, payload Base64 + szyfr `o3.h` |
| USB export | `r3.a` | Katalog `#AMICA#` → `DISO/` |

---

## 2. Tryby łączności (`comm_mode`)

Enum w `o3.f.b`: **`LAN`**, **`WAN`**, **`USB`** (w UI odpowiednikom AP/LAN/WAN z opisu Amica Home — w tej apce starszej nazewnictwo jest w XML `comm_mode`).

| Tryb | Zachowanie (kod) | Użytkownik |
|------|------------------|------------|
| **LAN** | Bezpośredni `Socket` na IP piekarnika, port **7776**; odświeżanie przez `q3.g`/`q3.f` | Ten sam WiFi co piekarnik (lub AP SmartIN) |
| **WAN** | Logowanie `LOGUJ`/`LOGUJ2`, sesja `CZY_AKTYWNA_SESJA`, komendy `MEILING_DEVICE_*` / `SMART2_DEVICE_*` przez HTTPS | Zdalnie przez serwer Amica/MKSoft |
| **USB** | Zapis pakietów `.cm2`/`.dat` na pendrive `#AMICA#` lub lokalnie w trybie USB | Aktualizacja / przenoszenie danych bez TCP |

Domyślna konfiguracja w `u3.f` (nadpisywana po `GET_TEXT`/`FORMALNE` z serwera):

| Parametr | Wartość domyślna |
|----------|------------------|
| `tcp_port` | **7776** |
| `udp_port` | **7777** |
| `http` | `https://geryco.pl:7770/AMICASMART` |
| `http1` | `https://g4help.com:7770/AMICASMART` |
| `http2` | `https://g4help.pl:7770/AMICASMART` |
| `application_version` (AmicaIN) | **`SMARTIN.ANDROID.LAN.`** |
| `http_timeout` / `tcp_timeout` | 1000 ms |
| `refresh_oven` | 1000 ms |

**HTTP:** `POST {base}/@{yyyyMMddHHmmss}` — body = Base64( XOR/hash pipeline z `o3.h` ). **TLS:** `SSLSocketFactory` z **AllowAllHostnameVerifier** (brak pinningu — MITM teoretycznie możliwy przy złym CA).

---

## 3. Odkrywanie urządzenia (UDP)

Na starcie / wizardzie aplikacja wysyła datagramy na **broadcast** (lub `udp_ip` z config):

| Magic | Użycie |
|-------|--------|
| `#SMT_AMC#` | Broadcast „szukam piekarnika” (`q3.a`) |
| `#PAE_AMC#` / `#PAG_AMC#` | Wariant konfiguracji PAE/PAG (`q3.b`, typ `f9951c` / `f9952d`) |

Payload: ID sesji + IP telefonu (15 znaków) + port TCP (6 znaków) + licznik — potem **obfuskacja bajtowa** (`o3.h.d` / `o3.h.g` z seed 123 lub 238).

Odpowiedź piekarnika (TCP cmd `100`, typ `2`) zawiera m.in. bajty **ID / SOFT / HARD / NS** — parsowane w `q3.d.d()` jako stringi typu `SOFT:xx-yy`, `HARD:…`.

---

## 4. Protokół TCP (sterowanie + transfer plików)

Główna logika: **`q3.d.w()`** — wysyłka ramek na utrzymywanym **`q3.c`** (`Socket`).

Cechy (z decompilacji):

- Numer sekwencyjny komunikatu (16-bit LE) — musi zgadzać się z odpowiedzią.
- Payload chunkowany: **max 992 bajty** na ramkę przy uploadzie (`z()`).
- Komendy pomocnicze: m.in. **`185`** (ping/init), **`296`** (status transferu), **`300`** (Multiple Choices — transfer).
- Odpowiedzi deszyfrowane zależnie od typu urządzenia (`o3.h.d` seed z `f9962e`).
- Osobny wątek **`q3.e`** utrzymuje połączenie, obsługuje timeouty, pliki `id.bin` / `refridge_id.bin` w katalogu aplikacji.

### 4.1 Upload do piekarnika (przepisy, albumy, **firmware**)

Wspólny format (`q3.d.y()` / `r3.a.e()`):

1. Plik źródłowy → transform **`o3.b.a()`** (kompresja/obfuskacja).
2. Nagłówek: **`DZ` + 3 pola + długość** + hash `o3.h.c()` na bazie ID sesji `k3.a.u()`.
3. Opakowanie XML-like: **`<cm2>…hash…</cm2><data=…>…</data>`** (WAN używa tagu **`cm2`** w `p3.b.l`).
4. Transfer TCP w chunkach; UI: **`TransferToOverActivity`**.

**USB:** ten sam pakiet zapisywany jako `{id}.cm2` (nagłówek) + `{id}.dat` (payload) w **`/mnt/.../#AMICA#/DISO/`** (`r3.a`).

**Lokalny USB mode (bez pendrive):** `TransferToOverActivity` zapisuje `.cm2` przez `k3.a.J().f()` gdy `comm_mode == USB`.

Pliki pomocnicze w transferach przepisów: **`com.bin`**, **`tmp`**, rozszerzenie **`.mtx`**.

---

## 5. Firmware piekarnika — trzy ścieżki

### A) Aktualizacja przez serwer (WAN + lista wersji)

1. UI: `DATA/.../UPGRADE/`, `MAIN/AREA/UPGRADE`, menu serwisowe (`APP_UPG_*` w `smarttxt.xml`).
2. Metadane wersji z serwera parsowane przez **`t3.j`** → lista **`u3.g`**: `soft_version`, `server_version`, `hard_version`, `soft_size`, **`is_to_update`**, `is_critical`, `device_id`, `folder`, `data` (Base64).
3. Pobranie binariów: przez ten sam stos HTTPS (`p3.a.i` / `h`) — odpowiedź często **Base64** dekodowana do plików lokalnych.
4. Po pobraniu: **TCP upload** (`q3.d.t(u3.h)` iteruje i woła `s()`) **lub** przygotowanie pendrive.

Teksty UX (PL): krok 1 — włóż pendrive do piekarnika i wybierz aktualizację na panelu; krok 2 — pendrive z powrotem w PC; itd. (`UPGRADE/AREA/STEP*`).

### B) Pendrive (offline)

- Struktura: folder **`#AMICA#`** → **`DISO/`** → pary **`NNN.cm2`** + **`NNN.dat`**.
- Zgodne z eksportem `r3.a.g()`.
- Pieczęć licencyjna (`ul_pl.txt`) explicite wymienia **aktualizację oprogramowania programatora urządzenia**.

### C) Aktualizacja **samej aplikacji** AmicaIN (nie MCU piekarnika)

- Długie naciśnięcie kafelka języka → **`POBIERZ_LNG`** → `tmp.zip` → rozpakowanie struktur `DATA` (`LangKafelItm`).
- System **SMART2** w tekstach: backup lokalny, rollback, „aktualizacja struktur lokalnych”.

Wątek w logach/UI: **`TCP_UW`** = „Wątek aktualizacji oprogramowania” — dotyczy **procesu update’u**, nie osobnego protokołu MQTT.

---

## 6. WAN — katalog komend HTTPS (wyekstrahowane stringi)

| Komenda | Cel |
|---------|-----|
| `FORMALNE` | Bootstrap: pobranie XML config (`t3.h` → `u3.f`) |
| `GET_TEXT` | Teksty UI (`smarttxt`) |
| `LOGUJ` / `LOGUJ2` | Rejestracja / logowanie WAN |
| `CZY_AKTYWNA_SESJA` | Walidacja sesji |
| `SMART2_POBIERZ_ID` | ID urządzenia / klienta |
| `SMART2_DEVICE_STATE` / `SMART2_DEVICE_REQUEST` | Stan i żądania w trybie SMART2 |
| `MEILING_DEVICE_STATE` / `MEILING_DEVICE_REQUEST` | Stan/żądania po powiązaniu z `target` (MAC/id piekarnika) |
| `SMART2_POBIERZ_*` | Książka kucharska, pogoda, rozdziały |
| `POBIERZ_LNG` | Paczka językowa / update app |
| `POBIERZ_LISTE_PRZEPISOW` / `POBIERZ_PRZEPIS_CMD` | Przepisy |
| `KOMUNIKAT_LISTA_ROZDZIALOW` | `com.bin` dla cookbook |

Odpowiedzi: XML **`VFP`** z `<ret>OK</ret>` lub `<ret>ERR</ret>`; błąd sieci: **`NETERR`**.

---

## 7. JSON do piekarnika (WiFi provisioning / status)

`n3.c` buduje m.in.:

```json
{"target":"…","from":"…","type":N, … pola Wxxx/Rxxx/Mxxx/Exxx …}
```

oraz `{"SSID":"…","password":"…"}` — konfiguracja WiFi piekarnika (`WiFiSettingActivity` zbiera SSID/hasło).

Pola **`R001`–`R005`**, **`E000`–`E004`**, **`M000`/`M001`** mapują stany piekarnika (temperatury, funkcje grzania — `n3.d`, `n3.e` generują fragmenty JSON).

---

## 8. Uprawnienia Android (implikacje)

Z `badging.txt`:

- `INTERNET`, `ACCESS_WIFI_STATE`, `CHANGE_WIFI_STATE`, `ACCESS_FINE/COARSE_LOCATION` (skan WiFi),
- `LOCAL_MAC_ADDRESS`,
- **`READ/WRITE_EXTERNAL_STORAGE`** (pendrive / pliki `.cm2`),
- **`DELETE_PACKAGES` / `REQUEST_DELETE_PACKAGES`** (legacy / updater? — wymaga audytu runtime).

**Brak** `BLUETOOTH_*` — komunikacja **WiFi + TCP/UDP + HTTPS**, nie BLE.

---

## 9. AmicaIN vs Amica Home

| | **AmicaIN** (`amica.com`) | **Amica Home** (`amicahome.com`) |
|--|---------------------------|----------------------------------|
| Generacja | SMART2 / SmartIN, MKSoft | Nowszy produkt (Play opisuje AP/LAN/WAN/AUTO) |
| Ten dokument | ✅ v1.0.50 | Osobna analiza APK |

---

## 10. Co jeszcze wymaga runtime (nie ze statyki)

- Pełna mapa kodów poleceń TCP (`i7` w `w()`: 100, 185, 296, 300, …).
- Dokładny format pliku po `o3.b.a()` przed wgraniem firmware.
- Zachowanie relay **geryco / g4help** dziś (DNS/SSL cert) — hosty mogą być legacy; app ma **3 fallback URL**.
- Hasła w `USER_CONFIG.zip` (zip encrypted — nie rozpakowany).

---

## 11. Szybkie linki w projekcie

- [KOMUNIKACJA (ten plik)](KOMUNIKACJA-PIEKARNIK.md)
- [badging](apk-static/2026-10-29__amicain/badging.txt)
- [endpointy HTTPS](apk-static/2026-10-29__amicain/endpoints.txt)
- [UPGRADE PL hint krok 1](assets-extract/2026-10-29/DATA/AMICA/PL/UPGRADE/AREA/STEP1/hint.txt)

**Evidence:** AmicaIN XAPK 2026-10-29, jadx → `com.mksoft.smart2`, `k3`/`q3`/`p3`/`u3`/`r3`, asset `DATA.zip` + `strings classes.dex`.

---

# Część II — SmartIN / SMART2 (głęboko)


Uzupełnienie [KOMUNIKACJA-PIEKARNIK.md](KOMUNIKACJA-PIEKARNIK.md). Źródła: reverse AmicaIN 1.0.50 + dokumentacja publiczna + fora.

---

## 1. Kto za tym stoi (mapa ekosystemu)

| Podmiot | Rola |
|---------|------|
| **Amica S.A.** | Producent AGD, marka, serwis, nowsze **Amica Home** / **Amica Smart** (Tuya) |
| **Geryco sp. z o.o.** (Kraków / historycznie też UK GERYCO LTD) | Wsparcie techniczne „Smart”, portal [geryco.pl/Home/Smart](https://geryco.pl/Home/Smart), hosty HTTPS w apk (`geryco.pl`, `g4help.com/pl`) |
| **MKSoft** (`com.mksoft.smart2` w APK) | Platforma **SMART2** — silnik aplikacji, protokół TCP/UDP, format `.cm2`, backend `AMICASMART` |
| **SmartIN** | Nazwa **Wi‑Fi AP piekarnika** (SSID) + linia produktowa; w kodzie: `SMARTIN.ANDROID.LAN.*`, pakiety `amica.com`, `smartin.com`, `com.mksoft.smartin` |
| **White-label** | Ten sam silnik: **Hansa** (`HANSA.ANDROID.LAN.`), generic **SMART2.ANDROID.LAN.** |

**Ważne:** „SMART2” w internecie często trafia na **dongle TV / package manager Linux** — to **nie** piekarnik Amica. Szukaj: `mksoft smart2`, `SmartIN`, `geryco`, `AMICASMART`.

---

## 2. Trzy różne „pokolenia” softu piekarnika Amica

Nie mylić — to **trzy stosy**:

| Linia | Sprzęt | Aplikacja | Aktualizacja MCU / panelu |
|-------|--------|-----------|---------------------------|
| **Amica .IN + SmartIN WiFi** | RJ45 + moduł WiFi, wyśw. **Tiw** | **AmicaIN** (`amica.com`) — SMART2 | Serwer MKSoft → telefon → TCP/USB `#AMICA#`; stary program PC **Amica.IN.USB_DataTransfer** (Geryco) |
| **Amica Integra** | LCD, często **karta SD** w programatorze | Integra / USB_DataTransfer | **IMG/klon SD**, pendrive serwisowy; soft **PGxxx / MGxxx** (Elektroda) |
| **Amica .Home / X-Type WiFi** | Knob + WiFi, wyśw. **Tc** | **Amica Home** (`amicahome.com`) | **OTA** z chmury (ekran **OtA**), regulamin: platforma **Tuya IoT** — **inny protokół niż SMART2** |

AmicaIN **≠** Amica Home. Reverse SMART2 **nie** opisuje Tuya.

Oficjalna instrukcja parowania **Amica Home**: [PDF parowania Android Tc](https://www.amica.pl/media/wysiwyg/programatory/tc/android_manual.pdf).

---

## 3. Jak to obsługiwać (SmartIN / SMART2) — praktyka

### 3.1 Po stronie piekarnika (Geryco + APK)

Źródło: [Geryco Amica](https://geryco.com.pl/Amica), [geryco.pl Smart](https://geryco.pl/Home/Smart).

1. W menu WiFi piekarnika: **AP=1**, **M=1**, **S=1** (WiFi włączone, zdalne sterowanie dozwolone).
2. Tryb **WI** (ramka komunikacyjna + OK) — **pierwsze** połączenie aplikacji rejestruje **ID apk w „firewallu”** piekarnika.
3. Router domowy (LAN/WAN): **2,4 GHz**, WPA2-PSK (TKIP/AES), porty **7770, 7773, 7763** otwarte (TCP; w apk lokalnie dominuje **7776/7777** — patrz reverse).
4. AP **SmartIN**: telefon łączy się bezpośrednio z AP piekarnika (jak „pilot”).

### 3.2 Po stronie aplikacji AmicaIN (reverse)

| Krok | Działanie |
|------|-----------|
| Instalacja | `InstallActivity` rozpakowuje `DATA.zip` / `USER.zip` → katalog roboczy |
| Bootstrap WAN | `FORMALNE` + `GET_TEXT` → XML config (`t3.h` → porty, URL-e) |
| Konto zdalne | `ClientActivity` + `LOGUJ` / `LOGUJ2` (wymaga wcześniejszej sesji LAN wg komunikatów w apk) |
| Discovery | UDP `#SMT_AMC#` / `#PAE_AMC#` → TCP **7776** |
| Sterowanie | JSON `n3.c` (temperatury, funkcje) + cykliczny `q3.d.r()` (~76 B stanu) |
| Przepisy / zdjęcia | Transfer `DZ…` + `<cm2>` + chunki **992 B** lub USB `#AMICA#/DISO/` |
| Firmware piekarnika | Lista z serwera (`t3.j`, `is_to_update`) → pobranie HTTPS → upload TCP/USB (patrz KOMUNIKACJA §5) |

### 3.3 Windows (legacy, Geryco)

**Amica.IN.USB_DataTransfer** (Win10+) — przepisy, albumy, pendrive; **nie** zastępuje pełnego flashowania PG/MG Integra. Opis na portalu Geryco; użytkownicy zgłaszają, że **Amica nie wspiera już** starego ekosystemu aktualizacji plików ([Elektroda EB9333BA+ IN, 2024](https://www.elektroda.pl/rtvforum/topic4057250.html)).

### 3.4 Nowe piekarniki OTA (Amica Home / Tuya)

Marketing OTA: po WiFi, komunikat **OtA**, ikona WiFi miga ([Icecat / materiały Amica](https://objects.icecat.biz/objects/mmo_120046661_1749168948_653_541992.pdf)). **Bez reverse Tuya** — integracja przez aplikację producenta, nie przez port 7770 SMART2.

---

## 4. Protokół SMART2 — skrót techniczny (do integracji)

| Element | Wartość |
|---------|---------|
| Id klienta AmicaIN | `SMARTIN.ANDROID.LAN.{wersja}` |
| TCP device | **7776** (domyślnie) |
| UDP | **7777** |
| HTTPS relay | `{geryco\|g4help}:7770/AMICASMART` POST `/@{timestamp}` |
| Payload WAN | Base64 + `o3.h` (XOR-like), brak cert pinning |
| Upload | `.cm2` + `.dat`, magic UDP/TCP `#*_AMC#` |
| Stan piekarnika | **Nie** pełny dump flash — wersja SOFT/HARD + krótki status |

Potencjalna integracja (Home Assistant itp.): **tylko LAN**, reverse `q3.d` + capture — **brak oficjalnego API**; WAN wymaga konta i relay MKSoft.

---

## 5. Custom firmware / społeczność — werdykt

### 5.1 SmartIN / SMART2 / AmicaIN (WiFi MKSoft)

| Pytanie | Odpowiedź |
|---------|-----------|
| Czy ktoś publikuje **własny** firmware do modułu SmartIN? | **Nie znaleziono** — brak repozytoriów, exploitów, „root” piekarnika WiFi SMART2. |
| GitHub `mksoft` / `smart2` | **Niepowiązane** z Amica (np. [mksoft-ltd](https://github.com/mksoft-ltd) — aplikacje mobilne; [ubinux/smart2](https://github.com/ubinux/smart2/) — package manager Linux). |
| DIY smart oven | Projekty typu [SmartOven MQTT](https://github.com/banana-breads/SmartOven) to **własny piekarnik + ESP32** — zero Amica SmartIN. |

**Wniosek:** społeczność **nie wgrywa custom firmware** do stosu MKSoft; ewentualna modyfikacja to teoretycznie **podmiana oficjalnej paczki** `.cm2`/serwer — nadal soft producenta, wysokie ryzyko brick.

### 5.2 Amica Integra / IN — soft **PG/MG** (programator, SD, pendrive serwis)

To **inna warstwa** (panel/sterownik, np. **PG351**, **MG351**, **PG353**):

- [Elektroda](https://poszukaj.elektroda.pl/szukaj,amica-piekarnik-oprogramowanie.html): użytkownicy **wymieniają oficjalne obrazy** `.IMG` / `.7z` do odzyskania po **SD Card Error**, trybie **Serwis**, pendrive — **recovery serwisowe**, nie „custom ROM”.
- Przykład udostępnienia wsadu: [EBI81064WAA PG351.05](https://www.elektroda.pl/rtvforum/topic4066841.html) (plik od forumowicza).
- **EB9333BA+ IN**: instrukcja pendrive, ale **Amica nie udostępnia już softu** i nie wspiera programu aktualizacji ([topic4057250](https://www.elektroda.pl/rtvforum/topic4057250.html)).

**Custom firmware** w sensie homebrew **nie występuje** — wyłącznie **klony/wsady fabryczne** lub serwis. Wgrywanie cudzego PG/MG **bez dopasowania** = ryzyko uszkodzenia.

### 5.3 Amica Smart / Home (Tuya)

Regulamin: aplikacja na **Tuya IoT** ([PDF umowy](https://amica-group.de/media/wysiwyg/AmicaSmart/PL_-_Amica_Smart_-_Regulamin_oraz_umowa_u_ytkownika_-_final.pdf)). Custom = ekosystem Tuya (inne urządzenia), **nie** dokumentowany hack OTA Amica. OTA **fabryczne** z serwerów Tuya/Amica.

---

## 6. „Firewall” aplikacji na piekarniku

Geryco: pierwsze połączenie w trybie **WI** dodaje **identyfikator aplikacji** do whitelist piekarnika. W apk: sesja **`k3.a.u()`** (id.bin), hash w `LOGUJ`, pola `MEILING_*` z MAC/target — **telefon nie jest generycznym klientem TCP** bez wcześniejszej rejestracji / znanych sekretów sesji.

Implikacja: **własny skrypt LAN** musi odtworzyć discovery + handshake (lub sklonować id z legalnie sparowanego telefonu — etycznie tylko **własne** urządzenie).

---

## 7. Otwarte kierunki (legalne, własny sprzęt)

1. **Capture LAN** (tcpdump na routerze) podczas: discovery, włączenie grzania, update firmware — mapowanie opcode `q3.d.w(…, i7, …)`.
2. Porównanie **Amica Home** APK (Tuya) vs **AmicaIN** — czy nowe modele w ogóle używają SMART2.
3. Odnalezienie aktualnego URL **Amica.IN.USB_DataTransfer** na Geryco (linki często bez bezpośredniego href w HTML — tylko opis).
4. **Home Assistant**: wrapper tylko po stabilnym odczycie stanu LAN (bez emulacji WAN login).

---

## 8. Linki zewnętrzne (kolejność czytania)

1. [Geryco — Smart / Amica IN](https://geryco.pl/Home/Smart) — porty, WI, M/S/AP, USB_DataTransfer  
2. [Geryco Amica (PL)](https://geryco.com.pl/Amica)  
3. [Amica Home — parowanie PDF](https://www.amica.pl/media/wysiwyg/programatory/tc/android_manual.pdf)  
4. [Elektroda — soft piekarnik Amica (indeks)](https://poszukaj.elektroda.pl/szukaj,amica-piekarnik-oprogramowanie.html)  
5. [Elektroda — brak wsparcia EB9333BA+ IN](https://www.elektroda.pl/rtvforum/topic4057250.html)  
6. [Amica Smart — umowa Tuya PDF](https://amica-group.de/media/wysiwyg/AmicaSmart/PL_-_Amica_Smart_-_Regulamin_oraz_umowa_u_ytkownika_-_final.pdf)

---

*Evidence: AmicaIN APK 2026-10-29, public web 2026-10-29. Brak potwierdzonego custom firmware SmartIN w źródłach publicznych.*
