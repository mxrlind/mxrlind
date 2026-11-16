# Vídeo — Trabalho escravo contemporâneo (POT · AV1 · UNIFESO)

Vídeo narrado em motion graphics (1920×1080, 30 fps, **8min48s**) que apresenta o trabalho
**"Psicologia Organizacional e do Trabalho: desafios contemporâneos"**, com destaque para o caso real
da trabalhadora resgatada (g1 Ceará, jul. 2026) e créditos das autoras e do professor no final.

- `trabalho-escravo-contemporaneo.mp4`: vídeo final (narração + trilha).
- `roteiro-narracao.md`: texto completo da narração, cena a cena, com tempos.
- `video.html`: o vídeo em si; abra no navegador e clique para tocar com o áudio (`?t=120` começa no segundo 120).
- `narracao.py`: roteiro + geração da voz (Kokoro TTS, voz `pf_dora`, pt-BR, offline) e dos tempos (`cues.js`).
- `render.mjs`, `trilha.py`, `build.sh`: geram quadros, trilha com ducking e o MP4.

As animações são sincronizadas com a fala: cada elemento entra quando a frase correspondente é narrada.

## Regerar
```bash
pip install kokoro-onnx soundfile numpy
# modelo: github.com/thewh1teagle/kokoro-onnx/releases (model-files-v1.0: kokoro-v1.0.onnx e voices-v1.0.bin)
./build.sh /caminho/do/modelo
```
