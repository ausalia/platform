import subprocess, os, re, shutil
from pathlib import Path
BRAND = Path(__file__).resolve().parents[1]
REPO = BRAND.parent
BUILD = BRAND / "build"
A = str(BUILD / "guidelines" / "assets"); os.makedirs(A, exist_ok=True)
SRC = str(BUILD / "mark")
F, C, AM, B = "#14261C", "#1B3A2B", "#E8A13A", "#F4F1EA"
VB = "-4.6 3 64 64"

def mark(fg, amber, leaf=None, extra_arcs=False, outline=False, defs=""):
    leaf = leaf or fg
    leaf_svg = (f'<path d="M28 48C28 37 18 31 7 31C7 42 17 50 28 48Z" fill="none" stroke="{fg}" stroke-width="2.4"/>'
                if outline else f'<path d="M28 48C28 37 18 31 7 31C7 42 17 50 28 48Z" fill="{leaf}"/>')
    mirror = ""
    if extra_arcs:
        mirror = f'<path d="M16.5 16A14 14 0 0 0 16.5 32" fill="none" stroke="{amber}" stroke-width="3.6" stroke-linecap="round"/>'
    return f'''{defs}<path d="M28 58V12" fill="none" stroke="{fg}" stroke-width="5" stroke-linecap="round"/>
{leaf_svg}
<circle cx="28" cy="24" r="6" fill="{amber}"/>
<path d="M39.5 16A14 14 0 0 1 39.5 32" fill="none" stroke="{amber}" stroke-width="3.6" stroke-linecap="round"/>
<path d="M46 11.4A22 22 0 0 1 46 36.6" fill="none" stroke="{amber}" stroke-width="3.6" stroke-linecap="round"/>{mirror}'''

def svg(body, vb=VB, w=512, h=512, bg=None, wrap=None):
    x0, y0, vw, vh = [float(v) for v in vb.split()]
    rect = f'<rect x="{x0}" y="{y0}" width="{vw}" height="{vh}" fill="{bg}"/>' if bg else ""
    inner = body if not wrap else f'<g transform="{wrap}">{body}</g>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}">{rect}{inner}</svg>'

def render(name, s, w=512, h=None):
    p = f"{A}/{name}.svg"; open(p, "w").write(s)
    cmd = ["rsvg-convert", "-w", str(w)]
    if h: cmd += ["-h", str(h)]
    subprocess.run(cmd + [p, "-o", f"{A}/{name}.png"], check=True)

# --- don'ts ---
render("dont_stretch", svg(mark(C, AM), vb="-4.6 3 64 64", w=640, h=380, wrap="translate(-4.6 3) scale(1.5 0.8) translate(4.6 -3)"), 640, 380)
render("dont_recolor", svg(mark("#C0491F", "#4f8fd1")))
grad = f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8DD16B"/><stop offset="1" stop-color="#2B6CB0"/></linearGradient></defs>'
render("dont_gradient", svg(mark("url(#g)", "url(#g)", defs=grad)))
render("dont_rotate", svg(mark(C, AM), wrap="rotate(28 27.4 35)"))
sh = '<defs><filter id="s" x="-30%" y="-30%" width="180%" height="180%"><feGaussianBlur in="SourceAlpha" stdDeviation="2.2"/><feOffset dx="2.5" dy="3" result="o"/><feComponentTransfer><feFuncA type="linear" slope="0.6"/></feComponentTransfer><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
render("dont_shadow", svg(sh + f'<g filter="url(#s)">{mark(C, AM)}</g>'))
render("dont_lowcontrast", svg(mark(C, AM)))
render("dont_outline", svg(mark(C, AM, outline=True)))
render("dont_arcs", svg(mark(C, AM, extra_arcs=True)))
render("dont_crowded", svg(mark(C, AM)))

# --- variants from earlier export (1024 px) ---
for n in ["auselia-mark-color", "auselia-mark-reversed", "auselia-mark-mono-forest", "auselia-mark-mono-bone", "auselia-mark-mono-amber", "auselia-app-icon"]:
    shutil.copy(f"{SRC}/{n}-1024.png", f"{A}/{n}.png")

# --- illustration in brand colors ---
paths = re.findall(r'<path d="([^"]+)"', (REPO / "src" / "components" / "plant-mark.tsx").read_text())
for name, colr in [("plant_sage", "#5C7A63"), ("plant_sap", "#A9C7A0"), ("plant_canopy", "#1B3A2B")]:
    body = "".join(f'<path d="{d}" fill="{colr}"/>' for d in paths)
    render(name, f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="800" height="800">{body}</svg>', 800, 800)
print(sorted(os.listdir(A)))
