/**
 * よさんAI バックエンド（Cloudflare Worker 参照実装）
 * フロント(site/index.html)の askAI() が {question, context} をPOSTし、
 * Gemini で「根拠に基づく市民向け回答」を生成して返す。
 *
 * デプロイ:
 *   1. npm i -g wrangler
 *   2. wrangler secret put GEMINI_API_KEY   （Gemini APIキーを登録）
 *   3. wrangler deploy
 *   4. 発行されたURLを site/index.html の AI_ENDPOINT に設定
 *
 * RAG設計: 検索(retrieval)はブラウザ側で完結し、ヒットした事業データのみを
 * context として渡すため、予算全文を送らずトークンを最小化できる。
 */
const MODEL = "gemini-2.5-flash"; // レート制限/障害時のフォールバックは 'gemini-2.0-flash'

const SYSTEM = `あなたは小金井市「よさんラボ」の予算アシスタントです。
市民の質問に、渡された【関連予算データ】だけを根拠にやさしく答えてください。
ルール:
- 金額は「億円」「万円」で表記（データは千円単位）
- 必ず根拠の事業名を示す（例:「〇〇事業(△△課)に□□万円が計上されています」）
- データに無いことは推測せず「予算書に記載が見つかりませんでした」と答える
- 政治的評価は避け、事実と数値で簡潔に。3〜5文程度`;

export default {
  async fetch(req, env) {
    if (req.method === "OPTIONS") return cors(new Response(null, { status: 204 }));
    if (req.method !== "POST") return cors(new Response("POST only", { status: 405 }));

    let body;
    try { body = await req.json(); } catch { return cors(json({ error: "bad json" }, 400)); }
    const { question, context } = body;
    if (!question) return cors(json({ error: "no question" }, 400));

    const prompt = `${SYSTEM}\n\n【質問】\n${question}\n\n【関連予算データ】\n${context || "(なし)"}`;
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${env.GEMINI_API_KEY}`;
    try {
      const r = await fetch(url, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] }),
      });
      const j = await r.json();
      const answer = j?.candidates?.[0]?.content?.parts?.[0]?.text || "回答を生成できませんでした。";
      return cors(json({ answer }));
    } catch (e) {
      return cors(json({ error: String(e) }, 500));
    }
  },
};

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: { "content-type": "application/json" } });
}
function cors(res) {
  res.headers.set("access-control-allow-origin", "*");
  res.headers.set("access-control-allow-methods", "POST, OPTIONS");
  res.headers.set("access-control-allow-headers", "content-type");
  return res;
}
