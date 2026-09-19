"""Auselia brand guidelines. Landscape 16:9 PDF, built with reportlab.
Nothing here writes into the repos; it only reads platform/src/lib/dashboard/demo-geo.ts."""
import json, os, re, math, datetime
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.dirname(HERE)
REPO = os.path.dirname(BRAND)
BUILD = os.path.join(BRAND, "build")
A = os.path.join(BUILD, "guidelines", "assets")
OUT = os.path.join(BUILD, "Auselia-Brand-Guidelines-v0.1.pdf")
METRICS = json.load(open(os.path.join(BUILD, "analysis", "metrics.json")))
GEO_TS = open(os.path.join(REPO, "src", "lib", "dashboard", "demo-geo.ts")).read()
GEO = json.loads(re.search(r"DEMO_GEO: Geo = (\{.*\});", GEO_TS, re.S).group(1))

for name, f in [("SG-Bold", "SpaceGrotesk-Bold"), ("SG-Med", "SpaceGrotesk-Medium"),
                ("Inter", "Inter-Regular"), ("Inter-Med", "Inter-Medium"), ("Inter-Semi", "Inter-SemiBold"),
                ("Mono", "IBMPlexMono-Regular"), ("Mono-Med", "IBMPlexMono-Medium"), ("Mono-Semi", "IBMPlexMono-SemiBold")]:
    pdfmetrics.registerFont(TTFont(name, os.path.join(BUILD, "fonts", f + ".ttf")))

W, H = 960, 540
M = 56
def hx(s): return tuple(int(s[i:i + 2], 16) / 255 for i in (1, 3, 5))
FOREST, CANOPY, AMBER = "#14261C", "#1B3A2B", "#E8A13A"
SAGE, SAP, AMBER_DEEP = "#5C7A63", "#A9C7A0", "#C77F1E"
BONE, BONE2, INK, GREY = "#F4F1EA", "#EDE8DC", "#1A1A1A", "#6A7A6F"
S_OK, S_STRESS, S_CRIT, S_IDLE = "#5C7A63", "#E8A13A", "#C0491F", "#7A8A80"

c = canvas.Canvas(OUT, pagesize=(W, H))
c.setTitle("Auselia Brand Guidelines v0.1")
c.setAuthor("Auselia")
page_no = [0]

def Y(t): return H - t
def fill(hexc, a=1.0): c.setFillColorRGB(*hx(hexc), alpha=a)
def stroke(hexc, w=1, a=1.0): c.setStrokeColorRGB(*hx(hexc), alpha=a); c.setLineWidth(w)
def mix(a, b, t):  # t of a over b
    A_, B_ = hx(a), hx(b)
    return "#%02X%02X%02X" % tuple(int(round((A_[i] * t + B_[i] * (1 - t)) * 255)) for i in range(3))
def text(x, top, s, font="Inter", size=10.5, color=INK, align="left", cs=0, alpha=1.0):
    if not s: return
    fill(color, alpha)
    w = stringWidth(s, font, size) + cs * len(s)
    if align == "center": x -= w / 2
    elif align == "right": x -= w
    t = c.beginText(x, Y(top)); t.setFont(font, size); t.setCharSpace(cs); t.textOut(s); c.drawText(t)
def wrap(x, top, s, w, font="Inter", size=10.5, color=INK, lead=None, alpha=1.0):
    lead = lead or size * 1.5
    for ln in simpleSplit(s, font, size, w):
        text(x, top, ln, font, size, color, alpha=alpha); top += lead
    return top
def wrap_h(s, w, font="Inter", size=10.5, lead=None):
    return len(simpleSplit(s, font, size, w)) * (lead or size * 1.5)
def kicker(x, top, s, color=SAGE):
    text(x, top, s.upper(), "Mono-Med", 7.6, color, cs=1.6)
def rect(x, top, w, h, color, r=0, a=1.0):
    fill(color, a)
    (c.roundRect(x, Y(top + h), w, h, r, stroke=0, fill=1) if r else c.rect(x, Y(top + h), w, h, stroke=0, fill=1))
def frame(x, top, w, h, color, r=8, lw=0.9, a=1.0, dash=None):
    stroke(color, lw, a)
    if dash: c.setDash(*dash)
    c.roundRect(x, Y(top + h), w, h, r, stroke=1, fill=0); c.setDash()
def img(name, x, top, w, h, anchor="c"):
    c.drawImage(ImageReader(name if os.path.isabs(name) else os.path.join(A, name)), x, Y(top + h), width=w, height=h, mask="auto", preserveAspectRatio=True, anchor=anchor)
def bg(color): rect(0, 0, W, H, color)
def chrome(dark=False, num=True):
    col = SAP if dark else SAGE
    text(M, H - 22 + 0, "AUSELIA  /  BRAND GUIDELINES  /  VERSION 0.1", "Mono", 6.4, col, cs=1.2)
    if num:
        text(W - M, H - 22, f"{page_no[0]:02d}", "Mono-Med", 7.5, col, "right")
def new(dark=False, bgc=None):
    if page_no[0]: c.showPage()
    page_no[0] += 1
    bg(bgc or (FOREST if dark else BONE))
    chrome(dark)
def title(s, dark=False, top=92, size=34):
    text(M, top, s, "SG-Bold", size, BONE if dark else CANOPY, cs=-0.5)
def lede(s, dark=False, top=118, w=560, size=12.5):
    return wrap(M, top, s, w, "Inter", size, (BONE if dark else INK), lead=size * 1.55, alpha=0.9)

def lede_one(s, dark=False, top=124, w=848, size=12.5):
    while stringWidth(s, "Inter", size) > w and size > 9.5:
        size -= 0.25
    text(M, top, s, "Inter", size, BONE if dark else INK, alpha=0.9)

def centered_lines(x, top, w, h, lines, font="Inter", size=10, color=INK, lead=None, alpha=1.0, align="left", pad=18):
    """Vertically centers a block of lines inside a box (top, h)."""
    lead = lead or size * 1.5
    total = len(lines) * lead
    y0 = top + (h - total) / 2 + size * 0.85
    for i, ln in enumerate(lines):
        if align == "center": text(x + w / 2, y0 + i * lead, ln, font, size, color, "center", alpha=alpha)
        else: text(x + pad, y0 + i * lead, ln, font, size, color, alpha=alpha)

# ---- small vector helpers ----
def status_icon(kind, cx, cy, r, color):
    fill(color)
    if kind == "good":
        c.circle(cx, Y(cy), r, stroke=0, fill=1)
    elif kind == "warning":
        p = c.beginPath(); p.moveTo(cx, Y(cy - r)); p.lineTo(cx + r, Y(cy + r * 0.85)); p.lineTo(cx - r, Y(cy + r * 0.85)); p.close(); c.drawPath(p, stroke=0, fill=1)
    elif kind == "critical":
        p = c.beginPath(); p.moveTo(cx, Y(cy - r * 1.1)); p.lineTo(cx + r * 1.1, Y(cy)); p.lineTo(cx, Y(cy + r * 1.1)); p.lineTo(cx - r * 1.1, Y(cy)); p.close(); c.drawPath(p, stroke=0, fill=1)
    else:
        c.roundRect(cx - r, Y(cy + r * 0.22), r * 2, r * 0.44, r * 0.22, stroke=0, fill=1)
STATUS = {"good": (S_OK, "Nominal", "Normal"), "warning": (S_STRESS, "Elevated", "Elevado"), "critical": (S_CRIT, "Critical", "Crítico"), "idle": (S_IDLE, "No data", "Sin datos")}
def pill(x, top, kind, base=BONE2, lang=0, h=17, size=7.2):
    col, en, es = STATUS[kind]; label = (en, es)[lang]
    w = stringWidth(label.upper(), "Mono-Semi", size) + 34
    rect(x, top, w, h, mix(col, base, 0.18), h / 2)
    status_icon(kind, x + 11, top + h / 2, 3.3, col)
    text(x + 20, top + h / 2 + 2.5, label.upper(), "Mono-Semi", size, INK if base in (BONE, BONE2) else BONE, cs=0.4)
    return w
