# 02-PostgreSQL + pgvector 導入（schema / 索引 / 查詢樣式）

## 你將學到（Learning Objectives）

- 了解為什麼「先用 Postgres + pgvector」是常見的可上線起手式
- 知道 schema 需要怎麼設計，才能支援：**權限 filter、版本化、引用回溯**
- 會做出一套可直接採用的：**DDL / 索引 / 查詢樣式（含混合檢索）**
- 知道 pgvector 上線後最常見的效能坑，以及如何用可觀測性把問題抓出來

## 本章地圖

- **適合用在**：要用 Postgres 先導入向量檢索，且查詢形狀可控、ACL 能治理時。
- **你會做出**：可上線的 schema、索引、查詢樣式（含混合檢索）與維運準則。
- **最可能踩雷**：索引沒用上、filter 破壞索引、k 值/維度導致效能爆炸、ACL 只在應用層後過濾。

## 何時選 pgvector（以及何時不該）

### 適合

- 你已經有 PostgreSQL 維運能力（備份、監控、權限）
- 早期流量不大（或可以接受較高延遲），更在意「先上線」
- 需要把 metadata filter（權限/租戶/版本）做得很「資料庫原生」

### 可能不適合

- 需要高吞吐、低延遲且向量量級很大（例如數千萬以上，依硬體而異）
- 需要更成熟的向量能力（更完整分片、向量壓縮、HNSW 調參、向量搜尋專用觀測）
- 你已經確定會強依賴「多叢集水平擴展」與「跨區域」：把檢索抽成服務通常更乾淨

本手冊策略：**先用 pgvector 上線**，需要時再抽換成專用向量庫（介面保持一致）。

## 先把兩個決策做死：相似度與維度

你會在 3 個地方用到這兩個決策：**資料表型別**、**索引 ops class**、**查詢運算子**。

- **相似度**：常見選擇是 cosine / dot product / L2。你在模型選型時就應該固定（參考本手冊「相似度」章）。
- **維度**：同一個索引/欄位不要混不同維度。換 embedding 模型而維度不同，基本上就是一輪「重算 + 重建索引」。

> [!TIP]
> **起手式**：如果你沒把握，先用 cosine（語意檢索最常見），並在表上存 `embedding_model` / `embedding_dim` 以避免混寫。

## 建議的資料模型（概念）

你至少需要三層概念：

- **documents**：原始文件（或文件版本）
- **chunks**：切分後片段（含引用資訊）
- **embeddings**：chunk 對應的向量（含 embedding model 版本）

實務上可以合併（例如 embeddings 直接放在 chunks 表），但分開的好處是版本化與回補更清楚。

## 起手式：一套可上線的 schema（含版本化 / 引用 / 租戶隔離）

下面是一套「先能上線」的最小可用設計：把向量放在 `chunks` 表，並把 **租戶/版本/引用** 做成一等公民。你可以先照抄，之後再依流量與資料量演進（拆表、分區、抽到獨立檢索服務）。

> [!WARNING]
> **上線風險**：不要只在應用層做 ACL 後過濾。你需要把 `tenant_id` 與 ACL 變成 SQL filter 的一部分，否則會出現「先檢索到不該看的 chunk，再在應用層丟掉」的越權風險。

### 0) 必要 extension

```sql
-- pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- 混合檢索：全文檢索 + trgm（可選）
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

### 1) documents：文件與版本

```sql
CREATE TABLE IF NOT EXISTS rag_documents (
  id               bigserial PRIMARY KEY,
  tenant_id        text NOT NULL,

  -- 來源可回溯（例如 Confluence URL、S3 URI、Git path）
  source_uri       text NOT NULL,
  source_etag      text NULL,             -- 上游版本（hash/etag/rev），用來判斷是否需要重建

  title            text NULL,
  doc_type         text NULL,             -- policy/spec/wiki/pdf 等

  -- 版本化：避免線上更新造成抖動，保留多版本並用 is_active 切換
  ingest_version   integer NOT NULL,      -- 每次 ingest 批次遞增
  is_active        boolean NOT NULL DEFAULT true,

  created_at       timestamptz NOT NULL DEFAULT now(),
  updated_at       timestamptz NOT NULL DEFAULT now(),

  UNIQUE (tenant_id, source_uri, ingest_version)
);

CREATE INDEX IF NOT EXISTS rag_documents_tenant_active_idx
  ON rag_documents (tenant_id, is_active, ingest_version DESC);
