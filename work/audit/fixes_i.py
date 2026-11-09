"""マイナ保険証・電子処方箋・ヘルプ(i)の修正。fixes.py から読み込まれる。"""
from fixlib import *


def run(del_step):
    # A004: PDF652 の参照先(サイト・文書名・版・ページ)
    add_list('i-onshi-gaiyou', 'warnings',
             '環境設定の方法は、医療機関向け総合ポータルサイトの「手順・マニュアル」の一覧にある「2-③-A 操作マニュアル(管理者編)」(2026/2/10版)のP53〜を参照します(下の参考リンク)。',
             'A004 / PDF652', pos=1)
    add_link('i-onshi-gaiyou', '医療機関向け総合ポータルサイト「手順・マニュアル」の一覧', 'https://iryohokenjyoho.service-now.com/csm?id=kb_article_view&sysparm_article=KB0010259', 652, 'A096 / PDF652')
    add_link('i-onshi-gaiyou', '「2-③-A 操作マニュアル(管理者編)」(2026/2/10版)', 'https://iryohokenjyoho.service-now.com/sys_attachment.do?sys_id=3f69cc032f9d87502d7d413fafa4e3d8', 652, 'A097 / PDF652')

    # A118 ほか: PDF703〜704 の流れ図どおりに組み直す(画像は流れ図のページ全体)
    t = T('i-shougai')
    t['summary'] = '「ログインできない」「動かない」などシステム障害が疑われる場合の対応の流れ(マニュアルの流れ図)です。'
    t['warnings'] = ['デジカル障害で紙カルテや紙処方箋で運用した分は、デジカルにログインできるようになってから、カルテ入力と会計をデジカルに入力します。']
    t['tips'] = []
    t['parts'] = [
        {'heading': 'マニュアルの流れ図', 'steps': [
            {'text': '全体の流れは、次の流れ図のとおりです(マニュアル703〜704ページ)', 'imgs': ['img/p703_flow.jpg', 'img/p704_flow.jpg']}]},
        {'heading': 'まず確認する', 'steps': [
            {'text': 'デジカルにログインできない時は、デジカル以外のサイトが見られるか確認する'}]},
        {'heading': 'デジカル以外のサイトが見られない時', 'steps': [
            {'text': 'スマートフォンのテザリング等を利用して、インターネットに接続できる状態にする'},
            {'text': 'デジカルにログインし、ネットが復旧するまでそのまま利用する'}]},
        {'heading': 'デジカル以外のサイトが見られる時', 'steps': [
            {'text': 'デジカルサイトで障害状況を確認する(ヘルプサイト https://digikar.zendesk.com 、現在のサーバー稼働状況 https://digikar.zendesk.com/hc/ja/articles/360044476594)'},
            {'text': '障害情報が掲載されている時は「デジカル障害発生」として、下の「デジカル障害発生のとき」へ進む'},
            {'text': '障害情報が掲載されていない時は、ページを更新して障害情報を再確認する。その後は、流れ図のとおり下の「デジカル障害発生のとき」の枠へ進む'}]},
        {'heading': 'デジカル障害発生のとき', 'steps': [
            {'text': '一時的に紙カルテや紙処方箋で運用する'},
            {'text': 'カルテビューワーにログインして過去カルテを参照する(前日カルテまで参照可能)', 'note': 'カルテビューワー(過去カルテ参照システム) https://viewer.digikar.jp/ 。手順の詳細は「カルテビューワーで過去カルテを見る」。'},
            {'text': '(参考)障害発生時の対応・カルテビューワーマニュアル、障害発生時の院内運用マニュアルは、下の参考リンクから見られる'},
            {'text': '(任意のタイミングで)再度デジカルへログインする'},
            {'text': 'ログインできない時は、紙カルテ・紙処方箋での運用とカルテビューワーでの参照を続ける(流れ図の「いいえ」)'},
            {'text': 'ログインできたら、紙カルテ分をデジカルへ入力する(カルテ入力・会計)。これで完了'}]},
    ]
    log('i-shougai', '手順をPDF703〜704の流れ図どおりに組み直し: テザリング後は「デジカルにログインし、ネット復旧までそのまま利用」で終わる分岐を明記(A118)。原典にない「掲載されていれば」の再分岐と「サポートセンターに連絡」を削除。紙運用の後入力の注意をデジカル障害の分岐に限定。画像は流れ図のページ全体に差し替え', 'A118 / PDF703・704')
    for label, url, pg in [('デジカル ヘルプサイト', 'https://digikar.zendesk.com/', 703),
                           ('現在のサーバー稼働状況', 'https://digikar.zendesk.com/hc/ja/articles/360044476594', 703),
                           ('カルテビューワー(過去カルテ参照システム)', 'https://viewer.digikar.jp/', 704),
                           ('(参考)障害発生時の対応・カルテビューワーマニュアル', 'https://digikar.zendesk.com/hc/ja/articles/360053175534', 704),
                           ('(参考)障害発生時の院内運用マニュアル', 'https://viewer.digikar.jp/documents/system_failure_operation_manual_v1.0.pdf', 704)]:
        add_link('i-shougai', label, url, pg, 'A105〜A109 / PDF%d' % pg)

    # A117: PDF665・667(と同じ形の675)の本文は「保険」、画面写真は公費編集画面。原文の語を残し、事実を補足する(機械的に戻さない)
    for tid, old, pg in [('i-myna-sairai-iryofujo', '違う時は、今の公費の有効期間終了日(青枠)を入力して更新し、新しい公費を追加する', 665),
                         ('i-myna-sairai-pmh', '違う時は、今の公費の有効期間終了日(青枠)を入力して更新し、新しい公費を追加する', 667),
                         ('i-shikakukakunin-sairai-iryofujo', '違う時は、今の保険の有効期間終了日(青枠)を入力して更新し、新しい保険を追加する', 675)]:
        rep(tid, old, '相違がある時は、現在登録されている保険の有効期間終了日(青枠)を入力して更新後、新しい保険を追加する', 'A117 / PDF%d 本文' % pg)
        s = step(tid, '相違がある時は、現在登録されている保険の有効期間終了日')
        s['note'] = 'マニュアル本文の表記は「保険」です。ただし、この節の画面写真は「公費編集」の画面で、青枠は公費の有効期間の終了日の欄にあります(要確認)。'
        log(tid, '手順の補足: 本文は「保険」、画面写真は公費編集画面である事実を記載(要確認)', 'A117 / PDF%d 写真' % pg)

    # i その他
    s = step('i-ai-prompt', '送信ボタン左の「マイク」を押して話す')
    s['note'] = 'すでに文字が入力されている場合は、最終行から改行された位置から文字起こしが開始されます。'
    log('i-ai-prompt', '音声入力の手順1に補足を追加', 'PDF646')
    rep('i-ai-prompt', '「Command」(Windowsは「Ctrl」)+「Enter」', '「Command」または「Ctrl」+「Enter」', 'PDF644(Windowsの区別は原典にない)')
    rep('i-ai-seigen', '診断・処方などの医学的判断を求める内容を入れると、プロンプトの下に警告文が出る',
        '「診断・処方などの医学的判断」を求める表現が含まれているとAIが判断した場合、プロンプトの下に警告文が出る', 'PDF651')
    p = T('i-myna-ryaku')['parts'][0]
    p['steps'].append({'text': '有効資格が無い時は、新患・再来とも全額自費診療を案内する。有効資格が有る時は、新患は取得した情報を保険追加、再来は負担率等の変更を確認する'})
    log('i-myna-ryaku', '流れ図の「有効資格の有無」の分岐を手順に追加', 'PDF654 流れ図')
    del_list('i-myna-shinki-touroku', 'tips', 'カナと生年月日が一致する人の情報が表示されます', 'PDF656(医療保険登録の記載。新患登録の節にはない)')
    del_list('i-myna-shinki-hoken', 'tips', '「枝番」が未設定の時は', 'PDF656〜658 に記載なし(PDF684 電子処方箋の受付の記載)')
    rep('i-onshi-etsuran', '処方箋: 電子処方箋管理サービスから取得した処方箋情報、または院内処方などの情報',
        '処方箋: 自院・他院が電子処方箋管理サービスに登録した処方箋情報、院内処方情報が表示される', 'PDF677')
    add_list('i-epre-hikikae-settei', 'warnings', '電子処方箋の機能を使うには、オンライン資格確認システムが起動している必要があります。', 'PDF682 冒頭', pos=0)
    del_list('i-epre-hyojun-yoho-check', 'warnings', '標準用法マスタ以外の用法のまま登録すると', 'PDF686(引換番号付き紙処方箋希望の場合の注意)')
    s = step('i-epre-hyojun-yoho-check', '「!」を押すと、「電」がついている用法を選び直すように表示される')
    s['note'] = 'カルテ保存時には表示されない。標準用法マスタ以外の用法をそのまま登録すると、引換番号なしの従来処方箋が印字される。'
    log('i-epre-hyojun-yoho-check', '「標準用法以外だと引換番号なしの処方箋になる」注意を、引換番号付き紙処方箋希望の場合の手順へ移す', 'PDF686')
    rep('i-inai-karte', 'コメント補足が必要な用法は「電子処方箋の用法コメント補足」のトピックを見る。', 'コメント補足が必要な用法は「補足コメントが必要な用法を入力」を見る。', 'PDF698(参照先の名前)')

    # 外部リンク(A098〜A104・A110)
    import json, os
    pdf_links = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pdf_links.json')))

    def uri(page, prefix):
        hits = sorted({l['uri'] for l in pdf_links if l['page'] == page and l['uri'].startswith(prefix)})
        assert len(hits) == 1, (page, prefix, hits)
        return hits[0]
    for label, pre in [('オン資等システムより取得した診療薬剤情報をデジカルで閲覧したい', 'https://digikar.zendesk.com/hc/ja/articles/53466680344985'),
                       ('オンライン資格確認等システムから取得した診療薬剤情報がデジカルで閲覧できない', 'https://digikar.zendesk.com/hc/ja/articles/53637258888985'),
                       ('初めて来院した患者様や久しぶりに来院した患者様について、診療情報等がデジカルに反映しない', 'https://digikar.zendesk.com/hc/ja/articles/54399707831961')]:
        add_link('i-onshi-sakujo', label, uri(678, pre), 678, 'A098〜A100 / PDF678')
    add_link('i-epre-tsuushin-error', 'オンライン資格確認で確認結果が表示されない(ヘルプサイト)', uri(692, 'https://digikar.zendesk.com/hc/ja/articles/8900175306777'), 692, 'A101 / PDF692')
    for label, url in [('マニュアルPDF', 'https://digikar.m3.com/documents/digikar_rececom_manual.pdf'),
                       ('マニュアル動画', 'https://www.youtube.com/channel/UCHoZzLcfieRDa8DIrYj7yKQ'),
                       ('ヘルプサイト', 'https://digikar.zendesk.com/')]:
        add_link('i-help-menu', label, url, 701, 'A102〜A104 / PDF701')
    add_link('i-karte-viewer', 'カルテビューワー', 'https://viewer.digikar.jp/', 705, 'A110 / PDF705')
