"""PDF に埋め込まれた画面写真のうち、元から粗いもの(1ポイントあたりの画素が少ないもの)を数える"""
import fitz, sys
doc = fitz.open(sys.argv[1])
pages = [int(a) for a in sys.argv[2:]]
buckets = {'<1.5': 0, '1.5-2': 0, '2-3': 0, '>=3': 0}
for pno in range(len(doc)):
    page = doc[pno]
    for info in page.get_image_info(xrefs=True):
        r = fitz.Rect(info['bbox'])
        if r.width < 40:
            continue
        ratio = info['width'] / r.width
        k = '<1.5' if ratio < 1.5 else '1.5-2' if ratio < 2 else '2-3' if ratio < 3 else '>=3'
        buckets[k] += 1
        if pno + 1 in pages:
            print(pno + 1, 'native', info['width'], 'x', info['height'], 'shown', round(r.width), 'ratio', round(ratio, 2), 'xref', info.get('xref'))
print(buckets)
