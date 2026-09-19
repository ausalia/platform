# Auselia brand tooling

Everything needed to regenerate the brand assets and documents from source, so
the PDFs are never the only copy.

## What is here

| Path | What it is |
| --- | --- |
| `mark/make_mark.py` | Single source of truth for the logo mark. Writes the SVG variants to `mark/svg/` (committed) and PNG exports to `build/mark/`. |
| `mark/svg/` | The six logo files: color, reversed, three one-color versions, and the app icon tile. |
| `analysis/analyze.py`, `analysis/build_report.py` | Runs the logo through balance, container fit, size, contour, quadrant, color, colorblind and contrast tests, then builds the "Logo Analysis Report" PDF. |
| `guidelines/make_assets.py`, `guidelines/build_brand.py` | Builds the brand guidelines PDF (landscape, brand typefaces, vector mockups drawn from the real map geometry and design tokens). |
| `fonts.py` | Downloads the typefaces (SIL Open Font License) and cuts static weights from the variable fonts. |
| `build.sh` | Runs all of the above in order. |
| `build/` | Generated output. Not committed. |

## Build

```bash
brew install librsvg        # provides rsvg-convert
./brand/build.sh            # creates brand/.venv on first run
```

Output lands in `brand/build/`:
`Auselia-Brand-Guidelines-v0.1.pdf` and `Auselia-Logo-Analysis-Report.pdf`.

Optional, for previewing pages as images: `pdftoppm -r 70 -png brand/build/Auselia-Brand-Guidelines-v0.1.pdf /tmp/page`
(part of poppler, `brew install poppler`).

## Editing

- **Change the logo:** edit `mark/make_mark.py`, run `./brand/build.sh`, commit the updated `mark/svg/`.
  The website has its own copy of the mark in `src/components/wordmark.tsx` and `src/app/icon.svg`; keep them in step.
- **Change the guidelines text or layout:** edit `guidelines/build_brand.py`. It is plain reportlab, one block per page.
  The version number is in the file name and the footer.
- **Colors and tokens** are duplicated from `src/app/globals.css` and the brand doc. If you change them there, change them in `build_brand.py` too.

The guidelines script reads two files from the app so the map and illustration stay real:
`src/lib/dashboard/demo-geo.ts` and `src/components/plant-mark.tsx`.

## Rules the documents follow

No em dashes. Amber is never text on a light background. Status is never color alone.
See the guidelines PDF, pages 10 to 12 and 23.
