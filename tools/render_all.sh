#!/bin/sh
# Final render queue (auto-resume: existing frames are skipped). Log: output/render.log
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
cd "$(dirname "$0")/.."
for s in ${SHOTS:-hero lamp floor wall roof}; do
  for try in 1 2 3; do
    "$B" -b -P blender/film.py -- $s 2>&1 | grep --line-buffered -E "FRAME|Error|Traceback|line [0-9]" >> output/render.log
    n=$(ls output/frames/$s/f_*.png 2>/dev/null | wc -l)
    echo "SHOT $s frames=$n try=$try" >> output/render.log
    case $s in hero) need=270;; wall) need=180;; *) need=150;; esac
    [ "$n" -ge "$need" ] && break
  done
done
echo ALLDONE >> output/render.log
