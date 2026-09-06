# 標題顯式 anchor id：收斂成單一真相來源，判準對齊消費者

日期：2026-09-06
狀態：設計已確認，待寫實作計畫
前身：`tasks/progress.md` 的 T3（原描述為「`anchors._ANCHOR` 只收 ASCII id，reference/ 的中文標題無法用顯式 `{#id}` 與 URL 解耦」）

## 一、T3 的原始動機已經消失，剩下的是另一個問題

T3 記於 2026-09-04（`tasks/notes.md`「已知取捨：reference/abort-and-assert.md 兩個標題改字 → 衍生 anchor slug 變更」）。當時 reference/ 的中文標題沒有顯式 `{#id}`，URL 由中文標題 auto-slug 而來，改字就換 URL。

2026-09-06 實測，**全語料 149 檔（book 114 + reference 35）的每一個標題都已帶顯式 ASCII `{#id}`**，id 由英文標題衍生：

```
$ for d in book reference; do 找出沒有 '^#{1,6} .*{#' 的檔案; done
book:      無 anchor 0 / 114
reference: 無 anchor 0 / 35
```

排乾工作（PR #26–#30）本身就把中文標題與 URL 解耦了。**T3 的字面目標不必再做。**

剩下的實體是調查過程中量到的另一件事：repo 內對「什麼是顯式 `{#id}`」有三份互相不一致的定義，且沒有一份等於真正的消費者。

## 二、缺陷：三份定義，零份等於消費者

### 消費鏈（lessons L23：查規格前先確認誰在消費）

```
book/**.md, reference/**.md
  → site/src/plugins/{yaml-sidebar,mdbook-anchor-code}.ts   （不碰標題）
  → @docusaurus/mdx-loader remark/headings/index.ts
       extractClassicSyntaxHeadingId()
       → @docusaurus/utils parseMarkdownHeadingId(heading, 'classic')
            /\s*\{#(?<id>(?:.(?!\{#|\}))*.)\}$/
```

上游原始碼的註解寫得很明白：**"The ID can contain any characters except `{#` and `}`"**。docusaurus 本來就吃 CJK anchor；擋住的是我們自己。

### 三份定義

| 位置 | regex | 吃 CJK |
|---|---|---|
| `scripts/zh_tw/anchors.py:19` `_ANCHOR` | `[A-Za-z0-9_-]+` | ✗ |
| `scripts/zh_tw/validate.py:492` `_ANCHOR_SUFFIX`（gate 6 前處理） | `[\w-]+`（Python `\w` 是 Unicode-aware） | ✓ |
| `scripts/zh_tw/backends/fake.py:49` `_EXPLICIT_ANCHOR` | `[\w-]+` | ✓ |
| 消費者 docusaurus 3.10.2 | `[^{#}]+`（實質） | ✓ |

### 觀察到的實際分歧

輸入 `## 中止與斷言 {#終止與斷言-abort-and-assert}`：

```
anchors.existing_anchor  → None                                 認不得
anchors.slugify          → 中止與斷言-終止與斷言-abort-and-assert   把 id 併進 slug
validate.ANCHOR_SUFFIX   → '中止與斷言'                           認得，剝掉了
validate._anchor_ids     → {'中止與斷言-終止與斷言-abort-and-assert'}  與 gate 6 不同母體
anchors.inject           → '## 中止與斷言 {#終止與斷言-abort-and-assert} {#abort-and-assert}'
```

最後一行就是 notes.md 說的「反而更糟」。docusaurus 對它的判定是 id = `abort-and-assert`，**而標題文字裡留著字面的 `{#終止與斷言-abort-and-assert}` 被渲染出來**。

這是 lessons L15（同一個不變式兩份實作，第二份一定漂移）與 L23（判準只要還是我維護的一份推論，就會有第五輪）的合體形態。

## 三、要建立的不變式

> 「一個標題的顯式 id 是什麼」在整個 repo 只有**一份**定義，且那份定義**等於消費者**（docusaurus mdx-loader）的定義。

## 四、架構

