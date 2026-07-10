# zh-TW 翻譯管線重建與上游同步

日期：2026-07-10
狀態：設計已確認，待寫實作計畫

## 一、背景

`first-mover-tw/move-book-zh-tw` 是 `MystenLabs/move-book` 的繁體中文翻譯 fork。它**不把上游 merge 進翻譯分支**，而是走兩段式管線：

1. `sync-upstream.yml`：`upstream/main` → `english-main`（純英文鏡像）
2. `translate-zh-tw.yml`：從 `english-main` 取出英文檔，用 Gemini 整檔重譯，開 PR 進 `zh-tw-main`

`scripts/translation-manifest.json` 記錄 `路徑 → 上次翻譯所依據的英文 blob SHA`。過期的定義是 manifest SHA ≠ `english-main` 當前 SHA。

`english-main` 目前已追平上游（落後 0），`zh-tw-main` 有 151 個檔案過期。

> 註：直接 `git merge upstream/main` 進 `zh-tw-main` 會產生 167 個衝突檔，但那是這個 repo 設計上永不執行的操作。衝突數對本設計沒有意義。

## 二、調查發現的缺陷

以下皆為實測結果，非推論。

### D1：CI 翻譯管線從未執行過（已確認 root cause）

`zh-tw-main` 上有 0 個 bot commit。`translate-zh-tw.yml` 自 2026-02 設定 secret 起每日排程執行、每次 9–12 秒、全部回報 success、翻譯 0 個檔案。

原因是步驟順序：第 29 行的 `Detect` 執行 `python scripts/translate_to_zh_tw.py --detect`，但 `Setup Python`（52 行）與 `pip install google-genai`（60 行）排在它**後面**。detect 時 `google-genai` 尚未安裝，`scripts/translate_to_zh_tw.py:10` 的 top-level `from google import genai` 直接 `ModuleNotFoundError`。

而該行是 `CHANGED=$(python ... --detect ... 2>/dev/null || true)` —— `2>/dev/null` 吃掉 traceback，`|| true` 吃掉 exit code。`CHANGED` 成為空字串，`COUNT=0`，其後所有步驟被 `if: count != '0'` 跳過，job 綠燈。

驗證：run 28997766485 的 log 顯示 `Changed files:` 為空、Python 執行約 190ms、`Setup Python` 與 `Install dependencies` 均為 `skipped`。

`sync-upstream.yml` 未受影響，因為它只跑 git 指令、不需要 Python 依賴。

### D2：15 個檔案結構殘缺，其中 13 個嚴重截斷

