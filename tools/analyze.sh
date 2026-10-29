#!/usr/bin/env bash
#
# Wykrywanie stacku technologicznego aplikacji mobilnej (APK / AAB / XAPK / IPA).
# Użycie:  ./analyze.sh <ścieżka-do-pliku>
#
set -euo pipefail

FILE="${1:-}"
if [[ -z "$FILE" || ! -f "$FILE" ]]; then
  echo "Użycie: $0 <plik .apk|.aab|.xapk|.ipa>"
  echo "Wrzuć plik do katalogu input/ i podaj ścieżkę."
  exit 1
fi

BASE="$(cd "$(dirname "$0")" && pwd)"
WORK="$BASE/../apk-decompile-work/$(basename "$FILE").work"
rm -rf "$WORK"; mkdir -p "$WORK"
EXT="${FILE##*.}"; EXT="$(echo "$EXT" | tr '[:upper:]' '[:lower:]')"

echo "======================================================"
echo " Analiza: $(basename "$FILE")"
echo " Rozmiar: $(du -h "$FILE" | cut -f1)"
echo " Typ:     $EXT"
echo "======================================================"

hit() { echo "  [WYKRYTO] $1"; }

analyze_zip_listing() {
  local listing="$1" platform="$2"
  echo
  echo "--- Sygnały technologiczne ($platform) ---"
  local found=0
  if grep -qiE "flutter_assets/|libflutter\.so|Flutter\.framework|libapp\.so|App\.framework|kernel_blob\.bin" "$listing"; then
    hit "FLUTTER"; found=1
  fi
  if grep -qiE "libreactnative|libhermes|index\.android\.bundle|main\.jsbundle|React\.framework|libjsc\.so" "$listing"; then
    hit "REACT NATIVE"; found=1
  fi
  if grep -qiE "capacitor\.config\.json|public/cordova\.js|assets/www/|/www/index\.html|cordova_plugins\.js" "$listing"; then
    hit "CORDOVA / CAPACITOR / IONIC (WebView hybrid)"; found=1
  fi
  if grep -qiE "\.html$|\.htm$" "$listing" | head -1 >/dev/null 2>&1; then
    local htmlcount; htmlcount=$(grep -icE "\.html$|\.htm$" "$listing" || true)
    if [[ "${htmlcount:-0}" -gt 3 ]]; then hit "WebView (dużo plików HTML: $htmlcount)"; found=1; fi
  fi
  if grep -qiE "libmono|Xamarin|\.dll$|blazor" "$listing"; then
    hit ".NET / XAMARIN / MAUI"; found=1
  fi
  if grep -qiE "kotlin/kotlin\.kotlin_builtins|META-INF/.*kotlin" "$listing"; then
    hit "Kotlin (natywny Android)"; found=1
  fi
  if [[ "$found" -eq 0 ]]; then
    echo "  Brak sygnałów cross-platform -> prawdopodobnie NATYWNA aplikacja."
  fi
}

case "$EXT" in
  apk|aab|xapk|zip)
    echo "Rozpakowuję archiwum..."
    unzip -o -q "$FILE" -d "$WORK" || true
    # XAPK / AAB moga zawierac zagniezdzone APK
    NESTED_APK=$(find "$WORK" -maxdepth 2 -iname "*.apk" | head -1 || true)
    LIST="$WORK/_listing.txt"
    if [[ -n "$NESTED_APK" ]]; then
      echo "Znaleziono zagnieżdżony APK: $(basename "$NESTED_APK")"
      unzip -l "$NESTED_APK" | awk '{print $4}' > "$LIST"
      TARGET_APK="$NESTED_APK"
    else
      unzip -l "$FILE" | awk '{print $4}' > "$LIST"
      TARGET_APK="$FILE"
    fi

    echo
    echo "--- Manifest (aapt2) ---"
    AAPT2=$(find "$HOME/Library/Android/sdk/build-tools" -name aapt2 2>/dev/null | sort | tail -1 || true)
    if [[ -n "$AAPT2" ]]; then
      "$AAPT2" dump badging "$TARGET_APK" 2>/dev/null | grep -iE "^package:|sdkVersion:|targetSdkVersion:|application-label:|uses-permission" | sed 's/^/  /' || true
    else
      echo "  (aapt2 niedostępne — pomijam manifest)"
    fi

    analyze_zip_listing "$LIST" "Android"

    echo
    echo "--- Biblioteki natywne (lib/) ---"
    grep -iE "lib/.*\.so" "$LIST" | sed 's/^/  /' | sort -u | head -40 || echo "  (brak)"
    ;;

  ipa)
    echo "Rozpakowuję IPA..."
    unzip -o -q "$FILE" -d "$WORK" || true
    LIST="$WORK/_listing.txt"
    unzip -l "$FILE" | awk '{print $4}' > "$LIST"
    analyze_zip_listing "$LIST" "iOS"

    APP_DIR=$(find "$WORK/Payload" -maxdepth 1 -iname "*.app" | head -1 || true)
    if [[ -n "$APP_DIR" ]]; then
      echo
      echo "--- Frameworki (.app/Frameworks) ---"
      ls "$APP_DIR/Frameworks" 2>/dev/null | sed 's/^/  /' || echo "  (brak folderu Frameworks)"
      BIN=$(/usr/libexec/PlistBuddy -c "Print :CFBundleExecutable" "$APP_DIR/Info.plist" 2>/dev/null || true)
      if [[ -n "$BIN" && -f "$APP_DIR/$BIN" ]]; then
        echo
        echo "--- otool -L (zlinkowane biblioteki) ---"
        otool -L "$APP_DIR/$BIN" 2>/dev/null | sed 's/^/  /' | head -40 || true
        echo
        echo "--- strings: sygnały frameworków ---"
        strings "$APP_DIR/$BIN" 2>/dev/null | grep -iE "flutter|cordova|capacitor|react-native|hermes|xamarin" | sort -u | head -20 || echo "  (brak)"
      fi
      echo
      echo "--- Min iOS / uprawnienia (Info.plist) ---"
      /usr/libexec/PlistBuddy -c "Print :MinimumOSVersion" "$APP_DIR/Info.plist" 2>/dev/null | sed 's/^/  MinimumOSVersion: /' || true
      plutil -p "$APP_DIR/Info.plist" 2>/dev/null | grep -iE "UsageDescription|WebView" | sed 's/^/  /' || true
    fi
    ;;

  *)
    echo "Nieobsługiwane rozszerzenie: $EXT"
    exit 1
    ;;
esac

echo
echo "======================================================"
echo " Gotowe. Pełne pliki w: $WORK"
echo " Aby zobaczyć kod źródłowy (Android): jadx -d apk-decompile-work/src \"$FILE\""
echo "======================================================"