```

### 2) chunks：引用資訊 + embedding + 權限欄位

下面的設計重點是：

- **引用**：`source_uri/title_path/page/section_id` 讓你能顯示與審計
- **版本**：`ingest_version/embedding_model/embedding_dim` 讓你能重現
- **ACL**：先用最小可用的欄位形狀（可演進）

```sql
-- 你需要把 embedding 維度固定下來；例如 1536 / 3072 / 1024
-- 建議把維度寫成 migration 常數（同一張表不要混不同維度）。
CREATE TABLE IF NOT EXISTS rag_chunks (
  id                      bigserial PRIMARY KEY,
  tenant_id               text NOT NULL,
  document_id             bigint NOT NULL REFERENCES rag_documents(id) ON DELETE CASCADE,

  -- 引用回溯（顯示給使用者/審計用）
  source_uri              text NOT NULL,
  title_path              text NULL,          -- 例如 "第2章/2.1/2.1.3"
  page_start              integer NULL,
  page_end                integer NULL,
  section_id              text NULL,          -- 例如 HTML anchor / heading id

  -- chunk 內容
  chunk_index             integer NOT NULL,   -- 同一文件內的序號
  content                 text NOT NULL,

  -- 用於混合檢索（FTS）：由 trigger 或寫入流程維護
  content_tsv             tsvector NULL,

  -- 權限欄位（起手式：先用 array；資料大或 ACL 複雜再演進成 join table）
  acl_principals          text[] NULL,        -- 允許的使用者/群組/角色 id
  acl_is_public           boolean NOT NULL DEFAULT false,

  -- 版本化
  ingest_version          integer NOT NULL,
  embedding_model         text NOT NULL,      -- 例如 "text-embedding-3-large"
  embedding_dim           integer NOT NULL,   -- 防止誤寫不同維度

  -- 向量
  embedding               vector(1536) NOT NULL,

  created_at              timestamptz NOT NULL DEFAULT now(),

  UNIQUE (tenant_id, document_id, chunk_index, ingest_version, embedding_model)
);

CREATE INDEX IF NOT EXISTS rag_chunks_tenant_doc_idx
  ON rag_chunks (tenant_id, document_id, ingest_version DESC);

CREATE INDEX IF NOT EXISTS rag_chunks_tenant_version_idx
  ON rag_chunks (tenant_id, ingest_version DESC, embedding_model);
```

### 3) 內容全文索引（混合檢索用）

> [!TIP]
> **起手式**：先讓 `content_tsv` 由寫入流程同步維護（最直覺）。等寫入量大了，再改成「批次更新」或「背景任務」。

```sql
UPDATE rag_chunks
SET content_tsv = to_tsvector('simple', coalesce(content, ''))
WHERE content_tsv IS NULL;

CREATE INDEX IF NOT EXISTS rag_chunks_content_tsv_gin
  ON rag_chunks USING GIN (content_tsv);

-- 若你需要「關鍵字包含」的彈性（尤其中文/代碼），可加 trgm
CREATE INDEX IF NOT EXISTS rag_chunks_content_trgm_gin
  ON rag_chunks USING GIN (content gin_trgm_ops);
```

### 4) ACL 演進：從 array 走向 join table（可選）

當你發現以下任一情況，`acl_principals text[]` 通常就不夠用了：

- 需要大量 principal（群組/部門/專案）且更新頻繁
- 需要「deny 規則」或時間有效期
- 需要更好的索引與可觀測性（誰能看哪些 chunk）

此時建議改成 join table：

```sql
CREATE TABLE IF NOT EXISTS rag_chunk_acl (
  chunk_id       bigint NOT NULL REFERENCES rag_chunks(id) ON DELETE CASCADE,
  principal_id   text NOT NULL,
  PRIMARY KEY (chunk_id, principal_id)
);

CREATE INDEX IF NOT EXISTS rag_chunk_acl_principal_idx
  ON rag_chunk_acl (principal_id, chunk_id);
```

## 必備欄位（再次強調）

- **doc_id / source_uri**：可回溯
- **title_path / page / section**：可引用
- **tenant_id / acl**：權限隔離
- **ingest_version / embedding_model_version**：可重現

## 查詢樣式（你應該具備的能力點）

> [!NOTE]
> **運算子**：pgvector 常見距離運算子包含 `<->`（L2）、`<#>`（內積）、`<=>`（cosine distance）。你要先決定「用哪一種相似度」並在 schema/索引/查詢保持一致。

### 1) 基本向量近鄰（取 top-k）

- 輸入：query_vector
- 輸出：最相近的 k 個 chunk（含 doc_id、source_uri、title_path/page）

```sql
-- 以 cosine distance 為例（越小越相近）
SELECT
  c.id,
  c.document_id,
  c.source_uri,
  c.title_path,
  c.page_start,
  c.page_end,
  c.chunk_index,
  c.content,
  (c.embedding <=> $1) AS distance
FROM rag_chunks c
WHERE c.tenant_id = $2
  AND c.ingest_version = $3
  AND c.embedding_model = $4
ORDER BY c.embedding <=> $1
LIMIT $5;
```

