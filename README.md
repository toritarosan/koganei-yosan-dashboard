# 小金井よさんラボ

小金井市の令和8年度一般会計予算（546億円）を、市民が「さわって探検」できる予算可視化サイト。

**公開URL**: https://toritarosan.github.io/koganei-yosan-dashboard/

## 特徴

- **ヒーロー**: 546億円を市民1人あたり・1日あたりに換算
- **税金シミュレータ**: 年収から市民税を概算し、その使い道を1日あたりで表示
- **予算ドリルダウン**: 款→項→目→事業→節→細目までツリーマップで探検
- **予算検索（RAG）**: 「子育て」「ゴミ収集」など話しことばで520事業を根拠つき検索
- **新規事業ハイライト**: 令和8年度に始まる20事業
- **予算ガチャ / 4か年推移**: 4,500件からランダム紹介、R5〜R8の分野別推移

技術: 静的サイト（HTML + ECharts）。データは検算済みの予算JSONから生成。追加のサーバは不要。

## ディレクトリ

```
index.html            サイト本体（単一ファイル）
data/r8.json          予算データ（款〜細目 + 検索用flat + 4か年推移）
data/new_projects.json 新規事業20件
og-image.png / .svg   OGP画像
build_data.py         予算JSON → data/r8.json 生成
make_og.py            OGP画像生成
worker/               よさんAI用 Cloudflare Worker（任意）
```

## データ更新

年度更新や予算JSONを差し替えたら再生成するだけ:

```bash
python site/build_data.py     # → site/data/r8.json
```

データ出典: 令和8年度小金井市一般会計予算 事項別明細書。目・事業・節・細目の全階層で検算済み。

## AI検索（よさんAI）の有効化（任意）

検索は標準でサーバ不要（ブラウザ内で完結し「根拠データ」を表示）。AIによる要約回答を足す場合:

```bash
cd site/worker
wrangler secret put GEMINI_API_KEY   # Gemini APIキーを登録
wrangler deploy
```

発行された Worker URL を `index.html` の `const AI_ENDPOINT` に設定する。

## デプロイ（GitHub Pages）

master ブランチの root を公開。`.nojekyll` により Jekyll 処理はスキップ。

## 免責

本サイトは有志が公開データをもとに作成した非公式サイトです。正確・最新の情報は
[小金井市公式サイト](https://www.city.koganei.lg.jp/)をご確認ください。