def parse_path(d):
    n = [float(v) for v in re.findall(r"-?\d+\.?\d*", d)]
    return [(n[i], n[i + 1]) for i in range(0, len(n) - 1, 2)]
def draw_map(x, top, w, h, statuses, base, outline, selected=None, icons=True):
    vw, vh = GEO["width"], GEO["height"]
    s = min(w / vw, h / vh)
    ox, oy = x + (w - vw * s) / 2, top + (h - vh * s) / 2
    P = lambda px, py: (ox + px * s, Y(oy + py * s))
    pts = parse_path(GEO["farmPath"])
    p = c.beginPath(); p.moveTo(*P(*pts[0]))
    for q in pts[1:]: p.lineTo(*P(*q))
    p.close(); stroke(outline, 0.8, 0.5); c.drawPath(p, stroke=1, fill=0)
    for cu in GEO["cuarteles"]:
        st = statuses.get(cu["id"], "good")
        pp = parse_path(cu["path"]); p = c.beginPath(); p.moveTo(*P(*pp[0]))
        for q in pp[1:]: p.lineTo(*P(*q))
        p.close(); fill(mix(STATUS[st][0], base, 0.55))
        stroke(outline if selected == cu["id"] else base, 2 if selected == cu["id"] else 1.2)
        c.drawPath(p, stroke=1, fill=1)
        if icons and st != "good":
            cx = sum(a for a, _ in pp) / len(pp); cy = sum(b for _, b in pp) / len(pp)
            px_, py_ = P(cx, cy); status_icon(st, px_, H - py_, 3.4, STATUS[st][0])
def lum(hexc):
    def f(v): return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = [f(v) for v in hx(hexc)]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b
def ratio(a, b):
    la, lb = lum(a), lum(b); hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)
def rgb_s(hexc): return "%d, %d, %d" % tuple(int(round(v * 255)) for v in hx(hexc))

TODAY = datetime.datetime.now().strftime("%B %d, %Y").replace(" 0", " ")

# ============================ 1. COVER ============================
new(dark=True)
# the mark is drawn square (400 pt) and centered in its 460 pt box
CX, CTOP, CS_ = 500, 40 + (460 - 400) / 2, 400
img("auselia-mark-reversed.png", 500, 40, 400, 460)
node_x = CX + (28 + 4.6) / 64 * CS_
node_y = CTOP + (24 - 3) / 64 * CS_
for r_, a_ in [(46, 0.5), (86, 0.28), (130, 0.14)]:   # faint rings centered exactly on the amber node
    stroke(AMBER, 1.4, a_); c.circle(node_x, Y(node_y), r_, stroke=1, fill=0)
kicker(M, 118, "Brand guidelines  /  version 0.1", SAP)
text(M, 205, "AUS", "SG-Bold", 76, BONE, cs=-1.5)
text(M + stringWidth("AUS", "SG-Bold", 76) - 3, 205, "ELIA", "SG-Bold", 76, AMBER, cs=-1.5)
text(M, 248, "Edge-AI silicon that listens to plants.", "Inter", 17, BONE, alpha=0.92)
wrap(M, 330, "How Auselia looks, sounds and behaves: the mark, color, type, voice, motion and the interface.", 340, "Inter", 10.5, SAP, lead=16)
text(M, 470, f"Version 0.1  /  {TODAY}", "Mono", 8, SAP, cs=0.8)

# ============================ 2. CONTENTS ============================
new()
title("What is in this guide")
sections = [
    ("01", "The idea", "What Auselia is, the name, and the one tension behind every choice", "03"),
    ("02", "The mark", "Logo, variants, lockups, clear space, sizes, and what to avoid", "05"),
    ("03", "Color", "Palette, ratios, tested contrast pairs, and status colors", "10"),
    ("04", "Type and voice", "Three typefaces, how we write, taglines, and copy examples", "13"),
    ("05", "Imagery, motion, data", "The plant, the signal rings, charts, the map, and the interface", "17"),
    ("06", "In use", "Website, app icon, field signage, chip silkscreen, ship checklist", "21"),
    ("07", "Reference", "Palette, type, mark, status, voice and motion on one page", "24"),
]
t = 152
for n, name, desc, pg in sections:
    text(M, t, n, "Mono-Med", 9, AMBER_DEEP, cs=1)
    text(M + 48, t, name, "SG-Bold", 19, CANOPY)
    text(M + 48, t + 19, desc, "Inter", 10.5, GREY)
    text(W - M, t, pg, "Mono-Med", 9.5, SAGE, "right")
    stroke(CANOPY, 0.6, 0.15); c.line(M, Y(t + 32), W - M, Y(t + 32))
    t += 49

# ============================ 3. WHAT AUSELIA IS ============================
new()
kicker(M, 56, "01  The idea")
title("What Auselia is", top=100)
wrap(M, 150, "Auselia is a research project building heterogeneous edge-AI silicon that listens to plants.", 420, "SG-Med", 20, CANOPY, lead=27)
wrap(M, 240, "A field node picks up the quiet ultrasonic clicks a plant makes when its water column starts to fail (xylem cavitation, 100 kHz to 1 MHz). A custom low-power RISC-V chip runs TinyML on the device and flags water stress before it shows on the leaf.", 420, "Inter", 11, INK, lead=17)
wrap(M, 336, "It is aimed at Chilean agriculture first: blueberries, cherries and wine grapes.", 420, "Inter", 11, INK, lead=17)
rect(M, 392, 420, 78, BONE2, 10)
text(M + 16, 416, "The first plant", "Mono-Med", 7.6, AMBER_DEEP, cs=1.2)
wrap(M + 16, 436, "Hope, the bench-test pot. “Auselia listens to Hope.” Chips are named after virtues and missions, starting with Hope. Keep the origin story.", 388, "Inter", 10, INK, lead=14.5)
# right column: the name
rect(500, 70, 404, 400, CANOPY, 16)
kicker(524, 104, "The name", SAP)
text(524, 152, "auscultāre", "SG-Bold", 34, BONE, cs=-0.5)
text(524, 176, "Latin, “to listen”", "Inter", 11, SAP)
wrap(524, 210, "The root of auscultation, what a doctor does with a stethoscope: listening to the inner sounds of a living body. Auselia auscultates a plant.", 356, "Inter", 11, BONE, lead=17, alpha=0.92)
wrap(524, 292, "One-line answer when asked:", 356, "Inter", 9.5, SAP)
wrap(524, 310, "“It is from auscultar, to listen to what is hidden inside a living body. That is what the device does to a plant.”", 356, "Inter-Med", 11, BONE, lead=17)
rect(524, 388, 356, 62, FOREST, 10)
text(542, 412, "PRONOUNCED", "Mono-Semi", 7.4, AMBER, cs=1.4)
text(542, 436, "au\u00b7SE\u00b7lia", "SG-Bold", 17, BONE, cs=0.4)

# ============================ 4. CORE IDEA ============================
new()
kicker(M, 56, "01  The idea")
title("One tension, on purpose", top=100)
lede("Every design decision serves the same tension. If a page loses one side, it is wrong.", top=128, w=520)
cw = 300
for i, (h, sub, col, items) in enumerate([
    ("The living voice", "A plant in quiet distress", CANOPY, ["Organic greens", "The plant and root motif", "Warmth"]),
    ("The instrument", "Silicon precise enough to hear it", FOREST, ["Disciplined geometric type", "Mono for data", "The amber signal, used sparingly", "Restraint"]),
]):
    x = M + i * (cw + 24)
    rect(x, 170, cw, 190, col, 14)
    text(x + 22, 202, h, "SG-Bold", 20, BONE)
    text(x + 22, 222, sub, "Inter", 10.5, SAP)
    for j, it in enumerate(items):
        fill(AMBER); c.circle(x + 26, Y(252 + j * 21), 2.4, stroke=0, fill=1)
        text(x + 38, 255 + j * 21, it, "Inter", 11, BONE, alpha=0.92)
