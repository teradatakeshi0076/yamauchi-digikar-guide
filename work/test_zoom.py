"""拡大の書き出し方を比べる: 今のもの / 4倍で書き出し / 4倍+輪郭くっきり"""
import fitz, sys, json, os
from PIL import Image, ImageFilter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
doc = fitz.open(sys.argv[1])
pno = int(sys.argv[2]); k = int(sys.argv[3]); out = sys.argv[4]
items = json.load(open(os.path.join(ROOT, 'work', 'pages', 'p%03d.json' % pno)))['items']
img = [i for i in items if i['type'] == 'img'][k - 1]
r = fitz.Rect(img['bbox'])
clip = fitz.Rect(r.x0 - 2, r.y0 - 2, r.x1 + 2, r.y1 + 2)
page = doc[pno - 1]
for z in [4, 6]:
    pix = page.get_pixmap(matrix=fitz.Matrix(z, z), clip=clip)
    p = os.path.join(out, 'z%d.png' % z)
    pix.save(p)
    im = Image.open(p).convert('RGB')
    im.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=2)).save(os.path.join(out, 'z%d_sharp.png' % z))
    print(z, pix.width, pix.height)
