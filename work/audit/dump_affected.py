"""報告で指摘のあった項目の今の中身を、手順番号つきで1つのファイルに書き出す(直す文を正確に指定するため)"""
import json, glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ids = set()
for f in glob.glob(os.path.join(HERE, 'review_*.md')):
    for m in re.finditer(r'^### ([a-z0-9][a-z0-9\-]+)', open(f).read(), re.M):
        ids.add(m.group(1))
ids |= {'h-rousai-denshika', 'h-allergy-kensa', 'c-teiki-nyuryoku', 'i-myna-sairai-pmh', 'i-shikakukakunin-sairai-iryofujo',
        'i-myna-shinki-hoken', 'b-hoken-koufi-henshu', 'g-kouhi-jiritsushien', 'i-karte-viewer', 'i-help-menu',
        'c-santei-check', 'c-comment-toroku', 'c-taiju-yoryo', 'f-tenken-naoshi', 'f-online-toiawase', 'f-rousai-seikyu',
        'i-onshi-sakujo', 'i-epre-tsuushin-error', 'a-agent-v2-saikidou', 'g-kouhi-fukushima-kodomo'}
out = []
for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'topics_*.json'))):
    for t in json.load(open(f)):
        if t['id'] not in ids:
            continue
        out.append('=' * 8 + ' %s (%s) pages=%s' % (t['id'], os.path.basename(f), t['pages']))
        out.append('title: ' + t['title'] + ' | manualTitle: ' + str(t.get('manualTitle')))
        out.append('summary: ' + t['summary'])
        for i, w in enumerate(t.get('warnings', [])): out.append('W%d: %s' % (i, w))
        for i, w in enumerate(t.get('tips', [])): out.append('T%d: %s' % (i, w))
        for pi, p in enumerate(t['parts']):
            out.append('P%d heading: %s' % (pi, p.get('heading', '')))
            for si, s in enumerate(p['steps']):
                out.append('  P%dS%d: %s' % (pi, si, s['text']))
                if s.get('note'): out.append('    note: ' + s['note'])
                if s.get('imgs'): out.append('    imgs: ' + ' '.join(s['imgs']))
        out.append('keywords: ' + ' / '.join(t.get('keywords', [])))
        out.append('related: ' + str(t.get('related')))
open(os.path.join(HERE, 'affected_dump.txt'), 'w').write('\n'.join(out))
print(len(ids), 'ids', len(out), 'lines')
