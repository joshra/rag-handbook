# RAG 手冊（靜態網站版）

本 repo 以 **MkDocs + Material for MkDocs** 將 `rag-handbook/` 的 Markdown 手冊轉成可部署到 **GitHub Pages** 的靜態網站。

## 本機預覽

1) 建立環境並安裝依賴：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) 啟動本機伺服器：

```bash
mkdocs serve
```

3) 瀏覽 `http://127.0.0.1:8000/`

## 建置靜態檔

```bash
mkdocs build --strict
```

輸出會在 `site/`（已加入 `.gitignore`，不需要 commit）。

## 部署到 GitHub Pages

本 repo 已內建 GitHub Actions workflow：`.github/workflows/deploy-mkdocs.yml`。

你需要在 GitHub repo 設定：

- **Settings → Pages → Build and deployment**
  - **Source**：選 **GitHub Actions**

之後 push 到 `main` 或 `master` 分支，就會自動建置並部署。

