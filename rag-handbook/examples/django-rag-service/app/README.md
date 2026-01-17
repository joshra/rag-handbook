# app（Django 專案 stub）

這裡先提供「放置位置與責任邊界」的 stub，方便你把既有 Django 專案對應到手冊的模組切分。

建議你在真實專案內至少建立以下模組：

- `rag/adapters/`：LLM / Embedding / Rerank 的抽象介面與實作
- `rag/ingest/`：資料清理、切分、版本化（背景任務）
- `rag/retrieval/`：pgvector 查詢、filters、MMR、多路召回
- `rag/generation/`：prompt、context packing、引用、拒答/追問策略
- `rag/observability/`：trace log、回放資料、失敗分類

後續如果你希望我把這個骨架補成「可直接跑起來的 Django 專案」（含 DRF endpoint、Celery 任務、pgvector 查詢 code），我可以再把 `manage.py`、`settings.py`、`urls.py` 與最小 API 一次補齊。

