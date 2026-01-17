from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]  # rag-handbook/


@dataclass(frozen=True)
class ChapterExtras:
    map_lines: list[str]
    summary_lines: list[str]
    further_reads: list[str]  # paths (within rag-handbook/) to link to


def rel_link(from_file: Path, to_file: Path) -> str:
    rel = os.path.relpath(to_file, start=from_file.parent).replace("\\", "/")
    return rel


def link_line(from_file: Path, to_rel_path: str) -> str:
    to_file = (ROOT / to_rel_path).resolve()
    text = Path(to_rel_path).name.replace(".md", "")
    return f"- [{text}]({rel_link(from_file, to_file)})"


EXTRAS: dict[str, ChapterExtras] = {
    "README.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：工程團隊要把 RAG 從 0 做到可上線（不綁定特定 LLM 供應商）。",
            "- **你會做出**：一套可維運的 ingest/index/query 流程與評估迭代循環。",
            "- **最可能踩雷**：只做向量庫、不做資料/權限/觀測/版本化，最後「跑得動但不可用」。",
        ],
        summary_lines=[
            "- 本手冊的主線是「資料工程 → 檢索 → 生成可靠性 → 評估觀測 → 工程化上線」。",
            "- 以 Django + PostgreSQL + pgvector 作為可直接導入的起點，並明確標出可替換介面（LLM/Embedding/Rerank）。",
            "- 每章以可交付工件與責任邊界為核心，方便做 code review 與上線驗收。",
        ],
        further_reads=[
            "00-導讀/00-手冊使用方式.md",
            "00-導讀/01-名詞表與縮寫.md",
            "01-總覽（從0到上線的RAG藍圖）/02-端到端資料流與系統架構.md",
            "11-附錄/01-Checklist（上線前-事故後）.md",
        ],
    ),
    "00-導讀/00-手冊使用方式.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：第一次帶團隊導入 RAG，需要共同語言與交付標準。",
            "- **你會做出**：一致的閱讀路徑與「最小可交付」驗收清單。",
            "- **最可能踩雷**：把 RAG 當成純模型問題，忽略資料/權限/觀測/版本化。",
        ],
        summary_lines=[
            "- 先建立共同語言（名詞表）與成功標準（KPI/可交付工件），再進入實作細節。",
            "- 索引與重任務一律走背景任務；線上 query 以延遲與可回放為優先。",
            "- 全程保持供應商不綁定：介面抽象優先於框架語法。",
        ],
        further_reads=[
            "00-導讀/01-名詞表與縮寫.md",
            "01-總覽（從0到上線的RAG藍圖）/03-成功標準與KPI（正確率-覆蓋率-成本-延遲）.md",
            "07-工程化與上線（Django+Postgres實作）/03-Django整合：API設計-背景任務-快取-速率限制.md",
            "11-附錄/01-Checklist（上線前-事故後）.md",
        ],
    ),
    "00-導讀/01-名詞表與縮寫.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：團隊討論設計與排查問題時，避免同名異義。",
            "- **你會做出**：一份可被引用的詞彙標準與常見誤解清單。",
            "- **最可能踩雷**：把「RAG/檢索/向量庫」混為一談，導致方案討論失焦。",
        ],
        summary_lines=[
            "- 名詞一致性是協作速度的倍增器：同一個詞只代表一件事。",
            "- RAG 的準確度主要由資料清理、切分、metadata、檢索策略與引用規則共同決定。",
            "- 混合檢索與 rerank 是上線穩定度的常見分水嶺。",
        ],
        further_reads=[
            "03-檢索基礎（向量化-索引-混合檢索）/03-混合檢索（BM25+向量）與何時要用.md",
            "04-檢索策略（把找回來的內容變準）/03-Rerank（二階段檢索）與常見模型.md",
            "05-生成策略（把答案變可靠）/01-Context組裝（packing）與引用格式.md",
        ],
    ),
    "00-導讀/02-主流工具版圖（LangChain-LlamaIndex-Haystack）.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：要選框架或評估是否需要框架時，用組件視角對準需求。",
            "- **你會做出**：框架無關的模組拆分與「可替換介面」思維。",
            "- **最可能踩雷**：先被框架抽象綁住，導致除錯與上線治理困難。",
        ],
        summary_lines=[
            "- 不論框架，RAG 都可拆成 loader/cleaner/chunker/embedder/store/retriever/rerank/answerer。",
            "- 框架的價值在「組裝效率」與「生態整合」，代價是抽象成本與除錯複雜度。",
            "- 先用清楚的 Python 介面與可觀測資料流導入，再決定要不要引入框架加速。",
        ],
        further_reads=[
            "07-工程化與上線（Django+Postgres實作）/01-系統切分：Ingest-Index-Retrieve-Generate服務邊界.md",
            "07-工程化與上線（Django+Postgres實作）/03-Django整合：API設計-背景任務-快取-速率限制.md",
        ],
    ),
    "01-總覽（從0到上線的RAG藍圖）/01-RAG是什麼與適用場景.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：要判斷是不是該用 RAG、用在哪些問題類型時。",
            "- **你會做出**：場景判斷準則與最小可行的系統邊界。",
            "- **最可能踩雷**：把「需要推理/需要外部事實」混在一起，導致誤用 RAG。",
        ],
        summary_lines=[
            "- RAG 適合「答案依賴可追溯資料」且資料會變動的問題，而非純常識或純推理。",
            "- 成功的關鍵不是向量庫，而是資料工程、權限與可回放的治理能力。",
            "- 先把不可回答與澄清策略納入設計，避免上線後硬答造成風險。",
        ],
        further_reads=[
            "01-總覽（從0到上線的RAG藍圖）/03-成功標準與KPI（正確率-覆蓋率-成本-延遲）.md",
            "05-生成策略（把答案變可靠）/02-Prompt模板（可回答-不可回答-追問澄清）.md",
            "11-附錄/02-FAQ（常見誤解與坑）.md",
        ],
    ),
    "01-總覽（從0到上線的RAG藍圖）/02-端到端資料流與系統架構.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：要把 RAG 拆成工程模組、定責任邊界與資料流時。",
            "- **你會做出**：端到端流程圖、可替換介面、最小上線責任清單。",
            "- **最可能踩雷**：權限/觀測/版本化放錯層，導致越權或不可回放。",
        ],
        summary_lines=[
            "- 端到端主線是：資料 → 切分 → 向量化 → 儲存 → 檢索 → 組裝 → 生成 → 回應（含引用）。",
            "- 供應商不綁定的核心在於抽象 LLM/Embedding/Rerank 介面與版本化管理。",
            "- 上線必備的責任邊界：檢索層權限、全流程可觀測、最小版本化與失敗處理。",
        ],
        further_reads=[
            "02-資料工程（最容易踩雷的地方）/03-Metadata與權限欄位設計（ACL-租戶隔離）.md",
            "06-評估與觀測（讓工程團隊能迭代）/03-可觀測性：log-trace-命中率-失敗分類.md",
            "07-工程化與上線（Django+Postgres實作）/01-系統切分：Ingest-Index-Retrieve-Generate服務邊界.md",
        ],
    ),
    "01-總覽（從0到上線的RAG藍圖）/03-成功標準與KPI（正確率-覆蓋率-成本-延遲）.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：要用 KPI 定義 RAG 是否成功，並把討論從感覺拉回數據時。",
            "- **你會做出**：離線/線上指標與成本/延遲的控制目標。",
            "- **最可能踩雷**：只看回答好不好，不看 retrieval 命中與失敗分類。",
        ],
        summary_lines=[
            "- 先把成功拆成 Retrieval 與 Answer 兩段衡量，才能知道問題出在哪一段。",
            "- KPI 必須同時納入：正確率、覆蓋率、成本與延遲（以及越權/合規風險）。",
            "- 沒有失敗分類的指標只能「看起來在量測」，無法支撐迭代。",
        ],
        further_reads=[
            "06-評估與觀測（讓工程團隊能迭代）/01-離線評估：Retrieval-Answer指標與資料集.md",
            "06-評估與觀測（讓工程團隊能迭代）/03-可觀測性：log-trace-命中率-失敗分類.md",
            "07-工程化與上線（Django+Postgres實作）/04-效能與成本：快取-批次-串流-降延遲.md",
        ],
    ),
    "02-資料工程（最容易踩雷的地方）/01-資料盤點與清理（格式-去重-版本）.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：要把文件變成可索引資料，並確保可重跑與可追溯時。",
            "- **你會做出**：資料盤點表、清理規則、版本策略與最小品質門檻。",
            "- **最可能踩雷**：清理不可重跑、來源不可追溯、資料版本混在一起。",
        ],
        summary_lines=[
            "- 資料工程的首要目標是「可重跑、可追溯、可回補」，不是一次性匯入。",
            "- 去重與版本化會直接影響命中率與成本；沒有版本就沒有可靠的回歸測試。",
            "- 先定義資料 owner、權限與更新頻率，才能談索引與上線維運。",
        ],
        further_reads=[
            "02-資料工程（最容易踩雷的地方）/02-Chunking切分策略（大小-重疊-結構化文件）.md",
            "07-工程化與上線（Django+Postgres實作）/06-版本化與可重現：資料-索引-embedding-prompt版本.md",
        ],
    ),
    "02-資料工程（最容易踩雷的地方）/02-Chunking切分策略（大小-重疊-結構化文件）.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：命中率不穩、引用不可信、成本暴增時，先從切分下手。",
            "- **你會做出**：中文文件的切分規則、必備欄位與可引用的 chunk 格式。",
            "- **最可能踩雷**：切太小缺語境、切太大雜訊爆炸、chunk 無來源/無 ACL。",
        ],
        summary_lines=[
            "- Chunking 是 RAG 的上限：切分決定你「能檢索到什麼」，後面再強也救不了。",
            "- 中文文件起手式可用 200–500 字 + 30–80 字 overlap，再依條款/說明文調整。",
            "- chunk 必備欄位要能支援引用與權限：doc_id/source_uri/title_path/acl/version。",
            "- 表格與條列要保留結構（表頭、清單標題），否則檢索命中也會答錯。",
        ],
        further_reads=[
            "02-資料工程（最容易踩雷的地方）/03-Metadata與權限欄位設計（ACL-租戶隔離）.md",
            "05-生成策略（把答案變可靠）/01-Context組裝（packing）與引用格式.md",
        ],
    ),
    "02-資料工程（最容易踩雷的地方）/03-Metadata與權限欄位設計（ACL-租戶隔離）.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：要把權限/租戶隔離下沉到檢索層，避免越權外洩時。",
            "- **你會做出**：metadata schema（含 ACL/tenant/version）與 filter 策略。",
            "- **最可能踩雷**：把權限當後處理；cache key 沒把 tenant/version 納入。",
        ],
        summary_lines=[
            "- metadata 的目的不是「補充資訊」，而是讓檢索可控：filter、排序、回放都靠它。",
            "- 權限/租戶隔離必須在檢索查詢內導入，做到「拿不到」而非「拿到再丟掉」。",
            "- 版本欄位是回歸測試與事故回放的核心；沒有版本就沒有可重現性。",
        ],
        further_reads=[
            "04-檢索策略（把找回來的內容變準）/02-top-k-filter-MMR-多路召回.md",
            "07-工程化與上線（Django+Postgres實作）/05-安全合規：PII-權限-審計-提示注入防護.md",
            "06-評估與觀測（讓工程團隊能迭代）/03-可觀測性：log-trace-命中率-失敗分類.md",
        ],
    ),
    "03-檢索基礎（向量化-索引-混合檢索）/01-Embedding選型與中文語料注意事項.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：要選 embedding 模型、或中文語料檢索效果不穩時。",
            "- **你會做出**：embedding 選型準則、批次/限流策略與版本欄位。",
            "- **最可能踩雷**：只換模型不修資料；embedding 版本混用導致回歸失真。",
        ],
        summary_lines=[
            "- embedding 選型要跟語料與 query 分佈對準；中文常見問題在斷詞、專有名詞與符號。",
            "- 一定要把 embedding 的 model/dim/version 寫進資料，否則無法回放與回歸。",
            "- 批次化與快取通常比「換更大模型」更能穩定成本與延遲。",
        ],
        further_reads=[
            "02-資料工程（最容易踩雷的地方）/02-Chunking切分策略（大小-重疊-結構化文件）.md",
            "07-工程化與上線（Django+Postgres實作）/06-版本化與可重現：資料-索引-embedding-prompt版本.md",
        ],
    ),
    "03-檢索基礎（向量化-索引-混合檢索）/02-向量索引與相似度（cosine-dot-L2）.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：要理解相似度/索引型別，或查詢很慢、命中怪怪時。",
            "- **你會做出**：相似度選擇與索引策略（含 pgvector 導入注意事項）。",
            "- **最可能踩雷**：度量與正規化搞錯、索引未命中、top-k 設太大。",
        ],
        summary_lines=[
            "- cosine/dot/L2 的差異會影響排序；要跟 embedding 模型的輸出特性一起看。",
            "- 索引不是萬靈丹：資料分佈、filter、k 值與查詢形狀會決定是否用得上索引。",
            "- 先用小規模壓測驗證延遲與 recall，再決定要不要升級專用向量庫。",
        ],
        further_reads=[
            "07-工程化與上線（Django+Postgres實作）/02-PostgreSQL+pgvector導入（schema-索引-查詢樣式）.md",
            "04-檢索策略（把找回來的內容變準）/02-top-k-filter-MMR-多路召回.md",
        ],
    ),
    "03-檢索基礎（向量化-索引-混合檢索）/03-混合檢索（BM25+向量）與何時要用.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：有大量精確術語/型號/條款編號，純向量容易漏時。",
            "- **你會做出**：向量 + FTS/BM25 的多路召回與合併去重流程。",
            "- **最可能踩雷**：只做 hybrid 不做 rerank；兩路結果合併沒去重/沒權限 filter。",
        ],
        summary_lines=[
            "- 混合檢索的核心是「不漏」：關鍵字擅長精確命中，向量擅長語意相近。",
            "- 合併召回後要去重並保留來源/分數，才能做可解釋的 rerank 與回放。",
            "- 上線通常以 hybrid + rerank 更穩，尤其在規格/條款/代碼語料。",
        ],
        further_reads=[
            "04-檢索策略（把找回來的內容變準）/03-Rerank（二階段檢索）與常見模型.md",
            "07-工程化與上線（Django+Postgres實作）/02-PostgreSQL+pgvector導入（schema-索引-查詢樣式）.md",
        ],
    ),
    "04-檢索策略（把找回來的內容變準）/01-Query改寫-擴展（rewrite-expand）.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：使用者問題太短/太口語，導致檢索 miss 或召回太雜時。",
            "- **你會做出**：query 正規化、改寫與擴展策略（含安全邊界）。",
            "- **最可能踩雷**：改寫引入幻覺或越權；改寫結果不納入 trace 回放。",
        ],
        summary_lines=[
            "- rewrite/expand 的目標是把「人話」轉成「可檢索的 query」，並控制其風險。",
            "- 改寫必須可觀測：原 query、改寫後 query、使用的版本與耗時都要能回放。",
            "- 安全邊界優先：改寫不能引入不存在的實體或擴大權限範圍。",
        ],
        further_reads=[
            "04-檢索策略（把找回來的內容變準）/02-top-k-filter-MMR-多路召回.md",
            "05-生成策略（把答案變可靠）/03-降低幻覺的防線（guardrails-證據不足處理）.md",
            "06-評估與觀測（讓工程團隊能迭代）/03-可觀測性：log-trace-命中率-失敗分類.md",
        ],
    ),
    "04-檢索策略（把找回來的內容變準）/02-top-k-filter-MMR-多路召回.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：要把線上檢索調到「不漏且不亂」，並能控制成本/延遲時。",
            "- **你會做出**：top-k 起手式、filters 分類、MMR 與多路召回流程。",
            "- **最可能踩雷**：filters 不當成硬規則；k 值過大導致 rerank/LLM 成本爆炸。",
        ],
        summary_lines=[
            "- top-k 是 recall 與成本/延遲的交易：先用起手式，再用離線集與 trace 調參。",
            "- filters 分成安全（必套用）與產品（可選）；安全 filter 必須在查詢內導入。",
            "- 多路召回先求不漏，再靠 rerank 求變準；合併去重是穩定性的關鍵細節。",
        ],
        further_reads=[
            "04-檢索策略（把找回來的內容變準）/03-Rerank（二階段檢索）與常見模型.md",
            "02-資料工程（最容易踩雷的地方）/03-Metadata與權限欄位設計（ACL-租戶隔離）.md",
        ],
    ),
    "04-檢索策略（把找回來的內容變準）/03-Rerank（二階段檢索）與常見模型.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：候選召回很雜、命中率不穩、需要把「相關性」做上去時。",
            "- **你會做出**：二階段檢索流程、rerank 候選數與延遲控制策略。",
            "- **最可能踩雷**：候選集合品質太差；rerank 超時導致整體 SLA 崩潰。",
        ],
        summary_lines=[
            "- rerank 是把「不漏」變成「變準」的常見關鍵，尤其在 hybrid/多路召回後。",
            "- rerank 的主要風險是延遲與成本：候選數、batch、timeout 與降級必須先設好。",
            "- rerank 也要可回放：候選集合、分數、最終選取與版本都要進 trace。",
        ],
        further_reads=[
            "04-檢索策略（把找回來的內容變準）/02-top-k-filter-MMR-多路召回.md",
            "06-評估與觀測（讓工程團隊能迭代）/01-離線評估：Retrieval-Answer指標與資料集.md",
        ],
    ),
    "05-生成策略（把答案變可靠）/01-Context組裝（packing）與引用格式.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：答案引用不穩、context 太長太亂、LLM 常抓錯重點時。",
            "- **你會做出**：context packing 流程與可審計的引用格式。",
            "- **最可能踩雷**：塞越多越好；引用格式不固定導致回放困難與假引用。",
        ],
        summary_lines=[
            "- context packing 的目標是「足夠但不冗餘」：去重、多樣性控制、截斷與固定格式。",
            "- 引用格式要同時滿足人讀與機器回放：citation id + 可追溯來源 + chunk 內容。",
            "- 在 prompt 內強制：每個結論要引用、證據不足要拒答/追問、禁止假引用。",
        ],
        further_reads=[
            "05-生成策略（把答案變可靠）/02-Prompt模板（可回答-不可回答-追問澄清）.md",
            "06-評估與觀測（讓工程團隊能迭代）/03-可觀測性：log-trace-命中率-失敗分類.md",
        ],
    ),
    "05-生成策略（把答案變可靠）/02-Prompt模板（可回答-不可回答-追問澄清）.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：要把輸出格式、拒答策略與追問策略制度化時。",
            "- **你會做出**：可回答/不可回答/追問澄清的 prompt 套件與輸出規範。",
            "- **最可能踩雷**：不定義拒答條件；輸出格式不固定導致前端/下游難解析。",
        ],
        summary_lines=[
            "- prompt 的目標不是「更像人」，而是可控：可解析格式、引用規則與拒答策略。",
            "- 把不可回答變成產品能力：明確說缺什麼證據、提出可行澄清問題。",
            "- prompt 版本要可追溯，並納入回歸測試與事故回放。",
        ],
        further_reads=[
            "05-生成策略（把答案變可靠）/01-Context組裝（packing）與引用格式.md",
            "07-工程化與上線（Django+Postgres實作）/06-版本化與可重現：資料-索引-embedding-prompt版本.md",
        ],
    ),
    "05-生成策略（把答案變可靠）/03-降低幻覺的防線（guardrails-證據不足處理）.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：上線後最怕的兩件事：硬答幻覺、越權外洩。",
            "- **你會做出**：證據不足處理、引用強制、提示注入基本防護。",
            "- **最可能踩雷**：只靠 prompt 口頭約束；沒有 trace 回放導致無法定位問題。",
        ],
        summary_lines=[
            "- 降低幻覺要多層防線：檢索品質、context packing、引用強制、拒答/追問、輸出驗證。",
            "- 證據不足要明確拒答或追問，不能用語氣把不確定包裝成肯定。",
            "- 提示注入要用「把證據當資料」的方式處理，並把權限與 system prompt 隔離。",
        ],
        further_reads=[
            "02-資料工程（最容易踩雷的地方）/03-Metadata與權限欄位設計（ACL-租戶隔離）.md",
            "06-評估與觀測（讓工程團隊能迭代）/03-可觀測性：log-trace-命中率-失敗分類.md",
            "07-工程化與上線（Django+Postgres實作）/05-安全合規：PII-權限-審計-提示注入防護.md",
        ],
    ),
    "06-評估與觀測（讓工程團隊能迭代）/01-離線評估：Retrieval-Answer指標與資料集.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：要建立可迭代的基線、做回歸測試與比較不同策略時。",
            "- **你會做出**：離線題庫、Retrieval/Answer 指標與失敗分類標籤。",
            "- **最可能踩雷**：只做主觀評語；沒有資料版本/提示版本，導致結果不可重現。",
        ],
        summary_lines=[
            "- 離線評估的核心是可重現：固定題庫、固定版本、固定指標與可回放資料。",
            "- 指標要拆段：先量 retrieval（命中/排序），再量 answer（正確/引用/可用性）。",
            "- 把失敗分類做成流程，才能讓改動（chunking/檢索/prompt）變成可控迭代。",
        ],
        further_reads=[
            "01-總覽（從0到上線的RAG藍圖）/03-成功標準與KPI（正確率-覆蓋率-成本-延遲）.md",
            "07-工程化與上線（Django+Postgres實作）/06-版本化與可重現：資料-索引-embedding-prompt版本.md",
        ],
    ),
    "06-評估與觀測（讓工程團隊能迭代）/02-線上評估：A-B-回饋循環-人工標註流程.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：要把線上流量變成可用回饋，支援 A/B 與人工標註時。",
            "- **你會做出**：回饋收集、抽樣標註、A/B 與回歸題庫回補流程。",
            "- **最可能踩雷**：只收「讚/倒讚」不收理由；不記版本導致無法歸因。",
        ],
        summary_lines=[
            "- 線上評估的關鍵是歸因：每次回答都要能對到資料/索引/模型/prompt 版本。",
            "- 回饋循環要可執行：收集 → 抽樣 → 標註 → 失敗分類 → 回補題庫 → 回歸。",
            "- A/B 要先定義守門指標（越權/錯誤率/P95/成本），再談提升準確率。",
        ],
        further_reads=[
            "06-評估與觀測（讓工程團隊能迭代）/03-可觀測性：log-trace-命中率-失敗分類.md",
            "11-附錄/01-Checklist（上線前-事故後）.md",
        ],
    ),
    "06-評估與觀測（讓工程團隊能迭代）/03-可觀測性：log-trace-命中率-失敗分類.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：上線後要能除錯、回放、歸因與持續迭代時。",
            "- **你會做出**：trace schema、命中率/耗時/成本指標與失敗分類儀表板。",
            "- **最可能踩雷**：只記答案不記候選 chunks；沒有版本欄位導致不可重現。",
        ],
        summary_lines=[
            "- 可觀測性要覆蓋整條鏈：query → 候選 → rerank → context → 生成 → 引用 → 回應。",
            "- 每次問答都應能回放：取了哪些 chunk、分數如何、為何被引用、耗時在哪。",
            "- 失敗分類是把 log 變成迭代能力的關鍵：retrieval miss/noisy、generation、越權、超時等。",
        ],
        further_reads=[
            "07-工程化與上線（Django+Postgres實作）/03-Django整合：API設計-背景任務-快取-速率限制.md",
            "07-工程化與上線（Django+Postgres實作）/06-版本化與可重現：資料-索引-embedding-prompt版本.md",
        ],
    ),
    "07-工程化與上線（Django+Postgres實作）/01-系統切分：Ingest-Index-Retrieve-Generate服務邊界.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：要決定單體/分離服務/三段式切分，並定責任邊界時。",
            "- **你會做出**：服務邊界、資料流與可擴展的部署/維運策略。",
            "- **最可能踩雷**：把 ingest 放在線上；把權限只留在產品層。",
        ],
        summary_lines=[
            "- 切分的核心是風險隔離：重任務（ingest/index）不要卡住線上 query。",
            "- 把可替換介面做在服務邊界上：LLM/Embedding/Rerank 可替換、版本可回放。",
            "- 先選能上線的最小切分，再用流量/更新頻率決定是否拆成三段式。",
        ],
        further_reads=[
            "07-工程化與上線（Django+Postgres實作）/03-Django整合：API設計-背景任務-快取-速率限制.md",
            "06-評估與觀測（讓工程團隊能迭代）/03-可觀測性：log-trace-命中率-失敗分類.md",
        ],
    ),
    "07-工程化與上線（Django+Postgres實作）/02-PostgreSQL+pgvector導入（schema-索引-查詢樣式）.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：要用 Postgres 先導入向量檢索，並確保查詢形狀可控時。",
            "- **你會做出**：schema、索引、查詢樣式與效能/限制的工程準則。",
            "- **最可能踩雷**：索引沒用上、filter 破壞索引、k 值/維度導致效能爆炸。",
        ],
        summary_lines=[
            "- pgvector 是「先用 DB 也能做」的務實起點，但要清楚它的查詢形狀與限制。",
            "- schema 必須為可回放與治理服務：來源、版本、ACL、title_path 等欄位不能省。",
            "- 先用真實 workload 壓測，再決定是否需要專用向量庫或分離服務。",
        ],
        further_reads=[
            "03-檢索基礎（向量化-索引-混合檢索）/02-向量索引與相似度（cosine-dot-L2）.md",
            "07-工程化與上線（Django+Postgres實作）/04-效能與成本：快取-批次-串流-降延遲.md",
        ],
    ),
    "07-工程化與上線（Django+Postgres實作）/03-Django整合：API設計-背景任務-快取-速率限制.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：要把 RAG 做成可上線 API：可觀測、可控、可擴展。",
            "- **你會做出**：/query /ingest /traces 的最小 API、背景任務與快取/限流策略。",
            "- **最可能踩雷**：重任務走 request path；cache key 忘了 tenant/version；無降級策略。",
        ],
        summary_lines=[
            "- API 最小面向是 query/ingest/observability，並把 tenant/user/roles 由後端注入。",
            "- ingest/indexing 必須在背景任務跑；線上只做穩定、低延遲、可回放的查詢與生成。",
            "- 快取/限流/timeout/降級是上線必備，且必須以權限/版本維度設計 cache key。",
        ],
        further_reads=[
            "07-工程化與上線（Django+Postgres實作）/05-安全合規：PII-權限-審計-提示注入防護.md",
            "06-評估與觀測（讓工程團隊能迭代）/03-可觀測性：log-trace-命中率-失敗分類.md",
        ],
    ),
    "07-工程化與上線（Django+Postgres實作）/04-效能與成本：快取-批次-串流-降延遲.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：P95 延遲或成本過高，需要優先把系統做穩時。",
            "- **你會做出**：快取層級、批次策略、串流與降級的上線配方。",
            "- **最可能踩雷**：只優化 LLM；忽略檢索/embedding/外部依賴的尾延遲。",
        ],
        summary_lines=[
            "- 先把耗時拆段量測（retrieval/rerank/LLM），再決定快取與降級放在哪。",
            "- 檢索快取與 embedding 快取通常是最划算的優化；query 結果快取要小心權限與一致性。",
            "- timeout、降級與串流要一起設計：穩定性比平均延遲更重要。",
        ],
        further_reads=[
            "07-工程化與上線（Django+Postgres實作）/03-Django整合：API設計-背景任務-快取-速率限制.md",
            "04-檢索策略（把找回來的內容變準）/03-Rerank（二階段檢索）與常見模型.md",
        ],
    ),
    "07-工程化與上線（Django+Postgres實作）/05-安全合規：PII-權限-審計-提示注入防護.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：多租戶/敏感資料場景，要把越權與提示注入風險降到可控時。",
            "- **你會做出**：ACL/租戶隔離、審計回放、PII 策略與提示注入防護清單。",
            "- **最可能踩雷**：只在 UI 做權限；把內部 prompt/debug 外洩到前端。",
        ],
        summary_lines=[
            "- 安全的核心是「檢索層硬隔離 + 全流程可審計」：拿不到就不會外洩。",
            "- PII 與敏感等級要制度化：資料側標記、檢索側 filter、輸出側護欄。",
            "- 提示注入要用工程手段處理：資料/指令分離、引用強制、輸出檢查與降級。",
        ],
        further_reads=[
            "02-資料工程（最容易踩雷的地方）/03-Metadata與權限欄位設計（ACL-租戶隔離）.md",
            "05-生成策略（把答案變可靠）/03-降低幻覺的防線（guardrails-證據不足處理）.md",
        ],
    ),
    "07-工程化與上線（Django+Postgres實作）/06-版本化與可重現：資料-索引-embedding-prompt版本.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：要做回歸測試、事故回放與安全切換版本（藍綠/雙跑）時。",
            "- **你會做出**：資料/索引/embedding/prompt 的版本欄位與切換流程。",
            "- **最可能踩雷**：版本散落在多處不可追溯；線上回答無法對應到版本。",
        ],
        summary_lines=[
            "- 版本化的目標是可重現：同一題在同一版本應得到同等級的可解釋結果。",
            "- 最小版本集合：資料版本、chunking/cleaner 版本、embedding 版本、索引版本、prompt 版本。",
            "- 上線切換要可控：並行建索引 → 回歸 → 切換 active → 觀測 → 回收舊版。",
        ],
        further_reads=[
            "06-評估與觀測（讓工程團隊能迭代）/01-離線評估：Retrieval-Answer指標與資料集.md",
            "06-評估與觀測（讓工程團隊能迭代）/03-可觀測性：log-trace-命中率-失敗分類.md",
        ],
    ),
    "08-進階主題（了解主流走向）/01-Agentic RAG（工具使用與工作流）.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：需要多步推理、工具使用與可控工作流的問答任務。",
            "- **你會做出**：Agentic RAG 的風險/收益判斷與最小工作流設計原則。",
            "- **最可能踩雷**：把 agent 當成魔法；缺乏權限/審計/成本控制。",
        ],
        summary_lines=[
            "- Agentic RAG 的價值在於多步工作流與工具使用，但治理成本顯著上升。",
            "- 先用可觀測的 pipeline（retrieval→generate）打底，再逐步引入工具與狀態。",
            "- 每一步都要納入權限、trace 與成本護欄，否則很難上線。",
        ],
        further_reads=[
            "06-評估與觀測（讓工程團隊能迭代）/03-可觀測性：log-trace-命中率-失敗分類.md",
            "07-工程化與上線（Django+Postgres實作）/05-安全合規：PII-權限-審計-提示注入防護.md",
        ],
    ),
    "08-進階主題（了解主流走向）/02-多模態RAG（圖片-表格）.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：知識主要在圖片/掃描件/表格，純文字抽取會丟失關鍵資訊時。",
            "- **你會做出**：多模態資料 ingest 與索引策略的選型框架。",
            "- **最可能踩雷**：只做 OCR 不保留版面/表格結構；引用無法回到原圖位置。",
        ],
        summary_lines=[
            "- 多模態的關鍵是保留結構與可追溯位置：頁碼、框選區域、表格 header。",
            "- 先選擇「抽成結構化文本」還是「以視覺特徵檢索」的路線，再談模型。",
            "- 引用與審計要能指到原圖/原表的位置，否則上線難以除錯與合規。",
        ],
        further_reads=[
            "02-資料工程（最容易踩雷的地方）/02-Chunking切分策略（大小-重疊-結構化文件）.md",
            "05-生成策略（把答案變可靠）/01-Context組裝（packing）與引用格式.md",
        ],
    ),
    "08-進階主題（了解主流走向）/03-Graph RAG與知識圖譜（何時值得）.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：問題需要跨文件關聯、實體關係或多跳查詢時。",
            "- **你會做出**：何時值得建圖譜、以及與向量檢索的組合策略。",
            "- **最可能踩雷**：為了酷而上圖譜；資料治理與更新成本被低估。",
        ],
        summary_lines=[
            "- Graph RAG 的價值在關聯推理與可解釋的關係路徑，但建置與維護成本高。",
            "- 先用 metadata/結構化欄位解掉 80% 關聯需求，再評估是否上圖譜。",
            "- 圖譜與向量常是互補：圖譜提供關聯範圍，向量提供語意匹配。",
        ],
        further_reads=[
            "02-資料工程（最容易踩雷的地方）/03-Metadata與權限欄位設計（ACL-租戶隔離）.md",
            "03-檢索基礎（向量化-索引-混合檢索）/03-混合檢索（BM25+向量）與何時要用.md",
        ],
    ),
    "09-導入既有場景（工程團隊導入配方）/01-導入路線圖（PoC→試點→正式）.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：要規劃導入節奏，避免 PoC 永遠卡在 PoC 時。",
            "- **你會做出**：PoC→試點→正式的交付物、風險與驗收節點。",
            "- **最可能踩雷**：只追求 demo；忽略資料權限與觀測，試點就爆炸。",
        ],
        summary_lines=[
            "- PoC 的目標是驗證價值與可行性；試點的目標是驗證可維運；正式才談規模化。",
            "- 每一階段都要交付可回放與版本化能力，否則你無法自信地迭代。",
            "- 把風險（越權/成本/延遲/品質）當成里程碑守門條件，而不是事後補洞。",
        ],
        further_reads=[
            "11-附錄/01-Checklist（上線前-事故後）.md",
            "06-評估與觀測（讓工程團隊能迭代）/02-線上評估：A-B-回饋循環-人工標註流程.md",
        ],
    ),
    "09-導入既有場景（工程團隊導入配方）/02-文件型知識庫配方（企業內規-手冊-規格）.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：企業內規/手冊/規格等「文件型知識」要導入 RAG 時。",
            "- **你會做出**：文件 ingest、切分、引用與權限的導入配方。",
            "- **最可能踩雷**：文件版本與例外條款被切斷；引用回不到條款位置。",
        ],
        summary_lines=[
            "- 文件型知識的重點在結構：標題路徑、條款編號、頁碼與例外條件要被保留。",
            "- 混合檢索與 rerank 往往更穩，因為文件常有精確術語與編號需求。",
            "- 引用是產品能力：能回到條款位置，才能支撐審計與使用者信任。",
        ],
        further_reads=[
            "02-資料工程（最容易踩雷的地方）/02-Chunking切分策略（大小-重疊-結構化文件）.md",
            "05-生成策略（把答案變可靠）/01-Context組裝（packing）與引用格式.md",
        ],
    ),
    "09-導入既有場景（工程團隊導入配方）/03-研發型知識庫配方（issues-PRD-設計文-ADR）.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：issues/PRD/設計文/ADR 這類研發知識要檢索與引用時。",
            "- **你會做出**：以版本與連結關係為核心的索引與檢索策略。",
            "- **最可能踩雷**：缺乏去重與版本策略；把過期方案與現行方案混在一起。",
        ],
        summary_lines=[
            "- 研發型知識的關鍵是版本與關聯：狀態（open/closed）、時間、repo/PR/issue 連結要進 metadata。",
            "- 查詢通常需要混合檢索（關鍵字/代碼/ID）＋向量（語意）；rerank 是常見必要品。",
            "- 引用要能回到原始 issue/PR/ADR，並在答案中標示「是否已過期」。",
        ],
        further_reads=[
            "03-檢索基礎（向量化-索引-混合檢索）/03-混合檢索（BM25+向量）與何時要用.md",
            "02-資料工程（最容易踩雷的地方）/03-Metadata與權限欄位設計（ACL-租戶隔離）.md",
        ],
    ),
    "11-附錄/01-Checklist（上線前-事故後）.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：上線驗收與事故復盤，快速補齊治理缺口。",
            "- **你會做出**：一份可直接拿來做 release gate 的檢查清單。",
            "- **最可能踩雷**：把 checklist 當形式；沒有 trace/版本化就無法真正驗收。",
        ],
        summary_lines=[
            "- 上線前要從資料、安全、品質、工程、可維運五面向驗收，而不是只看 demo。",
            "- 事故後要先分類（越權/檢索/生成/超時）並用 trace 重現，再決定修資料、修檢索或修 prompt。",
            "- 每次事故都要回補回歸題與監控告警，讓團隊越跑越穩。",
        ],
        further_reads=[
            "06-評估與觀測（讓工程團隊能迭代）/03-可觀測性：log-trace-命中率-失敗分類.md",
            "07-工程化與上線（Django+Postgres實作）/06-版本化與可重現：資料-索引-embedding-prompt版本.md",
        ],
    ),
    "11-附錄/02-FAQ（常見誤解與坑）.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：團隊討論卡關時，快速對準常見誤解與真實工程成本。",
            "- **你會做出**：一份「先別做錯」的防踩雷清單。",
            "- **最可能踩雷**：把 RAG 當成向量庫專案；忽略權限與可回放。",
        ],
        summary_lines=[
            "- 多數 RAG 失敗不是模型不夠大，而是資料、切分、metadata、權限與觀測沒有做到位。",
            "- 先做出可回放與可版本化，才有資格談優化與規模化。",
            "- 若不能拒答與追問，系統會以硬答方式把不確定變成事故。",
        ],
        further_reads=[
            "00-導讀/01-名詞表與縮寫.md",
            "11-附錄/01-Checklist（上線前-事故後）.md",
        ],
    ),
    "11-附錄/03-參考文獻與延伸閱讀.md": ChapterExtras(
        map_lines=[
            "- **適合用在**：需要進一步深入官方文件、或安排團隊讀書會路徑時。",
            "- **你會做出**：一份可持續擴充的閱讀清單與討論題目。",
            "- **最可能踩雷**：只堆連結不給閱讀順序；團隊看完仍無法導入。",
        ],
        summary_lines=[
            "- 延伸閱讀以「可直接導入」為優先：官方文件、關鍵章節串讀、讀書會題目。",
            "- 建議以本手冊的主線順序閱讀：先地基（資料/切分/權限），再做準（檢索/重排），最後做穩（觀測/版本/上線）。",
            "- 團隊討論題目應能對應到你們的 query 分佈、資料更新與權限模型。",
        ],
        further_reads=[
            "07-工程化與上線（Django+Postgres實作）/02-PostgreSQL+pgvector導入（schema-索引-查詢樣式）.md",
            "03-檢索基礎（向量化-索引-混合檢索）/03-混合檢索（BM25+向量）與何時要用.md",
        ],
    ),
}


