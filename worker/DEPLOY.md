# よさんAI バックエンドのデプロイ手順

AI検索の「要約回答」を有効化するための手順です。
（※検索そのものはバックエンド無しでも動作します。これはAI要約を足すための任意ステップ）

前提: Node.js（インストール済み）、Cloudflareの無料アカウント、Gemini APIキー

## 手順（対話ターミナルで実行）

```bash
cd site/worker
npm install                 # wrangler を取得
npx wrangler login          # ← ブラウザが開きCloudflareにログイン（この一手だけ対話が必要）
npx wrangler secret put GEMINI_API_KEY   # ← Gemini APIキーを貼り付けてEnter
npx wrangler deploy         # デプロイ実行
```

デプロイ成功すると次のようなURLが表示される:
```
https://yosan-ai.<あなたのサブドメイン>.workers.dev
```

## 仕上げ（サイト側にURLを設定）

1. `site/index.html` の以下の行に、上で発行されたURLを設定:
   ```js
   const AI_ENDPOINT = "https://yosan-ai.xxx.workers.dev";
   ```
2. データを反映して再公開:
   ```bash
   cd ..                      # site/ へ
   cp index.html ../dashboard-site/
   cd ../dashboard-site
   git add -A && git commit -m "AI検索を有効化" && git push
   ```

## Gemini APIキーの取得

https://aistudio.google.com/apikey で無料で発行できます。
（旧よさんラボ〔HF Spaces〕のSecretに設定済みのキーがあれば、それを再利用可能）

## 動作確認

サイトの「予算に、聞いてみる」で検索すると、根拠データの上に「よさんAI」の要約が表示されます。
接続できない場合は自動で根拠データ表示にフォールバックします。
