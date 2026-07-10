# zh-TW 翻譯管線重建 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 重建 zh-TW 翻譯管線，把 frontmatter／anchor／術語／驗證從 LLM 手中移交給有測試的決定性程式碼，修好從未執行過的 CI，然後安全地補譯 151 個檔案。

**Architecture:** `scripts/zh_tw/` 模組化。LLM 只出現在 `backends/` 的 `translate(text) -> str`；其餘皆為純函式。每個檔案寫入前必須通過 7 道驗證，不過就 raise、不寫檔。本地 backfill 走 `claude -p`，CI 走 Gemini，共用同一個 `pipeline.py`。

**Tech Stack:** Python 3.13、uv、pytest、PyYAML、**markdown-it-py**（CommonMark 參考實作）、**opencc-python-reimplemented**（簡繁字形偵測）、`claude -p` CLI、`google-genai`、GitHub Actions。

## Global Constraints

- Python `>=3.13`（`.python-version` = 3.13）。一律以 `uv run` 執行，不要 `pip install` 到系統環境。
- **`scripts/zh_tw/manifest.py` 絕對不可 import 任何 backend。** 這是 D1（CI 五個月未執行）的結構性根除；`--detect` 必須在沒有 `google-genai` 的環境下可執行。
- **驗證失敗一律 raise，不得寫檔。** 現行腳本先 `write_text` 再處理例外，是 D2（19 檔結構殘缺）得以進入 repo 的成因。
- **anchor 是已發佈的 URL，是對外契約。** 既有 `{#id}` 一律沿用，永不重算。
- Glossary 替換必須跳過 fenced code block 與 inline code。
- `git add` 只加明確指定的檔案，禁止 `git add -A` / `git add .`。
- **禁止任何會改寫工作區的 git 操作**：`git stash` / `git stash pop` / `git stash apply`、
  `git reset --hard`、`git checkout <ref> -- <path>`、`git restore --source`、`git merge`、`git rebase`。
  要讀某個 ref 的檔案內容，一律用 `git show <ref>:<path>` 讀到記憶體或 scratchpad，不要落到工作區。
  （事故：一個 subagent 在無未提交變更時跑了 `git stash`（no-op），接著 `git stash pop` 彈出使用者
  一個不相關的舊 stash，在 24 個檔案上撞出衝突。它自己沒有未提交的東西，卻假設 stash 頂端是自己的。）
- 術語表固定為這 8 條，不擴充：`函數→函式`、`調用→呼叫`、`返回→回傳`、`循環→迴圈`、`全局→全域`、`變量→變數`、`遍歷→走訪`、`優化→最佳化`。不動 `類型`、`實例`。
- 測試中的翻譯後端一律用 fake，不打真實 API。
- **markdown 區塊解析一律走 `scripts/zh_tw/anchors.py` 匯出的 `headings()` / `visible_lines()` / `fence_lines()`。**
  任何模組都不得自己寫 fence 切換迴圈。手刻掃描器連續三輪出現 CommonMark 規格落差（HTML 註解、
  空格縮排、tab 縮排），且每次的失效簽名都是「假陽性 + 假陰性互相抵消」，讓數量相符的守衛全部變綠。
  這三個 helper 底層改用 `markdown-it-py`（CommonMark 參考實作）。
- 這三個 helper 接收的是 **body**（frontmatter 已剝除）。傳入完整文件會讓 `---\ndescription: ...\n---`
  被 CommonMark 解析成 setext 標題，憑空多一個 h2。
- **任何用 regex 逼近 CommonMark 語意的地方，必須有接上生成器的差異測試。** 以 `markdown-it-py`
  的 token stream 為 oracle，用片段組合（反引號串、換行、違禁詞、一般文字）生成上萬個 body，
  斷言我們的判定與 oracle 逐一相符。Task 5 的 inline code 遮蔽連續三輪出現規格落差
  （跨行 span、非極大反引號串、span 越過 fence 邊界），前兩輪靠人工探針才發現，
  第三輪是生成器在幾秒內找到的。手選探針只能覆蓋想得到的情況。
- **解析 `git ls-tree` 一律用 `-z` 並以 `\0` 切分。** `.split()` 會依任意空白切開，含空格的路徑會靜默裂成兩個
  看似合理的假路徑；`--name-only` 預設還會把非 ASCII 路徑加引號轉義。這與 D1 的失效形狀相同：不噴錯、輸出看起來對。
  （`git diff --numstat` 的數字輸出不受此限。）
- 暫存清單檔一律寫入 session scratchpad，不寫 `/tmp`。每個 shell 步驟開頭先設定：
  ```bash
  export SP="/private/tmp/claude-501/-Users-ramonliao-Documents-Code-Project-Web3-BlockchainDev-SUI-First-Mover-TW-move-book/5f7f30a1-5d4e-475c-9570-ddb0ae12915c/scratchpad"
  ```
  （`.github/workflows/` 內的 `/tmp/changed_files.txt` 是 CI runner 內部路徑，不適用此規則。）

## 名詞

- **英文來源（`en_text`）**：某個中文檔當初賴以翻譯的英文內容。基線測試時是 merge-base `f2c0a93e`；backfill 後是 `english-main`。`validate()` 一律以參數接收，不自行讀 ref。
- **A 層**：上游 delta ≤ 6 行且結構驗證通過 → 只換 frontmatter，內文不動（47 檔）。
- **B 層**：其餘 → 整檔重譯內文（104 檔）。

---

### Task 1: 專案骨架與術語表

**Files:**
- Create: `scripts/zh_tw/__init__.py`
- Create: `scripts/zh_tw/glossary.json`
- Create: `tests/__init__.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Produces: `scripts/zh_tw/glossary.json` — `dict[str, str]`，大陸用語 → 台灣用語。

- [ ] **Step 1: 建立套件骨架**

```bash
mkdir -p scripts/zh_tw/backends tests
touch scripts/zh_tw/__init__.py scripts/zh_tw/backends/__init__.py tests/__init__.py
```

- [ ] **Step 2: 寫術語表**

`scripts/zh_tw/glossary.json`:

```json
{
  "函數": "函式",
  "調用": "呼叫",
  "返回": "回傳",
  "循環": "迴圈",
  "全局": "全域",
  "變量": "變數",
  "遍歷": "走訪",
  "優化": "最佳化"
}
```

- [ ] **Step 3: 修正 pyproject.toml 的假依賴**

`"google>=3.0.0"` 是 PyPI 上與 `google-genai` 無關的搜尋爬蟲 stub，移除。加入 `pyyaml` 與 dev 依賴。

```toml
[project]
name = "move-book"
version = "0.1.0"
description = "The Move Book, Traditional Chinese (Taiwan)"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "google-genai>=1.61.0",
    "pyyaml>=6.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
]
```

- [ ] **Step 4: 驗證環境**

Run: `uv run --with pytest pytest --version`
Expected: `pytest 9.x.x`

- [ ] **Step 5: Commit**

```bash
git add scripts/zh_tw/__init__.py scripts/zh_tw/backends/__init__.py tests/__init__.py scripts/zh_tw/glossary.json pyproject.toml
git commit -m "chore: scaffold scripts/zh_tw package and glossary"
```

---

### Task 2: frontmatter 拆合

**Files:**
- Create: `scripts/zh_tw/frontmatter.py`
- Test: `tests/test_frontmatter.py`

**Interfaces:**
- Produces:
  - `split(text: str) -> tuple[dict, str]` — 回傳 `(meta, body)`。無 frontmatter 時 `meta == {}`。
  - `join(meta: dict, body: str) -> str` — `meta` 為空時直接回傳 `body`。
  - `TRANSLATABLE_KEYS: frozenset[str]` — `{"description", "title"}`

- [ ] **Step 1: 寫失敗測試**

`tests/test_frontmatter.py`:

```python
from scripts.zh_tw import frontmatter as fm


def test_split_extracts_meta_and_body():
    text = '---\ndescription: "Hello"\n---\n\n# Title\n\nBody.\n'
    meta, body = fm.split(text)
    assert meta == {"description": "Hello"}
    assert body == "# Title\n\nBody.\n"


def test_split_tolerates_blank_line_after_opening_fence():
    """現存 87 個檔案的 frontmatter 長這樣，必須能讀。"""
    text = '---\n\ndescription: "Hello"\n---\n\n# Title\n'
    meta, body = fm.split(text)
    assert meta == {"description": "Hello"}


def test_split_returns_empty_meta_when_absent():
    meta, body = fm.split("# Title\n\nBody.\n")
    assert meta == {}
    assert body == "# Title\n\nBody.\n"


def test_join_emits_canonical_form_without_blank_line():
    """輸出一律規範化，D3 的多餘空行自然消失。"""
    out = fm.join({"description": "你好"}, "# 標題\n")
    assert out.startswith("---\ndescription:")
    assert "---\n\ndescription" not in out
    assert out.endswith("# 標題\n")


def test_round_trip_is_stable():
    text = fm.join({"description": "你好", "unlisted": True}, "# 標題\n")
    meta, body = fm.split(text)
    assert meta == {"description": "你好", "unlisted": True}
    assert body == "# 標題\n"


def test_non_string_values_survive():
    meta, _ = fm.split('---\nunlisted: true\n---\n\nx\n')
    assert meta == {"unlisted": True}
```

- [ ] **Step 2: 執行測試確認失敗**

Run: `uv run --with pytest --with pyyaml pytest tests/test_frontmatter.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.zh_tw.frontmatter'`

- [ ] **Step 3: 實作**

`scripts/zh_tw/frontmatter.py`:

```python
"""Frontmatter 的拆解與規範化重建。

輸出一律以 yaml.safe_dump 產生，故 LLM 不再有機會弄壞這段結構。
"""

import re

import yaml

TRANSLATABLE_KEYS = frozenset({"description", "title"})

_FENCE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def split(text: str) -> tuple[dict, str]:
    m = _FENCE.match(text)
    if not m:
        return {}, text
    meta = yaml.safe_load(m.group(1)) or {}
    if not isinstance(meta, dict):
        return {}, text
    body = text[m.end():]
    return meta, body.lstrip("\n")


def join(meta: dict, body: str) -> str:
    if not meta:
        return body
    dumped = yaml.safe_dump(
        meta, allow_unicode=True, default_flow_style=False, sort_keys=False
    ).rstrip("\n")
    return f"---\n{dumped}\n---\n\n{body}"
```

- [ ] **Step 4: 執行測試確認通過**

Run: `uv run --with pytest --with pyyaml pytest tests/test_frontmatter.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/zh_tw/frontmatter.py tests/test_frontmatter.py
git commit -m "feat(zh_tw): deterministic frontmatter split/join"
```

---

### Task 3: 標題解析與 slugify

**Files:**
- Create: `scripts/zh_tw/anchors.py`
- Test: `tests/test_anchors_slug.py`

**Interfaces:**
- Produces:
  - `headings(body: str) -> list[tuple[int, str]]` — `(level, raw_text)`，只回傳實際會渲染的標題。
  - `heading_lines(body: str) -> list[tuple[int, int]]` — `(line_index_0based, level)`，供 chunking 取切段邊界。
  - `visible_lines(body: str) -> list[tuple[int, str]]` — 不在 fence / HTML block / 縮排程式碼內的行。
  - `fence_lines(body: str) -> int` — 實際會渲染的 fence 分隔行數。
  - `slugify(heading: str) -> str`
  - `slugify_all(texts: list[str]) -> list[str]` — 依 github-slugger 規則對重複 slug 加 `-1`、`-2` 後綴。

- [ ] **Step 1: 寫失敗測試**

`tests/test_anchors_slug.py`:

```python
from scripts.zh_tw import anchors


def test_slugify_basic():
    assert anchors.slugify("Vector Syntax") == "vector-syntax"


def test_slugify_strips_inline_code_backticks():
    assert anchors.slugify("Enums and `match`") == "enums-and-match"


def test_slugify_keeps_underscores():
    """github-slugger 保留底線；`ALL_CAPS` -> all_caps。"""
    assert anchors.slugify("Regular Constants Are `ALL_CAPS`") == "regular-constants-are-all_caps"


def test_slugify_drops_colons():
    assert anchors.slugify("Do Not Import `std::string::utf8`") == "do-not-import-stdstringutf8"


def test_slugify_takes_link_text():
    assert anchors.slugify("See [the docs](https://x.com)") == "see-the-docs"


def test_slugify_ignores_existing_anchor_id():
    assert anchors.slugify("Vector Syntax {#custom}") == "vector-syntax"


def test_slugify_all_deduplicates():
    """english-main 有 3 個檔案存在重複 slug。"""
    assert anchors.slugify_all(["Setup", "Setup", "Setup"]) == ["setup", "setup-1", "setup-2"]


def test_headings_skips_fenced_code():
    body = "# Real\n\n```move\n# not a heading\n```\n\n## Also Real\n"
    assert anchors.headings(body) == [(1, "Real"), (2, "Also Real")]


def test_headings_reports_level():
    assert anchors.headings("### Deep\n") == [(3, "Deep")]
```

- [ ] **Step 2: 執行測試確認失敗**

Run: `uv run --with pytest --with pyyaml pytest tests/test_anchors_slug.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.zh_tw.anchors'`

- [ ] **Step 3: 實作**

`scripts/zh_tw/anchors.py`:

