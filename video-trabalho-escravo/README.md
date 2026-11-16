# Vídeo — Trabalho escravo contemporâneo (POT · AV1 · UNIFESO)

Vídeo animado (motion graphics, 1920×1080, 30 fps, ~3min55s) que resume o trabalho
**"Psicologia Organizacional e do Trabalho: desafios contemporâneos"**, com destaque
para o caso real da trabalhadora resgatada (g1 Ceará, jul. 2026) e créditos das autoras e do professor no final.

- `trabalho-escravo-contemporaneo.mp4` — vídeo final com trilha sonora.
- `video.html` — o vídeo em si (abra no navegador para ver ao vivo; clique para pausar; `?t=120` começa no segundo 120).
- `render.mjs` / `trilha.py` / `build.sh` — geram o MP4 a partir do HTML.

## Roteiro (cenas)
| # | Tempo | Cena |
|---|-------|------|
| 1–2 | 0:00 | Gancho (abolição de 1888) e título |
| 3–7 | 0:15 | Contexto e conceitos: trabalho digno, art. 149, controle sem correntes, servidão por dívida |
| 8–9 | 1:06 | Causas: fatores sociais (Figueira) e cadeias produtivas/terceirização |
| 10–11 | 1:30 | Impactos: saúde pública (Leão) e sofrimento psicossocial |
| 12–16 | 1:52 | **Caso real**: 7 → 62 anos, 55 anos com a mesma família, o que a fiscalização viu, o outro lado, e depois do resgate |
| 17–20 | 2:44 | Enfrentamento: políticas públicas, papel da POT, ética, rede |
| 21–22 | 3:33 | Conclusão + créditos (professor e autoras) |

## Regerar
```bash
./build.sh   # requer node + playwright (chromium), python3 + numpy, ffmpeg
```
