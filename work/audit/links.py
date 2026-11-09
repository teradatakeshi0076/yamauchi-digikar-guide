"""PDF の外部リンク(URL)を全部取り出し、リンクが付いている文字と、そのページの Web 項目を並べる"""
import fitz, json, glob, os
PDF = '/Users/teradatakeshi/Desktop/デジカル　マニュアル.pdf'
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
doc = fitz.open(PDF)
topics = []
for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'topics_*.json'))):
    topics += json.load(open(f))
rows = []
for pno in range(len(doc)):
    page = doc[pno]
    for l in page.get_links():
        uri = l.get('uri')
        if not uri:
            continue
        r = fitz.Rect(l['from'])
        txt = page.get_textbox(fitz.Rect(r.x0 - 1, r.y0 - 1, r.x1 + 1, r.y1 + 1)).strip().replace('\n', '')
        on = [t['id'] for t in topics if t['pages'] and t['pages'][0] <= pno + 1 <= t['pages'][-1]]
        rows.append({'page': pno + 1, 'uri': uri, 'text': txt, 'topics': on})
json.dump(rows, open(os.path.join(ROOT, 'work', 'audit', 'pdf_links.json'), 'w'), ensure_ascii=False, indent=1)
print('links', len(rows), 'unique', len({r['uri'] for r in rows}))
for r in rows:
    print(r['page'], '|', r['text'][:50], '|', r['uri'], '|', ','.join(r['topics']))
