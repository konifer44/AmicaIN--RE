#!/usr/bin/env bash
#
# Detect the technology stack of a mobile application (APK / AAB / XAPK / IPA).
# Usage: ./analyze.sh <path-to-file>
#
set -euo pipefail

FILE="${1:-}"
if [[ -z "$FILE" || ! -f "$FILE" ]]; then
  echo "Usage: $0 <file .apk|.aab|.xapk|.ipa>"
  echo "Place the file in input/ and provide its path."
  exit 1
fi

BASE="$(cd "$(dirname "$0")" && pwd)"
WORK="$BASE/../apk-decompile-work/$(basename "$FILE").work"
rm -rf "$WORK"; mkdir -p "$WORK"
EXT="${FILE##*.}"; EXT="$(echo "$EXT" | tr '[:upper:]' '[:lower:]')"

echo "======================================================"
echo " Analysis: $(basename "$FILE")"
echo " Size: $(du -h "$FILE" | cut -f1)"
echo " Type:     $EXT"
echo "======================================================"

hit() { echo "  [DETECTED] $1"; }

analyze_zip_listing() {
  local listing="$1" platform="$2"
  echo
  echo "--- Technology indicators ($platform) ---"
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
    if [[ "${htmlcount:-0}" -gt 3 ]]; then hit "WebView (many HTML files: $htmlcount)"; found=1; fi
  fi
  if grep -qiE "libmono|Xamarin|\.dll$|blazor" "$listing"; then
    hit ".NET / XAMARIN / MAUI"; found=1
  fi
  if grep -qiE "kotlin/kotlin\.kotlin_builtins|META-INF/.*kotlin" "$listing"; then
    hit "Kotlin (native Android)"; found=1
  fi
  if [[ "$found" -eq 0 ]]; then
    echo "  No cross-platform indicators -> likely a NATIVE application."
  fi
}

case "$EXT" in
  apk|aab|xapk|zip)
    echo "Extracting archive..."
    unzip -o -q "$FILE" -d "$WORK" || true
    # XAPK / AAB may contain nested APKs
    NESTED_APK=$(find "$WORK" -maxdepth 2 -iname "*.apk" | head -1 || true)
    LIST="$WORK/_listing.txt"
    if [[ -n "$NESTED_APK" ]]; then
      echo "Found nested APK: $(basename "$NESTED_APK")"
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
      echo "  (aapt2 unavailable; skipping manifest)"
    fi

    analyze_zip_listing "$LIST" "Android"

    echo
    echo "--- Native libraries (lib/) ---"
    grep -iE "lib/.*\.so" "$LIST" | sed 's/^/  /' | sort -u | head -40 || echo "  (none)"
    ;;

  ipa)
    echo "Extracting IPA..."
    unzip -o -q "$FILE" -d "$WORK" || true
    LIST="$WORK/_listing.txt"
    unzip -l "$FILE" | awk '{print $4}' > "$LIST"
    analyze_zip_listing "$LIST" "iOS"

    APP_DIR=$(find "$WORK/Payload" -maxdepth 1 -iname "*.app" | head -1 || true)
    if [[ -n "$APP_DIR" ]]; then
      echo
      echo "--- Frameworks (.app/Frameworks) ---"
      ls "$APP_DIR/Frameworks" 2>/dev/null | sed 's/^/  /' || echo "  (no Frameworks directory)"
      BIN=$(/usr/libexec/PlistBuddy -c "Print :CFBundleExecutable" "$APP_DIR/Info.plist" 2>/dev/null || true)
      if [[ -n "$BIN" && -f "$APP_DIR/$BIN" ]]; then
        echo
        echo "--- otool -L (linked libraries) ---"
        otool -L "$APP_DIR/$BIN" 2>/dev/null | sed 's/^/  /' | head -40 || true
        echo
        echo "--- strings: framework indicators ---"
        strings "$APP_DIR/$BIN" 2>/dev/null | grep -iE "flutter|cordova|capacitor|react-native|hermes|xamarin" | sort -u | head -20 || echo "  (none)"
      fi
      echo
      echo "--- Minimum iOS / permissions (Info.plist) ---"
      /usr/libexec/PlistBuddy -c "Print :MinimumOSVersion" "$APP_DIR/Info.plist" 2>/dev/null | sed 's/^/  MinimumOSVersion: /' || true
      plutil -p "$APP_DIR/Info.plist" 2>/dev/null | grep -iE "UsageDescription|WebView" | sed 's/^/  /' || true
    fi
    ;;

  *)
    echo "Unsupported extension: $EXT"
    exit 1
    ;;
esac

echo
echo "======================================================"
echo " Done. Complete files in: $WORK"
echo " To view source code (Android): jadx -d apk-decompile-work/src \"$FILE\""
echo "======================================================"
