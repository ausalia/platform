"""Builds the Auselia logo analysis PDF from assets/ + metrics.json (see analyze.py)."""
import json, os, datetime
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Patch
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.dirname(HERE)
BUILD = os.path.join(BRAND, "build")
A = os.path.join(BUILD, "analysis", "assets")
R = json.load(open(os.path.join(BUILD, "analysis", "metrics.json")))
OUT = os.path.join(BUILD, "Auselia-Logo-Analysis-Report.pdf")

for w in ["Regular", "Medium", "SemiBold", "Bold"]:
    pdfmetrics.registerFont(TTFont(f"P-{w}", os.path.join(BUILD, "fonts", f"Poppins-{w}.ttf")))
    font_manager.fontManager.addfont(os.path.join(BUILD, "fonts", f"Poppins-{w}.ttf"))
plt.rcParams["font.family"] = "Poppins"

PW, PH = 595.28, 841.89
LM, CW = 100, 395           # content column, like the sample
NAVY = (0.12, 0.11, 0.23)
MUTED = (0.42, 0.41, 0.50)
BORDER = (0.79, 0.78, 0.87)
TEXT = (0.05, 0.05, 0.08)
CHIP_BG = (0.925, 0.918, 0.965)
RATING = {  # fill, border
    "Great": ((0.80, 1.00, 0.67), (0.45, 0.80, 0.40)),
    "Okay": ((1.00, 0.97, 0.72), (0.90, 0.82, 0.35)),
    "Weak": ((1.00, 0.85, 0.72), (0.90, 0.60, 0.35)),
    "Poor": ((1.00, 0.72, 0.72), (0.90, 0.40, 0.40)),
}
MPL = {"Great": "#C9FFAA", "Okay": "#FFF6B8", "Weak": "#FFD9B8", "Poor": "#FFB8B8"}

c = canvas.Canvas(OUT, pagesize=(PW, PH))
c.setTitle("Auselia Logo Analysis Report")
c.setAuthor("Auselia")

def y(top): return PH - top
def col(rgb): c.setFillColorRGB(*rgb)
def text(x, top, s, font="P-Regular", size=9, color=TEXT, align="left"):
    c.setFont(font, size); col(color)
    fn = {"left": c.drawString, "center": c.drawCentredString, "right": c.drawRightString}[align]
    fn(x, y(top), s)
def wrap(x, top, s, w, font="P-Regular", size=9, color=TEXT, lead=None, bullet=False):
    lead = lead or size * 1.55
    lines = simpleSplit(s, font, size, w - (8 if bullet else 0))
    for i, ln in enumerate(lines):
        if bullet and i == 0:
            text(x, top, "•", font, size, color)
        text(x + (8 if bullet else 0), top, ln, font, size, color)
        top += lead
    return top
def wrap_h(s, w, size=9, font="P-Regular", lead=None, bullet=False):
    lead = lead or size * 1.55
    return len(simpleSplit(s, font, size, w - (8 if bullet else 0))) * lead
def card(x, top, w, h, title=None, center=False, size=8.6):
    c.setStrokeColorRGB(*BORDER); c.setLineWidth(0.9); c.setFillColorRGB(1, 1, 1)
    c.roundRect(x, y(top + h), w, h, 8, stroke=1, fill=1)
    if title:
        text(x + (w / 2 if center else 13), top + 17, title, "P-SemiBold", size, NAVY if not center else NAVY, "center" if center else "left")
def heading(s, sub=None):
    text(LM, 62, s, "P-SemiBold", 24, NAVY)
    top = 78
    if sub:
        top = wrap(LM, 84, sub, CW, size=8.2, color=MUTED, lead=12.5) - 2
    return top + 8
def chip(cx, top, label, kind, h=14, size=6.6):
    fill, brd = RATING[kind]
    w = stringWidth(label, "P-Medium", size) + 18
    c.setFillColorRGB(*fill); c.setStrokeColorRGB(*brd); c.setLineWidth(0.9)
    c.roundRect(cx - w / 2, y(top + h), w, h, h / 2, stroke=1, fill=1)
    text(cx, top + h - 4.6, label, "P-Medium", size, TEXT, "center")
