"""画像の名前の付け替え・図・本文に差し込むアイコン(監査A005〜A043)。fixes.py から読み込まれる。"""
import json, os
from fixlib import *

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run(del_step):
    # 1) 切り出し直しで1枚にまとまった画像の名前を付け替える(重複は1つにする)
    ch = json.load(open(os.path.join(ROOT, 'work', 'extract_changes.json')))
    for old, new in ch['renames'].items():
        for t in TOP.values():
            for p in t['parts']:
                for s in p['steps']:
                    if old in s.get('imgs', []):
                        imgs = [new if i == old else i for i in s['imgs']]
                        s['imgs'] = [i for k, i in enumerate(imgs) if i not in imgs[:k]]
                        log(t['id'], '画像 %s は %s と1枚にまとまったので付け替え' % (old, new), '切り出しの修正(重なった画像を捨てていた不具合)')

    # 2) 同じ図が2つの手順に付いていた箇所は、写真ごとに切り出し直した(make_extra.py)ので、そのまま使える
    log('h-tokutei-yakuzai-kanri', '画像 p617_1・p617_2 を写真ごとに切り出し直し(入力画面 / 「算定しない」メニュー)', 'PDF617(同じ図が重複していた)')
    log('h-shujutsu-ryosoku', '画像 p632_1・p632_2 を写真ごとに切り出し直し(左: コメントを追加 / 右: 両側・回数2)', 'PDF632(同じ図が重複していた)')

    # 3) 「←返金額」の札(p196_3)は会計画面の画像 p196_2 と1枚にした
    take_img('e-kaikei-henkin-touzitsu', 'img/p196_3.jpg')
    set_note('e-kaikei-henkin-touzitsu', '負担金が再計算されるので、差額を患者さんに返金する',
             '会計画面の「差額」欄にマイナスで表示される金額が返金額です(画面の「←返金額」)。', 'PDF196(札だけの画像を画面と1枚に)')

    # 4) 図(小さい画像の欠落 A019〜A022・A013)
    s = step('c-shohou-kansa', '警告レベルは3段階')
    s.setdefault('imgs', []).append('img/p116_level.jpg')
    log('c-shohou-kansa', '警告レベルの図(レベル1〜3のマークと矢印)を追加', 'A019〜A022 / PDF116')
    # PDF86 の色のパレットは、切り出し直しで p086_4 に入った(画像を比べて確認済み)ので、別の図は使わない

    # 5) 本文の中で「このボタン」と説明されているアイコンを、文の中に小さく差し込む(A005・A006・A018・A025〜A028・A030・A032〜A037)
    def icon(tid, sub, old, new, ref, field='text'):
        s = step(tid, sub)
        v = s.get(field, '')
        if v.count(old) != 1:
            raise FixError('%s: 「%s」が %d か所' % (tid, old, v.count(old)))
        s[field] = v.replace(old, new)
        log(tid, 'アイコンを差し込み: 「%s」→「%s」' % (old, new), ref)
    icon('a-icon-karte-pdf', 'カルテ表示設定: 同じ日に複数のカルテがある時の', '「まとめて表示」(', '「まとめて表示」[[img/icon_p030_1.webp]](', 'A006 / PDF30')
    icon('a-icon-karte-pdf', 'カルテ表示設定: 同じ日に複数のカルテがある時の', '「全て表示」(', '「全て表示」[[img/icon_p030_2.webp]](', 'A005 / PDF30')
    t = T('c-set-toroku')
    hits = [s for p in t['parts'] for s in p['steps'] if 'ドラッグ' in s.get('note', '')]
    assert len(hits) == 1
    hits[0]['note'] = hits[0]['note'].replace('先頭の取っ手部分を', '先頭の取っ手部分[[img/icon_p107_1.webp]]を')
    assert '[[img/icon_p107_1.webp]]' in hits[0]['note']
    log('c-set-toroku', 'アイコンを差し込み: 並び替えの取っ手', 'A018 / PDF107')
    icon('d-toyaku-rireki', '処方年月のマークを押すと', '処方年月のマークを', '処方年月の[[img/icon_p163_1.webp]]マークを', 'A025 / PDF163')
    for tid, ic, ref in [('f-seikyu-fukumenai', 'icon_p223_1', 'A026 / PDF223'), ('f-rousai-tsukiokure', 'icon_p259_1', 'A028 / PDF259'), ('f-jibai-tsukiokure', 'icon_p272_1', 'A030 / PDF272')]:
        t = T(tid)
        hits = [s for p in t['parts'] for s in p['steps'] if '診療履歴の編集ボタンから' in s.get('note', '')]
        assert len(hits) == 1, (tid, len(hits))
        hits[0]['note'] = hits[0]['note'].replace('診療履歴の編集ボタンから', '診療履歴の編集ボタン([[img/%s.webp]])から' % ic)
        log(tid, 'アイコンを差し込み: 診療履歴の編集ボタン', ref)
    icon('f-henrei-riyu', '画面の右上に出るダウンロードファイルを押してひらく', 'ダウンロードアイコンを押します', 'ダウンロードアイコン[[img/icon_p252_1.webp]]を押します', 'A027 / PDF252', field='note')
    icon('g-rme-tsuchi', 'デイリーレポートで「削除」ボタンを押すと', '「削除」ボタンを押すと', '「削除」ボタン[[img/icon_p316_1.webp]]を押すと', 'A032 / PDF316')
    icon('g-rme-tsuchi', 'デイリーレポートで「削除」ボタン', '別タブでカルテを表示することもできる', '別タブ[[img/icon_p316_2.webp]]でカルテを表示することもできる', 'A033 / PDF316')
    icon('g-rme-tsuchi', '受付画面でRMEデイリーレポートのボタンを押すと', 'RMEデイリーレポートのボタンを', 'RMEデイリーレポートのボタン[[img/icon_p316_3.webp]]を', 'A034 / PDF316')
    icon('g-rme-tsuchi', 'カルテを開き、右上の患者リストを開いて', '右上の患者リストを開いてボタンを', '右上の患者リスト[[img/icon_p316_4.webp]]を開いて[[img/icon_p316_5.webp]]ボタンを', 'A036・A037 / PDF316')
