"""Web項目(手順データ)の中身を表示する。使い方: python3 topic.py h-tokutei-yakuzai-kanri [...]"""
import json, glob, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
T = {}
for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'topics_*.json'))):
    for t in json.load(open(f)):
        t['_file'] = os.path.basename(f)
        T[t['id']] = t
for tid in sys.argv[1:]:
    t = T.get(tid)
    if not t:
        print('見つかりません', tid); continue
    print('=' * 20, tid, '(', t['_file'], ')', '=' * 20)
    print('題:', t['title'], '| 原典:', t.get('manualTitle'), '| ページ:', t.get('pages'))
    print('要約:', t['summary'])
    for w in t.get('warnings', []): print('注意:', w)
    for p in t['parts']:
        if p.get('heading'): print('## ', p['heading'])
        for i, s in enumerate(p['steps'], 1):
            print(' %d. %s' % (i, s['text']))
            if s.get('note'): print('    ※', s['note'])
            if s.get('imgs'): print('    画像:', ' '.join(s['imgs']))
    for w in t.get('tips', []): print('便利:', w)
    print('関連:', t.get('related'))
