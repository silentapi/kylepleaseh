import json, re, sys, numpy as np, soundfile as sf
from faster_whisper import WhisperModel
from script import SEGMENTS
B = sys.argv[1]
m = WhisperModel("small.en", device="cpu", compute_type="int8")
timing = json.load(open(f"{B}/timing.json"))
for seg, s in zip(timing, SEGMENTS):
    x, sr = sf.read(f"{B}/seg_{seg['i']:02d}.wav"); x = np.interp(np.arange(0, len(x), sr/16000), np.arange(len(x)), x).astype(np.float32)
    res, _ = m.transcribe(x, word_timestamps=True, language="en", initial_prompt=s["say"])
    ws = [w for r in res for w in r.words]
    show = s.get("show", s["say"]).split()
    dur = seg["end"] - seg["start"]
    heard = " ".join(w.word.strip() for w in ws)
    if len(ws) == len(show):
        times = [(w.start, w.end) for w in ws]; how = "exact"
    else:
        a = ws[0].start if ws else 0; b = ws[-1].end if ws else dur
        L = [len(re.sub(r"\W", "", x)) + 2 for x in show]; tot = sum(L); c = a; times = []
        for l in L:
            d = (b - a) * l / tot; times.append((c, c + d)); c += d
        how = "prop"
    seg["words"] = [dict(w=x, s=seg["start"] + t0, e=seg["start"] + t1) for x, (t0, t1) in zip(show, times)]
    print(seg["i"], how, "|", heard)
json.dump(timing, open(f"{B}/timing.json", "w"), indent=1)
