"""Mix narration with one continuous stretch of the user's song (starting at plan['song_start']).
The song's own silence carries "So she says no" and its beat return lands on "Thursday".
Writes mix.wav (voice + song + light sfx) and mix_nomusic.wav (voice + light sfx, for adding the sound in TikTok).
usage: python audio_batida.py <build_dir> <song.mp3>
"""
import json, subprocess, sys
import numpy as np, soundfile as sf
from script import SEGMENTS

B, SONG = sys.argv[1], sys.argv[2]
SR = 48000
plan = json.load(open(f"{B}/plan.json")); timing = json.load(open(f"{B}/timing.json"))
T = plan["total"]; S = plan["song_start"]; N = int(T * SR); t = np.arange(N) / SR

# voice: light polish only (no pitch or reverb), keep it natural
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{B}/voice_raw.wav", "-af",
                "aresample=48000,highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=6:release=120:makeup=2",
                "-ac", "1", f"{B}/voice.wav"], check=True)
v_, _ = sf.read(f"{B}/voice.wav"); v = np.zeros(N); v[:min(N, len(v_))] = v_[:N]

subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{S:.3f}", "-t", f"{T + 0.5:.3f}", "-i", SONG,
                "-ar", str(SR), "-ac", "2", f"{B}/song_cut.wav"], check=True)
m_, _ = sf.read(f"{B}/song_cut.wav"); m = np.zeros((N, 2)); m[:min(N, len(m_))] = m_[:N]
m *= (np.clip(t / 0.03, 0, 1) * np.clip((T - t) / 1.8, 0, 1))[:, None]

# ducking: music dips under the voice and swells in the gaps
env = np.convolve(np.abs(v), np.ones(int(0.04 * SR)) / int(0.04 * SR), "same")
act = (env > 0.008).astype(float)
act = np.clip(np.convolve(act, np.ones(int(0.3 * SR)) / int(0.3 * SR), "same") * 2.5, 0, 1)
m *= (1.0 - 0.75 * act)[:, None]

# light sfx: only a low thump under the quote cards and the stamp moments (the song carries the energy)
rng = np.random.default_rng(3)
def thump():
    n = int(0.9 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * (70 * tt - 30 * tt ** 2)) * np.exp(-tt / 0.25)
def ding():
    n = int(1.0 * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1318.5 * tt) * np.exp(-tt / .25) + np.sin(2 * np.pi * 1975.5 * np.clip(tt - .12, 0, None)) * np.exp(-tt / .3) * (tt > .12)) * 0.3
sfx = np.zeros(N)
for seg, s in zip(timing, SEGMENTS):
    kind = s.get("sfx")
    x = ding() if kind == "ding" else thump() * 0.6 if (s["k"] == "card" or kind in ("stamp", "hit")) else None
    if x is not None:
        i = max(0, int((seg["start"] - 0.03) * SR)); sfx[i:i + len(x)] += x[:N - i]

def finish(mix, name):
    mix = mix / np.max(np.abs(mix)) * 0.95; sf.write(f"{B}/{name}_raw.wav", mix, SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{B}/{name}_raw.wav", "-af", "loudnorm=I=-14:TP=-1.0:LRA=11",
                    "-ar", "48000", f"{B}/{name}.wav"], check=True)
vv = np.stack([v, v], 1); ss = np.stack([sfx, sfx], 1)
finish(vv * 1.0 + m * 0.5 + ss * 0.25, "mix")
finish(vv * 1.0 + ss * 0.25, "mix_nomusic")
print(f"audio done {T:.2f}s, song from {S:.3f}s to {S + T:.3f}s")
