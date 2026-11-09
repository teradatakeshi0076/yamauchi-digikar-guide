"""除外された小さい画像を、周りの文字ごと切り出して一覧画像にする(赤枠が対象)"""
import fitz, os, re
from PIL import Image, ImageDraw, ImageFont
PDF = '/Users/teradatakeshi/Desktop/デジカル　マニュアル.pdf'
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = '/private/tmp/claude-501/-Users-teradatakeshi-claude/0ed2efdc-3b67-4aa3-9f7a-00796a7cb116/scratchpad/small'
os.makedirs(OUT, exist_ok=True)
doc = fitz.open(PDF)
rows = []
for line in open(os.path.join(HERE, 'lost_images.txt')):
    if not line.startswith('S'):
        continue
    m = re.match(r"S \((\d+), \[(\d+), (\d+), (\d+), (\d+)\]", line)
    p, x0, y0, x1, y1 = map(int, m.groups())
    rows.append((p, fitz.Rect(x0, y0, x1, y1)))
tiles = []
for i, (p, r) in enumerate(rows):
    page = doc[p - 1]
    ctx = fitz.Rect(40, max(0, r.y0 - 55), page.rect.width - 20, min(page.rect.height, r.y1 + 55))
    pix = page.get_pixmap(matrix=fitz.Matrix(1.3, 1.3), clip=ctx)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    d = ImageDraw.Draw(im)
    k = 1.3
    d.rectangle([(r.x0 - ctx.x0) * k - 3, (r.y0 - ctx.y0) * k - 3, (r.x1 - ctx.x0) * k + 3, (r.y1 - ctx.y0) * k + 3], outline=(230, 0, 0), width=3)
    d.rectangle([0, 0, 120, 22], fill=(0, 0, 0))
    d.text((6, 4), 'S%02d p%d' % (i + 1, p), fill=(255, 255, 255))
    tiles.append(im)
# 4枚ずつ縦に並べた画像を何枚か作る
for s in range(0, len(tiles), 4):
    group = tiles[s:s + 4]
    W = max(t.width for t in group); H = sum(t.height for t in group) + 10 * len(group)
    sheet = Image.new('RGB', (W, H), 'white'); y = 0
    for t in group:
        sheet.paste(t, (0, y)); y += t.height + 10
    sheet.save(os.path.join(OUT, 'sheet%d.png' % (s // 4 + 1)))
print(len(tiles), 'tiles')
