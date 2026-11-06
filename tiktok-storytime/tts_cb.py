"""Expressive narration with Chatterbox (open-source, MIT). Per-line delivery direction:
ex = emotion exaggeration (0.5 neutral -> 1.0 very dramatic), cfg = pacing (lower = slower, more deliberate).
Generates N takes per line; pick_takes.py picks the best by Whisper accuracy + expressiveness."""
import sys, os, torch, torchaudio as ta
from chatterbox.tts import ChatterboxTTS
from script import SEGMENTS
OUT, TAKES = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 2
os.makedirs(f"{OUT}/takes", exist_ok=True)
torch.set_num_threads(4)
# Delivery comes from script.py ("d"): calm by default, dramatic only on key beats. Capped at 0.75 so the voice never distorts.
STYLE = {"N": (0.5, 0.5), "B": (0.58, 0.45), "D": (0.68, 0.4), "P": (0.75, 0.4)}
REF = "assets/voice/narrator_ref.wav"   # one fixed voice for every line
m = ChatterboxTTS.from_pretrained(device="cpu")
only = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else range(len(SEGMENTS))
for i in only:
    ex, cfg = STYLE[SEGMENTS[i]["d"]]; txt = SEGMENTS[i].get("tts", SEGMENTS[i]["say"])
    for k in range(TAKES):
        fn = f"{OUT}/takes/seg_{i:02d}_t{k}.wav"
        if os.path.exists(fn): continue
        torch.manual_seed(1000 * i + k + 17)
        w = m.generate(txt, audio_prompt_path=REF, exaggeration=ex, cfg_weight=cfg, temperature=0.7)
        ta.save(fn, w, m.sr); print(i, k, round(w.shape[1] / m.sr, 2), txt, flush=True)
print("ALL DONE")
