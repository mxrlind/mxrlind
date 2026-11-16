"""Gera a trilha sonora (ambiente + efeitos) sincronizada com out/timeline.json.
Uso: python3 trilha.py  ->  out/trilha.wav
"""
import json, wave, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
tl = json.load(open(os.path.join(HERE, 'out', 'timeline.json')))
SR = 44100
TOTAL = tl['total']
N = int((TOTAL + 1) * SR)
rng = np.random.default_rng(11)
L = np.zeros(N); R = np.zeros(N)

def hz(note):  # MIDI -> Hz
    return 440.0 * 2 ** ((note - 69) / 12)

def lowpass(x, fc, order=2):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / fc) ** (2 * order))
    return np.fft.irfft(X, len(x))

def bandpass(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= (1 / np.sqrt(1 + (lo / np.maximum(f, 1)) ** 4)) * (1 / np.sqrt(1 + (f / hi) ** 4))
    return np.fft.irfft(X, len(x))

def add(buf, start_s, sig):
    i = int(start_s * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]

# ---- harmonia por trecho (acordes de 8 s) ----
A, F, C, G, Dm, E, Am = [57, 60, 64], [53, 57, 60], [48, 52, 55, 60], [55, 59, 62], [50, 53, 57], [52, 56, 59], [57, 60, 64]
MAJ = True
case_start = next((s['start'] for s in tl['scenes'] if s['light']), 1e9)
case_end = max([s['start'] + s['dur'] for s in tl['scenes'] if s['light']] or [1e9])
credits_start = tl['scenes'][-1]['start']

def chord_at(t):
    k = int(t // SEG)
    if case_start <= t < case_end:
        return [Dm, Am, F, E][k % 4], 'case'
    if t >= case_end:
        return [F, C, G, Am][k % 4] if t < credits_start - 8 else [F, C, F, C][k % 4], 'hope'
    return ([C, G, Am, F] if MAJ else [Am, F, C, G])[k % 4], 'main'

SEG = 4.0
t = 0.0
while t < TOTAL:
    chord, mood = chord_at(t + 0.01)
    dur = SEG + 3.0
    n = int(dur * SR); tt = np.arange(n) / SR
    env = np.minimum(1, tt / 2.2) * np.clip((dur - tt) / 3.0, 0, 1)
    env = np.sin(env * np.pi / 2) ** 2
    padL = np.zeros(n); padR = np.zeros(n)
    for note in chord + [chord[0] + 12]:
        f0 = hz(note)
        for h in range(1, 7):
            amp = 1 / h ** 1.5
            for det, side in ((-0.0025, 0), (0.0, 2), (0.0025, 1)):
                ph = rng.uniform(0, 2 * np.pi)
                s = amp * np.sin(2 * np.pi * f0 * h * (1 + det) * tt + ph)
                if side in (0, 2): padL += s
                if side in (1, 2): padR += s
    lfo = 1 + 0.12 * np.sin(2 * np.pi * 0.15 * tt + t)
    padL *= env * lfo; padR *= env * lfo
    add(L, t, padL * 0.010); add(R, t, padR * 0.010)
    # baixo
    b = np.sin(2 * np.pi * hz(chord[0] - 24) * tt) + 0.3 * np.sin(2 * np.pi * hz(chord[0] - 12) * tt)
    add(L, t, b * env * 0.05); add(R, t, b * env * 0.05)
    # arpejo (pluck) — mais esparso no caso real, ausente no início
    if t >= 0 and t < TOTAL - 2:
        step = 0.25 if mood != 'case' else 1.0
        tones = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[0] + 24]
        pattern = [0, 1, 2, 1, 3, 2, 1, 2] if mood != 'case' else [0, 2, 1, 3]
        for i in range(int(SEG / step)):
            note = tones[pattern[i % len(pattern)]]
            m = int(1.6 * SR); pt = np.arange(m) / SR
            pl = (np.sin(2 * np.pi * hz(note) * pt) + 0.25 * np.sin(4 * np.pi * hz(note) * pt)) * np.exp(-pt / 0.45) * np.minimum(1, pt / 0.004)
            vel = 0.055 if mood != 'case' else 0.045
            vel *= 0.85 + 0.3 * rng.random()
            pan = 0.5 + 0.35 * np.sin(i * 1.3)
            st = t + i * step
            for e, g in enumerate([1, 0.35, 0.14]):  # eco
                add(L, st + e * 0.375, pl * vel * g * (1 - pan) * 2)
                add(R, st + e * 0.375 + 0.011, pl * vel * g * pan * 2)
    t += SEG

L = lowpass(L, 2600); R = lowpass(R, 2600)

# ---- efeitos ----
for k, s in enumerate(tl['scenes']):
    if k > 0:  # whoosh na troca de cena
        n = int(1.1 * SR); tt = np.arange(n) / SR
        noise = bandpass(rng.standard_normal(n), 350, 3800)
        env = np.where(tt < 0.55, (tt / 0.55) ** 2.5, np.exp(-(tt - 0.55) / 0.12))
        w = noise * env * 0.045
        add(L, s['start'] - 0.55, w); add(R, s['start'] - 0.53, w)
    if s['sfx'] == 'hit':
        at = s['start'] + (0.55 if not s['light'] else 0.95)
        n = int(2.5 * SR); tt = np.arange(n) / SR
        freq = 48 + 50 * np.exp(-tt / 0.08)
        boom = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-tt / 0.7)
        click = bandpass(rng.standard_normal(n), 120, 2500) * np.exp(-tt / 0.05) * 0.5
        hit = (boom + click) * 0.2
        add(L, at, hit); add(R, at, hit)

