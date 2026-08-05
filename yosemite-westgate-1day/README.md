# ヨセミテ 1日プラン — West Gate Lodge 発

Yosemite Westgate Lodge（Buck Meadows, CA / State Hwy 120）を拠点に、
ヨセミテ国立公園を1日で味わい尽くすための単一ファイル Web ページ。

- `index.html` — 完成品。写真・フォントすべて data URI で埋め込んだ自己完結の1ファイル（約1.9MB）。
  ダブルクリックでブラウザで開くだけで動く。サーバー不要・ネット接続不要。
  ローカルで配信したいだけなら `python3 -m http.server` でも可。
- `artifact-fragment.html` — 同じ内容の body フラグメント。`<head>` を自前で用意する
  ホスティング環境（Claude Artifacts など）向け。**スマホに送るなら `index.html` の方**。
- `src/template.html` — 編集用のソース。画像とフォントは `{{IMG:key}}` / `{{FONT:name}}` のプレースホルダ。
- `src/fetch_assets.py` — Wikimedia Commons から写真を取得して WebP に再エンコードし、
  Google Fonts から Latin サブセットの woff2 を落とす。
- `src/build.py` — テンプレートにアセットを埋め込んで2種類の成果物を生成する。
- `src/verify.py` — 2つの成果物が同一に描画されることを検証する（要素のボックス比較＋ピクセル比較）。
- `src/failmodes.py` — スクロール連動の表示演出が失敗しても本文が消えないことを検証する。

## 中身

- 移動日（8/5 水）: Mountain View 11:00 発 → Groveland で補給 → ロッジ →
  到着後の4時間半の使い方3案（セコイア / Hetch Hetchy / 渓谷直行）
- 出発前に効いてくる道路規制・工事・トレイル閉鎖のまとめ
- 本命プラン（04:45 起床 → 22:45 帰着）: 渓谷の朝 → 川で昼 → Glacier Point で日没
- 別プラン2案: Tioga Road 高地プラン / 半日ゆったりプラン
- 1日の標高プロファイル（930m → 2,476m → 930m）
- 持ち物チェックリスト（24項目・localStorage に保存）
- 前夜にやること6つ / 現地の掟4つ（熊・圏外・駐車・暑さ）

## 作り直すとき

```sh
cd src
python3 -m pip install Pillow
python3 fetch_assets.py   # img/ と fonts/ を生成
python3 build.py          # standalone.html と artifact 用フラグメントを出力
python3 verify.py         # 2つが同一に描画されるか検証
```

`build.py` は2種類を吐く。`standalone.html` が `index.html` になるもので、
`<meta charset>` と viewport と `lang="ja"` を持つ完全な HTML ドキュメント。
この3つが無いとスマホのブラウザが日本語を化けさせたり、980px幅でレイアウトして
極端に縮小表示したりする（Chrome の文字コード推測は当たるが iOS Safari は外す）。

スタイルシートはリセットを自前で持っている。ブラウザの初期値に頼った箇所があると、
フラグメントを埋め込むホスト側のリセット CSS 次第で見え方が変わってしまうため。
`verify.py` はフラグメントをあえて強めのリセットで包んで standalone と突き合わせ、
差分が出たら落ちる。`build.py` は `clamp()` / `calc()` 内で `+` `-` の前後に
スペースが無い箇所も弾く（CSS の数式では無効値になり、宣言ごと捨てられる）。

## スマホで壊れないための制約

コンテンツを隠す仕組みは、必ず「見える方向」に倒れるようにしてある。

- スクロール連動の表示演出（`.rv`）の非表示状態は `html.js` に限定してある。
  JS が動かなければ最初から全部見えている。加えて読み込み3秒後に強制表示する
  タイマーがあるので、IntersectionObserver が発火しなくても本文は消えない。
  `failmodes.py` が JS 無効・IO 無し・IO が発火しない、の3ケースを検証する。
- 画面全体を覆う固定レイヤーに `mix-blend-mode` を使わない。ページ全体が
  1枚の合成面に載り、長いページだと iOS Safari が再描画を落とす。
- `backdrop-filter` は上部ナビだけ。大きいカードには使わない。
- 負の `z-index` を使わない（iOS で背景の裏に回り込むことがある）。
- `color-mix()` を使った箇所は `@supports not` で rgba の代替を持つ。
  Safari 16.4 未満だと `--rail` ごと無効になり、罫線が一斉に消える。

## 前提と注意

8月上旬の平日を想定。日の出6:10／日没20:05は概算で月内に約30分ずれる。
道路状況・工事・山火事で計画は変わるため、出発前夜に NPS の
[Current Conditions](https://www.nps.gov/yose/planyourvisit/conditions.htm) を確認すること。

写真はすべて Wikimedia Commons のパブリックドメイン／クリエイティブ・コモンズ画像。
クレジットはページ下部に記載。
