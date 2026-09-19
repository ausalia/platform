#!/usr/bin/env bash
# Rebuilds everything under brand/build/: fonts, logo PNGs, the logo analysis
# report and the brand guidelines PDF.
#   ./brand/build.sh            build everything
#   PYTHON=/path/to/python ./brand/build.sh   use an existing environment
# Requirements: python3, and rsvg-convert (brew install librsvg).
set -euo pipefail
cd "$(dirname "$0")"

PY="${PYTHON:-.venv/bin/python}"
if [ ! -x "$PY" ]; then
  echo "creating .venv and installing requirements..."
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
  PY=.venv/bin/python
fi
command -v rsvg-convert >/dev/null || { echo "rsvg-convert not found. Install it: brew install librsvg"; exit 1; }

"$PY" fonts.py
"$PY" mark/make_mark.py
"$PY" analysis/analyze.py > /dev/null
"$PY" guidelines/make_assets.py
"$PY" guidelines/build_brand.py
"$PY" analysis/build_report.py
echo
echo "Done. PDFs are in brand/build/:"
ls -1 build/*.pdf