# fade in/out geral
env = np.ones(N); tt = np.arange(N) / SR
env *= np.clip(tt / 2.0, 0, 1)
env *= np.clip((TOTAL + 0.5 - tt) / 5.0, 0, 1)
L *= env; R *= env
peak = max(np.abs(L).max(), np.abs(R).max())
L /= peak / 0.89; R /= peak / 0.89

# ---- narração + ducking (a música abaixa enquanto a voz fala) ----
nar_path = os.path.join(HERE, 'out', 'narracao.wav')
if os.path.exists(nar_path):
    with wave.open(nar_path) as w:
        vsr = w.getframerate(); raw = w.readframes(w.getnframes()); sw = w.getsampwidth()
    v = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768 if sw == 2 else None
    if v is None:  # soundfile grava PCM_16 por padrão; fallback
        raise SystemExit('narracao.wav deve ser PCM 16 bits')
    # reamostragem por FFT (24 kHz -> 44,1 kHz)
    m = int(round(len(v) * SR / vsr))
    V = np.fft.rfft(v); Vn = np.zeros(m // 2 + 1, dtype=complex); k = min(len(V), len(Vn)); Vn[:k] = V[:k]
    v = np.fft.irfft(Vn, m) * (m / len(v))
    voice = np.zeros(N); voice[:min(N, len(v))] = v[:N]
    # envelope da voz -> ganho da música
    def movavg(x, w):  # média móvel centrada (O(N), via soma acumulada)
        c = np.concatenate([[0], np.cumsum(x)]); h = w // 2
        i = np.arange(len(x)); a = np.clip(i - h, 0, len(x)); b = np.clip(i + h + 1, 0, len(x))
        return (c[b] - c[a]) / (b - a)
    def trailing(x, w):  # média móvel olhando para trás (release)
        c = np.concatenate([[0], np.cumsum(x)]); i = np.arange(len(x)); a = np.clip(i + 1 - w, 0, None)
        return (c[i + 1] - c[a]) / w
    win = int(0.08 * SR)
    e = np.sqrt(movavg(voice ** 2, win))
    speaking = (e > 0.02).astype(float)
    att, rel = int(0.12 * SR), int(0.7 * SR)
    sm = trailing(speaking, rel)                      # solta devagar
    sm = np.maximum(sm, movavg(speaking, att))
    sm = np.clip(sm * 1.5, 0, 1)
    duck = 1 - 0.55 * sm
    music_gain = 0.42
    L = L * music_gain * duck + voice * 0.92
    R = R * music_gain * duck + voice * 0.92
    peak = max(np.abs(L).max(), np.abs(R).max())
    if peak > 0.98: L /= peak / 0.98; R /= peak / 0.98

out_name = 'mix.wav' if os.path.exists(nar_path) else 'trilha.wav'
stereo = (np.stack([L, R], 1) * 32767).astype(np.int16)
with wave.open(os.path.join(HERE, 'out', out_name), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(stereo.tobytes())
print('ok', out_name, TOTAL)
