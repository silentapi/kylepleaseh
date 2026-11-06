"""Picks the best Chatterbox take per line, keeps the voice unprocessed, and lays every line out on the
music's beat grid. Writes build/voice_raw.wav, build/seg_XX.wav, build/timing.json and build/plan.json.

Music plan (track: "ʀᴏsᴇᴍᴀʀʏʟʏɴɴ |sʟᴏᴡ|", 89 BPM, sax section starts at the 43.37s downbeat):
  A) hook .. "You would've been paid mileage."  -> sparse intro, ends exactly on the sax-entry downbeat
  B) "She says no." / "...gets ugly."          -> tape-stop, music silent
  C) "Thursday." onward                         -> music resumes AT the sax entry
usage: python arrange.py <build_dir>
"""
import json, re, subprocess, sys, os
import numpy as np, soundfile as sf, librosa
from faster_whisper import WhisperModel
from script import SEGMENTS

B = sys.argv[1]
SR = 24000
beats = json.load(open("assets/music/beats.json"))
SAX_IN = 43.37
P = (88.54 - 0.86) / 33 / 4          # beat period (s)
BAR = 4 * P
CUT_SEG, THURS_SEG = 15, 17         # "She says no." / "Thursday."
ON_BEAT = {i for i, s in enumerate(SEGMENTS) if s["k"] == "card"} | {6, 9, 13, 16, 29, 35, 37, 38}
ON_BAR = {CUT_SEG, THURS_SEG}

def norm(s): return re.sub(r"[^a-z0-9 ]", "", s.lower().replace("-", " ")).split()
NUM = {"five": "5", "seventy": "70", "fifty": "50", "two": "2", "eleven": "11", "thirty": "30"}
def words_eq(a, b):
    a = [NUM.get(w, w) for w in a]; b = [NUM.get(w, w) for w in b]
    import difflib
    return difflib.SequenceMatcher(None, a, b).ratio()

def trim(x, thr_db=-38):
    e = librosa.feature.rms(y=x, frame_length=1024, hop_length=256)[0]
    db = 20 * np.log10(e + 1e-9); on = np.where(db > db.max() + thr_db)[0]
    if len(on) == 0: return x
    a = max(0, on[0] * 256 - int(0.03 * SR)); b = min(len(x), on[-1] * 256 + 1024 + int(0.08 * SR))
    y = x[a:b].copy(); f = int(0.01 * SR); y[:f] *= np.linspace(0, 1, f); y[-f * 4:] *= np.linspace(1, 0, f * 4)
    return y

def finalize(path_in, path_out):
    """No pitch shifting. One uniform, gentle 6% pace-up (pitch unchanged) applied identically to every line."""
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path_in, "-af", "atempo=1.06", path_out], check=True)

wm = WhisperModel("small.en", device="cpu", compute_type="int8")
def transcribe(x):
    x16 = np.interp(np.arange(0, len(x), SR / 16000), np.arange(len(x)), x).astype(np.float32)
    res, _ = wm.transcribe(x16, language="en", beam_size=5)
    return " ".join(r.text for r in res)

def median_f0(x):
    f0, _, _ = librosa.pyin(x, fmin=55, fmax=320, sr=SR, frame_length=2048)
    f0 = f0[~np.isnan(f0)]; return float(np.median(f0)) if len(f0) >= 5 else None
BASE_F0 = 97.0   # narrator's natural median pitch (from the reference voice)
DRAMATIC = {0, 1, 6, 9, 13, 14, 15, 16, 17, 20, 21, 23, 25, 28, 29, 33, 34, 35, 36, 37, 38}
def pitch_range(x):
    f0, _, _ = librosa.pyin(x, fmin=55, fmax=320, sr=SR, frame_length=2048)
    f0 = f0[~np.isnan(f0)]
    if len(f0) < 10: return 0.0
    st = 12 * np.log2(f0 / np.median(f0)); return float(np.percentile(st, 95) - np.percentile(st, 5))

chosen, report = [], []
for i, s in enumerate(SEGMENTS):
    best = None
    for k in range(6):
        fn = f"{B}/takes/seg_{i:02d}_t{k}.wav"
        if not os.path.exists(fn): continue
        x, sr = sf.read(fn); assert sr == SR
        x = trim(x); txt = transcribe(x)
        sim = words_eq(norm(txt), norm(s["say"]))
        nw = len(s["say"].split()); dur = len(x) / SR
        slow_pen = max(0, dur - (0.55 * nw + 1.0))       # hallucinated tails / dragging
        pr = pitch_range(x); mf = median_f0(x)
        drift = abs(12 * np.log2(mf / BASE_F0)) if mf else 0.0     # same-person check
        allow = 4.0 if i in DRAMATIC else 2.5
        score = sim * 3 + min(pr, 14) / 14 - slow_pen - max(0, drift - allow) * 0.5
        report.append(f"{i:02d} t{k} sim={sim:.2f} f0={mf or 0:4.0f} pr={pr:4.1f} dur={dur:4.2f} score={score:.2f} | {txt.strip()}")
        if best is None or score > best[0]: best = (score, k, x, sim)
    if best is None: sys.exit(f"no takes for segment {i}")
    if best[3] < 0.75: print(f"WARNING seg {i} best similarity {best[3]:.2f}")
    sf.write(f"{B}/_tmp.wav", best[2], SR); finalize(f"{B}/_tmp.wav", f"{B}/seg_{i:02d}.wav")
    chosen.append(best[1])
open(f"{B}/take_report.txt", "w").write("\n".join(report))
print("\n".join(report))

# ---------- beat-grid layout ----------
segs, cursor = [], 0.0
def snap(t, grid): return np.ceil((t - 1e-6) / grid) * grid
cut_time = None
for i, s in enumerate(SEGMENTS):
    x, _ = sf.read(f"{B}/seg_{i:02d}.wav")
    d = len(x) / SR
    if i == 0: start = 0.0
    elif i == THURS_SEG:
        # silence between cut and Thursday = whole number of beats
        start = cut_time + snap(cursor - cut_time, P)
    elif i in ON_BAR: start = snap(cursor, BAR)
    elif i in ON_BEAT: start = snap(cursor, P)
    else: start = snap(cursor, P / 2)
    if i == CUT_SEG: cut_time = start
    segs.append(dict(i=i, start=round(float(start), 4), end=round(float(start + d), 4), take=chosen[i]))
    minpause = 0.06 + 0.3 * s.get("pause", 0.2)
    cursor = start + d + minpause

total = segs[-1]["end"] + 1.6
voice = np.zeros(int(total * SR))
for sg in segs:
    x, _ = sf.read(f"{B}/seg_{sg['i']:02d}.wav"); a = int(sg["start"] * SR); voice[a:a + len(x)] += x[:len(voice) - a]
sf.write(f"{B}/voice_raw.wav", voice.astype(np.float32), SR)
json.dump(segs, open(f"{B}/timing.json", "w"), indent=1)
thurs = segs[THURS_SEG]["start"]
plan = dict(total=total, P=P, cut=cut_time, music_a_start=SAX_IN - cut_time, thurs=thurs, sax_in=SAX_IN)
json.dump(plan, open(f"{B}/plan.json", "w"), indent=1)
print("layout:", json.dumps(plan))
for sg in segs: print(sg["i"], sg["start"], SEGMENTS[sg["i"]]["say"])
