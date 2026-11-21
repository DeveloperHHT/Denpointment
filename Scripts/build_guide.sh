#!/bin/sh
# Builds Docs/User-Guide.pdf from Docs/User-Guide.html with a Chromium based browser.
# Take fresh screenshots first (see Scripts/screenshots.mjs) when the interface has changed.
#   BROWSER="/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" sh Scripts/build_guide.sh
set -eu
root="$(cd "$(dirname "$0")/.." && pwd)"
browser="${BROWSER:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
"$browser" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$root/Docs/User-Guide.pdf" "file://$root/Docs/User-Guide.html"
echo "Wrote $root/Docs/User-Guide.pdf"
