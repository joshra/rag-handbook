# 03-Metadata 與權限欄位設計（ACL / 租戶隔離）

## 你將學到（Learning Objectives）

- 知道 metadata 不是附加資訊，而是「讓 RAG 可上線」的核心
- 能設計最小 metadata schema：引用、權限、版本、文件分類
- 能把權限下沉到檢索層（避免越權檢索）

## 本章地圖

- **適合用在**：要把權限/租戶隔離下沉到檢索層，避免越權外洩時。
- **你會做出**：metadata schema（含 ACL/tenant/version）與 filter 策略。
- **最可能踩雷**：把權限當後處理；cache key 沒把 tenant/version 納入。

## metadata 決定三件事

- **你能不能安全上線**：tenant/ACL filter
- **你能不能 debug**：trace 能回溯到 doc/章節/頁碼
- **你能不能迭代**：版本化與資料治理

## 最小必備欄位（chunk 級）

- **tenant_id**：多租戶隔離（即使你目前單租戶，也建議先放）
- **acl**：可見性（角色、部門、群組、使用者 id 清單或規則）
- **doc_id / doc_version**：原文件識別與版本
- **source_uri**：引用來源（URL/檔名/路徑）
- **title_path / section / page**：人類可讀引用定位
- **doc_type**：政策/流程/規格/FAQ…（可用於 filters 與評估分層）
- **ingest_version / chunker_version / embedding_model_version**：可重現

## ACL 設計（實務上最重要）

### 不要做的事

- 只在應用層判斷權限，DB 查詢不帶 filter
- 先檢索出一堆 chunks，再在 Python 裡過濾（風險高、且浪費成本）

### 建議做法（起手式）

- 每個 chunk 都帶 tenant_id
- ACL 用「可由 DB filter 的形式」表示，例如：
  - role-based（role in [...]）
  - department-based（dept_id）
  - group-based（group_id）
  - doc-level visibility（public/internal/confidential）

如果你的 ACL 很複雜：
- 先以「文件級 ACL」起步（chunk 繼承 doc ACL）
- 需要更細再做 chunk 級 ACL（但工程成本上升）

## filters 的設計（讓你們工程團隊好用）

建議把 filters 分成兩種：

- **安全 filter（必定套用）**：tenant/ACL/機密等級
- **產品 filter（可選）**：doc_type、日期範圍、資料版本、資料來源

並在 trace 記錄「實際套用過哪些 filter」。

## 本章小結

- metadata 的目的不是「補充資訊」，而是讓檢索可控：filter、排序、回放都靠它。
- 權限/租戶隔離必須在檢索查詢內落地，做到「拿不到」而非「拿到再丟掉」。
- 版本欄位是回歸測試與事故回放的核心；沒有版本就沒有可重現性。

## 延伸閱讀

- [02-top-k-filter-MMR-多路召回](../04-檢索策略（把找回來的內容變準）/02-top-k-filter-MMR-多路召回.md)
- [05-安全合規：PII-權限-審計-提示注入防護](../07-工程化與上線（Django+Postgres實作）/05-安全合規：PII-權限-審計-提示注入防護.md)
- [03-可觀測性：log-trace-命中率-失敗分類](../06-評估與觀測（讓工程團隊能迭代）/03-可觀測性：log-trace-命中率-失敗分類.md)
