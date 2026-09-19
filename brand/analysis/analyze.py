"""Logo analysis for the Auselia mark. Writes assets/ (images) and metrics.json.
Run with the venv python. Nothing here touches the repo."""
import json, math, os, subprocess
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw
from skimage.metrics import structural_similarity as ssim
from skimage import color as skcolor

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = Path(HERE).parent
SRC = str(BRAND / "mark" / "svg")
BUILD = BRAND / "build" / "analysis"
BUILD.mkdir(parents=True, exist_ok=True)
A = str(BUILD / "assets")
os.makedirs(A, exist_ok=True)

def render(svg, px=1024):
    out = os.path.join(A, os.path.basename(svg).replace(".svg", f"_{px}.png"))
    subprocess.run(["rsvg-convert", "-w", str(px), "-h", str(px), svg, "-o", out], check=True)
    return Image.open(out).convert("RGBA")

def crop_alpha(im, pad_frac=0.0):
    a = np.array(im)[:, :, 3]
    ys, xs = np.where(a > 8)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    c = im.crop(box)
    if pad_frac:
        p = int(round(max(c.size) * pad_frac))
        n = Image.new("RGBA", (c.width + 2 * p, c.height + 2 * p), (0, 0, 0, 0))
        n.paste(c, (p, p))
        c = n
    return c

def on_bg(im, bg=(255, 255, 255)):
    b = Image.new("RGBA", im.size, bg + (255,))
    b.alpha_composite(im)
    return b.convert("RGB")

color_full = render(os.path.join(SRC, "auselia-mark-color.svg"))
rev_full = render(os.path.join(SRC, "auselia-mark-reversed.svg"))
tight = crop_alpha(color_full)                 # exact bounding box
logo = crop_alpha(color_full, 0.06)            # padded container used for balance/slices
logo_rev_tight = crop_alpha(rev_full)
tight.save(os.path.join(A, "tight.png"))
logo.save(os.path.join(A, "logo.png"))
R = {}
W, H = logo.size
R["logo_px"] = [W, H]
R["tight_aspect"] = tight.width / tight.height

def lum01(rgb):  # rec.709 luma of 0-255 array -> 0..1
    return (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]) / 255.0

# ---------------- Balance ----------------
arr = np.array(logo).astype(float)
alpha = arr[:, :, 3] / 255.0
comp = np.array(on_bg(logo)).astype(float)
weight = alpha * (1 - lum01(comp) * 1.0)
weight = alpha * (1 - lum01(arr[:, :, :3]))           # darkness of the ink itself, weighted by coverage
ys, xs = np.mgrid[0:H, 0:W]
cx = (weight * xs).sum() / weight.sum()
cy = (weight * ys).sum() / weight.sum()
R["balance"] = {"cx": cx, "cy": cy, "x_off_pct": (cx - W / 2) / W * 100, "y_off_pct": (cy - H / 2) / H * 100}
# greyscale mass render
g = np.round(lum01(comp) * 255).astype(np.uint8)
grey = Image.fromarray(g).convert("RGB")
grey.save(os.path.join(A, "balance_grey.png"))

# ---------------- Containers ----------------
ratios = [1 / 3, 0.5, 1.0, 1.5, 2.0, 3.0]
labels = ["0.33 : 1", "0.5 : 1", "1 : 1", "1.5 : 1", "2 : 1", "3 : 1"]
def fill_rating(f):
    return "Great" if f >= 0.66 else "Okay" if f >= 0.40 else "Weak" if f >= 0.20 else "Poor"
