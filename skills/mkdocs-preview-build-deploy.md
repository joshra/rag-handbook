# Skill：MkDocs 預覽／嚴格建置／GitHub Pages 部署

## 目標

把 `rag-handbook/` 的 Markdown 轉成可預覽、可嚴格檢查、可自動部署的靜態網站。

## 依據（本 repo 的設定）

- MkDocs 設定：`mkdocs.yml`
  - `docs_dir: rag-handbook`
  - `site_dir: site`
  - `exclude_docs`：排除 `examples/`、`scripts/`、`templates/`
- 依賴：`requirements.txt`
- 本機操作：根目錄 `README.md`
- CI/CD：`.github/workflows/deploy-mkdocs.yml`

## 本機預覽（開發時）

在 repo 根目錄：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

預設瀏覽：`http://127.0.0.1:8000/`

## 嚴格建置（提交前）

```bash
mkdocs build --strict
```

輸出目錄為 `site/`（此 repo 設定為不需要 commit）。

## 部署到 GitHub Pages（Repo 設定一次即可）

此 repo 已內建 GitHub Actions workflow：`.github/workflows/deploy-mkdocs.yml`，觸發條件：

- push 到 `main` 或 `master`
- 或手動觸發（workflow_dispatch）

你需要在 GitHub repo 設定：

- **Settings → Pages → Build and deployment**
  - **Source**：選 **GitHub Actions**

## 常見坑

- **本機可跑、CI 失敗**：多半是 `mkdocs build --strict` 抓到連結/語法問題；以 strict 當作 release gate
- **檔案放錯位置**：MkDocs 的 `docs_dir` 是 `rag-handbook/`，放在 repo 根目錄的文件不會出現在網站（例如本資料夾 `skills/`）
- **想在網站顯示 skills**：要嘛把 skill 文件放進 `rag-handbook/`，要嘛調整 `docs_dir` 與導覽策略（建議先不要混在一起）

