# ヨセミテ 1日プラン — West Gate Lodge 発

Yosemite Westgate Lodge（Buck Meadows, CA / State Hwy 120）を拠点に、
ヨセミテ国立公園を1日で味わい尽くすための単一ファイル Web ページ。

## 成果物

- `index.html` — **英語版**。写真・フォントすべて data URI で埋め込んだ自己完結の1ファイル
  （約2.2MB）。ダブルクリックでブラウザで開くだけで動く。サーバー不要・ネット接続不要。
  人に渡すのはこれ。ローカルで配信したいだけなら `python3 -m http.server` でも可。
- `index.ja.html` — 日本語版。中身は同じ。
- `artifact-fragment.html` — 日本語版の body フラグメント。`<head>` を自前で用意する
  ホスティング環境（Claude Artifacts など）向け。**人に送るなら `index.html` の方**。

## ソース

- `src/template.html` — 日本語版のソース。スタイルとスクリプトの正本もここ。
  画像とフォントは `{{IMG:key}}` / `{{FONT:name}}` のプレースホルダ。
- `src/body.en.html` — 英語版の本文だけ。スタイルとスクリプトは `template.html` から
  そのまま流用されるので、CSS や JS の修正が片方の言語だけに入ることはない。
- `src/fetch_assets.py` — Wikimedia Commons から写真を取得して WebP に再エンコードし、
  Google Fonts から Latin サブセットの woff2 を落とす。
- `src/build.py` — アセットを埋め込んで3種類の成果物を生成する。
- `src/verify.py` — 日本語の完全版とフラグメントが同一に描画されることを検証する。
- `src/nojs.py` — JS 有効・無効の両方でプラン切り替えとチェックリストが動くことを検証する。
- `src/enchk.py` — 英語版を3つの画面幅で読み込んでエラーと横スクロールを見る。

## 中身

- 移動日（8/5 水）: Mountain View 11:00 発 → Groveland で補給 → ロッジ →
  到着後の4時間半の使い方3案（セコイア / Hetch Hetchy / 渓谷直行）
- 出発前に効いてくる道路規制・工事・トレイル閉鎖のまとめ
- 本命プラン（04:45 起床 → 22:45 帰着）: 渓谷の朝 → 川で昼 → Glacier Point で日没
- 別プラン2案: Tioga Road 高地プラン / 半日ゆったりプラン
- 1日の標高プロファイル（930m → 2,476m → 930m。英語版は ft 表記）
- 持ち物チェックリスト（24項目・localStorage に保存）
- 前夜にやること6つ / 現地の掟4つ（熊・圏外・駐車・暑さ）

## 作り直すとき

```sh
cd src
python3 -m pip install Pillow playwright
python3 fetch_assets.py   # img/ と fonts/ を生成
python3 build.py          # 3種類の成果物を出力
python3 verify.py         # 完全版とフラグメントが同一か
python3 nojs.py           # JS 無効でも操作できるか
python3 enchk.py          # 英語版の各画面幅
```

`build.py` は日英の本文を突き合わせて、id の集合・チェックボックス数・ラジオ数・
パネル数・画像数が食い違ったらビルドを落とす。片方の言語に要素を足し忘れると止まる。

## 壊れないための制約

過去に踏んだ落とし穴と、その再発防止。

**完全な HTML ドキュメントであること。** `<meta charset>` と viewport と `lang` が
無いと、スマホのブラウザが文字コードを推測して日本語を化けさせたり、980px幅で
レイアウトして極端に縮小表示したりする（Chrome の推測は当たるが iOS Safari は外す）。
`build.py` が先頭1024バイト以内にあるか検査する。

**ブラウザの初期値に頼らない。** リセットはスタイルシートが自前で持つ。初期値に
頼った箇所があると、フラグメントを埋め込むホスト側のリセット CSS 次第で見え方が
変わる。`verify.py` がフラグメントをあえて強めのリセットで包んで突き合わせる。
`build.py` は `clamp()` / `calc()` 内で `+` `-` の前後にスペースが無い箇所も弾く
（CSS の数式では無効値になり、宣言ごと捨てられる）。

**JS が動かない前提で作る。** ファイルのプレビュー表示やアプリ内ブラウザでは JS が
まったく動かないことがある。

- プラン切り替えは `<input type="radio">` と `:checked` だけで動く。JS は使わない。
- チェックリストの総数は HTML に直接書いてある（`build.py` が実数と一致するか検査）。
  チェック自体は CSS で付く。カウンタと保存だけが JS で、動かない環境では
  `<noscript>` がその旨を出し、リセットボタンは隠れる。
- スクロール連動の表示演出（`.rv`）の非表示状態は `html.js` に限定。JS が動かなければ
  最初から全部見えている。加えて読み込み3秒後に強制表示するタイマーがある。

**iOS Safari が苦手な合成を避ける。**

- 画面全体を覆う固定レイヤーに `mix-blend-mode` を使わない。ページ全体が1枚の
  合成面に載り、長いページだと再描画を落とす。
- `backdrop-filter` は上部ナビだけ。大きいカードには使わない。
- 負の `z-index` を使わない（背景の裏に回り込むことがある）。
- `color-mix()` を使った箇所は `@supports not` で rgba の代替を持つ。
  Safari 16.4 未満だと `--rail` ごと無効になり、罫線が一斉に消える。

## 前提と注意

8月上旬の平日を想定。日の出6:10／日没20:05は概算で月内に約30分ずれる。
Mist Trail の階段部分は10月まで月〜木の 7:00–15:30 が閉鎖、El Portal Road は
夜間工事あり。道路状況・工事・山火事で計画は変わるため、出発前に
209-372-0200（1→1）か NPS の
[Current Conditions](https://www.nps.gov/yose/planyourvisit/conditions.htm) を確認すること。

写真はすべて Wikimedia Commons のパブリックドメイン／クリエイティブ・コモンズ画像。
クレジットはページ下部に記載。