a = tight.width / tight.height
cont = []
for r, lab in zip(ratios, labels):
    cw, ch = r, 1.0
    s = min(cw / a, ch / 1.0)                      # logo height scale: width=a*s, height=s
    lw, lh = a * s, s
    fill = (lw * lh) / (cw * ch)
    cont.append({"ratio": r, "label": lab, "fill": fill, "rating": fill_rating(fill)})
    # thumbnail with checkerboard
    Wc = 300 if r >= 1 else int(300 * r) if r > 0 else 100
    Hc = 300 if r >= 1 else 300
    if r >= 1:
        Wc, Hc = int(240 * r) if r > 1 else 240, 240 if r <= 1.5 else int(240 / r * r)
    tw, th = (int(220 * r), 220) if r < 1 else (220, int(220 / r))
    tw, th = max(tw, 60), max(th, 60)
    chk = Image.new("RGB", (tw, th), (255, 255, 255))
    d = ImageDraw.Draw(chk)
    step = 10
    for yy in range(0, th, step):
        for xx in range(0, tw, step):
            if (xx // step + yy // step) % 2 == 0:
                d.rectangle([xx, yy, xx + step - 1, yy + step - 1], fill=(233, 233, 233))
    sc = min(tw / tight.width, th / tight.height)
    lg = tight.resize((max(1, int(tight.width * sc)), max(1, int(tight.height * sc))), Image.LANCZOS)
    chk_rgba = chk.convert("RGBA")
    chk_rgba.alpha_composite(lg, ((tw - lg.width) // 2, (th - lg.height) // 2))
    chk_rgba.convert("RGB").save(os.path.join(A, f"cont_{lab.replace(' ', '').replace(':', '_')}.png"))
R["containers"] = cont

# ---------------- Size ----------------
ref_n = 256
ref_img = on_bg(tight)
scale_ref = ref_n / max(ref_img.size)
ref = ref_img.resize((round(ref_img.width * scale_ref), round(ref_img.height * scale_ref)), Image.LANCZOS)
ref_arr = np.array(ref)
def sim_rating(s):
    return "Great" if s >= 0.90 else "Okay" if s >= 0.75 else "Weak" if s >= 0.60 else "Poor"
sizes = [128, 96, 64, 48, 32, 16]
size_res = []
for n in sizes:
    sc = n / max(tight.size)
    small = on_bg(tight).resize((max(1, round(tight.width * sc)), max(1, round(tight.height * sc))), Image.LANCZOS)
    up = small.resize(ref.size, Image.BICUBIC)
    s = ssim(ref_arr, np.array(up), channel_axis=2, data_range=255)
    size_res.append({"n": n, "w": small.width, "h": small.height, "score": float(s), "rating": sim_rating(s)})
    small.save(os.path.join(A, f"size_{n}.png"))
R["size"] = size_res

# ---------------- Contours ----------------
mask = (np.array(logo)[:, :, 3] > 127).astype(np.uint8) * 255
cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cinfo = []
for c in cnts:
    per = cv2.arcLength(c, True)
    area = cv2.contourArea(c)
    cinfo.append({"perimeter": per, "area": area, "complexity": per / max(area, 1)})
mx = max(ci["complexity"] for ci in cinfo)
for ci in cinfo:
    rel = ci["complexity"] / mx
    ci["rel"] = rel
    ci["class"] = "Simple" if (len(cinfo) == 1 or rel < 0.34) else "Moderate" if rel < 0.67 else "Complex"
R["contours"] = cinfo
COL = {"Simple": (85, 230, 58), "Moderate": (255, 176, 32), "Complex": (238, 64, 64)}
canvas = np.full((H, W, 3), 255, np.uint8)
for c, ci in zip(cnts, cinfo):
    cv2.drawContours(canvas, [c], -1, COL[ci["class"]][::-1][::-1], 3, lineType=cv2.LINE_AA)
Image.fromarray(canvas).save(os.path.join(A, "contours.png"))

# ---------------- Slices ----------------
edges = np.zeros((H, W), np.uint8)
allc, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
cv2.drawContours(edges, allc, -1, 255, 1)
edge_pts = edges > 0
q = {
    "tl": edge_pts[: H // 2, : W // 2].sum(), "tr": edge_pts[: H // 2, W // 2:].sum(),
    "bl": edge_pts[H // 2:, : W // 2].sum(), "br": edge_pts[H // 2:, W // 2:].sum(),
}
tot = sum(q.values())
R["slices"] = {k: float(v) / tot * 100 for k, v in q.items()}
outline = np.full((H, W, 3), 255, np.uint8)
cv2.drawContours(outline, allc, -1, (30, 30, 30), 2, lineType=cv2.LINE_AA)
Image.fromarray(outline).save(os.path.join(A, "slices_outline.png"))
full = on_bg(logo)
for k, box in {"tl": (0, 0, W // 2, H // 2), "tr": (W // 2, 0, W, H // 2), "bl": (0, H // 2, W // 2, H), "br": (W // 2, H // 2, W, H)}.items():
    full.crop(box).save(os.path.join(A, f"slice_{k}.png"))

# ---------------- Color ----------------
white = on_bg(logo)
white.save(os.path.join(A, "color_original.png"))
gimg = white.convert("L").convert("RGB"); gimg.save(os.path.join(A, "color_grey.png"))
al = np.array(logo)[:, :, 3]
bw = np.full((H, W, 3), 255, np.uint8); bw[al > 127] = 0
Image.fromarray(bw).save(os.path.join(A, "color_bw.png"))
wb = np.full((H, W, 3), 0, np.uint8); wb[al > 127] = 255
Image.fromarray(wb).save(os.path.join(A, "color_wb.png"))
palette = {"Canopy": (0x1B, 0x3A, 0x2B), "Amber": (0xE8, 0xA1, 0x3A)}
px = np.array(logo)
opaque = px[:, :, 3] > 200
rgb = px[:, :, :3][opaque].astype(float)
names = list(palette)
d = np.stack([np.linalg.norm(rgb - np.array(palette[n]), axis=1) for n in names], 1)
assign = d.argmin(1)
dist = {n: float((assign == i).sum()) / len(assign) * 100 for i, n in enumerate(names)}
R["color_dist"] = dist
R["palette"] = {n: "#%02X%02X%02X" % palette[n] for n in names}

# ---------------- Colorblindness ----------------
M = {  # Machado et al. 2009, severity 1.0
    "Protanopia": np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]),
    "Deuteranopia": np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]),
    "Tritanopia": np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]),
}
M06 = {  # severity 0.6 (anomalous trichromacy)
    "Protanomaly": np.array([[0.458064, 0.679578, -0.137642], [0.092785, 0.846313, 0.060902], [-0.007494, -0.016807, 1.024301]]),
    "Deuteranomaly": np.array([[0.547494, 0.607765, -0.155259], [0.181692, 0.781742, 0.036566], [-0.010410, 0.027275, 0.983136]]),
    "Tritanomaly": np.array([[1.017277, 0.027029, -0.044306], [-0.006113, 0.958479, 0.047634], [0.006379, 0.248708, 0.744913]]),
}
def srgb2lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def lin2srgb(c): return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)
def simulate(img_rgb, mat):
    lin = srgb2lin(img_rgb / 255.0)
    out = np.clip(lin @ mat.T, 0, 1)
    return lin2srgb(out) * 255
