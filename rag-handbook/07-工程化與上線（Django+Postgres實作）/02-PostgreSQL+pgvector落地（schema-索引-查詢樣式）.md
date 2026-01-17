# 02-PostgreSQL + pgvector 落地（schema / 索引 / 查詢樣式）

## 你將學到（Learning Objectives）

- 了解為什麼「先用 Postgres + pgvector」是常見的可上線起手式
- 知道 schema 需要怎麼設計，才能支援：**權限 filter、版本化、引用回溯**
- 了解向量查詢的基本能力點與索引選型（先能跑、再能快、最後能穩）

## 本章地圖

- **適合用在**：要用 Postgres 先落地向量檢索，並確保查詢形狀可控時。
- **你會做出**：schema、索引、查詢樣式與效能/限制的工程準則。
- **最可能踩雷**：索引沒用上、filter 破壞索引、k 值/維度導致效能爆炸。

## 何時選 pgvector（以及何時不該）

### 適合

- 你已經有 PostgreSQL 維運能力（備份、監控、權限）
- 早期流量不大（或可以接受較高延遲）
- 需要把 metadata filter（權限/租戶）做得很「資料庫原生」

### 可能不適合

- 需要高吞吐、低延遲且向量量級很大（例如數千萬以上，依硬體而異）
- 需要更成熟的向量能力（更完整分片、向量壓縮、HNSW 調參、向量搜尋專用觀測）

本手冊策略：**先用 pgvector 上線**，需要時再抽換成專用向量庫（介面保持一致）。

## 建議的資料模型（概念）

你至少需要三層概念：

- **documents**：原始文件（或文件版本）
- **chunks**：切分後片段（含引用資訊）
- **embeddings**：chunk 對應的向量（含 embedding model 版本）

實務上可以合併（例如 embeddings 直接放在 chunks 表），但分開的好處是版本化與回補更清楚。

## 必備欄位（再次強調）

- **doc_id / source_uri**：可回溯
- **title_path / page / section**：可引用
- **tenant_id / acl**：權限隔離
- **ingest_version / embedding_model_version**：可重現

## 查詢樣式（你應該具備的能力點）

> 提醒：不同 pgvector 版本與索引類型（IVFFlat/HNSW）在語法與運算子上可能略有差異。
> 本章先用「能力點」描述你應該做得到什麼；範例專案會給可執行 SQL。

### 1) 基本向量近鄰（取 top-k）

- 輸入：query_vector
- 輸出：最相近的 k 個 chunk（含 doc_id、source_uri、title_path/page）

### 2) metadata filter（租戶/權限/文件類型）

- 查詢必須支援 tenant_id、doc_type、時間範圍、資料版本等條件
- **務必**把權限條件納入 DB 查詢（metadata filter），不要只在應用層做後過濾

### 3) 混合檢索（全文 + 向量）

- 用 Postgres 全文檢索（tsvector）做關鍵字召回（或 ranking）
- 與向量召回合併（多路召回後 merge），再做 rerank（通常效果最好）

## 索引選型（你要知道的重點）

你的選擇本質上是：

- **精確搜尋**：結果最準，但通常慢；資料量小/離線評估可用
- **ANN（近似最近鄰）**：資料量大需要速度；需調參與基準測試

上線前至少要做的 3 件事：

- **固定 embedding 維度**：同一個索引不要混不同維度
- **記錄 embedding model 版本**：避免「換模型後答案漂移卻找不到原因」
- **基準測試**：在真實 filters（tenant/ACL）下測 P50/P95 latency 與 recall 變化

## 遷移/版本化：避免上線後「無法回補」

推薦思路：

- 任何可重算的東西都要能重算（chunk、embedding、索引）
- 每一筆 chunk/embedding 都要帶版本（至少 ingest_version、embedding_model_version）
- 文件更新最好走「新版本並行建索引 → 切換 active 版本」避免線上抖動

## Django 整合要點（主線）

- 向量欄位與相似度查詢建議用 raw SQL（或選用支援 pgvector 的 ORM/套件）
- ingest/indexing 一律走背景任務（Celery/RQ/cron），不要卡在 request thread
- Query API 回傳最好包含：
  - 命中的 chunk 引用（source_uri/title_path/page）
  - 召回數量與耗時（方便觀測與 debug）
  - 使用的資料/模型版本（方便重現）

## 本章小結

- pgvector 是「先用 DB 也能做」的務實落地點，但要清楚它的查詢形狀與限制。
- schema 必須為可回放與治理服務：來源、版本、ACL、title_path 等欄位不能省。
- 先用真實 workload 壓測，再決定是否需要專用向量庫或分離服務。

## 延伸閱讀

- [02-向量索引與相似度（cosine-dot-L2）](../03-檢索基礎（向量化-索引-混合檢索）/02-向量索引與相似度（cosine-dot-L2）.md)
- [04-效能與成本：快取-批次-串流-降延遲](04-效能與成本：快取-批次-串流-降延遲.md)
