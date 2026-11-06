"""Expressive narration with Chatterbox (open-source, MIT). Per-line delivery direction:
ex = emotion exaggeration (0.5 neutral -> 1.0 very dramatic), cfg = pacing (lower = slower, more deliberate).
Generates N takes per line; pick_takes.py picks the best by Whisper accuracy + expressiveness."""
import sys, os, torch, torchaudio as ta
from chatterbox.tts import ChatterboxTTS
from script import SEGMENTS
OUT, TAKES = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 2
os.makedirs(f"{OUT}/takes", exist_ok=True)
torch.set_num_threads(4)
# Calm, natural narration by default; dramatic only on the key beats. Kept <= 0.75 so the voice never distorts.
N, BUILD, DRAMA, PEAK = (0.5, 0.5), (0.58, 0.45), (0.68, 0.4), (0.75, 0.4)
DIRECTION = {  # index: ((exaggeration, cfg_weight), optional TTS text)
 0: (PEAK, "Enjoy waiting here... until five P.M."), 1: (BUILD, "Her boss said that... to her face."),
 2: (N, "So she put it in writing. And sent it straight to H.R."), 3: (N, None), 4: (N, None), 5: (N, None),
 6: (DRAMA, "...Yet."), 7: (N, "Then suddenly, her assignments start changing."), 8: (N, "First? A solo home visit."),
 9: (BUILD, "Seventy miles away. Two hours each way."), 10: (N, None), 11: (N, None),
 12: (N, "And she has a special needs daughter who needs her nearby."), 13: (BUILD, None), 14: (DRAMA, None),
 15: (DRAMA, None), 16: (PEAK, "And that's when it gets... ugly."), 17: (BUILD, "Thursday. Eleven thirty A.M."),
 18: (N, None), 19: (N, None), 20: (BUILD, None), 21: (DRAMA, None), 22: (N, "Then."), 23: (DRAMA, None),
 24: (N, "Then."), 25: (DRAMA, None), 26: (N, None), 27: (N, None), 28: (BUILD, "And on his way out the door..."),
 29: (PEAK, "Enjoy waiting here... until five P.M."), 30: (N, None), 31: (N, None), 32: (N, None),
 33: (BUILD, None), 34: (DRAMA, None), 35: (BUILD, None), 36: (BUILD, "And he says she left something out..."),
 37: (DRAMA, "A working computer. That she refused to use."), 38: (BUILD, None), 39: (N, None),
}
REF = "assets/voice/narrator_ref.wav"   # one fixed voice for every line
m = ChatterboxTTS.from_pretrained(device="cpu")
only = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else range(len(SEGMENTS))
for i in only:
    (ex, cfg), txt = DIRECTION[i]; txt = txt or SEGMENTS[i]["say"]
    for k in range(TAKES):
        fn = f"{OUT}/takes/seg_{i:02d}_t{k}.wav"
        if os.path.exists(fn): continue
        torch.manual_seed(1000 * i + k + 17)
        w = m.generate(txt, audio_prompt_path=REF, exaggeration=ex, cfg_weight=cfg, temperature=0.7)
        ta.save(fn, w, m.sr); print(i, k, round(w.shape[1] / m.sr, 2), txt, flush=True)
print("ALL DONE")
