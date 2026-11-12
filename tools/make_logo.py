#!/usr/bin/env python3
"""Builds the game logo from images/images.png + the Domo-kun PNG.

Outputs:
  images/logo.png        960x544 full-res logo
  assets/ICON0.PNG       144x80  PSP XMB icon
  assets/PIC1.PNG        480x272 PSP XMB background
  title_img.h            480x272 palettized (256 colours) title screen for the game
"""
import os, random, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = lambda *p: os.path.join(ROOT, *p)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
LW, LH = 960, 544
random.seed(7)

# ---------------- background: fighting-game style split ----------------
# left: the Nyan Cat image; right: Domo's side (dark red/purple space); glowing diagonal divider
icon = Image.open(IMG('images', 'images.png')).convert('RGB').resize((LH, LH), Image.LANCZOS)
canvas = Image.new('RGB', (LW, LH))
# Domo side: radial gradient (warm glow behind Domo -> dark purple), plus stars
side = Image.new('RGB', (LW, LH))
sp = side.load()
gcx, gcy = 790, 360
for y in range(LH):
    for x in range(LW):
        t = min(1.0, math.hypot(x - gcx, (y - gcy) * 1.2) / 520)
        sp[x, y] = (int(120 * (1 - t) + 22 * t), int(30 * (1 - t) + 6 * t), int(40 * (1 - t) + 48 * t))
sd = ImageDraw.Draw(side)
for _ in range(110):
    x, y = random.randint(0, LW - 4), random.randint(0, LH - 4)
    r = random.choice((1, 1, 1, 2))
    sd.ellipse((x - r, y - r, x + r, y + r), fill=(255, 230, 230))
for _ in range(9):
    x, y = random.randint(560, LW - 20), random.randint(10, LH - 20)
    sd.line((x - 7, y, x + 7, y), fill=(255, 220, 220), width=2)
    sd.line((x, y - 7, x, y + 7), fill=(255, 220, 220), width=2)
canvas.paste(side)
TOP_X, BOT_X = 575, 505                      # divider: right of the cat at every height
def div_x(y): return TOP_X + (BOT_X - TOP_X) * y / LH
cut = Image.new('L', (LW, LH))
ImageDraw.Draw(cut).polygon([(0, 0), (TOP_X, 0), (BOT_X, LH), (0, LH)], fill=255)
wide_icon = Image.new('RGB', (LW, LH))
wide_icon.paste(icon, (0, 0))
# the icon is only 544 wide; extend its last columns a little so the polygon is always covered
wide_icon.paste(icon.crop((LH - 40, 0, LH, LH)).resize((TOP_X - LH + 50, LH)), (LH, 0))
canvas.paste(wide_icon, (0, 0), cut)
# glowing divider
dv = Image.new('RGBA', (LW, LH))
ImageDraw.Draw(dv).line(((TOP_X, 0), (BOT_X, LH)), fill=(255, 230, 120, 255), width=18)
dv = dv.filter(ImageFilter.GaussianBlur(7))
ImageDraw.Draw(dv).line(((TOP_X, 0), (BOT_X, LH)), fill=(255, 255, 255, 255), width=4)
canvas = Image.alpha_composite(canvas.convert('RGBA'), dv).convert('RGB')

# ---------------- Domo-kun ----------------
domo = Image.open(IMG('images', 'domo_kun_png_by_nickfamzi_dhgmsub-fullview.png')).convert('RGBA')
dbox = domo.getbbox()
domo = domo.crop(dbox)
DH = 330
sc = DH / domo.height
domo = domo.resize((round(domo.width * sc), DH), Image.LANCZOS)
DX, DY = LW - domo.width - 40, LH - DH - 6
# soft glow behind Domo so he pops off the dark background
glow = Image.new('RGBA', (LW, LH))
PAD = 30
ga = Image.new('L', (domo.width + 2 * PAD, domo.height + 2 * PAD))
ga.paste(domo.getchannel('A'), (PAD, PAD))
ga = ga.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(10))
glow.paste((255, 140, 60, 255), (DX - PAD, DY - PAD), ga.point(lambda v: v * 2 // 3))
canvas = Image.alpha_composite(canvas.convert('RGBA'), glow)
canvas.alpha_composite(domo, (DX, DY))

# eye positions (in the source PNG) -> logo coordinates
def domo_pt(x, y): return (DX + (x - dbox[0]) * sc, DY + (y - dbox[1]) * sc)
domo_eyes = [domo_pt(290, 123), domo_pt(487, 121)]
cat_eyes = [(300 * LH / 447, 200 * LH / 447), (370 * LH / 447, 185 * LH / 447)]
clash = (590, 238)

# ---------------- lasers ----------------
def beams(points, target, color):
    layer = Image.new('RGBA', (LW, LH))
    g = ImageDraw.Draw(layer)
    for p in points:
        g.line((p, target), fill=color + (150,), width=16)
    layer = layer.filter(ImageFilter.GaussianBlur(5))
    g = ImageDraw.Draw(layer)
    for p in points:
        g.line((p, target), fill=color + (255,), width=7)
        g.line((p, target), fill=(255, 255, 255, 255), width=3)
        g.ellipse((p[0] - 9, p[1] - 9, p[0] + 9, p[1] + 9), fill=color + (255,))
        g.ellipse((p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4), fill=(255, 255, 255, 255))
    return layer

canvas.alpha_composite(beams(cat_eyes, clash, (255, 30, 60)))
canvas.alpha_composite(beams(domo_eyes, clash, (60, 255, 90)))
# clash spark
spark = Image.new('RGBA', (LW, LH))
s = ImageDraw.Draw(spark)
cx, cy = clash
s.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), fill=(255, 255, 160, 170))
spark = spark.filter(ImageFilter.GaussianBlur(10))
s = ImageDraw.Draw(spark)
import math
for k in range(12):
    a = k * math.pi / 6 + 0.2
    ln = 40 if k % 2 else 26
    s.line((cx, cy, cx + math.cos(a) * ln, cy + math.sin(a) * ln), fill=(255, 255, 200, 255), width=4)
