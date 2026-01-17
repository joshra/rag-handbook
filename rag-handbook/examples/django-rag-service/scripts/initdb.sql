CREATE EXTENSION IF NOT EXISTS vector;

-- 這裡先放「最小」示意 schema（可依手冊章節自行擴充）
CREATE TABLE IF NOT EXISTS documents (
  id BIGSERIAL PRIMARY KEY,
  doc_id TEXT NOT NULL,
  doc_version TEXT NOT NULL,
  source_uri TEXT,
  title TEXT,
  tenant_id TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, doc_id, doc_version)
);

-- 注意：embedding 維度需要與你選用的 embedding 模型一致。
-- 這裡用 1536 只是示意（常見維度之一），實作時請改成你的實際維度。
CREATE TABLE IF NOT EXISTS chunks (
  id BIGSERIAL PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  doc_id TEXT NOT NULL,
  doc_version TEXT NOT NULL,
  chunk_id TEXT NOT NULL,
  chunk_order INT NOT NULL,
  title_path TEXT,
  chunk_text TEXT NOT NULL,
  source_uri TEXT,
  embedding_model TEXT NOT NULL,
  embedding_dim INT NOT NULL,
  embedding vector(1536),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, doc_id, doc_version, chunk_id)
);

-- 用於租戶/版本的篩選加速（向量索引則依 pgvector 設定另建）
CREATE INDEX IF NOT EXISTS idx_chunks_tenant_docver ON chunks (tenant_id, doc_id, doc_version);

