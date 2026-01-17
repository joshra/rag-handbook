# 02-主流工具版圖（LangChain / LlamaIndex / Haystack）

> 目標：知道「主流做法長什麼樣」，但不被框架綁死。

## 先講結論：你真正需要的元件

不管用哪個框架，RAG 都可以拆成可替換的模組：

- **Document loader**：從資料源讀入（檔案、DB、Confluence、Notion…）
- **Cleaner/Normalizer**：去噪、標準化、抽取結構
- **Chunker**：切分策略
- **Embedder**：文字 → 向量
- **Vector store**：向量與 metadata 的儲存與查詢（pgvector 也是一種）
- **Retriever**：封裝查詢邏輯（top-k、filters、MMR、hybrid）
- **Reranker**（選配但強烈建議）：「相關性變準」常靠它
- **Answerer（LLM）**：把 context + 問題 → 答案（含引用與不可回答策略）

本手冊會以這些模組做「抽象介面」描述，讓你：

- 先用 **Postgres + pgvector** 走到可上線
- 需要更高吞吐/更強檢索時，再換成 Milvus/Qdrant/Pinecone 等，不必重寫全部

## LangChain：偏「工作流/組裝」的工具箱

- **強項**：把 retriever、LLM、工具調用串起來很快；社群大、整合多
- **常見用法**：LCEL（chain 表達式）、retrieval chain、tool calling
- **風險**：抽象層多，初學容易「跑得動但不知道為什麼」

## LlamaIndex：偏「資料到索引」與「檢索組件」更完整

- **強項**：資料 ingest、索引結構、檢索策略（含多路召回、摘要索引等）概念清楚
- **常見用法**：Index / QueryEngine / Retriever / Node（chunk）模型
- **風險**：同樣有抽象成本；需要清楚你要的索引與評估方式

## Haystack：偏「檢索/搜尋系統」脈絡（企業搜尋風格）

- **強項**：pipeline 很明確，對「檢索評估」更貼近傳統 IR；部署感較重
- **常見用法**：DocumentStore、Retriever、Reader（或 Generator）、Pipeline
- **風險**：某些最新 LLM 生態整合可能不如 LangChain 廣

## 本手冊的採用策略（避免工具綁架）

- **主線**：先用「框架無關」的概念與最小介面，落到 Django + Postgres
- **補充**：在每個章節的最後附「用 LangChain/LlamaIndex/Haystack 怎麼對映」
- **原則**：能用清楚的 Python code 表達的，就不要被框架語法綁住

## 本章小結

- 不論框架，RAG 都可拆成 loader/cleaner/chunker/embedder/store/retriever/rerank/answerer。
- 框架的價值在「組裝效率」與「生態整合」，代價是抽象成本與除錯複雜度。
- 先用清楚的 Python 介面與可觀測資料流落地，再決定要不要引入框架加速。

## 延伸閱讀

- [01-系統切分：Ingest-Index-Retrieve-Generate服務邊界](../07-工程化與上線（Django+Postgres實作）/01-系統切分：Ingest-Index-Retrieve-Generate服務邊界.md)
- [03-Django整合：API設計-背景任務-快取-速率限制](../07-工程化與上線（Django+Postgres實作）/03-Django整合：API設計-背景任務-快取-速率限制.md)
