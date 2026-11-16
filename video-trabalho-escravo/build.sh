#!/usr/bin/env bash
# Gera o vídeo final: narração (Kokoro TTS) -> quadros (Playwright, 3 partes em paralelo) -> trilha+mix -> MP4
# Uso: ./build.sh PASTA_DO_MODELO   (pasta com kokoro-v1.0.onnx e voices-v1.0.bin)
set -euo pipefail
cd "$(dirname "$0")"
python3 narracao.py "$1"
node render.mjs video 0 3 & node render.mjs video 1 3 & node render.mjs video 2 3 & wait
python3 trilha.py
printf "file 'part_0.mp4'\nfile 'part_1.mp4'\nfile 'part_2.mp4'\n" > out/parts.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i out/parts.txt -i out/mix.wav -map 0:v -map 1:a -c:v copy \
  -af "loudnorm=I=-16:TP=-1.5:LRA=9" -ar 48000 -c:a aac -b:a 160k -shortest -movflags +faststart \
  trabalho-escravo-contemporaneo.mp4
ffmpeg -y -loglevel error -i trabalho-escravo-contemporaneo.mp4 -vn -c:a copy trabalho-escravo-contemporaneo.m4a
echo "OK -> trabalho-escravo-contemporaneo.mp4"
