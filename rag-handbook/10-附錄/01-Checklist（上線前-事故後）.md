# 01-Checklist（上線前 / 事故後）

## 上線前（Pre-launch）

- **資料**
  - 有 owner、來源、更新頻率、權限模型
  - 清理/去重規則可重跑，且有版本（cleaner_version）
  - chunk 必備欄位齊全（doc_id/source_uri/title_path/acl/version）
- **安全**
  - tenant/ACL filter 在檢索層導入（DB 查詢內）
  - 有提示注入基本防線（把證據當資料、強制引用）
  - 有 PII/敏感等級策略（至少能避免明顯外洩）
- **品質**
  - 有離線評估集（>=50 題）與基線指標
  - 有失敗分類（retrieval miss/noisy/generation）
  - 有不可回答/追問策略（不是硬答）
- **工程**
  - indexing 一律背景任務（不在 request path）
  - timeout / rate limit / 降級策略有設計
  - trace_id 回放能力（能看到 top-k、引用、版本、耗時）
- **可維運**
  - SLO/SLA 與告警（錯誤率、P95、成本）
  - 版本切換流程（並行建索引 → 切換 active → 回歸）

## 事故後（Post-incident）

- 這次屬於哪一類失敗：
  - 越權/資料外洩
  - retrieval miss/noisy
  - 生成幻覺
  - timeout/降級失效
- 從 trace 回放是否能重現？缺什麼 log？
- 是資料問題、切分問題、檢索參數問題、還是 prompt 問題？
- 修復後是否加入：
  - 回歸測試題（避免再發生）
  - 監控/告警（更早發現）

## 本章小結

- 上線前要從資料、安全、品質、工程、可維運五面向驗收，而不是只看 demo。
- 事故後要先分類（越權/檢索/生成/超時）並用 trace 重現，再決定修資料、修檢索或修 prompt。
- 每次事故都要回補回歸題與監控告警，讓團隊越跑越穩。

## 延伸閱讀

- [03-可觀測性：log-trace-命中率-失敗分類](../06-評估與觀測（讓工程團隊能迭代）/03-可觀測性：log-trace-命中率-失敗分類.md)
- [06-版本化與可重現：資料-索引-embedding-prompt版本](../07-工程化與上線（Django+Postgres實作）/06-版本化與可重現：資料-索引-embedding-prompt版本.md)
