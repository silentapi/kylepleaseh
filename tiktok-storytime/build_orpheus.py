"""Narration with Orpheus 3B (voice 'dan'), one take per PARAGRAPH so delivery flows naturally.
Each paragraph is checked with Whisper and re-taken (up to 4x) if words are wrong. Then every script word is
aligned to the audio for captions, and paragraphs are laid out on the music's beat grid.
Writes <B>/voice_raw.wav, timing.json (segments + word times), plan.json (music cue points).
usage: python build_orpheus.py <gguf> <build_dir>
"""
import sys, os, re, json, difflib, numpy as np, soundfile as sf, torch
from llama_cpp import Llama
from snac import SNAC
from faster_whisper import WhisperModel
from script import SEGMENTS

GGUF, B = sys.argv[1], sys.argv[2]
MUSIC = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else None   # song beats/silence plan (optional)
os.makedirs(f"{B}/paras", exist_ok=True)
VOICE, SR = "dan", 24000
CUSTOM0, END_SPEECH, EOT = 128256, 128258, 128009
llm = Llama(model_path=GGUF, n_ctx=8192, n_threads=4, n_batch=512, verbose=False)
snac = SNAC.from_pretrained("hubertsiuzdak/snac_24khz").eval()
wm = WhisperModel("small.en", device="cpu", compute_type="int8")

NUM = {"five": "5", "seventy": "70", "fifty": "50", "two": "2", "eleven": "11", "thirty": "30", "teena": "tina", "kuh": "cuh", "cuz": "cuh", "kah": "cuh", "ka": "cuh", "cut": "cuh", "coz": "cuh", "cus": "cuh", "cause": "cuh", "kuz": "cuh", "kuhh": "cuh", "kuuh": "cuh", "cuhh": "cuh"}
def norm(s):
    s = re.sub(r"[^a-z0-9' ]", " ", s.lower().replace("-", " "))          # drop all punctuation first
    s = re.sub(r"\bp\s+m\b", "pm", s); s = re.sub(r"\bh\s+r\b", "hr", s); s = re.sub(r"\bi\s+t\b", "it", s)
    s = re.sub(r"(\d)pm\b", r"\1 pm", s)
    return [NUM.get(w, w) for w in s.split()]

