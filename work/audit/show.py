"""監査CSVの指定IDを読みやすく表示する。使い方: python3 show.py A002 A003 ... / python3 show.py --summary"""
import csv, sys
P = '/Users/teradatakeshi/Documents/Codex/2026-11-09/gi/outputs/監査_118件の再確認結果.csv'
rows = list(csv.DictReader(open(P, encoding='utf-8-sig')))
if sys.argv[1:] == ['--summary']:
    from collections import Counter
    print(Counter(r['今回の判定'] for r in rows))
    print(Counter(r['元の種別'] for r in rows))
    for r in rows:
        print(r['ID'], '|', r['今回の判定'], '|', r['元の種別'], '|', r['PDFページ'], '|', r['Web項目'])
    sys.exit()
ids = set(sys.argv[1:])
for r in rows:
    if r['ID'] in ids:
        print('=' * 60)
        for k, v in r.items():
            print('【%s】%s' % (k, v))
