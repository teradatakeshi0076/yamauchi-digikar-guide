"""照合係の報告にある「PDF原文」の引用が、本当に PDF のそのページ(前後1ページ)にあるかを確かめる"""
import fitz, re, glob, os, unicodedata
PDF = '/Users/teradatakeshi/Desktop/デジカル　マニュアル.pdf'
HERE = os.path.dirname(os.path.abspath(__file__))
doc = fitz.open(PDF)
def norm(s):
    s = unicodedata.normalize('NFKC', s)
    return re.sub(r'[\s　・、。,.「」『』()（）\[\]［］【】:：;；!！?？"\'＂〜~\-‐―ー→⇒＞>＜<※*]', '', s)
PT = {i + 1: norm(doc[i].get_text()) for i in range(len(doc))}
ok = ng = 0
bad = []
for f in sorted(glob.glob(os.path.join(HERE, 'review_*.md'))):
    blocks = re.split(r'\n### ', open(f).read())
    for b in blocks[1:]:
        head = b.split('\n')[0]
        pages = [int(x) for x in re.findall(r'\d{2,3}', head.split('PDF')[-1])] if 'PDF' in head else []
        m = re.search(r'PDF原文[:：]\s*(.*)', b)
        if not m:
            continue
        quotes = re.findall(r'「(.+?)」', m.group(1))
        if not quotes:
            continue
        cand = set()
        for p in pages:
            for q in (p - 1, p, p + 1):
                if q in PT:
                    cand.add(q)
        text = ''.join(PT[p] for p in sorted(cand)) if cand else ''
        for q in quotes:
            nq = norm(q)
            if len(nq) < 4:
                continue
            # 長い引用は先頭と末尾の一部で確かめる(途中の改行・表のずれに強くする)
            found = nq in text or (len(nq) > 24 and nq[:12] in text and nq[-12:] in text)
            if found:
                ok += 1
            else:
                ng += 1
                bad.append((os.path.basename(f), head[:70], q[:80]))
print('引用 一致', ok, '/ 見つからない', ng)
for x in bad:
    print(' -', x[0], '|', x[1], '|', x[2])
