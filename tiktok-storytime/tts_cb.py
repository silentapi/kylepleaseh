"""Expressive narration with Chatterbox (open-source, MIT). Per-line delivery direction:
ex = emotion exaggeration (0.5 neutral -> 1.0 very dramatic), cfg = pacing (lower = slower, more deliberate).
Generates N takes per line; pick_takes.py picks the best by Whisper accuracy + expressiveness."""
import sys, os, torch, torchaudio as ta
from chatterbox.tts import ChatterboxTTS
from script import SEGMENTS
OUT, TAKES = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 2
os.makedirs(f"{OUT}/takes", exist_ok=True)
torch.set_num_threads(4)
DIRECTION = {  # index: (exaggeration, cfg_weight, optional TTS text)
 0: (0.9, 0.3, "Enjoy waiting here... until five P.M."), 1: (0.8, 0.3, "Her boss said that... to her face."),
 2: (0.7, 0.3, "So she put it in writing. And sent it straight to H.R."), 3: (0.55, 0.4, None),
 4: (0.6, 0.4, None), 5: (0.65, 0.3, None), 6: (0.9, 0.3, "...Yet."), 7: (0.7, 0.35, "Then suddenly... her assignments start changing."),
 8: (0.7, 0.35, "First? A solo home visit."), 9: (0.85, 0.3, "Seventy miles away. Two hours... each way."),
 10: (0.65, 0.4, None), 11: (0.65, 0.4, None), 12: (0.7, 0.35, "And she has a special needs daughter who needs her nearby."), 13: (0.8, 0.3, None), 14: (0.9, 0.3, None),
 15: (0.8, 0.35, None), 16: (0.95, 0.3, "And that's when it gets... ugly."), 17: (0.7, 0.35, "Thursday. Eleven thirty A.M."),
 18: (0.6, 0.4, None), 19: (0.75, 0.35, None), 20: (0.7, 0.35, None), 21: (0.9, 0.3, None), 22: (0.5, 0.5, "Then."),
 23: (0.9, 0.3, None), 24: (0.5, 0.5, "Then."), 25: (0.9, 0.3, None), 26: (0.7, 0.35, None), 27: (0.7, 0.35, None),
 28: (0.8, 0.3, "And on his way out the door..."), 29: (1.0, 0.3, "Enjoy waiting here... until five P.M."),
 30: (0.7, 0.35, None), 31: (0.8, 0.3, None), 32: (0.7, 0.35, None), 33: (0.8, 0.3, None), 34: (0.85, 0.3, None),
 35: (0.8, 0.3, None), 36: (0.8, 0.3, "And he says she left something out..."), 37: (0.9, 0.3, "A working computer. That she refused to use."),
 38: (0.8, 0.3, None), 39: (0.7, 0.35, None),
}
m = ChatterboxTTS.from_pretrained(device="cpu")
only = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else range(len(SEGMENTS))
for i in only:
    ex, cfg, txt = DIRECTION[i]; txt = txt or SEGMENTS[i]["say"]
    for k in range(TAKES):
        fn = f"{OUT}/takes/seg_{i:02d}_t{k}.wav"
        if os.path.exists(fn): continue
        torch.manual_seed(1000 * i + k + 17)
        w = m.generate(txt, exaggeration=ex, cfg_weight=cfg, temperature=0.8)
        ta.save(fn, w, m.sr); print(i, k, round(w.shape[1] / m.sr, 2), txt, flush=True)
print("ALL DONE")
