#!/bin/bash
# 試作のHTMLを画像に書き出す
cd "$(dirname "$0")"
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for f in A_エントランス B_白と明朝 C_1日の流れ; do
  "$CH" --headless=new --hide-scrollbars --force-device-scale-factor=1 --window-size=1440,1000 --virtual-time-budget=3000 --screenshot="$PWD/トップ画面の試作_$f.png" "file://$PWD/$f.html" >/dev/null 2>&1
done
ls -la *.png
