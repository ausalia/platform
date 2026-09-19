"""Single source of truth for the Auselia mark ("variant D"): stem, one leaf, an
amber node on the stem, and two signal arcs. Writes the SVG variants to
mark/svg/ (committed) and 1024 px PNG exports to build/mark/ (used by the
other scripts). Needs rsvg-convert (brew install librsvg)."""
import subprocess
from pathlib import Path

BRAND = Path(__file__).resolve().parents[1]
SVG_DIR = BRAND / "mark" / "svg"
PNG_DIR = BRAND / "build" / "mark"
FOREST, CANOPY, AMBER, BONE = "#14261C", "#1B3A2B", "#E8A13A", "#F4F1EA"
# The artwork is not symmetric about x=32, so the viewBox is offset to center it.
VIEWBOX = "-4.6 3 64 64"

def mark(stem_leaf: str, accent: str) -> str:
    return (
        f'<path d="M28 58V12" fill="none" stroke="{stem_leaf}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>\n'
        f'  <path d="M28 48C28 37 18 31 7 31C7 42 17 50 28 48Z" fill="{stem_leaf}"/>\n'
        f'  <circle cx="28" cy="24" r="6" fill="{accent}"/>\n'
        f'  <path d="M39.5 16A14 14 0 0 1 39.5 32" fill="none" stroke="{accent}" stroke-width="3.6" stroke-linecap="round"/>\n'
        f'  <path d="M46 11.4A22 22 0 0 1 46 36.6" fill="none" stroke="{accent}" stroke-width="3.6" stroke-linecap="round"/>'
    )

def svg(body: str, tile: str | None = None) -> str:
    rect = f'<rect x="-4.6" y="3" width="64" height="64" rx="14" fill="{tile}"/>\n  ' if tile else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VIEWBOX}" width="512" height="512">\n'
            f'  {rect}{body}\n</svg>\n')

VARIANTS = {
    "auselia-mark-color": svg(mark(CANOPY, AMBER)),              # light backgrounds
    "auselia-mark-reversed": svg(mark(BONE, AMBER)),             # dark backgrounds
    "auselia-mark-mono-forest": svg(mark(FOREST, FOREST)),       # one color
    "auselia-mark-mono-bone": svg(mark(BONE, BONE)),
    "auselia-mark-mono-amber": svg(mark(AMBER, AMBER)),
    "auselia-app-icon": svg(  # forest tile, mark scaled to 70% about the artwork center
        f'<g transform="translate(27.4 35) scale(0.7) translate(-27.4 -35)">{mark(BONE, AMBER)}</g>', tile=FOREST),
}

def main():
    SVG_DIR.mkdir(parents=True, exist_ok=True)
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    for name, body in VARIANTS.items():
        (SVG_DIR / f"{name}.svg").write_text(body)
        for px in ([1024, 512, 180, 32, 16] if "icon" in name else [1024, 512, 128, 32, 16]):
            subprocess.run(["rsvg-convert", "-w", str(px), "-h", str(px), str(SVG_DIR / f"{name}.svg"),
                            "-o", str(PNG_DIR / f"{name}-{px}.png")], check=True)
    print(f"wrote {len(VARIANTS)} SVGs to {SVG_DIR} and PNGs to {PNG_DIR}")

if __name__ == "__main__":
    main()