```python
"""標題 anchor 的解析與注入。

anchor 是已發佈的 URL，是對外契約。既有的 {#id} 一律沿用，永不重算。

區塊結構（標題、fence、HTML block、縮排程式碼）一律交給 markdown-it-py 判定。
手刻的 fence 切換迴圈連續三輪出現 CommonMark 規格落差，且失效簽名都是
「假陽性 + 假陰性互相抵消」——  數量相符的守衛因此全部變綠。本模組是全專案
唯一的 markdown 區塊真相來源；其他模組必須呼叫這裡的 helper。
"""

import re

from markdown_it import MarkdownIt

from . import frontmatter

_MD = MarkdownIt("commonmark")

_ANCHOR = re.compile(r"\s*\{#([A-Za-z0-9_-]+)\}\s*$")
_INLINE_CODE = re.compile(r"`([^`]+)`")
_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_FENCE_MARK = re.compile(r"^ {0,3}(`{3,}|~{3,})")

_OPAQUE = ("fence", "code_block", "html_block")


class FrontmatterPassedIn(ValueError):
    """呼叫者傳了完整文件而非 body。"""


def _require_body(text: str) -> str:
    """CommonMark 會把 `---\ndescription: x\n---` 解析成 setext 標題，憑空多一個 h2。"""
    meta, _ = frontmatter.split(text)
    if meta:
        raise FrontmatterPassedIn("headings/visible_lines/fence_lines 需要 body，不是完整文件")
    return text


def _tokens(body: str):
    return _MD.parse(body)


def heading_lines(body: str) -> list[tuple[int, int]]:
    """(0-based 行號, 標題層級)，只含實際會渲染的標題。"""
    _require_body(body)
    return [
        (t.map[0], int(t.tag[1]))
        for t in _tokens(body)
        if t.type == "heading_open" and t.map
    ]


def headings(body: str) -> list[tuple[int, str]]:
    """(層級, 標題原始文字)。文字保留 inline code 與 {#anchor}。"""
    _require_body(body)
    toks = _tokens(body)
    return [
        (int(t.tag[1]), toks[i + 1].content)
        for i, t in enumerate(toks)
        if t.type == "heading_open"
    ]


def visible_lines(body: str) -> list[tuple[int, str]]:
    """不在 fence / HTML block / 縮排程式碼內的行，附 0-based 行號。"""
    _require_body(body)
    hidden: set[int] = set()
    for t in _tokens(body):
        if t.type in _OPAQUE and t.map:
            hidden.update(range(t.map[0], t.map[1]))
    return [(i, l) for i, l in enumerate(body.splitlines()) if i not in hidden]


def fence_lines(body: str) -> int:
    """實際會渲染的 fence 分隔行數（不含 HTML 註解內的 fence）。"""
    _require_body(body)
    lines = body.splitlines()
    return sum(
        1
        for t in _tokens(body)
        if t.type == "fence" and t.map
        for l in lines[t.map[0]:t.map[1]]
        if _FENCE_MARK.match(l)
    )


def slugify(heading: str) -> str:
    text = _ANCHOR.sub("", heading)
    text = _LINK.sub(r"\1", text)
    text = _INLINE_CODE.sub(r"\1", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", "-", text).strip("-")


def slugify_all(texts: list[str]) -> list[str]:
    """github-slugger 風格去重：候選若已被占用，遞增後綴直到空出為止。"""
    used: set[str] = set()
    out: list[str] = []
    for t in texts:
        base = slugify(t)
        candidate, n = base, 0
        while candidate in used:
            n += 1
            candidate = f"{base}-{n}"
        used.add(candidate)
        out.append(candidate)
    return out


def existing_anchor(heading: str) -> str | None:
    m = _ANCHOR.search(heading)
    return m.group(1) if m else None
```

`markdown-it-py` 是 CommonMark 的參考實作。改用它之後，先前手刻掃描器的六個已知失效案例（HTML 註解、`~~~` fence、info string 誤關 fence、3/4 空格縮排、tab 縮排）全部與參考渲染器一致。實測：對 `zh-tw-main`、merge-base、`english-main` 三個 ref 的 423 個檔案版本，新舊實作的標題層級序列與 fence 行數 **完全一致**，故 47 / 15 兩個基線不受影響。

- [ ] **Step 4: 執行測試確認通過**

Run: `uv run --with pytest --with pyyaml pytest tests/test_anchors_slug.py -v`
Expected: 9 passed

- [ ] **Step 5: 對真實 repo 驗證 slugify**

這一步是把「slugify 能重現 46/48 個既有 anchor」這個實測結論釘進測試。

`tests/test_anchors_realworld.py`:

```python
import subprocess

import pytest

from scripts.zh_tw import anchors

MERGE_BASE = "f2c0a93e1a0422078d3d051e4410ac3edc612016"
# 修復前的 zh-tw-main tip。釘死不動，否則 backfill 合併後這個測試會因為
# 「我們修好了東西」而變紅 —— 基線必須是固定靶。
PRE_FIX = "0d4b8bea77f1a6195b589ded4067d287adb4379a"

# 這兩個 anchor 是人工刻意選定的，與英文 slug 不同。
# 它們的存在正是 inject() 必須「沿用優先於重算」的理由。
KNOWN_DIVERGENT = {
    ("book/object/ownership.md", "immutable-frozen-object"),
    ("book/programmability/epoch-and-time.md", "clock"),
}


def _show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def _files() -> list[str]:
    r = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "-z", PRE_FIX, "book", "reference"],
        capture_output=True, text=True, check=True,
    )
    return [f for f in r.stdout.split("\0") if f.endswith(".md")]


def test_slugify_reproduces_existing_anchors():
    """除了兩個已知的人工選定 anchor，slugify(英文標題) 應重現全部既有 anchor。

    47 而非 46：初版 headings() 把 HTML 註解裡的標題也算進去，導致
    book/move-basics/string.md 的中英文標題數不符（10 vs 11）而被跳過。
    修好 parser 後該檔重新納入，貢獻一個正確配對的 {#ascii-strings}。
    """
    divergent, reproduced = set(), 0
    for path in _files():
        zh, en = _show(PRE_FIX, path), _show(MERGE_BASE, path)
        if not zh or not en or "{#" not in zh:
            continue
        zh_h, en_h = anchors.headings(zh), anchors.headings(en)
        if len(zh_h) != len(en_h):
            continue  # 結構殘缺檔，由 validate 負責
        for (_, zt), (_, et) in zip(zh_h, en_h):
            aid = anchors.existing_anchor(zt)
            if aid is None:
                continue
            if aid == anchors.slugify(et):
                reproduced += 1
            else:
                divergent.add((path, aid))

    assert reproduced == 47
    assert divergent == KNOWN_DIVERGENT
```

- [ ] **Step 6: 執行**

Run: `uv run --with pytest --with pyyaml pytest tests/test_anchors_realworld.py -v`
Expected: 1 passed

- [ ] **Step 7: Commit**

```bash
git add scripts/zh_tw/anchors.py tests/test_anchors_slug.py tests/test_anchors_realworld.py
git commit -m "feat(zh_tw): heading parser and github-compatible slugify"
```

---

### Task 4: anchor 注入（沿用優先於重算）

**Files:**
- Modify: `scripts/zh_tw/anchors.py`
- Test: `tests/test_anchors_inject.py`

**Interfaces:**
- Consumes: `headings`, `slugify_all`, `existing_anchor`（Task 3）
- Produces:
  - `inject(zh_body: str, en_body: str, prev_zh_body: str = "", prev_en_body: str = "") -> str`
  - `inject_report(...) -> tuple[str, list[str]]` — 同上，另回傳退役／未沿用的說明
  - `DuplicateAnchor(Exception)` / `NestedHeading(Exception)`
  - `HeadingMismatch(Exception)` — 標題數不符時 raise

三層解析，逐標題：

1. `zh_body` 該標題已有 `{#id}` → 原樣沿用（tier 1）
2. 否則以 **`slugify_all(英文標題)`** 為身分鍵，從 `prev_zh_body` 搬移其 anchor（tier 2）
3. 否則補上 `slugify_all(新英文標題)[j]`（tier 3；先保留 tier 1/2 的 id，derived 撞號時讓 derived 退讓）

**身分鍵是 slug，不是位置，也不是原始文字。** 位置配對會在上游增刪標題時把 anchor 位移到錯誤的標題（見 spec D10）；
原始文字配對會因大小寫改變而誤退役（`Error constants` → `Error Constants`）。沒有 `prev_en_body` 時**不沿用任何 anchor**，
並在 `inject_report` 中說明 —— 位置猜測正是這個 bug 本身。

上游真的刪除／改名章節時，該 anchor 退役。`inject_report()` 回報，但**不阻斷**：validate 不因退役而失敗。

- [ ] **Step 1: 寫失敗測試**

`tests/test_anchors_inject.py`:

```python
import pytest

from scripts.zh_tw import anchors


def test_inject_adds_slug_from_english_heading():
    zh = "# 向量\n\n內文\n"
    en = "# Vector\n\nBody\n"
    assert anchors.inject(zh, en) == "# 向量 {#vector}\n\n內文\n"


def test_inject_carries_forward_existing_anchor():
    """人工選定的 anchor 必須原樣保留，即使它不等於英文 slug。"""
    zh = "## 不可變狀態\n"
    en = "## Immutable (Frozen) State\n"
    prev = "## 不可變狀態 {#immutable-frozen-object}\n"
    assert anchors.inject(zh, en, prev) == "## 不可變狀態 {#immutable-frozen-object}\n"


def test_inject_preserves_anchor_already_in_zh():
    zh = "## 群組 {#party}\n"
    en = "## Party\n"
    assert anchors.inject(zh, en) == "## 群組 {#party}\n"


def test_inject_deduplicates_repeated_slugs():
    zh = "## 設定\n\n## 設定\n"
    en = "## Setup\n\n## Setup\n"
    out = anchors.inject(zh, en)
    assert "{#setup}" in out
    assert "{#setup-1}" in out


def test_inject_raises_on_heading_count_mismatch():
    """這正是 reference/variables.md 的失效模式：21 個英文標題、6 個中文標題。"""
    with pytest.raises(anchors.HeadingMismatch):
        anchors.inject("# 一\n", "# One\n\n## Two\n")


def test_inject_ignores_headings_inside_code_fences():
    zh = "# 標題\n\n```move\n# 註解\n```\n"
    en = "# Title\n\n```move\n# comment\n```\n"
    out = anchors.inject(zh, en)
    assert out.count("{#") == 1
    assert "# 註解" in out
```

- [ ] **Step 2: 執行測試確認失敗**

Run: `uv run --with pytest --with pyyaml pytest tests/test_anchors_inject.py -v`
Expected: FAIL — `AttributeError: module 'scripts.zh_tw.anchors' has no attribute 'inject'`

- [ ] **Step 3: 實作**

追加到 `scripts/zh_tw/anchors.py`:

```python
class HeadingMismatch(Exception):
    """中文與英文的標題數量不符，通常代表翻譯被截斷。"""


def _anchor_map(body: str) -> dict[int, str]:
    """以標題序號為鍵，取出既有的 anchor id。"""
    return {
        i: aid
        for i, (_, text) in enumerate(headings(body))
        if (aid := existing_anchor(text)) is not None
    }


def inject(zh_body: str, en_body: str, prev_zh_body: str = "") -> str:
    zh_h, en_h = headings(zh_body), headings(en_body)
    if len(zh_h) != len(en_h):
        raise HeadingMismatch(
            f"標題數不符: 中文 {len(zh_h)}, 英文 {len(en_h)}"
        )

    carried = _anchor_map(prev_zh_body) if prev_zh_body else {}
    current = _anchor_map(zh_body)
    derived = slugify_all([t for _, t in en_h])

    wanted = [
        current.get(i) or carried.get(i) or derived[i]
        for i in range(len(en_h))
    ]

    # 行號與層級一律取自共用的區塊解析器，不自己掃 fence。
    at_line = {ln: (idx, lv) for idx, (ln, lv) in enumerate(heading_lines(zh_body))}

    out = []
    for i, line in enumerate(zh_body.splitlines(keepends=True)):
        if i not in at_line:
            out.append(line)
            continue
        idx, level = at_line[i]
        text = _ANCHOR.sub("", zh_h[idx][1])
        nl = "\n" if line.endswith("\n") else ""
        out.append(f"{'#' * level} {text} {{#{wanted[idx]}}}{nl}")
    return "".join(out)
```

- [ ] **Step 4: 執行測試確認通過**

Run: `uv run --with pytest --with pyyaml pytest tests/test_anchors_inject.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/zh_tw/anchors.py tests/test_anchors_inject.py
git commit -m "feat(zh_tw): anchor injection with carry-forward of published ids"
```

---

### Task 5: 術語表強制

**Files:**
- Create: `scripts/zh_tw/glossary.py`
- Test: `tests/test_glossary.py`

**Interfaces:**
- Produces:
  - `load(path: str | None = None) -> dict[str, str]`
  - `scan(body: str) -> dict[str, int]` — 程式碼區塊外的違禁詞出現次數
  - `enforce(body: str) -> str`
  - `prompt_rules() -> str` — 供 backend 注入 prompt

- [ ] **Step 1: 寫失敗測試**

`tests/test_glossary.py`:

```python
from scripts.zh_tw import glossary


def test_enforce_replaces_mainland_terms():
    assert glossary.enforce("這個函數會返回一個值") == "這個函式會回傳一個值"


def test_enforce_skips_fenced_code_block():
    body = "呼叫函數\n\n```move\n// 函數 stays\n```\n"
    out = glossary.enforce(body)
    assert "呼叫函式" in out
    assert "// 函數 stays" in out


def test_enforce_skips_inline_code():
    assert glossary.enforce("使用 `函數` 這個詞") == "使用 `函數` 這個詞"


def test_enforce_handles_multiple_terms():
    assert glossary.enforce("循環中調用變量") == "迴圈中呼叫變數"


def test_scan_counts_violations_outside_code():
    body = "函數\n\n```\n函數\n```\n\n`函數`\n"
    assert glossary.scan(body) == {"函數": 1}


def test_scan_returns_empty_when_clean():
    assert glossary.scan("這是乾淨的中文") == {}


def test_prompt_rules_lists_every_pair():
    rules = glossary.prompt_rules()
    for bad, good in glossary.load().items():
        assert f"{good}" in rules and f"{bad}" in rules
```

- [ ] **Step 2: 執行測試確認失敗**

Run: `uv run --with pytest --with pyyaml pytest tests/test_glossary.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.zh_tw.glossary'`

- [ ] **Step 3: 實作**

`scripts/zh_tw/glossary.py`:

```python
"""台灣用語術語表的掃描與強制替換。

模型的中文訓練語料以簡體為主，繁化後詞彙仍是大陸慣用語（「繁體字、大陸詞」）。
prompt 指示不可靠，故翻譯後一律以程式碼掃描並替換。
"""

import json
import re
from collections import Counter
from pathlib import Path

_DEFAULT = Path(__file__).parent / "glossary.json"

# 保護區：fenced code block 與 inline code
_PROTECTED = re.compile(r"(```.*?```|`[^`\n]*`)", re.S)


def load(path: str | None = None) -> dict[str, str]:
    return json.loads(Path(path or _DEFAULT).read_text(encoding="utf-8"))


def _split_protected(body: str) -> list[tuple[bool, str]]:
    """回傳 (is_protected, segment) 序列。"""
    parts, last = [], 0
    for m in _PROTECTED.finditer(body):
        if m.start() > last:
            parts.append((False, body[last:m.start()]))
        parts.append((True, m.group(0)))
        last = m.end()
    if last < len(body):
        parts.append((False, body[last:]))
    return parts


def enforce(body: str, table: dict[str, str] | None = None) -> str:
    table = table or load()
    out = []
    for protected, seg in _split_protected(body):
        if not protected:
            for bad, good in table.items():
                seg = seg.replace(bad, good)
        out.append(seg)
    return "".join(out)


def scan(body: str, table: dict[str, str] | None = None) -> dict[str, int]:
    table = table or load()
    counts: Counter[str] = Counter()
    for protected, seg in _split_protected(body):
        if protected:
            continue
        for bad in table:
            n = seg.count(bad)
            if n:
                counts[bad] += n
    return dict(counts)


def prompt_rules(table: dict[str, str] | None = None) -> str:
    table = table or load()
    pairs = "、".join(f"{good}（不要用{bad}）" for bad, good in table.items())
    return (
        "使用台灣繁體中文的技術用語。務必遵守以下對照："
        f"{pairs}。程式碼與 inline code 中的識別字不要翻譯。"
    )
```

- [ ] **Step 4: 執行測試確認通過**

Run: `uv run --with pytest --with pyyaml pytest tests/test_glossary.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/zh_tw/glossary.py tests/test_glossary.py
git commit -m "feat(zh_tw): glossary scan and enforcement, code-aware"
```

---

### Task 6: 依 H2 切段（防截斷）

**Files:**
- Create: `scripts/zh_tw/chunking.py`
- Test: `tests/test_chunking.py`

**Interfaces:**
- Produces:
  - `chunk(body: str, max_lines: int = 250) -> list[str]`
  - `join(chunks: list[str]) -> str`

不變式：`join(chunk(x)) == x`（逐位元組）。這是 D2 靜默截斷的根本修法 —— `reference/variables.md` 824 行整檔送模型會超出輸出額度。

**切段必須遞迴。** 只切 H2 不夠：`english-main` 上有 5 個檔案，其單一 H2 章節本身就超過 250 行（`variables.md` 432 行、`macros.md` 327、`method-syntax.md` 313、`functions.md` 285、`structs.md` 251），全部含有 H3 可再切。任何仍超長的段落必須依序按 H3、H4… 再切，直到夠小或再也沒有標題可切；無法再切者原樣送出，不 raise。

- [ ] **Step 1: 寫失敗測試**

`tests/test_chunking.py`:

```python
from scripts.zh_tw import chunking


def test_join_chunk_round_trip_is_identity():
    body = "# T\n\nintro\n\n## A\n\naaa\n\n## B\n\nbbb\n"
    assert chunking.join(chunking.chunk(body, max_lines=2)) == body


def test_short_body_is_single_chunk():
    body = "# T\n\nshort\n"
    assert chunking.chunk(body, max_lines=250) == [body]


def test_splits_on_h2_boundaries():
    body = "# T\n\nintro\n\n## A\n\naaa\n\n## B\n\nbbb\n"
    chunks = chunking.chunk(body, max_lines=2)
    assert len(chunks) == 3
    assert chunks[1].startswith("## A")
    assert chunks[2].startswith("## B")


def test_does_not_split_inside_code_fence():
    body = "# T\n\n```move\n## not a heading\n```\n\n## Real\n\nx\n"
    chunks = chunking.chunk(body, max_lines=1)
    assert any("## not a heading" in c for c in chunks)
    assert sum(c.startswith("## Real") for c in chunks) == 1


def test_round_trip_on_body_with_trailing_newline():
    body = "## A\n\nx\n"
    assert chunking.join(chunking.chunk(body, max_lines=1)) == body
```

- [ ] **Step 2: 執行測試確認失敗**

Run: `uv run --with pytest --with pyyaml pytest tests/test_chunking.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.zh_tw.chunking'`

- [ ] **Step 3: 實作**

`scripts/zh_tw/chunking.py`:

```python
"""按 H2 語意邊界切段，避免整檔送模型時輸出 token 用盡而靜默截斷。

切段邊界一律取自 anchors.heading_lines()，不得自己掃 fence —— 見 Global Constraints。
"""

from . import anchors


def chunk(body: str, max_lines: int = 250) -> list[str]:
    lines = body.splitlines(keepends=True)
    if len(lines) <= max_lines:
        return [body]

    starts = [i for i, level in anchors.heading_lines(body) if level == 2]

    if not starts:
        return [body]

    bounds = [0, *starts, len(lines)]
    seen, out = set(), []
    for a, b in zip(bounds, bounds[1:]):
        if a == b or (a, b) in seen:
            continue
        seen.add((a, b))
        out.append("".join(lines[a:b]))
    return [c for c in out if c]


def join(chunks: list[str]) -> str:
    return "".join(chunks)
```

- [ ] **Step 4: 執行測試確認通過**

Run: `uv run --with pytest --with pyyaml pytest tests/test_chunking.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/zh_tw/chunking.py tests/test_chunking.py
git commit -m "feat(zh_tw): H2-boundary chunking to prevent silent truncation"
```

---

### Task 7: manifest（無 backend 依賴）

**Files:**
- Create: `scripts/zh_tw/manifest.py`
- Test: `tests/test_manifest.py`

**Interfaces:**
- Produces:
  - `blob_sha(ref: str, path: str) -> str | None`
  - `load() -> dict[str, str]` / `save(m: dict[str, str]) -> None`
  - `tracked_files(ref: str) -> list[str]`
  - `stale_files(ref: str = "english-main") -> list[str]`
  - `orphans(ref: str = "english-main") -> list[str]`
  - `record(m: dict, path: str, ref: str) -> None` — 從 git ref 讀 SHA，**絕不 `git hash-object` working tree**
  - `MANIFEST_PATH: Path`

**這個模組不得 import 任何 backend。** `--detect` 必須在沒有 `google-genai` 的環境下可執行。

- [ ] **Step 1: 寫失敗測試**

`tests/test_manifest.py`:

```python
import subprocess
import sys

from scripts.zh_tw import manifest


def test_module_does_not_import_any_backend():
    """D1 的結構性根除：detect 路徑不得觸及 google-genai。"""
    src = manifest.__file__
    code = open(src, encoding="utf-8").read()
    assert "genai" not in code
    assert "backends" not in code


def test_detect_runs_without_genai_installed():
    """在沒有 google-genai 的乾淨環境裡，stale_files 必須能跑。"""
    r = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.modules['google']=None;"
         "from scripts.zh_tw import manifest; print(len(manifest.load()))"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr


def test_blob_sha_reads_from_ref_not_worktree():
    sha = manifest.blob_sha("english-main", "book/404.md")
    assert sha and len(sha) == 40


def test_blob_sha_returns_none_for_missing_path():
    assert manifest.blob_sha("english-main", "nope/missing.md") is None


def test_orphans_finds_upstream_deleted_file():
    """D9: 上游在 #223 刪除了 transfer-restrictions.md。"""
    assert "book/storage/transfer-restrictions.md" in manifest.orphans("english-main")


def test_stale_files_is_nonempty_before_backfill():
    assert len(manifest.stale_files("english-main")) == 151
```

- [ ] **Step 2: 執行測試確認失敗**

Run: `uv run --with pytest --with pyyaml pytest tests/test_manifest.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.zh_tw.manifest'`

- [ ] **Step 3: 實作**

`scripts/zh_tw/manifest.py`:

```python
"""翻譯 manifest：路徑 -> 該中文檔賴以翻譯的英文 blob SHA。

本模組刻意不 import 任何翻譯後端。`--detect` 是純 git 操作，
在沒有 google-genai 的環境下必須可執行 —— 這是 CI 沉默五個月的根因。
"""

import json
import subprocess
from pathlib import Path

MANIFEST_PATH = Path("scripts/translation-manifest.json")
SIDEBAR_FILES = ("book/sidebar.yml", "reference/sidebar.yml")
DIRS = ("book", "reference")


def load() -> dict[str, str]:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {}


def save(m: dict[str, str]) -> None:
    MANIFEST_PATH.write_text(
        json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def blob_sha(ref: str, path: str) -> str | None:
    r = subprocess.run(
        ["git", "rev-parse", f"{ref}:{path}"], capture_output=True, text=True
    )
    return r.stdout.strip() if r.returncode == 0 else None


def tracked_files(ref: str) -> list[str]:
    r = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "-z", ref, *DIRS],
        capture_output=True, text=True, check=True,
    )
    return [
        f for f in r.stdout.split("\0")
        if f.endswith(".md") or f in SIDEBAR_FILES
    ]


def stale_files(ref: str = "english-main") -> list[str]:
    m = load()
    out = []
    for path in tracked_files(ref):
        sha = blob_sha(ref, path)
        if sha is not None and m.get(path) != sha:
            out.append(path)
    return out


def orphans(ref: str = "english-main") -> list[str]:
    """manifest 或 zh 分支有、但英文來源已刪除的路徑。"""
    present = set(tracked_files(ref))
    r = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "-z", "HEAD", *DIRS],
        capture_output=True, text=True, check=True,
    )
    zh = {f for f in r.stdout.split("\0") if f.endswith(".md")}
    return sorted((zh | set(load())) - present)


def record(m: dict[str, str], path: str, ref: str = "english-main") -> None:
    sha = blob_sha(ref, path)
    if sha is None:
        raise ValueError(f"{path} 不存在於 {ref}")
    m[path] = sha
```

- [ ] **Step 4: 執行測試確認通過**

Run: `uv run --with pytest --with pyyaml pytest tests/test_manifest.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/zh_tw/manifest.py tests/test_manifest.py
git commit -m "feat(zh_tw): backend-free manifest module with orphan detection"
```

---

### Task 8: validate（七道關卡）

**Files:**
- Create: `scripts/zh_tw/validate.py`
- Test: `tests/test_validate.py`

**Interfaces:**
- Consumes: `frontmatter.split`, `anchors.headings/existing_anchor`, `glossary.scan`
- Produces:
  - `ValidationError(Exception)`
  - `check_file(zh_text: str, en_text: str, prev_zh_text: str = "", prev_en_text: str = "") -> list[str]` — 回傳失敗訊息清單，空清單代表通過
  - `check_links(files: dict[str, str]) -> list[str]` — repo 級 anchor 連結解析

- [ ] **Step 1: 寫失敗測試**

`tests/test_validate.py`:

```python
from scripts.zh_tw import validate

EN = '---\ndescription: "Vectors in Move."\n---\n\n# Vector\n\n```move\nx\n```\n\n## Syntax\n\ntext\n'
ZH = '---\ndescription: "Move 中的向量。"\n---\n\n# 向量 {#vector}\n\n```move\nx\n```\n\n## 語法 {#syntax}\n\n文字\n'


def test_clean_file_passes():
    assert validate.check_file(ZH, EN) == []


def test_detects_truncation_via_heading_sequence():
    """reference/variables.md 的失效模式。"""
    truncated = '---\ndescription: "Move 中的向量。"\n---\n\n# 向量 {#vector}\n'
    errs = validate.check_file(truncated, EN)
    assert any("標題" in e for e in errs)


def test_detects_missing_code_fence():
    no_code = '---\ndescription: "Move 中的向量。"\n---\n\n# 向量 {#vector}\n\n## 語法 {#syntax}\n\n文字\n'
    errs = validate.check_file(no_code, EN)
    assert any("fence" in e or "程式碼" in e for e in errs)


def test_detects_untranslated_description():
    """D3：89 個檔案的 description 仍是英文。"""
    en_desc = ZH.replace("Move 中的向量。", "Vectors in Move.")
    errs = validate.check_file(en_desc, EN)
    assert any("description" in e for e in errs)


def test_detects_frontmatter_key_mismatch():
    en = '---\ndescription: "d"\nunlisted: true\n---\n\n# T\n'
    zh = '---\ndescription: "描述"\n---\n\n# 標 {#t}\n'
    errs = validate.check_file(zh, en)
    assert any("frontmatter" in e for e in errs)


def test_detects_dropped_existing_anchor():
    prev = '---\ndescription: "描述"\n---\n\n# 標 {#custom-id}\n'
    en = '---\ndescription: "d"\n---\n\n# T\n'
    zh = '---\ndescription: "描述"\n---\n\n# 標 {#t}\n'
    errs = validate.check_file(zh, en, prev)
    assert any("custom-id" in e for e in errs)


def test_detects_glossary_violation():
    en = '---\ndescription: "d"\n---\n\n# T\n'
    zh = '---\ndescription: "描述"\n---\n\n# 標 {#t}\n\n這個函數\n'
    errs = validate.check_file(zh, en)
    assert any("函數" in e for e in errs)


def test_check_links_resolves_internal_anchors():
    files = {
        "book/a.md": "# A {#a}\n\n[see](./b#target)\n",
        "book/b.md": "# B {#target}\n",
    }
    assert validate.check_links(files) == []


def test_check_links_reports_unresolvable_anchor():
    files = {"book/a.md": "# A {#a}\n\n[see](./b#missing)\n", "book/b.md": "# B {#target}\n"}
    errs = validate.check_links(files)
    assert len(errs) == 1 and "missing" in errs[0]


def test_check_links_strips_query_string():
    """book/move-basics/visibility.md 有一條 ?highlight=native 的連結。
    不剝掉 query string 就會產生假陽性。"""
    files = {
        "book/a.md": "# A {#a}\n\n[x](./b?highlight=native#target)\n",
        "book/b.md": "# B {#target}\n",
    }
    assert validate.check_links(files) == []


def test_check_links_ignores_external_urls():
    files = {"book/a.md": "# A {#a}\n\n[x](https://docs.suins.io/mvr-cli#installation)\n"}
    assert validate.check_links(files) == []
```

- [ ] **Step 2: 執行測試確認失敗**

Run: `uv run --with pytest --with pyyaml pytest tests/test_validate.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.zh_tw.validate'`

- [ ] **Step 3: 實作**

`scripts/zh_tw/validate.py`:

```python
"""寫檔前的守門員。任一條不過就不寫檔。

七道關卡對修復前的 HEAD 執行即會變紅（19 檔結構、89 檔 description），
無需另行製造缺陷來驗證守衛有效。
"""

import os
import re

from . import anchors, frontmatter, glossary

_CJK = re.compile(r"[一-鿿]")
_LINK = re.compile(r"\]\((?!https?:|mailto:)([^)#\s]*)#([A-Za-z0-9_-]+)\)")


class ValidationError(Exception):
    pass


def check_file(zh_text: str, en_text: str, prev_zh_text: str = "") -> list[str]:
    errs: list[str] = []
    zh_meta, zh_body = frontmatter.split(zh_text)
    en_meta, en_body = frontmatter.split(en_text)

    zh_h = anchors.headings(zh_body)
    en_h = anchors.headings(en_body)

    # 1. 標題層級序列
    if [lv for lv, _ in zh_h] != [lv for lv, _ in en_h]:
        errs.append(f"標題層級序列不符: 中文 {len(zh_h)} 個, 英文 {len(en_h)} 個")

    # 2. code fence 數量
    if anchors.fence_lines(zh_body) != anchors.fence_lines(en_body):
        errs.append(
            f"程式碼 fence 數不符: 中文 {anchors.fence_lines(zh_body)}, "
            f"英文 {anchors.fence_lines(en_body)}"
        )

    # 3. frontmatter key 集合
    if set(zh_meta) != set(en_meta):
        errs.append(f"frontmatter key 不符: {sorted(set(zh_meta))} vs {sorted(set(en_meta))}")

    # 4. 可翻譯欄位必須含 CJK
    for key in frontmatter.TRANSLATABLE_KEYS & set(zh_meta):
        value = zh_meta[key]
        if isinstance(value, str) and not _CJK.search(value):
            errs.append(f"frontmatter {key} 未翻譯: {value!r}")

    # 6. 既有 anchor 不得消失或改變
    if prev_zh_text:
        _, prev_body = frontmatter.split(prev_zh_text)
        prev_ids = {
            aid for _, t in anchors.headings(prev_body)
            if (aid := anchors.existing_anchor(t))
        }
        now_ids = {
            aid for _, t in zh_h if (aid := anchors.existing_anchor(t))
        }
        for lost in sorted(prev_ids - now_ids):
            errs.append(f"既有 anchor 消失: {{#{lost}}}")

    # 7. glossary
    for bad, n in sorted(glossary.scan(zh_body).items()):
        errs.append(f"違禁詞 {bad} 出現 {n} 次")

    return errs


def _anchor_ids(text: str) -> set[str]:
    _, body = frontmatter.split(text)
    hs = anchors.headings(body)
    explicit = {aid for _, t in hs if (aid := anchors.existing_anchor(t))}
    derived = set(anchors.slugify_all([t for _, t in hs]))
    return explicit | derived


def check_links(files: dict[str, str]) -> list[str]:
    """5. 所有內部 anchor 連結可解析。files: 路徑 -> 內容。"""
    index = {p: _anchor_ids(c) for p, c in files.items()}
    errs = []
    for path, content in files.items():
        _, body = frontmatter.split(content)
        for target, anchor in _LINK.findall(body):
            target = target.split("?")[0]  # 剝掉 ?highlight=native 這類 query string
            if target == "":
                tgt = path
            else:
                t = target.rstrip("/")
                if not t.endswith(".md"):
                    t += ".md"
                tgt = os.path.normpath(os.path.join(os.path.dirname(path), t))
            if tgt not in index:
                errs.append(f"{path}: 連結目標不存在 {target}#{anchor}")
            elif anchor not in index[tgt]:
                errs.append(f"{path}: anchor 無法解析 {target}#{anchor}")
    return errs
```

> `_LINK` 的 `[^)#\s]*` 允許 `?`，故 `./functions?highlight=native#native-functions` 的 target 會帶著 query string。不剝掉就會把 `book/move-basics/visibility.md` 誤判為斷鏈。實測：不剝掉 1 個假陽性，剝掉後 0 個。

- [ ] **Step 4: 執行測試確認通過**

Run: `uv run --with pytest --with pyyaml pytest tests/test_validate.py -v`
Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/zh_tw/validate.py tests/test_validate.py
git commit -m "feat(zh_tw): seven validation gates, raise before write"
```

---

### Task 9: 基線測試（把現存缺陷鎖成已知數字）

**Files:**
- Create: `tests/test_baseline.py`

**Interfaces:**
- Consumes: `validate.check_file`, `manifest.blob_sha`

這個測試的作用是證明守衛有效：對修復前的 HEAD 執行，第 1、2 條紅 15 檔、第 4 條紅 88 檔、第 7 條紅 126 處、第 8 條紅 4 檔 5 字。backfill 完成後改為斷言全綠（收尾 task）。

> 這三個數字是以本計畫的 `check_file` 邏輯實測得出，與 spec 中的 89 / 143 略有出入。spec 的 89 來自粗略 grep；143 含 code block 內的字。**以此處為準。**

**中文檔的英文來源是 merge-base，不是 `english-main`。** 拿 `english-main` 當來源會讓幾乎每個檔案都紅，19 這個數字就失去意義。

- [ ] **Step 1: 寫基線測試**

`tests/test_baseline.py`:

```python
"""對修復前的 repo 執行 validate，鎖定已知缺陷數量。

backfill 完成後，這個檔案由收尾 task 改寫為「全綠」斷言。

PRE_FIX 必須是固定 commit，不能用 zh-tw-main 分支名 —— PR 2 一合併，
分支上的缺陷數就變了，這個測試會因為「我們修好了東西」而變紅。
"""

import subprocess

import pytest

from scripts.zh_tw import validate

MERGE_BASE = "f2c0a93e1a0422078d3d051e4410ac3edc612016"
PRE_FIX = "0d4b8bea77f1a6195b589ded4067d287adb4379a"


def _show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def _zh_files() -> list[str]:
    r = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "-z", PRE_FIX, "book", "reference"],
        capture_output=True, text=True, check=True,
    )
    return [f for f in r.stdout.split("\0") if f.endswith(".md")]


