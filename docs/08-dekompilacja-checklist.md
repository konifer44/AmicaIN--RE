> **Przygotowane przez Jan Koneiczny.**

# Dekompilacja AmicaIN — checklista A→Z

**Start:** [`../AGENTS.md`](../AGENTS.md) (jedyny plik AGENTS w projekcie).

PDF: [`../AmicaIN-SmartIN-ustalenia.pdf`](../AmicaIN-SmartIN-ustalenia.pdf) · LAN: [`../PROBE-LAN-RUNTIME.md`](../PROBE-LAN-RUNTIME.md)

AmicaIN (`amica.com`, SMART2) ≠ Amica Home (Tuya).

---

## 1. Identyfikacja

| Pole | Wartość (przykład analizy) |
|------|----------------------------|
| Package | `amica.com` |
| Plik | `APK/downloaded/amica.com.xapk` |
| Launcher | `com.mksoft.smart2.MainActivity` |
| Klient id | `SMARTIN.ANDROID.LAN.*` |

---

## 2. Komendy (z katalogu głównego projektu)

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

Popraw ścieżkę `tools/analyze.sh` jeśli uruchamiasz z podkatalogu `docs/`.

---

## 3. Mapa jadx

| Klasa | Rola |
|-------|------|
| `u3.f` | Porty, URL, `comm_mode` |
| `q3.a`, `q3.d`, `q3.e` | UDP/TCP |
| `o3.h` | Obfuskacja |
| `p3.a`, `p3.b` | HTTPS relay |
| `k3.a` | Session-id |
| `r3.a` | USB `#AMICA#` |
| `t3.j` | Lista firmware |

---

## 4. PDF

```bash
npx --yes md-to-pdf AmicaIN-SmartIN-ustalenia.md
```

---

## 5. Protokół (skrót)

TCP **7776**, UDP **7777**, relay `geryco.pl:7770/AMICASMART`, upload **992 B** + `.cm2`/`.dat`.

---

## 6. Runtime

[`../PROBE-LAN-RUNTIME.md`](../PROBE-LAN-RUNTIME.md) · [`../tools/probe-smartin-lan.py`](../tools/probe-smartin-lan.py)

---

## 7. Gotowe gdy

- [ ] jadx + `apk-static/…` + opcjonalnie `assets-extract/…`
- [ ] SMART2 ≠ Tuya potwierdzone