def should_process(path: Path) -> bool:
    if path.suffix.lower() != ".md":
        return False
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("examples/"):
        return False
    if rel.startswith("assets/"):
        return False
    if rel.startswith("templates/"):
        return False
    if rel.startswith("scripts/"):
        return False
    return True


def ensure_section(text: str, heading: str, body: str) -> str:
    if heading in text:
        return text
    # ensure a blank line before appending
    if not text.endswith("\n"):
        text += "\n"
    if not text.endswith("\n\n"):
        text += "\n"
    return text + f"{heading}\n\n{body}\n"


def normalize_objectives_heading(text: str) -> str:
    return text.replace("## 學習目標", "## 你將學到（Learning Objectives）", 1)


def insert_after_objectives(text: str, insert_block: str) -> str:
    marker = "## 你將學到（Learning Objectives）"
    idx = text.find(marker)
    if idx == -1:
        return text
    # find end of that section (next '## ')
    after = text.find("\n## ", idx + len(marker))
    if after == -1:
        after = len(text)
    if "## 本章地圖" in text:
        return text
    # Insert before the next section
    prefix = text[:after].rstrip() + "\n\n"
    suffix = text[after:].lstrip("\n")
    return prefix + insert_block.rstrip() + "\n\n" + suffix


def oreillyify_file(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    extras = EXTRAS.get(rel)

    raw = path.read_text(encoding="utf-8")
    text = raw

    text = normalize_objectives_heading(text)

    if extras and "## 本章地圖" not in text:
        map_block = "## 本章地圖\n\n" + "\n".join(extras.map_lines)
        text = insert_after_objectives(text, map_block)

    if extras:
        summary_body = "\n".join(extras.summary_lines)
        text = ensure_section(text, "## 本章小結", summary_body)
        reads_body = "\n".join(link_line(path, p) for p in extras.further_reads)
        text = ensure_section(text, "## 延伸閱讀", reads_body)
    else:
        # For any unmatched file, still make structure consistent without inventing content.
        text = ensure_section(text, "## 本章小結", "- （本章請補上 5–9 點可操作結論。）")
        text = ensure_section(text, "## 延伸閱讀", "- （本章請補上 3–7 項閱讀連結：本手冊章節＋官方文件。）")

    if text != raw:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed: list[str] = []
    for p in ROOT.rglob("*.md"):
        if not should_process(p):
            continue
        if oreillyify_file(p):
            changed.append(p.relative_to(ROOT).as_posix())

    print(f"Updated {len(changed)} markdown files.")
    if changed:
        for x in changed:
            print(f"- {x}")


if __name__ == "__main__":
    main()

