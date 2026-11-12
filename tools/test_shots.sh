#!/bin/sh
# render sparse test frames of every shot -> output/test_frames/<shot>
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
export ALG_OUT='C:\Users\mosto\Desktop\algora\output\test_frames' ALG_STEP=${STEP:-60}
for s in ${SHOTS:-hero wall floor lamp roof}; do
  "$B" -b -P blender/film.py -- $s 2>&1 | grep -E "FRAME|Error|Traceback|line [0-9]"
done
echo DONE