s.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=(255, 255, 255, 255))
canvas.alpha_composite(spark)

# ---------------- title text ----------------
RAINBOW = [(255, 0, 0), (255, 153, 0), (255, 255, 0), (51, 255, 0), (0, 153, 255), (102, 51, 255)]

def outlined_text(img, xy, text, size, fill_img_fn, stroke, stroke_w, anchor='mm'):
    font = ImageFont.truetype(FONT, size)
    m = Image.new('L', img.size)
    ImageDraw.Draw(m).text(xy, text, font=font, anchor=anchor, fill=255)
    so = Image.new('L', img.size)
    ImageDraw.Draw(so).text(xy, text, font=font, anchor=anchor, fill=255,
                            stroke_width=stroke_w, stroke_fill=255)
    shadow = so.filter(ImageFilter.GaussianBlur(4))
    img.paste((0, 0, 0, 255), (6, 6), shadow.point(lambda v: v * 3 // 4))
    img.paste(stroke + (255,), (0, 0), so)
    img.paste(fill_img_fn(m.getbbox()), (0, 0), m)

def rainbow_fill(bbox):
    f = Image.new('RGBA', (LW, LH))
    fd = ImageDraw.Draw(f)
    y0, y1 = bbox[1], bbox[3]
    hgt = (y1 - y0) / 6
    for i, c in enumerate(RAINBOW):
        fd.rectangle((0, y0 + i * hgt, LW, y0 + (i + 1) * hgt + 1), fill=c + (255,))
    return f

def solid(c):
    return lambda bbox: Image.new('RGBA', (LW, LH), c + (255,))

TX = 735
outlined_text(canvas, (TX, 54), 'NYAN CAT', 68, rainbow_fill, (10, 10, 30), 7)
outlined_text(canvas, (TX, 106), 'VS', 36, solid((255, 240, 80)), (60, 20, 0), 5)
outlined_text(canvas, (TX, 152), 'DOMO-KUN', 58, solid((150, 85, 40)), (255, 245, 225), 6)

logo = canvas.convert('RGB')
os.makedirs(IMG('assets'), exist_ok=True)
logo.save(IMG('images', 'logo.png'))

# ---------------- PSP outputs ----------------
title = logo.resize((480, 272), Image.LANCZOS)
title.save(IMG('assets', 'PIC1.PNG'))
icon0 = Image.new('RGB', (144, 80))
icon0.paste(logo.resize((141, 80), Image.LANCZOS), (1, 0))
icon0.save(IMG('assets', 'ICON0.PNG'))

q = title.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
pal = q.getpalette()[:768]
pal += [0] * (768 - len(pal))
data = q.tobytes()
with open(IMG('title_img.h'), 'w') as f:
    f.write('/* generated by tools/make_logo.py -- do not edit */\n')
    f.write('#define TITLE_W 480\n#define TITLE_H 272\n')
    f.write('static const unsigned char title_pal[256][3] = {\n')
    for i in range(256):
        f.write('{%d,%d,%d},' % tuple(pal[i * 3:i * 3 + 3]) + ('\n' if i % 8 == 7 else ''))
    f.write('};\nstatic const unsigned char title_pix[TITLE_W * TITLE_H] = {\n')
    for i in range(0, len(data), 40):
        f.write(','.join(str(b) for b in data[i:i + 40]) + ',\n')
    f.write('};\n')
print('wrote images/logo.png, assets/ICON0.PNG, assets/PIC1.PNG, title_img.h')
