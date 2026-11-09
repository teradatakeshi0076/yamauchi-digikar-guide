"""ロゴの白い背景を透明にする(濃い色の上に置くため)"""
from PIL import Image
import sys
im = Image.open(sys.argv[1]).convert('RGBA')
px = im.load()
for y in range(im.height):
    for x in range(im.width):
        r, g, b, a = px[x, y]
        m = min(r, g, b)
        if m > 235:
            px[x, y] = (r, g, b, 0)
        elif m > 200:
            px[x, y] = (r, g, b, int(255 * (235 - m) / 35))
bbox = im.getbbox()
im.crop(bbox).save(sys.argv[2])
print(im.crop(bbox).size)