> 修正（實作階段）：初次調查得出 19，但當時的掃描腳本與 Task 3 初版 `headings()` 共用同一個天真的 fence 切換邏輯 —— 它把 HTML 註解（`<!-- ... -->`）裡的 ``` 與標題也算進去。修正後為 **15**。移除的 4 個假陽性是 `struct.md`、`struct-methods.md`、`string.md`、`2024-migration-guide.md`：英文原檔有被註解掉的區塊，中文正確地沒翻。13 個嚴重截斷檔全數仍在名單內。

比對中文檔與其英文來源（merge-base `f2c0a93e`）的標題層級序列與 code fence 數量，143 個檔案中有 15 個不符。中文行數不到英文 60% 的有 13 個：

| 檔案 | 英文行數 | 中文行數 |
|---|---|---|
| `reference/variables.md` | 824 | 36 |
| `book/guides/code-quality-checklist.md` | 592 | 24 |
| `reference/unit-testing.md` | 438 | 45 |
| `book/storage/storage-functions.md` | 363 | 149 |
| `book/programmability/dynamic-collections.md` | 188 | 46 |
| （其餘 8 檔略） | | |

兩種失效模式：

- **靜默截斷**：`reference/variables.md` 停在「### 推斷 (Inference)」後無結語，68 個 code fence 剩 1 個。整檔丟給 flash 級模型，輸出 token 用盡即停止，`response.text` 回傳短字串，無 exception。
- **刻意存根**：`code-quality-checklist.md` 結尾寫著「（詳細內容請參閱英文原始版本的範例程式碼）」。

這些檔案能進 `main` 且 commit 訊息寫「100% content parity」，是因為流程中沒有任何自動檢查在比對中英文結構。

### D3：88/143 檔的 frontmatter `description:` 仍是英文

> 修正：初次調查以 `grep '^description:'` 粗掃得出 89，實際以 YAML 解析 + CJK 判定為 **88**。實作計畫以 88 為斷言值。

`SYSTEM_PROMPT` 要求 *"Preserve all Markdown structure"*，模型把 YAML frontmatter 當結構保留，未翻譯其中的散文。`book/move-basics/vector.md` 第 3 行為英文 description、第 8 行為中文內文。

附帶：87 檔的 frontmatter 在 `---` 後多一個空行。經測試 YAML 仍可正常 parse，屬美觀問題。

### D4：正文含大量大陸用語

`SYSTEM_PROMPT` 只有 `"Traditional Chinese (Taiwan)"` 一句，無術語約束（反倒是 `SIDEBAR_PROMPT` 有「套件 not 包、函式 not 函數、模組 not 模塊」）。實測 `zh-tw-main` 正文：

| 大陸用語 | 台灣用語 | 出現次數 |
|---|---|---|
| 循環 | 迴圈 | 62 |
| 函數 | 函式 | 33 |
| 調用 | 呼叫 | 18 |
| 返回 | 回傳 | 15 |
| 全局 | 全域 | 5 |
| 遍歷 | 走訪 | 5 |
| 變量 | 變數 | 3 |
| 優化 | 最佳化 | 2 |

`類型`（918 次）與 `實例`（75 次）為灰色地帶，本次**不處理**。

> 上表 143 次為含 fenced code block 與 inline code 的原始 grep 數。`glossary.scan` 會跳過程式碼，實際會被驗證關卡擋下的是 **126 處**。實作計畫以 126 為斷言值。

### D5：整檔重譯會摧毀人工成果

- **55 個自訂 anchor ID**（34 檔）。上游英文檔完全沒有 `{#id}`。目前 97 條內部 anchor 連結中 96 條可解析（唯一「失敗」是 parser 未處理 `?highlight=` query string，實際未斷）。重譯後 anchor 消失 → 連結斷裂。
- **374/928 個雙語標題**（`中文 (English)` 格式，覆蓋率 40%）。
- **經人工反覆調整的術語**（如 Hot Potato 經 `cc6ed707`、`109bef2b` 兩次修改定案為「燙手山芋」）。

### D6：manifest provenance 部分損壞

131 筆中，97 筆對得上 merge-base，3 筆對得上更舊的英文版本，**31 筆指向不存在於 repo 的 blob**。無中文 blob 被誤寫入（未中毒）。

用結構指紋（標題層級序列 + code fence 數）比對，31 筆中有 28 筆的中文內文結構與 merge-base 英文一致，可安全地將 provenance 回填為 merge-base blob SHA。餘 3 筆結構不符，一律全譯。

### D7：Prettier 是定時炸彈

根目錄 `.prettierrc` 設定 `proseWrap: "always"`、`printWidth: 100`。它不在 CI、非宣告依賴、無 pre-commit hook，故目前不會自動執行。

但 prettier 計算字寬時 CJK 算 2 格。實測中文檔 3189 行正文中有 970 行（30%）超過 100 顯示格；實際跑 `npx prettier@3 --write` 於 `vector.md` 改動 20/49 行、`control-flow.md` 改動 55/140 行，且會將中文句子從中間折斷。任何人執行一次 format 即產生橫跨全書的重排 diff。

### D8：兩個結構性地雷

- `--detect` 是純 git 操作，卻因 top-level `from google import genai` 而必須安裝 API 依賴。此即 D1 的成因。
- `git_hash_object()` 雜湊 **working tree** 檔案。CI 中因先 `git checkout origin/english-main -- <file>` 而正確；但本地執行 `--all` 會雜湊中文檔，將中文 blob SHA 寫入 manifest，永久污染該路徑的 provenance。目前尚未發生。
- `pyproject.toml` 宣告 `"google>=3.0.0"`，該 PyPI 套件與 `google-genai` 無關，應移除。

### D10：anchor carry-forward 按位置索引配對（實作階段發現）

`inject()` 原以標題序號配對沿用的 anchor。上游 `#223 massive rewrite` 大量增刪標題：35 個含顯式 anchor 的中文檔中，**19 個的英文標題序列已改變，其中 16 個標題數量也變了**（`control-flow.md` 9→11、`struct.md` 5→9、`references.md` 7→12）。位置配對會讓插入點之後的每個 anchor 靜默位移到錯誤的標題。

gate 6 原本只做集合差（`prev_ids - now_ids`），anchor 一個都沒少，守衛全綠。而兩個人工刻意選定、carry-forward 專為其存在的 anchor —— `{#clock}`（`epoch-and-time.md` 4→6）與 `{#immutable-frozen-object}`（`ownership.md` 7→8）—— **都在風險名單內**。

修法：配對改用**身分**而非位置。`inject()` 多收 `prev_en_body`，身分鍵為 `slugify_all(英文標題)`。

> 身分鍵必須是 anchor 本身的推導函式。原始文字會引入第二個、與推導不一致的身分：實測 `Error constants` → `Error Constants`、`Unpacking a struct` → `Unpacking a Struct` 這種只改大小寫的情形，原始文字比對會誤判「標題消失」而退役 anchor。改用 slug 後 carried 43→45、retired 6→4。slug 的去重後綴（`references` / `references-1`）另可正確區分 `references.md` 裡兩個同名為 `References` 的標題。

**退役政策：只警告，不阻斷。** 上游確實改名／刪除章節時該 anchor 本就應失效，英文站也一樣斷。以下 4 條已發佈 URL 會 404，須列入 PR 3 描述：

| 檔案 | 失效的 anchor | 舊英文標題 |
|---|---|---|
| `book/guides/2024-migration-guide.md` | `#method-aliases` | `Method Aliases`（併入 `` `use fun` and Method Aliases ``）|
| `book/move-basics/references.md` | `#references` | `References`（小節，上游刪除）|
| `book/move-basics/struct.md` | `#struct` | `Struct` |
| `book/move-basics/struct.md` | `#create-and-use-an-instance` | `Create and use an instance`（改名為 `Creating an Instance`）|

### D11：殘留簡體字（實作階段發現）

glossary 管**詞彙**（函數→函式），但語料庫另有**字形**問題：正文含 5 個簡體字，分佈於 4 檔 —— `witness-pattern.md` 的 `个`、`good-tests.md` 的 `麽`、`functions.md` 的 `况`、`structs.md` 的 `这`/`种`。重譯後模型一樣可能吐出零星簡體字。

偵測用 OpenCC 的 `s2tw`（簡體 → 台灣標準）逐字元比對，**必須配例外表 `{台, 游}`**：`台/臺` 在台灣通用；`游 → 遊` 是 OpenCC 詞組字典（旅游→旅遊）誤用到單字，「上游」的「游」是正確的。加例外表後語料庫零假陽性。

（`s2t` 不可用：它轉向「正統繁體」，把 `了→瞭`、`群→羣`、`才→纔`、`峰→峯` 全部誤報，35/143 檔中招。）

### D9：上游刪除的檔案不會被傳播

`detect_changed_files()` 只走訪 `english-main` 上存在的檔案，因此上游刪除的路徑永遠不會出現在工作清單中。

實例：`book/storage/transfer-restrictions.md` 於上游 `d700b884 [book] massive rewrite (#223)` 被刪除。`zh-tw-main` 已在 `site/docusaurus.config.ts:90` 加入 redirect、`book/sidebar.yml:137` 註解掉項目，但**檔案本身仍留在 repo**。這是目前唯一一個不在過期清單中的中文檔。

`manifest.py` 需額外回報「manifest 有記錄、但 `english-main` 已無此路徑」的孤兒檔。

## 三、決策

| # | 決策 | 理由 |
|---|---|---|
| 1 | 先修 pipeline，再同步 | 151 檔無論如何要重譯一次；先修 prompt 才不會翻兩遍 |
| 2 | 程式碼強制 + 術語表，且採用分層 | anchor / description / 驗證皆為決定性邏輯，不該交給 LLM |
| 3 | 本地跑 backfill，依章節分 PR | 一次跑完約數十分鐘，不需依賴每日 cron |
| 4 | 翻譯後端抽象成 `translate(text) -> text` | 本地用 `claude -p`，CI 用 Gemini；其餘邏輯共用同一份程式碼 |
| 5 | 術語表只收無爭議詞（8 條），不動 `類型` / `實例` | 控制 diff 面積與 review 成本 |
| 6 | 未過期檔案以 `glossary.enforce` 機械換詞，不重譯 | 見下方註記：實際對象僅 1 檔且違禁詞為 0，不需獨立工項 |
| 7 | PR 0（模組）與 PR 1（CI 修復）分開 | CI 修復需獨立 `workflow_dispatch` 驗證 |
| 8 | 本地 backfill 的 model 於 PR 3 第一步以 A/B 決定 | 無實測數據，不預先寫死 |
| 9 | 孤兒檔（上游已刪）由管線回報並刪除 | D9 |

> **決策 6 的修正**：討論過程中曾以「13 個未過期檔案」為前提做此決策，該數字有誤（源於將 manifest 筆數 131 與 zh 檔數 143 相減，但不在 manifest 中的檔案在 detect 眼中屬「從未翻譯」，同樣進入工作清單）。實測 `english-main` 的 149 個 md 檔**全部**過期；`zh-tw-main` 上唯一不在清單中的是孤兒檔 `book/storage/transfer-restrictions.md`，其 glossary 違禁詞數為 0。故本決策無實際對象，`glossary.enforce` 本即管線的一環。

## 四、架構

採「抽成模組、後端可插拔」。`scripts/zh_tw/` 下各單元職責單一、可獨立測試：

| 單元 | 職責 | 依賴 |
|---|---|---|
| `frontmatter.py` | 拆／合 YAML 區塊 | 無 |
| `anchors.py` | 從英文標題算 slug，注入 `{#slug}` | 無 |
| `glossary.py` | 載入詞表、掃描違禁詞、機械換詞 | `glossary.json` |
| `validate.py` | 七道斷言 | 上述三者 |
| `manifest.py` | 讀寫 manifest、計算過期清單 | git |
| `backends/gemini.py`<br>`backends/claude_cli.py` | `translate(text) -> text` | 各自 SDK / CLI |
| `pipeline.py` | 編排 | 全部 |

LLM 只出現在 `backends/`。`manifest.py` 不 import 任何後端，故 `--detect` 無 API 依賴 —— D1 在結構上不可能復發。

### 資料流

```
english-main:<path>          zh-tw-main:<path>
        │                            │
        └──────┬─────────────────────┘
               ▼
      manifest.stale_files()          純 git，無 API 依賴
               ▼
      tier(path)
        ├─ delta ≤ 6 行 且 結構驗證通過 ──→ 【A 層】內文不動，只換 frontmatter
        └─ 其餘 ────────────────────────→ 【B 層】整檔重譯內文
               │
               ▼
      frontmatter.split()  →  (meta, body)
               ▼
      chunk(body) if 過長          按 H2 切段，避免輸出 token 截斷
               ▼
      backend.translate(chunk)     唯一的 LLM 呼叫點
               ▼
      join(chunks)
               ▼
      anchors.inject(zh, en, prev_zh)   拼接完成後對整份文件跑一次
               ▼
      glossary.enforce(zh)              跳過 code block 與 inline code
               ▼
      validate(zh, en)                  不過就 raise，不寫檔
               ▼
      write + manifest.record(path, english_blob_sha)
```

`anchors.inject` 必須在**拼接後**執行：切段後每段的標題序列僅為全域序列的子區間，段級注入無法保證全域一致。

`manifest.record` 寫入的是從 git ref 讀取的 blob SHA，非 `git hash-object` working tree —— 消除 D8 的地雷。

## 五、分層

閾值 6 行，因上游該批 frontmatter 變更恰為 +4~5 行。

**A 層前提是中文內文與其英文來源結構一致**（validate 第 1、2 條）。不通過者強制降級 B 層。此規則救回 5 個檔案，其中包括 `reference/variables.md`（36/824 行）—— 上游只動它的 frontmatter，若純依 delta 分層，其缺失的 788 行永遠不會回來。

| 章節 | A | B-新檔 | B-過期 | B-強制 | 合計 |
|---|---|---|---|---|---|
| `book/move-basics` | 0 | 2 | 27 | 0 | 29 |
| `book/programmability` | 2 | 2 | 21 | 1 | 26 |
| `reference`（含子目錄） | 32 | 1 | 1 | 2 | 36 |
| `book/testing` | 0 | 13 | 0 | 0 | 13 |
| `book/concepts` | 0 | 0 | 6 | 0 | 6 |
| `book/object` | 0 | 0 | 6 | 0 | 6 |
| `book/guides` | 2 | 1 | 3 | 2 | 8 |
| `book/storage` | 0 | 0 | 7 | 0 | 7 |
| `book/appendix` | 4 | 0 | 2 | 0 | 6 |
| `book/before-we-begin` | 4 | 0 | 1 | 0 | 5 |
| `book`（根） | 2 | 1 | 1 | 0 | 4 |
| `book/move-advanced` | 0 | 1 | 2 | 0 | 3 |
| `book/your-first-move` | 1 | 0 | 1 | 0 | 2 |
| **合計** | **47** | **21** | **78** | **5** | **151** |

## 六、決定性層規格

### `anchors.py`

```
inject(zh_body, en_body, prev_zh_body) -> zh_body'
```

逐標題對位（標題數不同則 raise）。每個標題：

1. `prev_zh_body` 同位置已有 `{#id}` → **原樣沿用**
2. 否則 → 補上 `slugify(英文標題)`

`slugify`：去除 inline code 反引號、連結取顯示文字、轉小寫、移除標點、空白轉連字號。

規則 1 是必要的：實測 `slugify` 重現現有 46/48 個 anchor，剩 2 個是人工刻意選定的不同值（標題 `Immutable (Frozen) State` 配 `{#immutable-frozen-object}`；標題 `Time` 配 `{#clock}`）。**anchor 是已發佈的 URL，是對外契約，不是衍生值。**

規則 2 將覆蓋率從 34 檔擴及全部，且新 anchor 與上游英文站一致。

### `glossary.py`

```json
{ "函數": "函式", "調用": "呼叫", "返回": "回傳", "循環": "迴圈",
  "全局": "全域", "變量": "變數", "遍歷": "走訪", "優化": "最佳化" }
```

兩個用途：注入 prompt 作為指示；翻譯後機械掃描並替換。替換**必須跳過 code block 與 inline code**（`` `loop` `` 內的字不得更動）。

### `frontmatter.py`

接管上游整塊 frontmatter，逐欄位處理：

- `description`（149 檔）、`title`（35 檔）→ 送翻譯
- `unlisted`（1 檔）及任何未知欄位 → 原樣照抄

輸出以 `yaml.safe_dump` 產生，D3 的多餘空行自然消失。

### `validate.py`

| # | 斷言 | 擋住 |
|---|---|---|
| 1 | 中文標題層級序列 == 英文標題層級序列 | D2 截斷 |
| 2 | code fence 數量相等 | D2 程式碼遺失 |
| 3 | frontmatter key 集合 == 英文的 key 集合 | 欄位漏抄 |
| 4 | `description` / `title` 含 CJK | D3 漏譯 |
| 5 | 所有內部 anchor 連結可解析 | D5 anchor 被洗掉 |
| 6 | 既有 anchor 未消失，且仍綁在同一個英文標題（同一 slug 身分）上 | URL 契約破壞、anchor 位移（D10）|
| 7 | 無 glossary 違禁詞；`prettier --check` 通過 | D4、D7 |
| 8 | 正文（程式碼區塊外）無簡體字 | D11 字形（glossary 管詞彙，這道管字形）|

### `.prettierrc`

於 `zh-tw-main` 加入：

```json
"overrides": [
  { "files": "**/*.md", "options": { "proseWrap": "preserve" } }
]
```

`proseWrap: "always"` 是為英文設計。CJK 無詞間空格，prettier 只能在標點或 inline code 邊界折行，結果不美觀且使 review diff 充滿噪音。改為 `preserve` 後 prettier 對散文成為 no-op，其餘格式化能力仍可用。因永不 merge 上游進 `zh-tw-main`，此分岔不產生衝突。

## 七、執行計畫

各 PR 的檔案集合互斥且涵蓋全部 151 檔。PR 3 抽走的 15 個殘缺檔已自 PR 4–7 的章節計數中扣除。

| PR | 內容 | 譯文檔數 |
|---|---|---|
| 0 | `scripts/zh_tw/` 模組 + 單元測試 + `.prettierrc` override + manifest provenance 回填 + 移除 `pyproject.toml` 的 `google` 假依賴 | 0 |
| 1 | CI 修復（`translate-zh-tw.yml`） | 0 |
| 2 | A 層（只換 frontmatter） | 47 |
| 3 | **P0：結構殘缺檔** + 刪除孤兒檔 `transfer-restrictions.md` | 15 |
| 4 | `book/move-basics` | 29 |
| 5 | `book/programmability`（扣除 PR 3 的 6 檔） | 18 |
| 6 | `book/testing`（全新章節） | 13 |
| 7 | 其餘（`concepts` 6 / `storage` 6 / `object` 4 / `move-advanced` 3 / `appendix` 2 / `book` 根 2 / `guides` 2 / `before-we-begin` 1 / `your-first-move` 1 / `reference` 2） | 29 |
| | **合計** | **151** |

PR 3 的 15 檔分佈：`programmability` 6、`guides` 4、`object` 2、`reference` 2、`storage` 1。

PR 3 排在內容 PR 最前：那 13 個嚴重殘缺頁面現正掛在線上，優先於同步上游新內容。

PR 3 的第一個步驟：取一個術語密集的長檔（建議 `reference/variables.md`），以 `claude -p` 分別用 haiku 與 sonnet 各翻一次，人工比對後決定 backfill 使用的 model。避免 104 檔翻完才發現需重來。

### CI 修復清單

1. `Setup Python` + `Install dependencies` 移至 `Detect` 之前。
2. 移除 `2>/dev/null` 與 `|| true`。detect 失敗必須讓 job 紅。
3. `manifest.py` 不 import 後端 —— 即使步驟順序再度寫反也不會爆。
4. 移除 `git push -f`，改用 `auto/zh-tw-<run_id>` 唯一分支名。現行 force-push 會在 PR 未合併時覆蓋前一次的翻譯成果。
5. `head -5` 出現三次 + `--batch-size 5` 一次 → 收斂為單一 `BATCH_SIZE` 環境變數。
6. commit 前執行 `validate.py`，不過則 job 紅、不推送。

### 錯誤處理

單一檔案 validate 失敗 → 不寫檔、記錄原因、繼續下一檔、最終 exit 非零。不得出現「翻壞的檔案已落地但 job 綠燈」。現行腳本先 `write_text` 再處理例外，是 D2 得以進入 repo 的成因之一。

## 八、測試

- **純函式單元測試**：`slugify`、`glossary.enforce`（含 code block 跳過）、`frontmatter` round-trip、`chunk`／`join` 可逆性。
- **`validate.py` 以現有 repo 為 fixture**：對 HEAD 執行，斷言恰有 19 檔於第 1、2 條失敗、89 檔於第 4 條失敗。此舉將當前缺陷鎖定為已知基線；backfill 完成後改為斷言全綠。
- **後端在測試中替換為回傳固定字串的 fake**，不呼叫真實 API。

七道斷言對現在的 HEAD 執行即會變紅，無需另行製造缺陷來驗證守衛有效。

## 九、驗收條件

1. `zh-tw-main` 的 `book` + `reference` 下有 149 個 md 檔，與 `english-main` 路徑集合完全一致（含新增 7 檔、刪除孤兒檔 1 檔）。
2. `validate.py` 對全部 149 檔執行，全綠。修復前的基線為：第 1、2 條紅 15 檔，第 4 條紅 88 檔，第 7 條紅 126 處，第 8 條紅 4 檔 5 字。
3. `manifest.stale_files()` 回傳空清單；`manifest.orphans()` 回傳空清單。
4. 97 條內部 anchor 連結全部可解析（`check_links` 須剝除 `?query` 才不會有假陽性）；55 個既有 anchor 的 ID 值一個都沒變。
5. 8 條 glossary 違禁詞在正文中出現次數為 0（現況：程式碼區塊外 126 處）。
6. `npx prettier@3 --check 'book/**/*.md' 'reference/**/*.md'` 通過。
7. `translate-zh-tw.yml` 手動 dispatch 一次，能真實偵測到過期檔案（非 0）並在無過期檔時正確跳過；detect 步驟失敗時 job 必須紅。
8. `pnpm build` 成功，Docusaurus 無 broken anchor 警告。

## 十、風險

| 風險 | 對策 |
|---|---|
| Chunking 後拼接處語氣不連貫 | 按 H2 切段（語意邊界），非按行數 |
| haiku 中文技術翻譯品質不足 | PR 3 第一步做 A/B，先驗證再全量 |
| 重譯洗掉 40% 的雙語標題慣例 | 寫入 prompt 規則；覆蓋率本就僅 40%，不列入驗收硬條件 |
| glossary 機械換詞誤傷 code block | 單元測試涵蓋；替換前先遮蔽 fenced 與 inline code |
| A 層 47 檔內文停留在舊英文版 | 上游對這些檔僅改 frontmatter，內容實際未過期；且已通過結構驗證 |