@pytest.fixture(scope="module")
def failures() -> dict[str, list[str]]:
    out = {}
    for path in _zh_files():
        zh, en = _show(PRE_FIX, path), _show(MERGE_BASE, path)
        if zh is None or en is None:
            continue
        errs = validate.check_file(zh, en)
        if errs:
            out[path] = errs
    return out


def test_structural_failures_baseline(failures):
    """D2: 15 檔的標題序列或 fence 數與英文來源不符。

    19 是調查階段用有 bug 的 fence 掃描器算出來的。修正 parser 後為 15；
    移除的 4 個假陽性其英文原檔有被 HTML 註解掉的區塊。
    """
    structural = [
        p for p, errs in failures.items()
        if any("標題層級序列" in e or "fence" in e for e in errs)
    ]
    assert len(structural) == 15, sorted(structural)


def test_severe_truncation_is_present(failures):
    """最嚴重的兩個：英文 824 行 -> 中文 36 行。"""
    assert "reference/variables.md" in failures
    assert "book/guides/code-quality-checklist.md" in failures


def test_untranslated_description_baseline(failures):
    """D3: 88 檔的 frontmatter description 仍是英文。

    spec 記的 89 來自 `grep '^description:'` 的粗掃，多算了一個。
    88 是以 frontmatter.split + TRANSLATABLE_KEYS + CJK 實測的結果。
    """
    untranslated = [
        p for p, errs in failures.items()
        if any("未翻譯" in e for e in errs)
    ]
    assert len(untranslated) == 88, len(untranslated)