# spectrum
text(M, 398, "Where we sit", "Mono-Med", 7.6, SAGE, cs=1.4)
bx, bw = M, 624
for k in range(60):
    fill(mix(SAP, SAGE, 1 - k / 59) if False else mix(CANOPY, SAP, k / 59))
    c.rect(bx + k * bw / 60, Y(430), bw / 60 + 0.6, 14, stroke=0, fill=1)
fill(AMBER); c.circle(bx + bw / 2, Y(423), 11, stroke=0, fill=1)
stroke(FOREST, 2); c.circle(bx + bw / 2, Y(423), 11, stroke=1, fill=0)
text(bx, 452, "Too organic: hides the engineering", "Inter", 9, GREY)
text(bx + bw, 452, "Too clinical: hides the care", "Inter", 9, GREY, "right")
text(bx + bw / 2, 452, "Auselia", "Inter-Semi", 9, CANOPY, "center")
rect(M + 660, 170, 188, 190, AMBER, 14)
text(M + 678, 200, "THE TEST", "Mono-Semi", 7.6, FOREST, cs=1.6)
wrap(M + 678, 226, "Can you see the living thing AND the instrument in it?", 152, "SG-Bold", 17, FOREST, lead=22)
wrap(M + 678, 316, "Softness comes from color and the mark, never from soft or script fonts.", 152, "Inter", 9.4, FOREST, lead=13.5, alpha=0.85)

# ============================ 5. THE MARK ============================
new()
kicker(M, 56, "02  The mark")
title("The mark", top=100)
lede("One stem, one leaf, one amber node that has just been heard. Four parts, each with a job.", top=128, w=340)
PX0, PW_ = 452, 452                      # card runs to the right margin
MX, MS = PX0 + 10, 380
rect(PX0, 70, PW_, 400, BONE2, 16)
img("auselia-mark-color.png", MX, 90, MS, MS)
def mp(sx, sy): return (MX + (sx + 4.6) / 64 * MS, 90 + (sy - 3) / 64 * MS)
parts = [("Amber node", "the instant of being heard. The only focal point", (28, 24), 1), ("Leaf", "the living side. One leaf only", (14, 40), 2),
         ("Stem", "the plant, one continuous line", (28, 54), 3)]
ly = 220
for nme, desc, (sx, sy), i in parts:
    tx, ty = M, ly + (i - 1) * 74
    text(tx, ty, f"0{i}", "Mono-Med", 8, AMBER_DEEP, cs=1)
    text(tx + 26, ty, nme, "SG-Bold", 14, CANOPY)
    wrap(tx + 26, ty + 15, desc, 260, "Inter", 9.4, GREY, lead=13)
    px, py = mp(sx, sy)
    stroke(AMBER_DEEP, 0.9, 0.9); c.setDash(2, 2)
    c.line(tx + 236, Y(ty - 3), px, Y(py)); c.setDash()
    fill(AMBER_DEEP); c.circle(px, Y(py), 2.8, stroke=0, fill=1)
# arcs label sits inside the card, to the right of the arcs
apx, apy = mp(51.5, 24)
text(apx + 14, apy - 6, "04", "Mono-Med", 8, AMBER_DEEP, cs=1)
text(apx + 14, apy + 10, "Arcs", "SG-Bold", 14, CANOPY)
wrap(apx + 14, apy + 25, "the signal, the ring-down of a cavitation", 74, "Inter", 8.6, GREY, lead=12)
text(M, 470, "Flat shapes only. No gradients on the mark. It must print in one color on silicon.", "Inter", 9.4, SAGE)

# ============================ 6. VARIANTS ============================
new()
kicker(M, 56, "02  The mark")
title("Variants", top=100)
lede_one("Color mark on light grounds, reversed on dark. One-color versions are for stamps, silkscreen and engraving.", top=128)
tiles = [("Color", "auselia-mark-color.png", BONE2, "Light backgrounds. Default."),
         ("Reversed", "auselia-mark-reversed.png", FOREST, "Dark backgrounds, screens, outdoor use."),
         ("One color: forest", "auselia-mark-mono-forest.png", BONE2, "Stamps, single-ink print."),
         ("One color: bone", "auselia-mark-mono-bone.png", FOREST, "Engraving on dark surfaces."),
         ("One color: amber", "auselia-mark-mono-amber.png", FOREST, "Silicon, chip silkscreen."),
         ("App icon", "auselia-app-icon.png", BONE, "Below 24 px, favicons, home screen.")]