def pill(x, top, label, size=7.2):
    w = stringWidth(label, "P-SemiBold", size) + 20
    c.setFillColorRGB(*CHIP_BG); c.roundRect(x, y(top + 16), w, 16, 8, stroke=0, fill=1)
    text(x + 10, top + 11.2, label, "P-SemiBold", size, NAVY)
    return x + w + 8
def img(path, x, top, w, h):
    c.drawImage(ImageReader(path), x, y(top + h), width=w, height=h, mask="auto", preserveAspectRatio=True, anchor="c")
def dotted(x1, x2, top):
    c.setStrokeColorRGB(0.72, 0.72, 0.78); c.setDash(1, 2); c.setLineWidth(0.7)
    c.line(x1, y(top), x2, y(top)); c.setDash()
def legend_chip(x, top, label, fill_rgb, brd_rgb):
    c.setFillColorRGB(*fill_rgb); c.setStrokeColorRGB(*brd_rgb); c.setLineWidth(0.9)
    c.roundRect(x, y(top + 9), 16, 9, 4.5, stroke=1, fill=1)
    text(x + 21, top + 7.2, label, "P-Regular", 6.6, TEXT)
    return x + 21 + stringWidth(label, "P-Regular", 6.6) + 12
def newpage():
    c.showPage()

fmt = lambda v, d=1: f"{v:.{d}f}"
now = datetime.datetime.now()
date_s = now.strftime("%B ") + str(now.day) + now.strftime(", %Y")

# ============================ 1. Cover ============================
text(PW / 2, 158, "Logo Analysis Report", "P-Bold", 24, (0, 0, 0), "center")
text(PW / 2, 180, "Auselia mark, variant D", "P-Regular", 9.5, MUTED, "center")
img(os.path.join(A, "tight.png"), PW / 2 - 105, 250, 210, 240)
text(40, 787, f"Created on {date_s}", "P-Regular", 9)
newpage()

# ============================ 2. Summary ============================
text(LM, 62, "Logo Summary", "P-SemiBold", 24, NAVY)
top = 84
card(LM, top, CW, 58, "Brand Personality")
x = LM + 13
for t in ["Precise", "Curious", "Calm", "Quietly bold"]:
    x = pill(x, top + 30, t)
top += 58 + 14

bul_size = 8.4
def bullet_card(x, top, w, title, items):
    hh = 30 + sum(wrap_h(s, w - 26, bul_size, bullet=True) for s in items) + 12
    card(x, top, w, hh, title)
    t = top + 39
    for s in items:
        t = wrap(x + 13, t, s, w - 26, size=bul_size, bullet=True)
    return hh

hh = bullet_card(LM, top, CW, "Estimated Target Market", [
    "Fruit and wine growers in Chile (blueberries, cherries, grapes)",
    "Precision-irrigation and agtech companies",
    "Plant-science research groups and universities",
    "Water-management and sustainability programs",
    "Grant reviewers and agtech investors",
])
top += hh + 14
hh = bullet_card(LM, top, CW, "Possible Associations", [
    "A seedling with a broadcast or Wi-Fi symbol",
    "Audio levels or a speaker icon",
    "A plant that is speaking, or being heard",
])
top += hh + 14

cw2 = (CW - 14) / 2
strengths = [
    "The amber node with arcs tells the story at a glance: a plant being heard.",
    "Two brand colors and flat shapes only, so it reproduces on silicon, stamps and screens.",
    f"Colorblind-safe: worst simulated color change is {fmt(max(x['change_pct'] for x in R['colorblind']), 0)}%, and amber stays clearly apart from green.",
    f"Strong from 128 to 64 px (similarity {fmt(R['size'][0]['score']*100,0)} to {fmt(R['size'][2]['score']*100,0)}%).",
]
b = R["balance"]; sl = R["slices"]; c3 = R["containers"][-1]
weak = [
    "The arcs read as a Wi-Fi or broadcast symbol and could suggest a connectivity company.",
    f"Thin arcs are the first detail lost: similarity falls to {fmt(R['size'][-1]['score']*100,0)}% at 16 px.",
    f"Weight is uneven: mass sits {fmt(abs(b['x_off_pct']),1)}% left of center and {fmt(sl['tr'],0)}% of edge detail is in the top-right quadrant.",
    f"Portrait shape fills wide containers poorly ({fmt(c3['fill']*100,0)}% at 3:1); it needs a horizontal lockup with the wordmark.",
    "The seedling is a common shape. The ownable part is the node and arcs.",
]
h1 = 30 + sum(wrap_h(s, cw2 - 26, bul_size, bullet=True) for s in strengths) + 12
h2 = 30 + sum(wrap_h(s, cw2 - 26, bul_size, bullet=True) for s in weak) + 12
hh = max(h1, h2)
for xx, title, items in [(LM, "Strengths", strengths), (LM + cw2 + 14, "Potential Weaknesses", weak)]:
    card(xx, top, cw2, hh, title)
    t = top + 39
    for s in items:
        t = wrap(xx + 13, t, s, cw2 - 26, size=bul_size, bullet=True)