def test_glossary_violation_baseline():
    """D4: 程式碼區塊以外共 126 處大陸用語。

    spec 記的 143 是含 code block 的原始 grep 數。glossary.scan 會跳過
    fenced code 與 inline code，故以 126 為準 —— 這才是驗證關卡實際會擋的數量。
    """
    from scripts.zh_tw import glossary
    from scripts.zh_tw import frontmatter as fm

    total = 0
    for path in _zh_files():
        zh = _show(PRE_FIX, path)
        _, body = fm.split(zh)
        total += sum(glossary.scan(body).values())
    assert total == 126, total


def test_anchor_links_currently_resolve():
    """D5: 97 條內部 anchor 連結，現況全部可解析。重譯若洗掉 anchor，這裡會紅。

    需 check_links 剝掉 query string，否則 visibility.md 會有 1 個假陽性。
    """
    files = {p: _show(PRE_FIX, p) for p in _zh_files()}
    errs = validate.check_links(files)
    assert errs == [], errs
```

- [ ] **Step 2: 執行基線測試**

Run: `uv run --with pytest --with pyyaml pytest tests/test_baseline.py -v`
Expected: 5 passed

如果 `test_structural_failures_baseline` 的數字不是 19，**不要改測試去遷就實作** —— 先確認 `check_file` 的第 1、2 條邏輯是否與 spec 一致。這個數字來自對 repo 的實測。

- [ ] **Step 3: Commit**

```bash
git add tests/test_baseline.py
git commit -m "test: lock current translation defects as a measured baseline"
```

---

### Task 10: 翻譯後端

**Files:**
- Create: `scripts/zh_tw/backends/base.py`
- Create: `scripts/zh_tw/backends/fake.py`
- Create: `scripts/zh_tw/backends/claude_cli.py`
- Create: `scripts/zh_tw/backends/gemini.py`
- Test: `tests/test_backends.py`

**Interfaces:**
- Produces:
  - `base.Backend` — Protocol，`translate(self, text: str, *, kind: str = "markdown") -> str`
  - `base.get(name: str) -> Backend` — `"fake"` / `"claude"` / `"gemini"`
  - `base.SYSTEM_PROMPT: str`

- [ ] **Step 1: 寫失敗測試**

`tests/test_backends.py`:

```python
import pytest

from scripts.zh_tw.backends import base, fake


def test_fake_backend_is_deterministic():
    b = fake.FakeBackend()
    assert b.translate("hello") == b.translate("hello")


def test_fake_backend_preserves_structure():
    """fake 後端把英文標題換成假中文，但保留標題數與 fence 數，讓 pipeline 測試可用。"""
    b = fake.FakeBackend()
    out = b.translate("# Title\n\n```move\nx\n```\n\n## Sub\n")
    assert out.count("#") >= 3
    assert out.count("```") == 2


def test_get_resolves_fake():
    assert isinstance(base.get("fake"), fake.FakeBackend)


def test_get_rejects_unknown_backend():
    with pytest.raises(ValueError, match="unknown backend"):
        base.get("nope")


def test_system_prompt_embeds_glossary_rules():
    from scripts.zh_tw import glossary
    assert "函式" in base.SYSTEM_PROMPT
    assert "迴圈" in base.SYSTEM_PROMPT
```

- [ ] **Step 2: 執行測試確認失敗**

Run: `uv run --with pytest --with pyyaml pytest tests/test_backends.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.zh_tw.backends.base'`

- [ ] **Step 3: 實作 base 與 fake**

`scripts/zh_tw/backends/base.py`:

```python
"""翻譯後端介面。LLM 只在這一層出現。"""

from typing import Protocol

from .. import glossary

SYSTEM_PROMPT = (
    "你是專業的技術文件翻譯者。請將以下 Markdown 翻譯成台灣繁體中文。\n"
    "保留所有 Markdown 結構、連結、圖片與程式碼區塊。\n"
    "不要翻譯程式碼本身，但要翻譯程式碼區塊內的註解。\n"
    "不要增加或刪除任何標題，標題數量必須與原文完全相同。\n"
    "標題格式為「中文 (English)」，保留原文英文於括號內。\n"
    f"{glossary.prompt_rules()}\n"
    "只回傳翻譯後的 Markdown，不要任何解釋。"
)


class Backend(Protocol):
    def translate(self, text: str, *, kind: str = "markdown") -> str: ...


def get(name: str) -> Backend:
    if name == "fake":
        from .fake import FakeBackend
        return FakeBackend()
    if name == "claude":
        from .claude_cli import ClaudeCLIBackend
        return ClaudeCLIBackend()
    if name == "gemini":
        from .gemini import GeminiBackend
        return GeminiBackend()
    raise ValueError(f"unknown backend: {name}")
```

`scripts/zh_tw/backends/fake.py`:

```python
"""測試用後端。保留結構，把英文字母換成固定的中文字，不打任何 API。"""

import re


class FakeBackend:
    def translate(self, text: str, *, kind: str = "markdown") -> str:
        out, in_fence = [], False
        for line in text.splitlines(keepends=True):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                out.append(line)
                continue
            if in_fence:
                out.append(line)
                continue
            out.append(re.sub(r"[A-Za-z]{2,}", "中文", line))
        return "".join(out)
```

- [ ] **Step 4: 實作 claude_cli 與 gemini**

`scripts/zh_tw/backends/claude_cli.py`:

```python
"""本地後端：呼叫 headless 的 claude CLI。不需要 API key 環境變數。"""

import os
import subprocess

from .base import SYSTEM_PROMPT

MODEL = os.environ.get("ZH_TW_CLAUDE_MODEL", "haiku")
TIMEOUT = int(os.environ.get("ZH_TW_TIMEOUT", "600"))


class ClaudeCLIBackend:
    def translate(self, text: str, *, kind: str = "markdown") -> str:
        prompt = f"{SYSTEM_PROMPT}\n\n要翻譯的內容：\n\n{text}"
        r = subprocess.run(
            ["claude", "-p", "--model", MODEL, prompt],
            capture_output=True, text=True, timeout=TIMEOUT,
        )
        if r.returncode != 0:
            raise RuntimeError(f"claude CLI 失敗: {r.stderr[:400]}")
        out = r.stdout.strip()
        if not out:
            raise RuntimeError("claude CLI 回傳空字串")
        return out + "\n"
```

`scripts/zh_tw/backends/gemini.py`:

