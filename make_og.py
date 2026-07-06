# -*- coding: utf-8 -*-
"""OGP画像(1200x630 PNG)をPILで生成。実行: python site/make_og.py"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'site', 'og-image.png')
W, H = 1200, 630

def font(size, bold=True):
    cands = [
        r"C:\Windows\Fonts\YuGothB.ttc" if bold else r"C:\Windows\Fonts\YuGothR.ttc",
        r"C:\Windows\Fonts\meiryob.ttc" if bold else r"C:\Windows\Fonts\meiryo.ttc",
        r"C:\Windows\Fonts\BIZ-UDGothicB.ttc",
        r"C:\Windows\Fonts\msgothic.ttc",
    ]
    for c in cands:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    return ImageFont.load_default()

# 斜めグラデ背景
img = Image.new('RGB', (W, H))
px = img.load()
c0, c1 = (0x0B, 0x4A, 0x3E), (0x11, 0x7A, 0x62)
for y in range(H):
    for xband in range(0, W, 4):
        t = (xband / W * 0.55 + y / H * 0.45)
        r = int(c0[0] + (c1[0]-c0[0]) * t)
        g = int(c0[1] + (c1[1]-c0[1]) * t)
        b = int(c0[2] + (c1[2]-c0[2]) * t)
        for xx in range(xband, min(xband+4, W)):
            px[xx, y] = (r, g, b)

d = ImageDraw.Draw(img, 'RGBA')
# 装飾円
d.ellipse([1060-230, 90-230, 1060+230, 90+230], fill=(255, 255, 255, 16))
d.ellipse([150-180, 560-180, 150+180, 560+180], fill=(255, 255, 255, 12))

# テキスト
d.text((90, 118), "小金井市 令和8年度 一般会計予算", font=font(30), fill=(191, 233, 221))
d.text((84, 165), "546", font=font(200), fill=(255, 255, 255))
big = d.textlength("546", font=font(200))
d.text((84 + big + 10, 300), "億円", font=font(84), fill=(255, 255, 255))
d.text((90, 400), "あなたのまちの、1年分。", font=font(62), fill=(255, 255, 255))
d.text((90, 496), "さわって探検できる、市民のための予算サイト", font=font(30, bold=False), fill=(191, 233, 221))

# 棒グラフ + サイト名
bx, by = 92, 590
for i, (w, h, col) in enumerate([(22, 42, (0, 163, 136)), (22, 60, (77, 193, 230)), (22, 82, (245, 166, 35))]):
    x = bx + i * 34
    d.rounded_rectangle([x, by + (42 - h), x + w, by + 42], radius=3, fill=col)
d.text((bx + 118, by + 6), "小金井よさんラボ", font=font(26), fill=(255, 255, 255))

img.save(OUT, 'PNG')
print(f"saved {OUT} ({os.path.getsize(OUT):,} bytes)")
