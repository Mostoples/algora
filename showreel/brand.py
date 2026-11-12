"""ALGORA brand helpers for PIL (same tokens as app/css/style.css)."""
import os, glob
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "showreel", "fonts", "PlusJakartaSans.ttf")
BG, BG2, INK, INK2, MUTED = (233, 239, 247), (243, 246, 251), (22, 35, 63), (74, 90, 122), (131, 146, 174)
BLUE, DEEP, ALGAE, ALGAE2 = (47, 123, 255), (22, 70, 214), (47, 184, 106), (14, 143, 85)

def font(size, weight=800):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f

def ffmpeg():
    g = glob.glob(os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages", "Gyan.FFmpeg*", "ffmpeg-*", "bin", "ffmpeg.exe"))
    return g[0] if g else "ffmpeg"

def grad_text(img, xy, text, f, c1=BLUE, c2=DEEP):
    """Draw text filled with a horizontal gradient."""
    d = ImageDraw.Draw(img)
    bb = d.textbbox(xy, text, font=f)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).text(xy, text, font=f, fill=255)
    g = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    for x in range(int(bb[0]), int(bb[2]) + 1):
        t = (x - bb[0]) / max(1, w)
        gd.line([(x, bb[1] - 4), (x, bb[3] + 4)], fill=tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)) + (255,))
    img.paste(g, (0, 0), Image.composite(g, Image.new("RGBA", img.size, (0, 0, 0, 0)), mask).split()[3])
    return bb

def card(size, r=28, alpha=240, shadow=True, aura=False):
    """Neumorph card as RGBA with baked blue shadow / aura."""
    w, h = size
    pad = 60
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    if shadow or aura:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        col = (70, 150, 255, 150) if aura else (40, 90, 200, 70)
        off = (0, 0) if aura else (10, 14)
        ImageDraw.Draw(sh).rounded_rectangle((pad + off[0], pad + off[1], pad + w + off[0], pad + h + off[1]), r, fill=col)
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(22)))
    body = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(body).rounded_rectangle((pad, pad, pad + w, pad + h), r, fill=(250, 252, 255, alpha), outline=(255, 255, 255, 255), width=2)
    return Image.alpha_composite(im, body), pad

def chip(text, f=None):
    f = f or font(22, 800)
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    bb = d.textbbox((0, 0), text, font=f)
    w, h = bb[2] + 58, 46
    c, pad = card((w, h), 23, 245, shadow=True)
    dd = ImageDraw.Draw(c)
    dd.ellipse((pad + 18, pad + h // 2 - 5, pad + 28, pad + h // 2 + 5), fill=BLUE)
    dd.text((pad + 38, pad + h // 2), text, font=f, fill=BLUE, anchor="lm")
    return c, pad

def aura_bg(size, orbs=((0.12, 0.2, 520, (140, 198, 255)), (0.9, 0.85, 600, (125, 230, 170)))):
    w, h = size
    im = Image.new("RGB", size, BG)
    o = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(o)
    for fx, fy, r, c in orbs:
        d.ellipse((fx * w - r / 2, fy * h - r / 2, fx * w + r / 2, fy * h + r / 2), fill=c + (150,))
    o = o.filter(ImageFilter.GaussianBlur(120))
    im.paste(o, (0, 0), o)
    return im
