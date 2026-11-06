"""Free, local, expressive narration with Orpheus 3B (Apache-2.0 / Llama 3.2) via llama.cpp + SNAC decoder.
Generates a whole paragraph at once so the delivery flows naturally (not sentence by sentence).
usage: python orpheus_tts.py <gguf> <voice> <text_file> <out.wav> [temperature]
Voices: tara, leah, jess, leo, dan, mia, zac, zoe. Emotion tags: <sigh> <gasp> <chuckle> <laugh> <groan>
"""
import sys, time, numpy as np, soundfile as sf, torch
from llama_cpp import Llama
from snac import SNAC

GGUF, VOICE, TXT, OUT = sys.argv[1:5]
TEMP = float(sys.argv[5]) if len(sys.argv) > 5 else 0.6
CUSTOM0 = 128256                         # id of <custom_token_0>
END_SPEECH, EOT = 128258, 128009

llm = Llama(model_path=GGUF, n_ctx=8192, n_threads=4, n_batch=512, verbose=False)
snac = SNAC.from_pretrained("hubertsiuzdak/snac_24khz").eval()

def synth(text):
    prompt = f"<|audio|>{VOICE}: {text}<|eot_id|>"
    toks = llm.tokenize(prompt.encode(), add_bos=True, special=True)
    codes, t0 = [], time.time()
    max_new = int(len(text) * 9 + 600)           # ~84 tokens per second of speech
    for n, tok in enumerate(llm.generate(toks, temp=TEMP, top_p=0.9, repeat_penalty=1.1)):
        if tok in (END_SPEECH, EOT) or n > max_new: break
        if tok >= CUSTOM0 + 10:
            c = tok - CUSTOM0 - 10 - (len(codes) % 7) * 4096
            if 0 <= c < 4096: codes.append(c)
    print(f"  {len(codes)} codes in {time.time() - t0:.0f}s", flush=True)
    codes = codes[: len(codes) // 7 * 7]
    f = np.array(codes).reshape(-1, 7)
    l0 = torch.tensor(f[:, 0])[None]
    l1 = torch.tensor(f[:, [1, 4]].reshape(-1))[None]
    l2 = torch.tensor(f[:, [2, 3, 5, 6]].reshape(-1))[None]
    with torch.inference_mode():
        audio = snac.decode([l0, l1, l2]).squeeze().numpy()
    return audio

# split long text into paragraphs (blank-line separated) to stay inside the model's comfort zone
paras = [p.strip().replace("\n", " ") for p in open(TXT).read().split("\n\n") if p.strip()]
out = []
for i, p in enumerate(paras):
    print(f"para {i + 1}/{len(paras)}: {p[:60]}…", flush=True)
    out += [synth(p), np.zeros(int(24000 * 0.35))]
sf.write(OUT, np.concatenate(out), 24000)
print("wrote", OUT, round(sum(len(x) for x in out) / 24000, 1), "s")
