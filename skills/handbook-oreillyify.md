# Skill：手冊一致性整理（oreillyify）

## 目標

用自動化方式把章節結構「對齊同一套骨架」，降低整本手冊的風格漂移成本：

- 統一 `## 你將學到（Learning Objectives）` 標題
- 自動補齊缺少的 `## 本章地圖`（僅對已在映射表定義的章節）
- 自動補齊 `## 本章小結` 與 `## 延伸閱讀`

## 依據

- 腳本：`rag-handbook/scripts/oreillyify.py`
- 寫作規範：`rag-handbook/STYLEGUIDE.md`

## 這個腳本會處理/不處理哪些檔案

### 會處理

- `rag-handbook/` 內的 `*.md`（遞迴）

### 不會處理（跳過）

腳本會排除：

- `rag-handbook/examples/`
- `rag-handbook/assets/`
- `rag-handbook/templates/`
- `rag-handbook/scripts/`

（理由：避免動到範例專案、靜態資產、模板、腳本本身。）

## 如何執行

在 repo 根目錄執行：

```bash
python rag-handbook/scripts/oreillyify.py
```

你會看到：

- `Updated N markdown files.`
- 接著列出被更新的相對路徑

## 「本章地圖/小結/延伸閱讀」從哪來

`oreillyify.py` 內有一個映射表 `EXTRAS`，用「檔案相對路徑」對應到：

- **map_lines**：`## 本章地圖` 內容
- **summary_lines**：`## 本章小結` 內容
- **further_reads**：`## 延伸閱讀` 的連結（用相對路徑自動生成）

若某章 **不在 `EXTRAS`**：

- 仍會補齊 `## 本章小結`、`## 延伸閱讀`，但會放「請補上」的 placeholder（不會替你發明內容）

## 什麼時候該更新 `EXTRAS`

- 新增章節且希望 `本章地圖/小結/延伸閱讀` 有「可用的預設內容」
- 調整章節定位後，想同步更新該章的導讀/小結/串章閱讀路徑

更新方式：在 `rag-handbook/scripts/oreillyify.py` 的 `EXTRAS` 新增或修改對應項目（key 為 `rag-handbook/` 內的相對路徑）。

## 提交前檢查

- **不要**把 placeholder 留在正式內容中（例如「（本章請補上...）」）
- 確認 `延伸閱讀` 的連結都可點通（相對路徑正確）
- 大改動後建議跑一次 `mkdocs build --strict`（見 `skills/mkdocs-preview-build-deploy.md`）

