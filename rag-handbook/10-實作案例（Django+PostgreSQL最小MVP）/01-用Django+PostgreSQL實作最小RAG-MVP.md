# 01-用 Django + PostgreSQL 實作最小 RAG MVP（可回放、可上線起跑）

## 你將學到（Learning Objectives）

- 能把 RAG MVP 壓到「最小但可上線」：**一個 DB、一個 API、一條 ingest 任務**
- 能定義並做出 MVP 必備的 4 個工件：**schema、ingest、query、trace 回放**
- 知道 Django + PostgreSQL（pgvector）在 MVP 階段最常踩雷的點（權限、版本、重任務、可觀測）

## 本章地圖

- **適合用在**：你要在既有 Django 系統內做出第一版可用 RAG，且短期內不想引入外部向量庫與複雜服務切分。
- **你會做出**：一套最小可運作的 ingest/index → retrieve → generate 流程（含引用與回放）。
- **最可能踩雷**：把 embedding / index 重任務放進 request path；ACL 只在應用層後過濾；沒有版本導致「答案漂移但無法歸因」。

## 先講結論（In a Nutshell）

> [!TIP]
> **起手式**：用 Django + PostgreSQL（pgvector）做 MVP 時，把範圍壓到「能回放」：  
> 1) schema 必備 `tenant_id / acl / ingest_version / embedding_model`；2) ingest 一律背景任務；3) query 一律先 filter 再做 top-k；4) 每次回答寫 trace（候選、引用、版本、耗時）。

## MVP 的「最小系統邊界」長相

你在 MVP 階段不需要做成完美的企業搜尋，但你必須跑通「可回放」的端到端：

- **Ingest（背景任務）**：文件 → 清理/切分 → embedding → upsert 到 Postgres
- **Retrieve（線上）**：filter（tenant/ACL/版本）→ top-k（向量或混合檢索）→ 回傳候選 chunks（含引用欄位）
- **Generate（線上）**：context packing → 生成答案（要求引用）→ 產生 trace 以便回放

> [!WARNING]
> **上線風險**：MVP 最常見事故不是「答得不夠漂亮」，而是「越權/外洩」與「不可回放」。你要把權限與版本當成主線，而不是等到附錄才補。

## 配方：最小可上線的資料模型（schema）

你可以直接採用 `07-工程化與上線（Django+Postgres實作）/02-PostgreSQL+pgvector導入（schema-索引-查詢樣式）.md` 的起手式 schema；本章只強調 MVP 不能省的欄位。

### 你不能省的欄位（用來支撐治理與回放）

- **租戶/權限**：`tenant_id`、（最少）`acl_is_public` + `acl_principals`
- **版本**：`ingest_version`、`embedding_model`（必要時加 `embedding_dim`）
- **引用**：`source_uri`、`title_path`、（選配）`page_start/page_end` 或 `section_id`

> [!CAUTION]
> **常見誤解**：先把 chunk/embedding 做出來再補 ACL。等你補上 ACL，你會發現（a）查詢形狀變了（b）索引可能失效（c）快取 key 要全改（d）資料要重建。

## 配方：最小 ingest（用背景任務把資料變成可檢索 chunks）

MVP ingest 的驗收標準不是「吞吐很高」，而是：

- 同一份文件重跑不會產生一堆重複 chunk（可去重/可覆蓋）
- 每筆 chunk 都帶齊：引用 + 權限 + 版本
- 能在 trace 裡定位：這次回答用的是哪個 `ingest_version`

### 建議的最小 ingest 介面（Django 角度）

- **入口**：管理端觸發或 webhook 觸發 `POST /rag/ingest`
- **實作**：view 只做「登記 + 排程」，真正重任務（轉檔、切分、embedding、upsert）丟到 worker

> [!TIP]
> **起手式**：先用「批次匯入固定小資料集」起跑（例如 50～200 篇 SOP/規格/FAQ），等 query 跑通且可回放，再接正式資料源同步。

## 配方：最小 query API（先 filter 再 top-k，再生成）

你可以把線上 query 固定成一個非常可控的流程：

1. **Django 注入系統欄位**：`tenant_id`、`user_id`、`principals/roles`
2. **計算 query embedding**（可快取）
3. **DB 查詢**：`WHERE tenant/ACL/version` → `ORDER BY embedding <=> q` → `LIMIT k`
4. **組裝 context**：把 top-k chunks（含引用欄位）包進 prompt
5. **生成答案**：要求引用、證據不足就拒答或追問
6. **寫 trace**：候選、引用、版本、耗時、成本

### 最小 API 形狀（建議）

- `POST /rag/query`
  - request：`question`、`filters`（doc_type/time 等）
  - response：`answer`、`citations[]`、（內部用）`trace_id`

你可以直接對照本手冊的建議：
- `07-工程化與上線（Django+Postgres實作）/03-Django整合：API設計-背景任務-快取-速率限制.md`

## 配方：最小 trace（沒有回放就不能迭代）

MVP trace 先求「夠用」：每次 query 至少要能回放以下資訊：

- **輸入**：question、filters、tenant、principal/roles
- **檢索**：候選 chunks（含分數與引用欄位）、最後採用的 citations
- **版本**：ingest_version、embedding_model、（若有）prompt_version、llm_model
- **效能/成本**：retrieve_ms、generate_ms、tokens（可選）

> [!TIP]
> **起手式**：trace 可以先存 JSON（例如 `rag_traces.payload jsonb`），等你們開始做線上分析再拆欄位與索引。

## 常見坑（Pitfalls）

- **ACL 只在應用層後過濾**：會有越權風險，也會造成尾延遲暴增（需要多次查詢才湊滿 k）
- **把 embedding / upsert 放進 request path**：一旦遇到限流/慢回應，整個 API 會雪崩
- **沒有版本欄位**：文件更新、embedding 更新、prompt 更新造成答案改變，你卻無法歸因也無法回歸
- **引用欄位缺失**：即使回答正確，也無法建立信任（更無法審計）

## 本章小結

- MVP 的最小單位是「可回放」：schema（含 ACL/版本/引用）＋背景 ingest＋線上 query＋trace。
- Django + Postgres 的優勢是治理與維運：把 filter（tenant/ACL/版本）下沉到 DB 查詢，避免越權與尾延遲。
- 先把端到端跑穩，再談 rerank、多路召回、獨立檢索服務與專用向量庫。

## 延伸閱讀

- [02-PostgreSQL+pgvector導入（schema-索引-查詢樣式）](../07-工程化與上線（Django+Postgres實作）/02-PostgreSQL+pgvector導入（schema-索引-查詢樣式）.md)
- [03-Django整合：API設計-背景任務-快取-速率限制](../07-工程化與上線（Django+Postgres實作）/03-Django整合：API設計-背景任務-快取-速率限制.md)
- [01-Checklist（上線前-事故後）](../11-附錄/01-Checklist（上線前-事故後）.md)