tw, th = 262, 118
for i, (nme, f, bgc, use) in enumerate(tiles):
    x = M + (i % 3) * (tw + 20); t = 166 + (i // 3) * (th + 50)
    rect(x, t, tw, th, bgc, 12)
    if bgc == BONE: frame(x, t, tw, th, CANOPY, 12, 0.6, 0.2)
    img(f, x + 70, t + 10, tw - 140, th - 20) if f != "auselia-app-icon.png" else img(f, x + 83, t + 17, 94, 94)
    text(x, t + th + 17, nme, "SG-Bold", 11.5, CANOPY)
    text(x, t + th + 30, use, "Inter", 8.8, GREY)

# ============================ 7. LOCKUPS ============================
new()
kicker(M, 56, "02  The mark")
title("Lockups and wordmark", top=100)
lede("The wordmark is set in Space Grotesk Bold, all caps. On dark grounds AUS is bone and ELIA is amber. On light grounds it stays one dark color, because amber text fails on light.", top=128, w=620)
def wordmark_in_card(cx0, cw_, top, size, dark, mark_img):
    """Mark + wordmark, centered horizontally in a card."""
    fs = size * 0.68; cs_ = 0.3; gap = size * 0.28
    tw_ = stringWidth("AUSELIA", "SG-Bold", fs) + cs_ * 7
    x0 = cx0 + (cw_ - (size + gap + tw_)) / 2
    img(mark_img, x0, top, size, size)
    tx = x0 + size + gap
    aus = BONE if dark else CANOPY; elia = AMBER if dark else CANOPY
    text(tx, top + size * 0.68, "AUS", "SG-Bold", fs, aus, cs=cs_)
    text(tx + stringWidth("AUS", "SG-Bold", fs) + cs_ * 3, top + size * 0.68, "ELIA", "SG-Bold", fs, elia, cs=cs_)
rect(M, 190, 410, 130, BONE2, 14); wordmark_in_card(M, 410, 224, 62, False, "auselia-mark-color.png")
rect(M + 434, 190, 410, 130, FOREST, 14); wordmark_in_card(M + 434, 410, 224, 62, True, "auselia-mark-reversed.png")
text(M, 338, "Horizontal, on light", "Inter-Semi", 9.4, CANOPY); text(M + 434, 338, "Horizontal, on dark", "Inter-Semi", 9.4, CANOPY)
# stacked: mark and word centered on the card, block centered vertically
SW, SH = 200, 116
rect(M, 366, SW, SH, FOREST, 12)
fs = 17; cs_ = 0.3; mk = 44; cap = fs * 0.72; gap = 10
block_h = mk + gap + cap
mtop = 366 + (SH - block_h) / 2
scx = M + SW / 2
img("auselia-mark-reversed.png", scx - mk / 2, mtop, mk, mk)
tw_ = stringWidth("AUSELIA", "SG-Bold", fs) + cs_ * 7
sx0 = scx - tw_ / 2
base = mtop + mk + gap + cap
text(sx0, base, "AUS", "SG-Bold", fs, BONE, cs=cs_)
text(sx0 + stringWidth("AUS", "SG-Bold", fs) + cs_ * 3, base, "ELIA", "SG-Bold", fs, AMBER, cs=cs_)
text(M, 500 - 4, "Stacked, small spaces", "Inter-Semi", 9.4, CANOPY)
# rules
rules = ["Wordmark is legible down to about 14 px. Below that, use the mark alone or the app icon.",
         "Never split the colors on a light ground. Amber stays a shape there, not text.",
         "Keep the mark to the left of the wordmark, sized to the cap height of the type or a little more."]
ry = 372
for r_ in rules:
    fill(AMBER); c.circle(M + 232, Y(ry - 3), 2.4, stroke=0, fill=1)
    ry = wrap(M + 246, ry, r_, 560, "Inter", 10, INK, lead=14.5) + 8

# ============================ 8. CLEAR SPACE + SIZES ============================
new()
kicker(M, 56, "02  The mark")
title("Clear space and minimum size", top=100)
# clear space diagram
dx, dt, ds = 90, 170, 250
rect(M, 150, 330, 330, BONE2, 14)
ix, it_, iw = M + 65, 185, 200
img("auselia-mark-color.png", ix, it_, iw, iw)
# artwork bbox approx in the 64x64 box: x 4.5..47.8 (viewBox -4.6..59.4), y 9.5..60.5 (3..67)
bx0 = ix + (4.5 + 4.6) / 64 * iw; bx1 = ix + (51.8 + 4.6) / 64 * iw
by0 = it_ + (9.5 - 3) / 64 * iw; by1 = it_ + (60.5 - 3) / 64 * iw
xx = 12 / 64 * iw  # one node diameter
stroke(AMBER_DEEP, 0.9); c.setDash(3, 3)
c.rect(bx0 - 1 * xx, Y(by1 + xx), (bx1 - bx0) + 2 * xx, (by1 - by0) + 2 * xx, stroke=1, fill=0); c.setDash()
stroke(CANOPY, 0.7); c.rect(bx0, Y(by1), bx1 - bx0, by1 - by0, stroke=1, fill=0)
stroke(AMBER_DEEP, 0.9); c.setDash(2, 2); c.circle(bx0 - xx * 0.5, Y((by0 + by1) / 2), xx * 0.5, stroke=1, fill=0); c.setDash()
text(bx0 - xx * 0.5, (by0 + by1) / 2 + 3, "x", "Mono-Semi", 9, AMBER_DEEP, "center")
text(M + 165, 472, "Clear space = one node diameter (x) on every side", "Inter", 9, GREY, "center")
# min sizes
rx = 420
text(rx, 170, "Minimum sizes", "SG-Bold", 15, CANOPY)
rows = [("Full mark, screen", "24 px", "auselia-mark-color.png", 24), ("Full mark, print", "8 mm", "auselia-mark-color.png", 30),
        ("Below 24 px, favicon", "App icon tile", "auselia-app-icon.png", 20), ("Chip silkscreen", "One color amber", "auselia-mark-mono-amber.png", 30)]
ry = 190
for nme, val, f, sz in rows:
    bgc = FOREST if "amber" in f or "icon" in f else BONE2
    rect(rx, ry, 56, 46, bgc, 8); img(f, rx + 28 - sz / 2, ry + 23 - sz / 2, sz, sz)
    text(rx + 72, ry + 19, nme, "Inter-Semi", 10, CANOPY); text(rx + 72, ry + 34, val, "Mono", 8.4, GREY)
    ry += 54
# similarity table from analysis
text(rx, 428, "Measured legibility (similarity to the full-size mark)", "Mono-Med", 7.2, SAGE, cs=0.8)
sx = rx
for s in METRICS["size"]:
    pct = s["score"] * 100
    col = {"Great": "#7BD96B", "Okay": "#E5D26A", "Weak": "#E8A06A", "Poor": "#E86A6A"}[s["rating"]]
    rect(sx, 438, 68, 40, mix(col, BONE, 0.35), 6)
    text(sx + 34, 455, f"{pct:.0f}%", "SG-Bold", 13, INK, "center")
    text(sx + 34, 470, f"{s['n']} px", "Mono", 7.2, GREY, "center")
    sx += 76
# (six items fit at 62 px pitch)

# ============================ 9. DON'TS ============================
new()
kicker(M, 56, "02  The mark")
title("What to avoid", top=100)
donts = [("Stretch or squash", "dont_stretch.png"), ("Recolor the parts", "dont_recolor.png"), ("Add gradients", "dont_gradient.png"),
         ("Rotate or tilt", "dont_rotate.png"), ("Add shadows or glow", "dont_shadow.png"), ("Put it on mid-gray", "dont_lowcontrast.png"),
         ("Outline the leaf", "dont_outline.png"), ("Add or move arcs", "dont_arcs.png")]
tw, th = 196, 118
for i, (nme, f) in enumerate(donts):
    x = M + (i % 4) * (tw + 20); t = 134 + (i // 4) * (th + 54)
    rect(x, t, tw, th, S_IDLE if f == 'dont_lowcontrast.png' else BONE2, 12)
    img(f, x + 34, t + 8, tw - 68, th - 16)
    stroke(S_CRIT, 2.4); c.line(x + tw - 26, Y(t + 12), x + tw - 12, Y(t + 26)); c.line(x + tw - 12, Y(t + 12), x + tw - 26, Y(t + 26))
    text(x, t + th + 18, nme, "Inter-Semi", 10.5, CANOPY)
text(M, 484, "Also: never let the mark and the waveform become two separate objects, and never crowd it inside the clear space.", "Inter", 9.6, GREY)

# ============================ 10. COLOR ============================
new()
kicker(M, 56, "03  Color")
title("Palette", top=100)
big = [("Forest", FOREST, "Primary dark. Backgrounds, silkscreen."), ("Canopy", CANOPY, "Secondary green. Headings on light."), ("Amber", AMBER, "The signal. Actions and one key datum.")]
bx = M
for nme, col, role in big:
    rect(bx, 130, 200, 150, col, 12)
    text(bx + 16, 254, nme, "SG-Bold", 15, BONE if col != AMBER else FOREST)
    text(bx + 16, 268, col, "Mono", 8.4, BONE if col != AMBER else FOREST, alpha=0.9)
    text(bx, 298, role, "Inter", 8.8, GREY)
    text(bx, 311, f"RGB {rgb_s(col)}", "Mono", 7.4, SAGE)
    bx += 216
small = [("Sage", SAGE, "Labels, dividers (large text only)"), ("Sap", SAP, "Soft fills, text on dark"), ("Amber deep", AMBER_DEEP, "Amber text on DARK grounds only"),
         ("Bone", BONE, "Primary light background"), ("Bone 2", BONE2, "Cards, secondary light"), ("Ink", INK, "Body text on light")]
for i, (nme, col, role) in enumerate(small):
    x = M + (i % 3) * 216; t = 334 + (i // 3) * 60
    rect(x, t, 44, 44, col, 8)
    if col in (BONE, BONE2): frame(x, t, 44, 44, CANOPY, 8, 0.6, 0.25)
    text(x + 54, t + 14, f"{nme}  {col}", "Inter-Semi", 9.6, CANOPY)
    text(x + 54, t + 28, role, "Inter", 8.4, GREY)
# ratio bar on right
rx = M + 664
text(rx, 130, "Usage ratio", "SG-Bold", 15, CANOPY)
segs = [(FOREST, 40, "Forest"), (CANOPY, 15, "Canopy"), (BONE, 25, "Bone"), (INK, 10, "Ink"), (AMBER, 10, "Amber")]
yy = 150
for col, pct, nme in segs:
    hgt = pct / 100 * 250
    rect(rx, yy, 60, hgt - 2, col, 4)
    if col == BONE: frame(rx, yy, 60, hgt - 2, CANOPY, 4, 0.6, 0.3)
    text(rx + 72, yy + hgt / 2 + 2, f"{pct}%  {nme}", "Inter", 8.6, INK)
    yy += hgt
wrap(rx, 424, "About 55% green, 35% neutral, 10% amber. When amber is common it stops meaning signal.", 184, "Inter", 8.8, GREY, lead=12.5)

# ============================ 11. CONTRAST ============================
new()
kicker(M, 56, "03  Color")
title("Contrast that actually works", top=100)
lede_one("Measured ratios, not opinions. Amber is never a text color on a light background, at any size.", top=128)
pairs = [(BONE, FOREST, "Bone on Forest"), (INK, BONE, "Ink on Bone"), (BONE, CANOPY, "Bone on Canopy"), (AMBER, FOREST, "Amber on Forest"),
         (SAP, FOREST, "Sap on Forest"), (FOREST, AMBER, "Forest on Amber (buttons)"), (SAGE, BONE, "Sage on Bone"), (SAGE, FOREST, "Sage on Forest"),
         (AMBER, BONE, "Amber on Bone"), (AMBER_DEEP, BONE, "Amber deep on Bone"), (BONE, AMBER_DEEP, "Bone on Amber deep"), (AMBER_DEEP, FOREST, "Amber deep on Forest")]
def grade(r):
    return ("AAA", "#7BD96B") if r >= 7 else ("AA", "#7BD96B") if r >= 4.5 else ("Large text only", "#E5D26A") if r >= 3 else ("Fails", "#E86A6A")
cwid = 268
for i, (fg, bgc, nme) in enumerate(pairs):
    x = M + (i % 3) * (cwid + 22); t = 182 + (i // 3) * 68
    r = ratio(fg, bgc); g, gc = grade(r)
    rect(x, t, 62, 52, bgc, 8)
    if bgc in (BONE, BONE2): frame(x, t, 62, 52, CANOPY, 8, 0.6, 0.25)
    text(x + 31, t + 33, "Aa", "SG-Bold", 22, fg, "center")
    text(x + 74, t + 16, nme, "Inter-Semi", 9.6, CANOPY)
    text(x + 74, t + 32, f"{r:.1f} : 1", "Mono-Med", 10.5, INK)
    rect(x + 74, t + 38, stringWidth(g, "Mono-Med", 7) + 14, 13, mix(gc, BONE, 0.45), 6.5)
    text(x + 81, t + 47.5, g, "Mono-Med", 7, INK)
text(M, 470, "Rules: amber on light is a fill (buttons) only. Sage and grey are large text only. Body text is Ink on Bone or Bone on Forest.", "Inter", 9.6, GREY)

# ============================ 12. STATUS + ACCESSIBILITY ============================
new()
kicker(M, 56, "03  Color")
title("Status is never color alone", top=100)
lede_one("About 1 in 12 men and 1 in 200 women see color differently. Every status carries a word and its own shape.", top=128)
x = M
for kind in ["good", "warning", "critical", "idle"]:
    col, en, es = STATUS[kind]
    rect(x, 176, 198, 128, BONE2, 12)
    status_icon(kind, x + 34, 218, 13, col)
    text(x + 60, 216, en.upper(), "Mono-Semi", 11, INK, cs=0.8)
    text(x + 60, 232, es, "Inter", 9.4, GREY)
    text(x + 18, 268, col, "Mono", 8.4, GREY)
    shape = {"good": "Circle", "warning": "Triangle", "critical": "Diamond", "idle": "Dash"}[kind]
    text(x + 18, 284, f"Shape: {shape}", "Inter", 8.8, GREY)
    x += 214
# in-context pills
text(M, 336, "In the interface", "SG-Bold", 13, CANOPY)
px = M
for kind in ["good", "warning", "critical", "idle"]:
    px += pill(px, 348, kind) + 10
# colorblind
text(M + 450, 336, "How the mark holds up", "SG-Bold", 13, CANOPY)
cbn = ["Deuteranopia", "Protanopia", "Tritanopia"]
cbm = {r["name"]: r for r in METRICS["colorblind"]}
for i, nme in enumerate(cbn):
    x = M + 450 + i * 116
    rect(x, 350, 104, 96, WHITE if False else "#FFFFFF", 8); frame(x, 350, 104, 96, CANOPY, 8, 0.6, 0.2)
    img(os.path.join(BUILD, "analysis", "assets", f"cb_{nme}.png"), x + 8, 354, 88, 62)
    text(x + 52, 430, nme, "Inter-Semi", 8, CANOPY, "center")
    text(x + 52, 441, f"amber vs green: {cbm[nme]['amber_green_de']:.0f}", "Mono", 6.8, GREY, "center")
wrap(M, 396, "Thresholds today (soil moisture): below 20% is Critical, below 40% is Elevated. These are placeholders until an agronomist confirms them.", 380, "Inter", 9.6, GREY, lead=14)
wrap(M, 436, "Outdoor rule: anything seen in bright sun uses a forest ground, bone text and an amber accent. Never amber on light outdoors.", 380, "Inter", 9.6, GREY, lead=14)

# ============================ 13. TYPOGRAPHY ============================
new()
kicker(M, 56, "04  Type and voice")
title("Three typefaces, three jobs", top=100)
specs = [("Space Grotesk", "SG-Bold", "Display and headings", "Auselia is listening", "Tight tracking, confident. The instrument-panel voice."),
         ("Inter", "Inter", "Body and interface", "A field node that hears drought stress before it shows.", "Neutral and legible. No personality fighting the headings."),
         ("IBM Plex Mono", "Mono-Med", "Data, labels, telemetry", "SOIL MOISTURE  52%   ROOT TEMP  20.8°C", "Where the silicon texture lives. Uppercase, letter-spaced for labels.")]
t = 138
for nme, fnt, job, sample, note in specs:
    rect(M, t, 560, 104, BONE2, 12)
    text(M + 20, t + 26, nme, "Inter-Semi", 9.6, CANOPY); text(M + 540, t + 26, job, "Mono", 8, SAGE, "right", cs=0.6)
    fs = 30 if fnt == "SG-Bold" else 16 if fnt == "Inter" else 13.5
    text(M + 20, t + 66, sample, fnt, fs, INK, cs=(-0.6 if fnt == "SG-Bold" else 0))
    text(M + 20, t + 88, note, "Inter", 8.8, GREY)
    t += 116
# scale
rx = M + 592
text(rx, 150, "Scale (screen)", "SG-Bold", 14, CANOPY)
scale = [("Display", "48 / 56", "SG-Bold"), ("H1", "32 / 38", "SG-Bold"), ("H2", "20 / 26", "SG-Bold"), ("Body", "16 / 26", "Inter"), ("Small", "13 / 20", "Inter"), ("Label", "11, caps, +12%", "Mono-Med"), ("Data", "14 semibold", "Mono-Semi")]
yy = 172
for nme, val, fnt in scale:
    text(rx, yy, nme, fnt, 12 if fnt.startswith("SG") else 10.5, INK)
    text(rx + 250, yy, val, "Mono", 8.4, SAGE, "right")
    stroke(CANOPY, 0.5, 0.15); c.line(rx, Y(yy + 8), rx + 250, Y(yy + 8)); yy += 32
wrap(rx, 410, "Never a script, handwriting, serif display or leafy font. The tension needs type on the engineered side.", 250, "Inter", 9.4, GREY, lead=13.5)

# ============================ 14. VOICE ============================
new(dark=True)
kicker(M, 56, "04  Type and voice", SAP)
title("How we sound", dark=True, top=100)
text(M, 138, "Precise like an instrument, warm like something that cares for a living thing.", "SG-Med", 17.5, BONE)
text(M, 164, "Plain engineering language, never cold, with a little quiet wonder.", "SG-Med", 17.5, SAP)
cols = [("We are", ["Precise", "Calm", "Curious", "Grounded", "Quietly bold"], SAP), ("We are not", ["Hypey", "Corporate", "Cutesy", "Alarmist", "Jargon-drunk"], "#E86A6A")]
for i, (h, items, col) in enumerate(cols):
    x = M + i * 220
    text(x, 232, h.upper(), "Mono-Semi", 8, col, cs=1.6)
    for j, it in enumerate(items):
        text(x, 258 + j * 22, it, "Inter", 12, BONE)
x = M + 470
text(x, 232, "SAY", "Mono-Semi", 8, AMBER, cs=1.6)
wrap(x, 254, "listen, hear, signal, node, stress, early, quiet, field", 380, "Inter-Med", 12, BONE, lead=18)
text(x, 296, "VERBS", "Mono-Semi", 8, AMBER, cs=1.6)
wrap(x, 318, "listen, detect, hear, sense, read, flag, catch", 380, "Inter-Med", 12, BONE, lead=18)
text(x, 360, "NEVER", "Mono-Semi", 8, "#E86A6A", cs=1.6)
wrap(x, 382, "revolutionary, seamless, cutting-edge, disrupt, world-class, next-generation, effortless, robust, powerful", 400, "Inter", 11, BONE, lead=17, alpha=0.85)
frame(M, 400, 400, 70, SAP, 10, 0.7, 0.5)
centered_lines(M, 400, 400, 70, ["Punctuation rule: no em dashes. Use a period or a comma.", "Sentence case. Numbers with units in mono."], "Inter", 10.5, BONE, lead=17, align="center")

# ============================ 15. TAGLINES ============================
new()
kicker(M, 56, "04  Type and voice")
title("Taglines", top=100)
tags = [("Descriptor", "Edge-AI silicon that listens to plants.", "Silicio de IA en el borde que escucha a las plantas.", "Formal, grants, meta descriptions."),
        ("Primary spoken line", "We listen to what plants can’t say.", "Escuchamos lo que las plantas no pueden decir.", "The warm one. Hero, decks, conversation."),
        ("Alternate: benefit", "Hearing drought before it shows.", "Escuchar la sequía antes de que se note.", "Sharper, for technical readers."),
        ("Alternate: mysterious", "The plant speaks first.", "La planta habla primero.", "Use sparingly, editorial pieces.")]
t = 140
for i, (k, en, es, use) in enumerate(tags):
    hl = i == 1
    rect(M, t, 848, 62, CANOPY if hl else BONE2, 12)
    text(M + 20, t + 22, k.upper(), "Mono-Med", 7.4, (AMBER if hl else AMBER_DEEP), cs=1.3)
    text(M + 20, t + 46, en, "SG-Bold", 17, BONE if hl else CANOPY)
    text(M + 400, t + 26, es, "Inter", 9.6, SAP if hl else GREY)
    text(M + 400, t + 44, use, "Inter", 9, SAP if hl else SAGE, alpha=0.9)
    t += 72
wrap(M, 440, "Do not publish the internal essence line (“a voice too quiet to hear, and the instrument built to hear it”). It is a design touchstone, not a motto.", 700, "Inter", 9.6, GREY, lead=14)
wrap(M, 470, "Current homepage headline: “Auselia is listening...”. It plays on the name and on being early.", 700, "Inter", 9.6, SAGE, lead=14)

# ============================ 16. VOICE IN PRACTICE ============================
new()
kicker(M, 56, "04  Type and voice")
title("Voice in practice", top=100)
ex = [("Our revolutionary platform seamlessly detects drought stress.", "A field node that hears drought stress before it shows.", "Says what it does, with a verb, and no banned words."),
      ("Powerful AI-driven insights for growers!", "Right now it is listening to one plant, named Hope.", "Honest about the stage. Calm, not excited."),
      ("Warning!!! Critical failure detected in plot 8.", "Cuartel 8: Critical. Soil moisture 14%, falling since Tuesday.", "Label plus shape plus the number. No alarm."),
      ("No data available.", "No reading yet. Waiting for the next upload.", "Says what happens next.")]
t = 138
text(M + 8, t - 6, "INSTEAD OF", "Mono-Med", 7.4, S_CRIT, cs=1.4); text(M + 440, t - 6, "WE WRITE", "Mono-Med", 7.4, SAGE, cs=1.4)
for bad, good, why in ex:
    rect(M, t, 420, 66, BONE2, 10); rect(M + 434, t, 414, 66, CANOPY, 10)
    stroke(S_CRIT, 1.6); c.line(M + 396, Y(t + 12), M + 408, Y(t + 24)); c.line(M + 408, Y(t + 12), M + 396, Y(t + 24))
    wrap(M + 16, t + 26, bad, 360, "Inter", 10.5, GREY, lead=14)
    wrap(M + 450, t + 26, good, 380, "Inter-Med", 10.5, BONE, lead=14)
    text(M + 450, t + 58, why, "Inter", 8, SAP, alpha=0.9)
    t += 76
text(M, 456, "Spanish status words: Normal, Elevado, Crítico, Sin datos. Same tone in both languages, not a literal translation.", "Inter", 9.4, GREY)

# ============================ 17. IMAGERY ============================
new()
kicker(M, 56, "05  Imagery, motion, data")
title("The plant", top=100)
lede("The big illustration is one flat, calm plant in sage. It grows from the bottom edge of the page, anchored to the right, and never competes with the headline.", top=128, w=520)
rect(M, 190, 270, 270, BONE, 14); frame(M, 190, 270, 270, CANOPY, 14, 0.6, 0.2); img("plant_sage.png", M + 20, 210, 230, 250, "s")
rect(M + 288, 190, 270, 270, FOREST, 14); img("plant_sap.png", M + 308, 210, 230, 250, "s")
text(M, 478, "On light: sage", "Inter-Semi", 9.4, CANOPY); text(M + 288, 478, "On dark: sap", "Inter-Semi", 9.4, CANOPY)
rx = M + 590
text(rx, 200, "Rules", "SG-Bold", 15, CANOPY)
rl = ["Flat shapes. No gradients, no realistic leaves, no botanical illustration.", "Sage on light, sap on dark, at about 80% opacity.", "Amber appears only as the signal node and rings, never as decoration.",
      "Photography, when we use it: real fields, real light, no stock handshakes."]
yy = 224
for r_ in rl:
    fill(AMBER); c.circle(rx + 4, Y(yy - 3), 2.4, stroke=0, fill=1)
    yy = wrap(rx + 16, yy, r_, 240, "Inter", 9.6, INK, lead=13.5) + 8

# ============================ 18. MOTION ============================
new(dark=True)
kicker(M, 56, "05  Imagery, motion, data", SAP)
title("The signal rings", dark=True, top=100)
wrap(M, 130, "Cavitation is an occasional event, so the animation is too. A small amber node on the stem sends out a short burst of three thin rings, then goes quiet.", 560, "Inter", 12, BONE, lead=19, alpha=0.9)
# timeline
tx, tw_, tt = M, 560, 232
rect(tx, tt, tw_, 86, CANOPY, 12)
scale_x = (tw_ - 40) / 11.0
for i, (d, col) in enumerate([(0.0, AMBER), (0.7, AMBER), (1.6, AMBER)]):
    x0 = tx + 20 + d * scale_x
    rect(x0, tt + 22 + i * 15, 2.4 * scale_x, 9, mix(col, CANOPY, 0.85 - 0.12 * i), 4.5)
    text(x0 - 6, tt + 30 + i * 15, "", "Mono", 6, SAP)
for s_ in range(0, 12, 2):
    text(tx + 20 + s_ * scale_x, tt + 78, f"{s_}s", "Mono", 6.6, SAP, "center")
text(tx + 20, tt + 14, "ONE 11 SECOND CYCLE", "Mono-Med", 6.6, SAP, cs=1.2)
text(tx + 20 + 2.6 * scale_x, tt + 70 - 8, "", "Mono", 6, SAP)
text(tx + 20 + 7.8 * scale_x, tt + 56, "quiet, about 7 s", "Inter", 8.6, SAP, "center")
text(tx + 20 + 2.0 * scale_x, tt + 78 - 22, "", "Mono", 6, SAP)
specs2 = [("Burst", "3 rings, offset 0 / 0.7 / 1.6 s, each fades over 2.4 s"), ("Then", "about 7 s of nothing before the next burst"), ("Rings", "1.5 px line, amber, start at 70% opacity, expand and fade"),
          ("Size", "small: about 35 px reach on a 220 px plant. A detail, not a show"), ("Reduced motion", "no animation, just the static amber node")]
yy = 350
for k, v in specs2:
    text(M, yy, k.upper(), "Mono-Semi", 7.4, AMBER, cs=1.2)
    text(M + 110, yy, v, "Inter", 10, BONE, alpha=0.92)
    yy += 24
# plant with node and rings
img("plant_sap.png", 640, 100, 300, 400, "s")
nx = 640 + (292 / 512) * 300 * (300 / 300); ny = 100 + 400 - 300 + (130 / 512) * 300  # plant image is 800x800 square drawn to 300 x 400 bottom-anchored
for r_, a_ in [(9, 0.7), (18, 0.4), (30, 0.2)]:
    stroke(AMBER, 1.1, a_); c.circle(nx, Y(ny), r_, stroke=1, fill=0)
fill(AMBER); c.circle(nx, Y(ny), 3.6, stroke=0, fill=1)

# ============================ 19. DATA VIZ + MAP ============================
new()
kicker(M, 56, "05  Imagery, motion, data")
title("Charts and the map", top=100)
# chart
cx0, cy0, cw_, ch_ = M, 150, 400, 190
rect(cx0, cy0, cw_, ch_, BONE2, 12)
text(cx0 + 18, cy0 + 24, "SOIL MOISTURE  /  CUARTEL 5", "Mono-Med", 7.4, SAGE, cs=1.2)
import random
rnd = random.Random(7)
data = [58 - i * 0.55 + rnd.uniform(-1.2, 1.2) for i in range(24)]
gx0, gx1, gy0, gy1 = cx0 + 44, cx0 + cw_ - 40, cy0 + 44, cy0 + ch_ - 30
lo, hi = 30, 60
for v in (30, 40, 50, 60):
    yv = gy1 - (v - lo) / (hi - lo) * (gy1 - gy0)
    stroke(CANOPY, 0.5, 0.14); c.line(gx0, Y(yv), gx1, Y(yv)); text(gx0 - 8, yv + 2.5, str(v), "Inter", 7.4, SAGE, "right")
pts = [(gx0 + i / 23 * (gx1 - gx0), gy1 - (d - lo) / (hi - lo) * (gy1 - gy0)) for i, d in enumerate(data)]
stroke(CANOPY, 1.8); p = c.beginPath(); p.moveTo(pts[0][0], Y(pts[0][1]))
for q in pts[1:]: p.lineTo(q[0], Y(q[1]))
c.setLineJoin(1); c.drawPath(p, stroke=1, fill=0)
fill(BONE2); c.circle(pts[-1][0], Y(pts[-1][1]), 6.5, stroke=0, fill=1); fill(AMBER); c.circle(pts[-1][0], Y(pts[-1][1]), 4, stroke=0, fill=1)
text(pts[-1][0] + 8, pts[-1][1] + 3, f"{data[-1]:.0f}%", "Mono-Semi", 8, INK)
for i_, lab in [(0, "01:11 AM"), (12, "09:11 AM"), (23, "07:11 PM")]:
    text(gx0 + i_ / 23 * (gx1 - gx0), gy1 + 16, lab, "Inter", 7.2, SAGE, "center")
rl = ["Line is canopy (accent). Amber marks only the latest value, with a light ring.", "Grid lines at 14% opacity, labels in sage. Nothing decorative.", "Every status needs its shape and its word. A chart with fewer than 2 points says so in words."]
yy = 362
for r_ in rl:
    fill(AMBER); c.circle(cx0 + 4, Y(yy - 3), 2.4, stroke=0, fill=1)
    yy = wrap(cx0 + 16, yy, r_, 380, "Inter", 9.4, INK, lead=13) + 6
# map
mx0, mw = M + 440, 408
rect(mx0, 130, mw, 340, BONE2, 14)
statuses = {2: "warning", 9: "warning", 13: "warning", 8: "critical"}
draw_map(mx0 + 10, 142, mw - 20, 290, statuses, BONE2, CANOPY, selected=5)
px = mx0 + 18
for kind in ["good", "warning", "critical", "idle"]:
    status_icon(kind, px + 4, 448, 3.4, STATUS[kind][0]); text(px + 12, 451, STATUS[kind][1].upper(), "Mono", 6.6, INK, cs=0.6); px += 92
text(mx0 + 18, 464, "Survey geometry is real. Plot names and readings are simulated for the demo.", "Inter", 7.4, GREY) if False else None

# ============================ 20. INTERFACE ============================
new()
kicker(M, 56, "05  Imagery, motion, data")
title("The interface", top=100)
# dark mock dashboard
dx, dt, dw, dh = M, 132, 610, 350
rect(dx, dt, dw, dh, FOREST, 16)
img("auselia-mark-reversed.png", dx + 18, dt + 12, 22, 22)
text(dx + 46, dt + 28, "AUS", "SG-Bold", 11.5, BONE, cs=0.3); text(dx + 46 + stringWidth("AUS", "SG-Bold", 11.5) + 1, dt + 28, "ELIA", "SG-Bold", 11.5, AMBER, cs=0.3)
text(dx + 106, dt + 28, "·  Campo Verde", "Inter", 9, SAP)
for i, lab in enumerate(["ES", "EN"]):
    rect(dx + dw - 132 + i * 26, dt + 14, 24, 18, SAP if i else CANOPY, 6); text(dx + dw - 120 + i * 26, dt + 26.5, lab, "Mono-Semi", 7, FOREST if i else SAP, "center")
rect(dx + 16, dt + 48, dw - 32, dh - 64, CANOPY, 12)
text(dx + 30, dt + 68, "14 cuarteles monitored  ·  72.5 ha  ·  11 nominal  ·  3 elevated  ·  0 critical", "Inter", 7.6, SAP)
rect(dx + 30, dt + 80, 350, dh - 112, FOREST, 10)
draw_map(dx + 36, dt + 84, 338, dh - 122, {2: "warning", 9: "warning", 13: "warning"}, FOREST, BONE, selected=5)
px_ = dx + 400
rect(px_, dt + 80, 180, dh - 112, FOREST, 10)
text(px_ + 14, dt + 102, "Cuartel 5", "SG-Bold", 12, BONE)
w_ = pill(px_ + 110, dt + 90, "good", base=FOREST)
text(px_ + 14, dt + 118, "Kee Crisp  ·  7.75 ha", "Inter", 7.6, SAP)
for i, lab in enumerate(["Acoustic", "Environment", "Events"]):
    text(px_ + 14 + i * 56, dt + 140, lab, "Inter-Semi", 6.8, BONE if i == 1 else SAP)
stroke(AMBER, 1.2); c.line(px_ + 14 + 56, Y(dt + 145), px_ + 14 + 56 + 44, Y(dt + 145))
tl = [("SOIL MOISTURE", "52%"), ("ROOT TEMP", "20.4°C"), ("AIR TEMP", "25.5°C"), ("HUMIDITY", "57%")]
for i, (k, v) in enumerate(tl):
    tx = px_ + 14 + (i % 2) * 78; ty = dt + 158 + (i // 2) * 42
    rect(tx, ty, 72, 36, CANOPY, 6); text(tx + 7, ty + 13, k, "Mono", 5.4, SAP, cs=0.4); text(tx + 7, ty + 28, v, "Mono-Semi", 9, BONE)
# tokens
rx = M + 640
text(rx, 150, "Tokens the app uses", "SG-Bold", 14, CANOPY)
toks = [("bg", "Bone / Forest"), ("surface", "Bone 2 / Canopy"), ("ink", "Ink / Bone"), ("ink2 (secondary)", "Sage / Sap"), ("accent", "Canopy / Sap"), ("border", "14% ink or bone")]
yy = 176
for k, v in toks:
    text(rx, yy, k, "Mono-Med", 8, CANOPY); text(rx + 208, yy, v, "Inter", 8.8, GREY, "right")
    stroke(CANOPY, 0.5, 0.15); c.line(rx, Y(yy + 8), rx + 208, Y(yy + 8)); yy += 26
wrap(rx, 350, "Light and dark are both first-class. Light is bone with canopy green, dark is forest with sap. Amber stays the same in both.", 208, "Inter", 9.4, GREY, lead=13.5)
wrap(rx, 414, "Cursor is a pointer on every button. Motion respects reduced-motion settings.", 208, "Inter", 9.4, GREY, lead=13.5)

# ============================ 21. WEBSITE + ICON ============================
new()
kicker(M, 56, "06  In use")
title("The website and app icon", top=100)
# website mock (light)
wx, wt, ww, wh = M, 132, 560, 350
rect(wx, wt, ww, wh, BONE, 14); frame(wx, wt, ww, wh, CANOPY, 14, 0.7, 0.25)
img("auselia-mark-color.png", wx + 24, wt + 20, 26, 26)
text(wx + 56, wt + 39, "AUSELIA", "SG-Bold", 12.5, CANOPY, cs=0.3)
frame(wx + ww - 168, wt + 24, 60, 20, CANOPY, 10, 0.6, 0.3); text(wx + ww - 138, wt + 37, "DARK", "Mono", 6.6, SAGE, "center", cs=0.6)
frame(wx + ww - 100, wt + 24, 78, 20, CANOPY, 10, 0.6, 0.3); text(wx + ww - 61, wt + 37, "PARTNER SIGN IN", "Mono", 6, SAGE, "center", cs=0.4)
text(wx + 60, wt + 118, "EDGE-AI SILICON THAT LISTENS TO PLANTS", "Mono", 6.6, SAGE, cs=1.6)
text(wx + 60, wt + 150, "Auselia is listening...", "SG-Bold", 30, INK, cs=-0.6)
wrap(wx + 60, wt + 176, "A field node that hears the quiet acoustic signs of drought stress in a plant's xylem, long before it shows by looking.", 300, "Inter", 8.8, SAGE, lead=13)
rect(wx + 60, wt + 218, 118, 26, AMBER, 7); text(wx + 119, wt + 235, "Explore the live demo", "Inter-Semi", 8.4, FOREST, "center")
frame(wx + 186, wt + 218, 92, 26, CANOPY, 7, 0.6, 0.3); text(wx + 232, wt + 235, "Partner sign in", "Inter-Med", 8.4, INK, "center")
img("plant_sage.png", wx + ww - 210, wt + 130, 190, 220, "s")
fill(AMBER); c.circle(wx + ww - 210 + (292 / 512) * 190, Y(wt + 130 + 220 - 190 + (130 / 512) * 190), 2.6, stroke=0, fill=1)
# icons
rx = M + 596
text(rx, 150, "App icon and favicon", "SG-Bold", 14, CANOPY)
xi = rx
for sz in [88, 56, 32, 16]:
    img("auselia-app-icon.png", xi, 178 + (88 - sz) / 1, sz, sz)
    text(xi + sz / 2, 290, f"{sz}", "Mono", 7, SAGE, "center"); xi += sz + 18
wrap(rx, 316, "The tile is the small-size version. Forest ground, bone stem, amber node and arcs. It stays legible where the full mark would blur.", 252, "Inter", 9.4, GREY, lead=13.5)
wrap(rx, 372, "The website header always uses the full mark with the wordmark, in the light or dark treatment that matches the theme.", 252, "Inter", 9.4, GREY, lead=13.5)

# ============================ 22. FIELD + HARDWARE ============================
new(dark=True)
kicker(M, 56, "06  In use", SAP)
title("In the field and on the silicon", dark=True, top=100)
# field card
rect(M, 140, 400, 250, CANOPY, 16)
img("auselia-mark-reversed.png", M + 22, 156, 30, 30)
text(M + 60, 176, "AUSELIA", "SG-Bold", 13, BONE, cs=0.3)
text(M + 22, 226, "CUARTEL 5  /  ROW 12", "Mono-Med", 8, SAP, cs=1.4)
text(M + 22, 268, "Nominal", "SG-Bold", 34, BONE)
status_icon("good", M + 232, 256, 9, SAP)
text(M + 22, 300, "Soil moisture 52%   Root temp 20.4°C", "Mono", 10, BONE)
rect(M + 22, 326, 120, 30, AMBER, 8); text(M + 82, 345, "Read details", "Inter-Semi", 10, FOREST, "center")
text(M, 412, "Field card: forest ground, bone text, amber accent. Highest contrast, survives glare.", "Inter", 9.4, SAP)
# chip
cx, cy, cr = M + 640, 232, 108
fill(FOREST); stroke(SAP, 1.2, 0.6)
c.circle(cx, Y(cy), cr, stroke=1, fill=0)
for r_ in [cr - 10]:
    stroke(SAP, 0.6, 0.3); c.circle(cx, Y(cy), r_, stroke=1, fill=0)
img("auselia-mark-mono-amber.png", cx - 54, cy - 80, 108, 108)
text(cx, cy + 60, "AUSELIA  /  HOPE", "Mono-Med", 7.6, AMBER, "center", cs=1.6)
text(cx, cy + 140 + 0, "Chip silkscreen: one color, amber on forest.", "Inter", 9.4, SAP, "center")
wrap(M, 446, "Device label and PCB text use IBM Plex Mono, uppercase. Chips are named after virtues and missions, starting with Hope.", 700, "Inter", 9.4, SAP, lead=14)

# ============================ 23. SHIP CHECKLIST ============================
new()
kicker(M, 56, "06  In use")
title("Before you ship anything", top=100)
lede("Run this on every screen, slide, print or label. If one box is empty, fix it first.", top=128, w=520)
checks = ["I can see the living thing AND the instrument in it.", "Amber is 10% or less and only on an action, one key datum, or a stress state.", "No amber text on any light background.",
          "Body text is Ink on Bone or Bone on Forest.", "Every status has a color, a shape and a word.", "Field or outdoor use: forest ground, bone text, amber accent.",
          "Only Space Grotesk, Inter and IBM Plex Mono. No soft or script fonts.", "No banned words. No em dashes.", "The mark has its clear space and is not smaller than 24 px.", "Motion is small, occasional, and switches off for reduced-motion users."]
t = 164
for i, ch in enumerate(checks):
    x = M + (i % 2) * 432; y_ = t + (i // 2) * 56
    frame(x, y_, 14, 14, CANOPY, 3, 1.2)
    wrap(x + 26, y_ + 11, ch, 380, "Inter", 11, INK, lead=15)

# ============================ 24. QUICK REFERENCE ============================
new(dark=True)
kicker(M, 56, "07  Reference", SAP)
title("Quick reference", dark=True, top=100)
x = M
for col, nme in [(FOREST, "Forest"), (CANOPY, "Canopy"), (AMBER, "Amber"), (SAGE, "Sage"), (SAP, "Sap"), (BONE, "Bone"), (BONE2, "Bone 2"), (INK, "Ink")]:
    rect(x, 140, 96, 62, col, 8)
    if col in (FOREST, INK): frame(x, 140, 96, 62, SAP, 8, 0.6, 0.35)
    text(x + 8, 188, nme, "Inter-Semi", 8.4, FOREST if col in (AMBER, SAP, BONE, BONE2) else BONE)
    text(x + 8, 198, col, "Mono", 6.8, FOREST if col in (AMBER, SAP, BONE, BONE2) else BONE, alpha=0.85)
    x += 106
qc = [("Type", "Space Grotesk Bold for display. Inter for body. IBM Plex Mono for data and labels."),
      ("Mark", "Color on light, reversed on dark, tile below 24 px. Clear space is one node diameter."),
      ("Status", "Circle Nominal, triangle Elevated, diamond Critical, dash No data. Always with its word."),
      ("Voice", "Listen, hear, signal, node, field. No hype. No em dashes."),
      ("Say", "Edge-AI silicon that listens to plants.  We listen to what plants can’t say."),
      ("Motion", "Three amber rings, then about 7 quiet seconds. Off for reduced motion.")]
t = 236
for i, (k, v) in enumerate(qc):
    x = M + (i % 2) * 432; y_ = t + (i // 2) * 76
    text(x, y_, k.upper(), "Mono-Semi", 8, AMBER, cs=1.6)
    wrap(x, y_ + 20, v, 400, "Inter", 11, BONE, lead=16, alpha=0.92)

c.save()
print("pages:", page_no[0], "->", OUT)
