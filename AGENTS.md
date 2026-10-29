> **Przygotowane przez Jan Koneiczny.**

# AGENTS.md — AmicaIN / SmartIN / SMART2

Ten projekt dotyczy aplikacji **AmicaIN** (`amica.com`) i piekarnika z platformą **SmartIN / SMART2**. Nie utożsamiaj jej z aplikacją Amica Home (Tuya). Zacznij od tego pliku i [README.md](README.md); dobieraj dalsze dokumenty do zadania.

Wskazówki dla agenta w tym pliku mają pierwszeństwo przed starszymi instrukcjami w README i dokumentacji diagnostycznej.

## Praca dla osoby nietechnicznej

- Użytkownik nie musi znać adresu IP, podsieci, portów, identyfikatora sesji ani zasad działania routera. **Samodzielnie zbieraj dostępne dane i rozwiązuj problemy.** Nie rozpoczynaj od listy pytań technicznych.
- Gdy użytkownik chce połączyć się z piekarnikiem, potraktuj to jako zadanie do wykonania. Sprawdź istniejące wyniki, stan sieci komputera i możliwe sposoby wykrycia urządzenia; kontynuuj diagnostykę, dopóki możesz zrobić coś użytecznego.
- Zadaj pytanie dopiero, gdy niezbędnej informacji nie da się rozsądnie ustalić samodzielnie lub potrzebne jest fizyczne działanie użytkownika. Wyjaśnij krótko, dlaczego jest ono konieczne, i podaj jedną prostą instrukcję krok po kroku. Nie proś o hasło Wi‑Fi, dane logowania ani identyfikator sesji, jeśli istnieje inna droga.
- Pisz prostym językiem: powiedz, co udało się ustalić, co robisz dalej i jaki jest efekt. Terminy techniczne wyjaśniaj tylko wtedy, gdy pomagają użytkownikowi podjąć działanie. Nie przedstawiaj przypuszczenia jako potwierdzonego faktu.
- Stosuj już przekazane informacje. Jeśli użytkownik potwierdził, że piekarnik działa w AmicaIN, nie każ mu ponownie parować urządzenia bez ustalonej przyczyny.

## Łączenie z piekarnikiem

1. Przeczytaj [PROBE-LAN-RUNTIME.md](PROBE-LAN-RUNTIME.md), [KOMUNIKACJA-PIEKARNIK.md](KOMUNIKACJA-PIEKARNIK.md) i istniejące wyniki w `probes/`. Traktuj ich opis protokołu jako hipotezy wymagające potwierdzenia na urządzeniu.
2. Sam sprawdź aktywny interfejs, adres komputera i rzeczywistą maskę sieci. Użyj dostępnych lokalnych danych o urządzeniach i istniejących narzędzi, aby ustalić prawdopodobnego kandydata. Brak nazwy urządzenia lub otwartego portu nie dowodzi, że piekarnika nie ma w sieci; nie przypisuj adresu bez wiarygodnego potwierdzenia.
3. W razie potrzeby wykorzystaj discovery opisane w projekcie. Sprawdź faktyczny adres rozgłoszeniowy: obecny skrypt `tools/probe-smartin-lan.py` zakłada `/24`, co może nie pasować do sieci użytkownika. Znany adres urządzenia pozwala wskazać cel bez tego założenia. Wybierz ograniczoną diagnostykę potrzebną do odnalezienia własnego piekarnika.
4. Jeśli potrzebny jest identyfikator sesji, najpierw sprawdź dostępne w projekcie dane i inne możliwe sposoby nawiązania łączności. Nie zakładaj, że identyfikator zastępczy zapewni prawidłowe parowanie. Nie zapisuj sekretów w logach ani nie ujawniaj ich w odpowiedzi.
5. Opieraj kolejne kroki na faktycznych wynikach. Samo działanie aplikacji na telefonie nie potwierdza, że komputer ma dostęp do piekarnika przez LAN. Udane znalezienie urządzenia nie oznacza jeszcze poprawnego sterowania.
6. Zapisuj przydatne wyniki w `probes/{data}__lan-attempt/` oraz ustalenia w dokumentacji projektu, gdy zadanie obejmuje taką pracę. Wyjaśnij wyniki i konkretny punkt wznowienia. Gdy dostęp techniczny lub uprawnienia uniemożliwiają działanie, nazwij konkretną blokadę i zastosuj dostępne rozwiązanie zastępcze.

Tylko własny sprzęt; bez fuzzingu relay i bez obcych firmware z forów. Nie wysyłaj poleceń zmieniających ustawienia, uruchamiających grzanie ani aktualizujących firmware bez wyraźnego zlecenia użytkownika.

## Mapa projektu

| Miejsce | Zawartość |
|---------|-----------|
| [README.md](README.md) | Przegląd projektu i plików |
| [PROBE-LAN-RUNTIME.md](PROBE-LAN-RUNTIME.md) | Próba komunikacji w sieci lokalnej |
| [KOMUNIKACJA-PIEKARNIK.md](KOMUNIKACJA-PIEKARNIK.md) | Ustalenia o komunikacji i protokołach |
| [SMARTIN-SMART2-gleboko.md](SMARTIN-SMART2-gleboko.md) | Pogłębiona analiza platformy |
| [AmicaIN-SmartIN-ustalenia.pdf](AmicaIN-SmartIN-ustalenia.pdf) | Raport z dotychczasowych ustaleń |
| [docs/08-dekompilacja-checklist.md](docs/08-dekompilacja-checklist.md) | Wskazówki do analizy APK |
| `APK/downloaded/` | Pobrany pakiet aplikacji |
| `apk-decompile-work/` | Roboczy wynik dekompilacji |
| `apk-static/` | Wyniki analizy statycznej APK |
| `assets-extract/` | Wyodrębnione zasoby aplikacji |
| `probes/` | Wyniki diagnostyki urządzenia |
| `tools/` | Skrypty pomocnicze, w tym `probe-smartin-lan.py` |

Analizę APK, zasobów i raportów wykonuj, gdy pomaga w konkretnym zadaniu. Dostępność narzędzi i istniejących artefaktów sprawdzaj przed przyjęciem założenia, że trzeba coś pobrać lub odtworzyć. Zapisuj rezultaty w odpowiednich katalogach projektu, a nie w osobnym dokumencie poza nim.
