# 01-離線評估：Retrieval / Answer 指標與資料集

## 你將學到（Learning Objectives）

- 能建立最小離線評估集（不用很大，但要代表性）
- 能分開評估 retrieval 與 generation（避免混在一起看不出問題）
- 能把離線評估變成回歸測試（版本切換前必跑）

## 本章地圖

- **適合用在**：要建立可迭代的基線、做回歸測試與比較不同策略時。
- **你會做出**：離線題庫、Retrieval/Answer 指標與失敗分類標籤。
- **最可能踩雷**：只做主觀評語；沒有資料版本/提示版本，導致結果不可重現。

## 最小離線資料集怎麼做

起手式（建議 50～200 題）：

- 從真實工單/客服/內部提問蒐集
- 每題包含：
  - question（原始問題）
  - expected evidence（應該命中的文件/章節/條款）
  - expected answer（可選，但很有用）
  - filters（tenant/doc_type 等）

## Retrieval 指標（先看有沒有把證據找回來）

- **Recall@k**：正確證據是否出現在 top-k
- **MRR**：正確證據排名是否靠前（越靠前越好）
- **nDCG（可選）**：若你有多個相關證據分級

## Generation 指標（再看答案是否依據證據）

- **Correctness**：答案是否正確（人工標註最可靠；LLM-as-judge 可輔助）
- **Groundedness/Faithfulness**：答案是否可被引用證據支持
- **Citation accuracy**：引用是否指向正確 chunk
- **Refusal accuracy**：該拒答時是否拒答

## 評估的關鍵：失敗分類

離線評估一定要輸出：

- retrieval miss（證據沒找回）
- retrieval noisy（找回但太雜）
- generation error（證據有但答錯/亂總結）

這會直接指向你應該改哪一層。

## 本章小結

- 離線評估的核心是可重現：固定題庫、固定版本、固定指標與可回放資料。
- 指標要拆段：先量 retrieval（命中/排序），再量 answer（正確/引用/可用性）。
- 把失敗分類做成流程，才能讓改動（chunking/檢索/prompt）變成可控迭代。

## 延伸閱讀

- [03-成功標準與KPI（正確率-覆蓋率-成本-延遲）](../01-總覽（從0到上線的RAG藍圖）/03-成功標準與KPI（正確率-覆蓋率-成本-延遲）.md)
- [06-版本化與可重現：資料-索引-embedding-prompt版本](../07-工程化與上線（Django+Postgres實作）/06-版本化與可重現：資料-索引-embedding-prompt版本.md)
