# デジカル操作ガイド(やまうちクリニック)

電子カルテ「デジカル」の操作マニュアル(705ページ、2026年10月27日更新)を、やりたいことから検索できるようにしたWebページです。

## フォルダ
- `site/` … 完成したページ。`index.html` を開くと使えます(サーバーに置く時はこのフォルダごと)
- `data/` … 分野ごとの手順データ(9分野)
- `work/` … 作り直し用の道具
- `完成/` … 納品用のかんたん説明書(PDF)
- `説明書/` … 説明書の元(HTML)
- `試作/` … トップ画面の見た目の試作(不採用)

## 公開(GitHub Pages)
`main` に送ると、`site/` が自動で GitHub Pages に公開されます(`.github/workflows/pages.yml`)。
最初の1回だけ、保存場所の Settings → Pages で「Source」を「GitHub Actions」にしてください。
無料のアカウントでは、保存場所が「公開(Public)」の時だけ使えます。

## マニュアルが更新された時の作り直し
1. `python3 work/extract.py <新しいPDF>` … 画面写真と文字を取り出す
2. 変わったページの `data/topics_*.json` を直す(決まりは `work/SCHEMA.md`、確認は `work/check.py`)
3. `python3 work/build.py` … `site/data.js` を作り直し、版番号を付け直す

必要なもの: Python 3、PyMuPDF、Pillow
