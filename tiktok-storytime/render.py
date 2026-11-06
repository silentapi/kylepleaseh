"""Renders the 1080x1920 storytime video frame-by-frame with Pillow and pipes it to ffmpeg.
usage: python3 render.py <build_dir> <out.mp4> [--preview SECONDS_LIST]
"""
import json, math, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
from script import SEGMENTS

B, OUT = sys.argv[1], sys.argv[2]
PREVIEW = [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 and sys.argv[3] == "--preview" else None
W, H, FPS = 1080, 1920, 30
BW, BH = int(W * 1.16), int(H * 1.16)
IMG = "assets/img"
F_CAP = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
F_CARD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
F_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
F_MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-ExtraBold.ttf"
YELLOW, WHITE, RED = (255, 225, 60), (255, 255, 255), (224, 36, 59)
_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]

timing = json.load(open(f"{B}/timing.json"))
dur_audio = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                           "-of", "csv=p=0", f"{B}/" + os.environ.get("MIX", "mix.wav")]).decode())
TOTAL = dur_audio
for seg, s in zip(timing, SEGMENTS): seg.update(s)
for i, seg in enumerate(timing):
    seg["next"] = timing[i + 1]["start"] if i + 1 < len(timing) else TOTAL
timing[0]["start_vis"] = 0.0

# ---------- visual spans ----------
spans = []
for seg in timing:
    if spans and spans[-1]["v"] == seg["v"]: spans[-1]["end"] = seg["next"]
    else: spans.append(dict(v=seg["v"], start=seg["start"] if spans else 0.0, end=seg["next"]))
# go to black exactly when the music cuts out (song mode), not when the next line starts
if os.path.exists(f"{B}/plan.json"):
    _plan = json.load(open(f"{B}/plan.json"))
    for k, sp in enumerate(spans):
        if sp["v"] == "black" and k > 0 and _plan.get("cut") is not None and _plan["cut"] < sp["start"]:
            spans[k - 1]["end"] = sp["start"] = _plan["cut"]
for i, sp in enumerate(spans): sp["idx"] = i