```python
"""CI 後端。import 延遲到建構時，讓 manifest/detect 不必安裝 google-genai。"""

import os
import time

from .base import SYSTEM_PROMPT

MODELS = ["gemini-2.5-flash"]
MAX_RETRIES = 3
RATE_LIMIT_WAIT = 60


class GeminiBackend:
    def __init__(self) -> None:
        from google import genai  # noqa: PLC0415 — 延遲 import 是刻意的

        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        self._client = genai.Client(api_key=key)

    def translate(self, text: str, *, kind: str = "markdown") -> str:
        msg = f"{SYSTEM_PROMPT}\n\n要翻譯的內容：\n\n{text}"
        last: Exception | None = None
        for model in MODELS:
            for attempt in range(MAX_RETRIES):
                try:
                    resp = self._client.models.generate_content(model=model, contents=msg)
                    if not resp.text:
                        raise RuntimeError("Gemini 回傳空字串（可能被安全過濾攔截）")
                    return resp.text
                except Exception as e:  # noqa: BLE001
                    last = e
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        time.sleep(RATE_LIMIT_WAIT)
                    else:
                        time.sleep(5)
        raise RuntimeError(f"所有模型皆失敗: {last}")
```

> `MODELS` 只留一個穩定版。實作前執行 `uv run --with google-genai python -c "from google import genai; import os; [print(m.name) for m in genai.Client(api_key=os.environ['GEMINI_API_KEY']).models.list()]"` 確認可用模型名稱，不要沿用原本的 `gemini-3.0-flash-preview` / `gemini-2.0-flash-exp`。

- [ ] **Step 5: 執行測試確認通過**

Run: `uv run --with pytest --with pyyaml pytest tests/test_backends.py -v`
Expected: 5 passed

- [ ] **Step 6: Commit**

```bash
git add scripts/zh_tw/backends/base.py scripts/zh_tw/backends/fake.py scripts/zh_tw/backends/claude_cli.py scripts/zh_tw/backends/gemini.py tests/test_backends.py
git commit -m "feat(zh_tw): pluggable translate backends (fake/claude/gemini)"
```

---

### Task 11: pipeline 編排與 CLI

**Files:**
- Create: `scripts/zh_tw/pipeline.py`
- Create: `scripts/zh_tw/__main__.py`
- Test: `tests/test_pipeline.py`

**Interfaces:**
- Consumes: 全部前述模組
- Produces:
  - `tier(path: str, en_ref: str = "english-main") -> str` — `"A"` 或 `"B"`
  - `translate_file(path, backend, en_ref="english-main") -> str` — 回傳新的中文全文，不寫檔
  - `run(paths: list[str], backend_name: str, en_ref: str, apply: bool) -> tuple[int, dict[str, list[str]]]`

`anchors.inject` 必須在 chunk 拼接**之後**對整份文件執行一次 —— 切段後每段的標題序列僅為全域序列的子區間。

- [ ] **Step 1: 寫失敗測試**

`tests/test_pipeline.py`:

```python
from scripts.zh_tw import pipeline
from scripts.zh_tw.backends.fake import FakeBackend

EN = '---\ndescription: "Vectors."\n---\n\n# Vector\n\nBody text here.\n\n## Syntax\n\nMore text.\n'
PREV_ZH = '---\ndescription: "向量。"\n---\n\n# 向量 {#vector}\n\n舊內文。\n\n## 語法 {#custom-syntax}\n\n舊文字。\n'


def test_translate_body_preserves_heading_count():
    out = pipeline.translate_body(EN, FakeBackend())
    from scripts.zh_tw import anchors, frontmatter
    _, body = frontmatter.split(out)
    assert len(anchors.headings(body)) == 2


def test_anchor_injection_runs_after_chunk_join():
    """切段後拼回，anchor 序號必須以全域序列為準。"""
    out = pipeline.assemble(EN, PREV_ZH, FakeBackend(), max_lines=1)
    assert "{#vector}" in out
    assert "{#custom-syntax}" in out  # 沿用，不是 {#syntax}


def test_glossary_enforced_on_output():
    en = '---\ndescription: "d"\n---\n\n# T\n'
    class BadBackend:
        def translate(self, text, *, kind="markdown"):
            return "# 標題\n\n這個函數會返回值\n"
    out = pipeline.assemble(en, "", BadBackend())
    assert "函式" in out and "回傳" in out
    assert "函數" not in out


def test_assemble_raises_when_backend_truncates():
    en = '---\ndescription: "d"\n---\n\n# One\n\n## Two\n\n## Three\n'
    class TruncatingBackend:
        def translate(self, text, *, kind="markdown"):
            return "# 一\n"
    import pytest
    with pytest.raises(Exception):
        pipeline.assemble(en, "", TruncatingBackend())


def test_tier_a_for_frontmatter_only_delta():
    """book/404.md：上游只加了 frontmatter，中英文標題數相符 -> A 層。"""
    assert pipeline.tier("book/404.md") == "A"


def test_tier_b_when_structure_fails_even_if_delta_is_small():
    """reference/variables.md：上游只動 frontmatter，但中文只有 36 行 / 6 個標題
    （英文 824 行 / 21 個標題）。結構驗證擋下，強制降級 B 層全譯。
    這是分層閘門存在的理由 —— 純看 delta 大小會讓那 788 行永遠回不來。"""
    assert pipeline.tier("reference/variables.md") == "B"
```

- [ ] **Step 2: 執行測試確認失敗**

Run: `uv run --with pytest --with pyyaml pytest tests/test_pipeline.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.zh_tw.pipeline'`

- [ ] **Step 3: 實作**

`scripts/zh_tw/pipeline.py`:

```python
"""編排：分層 -> 翻譯 -> 注入 anchor -> 強制術語 -> 驗證 -> 寫檔。

驗證失敗一律 raise，絕不寫檔。
"""

import subprocess
from pathlib import Path

from . import anchors, chunking, frontmatter, glossary, manifest, validate
from .backends import base

MERGE_BASE = "f2c0a93e1a0422078d3d051e4410ac3edc612016"
FRONTMATTER_ONLY_DELTA = 6
CHUNK_MAX_LINES = 250


def _show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def _prev_en(path: str, m: dict[str, str]) -> str:
    """取回這個中文檔當初賴以翻譯的英文原檔內容。

    manifest 記的是英文 blob SHA。31 筆 provenance 曾經斷掉（Task 13 修復）；
    仍然取不到時退回 merge-base 的同路徑內容。兩者皆失敗則回傳空字串，
    inject 會因此不沿用任何 anchor —— 這是安全的降級，位置猜測不是。
    """
    sha = m.get(path)
    if sha:
        r = subprocess.run(["git", "cat-file", "-p", sha], capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout
    return _show(MERGE_BASE, path) or ""


def _delta_lines(old_sha: str, new_sha: str) -> int:
    r = subprocess.run(
        ["git", "diff", "--numstat", old_sha, new_sha], capture_output=True, text=True
    )
    parts = r.stdout.split()
    return int(parts[0]) + int(parts[1]) if len(parts) >= 2 else 10_000


def tier(path: str, en_ref: str = "english-main") -> str:
    """A 層的前提是中文內文與其英文來源結構一致；不通過者強制降級 B 層。"""
    m = manifest.load()
    new_sha = manifest.blob_sha(en_ref, path)
    old_sha = m.get(path)
    zh = _show("HEAD", path)
    if zh is None or new_sha is None or old_sha is None:
        return "B"

    # provenance 損壞（blob 不在 repo）→ 以 merge-base 為代理
    if subprocess.run(["git", "cat-file", "-e", old_sha], capture_output=True).returncode:
        old_sha = manifest.blob_sha(MERGE_BASE, path)
        if old_sha is None:
            return "B"

    if _delta_lines(old_sha, new_sha) > FRONTMATTER_ONLY_DELTA:
        return "B"

    en_old = _show(MERGE_BASE, path)
    if en_old is None or validate.check_file(zh, en_old):
        return "B"  # 結構驗證未過（例：reference/variables.md）
    return "A"


def translate_body(en_text: str, backend: base.Backend, max_lines: int = CHUNK_MAX_LINES) -> str:
    en_meta, en_body = frontmatter.split(en_text)
    zh_chunks = [backend.translate(c) for c in chunking.chunk(en_body, max_lines)]
    zh_body = chunking.join(zh_chunks)

    zh_meta = dict(en_meta)
    for key in frontmatter.TRANSLATABLE_KEYS & set(en_meta):
        if isinstance(en_meta[key], str):
            zh_meta[key] = backend.translate(en_meta[key], kind="text").strip()
    return frontmatter.join(zh_meta, zh_body)


def assemble(
    en_text: str,
    prev_zh_text: str,
    prev_en_text: str,
    backend: base.Backend,
    max_lines: int = CHUNK_MAX_LINES,
) -> str:
    """prev_en_text 是這個中文檔當初翻譯所依據的英文原檔。

    沒有它，anchors.inject 只能退回「不沿用任何 anchor」；**絕不可**退回位置配對。
    上游 #223 改動了 19/35 個含 anchor 檔案的標題序列，位置配對會把 anchor 靜默
    貼到錯誤的標題上，而 gate 6 的集合差看不出來（spec D10）。
    """
    translated = translate_body(en_text, backend, max_lines)
    zh_meta, zh_body = frontmatter.split(translated)
    _, en_body = frontmatter.split(en_text)
    _, prev_zh_body = frontmatter.split(prev_zh_text) if prev_zh_text else ({}, "")
    _, prev_en_body = frontmatter.split(prev_en_text) if prev_en_text else ({}, "")

    # 拼接完成後才注入 anchor：切段後每段的標題序列只是全域序列的子區間。
    zh_body, notes = anchors.inject_report(zh_body, en_body, prev_zh_body, prev_en_body)
    zh_body = glossary.enforce(zh_body)
    out = frontmatter.join(zh_meta, zh_body)

    errs = validate.check_file(out, en_text, prev_zh_text, prev_en_text)
    if errs:
        raise validate.ValidationError("; ".join(errs))
    for n in notes:
        print(f"  note: {n}")  # anchor 退役等資訊，警告但不阻斷
    return out


def rebuild_frontmatter_only(en_text: str, zh_text: str, backend: base.Backend) -> str:
    """A 層：內文原封不動，只接管上游 frontmatter。"""
    en_meta, _ = frontmatter.split(en_text)
    _, zh_body = frontmatter.split(zh_text)
    zh_meta = dict(en_meta)
    for key in frontmatter.TRANSLATABLE_KEYS & set(en_meta):
        if isinstance(en_meta[key], str):
            zh_meta[key] = backend.translate(en_meta[key], kind="text").strip()
    out = frontmatter.join(zh_meta, zh_body)
    errs = validate.check_file(out, en_text)
    if errs:
        raise validate.ValidationError("; ".join(errs))
    return out


def run(
    paths: list[str], backend_name: str, en_ref: str = "english-main", apply: bool = False
) -> tuple[int, dict[str, list[str]]]:
    backend = base.get(backend_name)
    m = manifest.load()
    ok, failed = 0, {}

    for path in paths:
        en = _show(en_ref, path)
        if en is None:
            failed[path] = [f"{path} 不存在於 {en_ref}"]
            continue
        prev = _show("HEAD", path) or ""
        try:
            if prev and tier(path, en_ref) == "A":
                out = rebuild_frontmatter_only(en, prev, backend)
            else:
                out = assemble(en, prev, backend)
        except Exception as e:  # noqa: BLE001
            failed[path] = [str(e)]
            continue

        if apply:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(out, encoding="utf-8")
            manifest.record(m, path, en_ref)
        ok += 1

    if apply:
        manifest.save(m)
    return ok, failed
```

`scripts/zh_tw/__main__.py`:

```python
import argparse
import sys

from . import manifest, pipeline


def main() -> int:
    p = argparse.ArgumentParser(prog="python -m scripts.zh_tw")
    p.add_argument("--detect", action="store_true", help="列出需要翻譯的檔案（純 git，無 API 依賴）")
    p.add_argument("--orphans", action="store_true", help="列出上游已刪除的檔案")
    p.add_argument("--english-ref", default="english-main")
    p.add_argument("--backend", default="claude", choices=["fake", "claude", "gemini"])
    p.add_argument("--apply", action="store_true", help="實際寫檔（預設 dry-run）")
    p.add_argument("--limit", type=int, default=0, help="只處理前 N 個檔案，0 為不限")
    p.add_argument("files", nargs="*")
    a = p.parse_args()

    if a.detect:
        for f in manifest.stale_files(a.english_ref):
            print(f)
        return 0
    if a.orphans:
        for f in manifest.orphans(a.english_ref):
            print(f)
        return 0

    paths = a.files or manifest.stale_files(a.english_ref)
    if a.limit:
        paths = paths[: a.limit]
    if not paths:
        print("沒有需要翻譯的檔案。")
        return 0

    ok, failed = pipeline.run(paths, a.backend, a.english_ref, a.apply)
    print(f"成功 {ok}，失敗 {len(failed)}")
    for path, errs in failed.items():
        print(f"  {path}: {'; '.join(errs)}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 執行測試確認通過**

Run: `uv run --with pytest --with pyyaml pytest tests/test_pipeline.py -v`
Expected: 5 passed

- [ ] **Step 5: 確認 detect 在無 genai 環境可執行**

Run: `uv run --with pyyaml python -m scripts.zh_tw --detect | wc -l`
Expected: `151`（且**不得**出現 `ModuleNotFoundError`）

這一步直接證明 D1 的根因已被結構性根除。

- [ ] **Step 6: 全套測試**

Run: `uv run --with pytest --with pyyaml pytest tests/ -v`
Expected: 全部 passed

- [ ] **Step 7: Commit**

```bash
git add scripts/zh_tw/pipeline.py scripts/zh_tw/__main__.py tests/test_pipeline.py
git commit -m "feat(zh_tw): pipeline orchestration and CLI"
```

---

### Task 12: prettier 設定與 repo 級檢查

**Files:**
- Modify: `.prettierrc`
- Create: `scripts/zh_tw/check_repo.py`
- Test: `tests/test_check_repo.py`

**Interfaces:**
- Produces: `check_repo.main() -> int` — 對 working tree 執行 `check_links` 與 glossary 掃描

`proseWrap: "always"` 是為英文設計。CJK 無詞間空格，prettier 只能在標點或 inline code 邊界折行；實測 `vector.md` 改動 20/49 行、`control-flow.md` 改動 55/140 行。

- [ ] **Step 1: 修改 .prettierrc**

```json
{
  "tabWidth": 2,
  "useTabs": false,
  "printWidth": 100,
  "semi": true,
  "singleQuote": true,
  "trailingComma": "all",
  "proseWrap": "always",
  "overrides": [
    { "files": "**/*.md", "options": { "proseWrap": "preserve" } }
  ]
}
```

- [ ] **Step 2: 確認 prettier 對中文檔成為 no-op**

Run: `npx --yes prettier@3 --check 'book/**/*.md' 'reference/**/*.md'`
Expected: `All matched files use Prettier code style!`

實測（HEAD 5add39b2）：現況 143 檔 prettier 不合規；`frontmatter.join` 的 YAML 規範化會在 backfill 時自動修好 93 檔（143→50）；剩 50 檔是兩個純機械問題 —— 清單標記 `-   `（三空格）→ `- `（一空格）、檔尾缺換行，prettier 修得乾淨、不折斷中文句子。

**這次 `prettier --write` 不在 Task 12 執行**（它會改動 50 個內容檔）。依人工裁決，併入 **PR 2（A 層）**：PR 2 本就只改 frontmatter、不碰譯文內文，把這 50 檔的清單標記與檔尾換行一併正規化，同屬「非譯文內容的機械格式改動」，diff 完全可預測。PR 2 的驗收改為：`npx prettier@3 --check` 對 A 層涉及的檔案通過。

- [ ] **Step 3: 寫 repo 級檢查**

`scripts/zh_tw/check_repo.py`:

```python
"""對 working tree 執行 repo 級驗證：anchor 連結解析、glossary 違禁詞。"""

