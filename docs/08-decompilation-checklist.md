> **Prepared by Jan Konieczny.**

# AmicaIN decompilation - A→Z checklist

**Start:** [`../AGENTS.md`](../AGENTS.md) (the only AGENTS file in the project).

PDF: [`../AmicaIN-SmartIN-Research-Report.pdf`](../AmicaIN-SmartIN-Research-Report.pdf) · LAN: [`../LAN-RUNTIME-INVESTIGATION.md`](../LAN-RUNTIME-INVESTIGATION.md)

AmicaIN (`amica.com`, SMART2) ≠ Amica Home (Tuya).

---

## 1. Identification

|Field|Value (analysis example)|
|------|----------------------------|
|Package| `amica.com` |
|File| `APK/downloaded/amica.com.xapk` |
|Launcher| `com.mksoft.smart2.MainActivity` |
|Customer id| `SMARTIN.ANDROID.LAN.*` |

---

## 2. Commands (from the project root directory)

```bash
mkdir -p APK/downloaded apk-decompile-work
apkeep -a amica.com -d apk-pure APK/downloaded/

WORK="apk-decompile-work/amica.com.xapk.work"
mkdir -p "$WORK"
unzip -q -o APK/downloaded/amica.com.xapk -d "$WORK"
BASE="$WORK/amica.com.apk"

OUT="apk-static/$(date +%F)__amicain"
mkdir -p "$OUT"
tools/analyze.sh "$BASE" | tee "$OUT/analyze-base.log"

jadx -d apk-decompile-work/amica-in-jadx --show-bad-code "$BASE"

AAPT2=$(find "$HOME/Library/Android/sdk/build-tools" -name aapt2 2>/dev/null | sort | tail -1)
"$AAPT2" dump badging "$BASE" > "$OUT/badging.txt"
"$AAPT2" dump permissions "$BASE" > "$OUT/permissions.txt"

UNZIP="apk-decompile-work/amica-in-unzip"
unzip -q -o "$BASE" -d "$UNZIP"
for d in "$UNZIP"/classes*.dex; do strings "$d"; done | sort -u > "$OUT/all_strings_unique.txt"
rg -i 'SMARTIN|AMICASMART|7776|LOGUJ|cm2|#AMICA#' "$OUT/all_strings_unique.txt"

ASSETS_OUT="assets-extract/$(date +%F)"
mkdir -p "$ASSETS_OUT/DATA" "$ASSETS_OUT/USER"
unzip -q -o "$UNZIP/assets/DATA.zip" -d "$ASSETS_OUT/DATA"
unzip -q -o "$UNZIP/assets/USER.zip" -d "$ASSETS_OUT/USER" || true
```

Correct the `tools/analyze.sh` path if you run from the `docs/` subdirectory.

---

## 3. Jadx map

|Class|Role|
|-------|------|
| `u3.f` |Ports, URL, `comm_mode`|
| `q3.a`, `q3.d`, `q3.e` |UDP/TCP|
| `o3.h` |Obfuscation|
| `p3.a`, `p3.b` |HTTPS relay|
| `k3.a` |Session-id|
| `r3.a` |USB `#AMICA#`|
| `t3.j` |Firmware list|

---

## 4. PDF

```bash
npx --yes md-to-pdf AmicaIN-SmartIN-Research-Report.md
```

---

## 5. Protocol (abbreviation)

TCP **7776**, UDP**7777**, relay `geryco.pl:7770/AMICASMART`, upload**992 B** + `.cm2`/`.dat`.

---

## 6. Runtime

[`../LAN-RUNTIME-INVESTIGATION.md`](../LAN-RUNTIME-INVESTIGATION.md) · [`../tools/probe-smartin-lan.py`](../tools/probe-smartin-lan.py)

---

## 7. Ready when

- [ ] jadx + `apk-static/…` + optional `assets-extract/…`
- [ ] SMART2 ≠ Tuya confirmed
