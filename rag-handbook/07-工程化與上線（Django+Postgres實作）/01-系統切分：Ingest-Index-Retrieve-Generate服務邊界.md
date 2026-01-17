# 01-系統切分：Ingest / Index / Retrieve / Generate 服務邊界

## 你將學到（Learning Objectives）

- 能把 RAG 系統切成清楚的責任邊界（可部署、可擴展、可觀測）
- 能在 Django 既有架構中選擇合適切分（單體 vs 分離服務）
- 知道哪些「一定要在檢索層做」：權限、版本、審計、觀測

## 本章地圖

- **適合用在**：要決定單體/分離服務/三段式切分，並定責任邊界時。
- **你會做出**：服務邊界、資料流與可擴展的部署/維運策略。
- **最可能踩雷**：把 ingest 放在線上；把權限只留在產品層。

## 為什麼要切邊界

RAG 常見的上線問題不是「跑不起來」，而是：

- ingest/indexing 跟線上 API 互相拖慢
- 沒有版本化 → 你不知道答案為什麼今天跟昨天不同
- 權限沒有下沉到檢索層 → 出現跨部門/跨租戶的資料外洩
- 沒有可回放的觀測資料 → 無法 debug，也無法迭代變準

切邊界的目的：**把不可控的部分隔離**，把可控的部分（資料/檢索/提示）變成可迭代工件。

## 四段式主流程（建議）

### 1) Ingest（資料攝取）

責任：
- 拉取資料（檔案、wiki、DB、API）
- 清理、去重、標準化（encoding、噪聲、模板文字）
- 產生文件版本（doc_version）與 ingest 批次（ingest_version）

輸出：
- 原文（或標準化後文本）
- 文件層 metadata（doc_id、source_uri、owner、tenant、ACL、version）

### 2) Index（索引建立）

責任：
- Chunking（保留結構：title_path、section、page）
- Embedding（記錄 embedding_model_version）
- 寫入向量庫（pgvector 或其他）
- 建索引/回補/重算（能重跑是關鍵）

輸出：
- chunks + embeddings（可查、可 filter、可引用）

### 3) Retrieve（檢索）

責任：
- query 理解（可選：rewrite/expand）
- 多路召回（向量/全文/規則）
- metadata filter（tenant/ACL/doc_type/version）
- rerank（強烈建議）
- 輸出「可引用」的 evidence set（候選 chunks）

輸出：
- 候選 evidence：chunk_text + 引用資訊 + 分數 + 版本

### 4) Generate（生成）

責任：
- context packing（避免超 token、避免重複、保留多樣性）
- prompt 模板（含不可回答/追問）
- 輸出格式（文字、JSON、引用清單）
- 風險控管：提示注入、越權內容、幻覺處理

輸出：
- 答案 + 引用（必要）+ 可觀測資料（耗時、token、模型）

## Django 中的切分選項（落地建議）

### 選項 A：單體 Django + 背景任務（最快落地）

結構：
- Web API（查詢/問答）在 Django
- Ingest/Index 放 Celery/RQ/cron（同 repo）
- pgvector 在同一個 Postgres

你需要把「重任務」隔離出 request path：
- 轉檔/OCR、embedding、批次 upsert 都必須在 worker

### 選項 B：Django（產品）+ RAG Service（推薦可上線主流）

結構：
- Django：身份/權限/業務 API、審計、UI
- RAG service：檢索/重排/context/生成（透過 LLM adapter 不綁供應商）

資料與權限的關鍵：
- Django 要把 tenant_id、user_id、role/ACL（或可判斷 ACL 的 token）傳給 RAG service
- RAG service 以 metadata filter 保證「只查得到該看的 chunks」

### 選項 C：Ingest/Index 獨立工作流 + Query service

適合文件量大/更新頻繁：
- ingest/index pipeline 可用工作流系統（或分離 worker）獨立擴展
- query service 專注低延遲與穩定性

## 上線必備的「邊界契約」

不管你選 A/B/C，都建議先定義以下契約（避免後期打掉重練）：

- **資料契約**：chunk 必備欄位（doc_id、source_uri、title_path、acl、version…）
- **檢索契約**：輸入（query + auth context）→ 輸出（evidence + scores + trace_id）
- **生成契約**：輸入（question + evidence）→ 輸出（answer + citations + refusal_reason）
- **觀測契約**：每次請求至少記錄 query、top-k、引用、耗時、版本、trace_id

## 本章小結

- 切分的核心是風險隔離：重任務（ingest/index）不要卡住線上 query。
- 把可替換介面做在服務邊界上：LLM/Embedding/Rerank 可替換、版本可回放。
- 先選能上線的最小切分，再用流量/更新頻率決定是否拆成三段式。

## 延伸閱讀

- [03-Django整合：API設計-背景任務-快取-速率限制](03-Django整合：API設計-背景任務-快取-速率限制.md)
- [03-可觀測性：log-trace-命中率-失敗分類](../06-評估與觀測（讓工程團隊能迭代）/03-可觀測性：log-trace-命中率-失敗分類.md)
