> **Prepared by Jan Konieczny.**

# SmartIN / SMART2 (MKSoft + Geryco) - deep analysis

Supplement [OVEN-COMMUNICATION.md](OVEN-COMMUNICATION.md). Sources: reverse AmicaIN 1.0.50 + public documentation + forums.

---

## 1. Who is behind it (ecosystem map)

|Subject|Role|
|---------|------|
|**Amica S.A.**|Household appliances manufacturer, brand, service, newer**Amica Home**/**Amica Smart** (Tuya)|
|**Geryco sp. z o. o.** (Kraków / historically also UK GERYCO LTD)|"Smart" technical support, portal [geryco.pl/Home/Smart](https://geryco.pl/Home/Smart), HTTPS hosts in apk (`geryco.pl`, `g4help.com/pl`)|
|**MKSoft** (`com.mksoft.smart2` in APK)|**SMART2** platform - application engine, TCP/UDP protocol, `.cm2` format, `AMICASMART` backend|
|**SmartIN**|The oven **Wi-Fi access point name** (SSID) and product line; in the code: `SMARTIN.ANDROID.LAN.*`, packages `amica.com`, `smartin.com`, `com.mksoft.smartin`|
|**White-label**|Same engine: **Hansa**(`HANSA.ANDROID.LAN.`), generic**SMART2.ANDROID.LAN.**|

**Important:** Internet searches for "SMART2" often lead to a **TV dongle or Linux package manager**, not an Amica oven. Search: `mksoft smart2`, `SmartIN`, `geryco`, `AMICASMART`.

---

## 2. Three different "generations" of Amica oven software

Don't get confused - this is **three stacks**:

|Line|Equipment|App|MCU/panel update|
|-------|--------|-----------|---------------------------|
|**Amica .IN + SmartIN WiFi**|RJ45 + WiFi module, display**Tiw**|**AmicaIN**(`amica.com`) - SMART2|MKSoft server → telephone → TCP/USB `#AMICA#`; old PC program**Amica.IN.USB_DataTransfer** (Geryco)|
|**Amica Integra**|LCD, often**SD card** in the programmer|Integra/USB_DataTransfer|**IMG/clone SD**, service pendrive; soft**PGxxx / MGxxx** (Electrode)|
|**Amica .Home / X-Type WiFi**|Knob + WiFi, display**Tc**|**Amica Home**(`amicahome.com`)|**OTA**from the cloud (screen**OtA**), regulations: platform**Tuya IoT**-**different protocol than SMART2**|

AmicaIN **≠** Amica Home. SMART2 reverse engineering does **not** describe Tuya.

**Amica Home** Official Pairing Guide: [Android Tc](https://www.amica.pl/media/wysiwyg/programatory/tc/android_manual.pdf) Pairing PDF.

---

## 3. How to operate it (SmartIN / SMART2) - practice

### 3.1 Oven Side (Geryco + APK)

Source: [Geryco Amica](https://geryco.com.pl/Amica), [geryco.pl Smart](https://geryco.pl/Home/Smart).

1. In the oven WiFi menu: **AP=1**,**M=1**,**S=1** (WiFi enabled, remote control allowed).
2. **WI** mode (communication frame + OK): the **first** app connection registers the **app ID** in the oven "firewall".
3. Home router (LAN/WAN): **2.4 GHz**, WPA2-PSK (TKIP/AES), ports**7770, 7773, 7763**open (TCP; in the apk it dominates locally**7776/7777** - see reverse).
4. AP **SmartIN**: the phone connects directly to the oven AP (like a "remote control").

### 3.2 On the AmicaIN application side (reverse)

|Step|Action|
|------|-----------|
|Installation|`InstallActivity` unpacks `DATA.zip` / `USER.zip` → working directory|
|Bootstrap WAN|`FORMALNE` + `GET_TEXT` → XML config (`t3.h` → ports, URLs)|
|Remote account|`ClientActivity` + `LOGUJ` / `LOGUJ2` (requires previous LAN session according to messages in the apk)|
|Discovery|UDP `#SMT_AMC#` / `#PAE_AMC#` → TCP **7776**|
|Control|JSON `n3.c` (temperatures, functions) + cyclic `q3.d.r()` (~76 B status)|
|Recipes/photos|Transfer `DZ…` + `<cm2>` + chunks **992 B** or USB `#AMICA#/DISO/`|
|Oven firmware|List from server (`t3.j`, `is_to_update`) → HTTPS download → TCP/USB upload (see COMMUNICATION §5)|

### 3.3 Windows (legacy, Geryco)

**Amica.IN.USB_DataTransfer** (Win10+) - recipes, albums, pendrive; does **not** replace full flashing of PG/MG Integra. Description on the Geryco website; users report that**Amica no longer supports** the old file update ecosystem ([Elektroda EB9333BA+ IN, 2024](https://www.elektroda.pl/rtvforum/topic4057250.html)).

### 3.4 New OTA ovens (Amica Home / Tuya)

OTA marketing: over WiFi, message **OtA**, WiFi icon flashing ([Icecat / Amica materials](https://objects.icecat.biz/objects/mmo_120046661_1749168948_653_541992.pdf)).**No reverse engineering of Tuya**: integration via the manufacturer's application, not via the 7770 SMART2 port.

---

## 4. SMART2 protocol - technical abbreviation (for integration)

|Element|Value|
|---------|---------|
|AmicaIN customer ID| `SMARTIN.ANDROID.LAN.{wersja}` |
|TCP device|**7776** (default)|
|UDP| **7777** |
|HTTPS relay|`{geryco\|g4help}:7770/AMICASMART` POST `/@{timestamp}`|
|Payload WAN|Base64 + `o3.h` (XOR-like), no cert pinning|
|Upload|`.cm2` + `.dat`, magic UDP/TCP `#*_AMC#`|
|Oven status|**Not** a full flash dump: SOFT/HARD version and a short status|

Potential integration (Home Assistant etc.): **LAN only**, reverse-engineering `q3.d` and packet capture; **no official API**; WAN requires an MKSoft account and relay.

---

## 5. Custom Firmware/Community - Verdict

### 5.1 SmartIN / SMART2 / AmicaIN (WiFi MKSoft)

|Question|Answer|
|---------|-----------|
|Does anyone publish **custom** firmware for the SmartIN module?|**Not Found** - No repositories, exploits, SMART2 WiFi Oven "root".|
|GitHub `mksoft` / `smart2`|**Unrelated** to Amica (e.g. [mksoft-ltd](https://github.com/mksoft-ltd) - mobile applications; [ubinux/smart2](https://github.com/ubinux/smart2/) - package manager Linux).|
|DIY smart oven|Projects like [SmartOven MQTT](https://github.com/banana-breads/SmartOven) use a **custom oven and ESP32**, not Amica SmartIN.|

**Conclusion:** No community custom firmware for the MKSoft stack was found. Replacing an official `.cm2` package or server response is a theoretical modification, still involving manufacturer software and a high risk of bricking the device.

### 5.2 Amica Integra / IN - soft **PG/MG** (programmer, SD, service pendrive)

This is **another layer**(panel/controller, e.g.**PG351**,**MG351**,**PG353**):

- [Elektroda](https://poszukaj.elektroda.pl/szukaj,amica-piekarnik-oprogramowanie.html): **users share official images**`.IMG` / `.7z` to recover from**SD Card Error**mode**Serwis**, pendrive -**service recoveries**, not "custom ROM".
- Example of sharing a batch: [EBI81064WAA PG351.05](https://www.elektroda.pl/rtvforum/topic4066841.html) (file from a forum member).
- **EB9333BA+ IN**: USB instructions exist, but **Amica no longer provides the software** or supports the update program ([topic4057250](https://www.elektroda.pl/rtvforum/topic4057250.html)).

No homebrew **custom firmware** was found, only factory images, clones, and service recovery material. Flashing an unmatched PG/MG image risks damaging the device.

### 5.3 Amica Smart / Home (Tuya)

Terms and conditions: application for **Tuya IoT**([PDF agreement](https://amica-group.de/media/wysiwyg/AmicaSmart/PL_-_Amica_Smart_-_Regulamin_oraz_umowa_u_ytkownika_-_final.pdf)). Custom = Tuya ecosystem (other devices), **not** a documented Amica OTA hack. **Factory OTA** comes from Tuya/Amica servers.

---

## 6. Application firewall on the oven

Geryco states that the first connection in **WI** mode adds the **application identifier** to the oven whitelist. In the APK, session **`k3.a.u()`** (id.bin), the hash in `LOGUJ`, and `MEILING_*` fields with MAC/target indicate that **the phone is not a generic TCP client** without prior registration or known session secrets.

Implication: a **custom LAN script** must reproduce discovery and the handshake, or use an ID from a legitimately paired phone, only for the operator's **own** device.

---

## 7. Open directions (legal, own equipment)

1. **Capture LAN** (tcpdump on the router) during: discovery, heating on, firmware update - `q3.d.w(…, i7, …)` opcode mapping.
2. Comparison of **Amica Home**APK (Tuya) vs**AmicaIN** - do the new models use SMART2 at all.
3. Finding the current URL **Amica.IN.USB_DataTransfer** on Geryco (links often without a direct href in HTML - just a description).
4. **Home Assistant**: wrapper only after stable LAN status reading (without WAN login emulation).

---

## 8. External links (reading order)

1. [Geryco - Smart / Amica IN](https://geryco.pl/Home/Smart) - Ports, WI, M/S/AP, USB_DataTransfer
2. [Geryco Amica (PL)](https://geryco.com.pl/Amica)
3. [Amica Home - Pairing PDF](https://www.amica.pl/media/wysiwyg/programatory/tc/android_manual.pdf)
4. [Elektroda - Amica soft oven (index)](https://poszukaj.elektroda.pl/szukaj,amica-piekarnik-oprogramowanie.html)
5. [Elektroda - not supported EB9333BA+ IN](https://www.elektroda.pl/rtvforum/topic4057250.html)
6. [Amica Smart - Tuya Agreement PDF](https://amica-group.de/media/wysiwyg/AmicaSmart/PL_-_Amica_Smart_-_Regulamin_oraz_umowa_u_ytkownika_-_final.pdf)

---

*Evidence: AmicaIN APK 2026-10-29, public web 2026-10-29. No confirmed SmartIN custom firmware in public sources.*
