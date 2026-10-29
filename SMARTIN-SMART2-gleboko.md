> **Przygotowane przez Jan Koneiczny.**

# SmartIN / SMART2 (MKSoft + Geryco) — analiza głęboka

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
