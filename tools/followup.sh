#!/bin/sh
cd "$(dirname "$0")/.."
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
until grep -q ALLDONE output/render.log; do sleep 20; done
# quick floor preview (3 frames) for QA
ALG_OUT='C:\Users\mosto\Desktop\algora\output\test_frames' ALG_STEP=70 ALG_SPP=16 ALG_W=640 ALG_H=360 "$B" -b -P blender/film.py -- floor 2>&1 | grep -E "FRAME|Error"
rm -f output/frames/floor/f_*.png
for f in $(seq 0 80); do rm -f output/frames/hero/f_$(printf %04d $f).png; done
"$B" -b -P blender/film.py -- hero 0 80 2>&1 | grep -E "Error|Traceback"
"$B" -b -P blender/film.py -- floor 2>&1 | grep -E "Error|Traceback"
echo "FOLLOWUP hero=$(ls output/frames/hero/f_*.png | wc -l) floor=$(ls output/frames/floor/f_*.png | wc -l)"
