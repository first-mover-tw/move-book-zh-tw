# Progress

## 2026-02-10: 翻譯系統重構

### 完成
- 重寫 `scripts/translate_to_zh_tw.py`
  - 新增 `--batch-size`、`--sleep`、`--diff-base` 參數
  - 增量偵測（git diff）+ 批次限制
  - client 只建立一次，翻譯間 sleep 避免 rate limit
  - 失敗檔案列出並 exit 1
- 重寫 `.github/workflows/translate-zh-tw.yml`
  - 增量：`git diff origin/zh-tw-main...HEAD` 找變動 .md
  - 每次最多翻 5 個檔案
  - 每日 02:00 UTC 排程 + push english-main 觸發
  - 用 `/tmp/changed_files.txt` 傳檔案列表（避免 injection）

## 2026-02-10: 移除 `.zh-TW.md` 後綴，改用 manifest 追蹤

### 完成
- 重寫 `scripts/translate_to_zh_tw.py`
  - 翻譯結果直接覆蓋原檔（不加 `.zh-TW` 後綴）
  - 新增 `scripts/translation-manifest.json`，記錄每個檔案對應的英文 blob hash
  - 新增 `--detect` mode：比對 english-main blob hash vs manifest，輸出需翻譯檔案
  - 新增 `--english-ref` 參數（預設 `english-main`）
  - 移除舊的 `get_changed_md_files` / `get_all_untranslated`（基於 diff / counterpart 的邏輯）
- 重寫 `.github/workflows/translate-zh-tw.yml`
  - Checkout `zh-tw-main` → fetch `english-main` → `--detect` 找差異
  - Checkout english 原檔 → 翻譯覆蓋 → commit `.md` + manifest
- 12 個 `.zh-TW.md` 檔 rename 為同名 `.md`（覆蓋英文版）
- 建立初始 manifest（12 筆已翻譯記錄）
- `--detect` 驗證：正確列出 119 個未翻譯檔案

### TODO
- [ ] 本地跑單檔翻譯測試（`python scripts/translate_to_zh_tw.py book/some-file.md`）
- [ ] 本地分批全量翻譯 119 個檔（`--all --batch-size 10`）
- [ ] commit 推到 zh-tw-main
- [ ] workflow_dispatch 手動觸發測試
