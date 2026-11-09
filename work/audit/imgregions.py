"""PDFページの画像の位置と、Webで切り出した画像の範囲(pages JSON の bbox)を並べる。使い方: python3 imgregions.py 34 [91 ...]"""
import fitz, json, os, sys
PDF = '/Users/teradatakeshi/Desktop/デジカル　マニュアル.pdf'
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
doc = fitz.open(PDF)
for a in sys.argv[1:]:
    p = int(a)
    page = doc[p - 1]
    print('=' * 10, 'PDF', p)
    for i in page.get_image_info():
        print('  PDF画像', [round(v) for v in i['bbox']], '元', i['width'], 'x', i['height'])
    items = json.load(open(os.path.join(ROOT, 'work', 'pages', 'p%03d.json' % p)))['items']
    for it in items:
        if it['type'] == 'img':
            print('  Web画像', it['src'], it['bbox'])
