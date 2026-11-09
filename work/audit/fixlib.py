"""手順データ(data/topics_*.json)を直すための道具。
すべての修正は「直す前の文」を指定して行い、見つからない・複数見つかる時は止まる(意図しない書き換えを防ぐ)。
修正の記録は LOG に残し、最後に work/audit/fix_log.md へ書き出す。
"""
import json, glob, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILES = {}
TOP = {}
for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'topics_*.json'))):
    FILES[f] = json.load(open(f))
    for t in FILES[f]:
        TOP[t['id']] = t
LOG = []


class FixError(Exception):
    pass


def T(tid):
    if tid not in TOP:
        raise FixError('項目が見つかりません: ' + tid)
    return TOP[tid]


def log(tid, what, ref=''):
    LOG.append((tid, what, ref))


def _strings(t):
    """項目の中の文字列の場所を全部返す: (容器, キー, 値)"""
    out = [(t, 'summary', t['summary']), (t, 'title', t['title'])]
    for i, w in enumerate(t.get('warnings', [])):
        out.append((t['warnings'], i, w))
    for i, w in enumerate(t.get('tips', [])):
        out.append((t['tips'], i, w))
    for p in t['parts']:
        out.append((p, 'heading', p.get('heading', '')))
        for s in p['steps']:
            out.append((s, 'text', s.get('text', '')))
            if s.get('note'):
                out.append((s, 'note', s['note']))
    return out


def rep(tid, old, new, ref=''):
    """項目の中で old をちょうど1か所だけ new に置き換える"""
    t = T(tid)
    hits = [(c, k, v) for (c, k, v) in _strings(t) if old in v]
    n = sum(v.count(old) for (_, _, v) in hits)
    if n != 1:
        raise FixError('%s: 「%s」が %d か所あります(1か所であること)' % (tid, old[:40], n))
    c, k, v = hits[0]
    c[k] = v.replace(old, new)
    log(tid, '「%s」→「%s」' % (old, new), ref)


def step(tid, sub):
    """text に sub を含む手順をちょうど1つ返す"""
    t = T(tid)
    hits = [s for p in t['parts'] for s in p['steps'] if sub in s.get('text', '')]
    if len(hits) != 1:
        raise FixError('%s: 手順「%s」が %d 個あります' % (tid, sub[:40], len(hits)))
    return hits[0]


def set_note(tid, sub, note, ref=''):
    s = step(tid, sub)
    old = s.get('note', '')
    if note:
        s['note'] = note
    else:
        s.pop('note', None)
    log(tid, '手順「%s」の補足: 「%s」→「%s」' % (sub[:30], old, note), ref)


def set_imgs(tid, sub, imgs, ref=''):
    s = step(tid, sub)
    old = s.get('imgs', [])
    s['imgs'] = list(imgs)
    log(tid, '手順「%s」の画像: %s → %s' % (sub[:30], old, imgs), ref)


def take_img(tid, img):
    """項目のどこかに付いている画像 img を外す(付いていなければ止まる)"""
    t = T(tid)
    for p in t['parts']:
        for s in p['steps']:
            if img in s.get('imgs', []):
                s['imgs'].remove(img)
                return
    raise FixError('%s: 画像 %s が付いていません' % (tid, img))


def move_img(tid, img, to_sub, ref='', to_tid=None):
    take_img(tid, img)
    s = step(to_tid or tid, to_sub)
    s.setdefault('imgs', []).append(img)
    log(to_tid or tid, '画像 %s を手順「%s」へ移す(元: %s)' % (img, to_sub[:30], tid), ref)


def del_list(tid, key, sub, ref=''):
    t = T(tid)
    hits = [w for w in t.get(key, []) if sub in w]
    if len(hits) != 1:
        raise FixError('%s: %s「%s」が %d 個' % (tid, key, sub[:30], len(hits)))
    t[key].remove(hits[0])
    log(tid, '%s を削除: 「%s」' % ({'warnings': '注意', 'tips': '便利'}[key], hits[0]), ref)


def add_list(tid, key, text, ref='', pos=None):
    t = T(tid)
    t.setdefault(key, [])
    if pos is None:
        t[key].append(text)
    else:
        t[key].insert(pos, text)
    log(tid, '%s を追加: 「%s」' % ({'warnings': '注意', 'tips': '便利'}[key], text), ref)


def set_field(tid, key, value, ref=''):
    t = T(tid)
    old = t.get(key)
    t[key] = value
    log(tid, '%s: 「%s」→「%s」' % (key, old, value), ref)


def add_part(tid, heading, steps, ref='', pos=None):
    """新しい段(見出し+手順)を足す。steps は [{'text':..., 'note':..., 'imgs':[...]}]"""
    t = T(tid)
    part = {'heading': heading, 'steps': steps}
    if pos is None:
        t['parts'].append(part)
    else:
        t['parts'].insert(pos, part)
    log(tid, '段を追加「%s」: %s' % (heading, ' / '.join(s['text'] for s in steps)), ref)


def set_parts(tid, parts, ref=''):
    """項目の手順を丸ごと書き直す(画像は書き直し前と同じ集合であることを確かめる)"""
    t = T(tid)
    before = sorted(i for p in t['parts'] for s in p['steps'] for i in s.get('imgs', []))
    after = sorted(i for p in parts for s in p['steps'] for i in s.get('imgs', []))
    t['_imgs_before'] = before
    t['parts'] = parts
    log(tid, '手順を書き直し(%d段)' % len(parts), ref)
    return before, after


def add_link(tid, label, url, page, ref=''):
    t = T(tid)
    t.setdefault('links', [])
    if any(l['url'] == url and l['label'] == label for l in t['links']):
        return
    t['links'].append({'label': label, 'url': url, 'page': page})
    log(tid, 'リンクを追加: %s (%s) PDF%d' % (label, url, page), ref)


def save():
    for f, data in FILES.items():
        for t in data:
            t.pop('_imgs_before', None)
        with open(f, 'w') as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    out = ['# 修正の記録(fixes.py で自動作成)', '']
    cur = None
    for tid, what, ref in LOG:
        if tid != cur:
            out.append('\n## ' + tid + ' — ' + TOP[tid]['title'])
            cur = tid
        out.append('- ' + what + ('  〔根拠: ' + ref + '〕' if ref else ''))
    open(os.path.join(ROOT, 'work', 'audit', 'fix_log.md'), 'w').write('\n'.join(out))
    print('修正', len(LOG), '件を保存')
