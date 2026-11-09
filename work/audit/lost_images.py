"""旧処理で消えた画像を全ページで数える。
(a) 他の画像に重なっていて、まとめる処理で捨てられたもの
(b) 小さすぎるとして除外されたもの(幅40未満または高さ15未満)
"""
import fitz, json, os, sys
PDF = '/Users/teradatakeshi/Desktop/デジカル　マニュアル.pdf'
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
doc = fitz.open(PDF)
def area(r):
    return max(0, r.width) * max(0, r.height)
lost_overlay, lost_small = [], []
for pno in range(len(doc)):
    page = doc[pno]
    items = json.load(open(os.path.join(ROOT, 'work', 'pages', 'p%03d.json' % (pno + 1))))['items']
    web = [fitz.Rect(it['bbox']) for it in items if it['type'] == 'img']
    for info in page.get_image_info():
        r = fitz.Rect(info['bbox']) & page.rect
        if r.is_empty:
            continue
        small = r.width < 40 or r.height < 15
        # Web のどれかの切り出しに 9割以上含まれていれば収載済み
        covered = any(area(r & w) >= 0.9 * area(r) for w in web if not (r & w).is_empty)
        if covered:
            continue
        rec = (pno + 1, [round(v) for v in r], round(r.width), round(r.height))
        (lost_small if small else lost_overlay).append(rec)
print('重なりで消えた画像:', len(lost_overlay), 'ページ数', len({x[0] for x in lost_overlay}))
print('小さいとして除外:', len(lost_small), 'ページ数', len({x[0] for x in lost_small}))
if '-v' in sys.argv:
    for x in lost_overlay: print('O', x)
    for x in lost_small: print('S', x)
