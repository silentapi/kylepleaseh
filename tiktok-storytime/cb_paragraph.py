"""Chatterbox, whole paragraphs at once (natural flow), same fixed narrator reference voice."""
import sys, torch, torchaudio as ta, numpy as np
from chatterbox.tts import ChatterboxTTS
TXT, OUT = sys.argv[1], sys.argv[2]
torch.set_num_threads(4)
m = ChatterboxTTS.from_pretrained(device="cpu")
paras = [p.strip().replace("\n", " ") for p in open(TXT).read().split("\n\n") if p.strip()]
outs = []
for i, p in enumerate(paras):
    torch.manual_seed(11 + i)
    w = m.generate(p, audio_prompt_path="assets/voice/narrator_ref.wav", exaggeration=0.6, cfg_weight=0.45, temperature=0.7)
    outs += [w, torch.zeros(1, int(m.sr * 0.35))]
ta.save(OUT, torch.cat(outs, 1), m.sr); print("wrote", OUT)