def synth(text, seed):
    llm.set_seed(seed)
    toks = llm.tokenize(f"<|audio|>{VOICE}: {text}<|eot_id|>".encode(), add_bos=True, special=True)
    codes = []
    for n, tok in enumerate(llm.generate(toks, temp=0.6, top_p=0.9, repeat_penalty=1.1)):
        if tok in (END_SPEECH, EOT) or n > len(text) * 9 + 600: break
        if tok >= CUSTOM0 + 10:
            c = tok - CUSTOM0 - 10 - (len(codes) % 7) * 4096
            if 0 <= c < 4096: codes.append(c)
    f = np.array(codes[: len(codes) // 7 * 7]).reshape(-1, 7)
    with torch.inference_mode():
        a = snac.decode([torch.tensor(f[:, 0])[None], torch.tensor(f[:, [1, 4]].reshape(-1))[None],
                         torch.tensor(f[:, [2, 3, 5, 6]].reshape(-1))[None]]).squeeze().numpy()
    idx = np.where(np.abs(a) > 0.01)[0]                       # trim edges
    return a[max(0, idx[0] - 480): idx[-1] + 2400] if len(idx) else a

def words_of(a, prompt):
    x = np.interp(np.arange(0, len(a), SR / 16000), np.arange(len(a)), a).astype(np.float32)
    res, _ = wm.transcribe(x, language="en", beam_size=5, word_timestamps=True, initial_prompt=prompt)
    return [w for r in res for w in r.words]

def tighten(a, max_gap=0.42, thr_db=-40):
    """Shorten silent gaps longer than max_gap (no stretching, no pitch change: the voice is untouched)."""
    fr = int(0.01 * SR); n = len(a) // fr
    e = 20 * np.log10(np.sqrt((a[: n * fr].reshape(n, fr) ** 2).mean(1)) + 1e-9)
    quiet = e < e.max() + thr_db
    out, i = [], 0
    while i < n:
        j = i
        while j < n and quiet[j] == quiet[i]: j += 1
        chunk = a[i * fr: j * fr]
        if quiet[i] and (j - i) * 0.01 > max_gap and 0 < i and j < n:
            keep = int(max_gap * SR); h = keep // 2
            chunk = np.concatenate([chunk[:h], chunk[-(keep - h):]])
        out.append(chunk); i = j
    out.append(a[n * fr:])
    return np.concatenate(out)

paras = sorted({s["p"] for s in SEGMENTS})
P_AUDIO, P_WORDS = {}, {}
for p in paras:
    segs = [s for s in SEGMENTS if s["p"] == p]
    tts = " ".join(s.get("tts", s["say"]) for s in segs)
    want = norm(" ".join(s["say"] for s in segs))
    best = None
    for k in range(4):
        fn = f"{B}/paras/p{p:02d}_t{k}.wav"
        if os.path.exists(fn): a, _ = sf.read(fn)
        else: a = synth(tts, 1000 * p + k + 7); sf.write(fn, a, SR)
        ws = words_of(a, " ".join(s["say"] for s in segs))
        got = norm(" ".join(w.word for w in ws))
        sim = difflib.SequenceMatcher(None, want, got).ratio()
        extra = max(0, len(got) - len(want))
        dur_ok = len(a) / SR < len(want) * 0.62 + 2.5         # reject run-on / hallucinated tails
        score = sim - 0.05 * extra - (0 if dur_ok else 0.3)
        print(f"P{p} take {k}: sim={sim:.2f} extra={extra} dur={len(a)/SR:.1f}s | {' '.join(got)}", flush=True)
        if best is None or score > best[0]: best = (score, a, ws, sim)
        if sim >= 0.97 and extra == 0 and dur_ok: break
    if best[3] < 0.9: print(f"WARNING P{p} best similarity {best[3]:.2f}")
    a = tighten(best[1])
    P_AUDIO[p], P_WORDS[p] = a, (words_of(a, " ".join(s["say"] for s in segs)) if len(a) != len(best[1]) else best[2])
    print(f"P{p}: {len(best[1])/SR:.1f}s -> {len(a)/SR:.1f}s after tightening pauses", flush=True)

# ---------- word alignment: script words -> whisper word times ----------
def align(segs, ws):
    script = [(si, w) for si, s in enumerate(segs) for w in s["say"].split()]
    sn = [(norm(w) or [""])[0] for _, w in script]
    wn = [(norm(w.word) or [""])[0] for w in ws]
    times = [None] * len(script)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, sn, wn, autojunk=False).get_opcodes():
        if tag in ("equal", "replace"):
            for d in range(min(i2 - i1, j2 - j1)): times[i1 + d] = (ws[j1 + d].start, ws[j1 + d].end)
    known = [i for i, t in enumerate(times) if t]
    for i in range(len(times)):                               # interpolate gaps
        if times[i] is None:
            prev = max([j for j in known if j < i], default=None); nxt = min([j for j in known if j > i], default=None)
            a = times[prev][1] if prev is not None else 0.0
            b = times[nxt][0] if nxt is not None else (ws[-1].end if ws else a + 0.3)
            cnt = (nxt if nxt is not None else len(times)) - (prev if prev is not None else -1)
            pos = i - (prev if prev is not None else -1)
            t0 = a + (b - a) * (pos - 1) / cnt; times[i] = (t0, t0 + (b - a) / cnt)
    out = [[] for _ in segs]
    for (si, w), t in zip(script, times): out[si].append(t)
    return out

# ---------- layout ----------
cut_p = next(s["p"] for s in SEGMENTS if s.get("mark") == "cut")
thu_p = next(s["p"] for s in SEGMENTS if s.get("mark") == "thurs")
dur = {p: len(P_AUDIO[p]) / SR for p in paras}
starts, plan_extra = {}, {}
if MUSIC:
    # One continuous stretch of the song starting at S: "she says no" lands in the song's own silence and
    # "Thursday" lands exactly where the beat returns. Paragraph starts snap to the song's beat grid.
    bt = np.array(MUSIC["beats"]); Ss, Br = MUSIC["silence_start"], MUSIC["beat_return"]
    pre = [p for p in paras if p < cut_p]
    need = sum(dur[p] for p in pre) + 0.3 * (len(pre) - 1) + 0.35
    drop_p = next((s["p"] for s in SEGMENTS if s.get("mark") == "drop"), None)
    lim = Ss - need
    if drop_p is not None and MUSIC.get("drop"):          # also land the song's big drop on this paragraph
        lim = min(lim, MUSIC["drop"] - (sum(dur[q] + 0.3 for q in pre if q < drop_p) + 0.75))
    S = float(bt[bt <= lim].max())
    vbeats = bt - S
    cursor = 0.0
    for p in pre:
        if p == pre[0]: st = 0.0
        elif p == drop_p and MUSIC.get("drop"): st = MUSIC["drop"] - S
        else:
            cand = vbeats[vbeats >= cursor + 0.25]; st = float(cand.min()) if len(cand) else cursor + 0.3
        starts[p] = st; cursor = st + dur[p]
    if drop_p is not None and starts.get(drop_p - 1, 0) + dur.get(drop_p - 1, 0) > starts[drop_p] - 0.1:
        print("WARNING: paragraph before the drop overlaps it")
    sil = (Br - Ss) - dur[cut_p]                                   # centre the line in the song's silence,
    starts[cut_p] = (Ss - S) + max(0.15, min(1.3, sil * 0.42)); cut_t = (Ss - S)   # a breath of quiet before it
    if starts[cut_p] + dur[cut_p] > Br - S - 0.1: print("WARNING: 'she says no' paragraph spills past the silence")
    starts[thu_p] = Br - S + 0.03; thu_t = starts[thu_p]
    cursor = starts[thu_p] + dur[thu_p]
    for p in [p for p in paras if p > thu_p]:
        cand = vbeats[vbeats >= cursor + 0.2]; st = float(cand.min()) if len(cand) else cursor + 0.3
        starts[p] = st; cursor = st + dur[p]
    plan_extra = dict(mode="batida", song_start=S)
    P_BEAT, SAX_IN = float(np.median(np.diff(bt))), Br
else:
    P_BEAT = (88.54 - 0.86) / 33 / 4; BAR = 4 * P_BEAT; SAX_IN = 43.37
    snap = lambda t, g: float(np.ceil((t - 1e-6) / g) * g)
    cursor, cut_t = 0.0, None
    for p in paras:
        if p == 0: st = 0.0
        elif p == cut_p: st = snap(cursor + 0.25, BAR); cut_t = st
        elif p == thu_p: st = cut_t + snap(cursor + 0.35 - cut_t, P_BEAT)
        else: st = snap(cursor + 0.2, P_BEAT / 2)
        starts[p] = st; cursor = st + dur[p]

total = cursor + 1.8
voice = np.zeros(int(total * SR))
timing, gi = [], 0
for p in paras:
    a = P_AUDIO[p]; o = int(starts[p] * SR); voice[o:o + len(a)] += a
    segs = [s for s in SEGMENTS if s["p"] == p]
    for s, wt in zip(segs, align(segs, P_WORDS[p])):
        show = s.get("show", s["say"]).split()
        s0, s1 = starts[p] + wt[0][0], starts[p] + wt[-1][1]
        if len(show) == len(wt): wtimes = [(starts[p] + a0, starts[p] + a1) for a0, a1 in wt]
        else:                                                 # proportional within the line's span
            L = [len(re.sub(r"\W", "", x)) + 2 for x in show]; c = s0; wtimes = []
            for l in L: d = (s1 - s0) * l / sum(L); wtimes.append((c, c + d)); c += d
        timing.append(dict(i=gi, start=round(s0, 4), end=round(s1, 4),
                           words=[dict(w=w, s=round(a0, 4), e=round(a1, 4)) for w, (a0, a1) in zip(show, wtimes)]))
        gi += 1
sf.write(f"{B}/voice_raw.wav", voice.astype(np.float32), SR)
json.dump(timing, open(f"{B}/timing.json", "w"), indent=1)
plan = dict(total=total, P=P_BEAT, cut=cut_t, music_a_start=SAX_IN - cut_t, thurs=starts[thu_p], sax_in=SAX_IN, **plan_extra)
json.dump(plan, open(f"{B}/plan.json", "w"), indent=1)
print("layout", json.dumps(plan))
