# 06-版本化與可重現：資料 / 索引 / embedding / prompt 版本

## 你將學到（Learning Objectives）

- 能回答這句上線必問：**「這個答案，是用哪一版資料與哪一版模型產生的？」**
- 能設計最小版本化策略，支援回補、回歸測試與事故追查

## 本章地圖

- **適合用在**：要做回歸測試、事故回放與安全切換版本（藍綠/雙跑）時。
- **你會做出**：資料/索引/embedding/prompt 的版本欄位與切換流程。
- **最可能踩雷**：版本散落在多處不可追溯；線上回答無法對應到版本。

## 為什麼版本化是 RAG 上線核心

RAG 的輸出會因為以下任一變動而改變：

- 文件內容更新（資料變了）
- chunking 規則更新（切分變了）
- embedding 模型更新（向量空間變了）
- 檢索參數更新（top-k/MMR/filters 變了）
- prompt 模板更新（生成策略變了）

如果沒有版本化，系統「看起來像在亂跳」，團隊無法迭代。

## 最小版本化清單（建議必做）

### 文件/資料版本

- doc_id
- doc_version（內容變更就 +1，或用 hash）
- ingest_version（一次導入批次 id）

### chunk 版本

- chunker_version（切分規則版本）
- chunk_id（可重算，建議可由 doc_id+range+hash 推導）

### embedding 版本

- embedding_model_name
- embedding_model_version
- embedding_dim

### 檢索/生成版本

- retriever_version（參數集合版本）
- prompt_version（模板版本）
- llm_model_name / llm_model_version（若有）

## 建議的上線流程（避免抖動）

- 新版本資料先「並行建索引」到另一個版本/命名空間
- 線上查詢只使用 active_version
- 切換版本用 config/旗標一次切換
- 回歸測試：對固定問題集比較新舊版本差異

## 本章小結

- 版本化的目標是可重現：同一題在同一版本應得到同等級的可解釋結果。
- 最小版本集合：資料版本、chunking/cleaner 版本、embedding 版本、索引版本、prompt 版本。
- 上線切換要可控：並行建索引 → 回歸 → 切換 active → 觀測 → 回收舊版。

## 延伸閱讀

- [01-離線評估：Retrieval-Answer指標與資料集](../06-評估與觀測（讓工程團隊能迭代）/01-離線評估：Retrieval-Answer指標與資料集.md)
- [03-可觀測性：log-trace-命中率-失敗分類](../06-評估與觀測（讓工程團隊能迭代）/03-可觀測性：log-trace-命中率-失敗分類.md)