> [!TIP]
> **起手式**：`k=8~20` 先起跑；等你導入 rerank，再把候選拉高（例如 40~200）來換召回率。

### 2) metadata filter（租戶/權限/文件類型）

- 查詢必須支援 tenant_id、doc_type、時間範圍、資料版本等條件
- **務必**把權限條件納入 DB 查詢（metadata filter），不要只在應用層做後過濾

```sql
-- 範例：只看 active documents，且 ACL 允許 public 或包含某 principal
SELECT
  c.id,
  c.source_uri,
  c.title_path,
  c.page_start,
  c.page_end,
  c.content,
  (c.embedding <=> $1) AS distance
FROM rag_chunks c
JOIN rag_documents d
  ON d.id = c.document_id
WHERE c.tenant_id = $2
  AND d.tenant_id = $2
  AND d.is_active = true
  AND c.ingest_version = d.ingest_version
  AND c.embedding_model = $3
  AND (c.acl_is_public = true OR $4 = ANY (c.acl_principals))
ORDER BY c.embedding <=> $1
LIMIT $5;
```

> [!CAUTION]
> **常見誤解**：把 ACL 做成「先向量查 top-k → 應用層過濾 → 不夠再查下一頁」。這會造成越權風險與尾延遲飆高（需要多次 round-trip 才湊滿 k）。

### 3) 混合檢索（全文 + 向量）

- 用 Postgres 全文檢索（tsvector）做關鍵字召回（或 ranking）
- 與向量召回合併（多路召回後 merge），再做 rerank（通常效果最好）

以下是一個務實的做法：用兩個子查詢各取一批候選（keyword / vector），做 `UNION` 去重後再排序。你可以先用簡單的線性組合，等有離線評估再調權重。

```sql
WITH
keyword AS (
  SELECT
    c.id,
    ts_rank(c.content_tsv, websearch_to_tsquery('simple', $4)) AS kw_score
  FROM rag_chunks c
  WHERE c.tenant_id = $1
    AND c.ingest_version = $2
    AND c.embedding_model = $3
    AND c.content_tsv @@ websearch_to_tsquery('simple', $4)
  ORDER BY kw_score DESC
  LIMIT $5
),
vector AS (
  SELECT
    c.id,
    1.0::float / (1.0 + (c.embedding <=> $6)) AS vec_score
  FROM rag_chunks c
  WHERE c.tenant_id = $1
    AND c.ingest_version = $2
    AND c.embedding_model = $3
  ORDER BY c.embedding <=> $6
  LIMIT $7
),
merged AS (
  SELECT id, kw_score, 0.0::float AS vec_score FROM keyword
  UNION ALL
  SELECT id, 0.0::float AS kw_score, vec_score FROM vector
),
scored AS (
  SELECT
    id,
    max(kw_score) AS kw_score,
    max(vec_score) AS vec_score,
    (0.4 * max(kw_score) + 0.6 * max(vec_score)) AS score
  FROM merged
  GROUP BY id
)
SELECT
  c.id,
  c.source_uri,
  c.title_path,
  c.page_start,
  c.page_end,
  c.content,
  s.score
FROM scored s
JOIN rag_chunks c ON c.id = s.id
ORDER BY s.score DESC
LIMIT $8;
```

> [!TIP]
> **起手式**：`keyword_limit=50`、`vector_limit=50`、最後 `limit=20`；先跑離線評估，再決定是否要提高候選數來換召回率。

### 4) 兩階段：DB 先召回，應用層 rerank

在 pgvector + Postgres 的導入路線裡，常見的高效果路徑是：

- 第一階段（DB）：用向量/混合檢索召回 **候選 50~200**
- 第二階段（模型）：用 reranker（Cross-Encoder）把候選重排，取 top-k

DB 要做的事很單純：回傳 **可引用的 chunk** 與 **可觀測的距離/分數**，並把版本與 ACL 一併固定。

## 索引選型（你要知道的重點）

你的選擇本質上是：

- **精確搜尋**：結果最準，但通常慢；資料量小/離線評估可用
- **ANN（近似最近鄰）**：資料量大需要速度；需調參與基準測試

上線前至少要做的 3 件事：

- **固定 embedding 維度**：同一個索引不要混不同維度
- **記錄 embedding model 版本**：避免「換模型後答案漂移卻找不到原因」
- **基準測試**：在真實 filters（tenant/ACL）下測 P50/P95 latency 與 recall 變化

## pgvector 索引：你可以怎麼選（與怎麼避免「建了也沒用」）

> [!TIP]
> **起手式**：資料量小（例如 < 50 萬 chunk）先不上 ANN，先把查詢形狀與 ACL/版本做正確；當延遲或成本開始痛，再導入 ANN（IVFFlat 或 HNSW）。

