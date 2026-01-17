# 03-Django 整合：API 設計 / 背景任務 / 快取 / 速率限制

## 你將學到（Learning Objectives）

- 能在 Django 中設計「可觀測、可控、可擴展」的 RAG API
- 知道哪些事情必須移到背景任務（indexing、回補、轉檔）
- 能做到供應商不綁定：LLM/Embedding/Rerank 皆可替換

## 本章地圖

- **適合用在**：要把 RAG 做成可上線 API：可觀測、可控、可擴展。
- **你會做出**：/query /ingest /traces 的最小 API、背景任務與快取/限流策略。
- **最可能踩雷**：重任務走 request path；cache key 忘了 tenant/version；無降級策略。

## API 設計建議（最小但可上線）

建議至少三個面向：

### 1) Query（線上問答）

- `POST /rag/query`
- 輸入：question、（可選）conversation_id、filters（doc_type/time）
- 系統輸入（由 Django 注入，不由前端提供）：tenant_id、user_id、roles/ACL
- 輸出：answer、citations（引用清單）、debug（可選，內部用）

### 2) Ingest（資料導入/同步）

- `POST /rag/ingest`（通常是內部管理或 webhook）
- 只負責「登記」與「排程」，不要在 request 內做重任務

### 3) Admin/Observability（可觀測與回放）

- `GET /rag/traces/{trace_id}`
- 能回放：query、候選 chunks、引用 chunks、模型/版本、耗時與錯誤

## 背景任務：哪些必須移出去

一定要在 worker 跑：

- PDF 轉文字 / OCR / 表格抽取
- Chunking（可能要讀取大檔案、做正規化）
- Embedding（外部 API 可能慢、也可能限流）
- 向量 upsert 與重建索引

建議工作流：

- ingest 任務：拉資料 → 清理 → 產生 chunks（可重跑）
- index 任務：chunks → embedding → upsert → 產出版本狀態（READY）

## 供應商不綁定：最小抽象介面（概念）

你至少要抽象三個 Adapter：

- **LLMAdapter**：generate（可串流）
- **EmbeddingAdapter**：embed_texts（批次）
- **RerankAdapter（選配）**：rerank(query, candidates)

建議把它們視為「可替換依賴」，以設定檔選擇實作（OpenAI/Azure/本地/vLLM/Ollama…都能換）。

下面是一個「最小但夠用」的介面草案（你可以直接照這個在專案內實作）：

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol


@dataclass(frozen=True)
class EmbeddingResult:
    vectors: list[list[float]]
    model: str
    dim: int


class EmbeddingAdapter(Protocol):
    def embed_texts(self, texts: list[str]) -> EmbeddingResult: ...


@dataclass(frozen=True)
class LLMResult:
    text: str
    model: str


class LLMAdapter(Protocol):
    def generate(self, prompt: str) -> LLMResult: ...
    # 若要串流：再加 stream_generate() -> Iterable[str]


@dataclass(frozen=True)
class RerankItem:
    id: str
    text: str
    score: float | None = None


class RerankAdapter(Protocol):
    def rerank(self, query: str, items: list[RerankItem]) -> list[RerankItem]: ...
```

## 快取策略（先做對，再做大）

### 1) Query 結果快取（選擇性）

適合：
- FAQ 類問題、低變動知識、可接受短時間一致性

注意：
- 需要把「權限/tenant」納入 cache key（避免越權）

### 2) 檢索快取（更常用）

- cache key =（normalized query + filters + tenant + active_version）
- cache value = top-k chunks（或 chunk ids）

優點：
- 生成仍可用不同 prompt/模型，但檢索成本先省下來

### 3) Embedding 快取（強烈建議）

- 對重複 query 產生 embedding（若採用 query embedding）很有用

## 速率限制與保護（上線必備）

- **rate limit**：以 user_id / tenant_id 限制（避免濫用與成本失控）
- **timeout**：retrieval、rerank、LLM 各自 timeout，避免整體卡死
- **降級策略**：
  - rerank 失敗 → 直接用向量排序
  - LLM 失敗 → 回傳「證據不足/服務忙碌」並提供引用片段（可選）
- **輸出安全**：禁止把 system prompt、金鑰、內部 debug 外洩到前端

## 權限放哪裡（最常踩雷）

正確：**在檢索查詢就做 filter**（tenant/ACL/doc_scope），讓「拿不到」而不是「拿到再丟掉」。

錯誤：只在 Django view 判斷權限，但向量查詢沒 filter，後面再把結果過濾掉。

## 本章小結

- API 最小面向是 query/ingest/observability，並把 tenant/user/roles 由後端注入。
- ingest/indexing 必須在背景任務跑；線上只做穩定、低延遲、可回放的查詢與生成。
- 快取/限流/timeout/降級是上線必備，且必須以權限/版本維度設計 cache key。

## 延伸閱讀

- [05-安全合規：PII-權限-審計-提示注入防護](05-安全合規：PII-權限-審計-提示注入防護.md)
- [03-可觀測性：log-trace-命中率-失敗分類](../06-評估與觀測（讓工程團隊能迭代）/03-可觀測性：log-trace-命中率-失敗分類.md)