newpage()

# ============================ 3. Balance ============================
top = heading("Balance", "Visual balance ensures stability and appeal. We analyze how elements are distributed to find the logo's visual center of mass. Ideally, it should be close to the geometric center.")
c.setStrokeColorRGB(0, 0, 0); c.setFillColorRGB(1, 1, 1); c.setLineWidth(1)
c.circle(LM + 6, y(top + 6), 4.5, stroke=1, fill=1)
text(LM + 20, top + 8, "Center of Image", "P-SemiBold", 8.6, (0, 0, 0))
text(LM + 20, top + 20, "The exact geometric center point of the image container.", "P-Regular", 7.6, (0.25, 0.25, 0.3))
top += 36
c.setFillColorRGB(0.87, 0.15, 0.1); c.setStrokeColorRGB(0, 0, 0)
c.circle(LM + 6, y(top + 6), 4.5, stroke=1, fill=1)
text(LM + 20, top + 8, "Visual Center of Mass", "P-SemiBold", 8.6, (0, 0, 0))
text(LM + 20, top + 20, "The perceived center based on visual weight distribution.", "P-Regular", 7.6, (0.25, 0.25, 0.3))
top += 42

# figure
S = 1000
fig = Image.new("RGB", (S, S), (255, 255, 255))
grey = Image.open(os.path.join(A, "balance_grey.png"))
sc = (S * 0.62) / grey.height
g2 = grey.resize((int(grey.width * sc), int(grey.height * sc)), Image.LANCZOS)
ox, oy = (S - g2.width) // 2, (S - g2.height) // 2
fig.paste(g2, (ox, oy))
mx = ox + R["balance"]["cx"] * sc; my = oy + R["balance"]["cy"] * sc
d = ImageDraw.Draw(fig)
d.line([(0, my), (S, my)], fill=(220, 40, 30), width=3)
d.line([(mx, 0), (mx, S)], fill=(220, 40, 30), width=3)
d.ellipse([S / 2 - 16, S / 2 - 16, S / 2 + 16, S / 2 + 16], fill=(255, 255, 255), outline=(0, 0, 0), width=4)
d.ellipse([mx - 18, my - 18, mx + 18, my + 18], fill=(222, 38, 26), outline=(0, 0, 0), width=4)
fig.save(os.path.join(A, "balance_fig.png"))
fh = 300
card(LM, top, CW, fh + 30, "Center of Mass", center=True)
img(os.path.join(A, "balance_fig.png"), LM + (CW - fh) / 2, top + 26, fh, fh)
top += fh + 30 + 16
card(LM, top, CW, 130, "CENTER OFFSET", center=True, size=7.6)
wrap(LM + 20, top + 38, "This shows how far the visual center of mass deviates from the geometric center of the logo.", CW - 40, size=7.6, lead=11.5, color=(0.25, 0.25, 0.3))
xo, yo = R["balance"]["x_off_pct"], R["balance"]["y_off_pct"]
c.setStrokeColorRGB(0.8, 0.8, 0.85); c.line(LM + CW / 2, y(top + 72), LM + CW / 2, y(top + 112))
text(LM + CW * 0.25, top + 92, f"{abs(xo):.1f}%", "P-Bold", 26, (0, 0, 0), "center")
text(LM + CW * 0.25, top + 108, "x-axis offset (" + ("left" if xo < 0 else "right") + ")", "P-Regular", 7.6, (0.3, 0.3, 0.35), "center")
text(LM + CW * 0.75, top + 92, f"{abs(yo):.1f}%", "P-Bold", 26, (0, 0, 0), "center")
text(LM + CW * 0.75, top + 108, "y-axis offset (" + ("up" if yo < 0 else "down") + ")", "P-Regular", 7.6, (0.3, 0.3, 0.35), "center")
newpage()

