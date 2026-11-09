"""PDFページ内の文字と画像の並び(上から順)を表示する。使い方: python3 order.py 22 17 41"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for a in sys.argv[1:]:
    p = int(a)
    items = json.load(open(os.path.join(ROOT, 'work', 'pages', 'p%03d.json' % p)))['items']
    print('=' * 8, 'PDF', p)
    for it in items:
        if it['type'] == 'img':
            print('   [画像]', it['src'], it['bbox'])
        else:
            print('   ', it['text'].replace('\n', ' ')[:90], it['bbox'][1])
