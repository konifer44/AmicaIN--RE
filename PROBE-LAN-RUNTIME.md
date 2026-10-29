> **Przygotowane przez Jan Koneiczny.**

# Piekarnik SmartIN/SMART2 już w sieci — próba komunikacji

**Start agenta:** [`AGENTS.md`](AGENTS.md) · **Protokół:** [`KOMUNIKACJA-PIEKARNIK.md`](KOMUNIKACJA-PIEKARNIK.md) · **Skrypt:** [`tools/probe-smartin-lan.py`](tools/probe-smartin-lan.py)

Nie dotyczy Amica Home (Tuya).

---

## 0. Agent bez sprzętu u siebie

1. Potwierdź: **AmicaIN** (`amica.com`), nie Amica Home.
2. Poproś operatora o podsieć, AP isolation, IP piekarnika.
3. Folder wyniku:

```
probes/{YYYY-MM-DD}__lan-attempt/
├── README.md
├── probe.log
├── operator-notes.md
└── capture/
```

---

## 1. Checklist operatora

| # | Warunek |
|---|---------|
| 1 | Wi‑Fi **2,4 GHz** |
| 2 | **AP=1, M=1, S=1** w menu WiFi piekarnika |
| 3 | Pierwsze połączenie: tryb **WI** |
| 4 | Raz działająca **AmicaIN** (session-id) |
| 5 | Znany **IP** piekarnika |
| 6 | PC: inbound TCP na **7776** dozwolony |

---

## 2. Model (reverse)

1. Klient **nasłuchuje TCP** (domyślnie **7776**).
2. **UDP :7777** broadcast `#SMT_AMC#` + session-id + IP + port (obfuskacja `o3.h.d`, seed 123).
3. Piekarnik **łączy się do klienta**; potem protokół `q3.d`.

---

## 3. Faza A — skan

Z **katalogu głównego projektu**:

```bash
OVEN=192.168.1.50
python3 tools/probe-smartin-lan.py --oven-ip "$OVEN" --scan-only | tee probes/scan.log
```

---

## 4. Faza B — discovery

```bash
SESSION=""
PROBE="probes/$(date +%F)__lan-attempt"
mkdir -p "$PROBE"
python3 tools/probe-smartin-lan.py \
  --oven-ip "$OVEN" \
  --session-id "$SESSION" \
  --listen-port 7776 \
  --udp-port 7777 \
  --repeat 5 \
  --wait 30 \
  2>&1 | tee "$PROBE/probe.log"
```

Sukces minimalny: `inbound_tcp:` w logu.

---

## 5. Session-id

Z jadx `k3.a` pole **G** (Base64 → `t()`), po sparowaniu AmicaIN, lub z pcap przy działającej apce.

---

## 6. Pętla przy fail

1. `probes/…/README.md` — werdykt  
2. Sieć, flagi AP/M/S/WI  
3. jadx + `apk-static/…/all_strings_unique.txt` + `assets-extract/…/smarttxt.xml`  
4. WebSearch: `geryco WI`, `SmartIN 7776`  
5. Popraw `tools/probe-smartin-lan.py`  
6. pcap: apka vs skrypt  
7. Powtórz §4  

| Objaw | Krok |
|-------|------|
| Brak `inbound_tcp` | WI / session-id / isolation |
| Amica Home | Stop — inny stack |

---

## 7. WAN

Tylko własne konto operatora; bez fuzzingu.

---

## 8. Dokumentacja

Dopisz do `KOMUNIKACJA-PIEKARNIK.md` · zaktualizuj PDF wg [`AGENTS.md`](AGENTS.md) §6.
