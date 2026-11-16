#!/usr/bin/env bash
# Gera o vídeo final: quadros (Playwright) -> trilha (numpy) -> MP4 com áudio
set -euo pipefail
cd "$(dirname "$0")"
node render.mjs video
python3 trilha.py
ffmpeg -y -loglevel error -i out/video_noaudio.mp4 -i out/trilha.wav \
  -af "loudnorm=I=-18:TP=-1.5:LRA=7" -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart \
  trabalho-escravo-contemporaneo.mp4
echo "OK -> trabalho-escravo-contemporaneo.mp4"
