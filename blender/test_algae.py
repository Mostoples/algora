import sys, os, math; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
reset(); setup((1200, 500), 64)
world_color("#9AA8BC", 0.25)
for i,(g,d) in enumerate([(0.0,1.0),(0.6,1.0),(1.5,0.7)]):
    hex_module(f"M{i}", ((i-1)*0.36, 0, 0.15), (math.radians(90),0,0), culture=algae_mat(f"alg{i}", d, g), bubbles=40, seed=i)
box(6, 6, 0.01, mat("floor", BG, 0.6), (0, 0, -0.01)); box(6, 0.02, 3, mat("wall", "#DCE3EC", 0.8), (0, 0.4, 1))
area("key", (1.2, -1.5, 1.4), 80, 1.2, target=(0,0,0.15))
camera((0, -1.25, 0.25), (0, 0, 0.15), 42)
render_still(sys.argv[-1])
