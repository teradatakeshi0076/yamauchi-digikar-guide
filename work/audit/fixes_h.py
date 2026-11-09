"""算定の入力例(h)の修正。fixes.py から読み込まれる。"""
import re
import fitz
from fixlib import *


def run(del_step):
    # A002: 選択式コメント21個を PDF617〜618 の文字から機械的に取り出して、原文どおり並べる(書き写しの誤りを防ぐ)
    doc = fitz.open('/Users/teradatakeshi/Desktop/デジカル　マニュアル.pdf')
    lines = [l.strip() for l in (doc[616].get_text() + doc[617].get_text()).split('\n')]
    comments = []
    for i, l in enumerate(lines):
        m = re.match(r'^（(.)）\s*(.+)$', l)
        if m and m.group(1) in 'イロハニホヘトチリヌルヲワカヨタレソツネナ':
            body = m.group(2).strip()
            if not body.endswith('投与') and i + 1 < len(lines):
                body += lines[i + 1].strip()  # (ヨ) は次の行に続く
            comments.append('(%s) %s' % (m.group(1), re.sub(r'\s+', '', body)))
    assert len(comments) == 21, comments
    assert comments[0] == '(イ) 心疾患患者でジギタリス製剤を投与', comments[0]
    assert comments[-1] == '(ナ) ブスルファンを投与', comments[-1]
    s = step('h-tokutei-yakuzai-kanri', '次の中から該当するコメントを選んで入力する')
    s['text'] = '薬剤についてのコメントは、次の選択式コメントから入力する\n' + '\n'.join('・' + c for c in comments)
    log('h-tokutei-yakuzai-kanri', '選択式コメント21個を、対象患者などの条件を省かずPDFの原文どおりに列記', 'A002 / PDF617〜618')

    s = step('h-tokutei-yakuzai-kanri', '管理料とコメントを同じ並びで入力する')
    s['text'] = '画面の入力例のとおり、「特定薬剤治療管理料1」「薬剤についてのコメント」「初回算定コメント」を入力する'
    s['note'] = 'マニュアルのこの部分は画面写真だけです。写真では、初回にあった加算(第1回目)は入っていません。検査は「算定しない」にしています。'
    log('h-tokutei-yakuzai-kanri', '2月目以降の手順を写真どおりに(「同じ並び」だと初回の加算まで毎月入れると読めた)', 'PDF618 写真')
    s = step('h-tokutei-yakuzai-kanri', '逓減の管理料を入力する')
    s['text'] = '画面の入力例のとおり、「特定薬剤治療管理料1(第4月目以降)」「薬剤についてのコメント」「初回算定コメント」を入力する'
    s['note'] = 'マニュアルのこの部分は画面写真だけです。検査は「算定しない」にしています。'
    log('h-tokutei-yakuzai-kanri', '4月目以降の手順を写真どおりに', 'PDF618 写真')

    set_note('h-toushi-zouei', '「透視診断」「診断料」「撮影料」「電子画像管理加算」',
             'スポット撮影等特殊撮影を施行した場合は、必ずこの位置(画面の赤枠: 「電子画像管理加算」の後、「薬剤」の前)に「特殊撮影の手技」を入力する。',
             'PDF637 写真の赤枠(「撮影料の後」は写真と合わない)')

    take_img('h-kenben-2kaihou', 'img/p633_4.jpg')
    log('h-kenben-2kaihou', '画像 p633_4(アレルギー検査の写真)を外す', 'PDF633')
    set_imgs('h-allergy-kensa', 'アレルゲン項目を同一グループ内に入力する', ['img/p633_4.jpg'], 'PDF633 アレルゲン14項目の写真')

    take_img('h-chouki-innai', 'img/p626_4.jpg')
    del_step('h-chouki-innai', 'カルテの入力例を確認する', 'PDF626')
    p = [p for p in T('h-chouki-innai')['parts'] if p['heading'] == '医療上必要で処方する場合'][0]
    p['steps'].append({'text': 'カルテの入力例を確認する',
                       'note': '画面の入力例のコメントは「長期収載品と後発医薬品で薬事上承認された効能・効果に差異があるため」(医療上必要の理由)です。',
                       'imgs': ['img/p626_4.jpg']})
    log('h-chouki-innai', '【カルテ入力例】の写真を、写っているコメントに合う「医療上必要で処方する場合」へ移す', 'PDF626')

    set_imgs('h-shochi-ryosoku', '「処」の区分をクリックして「コメントを追加」を選ぶ', ['img/p631_2.jpg'], 'PDF631 左の写真(メニュー)')
    set_imgs('h-shochi-ryosoku', '「両側」と入力して、回数を「2」回にする', ['img/p631_1.jpg'], 'PDF631 右の写真(完成)')

    set_note('h-gazou-jikangai-kinkyuu', '「画」の区分をクリックして「コメントを追加」を選ぶ',
             'マニュアルの画面写真では赤枠が「算定しない」に付いていますが、本文の指示は「コメントを追加」です。「算定しない」を押すと加算が算定されなくなります。',
             'PDF638 本文と写真の食い違い(要確認)')

    # PDF642 の POINT(選択式コメント)と参考リンクは「⑥ 労災電子化加算の入力」の下にある
    del_list('h-rousai-shishi-kasan', 'tips', '令和8年診療報酬改定にともない', 'PDF642 POINT は⑥の下')
    add_list('h-rousai-denshika', 'warnings',
             '令和8年診療報酬改定にともない、労災レセプトにおいても「選択式コメント」の入力が必要です。カルテに診療行為や検査等を入力した際、選択式コメントが未入力、または入力形式に誤りがある場合は赤い「¥」マークが表示されます。画面の案内に従ってコメントを入力してください。詳細なコメント内容やコードは、厚生労働省のホームページで確認してください(下の参考リンク)。',
             'PDF642 POINT')
    add_link('h-rousai-denshika', '労災レセプト電算処理システム(厚生労働省)',
             'https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/koyou_roudou/roudoukijun/rousai/rezeptsystem/index.html', 642, 'A094 / PDF642')
    add_link('h-rousai-denshika', '労災コメントマスタ[Excel形式:9KB](厚生労働省)', 'https://www.mhlw.go.jp/content/001650081.csv', 642, 'A095 / PDF642')
    for sub in ['四肢には「労災(1.5倍)(処置)」', '四肢には「労災(1.5倍)(手術)」']:
        set_note('h-rousai-shishi-kasan', sub, '画面の入力例では、加算の下に選択式コメント(部位)が入っています。', 'PDF642 写真')

    for tid in ['h-rousai-shoshin', 'h-rousai-saishin', 'h-rousai-jikangai', 'h-rousai-gairai-kanri', 'h-rousai-shishi-kasan', 'h-rousai-denshika']:
        t = T(tid)
        t['tips'] = [x for x in t.get('tips', []) if '健保準拠自賠責' not in x]
        add_list(tid, 'tips', 'マニュアルのこの章は「労災・労災準拠自賠責」の入力です。健保準拠自賠責の場合は、医療保険と同様のマスタで入力します。', 'PDF639 章見出し')

    rep('h-ippanmei-shohou', '保険医署名欄は自動記載されません。手書きしてください。',
        '処方せんの変更不可欄に「×」を付けるため「後発変更不可」のコメントを入力した場合、保険医署名欄は自動記載されませんので、手書きしてください。',
        'PDF624(同じ囲みの中の注意)')
    T('h-ippanmei-shohou')['related'] = (T('h-ippanmei-shohou').get('related') or []) + ['g-sonota-settei']
    log('h-ippanmei-shohou', '関連に「その他設定」を追加(全医薬品を一般名処方にする設定)', 'PDF624')
    set_field('h-yohou-comment', 'summary', '薬の用法に補足のコメントを付けます(画面の例: 1回2ブリスター 5日分)。', 'PDF627(「食前など細かい指示」は原典にない)')
