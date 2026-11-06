import sys, json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from script import SEGMENTS
M = sys.argv[1]  # models dir
OUT = sys.argv[2]
k = Kokoro(f"{M}/kokoro-v1.0.onnx", f"{M}/voices-v1.0.bin")
SR = 24000
VOICE, SPEED = "am_onyx", 1.17
def trim(x, thr=0.01):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0: return x
    a = max(0, idx[0] - int(0.02*SR)); b = min(len(x), idx[-1] + int(0.06*SR))
    return x[a:b]
chunks, segs, t = [np.zeros(int(0.25*SR))], [], 0.25
for i, s in enumerate(SEGMENTS):
    a, sr = k.create(s["say"], voice=VOICE, speed=SPEED, lang="en-us")
    assert sr == SR
    a = trim(a)
    sf.write(f"{OUT}/seg_{i:02d}.wav", a, SR)
    d = len(a)/SR
    segs.append(dict(i=i, start=t, end=t+d))
    chunks += [a, np.zeros(int(s.get("pause", 0.2)*0.8*SR))]
    t += d + s.get("pause", 0.2)*0.8
    print(i, round(d, 2), s["say"])
audio = np.concatenate(chunks).astype(np.float32)
sf.write(f"{OUT}/voice_raw.wav", audio, SR)
json.dump(segs, open(f"{OUT}/timing.json", "w"), indent=1)
print("total", round(len(audio)/SR, 2))
