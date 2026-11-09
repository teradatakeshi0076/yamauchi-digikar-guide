"""変わった画像の「前(左)・後(右)」を並べた確認用の一覧画像を作る"""
import os, sys
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = '/private/tmp/claude-501/-Users-teradatakeshi-claude/0ed2efdc-3b67-4aa3-9f7a-00796a7cb116/scratchpad/cmp'
os.makedirs(OUT, exist_ok=True)
names = sys.argv[1:]
W = 560
rows = []
for n in names:
    a = Image.open(os.path.join(ROOT, 'work', 'img_prev', n)).convert('RGB')
    b = Image.open(os.path.join(ROOT, 'site', 'img', n)).convert('RGB')
    a = a.resize((W, round(a.height * W / a.width)))
    b = b.resize((W, round(b.height * W / b.width)))
    h = max(a.height, b.height) + 24
    row = Image.new('RGB', (W * 2 + 20, h), 'white')
    d = ImageDraw.Draw(row)
    d.text((4, 4), n + '  前', fill=(200, 0, 0)); d.text((W + 24, 4), '後', fill=(0, 120, 0))
    row.paste(a, (0, 22)); row.paste(b, (W + 20, 22))
    rows.append(row)
for i in range(0, len(rows), 3):
    g = rows[i:i + 3]
    sheet = Image.new('RGB', (g[0].width, sum(r.height for r in g) + 12 * len(g)), (230, 230, 230))
    y = 0
    for r in g:
        sheet.paste(r, (0, y)); y += r.height + 12
    sheet.save(os.path.join(OUT, 'cmp%d.png' % (i // 3 + 1)))
print(len(rows), 'rows')