```
                         ┌─ anchors.existing_anchor(h) -> str | None   （取 id）
anchors.ANCHOR_SUFFIX ───┼─ anchors.strip_anchor(h)    -> str          （剝除）
  （唯一真相來源）         └─ anchors.slugify / inject 內部自用

消費端不再各自持有 regex：
  validate.ANCHOR_SUFFIX        = anchors.ANCHOR_SUFFIX   保留公開別名（pipeline.py:227-228 在用）
  validate.heading_suffix_error → anchors.strip_anchor
  validate._anchor_ids          → anchors.existing_anchor（已經是）
  backends/fake.py              → anchors.ANCHOR_SUFFIX（取 group(0).strip()，它要的是整段 `{#id}`）
```

regex 本體是上游移植，不是自己推的：

```python
# 移植自 @docusaurus/utils 3.10.2 lib/markdownHeadingIdUtils.ts parseMarkdownHeadingId('classic')
#   /\s*\{#(?<id>(?:.(?!\{#|\}))*.)\}$/
_ANCHOR = re.compile(r"\s*\{#((?:.(?!\{#|\}))*.)\}$")   # id 取出後 .strip()，比照上游
```

CJK 支援不是被「加」進來的，是收斂到消費者判準之後自然落地的副產品。

### 為什麼放寬是安全的：兩份語料實測 0 diff

```
zh 語料           149 檔 / 1102 標題  新舊 regex 判定  0 diff
en (english-main) 156 檔 / 1164 標題  新舊 regex 判定  0 diff（英文原檔顯式 id 數 = 0）
```

也就是本改動在現況下是 **byte 級 no-op**，風險面只存在於未來輸入。

## 五、新能力不能變成新的洞

一旦 `{#中文}` 被認得，`inject` 的 tier 1/2 就會沿用它，有可能長出 CJK URL。分層處置：

```
tier 1（zh_body 既有）／tier 2（依身分沿用）  → 字元集不設限。
                                              anchor 是已發佈契約，本來就該原封不動。
tier 3（衍生）                                → 仍由英文標題 slugify_all 產生，
                                              結構上不可能產出 CJK。
```

＝**能力開了，但管線自己不會長出 CJK anchor**；只有人手動寫進語料才會有。

另加一條 `check_repo` 層的 informational 統計（全語料 CJK anchor 數，baseline 0），比照 `glossary_scan_only` baseline 的做法，讓數字一變有人看見（`tasks/notes.md` 2026-09-04「scan_only 頻道需要 baseline，否則會變成沒人看的噪音」）。

## 六、測試

### `tests/test_anchors_upstream_parity.py`（新檔）

1. 上游 regex 字面值、來源路徑、版本號寫成測試常數。
2. **版本漂移守衛**：讀 `site/package.json` 的 `dependencies["@docusaurus/core"]`（現值 `3.10.2`），≠ 釘住的版本就紅，逼人回去看上游 regex 有沒有變。判準只要還是我維護的一份推論就會有第五輪（L23）；這條讓漂移**會叫**，而不是靜默腐化。
3. 共同輸入表，逐一斷言 Python 實作與上游移植同解：CJK id、含空白的 id、`{#a} {#b}`、`{#}`、`{#a}}`、`{#a}` 後面還有文字、id 前後有空白、標題只有 `{#id}` 沒有文字。
4. fuzz：由 heading token 原子表生成，Python 實作 vs 上游移植對拍。**報負面結果之前，先拿本設計第二節那幾個 repro 反餵 generator 驗覆蓋率**（L15 推論：fuzz 的負面結果只在 generator 生得出該類輸入時才有意義）。

### `tests/test_anchors_realworld.py`（既有檔，補一條）

釘固定 sha 讀 zh + en 語料（L3：census 測試不讀活狀態），斷言新實作對 1102 / 1164 個標題算出的 id 集合與既有 `{#id}` 全等。

### mutation（L5：每條新守衛先在真實缺陷面前紅一次）

| 變異 | 必須轉紅的測試 |
|---|---|
| `_ANCHOR` 改回 `[A-Za-z0-9_-]+` | parity 輸入表（CJK 案例） |
| `validate` 改回持有自己的 regex | 單一真相來源的一致性測試 |
| 釘住的版本號改成 `3.11.0` | 版本漂移守衛 |
| tier 3 衍生改成允許 CJK | 「管線不會自己長出 CJK anchor」的測試 |

## 七、驗收準則（可判定）

- [ ] `pytest` 全綠，且新增測試數 > 0；報數量不報形容詞。
- [ ] `check_repo` 0/0/0/0。
- [ ] `git diff --stat book reference` 為**空**（語料 byte 不動）。
- [ ] `scripts/zh_tw/` 底下比對 `{#` 的 regex 字面值只剩 `anchors.py` 一處（`grep -rn` 可驗；`tests/` 底下的上游移植字面值是刻意的第二份，用來對拍，不算違反）。
- [ ] 上表四個 mutation 各自讓指定測試轉紅（逐一實測，不靠推論）。

## 八、Non-goals

- 不改任何語料 byte。
- 不救回排乾過程換掉的舊中文 auto-slug URL（原「方案 B」）。repo 內以 CJK anchor 為目標的連結實測 0 處；外部深連結的實際流量未知，值不值得由使用者另行裁決。若日後要做，`site/docusaurus.config.ts` 已載入 `@docusaurus/plugin-client-redirects`，那是比改語料更好的路徑。
- 不跨語言呼叫 node 做 oracle（成本不成比例；改用「移植 + 版本漂移守衛」逼近同等效果）。
- 不碰 gate 5 / gate 6 的判定邏輯本身，只替換它們共用的前處理。
- 不做無關重構。

## 九、已知取捨

放寬到「除了 `{#` 與 `}` 以外的任何字元」之後，一個文字本身就以 `{#...}` 結尾的合法標題，其結尾會被當成 id 吃掉。這正是 docusaurus 的行為。**跟消費者一致地錯，優於跟消費者不一致地對** —— 不一致本身才是缺陷的來源。

## 十、Security constraints

無使用者資料、無 auth、無金流、無網路 I/O。改動範圍是純函式與其測試，不觸及檔案刪改路徑（Red Team Protocol 不適用；`tasks/lessons.md` L17 的破壞性 mutation 但書因此不觸發，但 mutation 仍須確認變異值不會流進 `rmtree`/`unlink`/`subprocess`——本案不會）。