import sys
from pathlib import Path

from . import frontmatter, glossary, validate


def collect() -> dict[str, str]:
    files = {}
    for root in ("book", "reference"):
        for p in Path(root).rglob("*.md"):
            files[str(p)] = p.read_text(encoding="utf-8")
    return files


def main() -> int:
    files = collect()
    errs = validate.check_links(files)

    total = 0
    for path, text in files.items():
        _, body = frontmatter.split(text)
        for bad, n in glossary.scan(body).items():
            errs.append(f"{path}: 違禁詞 {bad} x{n}")
            total += n

    for e in errs:
        print(e, file=sys.stderr)
    print(f"連結與術語檢查：{len(errs)} 個問題，違禁詞共 {total} 處")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 寫測試**

`tests/test_check_repo.py`:

```python
from scripts.zh_tw import check_repo


def test_collect_finds_book_and_reference():
    files = check_repo.collect()
    assert "book/404.md" in files
    assert any(p.startswith("reference/") for p in files)
    assert len(files) >= 143
```

- [ ] **Step 5: 執行**

Run: `uv run --with pytest --with pyyaml pytest tests/test_check_repo.py -v`
Expected: 1 passed

Run: `uv run --with pyyaml python -m scripts.zh_tw.check_repo`
Expected: 回報 143 處違禁詞、0 個連結問題，exit 1

- [ ] **Step 6: Commit**

```bash
git add .prettierrc scripts/zh_tw/check_repo.py tests/test_check_repo.py
git commit -m "feat(zh_tw): repo-level link/glossary check; disable proseWrap for CJK markdown"
```

---

### Task 13: manifest provenance 修復

**Files:**
- Create: `scripts/zh_tw/heal_manifest.py`
- Test: `tests/test_heal_manifest.py`
- Modify: `scripts/translation-manifest.json`

**Interfaces:**
- Produces: `heal_manifest.heal(dry_run: bool = True) -> tuple[list[str], list[str]]` — `(healed, unrecoverable)`

31 筆 manifest 指向不存在於 repo 的 blob。用結構指紋（標題層級序列 + fence 數）比對，其中 28 筆的中文內文與 merge-base 英文一致，可安全回填為 merge-base blob SHA；餘 3 筆結構不符，留給 backfill 全譯。

- [ ] **Step 1: 寫失敗測試**

`tests/test_heal_manifest.py`:

```python
from scripts.zh_tw import heal_manifest


def test_heal_dry_run_reports_28_healable():
    healed, unrecoverable = heal_manifest.heal(dry_run=True)
    assert len(healed) == 28
    assert len(unrecoverable) == 3


def test_heal_dry_run_does_not_write():
    import json
    from scripts.zh_tw import manifest
    before = json.dumps(manifest.load(), sort_keys=True)
    heal_manifest.heal(dry_run=True)
    assert json.dumps(manifest.load(), sort_keys=True) == before
```

- [ ] **Step 2: 執行測試確認失敗**

Run: `uv run --with pytest --with pyyaml pytest tests/test_heal_manifest.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.zh_tw.heal_manifest'`

- [ ] **Step 3: 實作**

`scripts/zh_tw/heal_manifest.py`:

```python
"""修復 provenance 損壞的 manifest 條目。

31 筆指向不存在的 blob。以結構指紋確認中文內文確實對應 merge-base 的英文，
再回填 merge-base 的 blob SHA。指紋不符者不動，留給 backfill 全譯。
"""

import subprocess
import sys

from . import anchors, frontmatter, manifest

MERGE_BASE = "f2c0a93e1a0422078d3d051e4410ac3edc612016"


def _show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def _fingerprint(text: str) -> tuple[tuple[int, ...], int]:
    _, body = frontmatter.split(text)
    return tuple(lv for lv, _ in anchors.headings(body)), anchors.fence_lines(body)


def heal(dry_run: bool = True) -> tuple[list[str], list[str]]:
    m = manifest.load()
    healed, unrecoverable = [], []

    for path, sha in list(m.items()):
        if not subprocess.run(["git", "cat-file", "-e", sha], capture_output=True).returncode:
            continue  # blob 存在，provenance 完好
        en_base, zh = _show(MERGE_BASE, path), _show("HEAD", path)
        base_sha = manifest.blob_sha(MERGE_BASE, path)
        if not (en_base and zh and base_sha):
            unrecoverable.append(path)
            continue
        if _fingerprint(en_base) == _fingerprint(zh):
            healed.append(path)
            if not dry_run:
                m[path] = base_sha
        else:
            unrecoverable.append(path)

    if not dry_run:
        manifest.save(m)
    return healed, unrecoverable


def main() -> int:
    healed, bad = heal(dry_run="--apply" not in sys.argv)
    print(f"可修復 {len(healed)}，無法修復 {len(bad)}")
    for p in bad:
        print(f"  結構不符，留給全譯: {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 執行測試確認通過**

Run: `uv run --with pytest --with pyyaml pytest tests/test_heal_manifest.py -v`
Expected: 2 passed

- [ ] **Step 5: 實際套用**

Run: `uv run --with pyyaml python -m scripts.zh_tw.heal_manifest --apply`
Expected: `可修復 28，無法修復 3`

- [ ] **Step 6: 確認 detect 數量不變**

Run: `uv run --with pyyaml python -m scripts.zh_tw --detect | wc -l`
Expected: `151`

修復 provenance 不改變工作清單（那 28 檔本來就過期），只是讓分層能正確判斷。

- [ ] **Step 7: Commit**

```bash
git add scripts/zh_tw/heal_manifest.py tests/test_heal_manifest.py scripts/translation-manifest.json
git commit -m "fix(zh_tw): heal 28 manifest entries with broken provenance"
```

---

### Task 14: sidebar.yml 標籤翻譯

**Files:**
- Create: `scripts/zh_tw/sidebar.py`
- Modify: `scripts/zh_tw/pipeline.py`
- Test: `tests/test_sidebar.py`

**Interfaces:**
- Consumes: `backends.base.Backend`
- Produces:
  - `labels(text: str) -> list[str]`
  - `apply(en_text: str, translated: list[str]) -> str`
  - `skeleton(text: str) -> str` — 把所有 `label:` 的值換成 `<L>`，用於結構比對
  - `translate(en_text: str, prev_zh_text: str, backend: Backend) -> str`
  - `SIDEBAR_PROMPT: str`

`--detect` 回傳的 151 個路徑包含 `book/sidebar.yml` 與 `reference/sidebar.yml`。它們不是 markdown：`pipeline.assemble` 會把整份 YAML 當 body 丟給 LLM，毀掉結構，而 markdown 的驗證關卡對 YAML 幾乎攔不住（標題數 0 == 0、fence 數 0 == 0）。必須分流。

**核心不變式**：除了 `label:` 的值，中文 sidebar 的每一行都必須與英文檔逐位元組相同。結構（`id`、`type`、`items`、縮排、註解）完全來自上游。

- [ ] **Step 1: 寫失敗測試**

`tests/test_sidebar.py`:

```python
import pytest

from scripts.zh_tw import sidebar

EN = """# comment
bookSidebar:
  - label: The Move Book
    id: index
  - type: category
    label: Before We Begin
    items:
      - label: Install Sui
        id: before-we-begin/install-sui
"""

PREV_ZH = """# comment
bookSidebar:
  - label: Move 寶典 (The Move Book)
    id: index
  - type: category
    label: 開始之前 (Before We Begin)
    items:
      - label: 安裝 Sui (Install Sui)
        id: before-we-begin/install-sui
"""


class EchoBackend:
    def translate(self, text, *, kind="markdown"):
        return "\n".join(f"{i + 1}. 譯{line.split('. ', 1)[1]}"
                         for i, line in enumerate(text.strip().splitlines()))


def test_labels_extracts_in_order():
    assert sidebar.labels(EN) == ["The Move Book", "Before We Begin", "Install Sui"]


def test_skeleton_masks_label_values():
    assert sidebar.skeleton(EN) == sidebar.skeleton(PREV_ZH)


def test_apply_replaces_labels_preserving_structure():
    out = sidebar.apply(EN, ["甲", "乙", "丙"])
    assert sidebar.labels(out) == ["甲", "乙", "丙"]
    assert sidebar.skeleton(out) == sidebar.skeleton(EN)
    assert "id: before-we-begin/install-sui" in out


def test_apply_quotes_labels_with_yaml_special_chars():
    out = sidebar.apply("a:\n  - label: X\n", ["模組: 進階"])
    assert "label: '模組: 進階'" in out


def test_apply_raises_on_count_mismatch():
    with pytest.raises(ValueError):
        sidebar.apply(EN, ["只有一個"])


def test_translate_carries_forward_existing_labels():
    """英文 label 未變的項目，直接沿用舊譯文，不重新翻譯。"""
    out = sidebar.translate(EN, PREV_ZH, EchoBackend())
    assert out == PREV_ZH


def test_translate_only_calls_backend_for_new_labels():
    en_plus = EN + "  - label: Brand New\n    id: new\n"
    out = sidebar.translate(en_plus, PREV_ZH, EchoBackend())
    assert "Move 寶典 (The Move Book)" in out       # 舊的沿用
    assert "譯Brand New" in out                      # 新的才翻
    assert sidebar.skeleton(out) == sidebar.skeleton(en_plus)
```

- [ ] **Step 2: 執行測試確認失敗**

Run: `uv run --with pytest --with pyyaml pytest tests/test_sidebar.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.zh_tw.sidebar'`

- [ ] **Step 3: 實作**

`scripts/zh_tw/sidebar.py`:

```python
"""sidebar.yml 的 label 翻譯。

只有 label 的值需要翻譯；其餘每一行都必須與英文檔逐位元組相同。
慣例格式為「繁體中文 (Original English)」。
"""

import re

from .backends.base import Backend

_LABEL = re.compile(r"^(\s*-?\s*label:\s*)(.+)$", re.M)
_YAML_SPECIAL = ":{}[],'\"&*?|>!%@`#"

SIDEBAR_PROMPT = (
    "你是專業的技術文件翻譯者。\n"
    "請將以下側邊欄標籤翻譯成台灣繁體中文。\n"
    "格式一律為「繁體中文翻譯 (Original English)」。\n"
    "使用台灣用語：套件（不是包）、函式（不是函數）、模組（不是模塊）。\n"
    "若標籤是專有名詞或縮寫（例如 BCS、Move 2024），保持原樣不譯。\n"
    "輸入為每行一個編號標籤，請以相同的編號格式回傳。\n"
    "只回傳編號後的翻譯結果，不要任何解釋。"
)


