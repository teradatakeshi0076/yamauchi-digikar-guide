"""手順データの確認: 形・カテゴリ・担当範囲の画像の落ち・存在しない画像を調べる。
使い方: python3 work/check.py data/topics_b.json 45 84 [追加範囲 例 442-449]
"""
import json, os, sys, glob, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATS = {'login', 'uketsuke', 'hoken', 'shinsatsu', 'kaikei', 'receipt', 'kanri', 'santei'}
path = sys.argv[1]
ranges = [(int(sys.argv[2]), int(sys.argv[3]))]
for extra in sys.argv[4:]:
    a, b = extra.split('-')
    ranges.append((int(a), int(b)))

errs = []
try:
    data = json.load(open(os.path.join(ROOT, path) if not os.path.isabs(path) else path))
except Exception as e:
    print('JSONが読めません:', e); sys.exit(1)
if not isinstance(data, list):
    print('配列ではありません'); sys.exit(1)
ALL_IDS = set(t['id'] for f in glob.glob(os.path.join(ROOT, 'data', 'topics_*.json')) for t in json.load(open(f)))
ids = set()
used = set()
for i, t in enumerate(data):
    where = '%d番目(%s)' % (i, t.get('id'))
    for k in ['id', 'category', 'title', 'summary', 'keywords', 'parts', 'pages']:
        if k not in t:
            errs.append('%s: %s がありません' % (where, k))
    if t.get('id') in ids:
        errs.append('%s: id が重複' % where)
    ids.add(t.get('id'))
    if t.get('id') and not re.match(r'^[a-z0-9-]+$', t['id']):
        errs.append('%s: id は英小文字・数字・ハイフンのみ' % where)
    if t.get('category') not in CATS:
        errs.append('%s: category が不正 %s' % (where, t.get('category')))
    if len(t.get('title', '')) > 24:
        errs.append('%s: title が長い' % where)
    for p in t.get('parts', []):
        if 'steps' not in p:
            errs.append('%s: parts に steps がありません' % where)
        for s in p.get('steps', []):
            if not s.get('text'):
                errs.append('%s: 手順の text が空' % where)
            for im in s.get('imgs', []):
                if not os.path.exists(os.path.join(ROOT, 'site', im.replace('.jpg', '.webp'))):
                    errs.append('%s: 画像がありません %s' % (where, im))
                used.add(im)
for t in data:
    for r in t.get('related', []):
        if r not in ids and r not in ALL_IDS:
            errs.append('%s: related の %s が見つかりません' % (t.get('id'), r))
expected = set()
for a, b in ranges:
    for p in range(a, b + 1):
        for f in glob.glob(os.path.join(ROOT, 'site', 'img', 'p%03d_*.webp' % p)):
            expected.add('img/' + os.path.basename(f).replace('.webp', '.jpg'))
ok_unused = set(l.strip() for l in open(os.path.join(ROOT, 'work', 'audit', 'unused_ok.txt')) if l.strip()) if os.path.exists(os.path.join(ROOT, 'work', 'audit', 'unused_ok.txt')) else set()
missing = sorted(expected - used - ok_unused)
if missing:
    errs.append('どこにも付いていない画像 %d枚: %s' % (len(missing), ', '.join(missing[:40])))
print('トピック', len(data), '件 / 使った画像', len(used), '枚')
if errs:
    print('エラー', len(errs), '件')
    for e in errs[:80]:
        print(' -', e)
    sys.exit(1)
print('OK')
