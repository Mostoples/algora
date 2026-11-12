#!/bin/sh
# Render video gambar teknik (detached-safe, auto-resume).
cd /c/Users/mosto/Desktop/algora
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
OUT="C:/Users/mosto/Desktop/algora/output/frames/tech"
ALG_OUT="$OUT" ALG_SPP=32 "$B" -b -P blender/tech_video.py 2>&1 | grep -E "FRAME|Error|Traceback" > output/render_tech.log
echo "TECHDONE $(ls output/frames/tech/f_*.png | wc -l)" >> output/render_tech.log
