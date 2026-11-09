"""PDFのページを画像にして保存し、文字も表示する。使い方: python3 pdfpage.py 617 [618 ...] [--noimg]"""
import fitz, sys, os
PDF = '/Users/teradatakeshi/Desktop/デジカル　マニュアル.pdf'
OUT = '/private/tmp/claude-501/-Users-teradatakeshi-claude/0ed2efdc-3b67-4aa3-9f7a-00796a7cb116/scratchpad/pdf'
os.makedirs(OUT, exist_ok=True)
doc = fitz.open(PDF)
noimg = '--noimg' in sys.argv
for a in sys.argv[1:]:
    if a.startswith('--'):
        continue
    p = int(a)
    page = doc[p - 1]
    if not noimg:
        page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6)).save(os.path.join(OUT, 'p%03d.png' % p))
    print('=' * 20, 'PDF', p, '=' * 20)
    print(page.get_text())
    for l in page.get_links():
        if l.get('uri'):
            print('[LINK]', l['uri'], [round(v) for v in l['from']])
