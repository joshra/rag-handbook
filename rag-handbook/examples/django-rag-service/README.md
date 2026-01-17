# django-rag-service（最小骨架）

> 目的：提供一個「**不綁定 LLM 供應商**」的 Django + PostgreSQL（pgvector）最小導入骨架，方便你把手冊概念帶回既有系統。

## 這個骨架包含什麼

- Postgres + pgvector 的 `docker-compose.yml`
- `scripts/initdb.sql`：啟用 pgvector extension（可自行擴充 schema）
- Django 專案結構（最小可擴展）：RAG API、Adapter 介面、背景任務位置（先留 stub）

## 啟動資料庫（pgvector）

在此目錄執行：

```bash
docker compose up -d
```

接著確認 DB 內已啟用 extension：

```sql
SELECT extname FROM pg_extension;
```

應該能看到 `vector`。

## 下一步（你可以怎麼用）

- 先把你們最常用的一小批中文文件（50～200 篇）導入 chunks
- 用 `pgvector` 做 top-k 檢索 + tenant/ACL filter
- 再把 LLM adapter 接到你們可用的供應商（OpenAI/Azure/本地皆可）