# ---------- chart helper ----------
def band_chart(path, xs, ys, bands, xlabel, ylabel, title, xlim, ylim, dotted_y=None, invert_x=False, size=(6.4, 3.9), extra=None, logy=False):
    fig, ax = plt.subplots(figsize=size, dpi=220)
    for lo, hi, name in bands:
        ax.axhspan(lo, hi, color=MPL[name], zorder=0)
    if dotted_y is not None:
        ax.axhline(dotted_y, color="black", lw=0.7, ls=(0, (2, 2)), zorder=1)
    ax.grid(color="white", alpha=0.6, lw=0.5)
    ax.plot(xs, ys, color="black", lw=1.1, zorder=3)
    ax.scatter(xs, ys, color="black", s=10, zorder=4)
    if extra:
        for ex in extra:
            ax.plot(ex[0], ex[1], color=ex[2], lw=1.1, ls=ex[3], zorder=3)
            ax.scatter(ex[0], ex[1], color=ex[2], s=10, zorder=4)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    if logy:
        ax.set_yscale('log'); ax.set_yticks([1, 2, 3, 5, 10, 15]); ax.set_yticklabels(['1', '2', '3', '5', '10', '15']); ax.minorticks_off()
    if invert_x: ax.invert_xaxis()
    ax.set_xlabel(xlabel, fontsize=6); ax.set_ylabel(ylabel, fontsize=6)
    ax.tick_params(labelsize=5.5, length=2)
    for s in ax.spines.values(): s.set_linewidth(0.6)
    ax.set_title(title, fontsize=8.6, fontweight="semibold", pad=34)
    handles = [Patch(facecolor=MPL[n], edgecolor="black", linewidth=0.5, label=n) for n in ["Great", "Okay", "Weak", "Poor"]]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=4, frameon=False, fontsize=6.4, handlelength=1.6, columnspacing=1.4)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.05, facecolor="white")
    plt.close(fig)

def thumb_card(x, top, w, h, title, image, big, sub, rating, imgh=70, extra=None, subtitle=None):
    card(x, top, w, h)
    text(x + 13, top + 16, title, "P-SemiBold", 8.4, NAVY)
    if subtitle:
        text(x + w - 13, top + 16, subtitle, "P-Regular", 6.4, MUTED, "right")
    img(image, x + 8, top + 24, w - 16, imgh)
    div = top + 24 + imgh + 8
    dotted(x, x + w, div)
    text(x + w / 2, div + 22, big, "P-Bold", 12, (0, 0, 0), "center")
    text(x + w / 2, div + 34, sub, "P-Regular", 7.4, TEXT, "center")
    chip(x + w / 2, div + 42, rating, rating)
    if extra:
        text(x + w / 2, div + 72, extra, "P-Regular", 6.4, MUTED, "center")

# ============================ 4. Containers ============================
top = heading("Containers", "See how your logo scales inside containers of various dimensions. A logo that fills space efficiently is often more adaptable.")
cont = R["containers"]
band_chart(os.path.join(A, "chart_containers.png"),
           [r["ratio"] for r in cont], [r["fill"] for r in cont],
           [(0.66, 1.0, "Great"), (0.40, 0.66, "Okay"), (0.20, 0.40, "Weak"), (0.05, 0.20, "Poor")],
           "Aspect Ratio", "Fill Percentage", "Fill Percentage vs. Aspect Ratio", (0, 3.5), (0.05, 1.0), dotted_y=0.66)
