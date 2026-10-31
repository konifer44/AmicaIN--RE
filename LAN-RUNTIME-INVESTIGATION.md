> **Prepared by Jan Konieczny.**

# SmartIN/SMART2 oven now online - communication test

**Agent start:**[`AGENTS.md`](AGENTS.md) ·**Protocol:**[`OVEN-COMMUNICATION.md`](OVEN-COMMUNICATION.md) ·**Script:** [`tools/probe-smartin-lan.py`](tools/probe-smartin-lan.py)

Does not apply to Amica Home (Tuya).

---

## 0. Agent without equipment at home

1. Confirm: **AmicaIN** (`amica.com`), not Amica Home.
2. Ask the operator for the subnet, AP isolation, oven IP.
3. Result folder:

```
probes/{YYYY-MM-DD}__lan-attempt/
├── README.md
├── probe.log
├── operator-notes.md
└── capture/
```

---

## 1. Operator checklist

| # |Condition|
|---|---------|
| 1 |Wi-Fi **2.4 GHz**|
| 2 |**AP=1, M=1, S=1** in the oven WiFi menu|
| 3 |First connection: **WI** mode|
| 4 |An existing working **AmicaIN** connection (session ID)|
| 5 |Known oven **IP address**|
| 6 |PC: TCP inbound on **7776** allowed|

---

## 2. Model (reverse)

1. The client **listens for TCP connections**(default**7776**).
2. **UDP :7777** broadcast `#SMT_AMC#` + session-id + IP + port (obfuscation `o3.h.d`, seed 123).
3. The oven **connects to the client**; then the `q3.d` protocol.

---

## 3. Phase A - scan

From the **project root directory**:

```bash
OVEN=192.168.1.50
python3 tools/probe-smartin-lan.py --oven-ip "$OVEN" --scan-only | tee probes/scan.log
```

---

## 4. Phase B - discovery

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

Minimum success: `inbound_tcp:` in the log.

---

## 5. Session-id

From jadx, `k3.a` field **G** (Base64 → `t()`), after pairing AmicaIN, or from a pcap captured while the app is running.

---

## 6. Loop on fail

1. `probes/…/README.md` - Verdict
2. Network, AP/M/S/WI flags
3. jadx + `apk-static/…/all_strings_unique.txt` + `assets-extract/…/smarttxt.xml`
4. WebSearch: `geryco WI`, `SmartIN 7776`
5. Correct `tools/probe-smartin-lan.py`
6. pcap: apk vs script
7. Repeat §4

|Symptom|Step|
|-------|------|
|`inbound_tcp` missing|WI/session-id/isolation|
|Amica Home|Stop - different stack|

---

## 7. WAN

Only your own operator account; no fuzzing.

---

## 8. Documentation

Add to `OVEN-COMMUNICATION.md` · update PDF according to [`AGENTS.md`](AGENTS.md) §6.
