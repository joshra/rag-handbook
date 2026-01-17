# 03-可觀測性：log / trace / 命中率 / 失敗分類

## 你將學到（Learning Objectives）

- 知道 RAG 需要觀測什麼，才有辦法除錯與迭代
- 能設計 trace 結構，支援「回放一次回答」的全鏈路資料
- 能把觀測資料直接連到失敗分類（可行動）

## 本章地圖

- **適合用在**：上線後要能除錯、回放、歸因與持續迭代時。
- **你會做出**：trace schema、命中率/耗時/成本指標與失敗分類儀表板。
- **最可能踩雷**：只記答案不記候選 chunks；沒有版本欄位導致不可重現。

## 為什麼 RAG 特別需要可觀測性

因為它是多階段系統：

- ingest/indexing
- retrieval（含 filter、merge、rerank）
- generation（prompt/context/輸出）

任何一段出錯，表面都會看起來像「模型亂答」。

## 最小 trace 結構（建議）

每次請求都產生 `trace_id`，並記錄：

- **request**：tenant_id、user_id、timestamp、question、filters
- **retrieval**：
  - query（含 rewrite/expand 前後）
  - 各路召回的 top-k（id、分數、doc_id、引用資訊）
  - 最終選入 context 的 chunks（含排序原因可選）
- **generation**：
  - prompt_version、llm_model、token 使用（或長度近似）
  - answer、citations、refusal_reason（若有）
- **timing**：每段 latency + total
- **versioning**：active_version、embedding_model_version、chunker_version

## 命中率/品質指標（線上）

- recall proxy：引用是否被使用者點擊/展開（視產品）
- refusal rate：拒答比例（太高或太低都要檢查）
- citation accuracy（抽樣人工檢查）

## 把觀測轉成「能修的問題」

建議每天/每週輸出：

- Top 失敗 query（負評/拒答/超時）
- 失敗分類分佈（retrieval miss/noisy/generation）
- 最常命中的 doc_type（用於優先清理與優化）

## 本章小結

- 可觀測性要覆蓋整條鏈：query → 候選 → rerank → context → 生成 → 引用 → 回應。
- 每次問答都應能回放：取了哪些 chunk、分數如何、為何被引用、耗時在哪。
- 失敗分類是把 log 變成迭代能力的關鍵：retrieval miss/noisy、generation、越權、超時等。

## 延伸閱讀

- [03-Django整合：API設計-背景任務-快取-速率限制](../07-工程化與上線（Django+Postgres實作）/03-Django整合：API設計-背景任務-快取-速率限制.md)
- [06-版本化與可重現：資料-索引-embedding-prompt版本](../07-工程化與上線（Django+Postgres實作）/06-版本化與可重現：資料-索引-embedding-prompt版本.md)
