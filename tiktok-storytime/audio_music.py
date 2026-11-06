"""Mixes narration + sax track (with tape-stop cut and sax-entry re-entry) + SFX.
Also writes mix_nomusic.wav (voice + SFX only) so a TikTok sound can be added in-app.
usage: python audio_music.py <build_dir>"""
import json, subprocess, sys
import numpy as np, soundfile as sf
from script import SEGMENTS

B = sys.argv[1]
SR = 48000
plan = json.load(open(f"{B}/plan.json")); timing = json.load(open(f"{B}/timing.json"))
rng = np.random.default_rng(7)

subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{B}/voice_raw.wav", "-af",
    "aresample=48000,highpass=f=60,equalizer=f=3000:t=q:w=1.5:g=1.5,"
    "acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120:makeup=2",
    "-ac", "1", f"{B}/voice.wav"], check=True)
voice, _ = sf.read(f"{B}/voice.wav")
T = plan["total"]; N = int(T * SR); t = np.arange(N) / SR
v = np.zeros(N); v[:min(N, len(voice))] = voice[:N]

subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "assets/music/rosemarylynn_slow.mp3", "-ar", str(SR), "-ac", "1",
                f"{B}/music_full.wav"], check=True)
mus, _ = sf.read(f"{B}/music_full.wav")
def mseg(m0, m1): return mus[int(m0 * SR):int(m1 * SR)].copy()

music = np.zeros(N)
cut, thurs = plan["cut"], plan["thurs"]
# A: intro, ending exactly on the sax-entry downbeat at the cut
a = mseg(plan["music_a_start"], plan["sax_in"])
# tape-stop over the last 0.7s before the cut
ts = int(0.7 * SR); tail = a[-ts:]
speed = np.linspace(1.0, 0.05, ts) ** 1.5; pos = np.cumsum(speed); pos = pos / pos[-1] * (ts - 1) * 0.55
a[-ts:] = np.interp(pos, np.arange(ts), tail) * np.linspace(1, 0, ts) ** 0.5
music[:len(a)] = a[:N]
# C: from the sax entry, starting at "Thursday"
c = mseg(plan["sax_in"], plan["sax_in"] + (T - thurs) + 1)
i0 = int(thurs * SR); n = min(len(c), N - i0); music[i0:i0 + n] = c[:n]
music *= np.clip(t / 0.15, 0, 1) * np.clip((T - t) / 2.2, 0, 1)

# ducking: music sits under the voice, swells in the gaps
env = np.abs(v); w = int(0.05 * SR)
env = np.convolve(env, np.ones(w) / w, "same"); act = (env > 0.01).astype(float)
rel = int(0.35 * SR); act = np.maximum.accumulate(act) if False else act
k = np.ones(rel) / rel; act = np.clip(np.convolve(act, k, "full")[:N] * 3, 0, 1)
duck = 1.0 - 0.68 * act
music *= duck

# ---- SFX ----
def env_exp(n, tau): return np.exp(-np.arange(n) / (tau * SR))
def boom():
    n = int(1.6 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * (85 * tt - 45 * tt ** 2 / 1.6)) * env_exp(n, 0.45) + np.convolve(rng.standard_normal(n) * env_exp(n, 0.02), np.ones(30) / 30, "same") * 0.6
def whoosh():
    n = int(0.5 * SR); x = np.convolve(rng.standard_normal(n), np.ones(12) / 12, "same"); return x * np.sin(np.pi * np.linspace(0, 1, n)) ** 2 * 1.2
def stamp():
    n = int(0.45 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * 70 * tt) * env_exp(n, 0.07) + rng.standard_normal(n) * env_exp(n, 0.01) * 0.8
def glitch():
    n = int(0.4 * SR); x = np.round(rng.standard_normal(n) * 3) / 3 * (np.sin(2 * np.pi * 23 * np.arange(n) / SR) > 0); return x * 0.3 * env_exp(n, 0.25)
def ding():
    n = int(1.1 * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1318.5 * tt) * env_exp(n, .25) + np.sin(2 * np.pi * 1975.5 * np.clip(tt - .12, 0, None)) * env_exp(n, .3) * (tt > .12)) * 0.35
FX = dict(boom=(boom, -0.06, 0.4), hit=(boom, -0.04, 0.9), whoosh=(whoosh, -0.28, 0.3), stamp=(stamp, -0.02, 0.8),
          glitch=(glitch, 0.0, 0.7), ding=(ding, -0.05, 0.8))
sfx = np.zeros(N)
for seg, s in zip(timing, SEGMENTS):
    if "sfx" in s:
        fn, off, g = FX[s["sfx"]]; x = fn() * g; i = max(0, int((seg["start"] + off) * SR)); sfx[i:i + len(x)] += x[:N - i]

def finish(mix, name):
    mix = np.stack([mix, mix], 1); mix = mix / np.max(np.abs(mix)) * 0.95
    sf.write(f"{B}/{name}_raw.wav", mix, SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{B}/{name}_raw.wav", "-af", "loudnorm=I=-14:TP=-1.0:LRA=11",
                    "-ar", "48000", f"{B}/{name}.wav"], check=True)
finish(v * 1.0 + music * 0.38 + sfx * 0.3, "mix")
finish(v * 1.0 + sfx * 0.3, "mix_nomusic")
print("audio done", round(T, 2))