def _unquote(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        return v[1:-1]
    return v


def labels(text: str) -> list[str]:
    return [_unquote(m.group(2)) for m in _LABEL.finditer(text)]


def skeleton(text: str) -> str:
    """把 label 的值換成 <L>，用於證明結構未被更動。"""
    return _LABEL.sub(lambda m: f"{m.group(1)}<L>", text)


def _quote(v: str) -> str:
    return f"'{v}'" if any(c in v for c in _YAML_SPECIAL) else v


def apply(text: str, translated: list[str]) -> str:
    matches = list(_LABEL.finditer(text))
    if len(matches) != len(translated):
        raise ValueError(f"label 數不符: 檔案 {len(matches)}, 譯文 {len(translated)}")
    out, last = [], 0
    for m, new in zip(matches, translated):
        out.append(text[last:m.start()])
        out.append(m.group(1) + _quote(new))
        last = m.end()
    out.append(text[last:])
    return "".join(out)


def _parse_numbered(raw: str, n: int) -> list[str]:
    got: dict[int, str] = {}
    for line in raw.strip().splitlines():
        m = re.match(r"^\s*(\d+)[.)]\s*(.+?)\s*$", line)
        if m:
            got[int(m.group(1))] = m.group(2)
    missing = [i for i in range(1, n + 1) if i not in got]
    if missing:
        raise ValueError(f"翻譯結果缺少編號: {missing}")
    return [got[i] for i in range(1, n + 1)]


def translate(en_text: str, prev_zh_text: str, backend: Backend) -> str:
    en_labels = labels(en_text)

    # 沿用：英文 label 未變者，直接用舊譯文
    carried: dict[str, str] = {}
    if prev_zh_text and skeleton(prev_zh_text) == skeleton(en_text):
        for en_l, zh_l in zip(en_labels, labels(prev_zh_text)):
            carried[en_l] = zh_l
    elif prev_zh_text:
        for zh_l in labels(prev_zh_text):
            m = re.search(r"\(([^)]+)\)\s*$", zh_l)
            if m:
                carried[m.group(1)] = zh_l

    todo = [l for l in en_labels if l not in carried]
    if todo:
        numbered = "\n".join(f"{i + 1}. {l}" for i, l in enumerate(todo))
        raw = backend.translate(f"{SIDEBAR_PROMPT}\n\n{numbered}", kind="text")
        for src, dst in zip(todo, _parse_numbered(raw, len(todo))):
            carried[src] = dst

    out = apply(en_text, [carried[l] for l in en_labels])
    if skeleton(out) != skeleton(en_text):
        raise ValueError("sidebar 結構被更動")
    return out
```

- [ ] **Step 4: 執行測試確認通過**

Run: `uv run --with pytest --with pyyaml pytest tests/test_sidebar.py -v`
Expected: 7 passed

- [ ] **Step 5: 讓 pipeline 分流 sidebar**

在 `scripts/zh_tw/pipeline.py` 的 import 區加入 `from . import sidebar`，並把 `run()` 中的 try 區塊改為：

```python
        prev_en = _prev_en(path, m)
        try:
            if path in manifest.SIDEBAR_FILES:
                out = sidebar.translate(en, prev, backend)
            elif prev and tier(path, en_ref) == "A":
                out = rebuild_frontmatter_only(en, prev, backend)
            else:
                out = assemble(en, prev, prev_en, backend)
        except Exception as e:  # noqa: BLE001
            failed[path] = [str(e)]
            continue
```

- [ ] **Step 6: 加一條 pipeline 分流測試**

追加到 `tests/test_pipeline.py`:

```python
def test_run_routes_sidebar_to_sidebar_module(monkeypatch, tmp_path):
    """sidebar.yml 不得走 markdown 路徑，否則整份 YAML 會被當內文翻譯。"""
    from scripts.zh_tw import pipeline

    called = []
    monkeypatch.setattr(
        pipeline.sidebar, "translate",
        lambda en, prev, backend: called.append("sidebar") or "ok\n",
    )
    monkeypatch.setattr(pipeline, "_show", lambda ref, path: "bookSidebar:\n  - label: X\n")
    ok, failed = pipeline.run(["book/sidebar.yml"], "fake", apply=False)
    assert called == ["sidebar"]
    assert ok == 1 and failed == {}
```

- [ ] **Step 7: 執行全套測試**

Run: `uv run --with pytest --with pyyaml pytest tests/ -v`
Expected: 全部 passed

- [ ] **Step 8: Commit**

```bash
git add scripts/zh_tw/sidebar.py scripts/zh_tw/pipeline.py tests/test_sidebar.py tests/test_pipeline.py
git commit -m "feat(zh_tw): sidebar.yml label translation with structural skeleton guard"
```

---

### Task 15: 汰換舊腳本

**Files:**
- Delete: `scripts/translate_to_zh_tw.py`
- Test: `tests/test_no_legacy_script.py`

舊腳本的三個致命設計已由新模組取代：top-level `genai` import（D1）、`git_hash_object` 讀 working tree（D8）、先 `write_text` 再處理例外（D2）。

- [ ] **Step 1: 確認新 CLI 涵蓋舊腳本的全部用途**

Run: `uv run --with pyyaml python -m scripts.zh_tw --detect | head -3`
Expected: 三個檔案路徑

Run: `uv run --with pyyaml python -m scripts.zh_tw --orphans`
Expected: `book/storage/transfer-restrictions.md`

- [ ] **Step 2: 寫防迴歸測試**

`tests/test_no_legacy_script.py`:

```python
from pathlib import Path


def test_legacy_script_is_gone():
    """舊腳本的 top-level genai import 是 CI 沉默五個月的根因。"""
    assert not Path("scripts/translate_to_zh_tw.py").exists()
```

- [ ] **Step 3: 刪除並執行測試**

```bash
git rm scripts/translate_to_zh_tw.py
uv run --with pytest --with pyyaml pytest tests/test_no_legacy_script.py -v
```
Expected: 1 passed

- [ ] **Step 4: Commit（PR 0 到此結束）**

```bash
git add tests/test_no_legacy_script.py
git commit -m "refactor: remove legacy translate_to_zh_tw.py, superseded by scripts/zh_tw"
```

- [ ] **Step 5: 開 PR 0**

```bash
git push -u origin design/zh-tw-sync-pipeline
gh pr create -R first-mover-tw/move-book-zh-tw --base zh-tw-main \
  --title "PR 0: rebuild zh-TW translation pipeline (no content changes)" \
  --body "見 docs/superpowers/specs/2026-07-10-zh-tw-upstream-sync-design.md。本 PR 不含任何譯文改動。"
```

---

### Task 16: 修復 CI workflow（PR 1）

**Files:**
- Modify: `.github/workflows/translate-zh-tw.yml`

**根因（已由 run 28997766485 的 log 證實）**：`Detect` 排在 `Install dependencies` 之前，`ModuleNotFoundError` 被 `2>/dev/null` 與 `|| true` 吞掉，`COUNT=0`，後續步驟全部 skip，job 綠燈。

- [ ] **Step 1: 建立分支**

```bash
git checkout zh-tw-main && git pull --ff-only
git checkout -b fix/ci-translate-workflow
```

- [ ] **Step 2: 改寫 workflow**

`.github/workflows/translate-zh-tw.yml`:

```yaml
name: Translate docs to zh-TW

permissions:
  contents: write
  pull-requests: write

on:
  push:
    branches: [english-main]
  schedule:
    - cron: "0 2 * * *"
  workflow_dispatch:

env:
  BATCH_SIZE: "5"

jobs:
  translate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout zh-tw-main
        uses: actions/checkout@v4
        with:
          ref: zh-tw-main
          fetch-depth: 0

      - name: Fetch english-main
        run: git fetch origin english-main

      # Setup 必須在 Detect 之前。這個順序是 D1 的根因。
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install dependencies
        run: pip install pyyaml markdown-it-py opencc-python-reimplemented google-genai

      - name: Detect files needing translation
        id: detect
        run: |
          set -euo pipefail   # detect 失敗必須讓 job 紅，不得靜默回傳 0
          python -m scripts.zh_tw --detect --english-ref origin/english-main \
            | head -n "$BATCH_SIZE" > /tmp/changed_files.txt
          COUNT=$(wc -l < /tmp/changed_files.txt | tr -d ' ')
          echo "count=$COUNT" >> "$GITHUB_OUTPUT"
          echo "將翻譯 $COUNT 個檔案:"
          cat /tmp/changed_files.txt

      - name: Skip if no changes
        if: steps.detect.outputs.count == '0'
        run: echo "沒有過期檔案，跳過。"

      - name: Translate
        if: steps.detect.outputs.count != '0'
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          PYTHONUNBUFFERED: "1"
        run: |
          set -euo pipefail
          xargs -a /tmp/changed_files.txt \
            python -m scripts.zh_tw --backend gemini \
              --english-ref origin/english-main --apply

      - name: Validate before commit
        if: steps.detect.outputs.count != '0'
        run: |
          set -euo pipefail
          python -m scripts.zh_tw.check_repo

      - name: Commit and push
        if: steps.detect.outputs.count != '0'
        run: |
          set -euo pipefail
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          BRANCH="auto/zh-tw-${{ github.run_id }}"
          git checkout -b "$BRANCH"
          git add scripts/translation-manifest.json
          xargs -a /tmp/changed_files.txt git add --
          git diff --cached --quiet && echo "無變更" && exit 0
          git commit -m "Auto update zh-TW translations (Gemini)"
          git push origin "$BRANCH"
          echo "BRANCH=$BRANCH" >> "$GITHUB_ENV"

      - name: Open PR into zh-tw-main
        if: steps.detect.outputs.count != '0' && env.BRANCH != ''
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh pr create --base zh-tw-main --head "$BRANCH" \
            --title "Update zh-TW translations (Gemini)" \
            --body "自動翻譯 english-main 上變動的 Markdown 檔案。已通過 validate。請檢查術語與翻譯品質後再合併。"
```

四個修正：`Setup Python` / `Install dependencies` 前移；`set -euo pipefail` 取代 `2>/dev/null || true`；`auto/zh-tw-${{ github.run_id }}` 取代 `git push -f` 到固定分支（原本會在 PR 未合併時覆蓋前一天的翻譯成果）；`BATCH_SIZE` 收斂三處重複的 `head -5`。

- [ ] **Step 3: 手動觸發驗證**

```bash
git add .github/workflows/translate-zh-tw.yml
git commit -m "fix(ci): run setup before detect; fail loudly; stop force-pushing over open PRs"
git push -u origin fix/ci-translate-workflow
```

在 GitHub UI 對 `fix/ci-translate-workflow` 執行 `workflow_dispatch`，或：

```bash
gh workflow run translate-zh-tw.yml -R first-mover-tw/move-book-zh-tw --ref fix/ci-translate-workflow
sleep 60
gh run list -R first-mover-tw/move-book-zh-tw --workflow=translate-zh-tw.yml --limit 1
```

Expected: `Detect` 步驟印出非零的檔案數（而非空白）。若 `Translate` 因 API quota 失敗，job 應**紅燈**而非綠燈 —— 這正是修復的重點。

- [ ] **Step 4: 開 PR 1**

```bash
gh pr create -R first-mover-tw/move-book-zh-tw --base zh-tw-main \
  --title "PR 1: fix translate workflow that has never translated a file" \
  --body "根因見 spec D1。run 28997766485 的 log 顯示 detect 在裝依賴前執行，ModuleNotFoundError 被 2>/dev/null 吞掉。"
```

---

### Task 17: 翻譯品質 A/B（決定 backfill 用的 model）

**Files:**
- Create: `$SP/zh-tw-ab/` （scratchpad，不進 repo）

spec 決策 8：無實測數據，不預先寫死 model。

- [ ] **Step 1: 挑一個術語密集的長檔**

`reference/variables.md`（英文 824 行），這也是截斷最嚴重的檔案。

- [ ] **Step 2: 用兩個 model 各翻一次**

```bash
mkdir -p $SP/zh-tw-ab
git checkout zh-tw-main && git pull --ff-only
for m in haiku sonnet; do
  ZH_TW_CLAUDE_MODEL=$m uv run --with pyyaml python -m scripts.zh_tw \
    --backend claude reference/variables.md > $SP/zh-tw-ab/$m.log 2>&1 || true
done
```

- [ ] **Step 3: 產出實際譯文供比對**

```bash
for m in haiku sonnet; do
  ZH_TW_CLAUDE_MODEL=$m uv run --with pyyaml python - <<'PY' > $SP/zh-tw-ab/$m.md
import subprocess, os
from scripts.zh_tw import pipeline
from scripts.zh_tw.backends.claude_cli import ClaudeCLIBackend
en = subprocess.run(["git","show","english-main:reference/variables.md"],
                    capture_output=True, text=True).stdout
prev = subprocess.run(["git","show","HEAD:reference/variables.md"],
                      capture_output=True, text=True).stdout
print(pipeline.assemble(en, prev, ClaudeCLIBackend()), end="")
PY
done
```

- [ ] **Step 4: 人工比對並記錄決定**

檢查點：術語是否一致、程式碼註解是否翻譯、標題是否為「中文 (English)」格式、是否有截斷。

Run: `wc -l $SP/zh-tw-ab/haiku.md $SP/zh-tw-ab/sonnet.md`
Expected: 兩者行數皆接近英文的 824 行（validate 已保證標題與 fence 數相符）

**這是一個人工決策點。** 把選定的 model 寫進 `scripts/zh_tw/backends/claude_cli.py` 的 `MODEL` 預設值，commit：

```bash
git add scripts/zh_tw/backends/claude_cli.py
git commit -m "chore(zh_tw): pin backfill model after A/B on reference/variables.md"
```

---

### Task 18: PR 2 — A 層 47 檔（只換 frontmatter）

A 層內文完全不動，diff 全部集中在 `---` 區塊。這是最安全的一批，先做。

- [ ] **Step 1: 建立分支並列出 A 層檔案**

```bash
git checkout zh-tw-main && git pull --ff-only
git checkout -b sync/pr2-frontmatter
uv run --with pyyaml python - > $SP/tier_a.txt <<'PY'
from scripts.zh_tw import manifest, pipeline
for p in manifest.stale_files("english-main"):
    if p.endswith(".md") and pipeline.tier(p) == "A":
        print(p)
PY
wc -l $SP/tier_a.txt
```
Expected: `47`

- [ ] **Step 2: Dry-run**

```bash
xargs -a $SP/tier_a.txt uv run --with pyyaml python -m scripts.zh_tw --backend claude
```
Expected: `成功 47，失敗 0`

若有失敗，**不要跳過** —— 失敗代表該檔的結構驗證未過，應降級 B 層（`tier()` 已處理，失敗代表有未預期的情況）。

- [ ] **Step 3: 實際套用**

```bash
xargs -a $SP/tier_a.txt uv run --with pyyaml python -m scripts.zh_tw --backend claude --apply
```

- [ ] **Step 4: 確認內文零改動**

```bash
git diff --stat -- book reference | tail -1
uv run --with pyyaml python - <<'PY'
import subprocess
from pathlib import Path
from scripts.zh_tw import frontmatter as fm
changed = 0
for p in subprocess.run(["git","diff","--name-only","--","book","reference"],
                        capture_output=True, text=True).stdout.split("\0"):
    old = subprocess.run(["git","show",f"HEAD:{p}"], capture_output=True, text=True).stdout
    _, old_body = fm.split(old)
    _, new_body = fm.split(Path(p).read_text(encoding="utf-8"))
    if old_body != new_body:
        changed += 1
        print(f"內文被改動: {p}")
print(f"內文被改動的檔案數: {changed}")
PY
```
Expected: `內文被改動的檔案數: 0`

**這一步是 A 層的核心保證。** 若不為 0，停止並檢查 `rebuild_frontmatter_only`。

- [ ] **Step 5: 跑 repo 級檢查與測試**

```bash
uv run --with pyyaml python -m scripts.zh_tw.check_repo
uv run --with pytest --with pyyaml pytest tests/ -v
npx --yes prettier@3 --check 'book/**/*.md' 'reference/**/*.md'
```
Expected: `check_repo` 的連結問題為 0；全部測試通過。

`test_baseline.py` 讀的是釘死的 `PRE_FIX` commit，**不會**因為本 PR 修好了 47 個 description 而變動 —— 基線衡量的是修復前的狀態，直到收尾 task 才整份改寫。`check_repo` 讀的是 working tree，違禁詞數會從 126 開始下降。

- [ ] **Step 6: Commit 與 PR**

```bash
git add scripts/translation-manifest.json
xargs -a $SP/tier_a.txt git add --
git commit -m "docs(zh-tw): sync frontmatter for 47 tier-A files (no body changes)"
git push -u origin sync/pr2-frontmatter
gh pr create -R first-mover-tw/move-book-zh-tw --base zh-tw-main \
  --title "PR 2: tier-A frontmatter sync (47 files, body untouched)" \
  --body "內文零改動，已由腳本驗證。diff 全部集中在 frontmatter。"
```

---

### Task 19: PR 3 — 15 個結構殘缺檔（P0）

這 13 個嚴重殘缺的頁面現正掛在線上：`reference/variables.md` 中文只有 36 行（英文 824）、`code-quality-checklist.md` 24 行（英文 592）。優先於同步上游新內容。

同時刪除孤兒檔 `book/storage/transfer-restrictions.md`（上游 `d700b884` 已刪，redirect 早已存在於 `site/docusaurus.config.ts:90`）。

- [ ] **Step 1: 建立分支並列出殘缺檔**

```bash
git checkout zh-tw-main && git pull --ff-only
git checkout -b sync/pr3-broken-files
uv run --with pyyaml python - > $SP/broken.txt <<'PY'
import subprocess
from scripts.zh_tw import validate
MERGE_BASE = "f2c0a93e1a0422078d3d051e4410ac3edc612016"
def show(ref, p):
    r = subprocess.run(["git","show",f"{ref}:{p}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None
files = subprocess.run(["git","ls-tree","-r","--name-only","-z","HEAD","book","reference"],
                       capture_output=True, text=True).stdout.split("\0")
for p in [f for f in files if f.endswith(".md")]:
    zh, en = show("HEAD", p), show(MERGE_BASE, p)
    if not zh or not en:
        continue
    errs = validate.check_file(zh, en)
    if any("標題層級序列" in e or "fence" in e for e in errs):
        print(p)
PY
wc -l $SP/broken.txt
```
Expected: `15`

- [ ] **Step 2: 全譯（B 層）**

```bash
xargs -a $SP/broken.txt uv run --with pyyaml python -m scripts.zh_tw --backend claude --apply
```
Expected: `成功 15，失敗 0`

任何失敗都代表 validate 攔下了壞翻譯 —— 這是設計意圖。重跑該檔即可。

- [ ] **Step 3: 確認截斷已修復**

```bash
for f in reference/variables.md book/guides/code-quality-checklist.md reference/unit-testing.md; do
  en=$(git show english-main:$f | wc -l)
  zh=$(wc -l < $f)
  echo "$f: 英文 $en 行, 中文 $zh 行"
done
```
Expected: 中文行數與英文同量級（先前是 36/824、24/592、45/438）

- [ ] **Step 4: 刪除孤兒檔**

```bash
git rm book/storage/transfer-restrictions.md
uv run --with pyyaml python -m scripts.zh_tw --orphans
```
Expected: 無輸出

- [ ] **Step 5: 驗證**

```bash
uv run --with pyyaml python -m scripts.zh_tw.check_repo
uv run --with pytest --with pyyaml pytest tests/test_validate.py tests/test_pipeline.py -v
npx --yes prettier@3 --check 'book/**/*.md' 'reference/**/*.md'
```
Expected: `check_repo` 連結問題 0

- [ ] **Step 6: Commit 與 PR**

```bash
git add scripts/translation-manifest.json
xargs -a $SP/broken.txt git add --
git commit -m "fix(zh-tw): restore 19 structurally truncated pages; drop orphaned transfer-restrictions

reference/variables.md was 36 lines against an 824-line English source;
code-quality-checklist.md was 24 against 592. Whole-file translation through
a flash-tier model silently truncated on output-token exhaustion and the old
script wrote the result to disk unchecked."
git push -u origin sync/pr3-broken-files
gh pr create -R first-mover-tw/move-book-zh-tw --base zh-tw-main \
  --title "PR 3 (P0): restore 19 truncated pages" \
  --body "這 13 個頁面目前線上內容嚴重殘缺。詳見 spec D2。"
```

---

### Task 20: PR 4/5/6 — 三個主要章節

三個 PR 結構相同，逐一執行。**每個 PR 獨立 review 後才做下一個。**

| PR | 路徑前綴 | 檔數 | 分支 |
|---|---|---|---|
| 4 | `book/move-basics/` | 29 | `sync/pr4-move-basics` |
| 5 | `book/programmability/` | 18 | `sync/pr5-programmability` |
| 6 | `book/testing/` | 13 | `sync/pr6-testing` |

檔數已扣除 PR 3 抽走的殘缺檔（move-basics 0 個、programmability 6 個）。

- [ ] **Step 1: PR 4 — book/move-basics**

```bash
git checkout zh-tw-main && git pull --ff-only
git checkout -b sync/pr4-move-basics
uv run --with pyyaml python -m scripts.zh_tw --detect \
  | grep '^book/move-basics/' > $SP/pr4.txt
wc -l $SP/pr4.txt   # Expected: 29
xargs -a $SP/pr4.txt uv run --with pyyaml python -m scripts.zh_tw --backend claude --apply
uv run --with pyyaml python -m scripts.zh_tw.check_repo
npx --yes prettier@3 --check 'book/**/*.md'
git add scripts/translation-manifest.json
xargs -a $SP/pr4.txt git add --
git commit -m "docs(zh-tw): sync book/move-basics with upstream"
git push -u origin sync/pr4-move-basics
gh pr create -R first-mover-tw/move-book-zh-tw --base zh-tw-main \
  --title "PR 4: sync book/move-basics (29 files)" --body "術語密集章節，請仔細 review。"
```

- [ ] **Step 2: 等 PR 4 合併，再做 PR 5 — book/programmability**

```bash
git checkout zh-tw-main && git pull --ff-only
git checkout -b sync/pr5-programmability
uv run --with pyyaml python -m scripts.zh_tw --detect \
  | grep '^book/programmability/' > $SP/pr5.txt
wc -l $SP/pr5.txt   # Expected: 18
xargs -a $SP/pr5.txt uv run --with pyyaml python -m scripts.zh_tw --backend claude --apply
uv run --with pyyaml python -m scripts.zh_tw.check_repo
npx --yes prettier@3 --check 'book/**/*.md'
git add scripts/translation-manifest.json
xargs -a $SP/pr5.txt git add --
git commit -m "docs(zh-tw): sync book/programmability with upstream"
git push -u origin sync/pr5-programmability
gh pr create -R first-mover-tw/move-book-zh-tw --base zh-tw-main \
  --title "PR 5: sync book/programmability (18 files)" --body ""
```

- [ ] **Step 3: 等 PR 5 合併，再做 PR 6 — book/testing（全新章節）**

```bash
git checkout zh-tw-main && git pull --ff-only
git checkout -b sync/pr6-testing
uv run --with pyyaml python -m scripts.zh_tw --detect \
  | grep '^book/testing/' > $SP/pr6.txt
wc -l $SP/pr6.txt   # Expected: 13
xargs -a $SP/pr6.txt uv run --with pyyaml python -m scripts.zh_tw --backend claude --apply
uv run --with pyyaml python -m scripts.zh_tw.check_repo
npx --yes prettier@3 --check 'book/**/*.md'
git add scripts/translation-manifest.json
xargs -a $SP/pr6.txt git add --
git commit -m "docs(zh-tw): sync book/testing chapter with upstream"
git push -u origin sync/pr6-testing
gh pr create -R first-mover-tw/move-book-zh-tw --base zh-tw-main \
  --title "PR 6: sync book/testing (13 files, new chapter)" \
  --body "全新章節，沒有舊譯文可比對。book/testing/linting.md 是首次翻譯。"
```

---

### Task 21: PR 7 — 剩餘 29 檔

`concepts` 6、`storage` 6、`object` 4、`move-advanced` 3、`appendix` 2、`book` 根 2、`before-we-begin` 1、`guides` 1、`your-first-move` 1、`reference` 2。

- [ ] **Step 1: 建立分支並取剩餘清單**

```bash
git checkout zh-tw-main && git pull --ff-only
git checkout -b sync/pr7-remainder
uv run --with pyyaml python -m scripts.zh_tw --detect > $SP/pr7.txt
wc -l $SP/pr7.txt
```
Expected: `30`（28 個 md + 2 個 sidebar.yml）

- [ ] **Step 2: 翻譯**

```bash
xargs -a $SP/pr7.txt uv run --with pyyaml python -m scripts.zh_tw --backend claude --apply
```
Expected: `成功 30，失敗 0`

其中 `book/sidebar.yml`（109 個 label）與 `reference/sidebar.yml`（40 個 label）由 `pipeline.run` 分流至 Task 14 的 `sidebar.translate`，不走 markdown 路徑。英文 label 未變動者沿用舊譯文，只有新增的 label 才呼叫 backend。

- [ ] **Step 2b: 確認 sidebar 結構未被更動**

```bash
uv run --with pyyaml python - <<'PY'
import subprocess
from pathlib import Path
from scripts.zh_tw import sidebar
for f in ("book/sidebar.yml", "reference/sidebar.yml"):
    en = subprocess.run(["git","show",f"english-main:{f}"], capture_output=True, text=True).stdout
    zh = Path(f).read_text(encoding="utf-8")
    assert sidebar.skeleton(en) == sidebar.skeleton(zh), f
    print(f"{f}: 結構一致，{len(sidebar.labels(zh))} 個 label")
PY
```
Expected: `book/sidebar.yml: 結構一致，109 個 label` 與 `reference/sidebar.yml: 結構一致，40 個 label`

- [ ] **Step 3: 驗證**

```bash
uv run --with pyyaml python -m scripts.zh_tw.check_repo
uv run --with pyyaml python -m scripts.zh_tw --detect | wc -l
```
Expected: `check_repo` 回報 0 個問題；`--detect` 回報 `0`

- [ ] **Step 4: Commit 與 PR**

```bash
git add scripts/translation-manifest.json
xargs -a $SP/pr7.txt git add --
git commit -m "docs(zh-tw): sync remaining chapters and sidebars with upstream"
git push -u origin sync/pr7-remainder
gh pr create -R first-mover-tw/move-book-zh-tw --base zh-tw-main \
  --title "PR 7: sync remaining 28 files + sidebars" --body ""
```

---

### Task 22: 收尾 — 基線轉綠與驗收

**Files:**
- Modify: `tests/test_baseline.py`

- [ ] **Step 1: 把基線測試改寫為全綠斷言**

`tests/test_baseline.py` 全檔取代：

```python
"""backfill 完成後，validate 對整個 repo 必須全綠。

修復前的基線（見 git history）：19 檔結構失敗、89 檔 description 未翻譯、
143 處大陸用語。這些數字曾是這個測試的斷言值。
"""

import subprocess

from scripts.zh_tw import check_repo, manifest, validate


def _show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def test_no_stale_files():
    assert manifest.stale_files("english-main") == []


def test_no_orphans():
    assert manifest.orphans("english-main") == []


def test_every_file_passes_validation():
    files = check_repo.collect()
    failures = {}
    for path, zh in files.items():
        en = _show("english-main", path)
        if en is None:
            failures[path] = ["英文來源不存在"]
            continue
        errs = validate.check_file(zh, en)
        if errs:
            failures[path] = errs
    assert failures == {}, failures


def test_all_anchor_links_resolve():
    assert validate.check_links(check_repo.collect()) == []


def test_zero_glossary_violations():
    from scripts.zh_tw import frontmatter as fm, glossary
    total = 0
    for _, text in check_repo.collect().items():
        _, body = fm.split(text)
        total += sum(glossary.scan(body).values())
    assert total == 0, total


def test_file_set_matches_english_main():
    en = {f for f in manifest.tracked_files("english-main") if f.endswith(".md")}
    zh = set(check_repo.collect())
    assert zh == en, {"缺少": sorted(en - zh), "多出": sorted(zh - en)}
```

- [ ] **Step 2: 執行驗收**

```bash
git checkout zh-tw-main && git pull --ff-only
uv run --with pytest --with pyyaml pytest tests/ -v
uv run --with pyyaml python -m scripts.zh_tw --detect | wc -l   # Expected: 0
uv run --with pyyaml python -m scripts.zh_tw.check_repo          # Expected: 0 個問題
npx --yes prettier@3 --check 'book/**/*.md' 'reference/**/*.md'
pnpm install && pnpm build
```
Expected: 全部通過；`pnpm build` 無 broken anchor 警告

- [ ] **Step 3: 確認 CI 現在會做事**

```bash
gh workflow run translate-zh-tw.yml -R first-mover-tw/move-book-zh-tw --ref zh-tw-main
sleep 90
gh run list -R first-mover-tw/move-book-zh-tw --workflow=translate-zh-tw.yml --limit 1
gh run view -R first-mover-tw/move-book-zh-tw --log | grep -A2 "將翻譯"
```
Expected: `將翻譯 0 個檔案` 且 job 綠燈（因為已無過期檔）

- [ ] **Step 4: Commit**

```bash
git checkout -b chore/green-baseline
git add tests/test_baseline.py
git commit -m "test: flip baseline from measured defects to all-green acceptance"
git push -u origin chore/green-baseline
gh pr create -R first-mover-tw/move-book-zh-tw --base zh-tw-main \
  --title "chore: green baseline after backfill" --body "驗收條件見 spec 第九節。"
```

---

## 驗收條件（對應 spec 第九節）

1. `zh-tw-main` 的 `book` + `reference` 下有 149 個 md 檔，路徑集合與 `english-main` 完全一致 — `test_file_set_matches_english_main`
2. `validate.check_file` 對全部 149 檔全綠 — `test_every_file_passes_validation`
3. `manifest.stale_files()` 與 `manifest.orphans()` 皆為空 — `test_no_stale_files` / `test_no_orphans`
4. 97 條內部 anchor 連結全部可解析；56 個既有 anchor 的 ID 值一個都沒變 — `test_all_anchor_links_resolve` + `validate` 第 6 條
5. 8 條 glossary 違禁詞出現次數為 0（現況 143） — `test_zero_glossary_violations`
6. `npx prettier@3 --check` 通過 — Task 22 Step 2
7. `translate-zh-tw.yml` 手動 dispatch 能真實偵測；detect 失敗時 job 紅 — Task 16 Step 3、Task 22 Step 3
8. `pnpm build` 成功，無 broken anchor 警告 — Task 22 Step 2
