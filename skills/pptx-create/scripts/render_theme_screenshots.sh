#!/usr/bin/env bash
# Render theme_gallery.pptx and slice each section's first slide into a per-theme PNG.
# Requires LibreOffice (soffice) and either pdf2image (Python) or poppler (pdftoppm).
#
# Usage: ./scripts/render_theme_screenshots.sh
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$SKILL_DIR/themes/screenshots"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

# 1. build deck
cd "$TMP_DIR"
python3 "$SKILL_DIR/examples/theme_gallery.py"
DECK="$TMP_DIR/theme_gallery.pptx"

# 2. find LibreOffice
SOFFICE=""
for candidate in soffice libreoffice "/Applications/LibreOffice.app/Contents/MacOS/soffice"; do
    if command -v "$candidate" >/dev/null 2>&1 || [ -x "$candidate" ]; then
        SOFFICE="$candidate"
        break
    fi
done
if [ -z "$SOFFICE" ]; then
    echo "error: LibreOffice not found. install from https://libreoffice.org" >&2
    exit 1
fi

# 3. pptx -> pdf
"$SOFFICE" --headless --convert-to pdf --outdir "$TMP_DIR" "$DECK" >/dev/null
PDF="$TMP_DIR/theme_gallery.pdf"

# 4. pdf -> per-page PNGs
mkdir -p "$OUT_DIR"
if command -v pdftoppm >/dev/null 2>&1; then
    pdftoppm -png -r 100 "$PDF" "$TMP_DIR/page"
elif python3 -c "import pdf2image" 2>/dev/null; then
    python3 - <<PY
from pdf2image import convert_from_path
import os
for i, p in enumerate(convert_from_path("$PDF", dpi=100), start=1):
    p.save("$TMP_DIR/page-%03d.png" % i, "PNG")
PY
else
    echo "error: install poppler (pdftoppm) or 'pip install pdf2image' to slice PDF." >&2
    exit 1
fi

# 5. map theme name to its section slide. theme_gallery.py emits:
#   slide 1: title
#   for each theme: section / bullets / metric_grid / cta  (4 slides per theme)
# pick the section slide (first per-theme slide) — index 2,6,10,...
THEMES=$(python3 -c "
import sys
sys.path.insert(0, '$SKILL_DIR')
from themes.themes import list_themes
print('\n'.join(list_themes()))
")

i=0
for theme in $THEMES; do
    page_num=$(( 2 + i * 4 ))
    src=$(printf "$TMP_DIR/page-%03d.png" "$page_num")
    if [ ! -f "$src" ]; then
        # try pdftoppm naming page-N.png (no zero pad) when total <10
        src=$(printf "$TMP_DIR/page-%d.png" "$page_num")
    fi
    if [ -f "$src" ]; then
        cp "$src" "$OUT_DIR/$theme.png"
        echo "+ $OUT_DIR/$theme.png"
    else
        echo "! missing $src for theme $theme" >&2
    fi
    i=$((i + 1))
done

echo "done. $OUT_DIR/"
