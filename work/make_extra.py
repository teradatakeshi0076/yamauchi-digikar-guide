"""通常の切り出しでは扱えない画像を作る(監査A005〜A043 の小さい画像・図への対応)。
- 流れ図のページ全体: img/p703_flow.webp, img/p704_flow.webp
- 図: img/p116_level.webp(処方監査の警告レベル), img/p086_palette.webp(シェーマのペン・色の選択)
- 本文に差し込むアイコン: img/icon_pNNN_K.webp
"""
import fitz, os, sys
from PIL import Image, ImageFilter

PDF = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'site', 'img')
doc = fitz.open(PDF)


def render(pno, rect, name, zoom, target_w=None):
    page = doc[pno - 1]
    clip = fitz.Rect(rect) & page.rect
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    if target_w and target_w > im.width:
        im = im.resize((target_w, round(im.height * target_w / im.width)), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=80, threshold=2))
    im.save(os.path.join(IMG, name), 'WEBP', quality=82, method=4)
    print(name, im.size)


# 流れ図: ページの本文部分全体(上下の余白とページ番号を除く)
for p in (703, 704):
    page = doc[p - 1]
    render(p, fitz.Rect(40, 60, page.rect.width - 15, page.rect.height - 70), 'p%03d_flow.webp' % p, 3.0)

# 警告レベルの図(PDF116): レベル1〜3のマークと矢印、「警告レベル」「高」「低」の文字を含む枠
render(116, fitz.Rect(70, 588, 400, 742), 'p116_level.webp', 4.0)
# シェーマのペン・色の選択(PDF86): 色のパレットと ②〜④ の説明
render(86, fitz.Rect(320, 520, 595, 612), 'p086_palette.webp', 4.0)

# 通常の切り出しでは2枚の写真が同じ範囲になってしまう箇所を、写真ごとに切り出し直す(上書き)。
# 必ず extract.py の後に実行する
def native_zoom(pno, rect):
    page = doc[pno - 1]
    best = 2.0
    for info in page.get_image_info():
        r = fitz.Rect(info['bbox'])
        if r.intersects(rect):
            best = max(best, info['width'] / max(r.width, 1))
    return min(4.0, best)


OVERRIDES = {
    'p617_1.webp': (617, (60, 268, 263, 378)),   # 初回算定の入力画面
    'p617_2.webp': (617, (112, 414, 278, 458)),  # 「検」→「算定しない」
    'p632_1.webp': (632, (55, 181, 273, 288)),   # 左: 「コメントを追加」メニュー
    'p632_2.webp': (632, (315, 181, 531, 288)),  # 右: 「両側」・回数2
    'p196_2.webp': (196, (77, 201, 402, 391)),   # 会計画面 +「←返金額」の札
}
for name, (p, r) in OVERRIDES.items():
    rect = fitz.Rect(r)
    z = native_zoom(p, rect)
    disp = min(1300, max(360, z * rect.width * 1.3))
    render(p, rect, name, z, target_w=round(2 * disp))

# 本文に差し込む小さなアイコン(PDF の画像の位置そのまま。少し余白をつける)
ICONS = {
    'icon_p030_1.webp': (30, (84, 94, 119, 127)),    # まとめて表示
    'icon_p030_2.webp': (30, (325, 94, 356, 125)),   # 全て表示
    'icon_p107_1.webp': (107, (279, 514, 296, 541)), # セットの並び替えの取っ手
    'icon_p163_1.webp': (163, (137, 69, 157, 86)),   # 処方年月の ✔ マーク
    'icon_p223_1.webp': (223, (222, 521, 240, 539)), # 診療履歴の編集ボタン
    'icon_p252_1.webp': (252, (313, 520, 344, 551)), # ダウンロードアイコン
    'icon_p259_1.webp': (259, (222, 161, 240, 179)), # 診療履歴の編集ボタン(労災)
    'icon_p272_1.webp': (272, (222, 161, 240, 179)), # 診療履歴の編集ボタン(自賠責)
    'icon_p316_1.webp': (316, (109, 197, 130, 219)), # 削除ボタン(ごみ箱)
    'icon_p316_2.webp': (316, (110, 228, 131, 248)), # 別タブでカルテ表示
    'icon_p316_3.webp': (316, (190, 103, 221, 126)), # RME ボタン(受付画面)
    'icon_p316_4.webp': (316, (224, 374, 248, 394)), # 患者リスト
    'icon_p316_5.webp': (316, (351, 373, 382, 396)), # RME ボタン(患者リスト)
}
for name, (p, r) in ICONS.items():
    x0, y0, x1, y1 = r
    render(p, fitz.Rect(x0 - 1, y0 - 1, x1 + 1, y1 + 1), name, 8.0)
