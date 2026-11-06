"""Synthesizes the music bed + sound effects (no samples, no licenses needed) and mixes with the narration."""
import json, sys, subprocess, numpy as np, soundfile as sf
from script import SEGMENTS
B = sys.argv[1]
SR = 48000
rng = np.random.default_rng(7)
timing = json.load(open(f"{B}/timing.json"))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{B}/voice_raw.wav", "-af",
    "aresample=48000,equalizer=f=110:t=q:w=1.2:g=3,equalizer=f=3500:t=q:w=1.5:g=2,"
    "acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2,aecho=0.85:0.5:35|70:0.10|0.06",
    "-ac", "1", f"{B}/voice.wav"], check=True)
voice, _ = sf.read(f"{B}/voice.wav")
T = len(voice) / SR + 0.5
N = int(T * SR); t = np.arange(N) / SR

def env_exp(n, tau): return np.exp(-np.arange(n) / (tau * SR))
def lp(x, a):  # one-pole lowpass
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y
def noise(n): return rng.standard_normal(n)

# ---- music bed: dark detuned drone + sub pulse ----
drone = np.zeros(N)
for f, amp in [(55, 1.0), (55.4, .8), (82.4, .5), (110.2, .35), (130.8, .18), (164.8, .12)]:
    drone += amp * np.sin(2*np.pi*f*t + rng.uniform(0, 6))
drone *= 0.55 + 0.45*np.sin(2*np.pi*0.07*t)          # slow swell
pad = np.convolve(noise(N), np.ones(400)/400, "same") * 2.5  # dark air
music = drone*0.6 + pad*0.3
# heartbeat pulse (lub-dub), gets faster after "Thursday"
thurs = timing[17]["start"]; pulse = np.zeros(N)
def kick(f0=60, dur=0.35):
    n = int(dur*SR); tt = np.arange(n)/SR
    return np.sin(2*np.pi*(f0*tt + 40*(1-np.exp(-tt*30))/30)) * env_exp(n, 0.09)
k1 = kick(); k2 = kick(52) * 0.7
pt = timing[3]["start"]
while pt < T - 1:
    period = 1.05 if pt < thurs else 0.78
    for off, kk in [(0, k1), (0.22, k2)]:
        i = int((pt+off)*SR); pulse[i:i+len(kk)] += kk[:N-i]
    pt += period
music = music/np.max(np.abs(music))*0.5 + pulse*0.55
# clock ticks during the hook
for tick in np.arange(0.1, timing[3]["start"], 0.5):
    n = int(0.03*SR); i = int(tick*SR)
    music[i:i+n] += np.sin(2*np.pi*2400*np.arange(n)/SR)*env_exp(n, 0.004)*0.6
# duck music to silence on "She says no." then slam back in
a, b = timing[15]["start"]-0.05, timing[17]["start"]
gate = np.ones(N); ia, ib = int(a*SR), int(b*SR); gate[ia:ib] = 0.0
gate = np.convolve(gate, np.ones(2400)/2400, "same")
music *= gate
# fade in/out
music *= np.clip(t/1.0, 0, 1) * np.clip((T - t)/2.0, 0, 1)

# ---- SFX ----
def boom():
    n = int(1.8*SR); tt = np.arange(n)/SR
    sub = np.sin(2*np.pi*(90*tt - 50*tt**2/1.8)) * env_exp(n, 0.55)
    hit = noise(n) * env_exp(n, 0.03)
    return sub*1.0 + np.convolve(hit, np.ones(30)/30, "same")*0.8
def whoosh():
    n = int(0.55*SR); x = np.convolve(noise(n), np.ones(12)/12, "same")
    e = np.sin(np.pi*np.linspace(0, 1, n))**2
    return x*e*1.4
def stamp():
    n = int(0.5*SR); tt = np.arange(n)/SR
    return (np.sin(2*np.pi*70*tt)*env_exp(n, 0.08) + noise(n)*env_exp(n, 0.012)*0.9)
def glitch():
    n = int(0.45*SR); x = noise(n)
    x = np.round(x*3)/3 * (np.sin(2*np.pi*23*np.arange(n)/SR) > 0)
    return x*0.35*env_exp(n, 0.25)
def ding():
    n = int(1.2*SR); tt = np.arange(n)/SR
    return (np.sin(2*np.pi*1318.5*tt)*env_exp(n, .25) + np.sin(2*np.pi*1975.5*np.clip(tt-0.12, 0, None))*env_exp(n, .3)*(tt > .12))*0.35
FX = dict(boom=(boom, 0.0, 0.9), hit=(boom, 0.0, 1.2), whoosh=(whoosh, -0.3, 0.45),
          stamp=(stamp, 0.0, 0.9), glitch=(glitch, 0.0, 0.8), ding=(ding, -0.05, 0.9))
sfx = np.zeros(N)
for seg, s in zip(timing, SEGMENTS):
    if "sfx" in s:
        fn, off, g = FX[s["sfx"]]; x = fn() * g
        start = seg["start"] + off
        if s["sfx"] == "stamp" or s["k"] == "card": start = seg["start"] - 0.02
        i = max(0, int(start*SR)); sfx[i:i+len(x)] += x[:N-i]

v = np.zeros(N); v[:len(voice)] = voice
mix = v*1.0 + music*0.16 + sfx*0.32
mix = np.stack([mix, mix], 1)
sf.write(f"{B}/mix_raw.wav", mix/np.max(np.abs(mix))*0.95, SR)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{B}/mix_raw.wav", "-af",
    "loudnorm=I=-14:TP=-1.0:LRA=9", "-ar", "48000", f"{B}/mix.wav"], check=True)
print("audio done", round(T, 2))
