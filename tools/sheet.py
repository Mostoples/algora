"""Contact sheet: python tools/sheet.py out.png cell_px img1 img2 ..."""
import sys
from PIL import Image, ImageDraw
out, cell, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
cols = min(5, len(files)); rows = (len(files) + cols - 1) // cols
S = Image.new("RGB", (cols * cell, rows * (cell + 16)), (233, 239, 247))
d = ImageDraw.Draw(S)
for i, f in enumerate(files):
    im = Image.open(f).convert("RGBA"); im.thumbnail((cell, cell))
    x, y = (i % cols) * cell, (i // cols) * (cell + 16)
    S.paste(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2), im)
    d.text((x + 4, y + cell + 2), f.replace("\\", "/").split("/")[-1], fill=(22, 35, 63))
S.save(out)
