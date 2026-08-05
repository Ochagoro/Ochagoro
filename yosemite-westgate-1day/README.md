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
- `src/build.py` — テンプレートにアセットを埋め込んで `index.html` を生成する。

## 中身

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
```

`build.py` は2種類を吐く。`standalone.html` が `index.html` になるもので、
`<meta charset>` と viewport と `lang="ja"` を持つ完全な HTML ドキュメント。
この3つが無いとスマホのブラウザが日本語を化けさせたり、980px幅でレイアウトして
極端に縮小表示したりする（Chrome の文字コード推測は当たるが iOS Safari は外す）。

## 前提と注意

8月上旬の平日を想定。日の出6:10／日没20:05は概算で月内に約30分ずれる。
道路状況・工事・山火事で計画は変わるため、出発前夜に NPS の
[Current Conditions](https://www.nps.gov/yose/planyourvisit/conditions.htm) を確認すること。

写真はすべて Wikimedia Commons のパブリックドメイン／クリエイティブ・コモンズ画像。
クレジットはページ下部に記載。
