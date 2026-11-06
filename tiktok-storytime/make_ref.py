"""Generates a calm, natural reference read in Chatterbox's default voice. Every narration line is
cloned from this one clip so the narrator stays the same person throughout."""
import torch, torchaudio as ta
from chatterbox.tts import ChatterboxTTS
torch.set_num_threads(4)
m = ChatterboxTTS.from_pretrained(device="cpu")
TXT = ("So this happened at work last week, and honestly, I still can't believe it. "
       "I'll tell you the whole story, from the very beginning, and you can decide for yourself.")
for k in range(3):
    torch.manual_seed(500 + k)
    w = m.generate(TXT, exaggeration=0.5, cfg_weight=0.5, temperature=0.7)
    ta.save(f"build_cb2/ref_{k}.wav", w, m.sr); print(k, w.shape[1] / m.sr, flush=True)
