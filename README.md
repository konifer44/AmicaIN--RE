> **Przygotowane przez Jan Koneiczny.**

# Amica — SmartIN / AmicaIN / SMART2

## Dla osoby wręczającej projekt agentowi

Powiedz agentowi **dosłownie**:

> Otwórz **folder główny projektu Amica** jako workspace. **Przeczytaj i wykonaj `AGENTS.md`** — najpierw sekcję ⚠️. **Nie** pisz podsumowań do Downloads/RTF. **Uruchom** jadx i zapisuj wyniki w `apk-static/` i `probes/`.

**Jedyny punkt wejścia:** [`AGENTS.md`](AGENTS.md)

| Plik / folder | Opis |
|---------------|------|
| [`AGENTS.md`](AGENTS.md) | **Start + zakazy + bootstrap APK** |
| [`AmicaIN-SmartIN-ustalenia.pdf`](AmicaIN-SmartIN-ustalenia.pdf) | Raport (kontekst) |
| `KOMUNIKACJA-PIEKARNIK.md` · `SMARTIN-SMART2-gleboko.md` | Reverse + ekosystem |
| [`PROBE-LAN-RUNTIME.md`](PROBE-LAN-RUNTIME.md) | Piekarnik w Wi‑Fi |
| [`docs/08-dekompilacja-checklist.md`](docs/08-dekompilacja-checklist.md) | Komendy A→Z |
| `tools/` | `analyze.sh`, `probe-smartin-lan.py` |
| `APK/downloaded/` | XAPK |
| `apk-decompile-work/` | jadx (gitignore) |
| `apk-static/` · `assets-extract/` | Ekstrakty |
| `probes/` | **Tu lądują logi LAN — nie Downloads** |

Scalenie PDF: po edycji części MD → `AmicaIN-SmartIN-ustalenia.md` → `npx md-to-pdf AmicaIN-SmartIN-ustalenia.md` (z katalogu głównego projektu).
