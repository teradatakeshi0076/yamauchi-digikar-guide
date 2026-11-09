"""PDFの各ページから、文字と画面写真を読む順に取り出す。
出力: work/pages/pNNN.json と site/img/pNNN_K.jpg
"""
import fitz, json, os, sys
from PIL import Image, ImageFilter

PDF = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(ROOT, 'work', 'pages')
IMG = os.path.join(ROOT, 'site', 'img')
os.makedirs(PAGES, exist_ok=True)
os.makedirs(IMG, exist_ok=True)

doc = fitz.open(PDF)
start = int(sys.argv[2]) if len(sys.argv) > 2 else 1
end = int(sys.argv[3]) if len(sys.argv) > 3 else len(doc)
total_imgs = 0
for pno in range(start - 1, end):
    page = doc[pno]
    W = page.rect.width
    items = []
    d = page.get_text('dict')
    for b in d['blocks']:
        if b['type'] == 0:
            lines = []
            for l in b['lines']:
                lines.append(''.join(s['text'] for s in l['spans']))
            t = '\n'.join(lines).strip()
            if not t:
                continue
            # ページ番号だけの行は除く
            if t.isdigit() and b['bbox'][1] > page.rect.height * 0.9:
                continue
            items.append({'type': 'text', 'text': t, 'bbox': [round(v) for v in b['bbox']]})
    # 画像の位置(同じ画像が複数ある場合も位置ごと)
    rects = []
    natives = []  # (位置, 元の細かさ=1ポイントあたりの画素数)
    for info in page.get_image_info():
        r = fitz.Rect(info['bbox']) & page.rect
        if r.width < 40 or r.height < 15:
            continue
        rects.append(r)
        natives.append((r, info['width'] / max(fitz.Rect(info['bbox']).width, 1)))
    # 重なっている画像はまとめる
    merged = []
    for r in sorted(rects, key=lambda r: (r.y0, r.x0)):
        for m in merged:
            if m.intersects(r):
                m |= r
                break
        else:
            merged.append(fitz.Rect(r))
    # 画面写真に重なる吹き出し・矢印・枠(図形)も含めて切り出す
    PA = page.rect.width * page.rect.height
    shapes = []
    for dr in page.get_drawings():
        rr = fitz.Rect(dr['rect'])
        if rr.width * rr.height < PA * 0.25 and not rr.is_empty or (rr.width < 2 or rr.height < 2):
            if rr.width * rr.height < PA * 0.25:
                shapes.append(rr)
    texts = [fitz.Rect(b['bbox']) for b in d['blocks'] if b['type'] == 0]
    k = 0
    for r0 in merged:
        k += 1
        r = fitz.Rect(r0)
        for _ in range(6):
            grown = fitz.Rect(r)
            for s in shapes:
                if fitz.Rect(s.x0 - 2, s.y0 - 2, s.x1 + 2, s.y1 + 2).intersects(r):
                    # 写真から大きく離れた大枠は含めない
                    if s.height < max(r0.height * 1.6, 120) and s.width < page.rect.width * 0.95:
                        grown |= s
            for tb in texts:
                if grown.contains(fitz.Rect(tb.x0 + 1, tb.y0 + 1, tb.x1 - 1, tb.y1 - 1)) is False and tb.intersects(grown) and not tb.intersects(r0):
                    # 吹き出しの中の文字(広げた範囲に一部かかる短い文字)
                    if tb.width < 200 and any(s.contains(tb) for s in shapes if s.intersects(grown)):
                        grown |= tb
            if grown == r:
                break
            r = grown
        clip = fitz.Rect(r.x0 - 2, r.y0 - 2, r.x1 + 2, r.y1 + 2) & page.rect
        # 表示の大きさ D = 元の画面写真の1.3倍(小さい文字を読みやすく。最大1300)。
        # その2倍の細かさで書き出し(細かい画面でもぼやけない)、輪郭を少しくっきりさせて WebP で保存
        native = max([ratio for (nr, ratio) in natives if nr.intersects(r0)] or [2.0])
        disp = min(1300, max(360, native * clip.width * 1.3))
        # いったん元の画面写真の細かさで書き出し(高倍率で書き出すと画像がカクカクになる)、
        # そこから表示の2倍までなめらかに拡大する
        target_w = round(2 * disp)
        zoom = max(2.0, min(4.0, native))
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip)
        name = 'p%03d_%d.jpg' % (pno + 1, k)  # データ上の名前(書き出しは .webp)
        pim = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        if target_w > pim.width:
            pim = pim.resize((target_w, round(pim.height * target_w / pim.width)), Image.LANCZOS)
        pim = pim.filter(ImageFilter.UnsharpMask(radius=1.6, percent=90, threshold=2))
        pim.save(os.path.join(IMG, name.replace('.jpg', '.webp')), 'WEBP', quality=80, method=4)
        items.append({'type': 'img', 'src': 'img/' + name, 'w': pix.width, 'h': pix.height,
                      'bbox': [round(v) for v in r]})
        total_imgs += 1
    items.sort(key=lambda it: (it['bbox'][1], it['bbox'][0]))
    with open(os.path.join(PAGES, 'p%03d.json' % (pno + 1)), 'w') as f:
        json.dump({'page': pno + 1, 'width': round(W), 'items': items}, f, ensure_ascii=False, indent=0)
print('pages', end - start + 1, 'images', total_imgs)
