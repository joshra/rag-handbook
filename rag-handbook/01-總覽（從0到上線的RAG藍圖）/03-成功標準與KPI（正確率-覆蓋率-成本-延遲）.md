# 03-成功標準與 KPI（正確率 / 覆蓋率 / 成本 / 延遲）

## 你將學到（Learning Objectives）

- 能把「RAG 做得好」翻譯成可量測的 KPI / SLO
- 能分清楚：檢索成功 ≠ 回答成功
- 能建立最小評估迴圈：離線 → 線上 → 失敗分類 → 改進

## 本章地圖

- **適合用在**：要用 KPI 定義 RAG 是否成功，並把討論從感覺拉回數據時。
- **你會做出**：離線/線上指標與成本/延遲的控制目標。
- **最可能踩雷**：只看回答好不好，不看 retrieval 命中與失敗分類。

## 先定義「成功」是什麼（避免做成玩具）

RAG 的成功通常不是「模型回答像人」，而是：

- **能回答該回答的問題**（覆蓋率）
- **回答有依據且正確**（正確率/可引用）
- **不該回答就拒答或追問**（安全性與信任）
- **在可接受成本與延遲下運行**（可上線）

## KPI 分層：Retrieval vs Generation

### 檢索層（Retrieval）

- **Recall@k（命中率）**：正確證據是否出現在 top-k
- **Precision@k（精準度）**：top-k 裡有多少是真的相關（越高越好，但與 recall 取捨）
- **Filter correctness**：權限/租戶/版本 filter 是否正確（安全 KPI）

### 生成層（Generation）

- **Answer correctness**：答案是否正確（人工標註或 LLM-as-judge 輔助）
- **Faithfulness / Groundedness**：答案是否只依據提供證據（避免「自己編」）
- **Citation quality**：引用是否指向正確 chunk/章節/頁碼
- **Refusal quality**：證據不足時是否正確拒答/追問

## 系統層（可上線）

- **Latency**：P50/P95/timeout 比例（拆分 retrieval/rerank/llm）
- **Cost**：每次請求平均成本（token、rerank 次數、embedding 次數）
- **Stability**：錯誤率、降級觸發率、重試率

## 建議的 SLO（起手式）

你可以先定一個務實的起手式：

- P95 latency：< 3～6 秒（依場景）
- Answer correctness（人工抽查）：> 70%（試點）→ > 85%（上線成熟）
- 具引用回答比例：> 80%（知識型場景）
- 越權/敏感外洩：0（硬性）

## 失敗分類（最有用的除錯地圖）

建議至少分成：

- **Retrieval miss**：top-k 沒召回正確證據（切分/embedding/查詢/filters 問題）
- **Retrieval noisy**：召回一堆無關（chunk 太大/太小、filters 太寬、rerank 缺失）
- **Generation hallucination**：證據有但模型亂答（prompt、引用規則、context packing）
- **Policy failure**：應該拒答卻硬答（不可回答策略、閾值、guardrails）

## 本章小結

- 先把成功拆成 Retrieval 與 Answer 兩段衡量，才能知道問題出在哪一段。
- KPI 必須同時納入：正確率、覆蓋率、成本與延遲（以及越權/合規風險）。
- 沒有失敗分類的指標只能「看起來在量測」，無法支撐迭代。

## 延伸閱讀

- [01-離線評估：Retrieval-Answer指標與資料集](../06-評估與觀測（讓工程團隊能迭代）/01-離線評估：Retrieval-Answer指標與資料集.md)
- [03-可觀測性：log-trace-命中率-失敗分類](../06-評估與觀測（讓工程團隊能迭代）/03-可觀測性：log-trace-命中率-失敗分類.md)
- [04-效能與成本：快取-批次-串流-降延遲](../07-工程化與上線（Django+Postgres實作）/04-效能與成本：快取-批次-串流-降延遲.md)