def ease_out(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_back(x, s=1.7):
    x = min(max(x, 0), 1) - 1; return 1 + (s + 1) * x ** 3 + s * x ** 2

# ---------- backgrounds ----------
def cover(im, w, h):
    r = max(w / im.width, h / im.height)
    im = im.resize((math.ceil(im.width * r), math.ceil(im.height * r)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))

def grade(im, dark=0.62, sat=0.6, tint=(0.96, 1.0, 1.08), blur=0):
    im = ImageEnhance.Color(im).enhance(sat)
    im = ImageEnhance.Contrast(im).enhance(1.15)
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(im).astype(np.float32) * dark * np.array(tint, np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def photo(name, **kw):
    im = Image.open(f"{IMG}/{name}.jpg").convert("RGB")
    return grade(cover(im, BW, BH), **kw).filter(ImageFilter.UnsharpMask(2, 60, 2))

def rrect(d, box, r, **kw): d.rounded_rectangle(box, r, **kw)

def doc_pip():
    bg = photo("hosp_6", dark=0.35, blur=6)
    paper = Image.new("RGBA", (720, 900), (0, 0, 0, 0)); d = ImageDraw.Draw(paper)
    rrect(d, (0, 0, 719, 899), 14, fill=(240, 238, 232, 255))
    d.text((360, 70), "PERFORMANCE", font=font(F_CAP, 62), fill=(25, 25, 30), anchor="mm")
    d.text((360, 140), "IMPROVEMENT PLAN", font=font(F_CAP, 62), fill=(25, 25, 30), anchor="mm")
    d.line((60, 195, 660, 195), fill=(25, 25, 30), width=4)
    for j, (k, v) in enumerate([("EMPLOYEE:", "TINA, RN"), ("SUPERVISOR:", "BEN"), ("STATUS:", "PENDING HR")]):
        d.text((60, 240 + j * 60), k, font=font(F_MONO, 30), fill=(90, 90, 95))
        d.text((300, 240 + j * 60), v, font=font(F_MONO, 30), fill=(25, 25, 30))
    rng = np.random.default_rng(3)
    for j in range(9):
        y = 450 + j * 46; d.rectangle((60, y, 60 + int(rng.uniform(380, 600)), y + 16), fill=(200, 198, 192))
    d.line((60, 850, 330, 850), fill=(120, 120, 120), width=2); d.text((60, 858), "Signature", font=font(F_BOLD, 22), fill=(120, 120, 120))
    paper = paper.rotate(3, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", paper.size, (0, 0, 0, 0)); sh.putalpha(paper.split()[3].point(lambda a: a * 0.6))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    ox, oy = (BW - paper.width) // 2, 430
    bg.paste((0, 0, 0), (ox + 20, oy + 30), sh); bg.paste(paper, (ox, oy), paper)
    return bg

def stamp_img(text, size=150, color=RED, angle=-14):
    f = font(F_CAP, size); tw = f.getlength(text)
    im = Image.new("RGBA", (int(tw + 100), size + 90), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rrect(d, (8, 8, im.width - 8, im.height - 8), 22, outline=color + (255,), width=14)
    d.text((im.width / 2, im.height / 2), text, font=f, fill=color + (255,), anchor="mm")
    return im.rotate(angle, expand=True, resample=Image.BICUBIC)

def doc_folder():
    bg = photo("desk_3", dark=0.3, blur=8)
    d = ImageDraw.Draw(bg); cx, top = BW // 2, 470
    rrect(d, (cx - 400, top, cx - 120, top + 90), 18, fill=(186, 146, 74))
    rrect(d, (cx - 420, top + 50, cx + 420, top + 700), 22, fill=(201, 163, 91))
    rrect(d, (cx - 300, top + 170, cx + 300, top + 400), 10, fill=(248, 246, 240))
    d.text((cx, top + 225), "EMPLOYEE RELATIONS", font=font(F_CAP, 50), fill=(25, 25, 30), anchor="mm")
    d.text((cx, top + 300), "CASE #REDACTED", font=font(F_MONO, 40), fill=(60, 60, 65), anchor="mm")
    d.text((cx, top + 360), "INVESTIGATION: OPEN", font=font(F_MONO, 30), fill=RED, anchor="mm")
    return bg

def phone_banner():
    im = Image.new("RGBA", (940, 270), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rrect(d, (0, 0, 939, 269), 46, fill=(242, 242, 247, 245))
    rrect(d, (34, 40, 124, 130), 22, fill=(30, 126, 246))
    d.rectangle((52, 66, 106, 104), outline=WHITE, width=5); d.line((52, 66, 79, 88, 106, 66), fill=WHITE, width=5)
    d.text((150, 42), "MAIL", font=font(F_BOLD, 30), fill=(110, 110, 115))
    d.text((905, 42), "now", font=font(F_BOLD, 30), fill=(110, 110, 115), anchor="ra")
    d.text((150, 92), "Ben (Director)", font=font(F_CARD, 44), fill=(10, 10, 12))
    d.text((150, 150), "RE: Recap of today's interaction", font=font(F_BOLD, 36), fill=(10, 10, 12))
    d.text((150, 202), "Hi Tina, I would like to provide additional…", font=font(F_BOLD, 32), fill=(95, 95, 100))
    return im

def error_box():
    im = Image.new("RGBA", (860, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rrect(d, (0, 0, 859, 419), 30, fill=(20, 20, 24, 235), outline=RED + (255,), width=6)
    d.polygon([(430, 50), (500, 170), (360, 170)], fill=RED)
    d.text((430, 128), "!", font=font(F_CAP, 80), fill=WHITE, anchor="mm")
    d.text((430, 240), "CONNECTION FAILED", font=font(F_CAP, 64), fill=WHITE, anchor="mm")
    d.text((430, 320), "VPN login unavailable · Workstation 2: no signal", font=font(F_BOLD, 30), fill=(200, 200, 205), anchor="mm")
    return im

print("building backgrounds…")
BG = {
    "clock": photo("clock_4"), "clock2": photo("clock_4", tint=(1.25, 0.8, 0.8), sat=0.4),
    "hall": photo("hosp_6"), "pip": doc_pip(), "highway": photo("hwy_3", dark=0.7),
    "miles": photo("hwy_7", dark=0.55), "mom": photo("mom_1", sat=0.45), "black": Image.new("RGB", (BW, BH), (6, 6, 8)),
    "thursday": photo("desk_3", dark=0.33, blur=3), "office": photo("desk_3"), "nurses": photo("hosp_3"),
    "error": photo("typing_5", dark=0.8), "typing": photo("typing_3"), "hrcase": doc_folder(),
    "notif": photo("typing_5", dark=0.45, blur=10), "part2": Image.new("RGB", (BW, BH), (8, 4, 6)),
}
BG["pip_denied"] = BG["pip"]
STAMP = stamp_img("DENIED"); STAMP_OPEN = stamp_img("+1 FILE ADDED", 70, (255, 225, 60), -8)
BANNER, ERRBOX = phone_banner(), error_box()

# ---------- vignette & grain ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.55 * np.clip(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2, 0, 1))[..., None]
GRAIN = [np.random.default_rng(i).normal(0, 4, (H, W, 1)).astype(np.float32) for i in range(6)]

# ---------- text helpers ----------
def stroke_text(d, xy, text, f, fill, stroke=12, anchor="la"):
    d.text(xy, text, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0), anchor=anchor)

def chunks_for(seg):
    out, cur = [], []
    for w in seg["words"]:
        cur.append(w)
        txt = " ".join(x["w"] for x in cur)
        if len(cur) >= 3 or len(txt) >= 15 or re.search(r"[.,?!…]$", w["w"]):
            out.append(cur); cur = []
    if cur: out.append(cur)
    for j, c in enumerate(out):
        c_start = c[0]["s"] - 0.04
        c_end = out[j + 1][0]["s"] - 0.04 if j + 1 < len(out) else min(seg["next"], c[-1]["e"] + 0.9)
        out[j] = dict(words=c, start=c_start, end=c_end)
    return out
for seg in timing:
    if seg["k"] == "cap": seg["chunks"] = chunks_for(seg)

def render_chunk(chunk, t):
    words = [w["w"].upper() for w in chunk["words"]]
    size = 124
    while True:
        f = font(F_CAP, size); sp = f.getlength(" ")
        widths = [f.getlength(w) for w in words]; tw = sum(widths) + sp * (len(words) - 1)
        if tw <= 900 or size < 70: break
        size -= 6
    im = Image.new("RGBA", (int(tw + 60), size + 70), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = 30
    for w, wd, meta in zip(words, widths, chunk["words"]):
        active = meta["s"] - 0.03 <= t < meta["e"] + 0.05 or (meta is chunk["words"][-1] and t >= meta["s"])
        stroke_text(d, (x, 22), w, f, YELLOW if active else WHITE, stroke=max(8, size // 10))
        x += wd + sp
    return im

def wrap(words, f, maxw):
    lines, cur = [], []
    for w in words:
        if cur and f.getlength(" ".join(cur + [w])) > maxw: lines.append(cur); cur = []
        cur.append(w)
    if cur: lines.append(cur)
    return lines

def render_card(seg, t):
    words = seg["show"].split(); n = len(words)
    size = 86 if n <= 7 else 72
    f = font(F_CARD, size); maxw = 820
    lines = wrap(words, f, maxw); lh = int(size * 1.22)
    boxw = int(max(f.getlength(" ".join(l)) for l in lines)) + 110; boxh = lh * len(lines) + 90
    im = Image.new("RGBA", (boxw + 40, boxh + 110), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rrect(d, (20, 70, 20 + boxw, 70 + boxh), 34, fill=RED + (255,))
    who = seg.get("who", "")
    if who:
        fw = font(F_MONO, 34); ww = fw.getlength(who)
        rrect(d, (20, 4, 20 + ww + 44, 62), 14, fill=(0, 0, 0, 235))
        d.text((42, 33), who, font=fw, fill=WHITE, anchor="lm")
    k = 0; y = 70 + 45
    for line in lines:
        x = 20 + 55
        for w in line:
            meta = seg["words"][k]; shown = t >= meta["s"] - 0.05 or seg["i"] == 0 and False
            if t >= meta["s"] - 0.05:
                d.text((x, y), w, font=f, fill=WHITE if t >= meta["e"] else YELLOW)
            x += f.getlength(w + " "); k += 1
        y += lh
    return im

def paste_center(frame, im, cx, cy, scale=1.0, angle=0.0, alpha=1.0):
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if angle: im = im.rotate(angle, expand=True, resample=Image.BILINEAR)
    if alpha < 1.0: im.putalpha(im.split()[3].point(lambda a: int(a * alpha)))
    frame.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)

# shake events
SHAKES = [seg["start"] for seg in timing if seg["k"] == "card" or seg.get("sfx") in ("stamp", "hit", "boom")]

def frame_at(t):
    sp = next(s for s in spans if s["start"] <= t < s["end"]) if t < spans[-1]["end"] else spans[-1]
    u = (t - sp["start"]) / max(0.01, sp["end"] - sp["start"])
    lt = t - sp["start"]
    zin = sp["idx"] % 2 == 0
    z = 1.0 + 0.09 * (u if zin else 1 - u)
    if sp["v"] == "clock2": z = 1.12 + 0.1 * u
    z += 0.06 * math.exp(-lt / 0.12) if sp["idx"] > 0 else 0     # punch-in on cut
    sx = sy = 0.0
    for st in SHAKES:
        dt = t - st
        if 0 <= dt < 0.35:
            a = 16 * (1 - dt / 0.35); sx += a * math.sin(dt * 90); sy += a * math.cos(dt * 77)
    bg = BG[sp["v"]]
    cw, ch = W * (BW / W) / z / 1.0, H * (BH / H) / z / 1.0
    cw, ch = min(cw, BW), min(ch, BH)
    panx = (BW - cw) / 2 + (u - 0.5) * (BW - cw) * (0.5 if sp["idx"] % 3 == 1 else -0.3 if sp["idx"] % 3 == 2 else 0)
    cx0 = min(max(panx + sx, 0), BW - cw); cy0 = min(max((BH - ch) / 2 + sy, 0), BH - ch)
    frame = bg.resize((W, H), Image.BILINEAR, box=(cx0, cy0, cx0 + cw, cy0 + ch))

    # ---- per-visual overlays ----
    v = sp["v"]
    if v == "pip_denied":
        k = ease_out(lt / 0.13); paste_center(frame, STAMP, W / 2, 880, scale=2.4 - 1.4 * k, alpha=min(1, lt / 0.06))
    elif v == "miles":
        d = ImageDraw.Draw(frame); n = int(70 * ease_out(lt / 1.1))
        stroke_text(d, (W / 2, 560), f"{n} MILES", font(F_CAP, 190), WHITE, 12, "mm")
        if lt > 1.0: stroke_text(d, (W / 2, 720), "≈ 2 HRS EACH WAY", font(F_MONO, 64), YELLOW, 8, "mm")
        s10 = next(sg["start"] for sg in timing if sg.get("mark") == "promised")
        if t >= s10:
            k = ease_back((t - s10) / 0.25)
            pill = Image.new("RGBA", (560, 120), (0, 0, 0, 0)); pd = ImageDraw.Draw(pill)
            rrect(pd, (0, 0, 559, 119), 26, fill=(0, 0, 0, 200), outline=RED + (255,), width=6)
            pd.text((280, 60), "PROMISED: 50 MAX", font=font(F_MONO, 50), fill=WHITE, anchor="mm")
            if t >= s10 + 1.0: pd.line((20, 64, 20 + 520 * ease_out((t - s10 - 1.0) / 0.3), 56), fill=RED, width=10)
            paste_center(frame, pill, W / 2, 880, scale=max(0.01, k))
    elif v == "thursday":
        d = ImageDraw.Draw(frame)
        s1, s2 = "THURSDAY", "11:30 AM"
        n1 = int(len(s1) * min(1, lt / 0.45)); n2 = int(len(s2) * min(1, max(0, lt - 0.55) / 0.45))
        stroke_text(d, (W / 2, 800), s1[:n1], font(F_MONO, 150), WHITE, 6, "mm")
        stroke_text(d, (W / 2, 990), s2[:n2], font(F_MONO, 130), RED, 6, "mm")
    elif v == "error":
        paste_center(frame, ERRBOX, W / 2, 720, scale=ease_back(lt / 0.3) if lt < 0.3 else 1.0)
    elif v == "hrcase":
        if lt > 0.15:
            paste_center(frame, STAMP_OPEN, W / 2 + 150, 1010, scale=2.0 - ease_out((lt - 0.15) / 0.12))
    elif v == "notif":
        y = -200 + 700 * ease_out(lt / 0.45); paste_center(frame, BANNER, W / 2, y)
    elif v == "part2":
        d = ImageDraw.Draw(frame); k = ease_back(lt / 0.35)
        big = Image.new("RGBA", (1000, 260), (0, 0, 0, 0)); bd = ImageDraw.Draw(big)
        stroke_text(bd, (500, 130), "PART 2", font(F_CAP, 230), RED, 10, "mm")
        paste_center(frame, big, W / 2, 620, scale=max(0.01, k))
        if lt > 0.3: stroke_text(d, (W / 2, 800), "BEN'S REPLY", font(F_CAP, 96), WHITE, 9, "mm")
        if lt > 0.6:
            pulse = 1 + 0.06 * math.sin((lt - 0.6) * 7)
            btn = Image.new("RGBA", (560, 150), (0, 0, 0, 0)); bd = ImageDraw.Draw(btn)
            rrect(bd, (0, 0, 559, 149), 75, fill=RED + (255,))
            bd.text((280, 75), "+ FOLLOW", font=font(F_CAP, 76), fill=WHITE, anchor="mm")
            paste_center(frame, btn, W / 2, 1000, scale=pulse)

    # ---- captions / cards ----
    cur = None
    for seg in timing:
        s0 = 0.0 if seg["i"] == 0 else seg["start"] - 0.04
        if s0 <= t < seg["next"]: cur = seg
    if cur is not None:
        if cur["k"] == "cap":
            for c in cur["chunks"]:
                if c["start"] <= t < c["end"]:
                    im = render_chunk(c, t); k = ease_back((t - c["start"]) / 0.12, 2.2)
                    paste_center(frame, im, W / 2, 1250, scale=0.75 + 0.25 * k)
        elif cur["k"] == "card":
            im = render_card(cur, t); ct = t - (0 if cur["i"] == 0 else cur["start"] - 0.04)
            k = ease_out(ct / 0.14); paste_center(frame, im, W / 2, 1020, scale=1.35 - 0.35 * k, angle=-2 * k, alpha=min(1, ct / 0.05))

    # ---- persistent chrome ----
    d = ImageDraw.Draw(frame)
    pill_f = font(F_MONO, 34); label = "STORYTIME · PART 1"; lw = pill_f.getlength(label)
    rrect(d, (W / 2 - lw / 2 - 26, 232, W / 2 + lw / 2 + 26, 290), 29, fill=(0, 0, 0))
    d.text((W / 2, 261), label, font=pill_f, fill=WHITE, anchor="mm")
    if t < 5.0:
        stroke_text(d, (W / 2, 1450), "names changed · based on her email", font(F_BOLD, 34), (220, 220, 220), 4, "mm")

    a = np.asarray(frame).astype(np.float32) * VIG + GRAIN[int(t * FPS) % len(GRAIN)]
    if v == "error":   # glitch flicker
        ph = (lt % 0.55)
        if ph < 0.07:
            a[..., 0] = np.roll(a[..., 0], 14, axis=1); a[..., 2] = np.roll(a[..., 2], -10, axis=1)
            for _ in range(5):
                y0 = int(np.random.uniform(0, H - 80)); a[y0:y0 + 60] = np.roll(a[y0:y0 + 60], int(np.random.uniform(-60, 60)), axis=1)
    return np.clip(a, 0, 255).astype(np.uint8)

if PREVIEW:
    for tt in PREVIEW:
        Image.fromarray(frame_at(tt)).save(f"{B}/preview_{tt:05.1f}.jpg", quality=85)
        print("preview", tt)
    sys.exit()

nf = int(TOTAL * FPS)
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                      "-r", str(FPS), "-i", "-", "-i", f"{B}/" + os.environ.get("MIX", "mix.wav"), "-c:v", "libx264", "-preset", "medium", "-maxrate", "5M", "-bufsize", "10M",
                      "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                      "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for fi in range(nf):
    p.stdin.write(frame_at(fi / FPS).tobytes())
    if fi % 300 == 0: print(f"frame {fi}/{nf}", flush=True)
p.stdin.close(); p.wait()
print("done", OUT)
