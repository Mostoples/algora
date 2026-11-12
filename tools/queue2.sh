#!/bin/sh
# Resume queue: wall (resume) -> roof -> hero 0-80 redo -> floor redo. Detached-safe, auto-resume.
cd /c/Users/mosto/Desktop/algora
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
log=output/render.log
SHOTS="wall roof" ./tools/render_all.sh
if [ ! -f output/frames/.hero_redo ]; then
  for f in $(seq 0 80); do rm -f output/frames/hero/f_$(printf %04d $f).png; done
  touch output/frames/.hero_redo
fi
"$B" -b -P blender/film.py -- hero 0 80 2>&1 | grep -E "Error|Traceback" >> $log
if [ ! -f output/frames/.floor_redo ]; then rm -f output/frames/floor/f_*.png; touch output/frames/.floor_redo; fi
SHOTS="floor" ./tools/render_all.sh
echo "QUEUE2DONE hero=$(ls output/frames/hero/f_*.png | wc -l) floor=$(ls output/frames/floor/f_*.png | wc -l) wall=$(ls output/frames/wall/f_*.png | wc -l) roof=$(ls output/frames/roof/f_*.png | wc -l)" >> $log