### 1) 先確保查詢「形狀固定」

你要養成兩個習慣：

- 用 `EXPLAIN (ANALYZE, BUFFERS)` 看是否走到你預期的路徑
- 把查詢固定成「可重複的形狀」：同樣的 `WHERE tenant_id / ingest_version / embedding_model`，同樣的 `ORDER BY embedding <=> $q LIMIT k`

### 2) ANN 建索引（示意）

不同版本的 pgvector 支援的索引類型與語法可能不同，但原則一致：

- **IVFFlat**：建索引快、查詢快、需要 `ANALYZE` 且要調 probes
- **HNSW**：通常召回更好、索引更大、寫入/更新成本更高、要調 ef_search

你可以先把它寫在 migration 裡，並用線上旗標控制是否啟用 ANN。

```sql
-- 示意：IVFFlat（lists 值要用你的資料量與壓測決定）
-- CREATE INDEX ... USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- 示意：HNSW（m / ef_construction 依資料量與效能需求調）
-- CREATE INDEX ... USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
```

> [!WARNING]
> **上線風險**：ANN 的效果與延遲會被「filter 選擇性」強烈影響。你如果每次都帶很嚴格的 ACL/tenant filter，可能會讓 ANN 的效益不如預期，甚至退化。這時要考慮（a）資料分區/分表（b）把檢索層抽成獨立服務（c）重新設計 ACL 的資料形狀。

## 遷移/版本化：避免上線後「無法回補」

推薦思路：

- 任何可重算的東西都要能重算（chunk、embedding、索引）
- 每一筆 chunk/embedding 都要帶版本（至少 ingest_version、embedding_model_version）
- 文件更新最好走「新版本並行建索引 → 切換 active 版本」避免線上抖動

> [!CAUTION]
> **常見誤解**：把文件更新做成「原地覆寫 chunks/embedding」。你會失去可重現性，也很難在出事時回溯「是哪個版本的資料/模型導致答案變差」。

## Django 整合要點（主線）

- 向量欄位與相似度查詢建議用 raw SQL（或選用支援 pgvector 的 ORM/套件）
- ingest/indexing 一律走背景任務（Celery/RQ/cron），不要卡在 request thread
- Query API 回傳最好包含：
  - 命中的 chunk 引用（source_uri/title_path/page）
  - 召回數量與耗時（方便觀測與 debug）
  - 使用的資料/模型版本（方便重現）

## 維運與效能：先盯這些就夠（避免「越用越慢」）

- **VACUUM / ANALYZE**：大量寫入後要確保統計資訊更新，否則 planner 會做出很差的決策
- **慢查詢觀測**：至少開 `pg_stat_statements`，把檢索 query 的 P50/P95/P99 拉出來看
- **索引膨脹**：向量索引與 GIN 索引都可能變大；定期檢查 bloat 與重建策略
- **連線池**：RAG 查詢常見「一個請求多次 DB round-trip」，務必使用連線池與 timeouts

## 本章小結

- pgvector 是「先用 DB 也能做」的務實起點，但要清楚它的查詢形狀與限制。
- schema 必須為可回放與治理服務：來源、版本、ACL、title_path 等欄位不能省。
- 上線前先固定：embedding 維度、相似度定義（L2/內積/cosine）、查詢形狀（WHERE + ORDER BY + LIMIT）。
- 任何檢索都必須把 `tenant_id` 與 ACL 變成 SQL filter；不要靠應用層後過濾。
- 混合檢索的務實路徑是「keyword 召回 + vector 召回 → merge → rerank」：先把候選做對，再用模型把排序做強。
- 版本化要用「新版本並行建好 → 切 active」；避免原地覆寫導致不可重現。
- 先用真實 workload 壓測，再決定是否需要專用向量庫或把檢索抽成服務。

## 延伸閱讀

- [02-向量索引與相似度（cosine-dot-L2）](../03-檢索基礎（向量化-索引-混合檢索）/02-向量索引與相似度（cosine-dot-L2）.md)
- [03-混合檢索（BM25+向量）與何時要用](../03-檢索基礎（向量化-索引-混合檢索）/03-混合檢索（BM25+向量）與何時要用.md)
- [03-Django整合：API設計-背景任務-快取-速率限制](03-Django整合：API設計-背景任務-快取-速率限制.md)
- [04-效能與成本：快取-批次-串流-降延遲](04-效能與成本：快取-批次-串流-降延遲.md)
- [pgvector 官方文件](https://github.com/pgvector/pgvector)
- [PostgreSQL 全文檢索（FTS）](https://www.postgresql.org/docs/current/textsearch.html)
- [PostgreSQL Row Level Security（RLS）](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
