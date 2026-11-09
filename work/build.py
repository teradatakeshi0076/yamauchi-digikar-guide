"""data/topics_*.json と他県の公費をまとめて site/data.js を作る。"""
import json, os, glob, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(ROOT, 'work', 'pages')

CATS = [
    {'id': 'uketsuke', 'name': '受付・予約', 'desc': '受付・患者登録・予約・マイナ保険証', 'tone': 'teal', 'icon': 'desk'},
    {'id': 'hoken', 'name': '保険証・公費', 'desc': '保険の登録・公費・労災・自費', 'tone': 'teal', 'icon': 'card'},
    {'id': 'shinsatsu', 'name': 'カルテ・処方', 'desc': '処置・処方・病名・検査・履歴', 'tone': 'blue', 'icon': 'note'},
    {'id': 'kaikei', 'name': '会計・返金', 'desc': '請求・領収書・未収金・返金・日計', 'tone': 'blue', 'icon': 'yen'},
    {'id': 'receipt', 'name': '月初の請求', 'desc': 'レセプトの点検・作成・提出', 'tone': 'blue', 'icon': 'cal'},
    {'id': 'santei', 'name': '算定の入力例', 'desc': '加算・管理料・注射・検査の入れ方', 'tone': 'navy', 'icon': 'calc'},
    {'id': 'kanri', 'name': '設定・集計', 'desc': '利用者・マスタ・各種データ', 'tone': 'navy', 'icon': 'gear'},
    {'id': 'login', 'name': 'ログイン・困った時', 'desc': '起動・画面の見方・障害・問合せ', 'tone': 'navy', 'icon': 'power'},
]

PREFS = [('北海道', 335), ('青森県', 383), ('岩手県', 386), ('宮城県', 396), ('秋田県', 399), ('山形県', 405),
         ('福島県', 408), ('茨城県', 413), ('栃木県', 419), ('群馬県', 422), ('埼玉県', 427), ('千葉県', 438),
         ('東京都', 442), ('神奈川県', 450), ('新潟県', 454), ('富山県', 458), ('石川県', 461), ('福井県', 465),
         ('山梨県', 468), ('長野県', 471), ('岐阜県', 477), ('静岡県', 481), ('愛知県', 487), ('三重県', 492),
         ('滋賀県', 501), ('京都府', 517), ('大阪府', 521), ('兵庫県', 526), ('奈良県', 537), ('和歌山県', 545),
         ('鳥取県', 549), ('島根県', 554), ('岡山県', 557), ('広島県', 560), ('山口県', 565), ('徳島県', 567),
         ('香川県', 571), ('愛媛県', 575), ('高知県', 578), ('福岡県', 583), ('佐賀県', 586), ('長崎県', 588),
         ('熊本県', 592), ('大分県', 601), ('宮崎県', 604), ('鹿児島県', 608), ('沖縄県', 610), ('END', 615)]
ROMA = ['hokkaido', 'aomori', 'iwate', 'miyagi', 'akita', 'yamagata', 'fukushima', 'ibaraki', 'tochigi', 'gunma',
        'saitama', 'chiba', 'tokyo', 'kanagawa', 'niigata', 'toyama', 'ishikawa', 'fukui', 'yamanashi', 'nagano',
        'gifu', 'shizuoka', 'aichi', 'mie', 'shiga', 'kyoto', 'osaka', 'hyogo', 'nara', 'wakayama', 'tottori',
        'shimane', 'okayama', 'hiroshima', 'yamaguchi', 'tokushima', 'kagawa', 'ehime', 'kochi', 'fukuoka', 'saga',
        'nagasaki', 'kumamoto', 'oita', 'miyazaki', 'kagoshima', 'okinawa']


def page_items(p):
    with open(os.path.join(PAGES, 'p%03d.json' % p)) as f:
        return json.load(f)['items']


def pref_topics():
    out = []
    for i, (name, start) in enumerate(PREFS[:-1]):
        if name == '東京都':
            continue
        end = PREFS[i + 1][1] - 1
        steps = []
        for p in range(start, end + 1):
            for it in page_items(p):
                if it['type'] == 'text':
                    t = re.sub(r'\s+', ' ', it['text']).strip()
                    if t:
                        steps.append({'text': t, 'imgs': []})
                elif steps:
                    steps[-1]['imgs'].append(it['src'])
                else:
                    steps.append({'text': '', 'imgs': [it['src']]})
        out.append({
            'id': 'pref-' + ROMA[i], 'category': 'hoken', 'region': 'other',
            'title': name + 'の公費', 'manualTitle': 'IX-2 ' + name + 'の公費',
            'pages': [start, end],
            'summary': name + 'の地方公費の登録方法(マニュアルの内容をそのまま載せています)。',
            'keywords': [name, name.rstrip('都道府県'), '地方公費', '県別公費', '他県', '県外'],
            'situations': [], 'parts': [{'heading': '', 'steps': steps, 'raw': True}],
            'warnings': [], 'tips': [], 'related': [],
        })
    return out


def main():
    topics = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'topics_*.json'))):
        with open(f) as fh:
            topics += json.load(fh)
    topics += pref_topics()
    ids = {t['id'] for t in topics}
    for t in topics:
        t['related'] = [r for r in t.get('related', []) if r in ids]
        t.setdefault('situations', []); t.setdefault('warnings', []); t.setdefault('tips', [])
        t['order'] = (t.get('pages') or [999])[0]
    topics.sort(key=lambda t: t['order'])
    # 画像は .webp で書き出してあるので、データ上の名前(.jpg)を差し替える
    for t in topics:
        for p in t['parts']:
            for s in p['steps']:
                s['imgs'] = [i.replace('.jpg', '.webp') for i in s.get('imgs', [])]
    # 表示の大きさ(書き出しは2倍の細かさなので半分)。読み込み前から場所を確保して表示がずれないように
    from PIL import Image
    sizes = {}
    for f in glob.glob(os.path.join(ROOT, 'site', 'img', '*.webp')):
        with Image.open(f) as im:
            sizes['img/' + os.path.basename(f)] = [round(im.size[0] / 2), round(im.size[1] / 2)]
    import time
    # ver: 画像を作り直した時に、ブラウザが古い画像を使わないための版番号
    data = {'cats': CATS, 'topics': topics, 'manualDate': '2026/10/27', 'sizes': sizes,
            'ver': time.strftime('%Y%m%d%H%M')}
    js = 'window.GUIDE=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';'
    with open(os.path.join(ROOT, 'site', 'data.js'), 'w') as f:
        f.write(js)
    # index.html の読み込みにも同じ版番号を付ける(古いプログラムや見た目が残らないように)
    ip = os.path.join(ROOT, 'site', 'index.html')
    html = open(ip).read()
    html = re.sub(r'\?v=\d+', '?v=' + data['ver'], html)
    open(ip, 'w').write(html)
    n_img = sum(len(s.get('imgs', [])) for t in topics for p in t['parts'] for s in p['steps'])
    print('topics', len(topics), 'images', n_img, 'size', len(js) // 1024, 'KB')


main()