def cb_rating(p): return "Great" if p < 30 else "Okay" if p < 45 else "Weak" if p < 50 else "Poor"
base = np.array(white).astype(float)
mask_o = np.array(logo)[:, :, 3] > 127
lab0 = skcolor.rgb2lab(base / 255.0)
amber = np.array(palette["Amber"], float)[None, None, :]
canopy = np.array(palette["Canopy"], float)[None, None, :]
def de_between(m, c1, c2):
    a1 = skcolor.rgb2lab(np.clip(simulate(c1, m), 0, 255) / 255.0)
    a2 = skcolor.rgb2lab(np.clip(simulate(c2, m), 0, 255) / 255.0)
    return float(skcolor.deltaE_ciede2000(a1, a2)[0, 0])
cb = []
for name, mat, aff in [("Deuteranopia", M["Deuteranopia"], "1.2%"), ("Deuteranomaly", M06["Deuteranomaly"], "5%"),
                       ("Protanopia", M["Protanopia"], "1.2%"), ("Protanomaly", M06["Protanomaly"], "1.2%"),
                       ("Tritanopia", M["Tritanopia"], "0.0001%"), ("Tritanomaly", M06["Tritanomaly"], "0.0001%")]:
    sim = np.clip(simulate(base, mat), 0, 255)
    de = skcolor.deltaE_ciede2000(lab0, skcolor.rgb2lab(sim / 255.0))
    pct = float(de[mask_o].mean())
    sep = de_between(mat, amber, canopy)
    normal_sep = float(skcolor.deltaE_ciede2000(skcolor.rgb2lab(amber / 255.0), skcolor.rgb2lab(canopy / 255.0))[0, 0])
    Image.fromarray(sim.astype(np.uint8)).save(os.path.join(A, f"cb_{name}.png"))
    cb.append({"name": name, "affects": aff, "change_pct": pct, "rating": cb_rating(pct), "amber_green_de": sep, "normal_de": normal_sep})
R["colorblind"] = cb

# ---------------- Contrast ----------------
def rel_lum(rgb):  # rgb 0..255 array
    lin = srgb2lin(rgb / 255.0)
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]
def logo_lum(im):
    p = np.array(im); m = p[:, :, 3] > 127
    return float(rel_lum(p[:, :, :3][m].astype(float)).mean())
Lc, Lr = logo_lum(logo), logo_lum(crop_alpha(rev_full, 0.06))
def ratio(l1, l2):
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)
def c_rating(r): return "Great" if r >= 3.0 else "Okay" if r >= 2.5 else "Weak" if r >= 2.0 else "Poor"
bgs = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
crs = []
rev_logo = crop_alpha(rev_full, 0.06)
for b in bgs:
    v = int(round(b * 255))
    lb = float(rel_lum(np.array([v, v, v], float)))
    rc, rr = ratio(Lc, lb), ratio(Lr, lb)
    best = "color" if rc >= rr else "reversed"
    crs.append({"bg": b, "color": rc, "reversed": rr, "best": best, "best_ratio": max(rc, rr), "rating": c_rating(max(rc, rr)), "rating_color": c_rating(rc), "rating_rev": c_rating(rr)})
    src = logo if best == "color" else rev_logo
    bg = Image.new("RGBA", (300, 170), (v, v, v, 255))
    sc = 110 / src.height
    lg = src.resize((int(src.width * sc), 110), Image.LANCZOS)
    bg.alpha_composite(lg, ((300 - lg.width) // 2, 30))
    bg.convert("RGB").save(os.path.join(A, f"contrast_{int(b*100)}.png"))
R["contrast"] = {"lum_color": Lc, "lum_reversed": Lr, "rows": crs}

json.dump(R, open(BUILD / "metrics.json", "w"), indent=1, default=float)
print(json.dumps(R, indent=1, default=float)[:6000])