card(LM, top, CW, 232)
img(os.path.join(A, "chart_containers.png"), LM + 10, top + 6, CW - 20, 220)
top += 232 + 16
cwid = (CW - 20) / 3
for i, r in enumerate(cont):
    xx = LM + (i % 3) * (cwid + 10); tt = top + (i // 3) * 164
    thumb_card(xx, tt, cwid, 154, r["label"], os.path.join(A, f"cont_{r['label'].replace(' ', '').replace(':', '_')}.png"),
               f"{r['fill']*100:.1f}%", "Fill Percentage", r["rating"], imgh=62)
newpage()

# ============================ 5. Size ============================
top = heading("Size", "See how small you can make your logo without losing too much detail. Sizes are the longest side of the mark.")
sz = R["size"]
band_chart(os.path.join(A, "chart_size.png"),
           [s["n"] for s in sz], [s["score"] for s in sz],
           [(0.90, 1.0, "Great"), (0.75, 0.90, "Okay"), (0.60, 0.75, "Weak"), (0.55, 0.60, "Poor")],
           "Logo Size (pixels, longest side)", "Similarity Score", "Similarity Score vs. Logo Size", (10, 135), (0.60, 1.0), dotted_y=0.90, invert_x=True)
card(LM, top, CW, 232)
img(os.path.join(A, "chart_size.png"), LM + 10, top + 6, CW - 20, 220)
top += 232 + 16
for i, s in enumerate(sz):
    xx = LM + (i % 3) * (cwid + 10); tt = top + (i // 3) * 164
    im = Image.open(os.path.join(A, f"size_{s['n']}.png"))
    disp = 160
    sc = disp / max(im.size)
    up = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.NEAREST if s["n"] <= 32 else Image.BICUBIC)
    up.save(os.path.join(A, f"size_disp_{s['n']}.png"))
    thumb_card(xx, tt, cwid, 154, f"{s['w']}x{s['h']}px", os.path.join(A, f"size_disp_{s['n']}.png"),
               f"{s['score']*100:.1f}%", "Similarity Score", s["rating"], imgh=62)
newpage()

# ============================ 6. Contours ============================
top = heading("Contours", "Analyze the complexity of your logo's silhouette through its contours. Simpler contours improve readability, especially at smaller sizes.")
card(LM, top, CW, 300, "Relative Contour Complexity", center=True)
xx = LM + 14
present = {ci["class"] for ci in R["contours"]}
for k, rgb in [("Simple", (0.33, 0.9, 0.23)), ("Moderate", (1.0, 0.69, 0.13)), ("Complex", (0.93, 0.25, 0.25))]:
    if k in present:
        xx = legend_chip(xx, top + 30, k, rgb, tuple(v * 0.6 for v in rgb))
img(os.path.join(A, "contours.png"), LM + 40, top + 46, CW - 80, 244)
top += 300 + 8
top = wrap(LM, top + 10, "*Complexity is the ratio of contour length to area. Contours are scored relative to each other, so logos with a single contour are always rated \"Simple\". Here the two thin arcs score highest because they are long and narrow.", CW, size=6.4, color=MUTED, lead=9.5) + 8
# donut
tot = sum(ci["perimeter"] for ci in R["contours"])
shares = {}
for ci in R["contours"]:
    shares[ci["class"]] = shares.get(ci["class"], 0) + ci["perimeter"] / tot * 100
order = [k for k in ["Simple", "Moderate", "Complex"] if k in shares]
cmap = {"Simple": "#55E63A", "Moderate": "#FFB020", "Complex": "#EE4040"}
fig, ax = plt.subplots(figsize=(3, 3), dpi=220)
ax.pie([shares[k] for k in order], colors=[cmap[k] for k in order], startangle=90, counterclock=False,
       wedgeprops=dict(width=0.32, edgecolor="white", linewidth=1))
fig.savefig(os.path.join(A, "donut.png"), bbox_inches="tight", pad_inches=0.02, transparent=True); plt.close(fig)
card(LM, top, CW, 260, "Contour Complexity Distribution", center=True)
xx = LM + 14
for k in order:
    rgb = {"Simple": (0.33, 0.9, 0.23), "Moderate": (1.0, 0.69, 0.13), "Complex": (0.93, 0.25, 0.25)}[k]
    xx = legend_chip(xx, top + 30, f"{k} ({shares[k]:.1f}% of outline length)", rgb, tuple(v * 0.6 for v in rgb))
img(os.path.join(A, "donut.png"), LM + 110, top + 50, 175, 175)
newpage()

# ============================ 7. Slices ============================
top = heading("Slices", "See the proportion of detail in each quadrant of your logo. Logos with evenly distributed detail can often feel more balanced and harmonious.")
card(LM, top, CW, 330, "Visual Complexity Per Quadrant", center=True)
oim = Image.open(os.path.join(A, "slices_outline.png"))
ih = 262; iw = ih * oim.width / oim.height
img(os.path.join(A, "slices_outline.png"), LM + (CW - iw) / 2, top + 40, iw, ih)
cx0, cy0 = LM + CW / 2, top + 40 + ih / 2
c.setStrokeColorRGB(0.55, 0.55, 0.6); c.setDash(2, 2); c.setLineWidth(0.6)
c.line(LM + 8, y(cy0), LM + CW - 8, y(cy0)); c.line(cx0, y(top + 34), cx0, y(top + 322)); c.setDash()
text(LM + 16, top + 50, f"{sl['tl']:.2f}%", "P-Regular", 9)
text(LM + CW - 16, top + 50, f"{sl['tr']:.2f}%", "P-Regular", 9, align="right")
text(LM + 16, top + 322, f"{sl['bl']:.2f}%", "P-Regular", 9)
text(LM + CW - 16, top + 322, f"{sl['br']:.2f}%", "P-Regular", 9, align="right")
top += 330 + 12
text(LM, top + 8, "It's often helpful for each quadrant of your logo to have recognizable characteristics.", "P-Regular", 7.4, MUTED)
top += 22
for i, (k, t) in enumerate([("tl", "Top Left"), ("tr", "Top Right"), ("bl", "Bottom Left"), ("br", "Bottom Right")]):
    xx = LM + (i % 2) * (cw2 + 14); tt = top + (i // 2) * 124
    card(xx, tt, cw2, 114, t)
    im = Image.open(os.path.join(A, f"slice_{k}.png"))
    ah = 76
    img(os.path.join(A, f"slice_{k}.png"), xx + 8, tt + 26, cw2 - 16, ah)
newpage()

# ============================ 8. Color ============================
top = heading("Color", "Get insight into your logo's color palette, color distribution, and color variations.")
for i, (t, f) in enumerate([("Original Color", "color_original"), ("Greyscale", "color_grey"), ("Black on White", "color_bw"), ("White on Black", "color_wb")]):
    xx = LM + (i % 2) * (cw2 + 14); tt = top + (i // 2) * 130
    card(xx, tt, cw2, 120, t)
    if f == "color_wb":
        c.setFillColorRGB(0, 0, 0); c.roundRect(xx + 1, y(tt + 120 - 1), cw2 - 2, 120 - 26 - 1, 6, stroke=0, fill=1)
        c.rect(xx + 1, y(tt + 26 + 8), cw2 - 2, 8, stroke=0, fill=1)
    img(os.path.join(A, f"{f}.png"), xx + 8, tt + 28, cw2 - 16, 86)
top += 260 + 4
card(LM, top, CW, 74, "Color Distribution")
text(LM + CW - 13, top + 17, "*Width of each color is proportional to its usage in the logo", "P-Regular", 6, MUTED, "right")
bx, bw, by = LM + 13, CW - 26, top + 30
xcur = bx
for name in ["Canopy", "Amber"]:
    wpart = bw * R["color_dist"][name] / 100
    hexc = R["palette"][name]
    c.setFillColorRGB(*[int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5)]); c.setStrokeColorRGB(0, 0, 0); c.setLineWidth(0.8)
    c.rect(xcur, y(by + 20), wpart, 20, stroke=1, fill=1)
    text(xcur + wpart / 2, by + 34, f"{name} {hexc}  {R['color_dist'][name]:.1f}%", "P-Regular", 6.6, TEXT, "center")
    xcur += wpart
top += 74 + 12
cb = R["colorblind"]
det = [
    ("Overall Feel", "Grounded and precise, with one warm spark. Deep forest green carries the living side of the mark, and the amber node reads as the single moment of signal."),
    ("Harmony", f"A two-color palette taken straight from the brand system. The lightness gap between canopy green and amber is large (color difference {cb[0]['normal_de']:.0f} on the CIEDE2000 scale), so the two never blur together, and amber appears only where something is being heard."),
    ("Brand Match", f"A direct match for the brand's tension between the living voice and the instrument. Amber makes up about {R['color_dist']['Amber']:.0f}% of the mark's ink, which is fine inside a logo but should not be copied onto surfaces, where the brand caps amber at roughly 10%."),
]
hh = 30 + sum(14 + wrap_h(s, CW - 26, 8.2) for _, s in det) + 6
card(LM, top, CW, hh, "Color Details")
t = top + 42
for k, s in det:
    text(LM + 13, t, k, "P-SemiBold", 8.4)
    t = wrap(LM + 13, t + 12, s, CW - 26, size=8.2) + 2
newpage()

# ============================ 9. Colorblindness ============================
top = heading("Colorblindness", "Over 350,000,000 people worldwide are colorblind. This is what your logo looks like to them. The second line in each card shows how far apart amber and green stay under that condition (CIEDE2000).")
cwid2 = (CW - 14) / 2
for i, r in enumerate(cb):
    xx = LM + (i % 2) * (cwid2 + 14); tt = top + (i // 2) * 205
    card(xx, tt, cwid2, 195)
    text(xx + 13, tt + 16, r["name"], "P-SemiBold", 8.4, NAVY)
    text(xx + cwid2 - 13, tt + 16, f"Affects {r['affects']} of people", "P-Regular", 6.4, MUTED, "right")
    img(os.path.join(A, f"cb_{r['name']}.png"), xx + 8, tt + 24, cwid2 - 16, 96)
    dotted(xx, xx + cwid2, tt + 128)
    text(xx + cwid2 / 2, tt + 146, f"{r['change_pct']:.1f}%", "P-Bold", 12, (0, 0, 0), "center")
    text(xx + cwid2 / 2, tt + 158, "Color Change vs. Original", "P-Regular", 7.4, TEXT, "center")
    chip(xx + cwid2 / 2, tt + 164, r["rating"], r["rating"])
    text(xx + cwid2 / 2, tt + 190, f"Amber vs. green: {r['amber_green_de']:.0f} (normal vision {r['normal_de']:.0f})", "P-Regular", 6.2, MUTED, "center")
newpage()

# ============================ 10. Contrast ============================
top = heading("Contrast", "Measure how your logo's brightness compares to its background. Two variants are compared: the color mark (canopy green with amber) and the reversed mark (bone with amber). Each card shows whichever is stronger on that background.")
rows = R["contrast"]["rows"]
band_chart(os.path.join(A, "chart_contrast.png"),
           [r["bg"] for r in rows], [r["color"] for r in rows],
           [(3.0, 16, "Great"), (2.5, 3.0, "Okay"), (2.0, 2.5, "Weak"), (1.0, 2.0, "Poor")],
           "Background Gray Value (0=Black, 1=White)", "Contrast Ratio", "Contrast Ratio vs. Background Brightness", (0, 1.0), (1, 16), dotted_y=3.0,
           extra=[([r["bg"] for r in rows], [r["reversed"] for r in rows], "#1F1D3B", (0, (3, 2)))], logy=True)
card(LM, top, CW, 232)
img(os.path.join(A, "chart_contrast.png"), LM + 10, top + 6, CW - 20, 220)
top += 232 + 6
text(LM, top + 8, "Solid line: color mark. Dashed line: reversed mark. Mid-tone grays (50 to 70%) are the weak zone for both.", "P-Regular", 6.4, MUTED)
top += 20
for i, r in enumerate(rows):
    xx = LM + (i % 3) * (cwid + 10); tt = top + (i // 3) * 184
    thumb_card(xx, tt, cwid, 174, f"{int(r['bg']*100)}% Brightness", os.path.join(A, f"contrast_{int(r['bg']*100)}.png"),
               f"{r['best_ratio']:.2f} : 1", "contrast ratio", r["rating"], imgh=62,
               extra=f"best: {r['best']} mark")
c.save()
print("wrote", OUT)
