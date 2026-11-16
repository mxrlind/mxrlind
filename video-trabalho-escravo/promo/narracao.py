"""Roteiro da narração + geração da voz (Kokoro TTS, pt-BR, offline).

Cada cena tem uma lista de falas ("cues"). A voz de cada fala é gerada separadamente,
o que dá o instante exato em que cada fala começa. Esses instantes vão para cues.js,
que o video.html usa para sincronizar as animações com a narração.

Uso: python3 narracao.py MODEL_DIR   (pasta com kokoro-v1.0.onnx e voices-v1.0.bin)
Saídas: cues.js, out/narracao.wav
"""
import json, os, sys, hashlib
import numpy as np

ROTEIRO = [
  ("gancho", [
    "Tem um trabalho da faculdade pra apresentar,",
    "e não sabe como deixar interessante?",
  ]),
  ("transforma", [
    "Eu transformo o seu trabalho em um vídeo animado,",
    "bonito, dinâmico e fácil de entender.",
  ]),
  ("passos", [
    "É simples:",
    "você me manda o PDF ou o Word,",
    "eu monto o roteiro e as animações,",
    "e você recebe o vídeo pronto pra apresentar.",
  ]),
  ("inclui", [
    "O vídeo vem com um resumo sem textão, animações, música de fundo,",
    "narração, se você quiser,",
    "e os créditos com o nome do grupo e do professor.",
  ]),
  ("exemplo", [
    "Olha um exemplo de verdade:",
    "um trabalho de Psicologia que virou um vídeo narrado, com o caso real em destaque.",
  ]),
  ("precos", [
    "Os valores:",
    "vídeo animado com música, de até três minutos, cinquenta reais.",
    "Vídeo completo, com narração, de até dez minutos, noventa reais.",
    "E, se for pra amanhã, entrega expressa por mais vinte.",
  ]),
  ("grupo", [
    "Dividindo no grupo de cinco,",
    "o vídeo completo sai por dezoito reais pra cada um.",
  ]),
  ("cta", [
    "Chama no WhatsApp e manda o seu trabalho!",
  ]),
]

VOICE, SPEED = "pf_dora", 1.15
LEAD, GAP, TAIL = 0.45, 0.25, 0.8      # segundos: antes da 1ª fala, entre falas, depois da última
SR = 24000
EXTRA = {"exemplo": 2.5, "precos": 1.0, "cta": 3.5}   # segundos a mais em cenas que precisam de tempo de leitura

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    model_dir = sys.argv[1]
    cache = os.path.join(here, "out", "tts_cache"); os.makedirs(cache, exist_ok=True)
    from kokoro_onnx import Kokoro
    import soundfile as sf
    k = Kokoro(os.path.join(model_dir, "kokoro-v1.0.onnx"), os.path.join(model_dir, "voices-v1.0.bin"))

    def tts(text):
        h = hashlib.sha1(f"{VOICE}|{SPEED}|{text}".encode()).hexdigest()[:16]
        f = os.path.join(cache, h + ".wav")
        if not os.path.exists(f):
            s, sr = k.create(text, voice=VOICE, speed=SPEED, lang="pt-br")
            assert sr == SR
            # corta silêncio nas pontas
            idx = np.where(np.abs(s) > 0.01)[0]
            s = s[max(0, idx[0] - 240): idx[-1] + 2400]
            sf.write(f, s, SR)
        return sf.read(f)[0]

    cues, chunks, t = {}, [], 0.0
    for sid, falas in ROTEIRO:
        start = t; local = LEAD; starts, lens = [], []
        audio = []
        for fala in falas:
            a = tts(fala)
            starts.append(round(local, 3)); lens.append(round(len(a) / SR, 3))
            audio.append((local, a)); local += len(a) / SR + GAP
        dur = round(local - GAP + TAIL + EXTRA.get(sid, 0), 2)
        cues[sid] = {"dur": dur, "c": starts, "len": lens}
        chunks.append((start, audio)); t += dur
        print(f"{sid:14s} {dur:6.2f}s  (início {start:6.1f}s)")
    total = t
    mix = np.zeros(int((total + 1) * SR), dtype=np.float32)
    for start, audio in chunks:
        for local, a in audio:
            i = int((start + local) * SR); mix[i:i + len(a)] += a
    mix = mix / max(1e-6, np.abs(mix).max()) * 0.95
    sf.write(os.path.join(here, "out", "narracao.wav"), mix, SR)
    with open(os.path.join(here, "cues.js"), "w") as f:
        f.write("window.__CUES = " + json.dumps(cues, ensure_ascii=False) + ";\n")
    print(f"TOTAL {total:.1f}s = {int(total // 60)}min{int(total % 60):02d}s")
