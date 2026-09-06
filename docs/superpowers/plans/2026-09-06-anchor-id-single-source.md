# 標題顯式 anchor id 單一真相來源 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把「一個標題的顯式 `{#id}` 是什麼」收斂成 repo 內唯一一份定義，且該定義等於消費者 docusaurus 3.10.2 的定義。

**Architecture:** `scripts/zh_tw/anchors.py` 成為唯一真相來源，內含由 `@docusaurus/utils` 移植的 regex 與兩個 helper（`existing_anchor` 取 id、`strip_anchor` 剝除）。`validate.py`、`backends/fake.py` 停止持有自己的 regex，改引用 `anchors.ANCHOR_SUFFIX`。CJK anchor 支援是收斂後自然落地的副產品，不是新功能；管線的衍生路徑（tier 3）仍只產出英文 slug。

**Tech Stack:** Python 3（`re`、`pytest`）、`markdown-it-py`（既有）、無新依賴。上游 oracle 以「移植 + 版本漂移守衛」逼近，不跨語言呼叫 node。

**Spec:** `docs/superpowers/specs/2026-09-06-anchor-id-single-source-design.md`

## Global Constraints

- **語料 byte 不動**：任務全程 `git diff --stat book reference` 必須為空。任何一步讓它非空即為實作錯誤。
- **`python` 不在 PATH**：所有指令前先 `source .venv/bin/activate`（`tasks/progress.md` Notes）。
- **只 stage 明確指定的檔案**：`git add <file>...`，禁止 `git add -A` / `git add .`。
- **上游 regex 字面值（唯一權威來源）**：`@docusaurus/utils` 3.10.2 `src/markdownHeadingIdUtils.ts` 的 `parseMarkdownHeadingId(heading, 'classic')`：
  ```
  /\s*\{#(?<id>(?:.(?!\{#|\}))*.)\}$/
  ```
  移植成 Python：`re.compile(r"\s*\{#((?:.(?!\{#|\}))*.)\}$")`，取出的 id 事後 `.strip()`（比照上游）。
- **釘住的 docusaurus 版本**：`3.10.2`，來源 `site/package.json` 的 `dependencies["@docusaurus/core"]`。
- **不新增任何語料掃描的 exit-code 失敗來源**：`check_repo` 的 `0/0/0/0` 摘要格式與回傳值語意不得改變。
- **既有測試基線**：改動前 531 passed。任務結束時總數只增不減，且無 skip。

---

### Task 1: `anchors.py` 成為唯一真相來源

**Files:**
- Modify: `scripts/zh_tw/anchors.py:19`（`_ANCHOR` 定義）、`scripts/zh_tw/anchors.py:136-138`（`existing_anchor`）
- Test: `tests/test_anchors_slug.py`（既有檔，附加）

**Interfaces:**
- Consumes: 無（第一個任務）
- Produces:
  - `anchors.ANCHOR_SUFFIX: re.Pattern` — 公開常數，`search()` 的 `group(0)` 是含前導空白的整段 `{#id}`，`group(1)` 是未 strip 的 id。
  - `anchors.existing_anchor(heading: str) -> str | None` — 既有簽名不變，行為擴張為接受任意字元 id。
  - `anchors.strip_anchor(heading: str) -> str` — 新函式，回傳剝掉尾端 `{#id}` 後的標題文字（不做 `.strip()`，由呼叫端決定）。

- [ ] **Step 1: 寫失敗測試**

附加到 `tests/test_anchors_slug.py` 檔尾：

```python
def test_existing_anchor_accepts_cjk_id():
    """docusaurus 的 id 可以是「除了 {# 和 } 以外的任何字元」，包含 CJK。
    這條在收斂前是紅的：舊 _ANCHOR 只收 [A-Za-z0-9_-]+。"""
    assert anchors.existing_anchor("中止與斷言 {#終止與斷言-abort-and-assert}") == (
        "終止與斷言-abort-and-assert"
    )


def test_slugify_strips_cjk_anchor_instead_of_folding_it_in():
    """舊行為把認不得的 CJK id 當成標題文字，slug 變成「標題-id」兩段相連。"""
    assert anchors.slugify("中止與斷言 {#終止與斷言-abort-and-assert}") == "中止與斷言"


def test_strip_anchor_returns_heading_without_id():
    assert anchors.strip_anchor("Foo {#bar}") == "Foo"
    assert anchors.strip_anchor("Foo") == "Foo"
    assert anchors.strip_anchor("Foo {#中文}") == "Foo"


def test_anchor_id_is_stripped_like_upstream():
    """上游對取出的 id 做 .trim()。"""
    assert anchors.existing_anchor("Foo {# bar }") == "bar"


def test_only_the_last_anchor_group_is_the_id():
    """上游 regex 的 id 不能含 `{#` 或 `}`，且必須貼著字串結尾。
    `A {#a} {#b}` 的 id 是 b，而 `{#a}` 留在標題文字裡（與 docusaurus 一致）。"""
    assert anchors.existing_anchor("A {#a} {#b}") == "b"
    assert anchors.strip_anchor("A {#a} {#b}") == "A {#a}"


def test_empty_id_is_not_an_anchor():
    assert anchors.existing_anchor("Foo {#}") is None


def test_double_closing_brace_is_not_an_anchor():
    assert anchors.existing_anchor("Foo {#a}}") is None
```

- [ ] **Step 2: 跑測試確認失敗**

```bash
source .venv/bin/activate && pytest tests/test_anchors_slug.py -v
```

Expected: `test_existing_anchor_accepts_cjk_id`、`test_slugify_strips_cjk_anchor_instead_of_folding_it_in`、`test_strip_anchor_returns_heading_without_id`、`test_anchor_id_is_stripped_like_upstream`、`test_only_the_last_anchor_group_is_the_id` FAIL；`test_empty_id_is_not_an_anchor`、`test_double_closing_brace_is_not_an_anchor` 已經是 PASS（舊 regex 恰好也擋得住，保留作為收斂後的回歸守衛）。

- [ ] **Step 3: 實作**

把 `scripts/zh_tw/anchors.py:19` 的

```python
_ANCHOR = re.compile(r"\s*\{#([A-Za-z0-9_-]+)\}\s*$")
```

替換為：

```python
# 移植自 @docusaurus/utils 3.10.2 src/markdownHeadingIdUtils.ts 的
# parseMarkdownHeadingId(heading, 'classic')：
#     /\s*\{#(?<id>(?:.(?!\{#|\}))*.)\}$/
# 上游原始碼的註解：「The ID can contain any characters except `{#` and `}`」。
#
# 這是本 repo 對「什麼是顯式 anchor id」的唯一定義。validate 與 backends.fake
# 一律引用 ANCHOR_SUFFIX，不得再自己刻一份 —— 三份定義互相漂移、且沒有一份
# 等於消費者，正是 2026-09-06 收斂前的狀態（lessons L15 / L23）。
#
# 上游的 regex 結尾是 `}$`（沒有 \s*），因為它拿到的 heading 文字已經被
# markdown 解析器 trim 過。本模組在 helper 入口顯式 rstrip 來對齊這個前提，
# 而不是在 regex 上加一個上游沒有的 \s* —— 那就又是第二份定義了。
_ANCHOR = re.compile(r"\s*\{#((?:.(?!\{#|\}))*.)\}$")
ANCHOR_SUFFIX = _ANCHOR  # 公開別名：validate / backends.fake 的唯一入口
```

把 `scripts/zh_tw/anchors.py:104` `slugify()` 的第一行

```python
    text = _ANCHOR.sub("", heading)
```

替換為：

```python
    text = strip_anchor(heading)
```

把 `scripts/zh_tw/anchors.py:136-138` 的 `existing_anchor` 替換為：

```python
def existing_anchor(heading: str) -> str | None:
    m = _ANCHOR.search(heading.rstrip())
    return m.group(1).strip() if m else None


def strip_anchor(heading: str) -> str:
    """剝掉尾端的 `{#id}`。不做前後 strip —— 由呼叫端決定，
    因為 pipeline._repair_headings 與 validate.heading_suffix_error
    對空白的處理時機不同。"""
    return _ANCHOR.sub("", heading.rstrip())
```

把 `scripts/zh_tw/anchors.py:332`（`inject_report` 內）的

```python
        text = _ANCHOR.sub("", zh_h[idx][1])
```

替換為：

```python
        text = strip_anchor(zh_h[idx][1])
```

- [ ] **Step 4: 跑測試確認通過**

```bash
source .venv/bin/activate && pytest tests/test_anchors_slug.py tests/test_anchors_inject.py tests/test_anchors_realworld.py -v
```

Expected: 全部 PASS。若 `test_anchors_inject.py:242` 的 `anchors._ANCHOR.findall(text)` 因為 group 數改變而壞掉，改成 `[m.group(1).strip() for m in anchors.ANCHOR_SUFFIX.finditer(text)]`（該處是測試輔助，不是產品行為）。

- [ ] **Step 5: 全套測試 + 語料未動**

```bash
source .venv/bin/activate && pytest -q && git diff --stat book reference
```

Expected: 全綠、測試數 = 531 + 7；`git diff --stat book reference` 無輸出。

- [ ] **Step 6: Commit**

```bash
git add scripts/zh_tw/anchors.py tests/test_anchors_slug.py tests/test_anchors_inject.py
git commit -m "refactor(anchors): {#id} 判準移植自 docusaurus 3.10.2，anchors 成唯一定義"
```

---

### Task 2: 消費端停止持有第二份 regex

**Files:**
- Modify: `scripts/zh_tw/validate.py:492-493`（`_ANCHOR_SUFFIX` / `ANCHOR_SUFFIX`）、`scripts/zh_tw/validate.py:569-570`（`heading_suffix_error`）
- Modify: `scripts/zh_tw/backends/fake.py:49`（`_EXPLICIT_ANCHOR`）、`scripts/zh_tw/backends/fake.py:61-64`
- Test: `tests/test_anchor_single_source.py`（新檔）

**Interfaces:**
- Consumes: `anchors.ANCHOR_SUFFIX`、`anchors.strip_anchor`（Task 1）
- Produces: `validate.ANCHOR_SUFFIX` 仍是公開名稱（`pipeline.py:227-228` 在用），但值是 `anchors.ANCHOR_SUFFIX` 本身（同一個物件，`is` 相等）。

- [ ] **Step 1: 寫失敗測試**

建立 `tests/test_anchor_single_source.py`：

```python
"""單一真相來源守衛：repo 內只准有一處 `{#id}` 的 regex 定義。

這條測試存在的理由是 2026-09-06 的實測狀態：anchors 用 [A-Za-z0-9_-]+、
validate 與 backends.fake 用 Unicode 的 [\\w-]+、消費者 docusaurus 用
[^{#}]+ —— 三份定義，零份等於消費者（lessons L15 / L23）。
"""

import re
from pathlib import Path

from scripts.zh_tw import anchors, validate
from scripts.zh_tw.backends import fake

SRC = Path("scripts/zh_tw")

# 產品程式碼裡「長得像在比對 {#id}」的 regex 字面值。
_REGEX_LITERAL = re.compile(r"""re\.compile\(\s*r?["'][^"']*\\\{#""")


def test_validate_reuses_the_anchors_pattern_object():
    assert validate.ANCHOR_SUFFIX is anchors.ANCHOR_SUFFIX


def test_fake_backend_reuses_the_anchors_pattern_object():
    assert fake.FakeBackend._EXPLICIT_ANCHOR is anchors.ANCHOR_SUFFIX


def test_only_anchors_module_compiles_an_anchor_regex():
    """tests/ 底下的上游移植字面值是刻意的第二份（對拍用），不在掃描範圍。"""
    offenders = sorted(
        str(p)
        for p in SRC.rglob("*.py")
        if p.name != "anchors.py" and _REGEX_LITERAL.search(p.read_text(encoding="utf-8"))
    )
    assert offenders == []


def test_gate_and_inject_agree_on_a_cjk_anchor():
    """收斂前的實證分歧：gate 的前處理剝得掉 CJK anchor，inject 認不得，
    於是同一份輸入產出兩套判定母體，inject 寫出兩個 {#id} 相連。"""
    heading = "中止與斷言 {#終止與斷言-abort-and-assert}"
    assert validate.ANCHOR_SUFFIX.sub("", heading).strip() == "中止與斷言"
    assert anchors.existing_anchor(heading) == "終止與斷言-abort-and-assert"

    zh = "# T {#a}\n\n## " + heading + "\n"
    en = "# T {#a}\n\n## Abort and Assert\n"
    out = anchors.inject(zh, en)
    assert out.count("{#") == 2  # 兩個標題各一個，不是三個
    assert "{#終止與斷言-abort-and-assert}" in out
```

- [ ] **Step 2: 跑測試確認失敗**

```bash
source .venv/bin/activate && pytest tests/test_anchor_single_source.py -v
```

Expected: 五條全 FAIL。前兩條是 `assert ... is ...` 失敗，第三條列出 `scripts/zh_tw/validate.py` 與 `scripts/zh_tw/backends/fake.py`，第四條在 `inject` 那行失敗（`out.count("{#")` 會是 3）。

- [ ] **Step 3: 實作**

`scripts/zh_tw/validate.py`：把第 492-493 行

```python
_ANCHOR_SUFFIX = re.compile(r"\s*\{#[\w-]+\}\s*$")
ANCHOR_SUFFIX = _ANCHOR_SUFFIX  # 公開別名：pipeline._repair_headings 與判定同一前處理
```

替換為：

```python
# 「什麼是顯式 {#id}」的定義在 anchors.py，這裡只轉出。曾經這裡有自己的
# 一份（`[\w-]+`），與 anchors 的 `[A-Za-z0-9_-]+` 對 CJK id 判定相反 ——
# gate 剝得掉、inject 認不得，同一份輸入兩套判定母體（lessons L15）。
ANCHOR_SUFFIX = anchors.ANCHOR_SUFFIX  # 公開別名：pipeline._repair_headings 在用
```

把 `heading_suffix_error` 的第 569-570 行

```python
    zh_t = _ANCHOR_SUFFIX.sub("", zh_t).strip()
    en_t = _ANCHOR_SUFFIX.sub("", en_t).strip()
```

替換為：

```python
    zh_t = anchors.strip_anchor(zh_t).strip()
    en_t = anchors.strip_anchor(en_t).strip()
```

`scripts/zh_tw/backends/fake.py`：把第 49 行

```python
    _EXPLICIT_ANCHOR = re.compile(r"\s*(\{#[\w-]+\})\s*$")
```

替換為（需在檔頂 `from .. import anchors`，若尚未匯入）：

```python
    # 判準與產品共用，不另刻一份（lessons L5：fake 要模擬真實 backend，
    # 不是讓守衛遷就 fake）。group(0) 含前導空白，取 {#id} 要 .strip()。
    _EXPLICIT_ANCHOR = anchors.ANCHOR_SUFFIX
```

把第 61-64 行

```python
                am = self._EXPLICIT_ANCHOR.search(title)
                anchor = f" {am.group(1)}" if am else ""
                if am:
                    title = title[: am.start()].rstrip()
```

替換為：

```python
                am = self._EXPLICIT_ANCHOR.search(title.rstrip())
                anchor = f" {am.group(0).strip()}" if am else ""
                if am:
                    title = title[: am.start()].rstrip()
```

- [ ] **Step 4: 跑測試確認通過**

```bash
source .venv/bin/activate && pytest tests/test_anchor_single_source.py -v
```

Expected: 五條全 PASS。

- [ ] **Step 5: 全套 + 語料未動**

```bash
source .venv/bin/activate && pytest -q && git diff --stat book reference
```

Expected: 全綠、測試數 = 531 + 7 + 5；語料 diff 為空。

- [ ] **Step 6: Commit**

```bash
git add scripts/zh_tw/validate.py scripts/zh_tw/backends/fake.py tests/test_anchor_single_source.py
git commit -m "refactor(anchors): validate 與 fake backend 改用 anchors 的單一 {#id} 判準"
```

---

### Task 3: 上游對拍與版本漂移守衛

**Files:**
- Create: `tests/test_anchors_upstream_parity.py`
- Test: 同上

**Interfaces:**
- Consumes: `anchors.existing_anchor`、`anchors.ANCHOR_SUFFIX`（Task 1）
- Produces: 模組常數 `UPSTREAM_REGEX`、`UPSTREAM_VERSION`、函式 `upstream_parse_id(heading: str) -> str | None`（僅測試內部使用）

> **這組測試的真實效力，說清楚**：Task 1 之後，`anchors._ANCHOR` 與這裡的
> `UPSTREAM_REGEX` 是同一條 regex，所以 fuzz 對拍在**當下**是恆真的。它的價值不在
> 現在，在**未來有人改動 `anchors._ANCHOR` 時會紅**（Task 6 mutation A 就是拿來證明
> 這件事的），以及版本漂移守衛會在 docusaurus 升級時叫人回去看上游。這不是
> 「找不到反例所以正確」的論證 —— 別在 commit message 或回報裡把它寫成那樣
> （lessons L15 推論）。

- [ ] **Step 1: 寫測試（這一條從一開始就該綠 —— 它是對拍，不是新行為）**

建立 `tests/test_anchors_upstream_parity.py`：

```python
"""與消費者 docusaurus 的 {#id} 判準對拍。

判準只要還是「我維護的一份推論」，就會有第五輪（lessons L23）。這裡不推論：
把上游 regex 原文移植過來對拍，並用版本漂移守衛逼人在升級時回去看一眼。
"""

import json
import random
import re
from pathlib import Path

from scripts.zh_tw import anchors

# 來源：site/node_modules/.../@docusaurus/utils/src/markdownHeadingIdUtils.ts
#       parseMarkdownHeadingId(heading, 'classic')
#   const customHeadingIdRegex = /\s*\{#(?<id>(?:.(?!\{#|\}))*.)\}$/;
UPSTREAM_VERSION = "3.10.2"
UPSTREAM_REGEX = re.compile(r"\s*\{#((?:.(?!\{#|\}))*.)\}$")


def upstream_parse_id(heading: str) -> str | None:
    """上游 parseMarkdownHeadingId 的 id 部分。上游對 heading 的前提是
    「已被 markdown 解析器 trim 過」，所以這裡先 rstrip。"""
    m = UPSTREAM_REGEX.search(heading.rstrip())
    return m.group(1).strip() if m else None


def test_docusaurus_version_has_not_drifted():
    """升級 docusaurus 時這條會紅 —— 去看 markdownHeadingIdUtils.ts 的
    customHeadingIdRegex 有沒有變，確認後再改 UPSTREAM_VERSION。
    沒有這條守衛，上游改了判準我們不會知道（靜默腐化）。"""
    pkg = json.loads(Path("site/package.json").read_text(encoding="utf-8"))
    assert pkg["dependencies"]["@docusaurus/core"] == UPSTREAM_VERSION


CASES = [
    "Foo {#bar}",
    "Foo",
    "中止與斷言 {#終止與斷言-abort-and-assert}",
    "中止與斷言 (Abort and Assert) {#abort-and-assert}",
    "Foo {# bar }",
    "Foo {#bar baz}",
    "A {#a} {#b}",
    "Foo {#}",
    "Foo {#a}}",
    "Foo {#a} trailing",
    "{#only-id}",
    "Foo {#a-b_c.d}",
    "`code` {#code}",
    "Foo {#a{#b}",
    "Foo #{a}",
]


def test_parity_on_curated_cases():
    mismatches = [
        (c, anchors.existing_anchor(c), upstream_parse_id(c))
        for c in CASES
        if anchors.existing_anchor(c) != upstream_parse_id(c)
    ]
    assert mismatches == []


# fuzz 的原子表。CASES 裡每一個手上的 repro 都必須是這張表拼得出來的形態，
# 否則負面結果沒有意義（lessons L15 推論：fuzz 的負面結果只在 generator
# 生得出該類輸入時才有效）。test_generator_covers_the_curated_repros 驗這件事。
ATOMS = ["Foo", "中止", " ", "{#", "}", "#", "{", "a-b", "_c.d", "`x`", "", "(En)"]


def _gen(rng: random.Random) -> str:
    return "".join(rng.choice(ATOMS) for _ in range(rng.randint(1, 8)))


def test_generator_covers_the_curated_repros():
    """generator 至少要生得出「以 {# ... } 結尾」與「含兩組 {#」的形態，
    否則下面的 fuzz 只是在測沒有 anchor 的字串。"""
    rng = random.Random(20260906)
    samples = [_gen(rng) for _ in range(20000)]
    assert any(s.rstrip().endswith("}") and "{#" in s for s in samples)
    assert any(s.count("{#") >= 2 for s in samples)
    assert any(anchors.existing_anchor(s) is not None for s in samples)


def test_parity_under_fuzz():
    rng = random.Random(20260906)
    for _ in range(20000):
        s = _gen(rng)
        assert anchors.existing_anchor(s) == upstream_parse_id(s), repr(s)
```

- [ ] **Step 2: 跑測試**

```bash
source .venv/bin/activate && pytest tests/test_anchors_upstream_parity.py -v
```

Expected: 五條全 PASS。**若 `test_parity_under_fuzz` 紅，那是真的分歧 —— 印出的 `repr(s)` 就是反例，回頭修 `anchors._ANCHOR` 的移植，不要改 oracle。**

- [ ] **Step 3: 確認上游檔案內容與註解裡寫的一致**

```bash
sed -n '/customHeadingIdRegex/p' site/node_modules/.pnpm/@docusaurus+utils@3.10.2*/node_modules/@docusaurus/utils/src/markdownHeadingIdUtils.ts
```

Expected: 印出 `const customHeadingIdRegex = /\s*\{#(?<id>(?:.(?!\{#|\}))*.)\}$/;`。若不符，以檔案為準改測試常數與 `anchors.py` 的移植。

- [ ] **Step 4: Commit**

```bash
git add tests/test_anchors_upstream_parity.py
git commit -m "test(anchors): 與 docusaurus 3.10.2 的 {#id} 判準對拍 + 版本漂移守衛"
```

---

### Task 4: 真實語料回歸（釘固定 sha）

**Files:**
- Modify: `tests/test_anchors_realworld.py`（既有檔，附加）

**Interfaces:**
- Consumes: `anchors.existing_anchor`（Task 1）、既有的 `_show()` / `MERGE_BASE` / `PRE_FIX`
- Produces: 無（純測試）

- [ ] **Step 1: 取得釘住用的 sha 與期望數字**

```bash
git rev-parse HEAD
source .venv/bin/activate && python - <<'PY'
import subprocess
from scripts.zh_tw import anchors, frontmatter
sha = subprocess.run(["git","rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()
def files(ref, *roots):
    r = subprocess.run(["git","ls-tree","-r","--name-only",ref,*roots],capture_output=True,text=True,check=True)
    return [f for f in r.stdout.split() if f.endswith(".md")]
def show(ref,p):
    return subprocess.run(["git","show",f"{ref}:{p}"],capture_output=True,text=True).stdout
tot=withid=0
for p in files(sha,"book","reference"):
    _, body = frontmatter.split(show(sha,p))
    for _, t in anchors.headings(body):
        tot+=1
        if anchors.existing_anchor(t): withid+=1
print("ZH_SHA =", sha, "headings =", tot, "with_id =", withid)
PY
```

把印出的 `sha`、`headings`、`with_id` 填進下一步的常數（**照實填，不要抄計畫裡的示例數字**）。

- [ ] **Step 2: 寫測試**

附加到 `tests/test_anchors_realworld.py` 檔尾（`<SHA>` / `<N>` / `<M>` 換成上一步的實測值）：

```python
# 收斂 {#id} 判準（2026-09-06）當下的語料狀態。釘固定 sha，不讀 working tree
# —— census 測試讀活狀態會在下一次排乾後永久紅（lessons L3）。
ANCHOR_CENSUS_SHA = "<SHA>"
ANCHOR_CENSUS_HEADINGS = <N>
ANCHOR_CENSUS_WITH_ID = <M>


def _files_at(ref: str, *roots: str) -> list[str]:
    r = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, *roots],
        capture_output=True, text=True, check=True,
    )
    return [f for f in r.stdout.split() if f.endswith(".md")]


def test_widened_anchor_pattern_is_a_noop_on_the_real_corpus():
    """放寬到上游判準之後，全語料每個標題的 id 判定都不能變。

    收斂前的窄版 regex 是 [A-Za-z0-9_-]+；語料裡的 id 全是 ASCII，所以
    正確的收斂應該是 byte 級 no-op。這條測試把「應該」變成可判定的事實。
    """
    narrow = re.compile(r"\s*\{#([A-Za-z0-9_-]+)\}\s*$")
    total = with_id = 0
    for path in _files_at(ANCHOR_CENSUS_SHA, "book", "reference"):
        _, body = frontmatter.split(_show(ANCHOR_CENSUS_SHA, path) or "")
        for _, t in anchors.headings(body):
            total += 1
            new = anchors.existing_anchor(t)
            m = narrow.search(t)
            old = m.group(1) if m else None
            assert new == old, (path, t, new, old)
            if new:
                with_id += 1
    assert total == ANCHOR_CENSUS_HEADINGS
    assert with_id == ANCHOR_CENSUS_WITH_ID
    assert with_id == total  # 全語料每個標題都已帶顯式 anchor


def test_widened_anchor_pattern_is_a_noop_on_the_english_source():
    """english-main 的英文原檔顯式 id 數為 0；slugify 的輸入端不因放寬而改變。"""
    narrow = re.compile(r"\s*\{#([A-Za-z0-9_-]+)\}\s*$")
    seen = 0
    for path in _files_at("english-main"):
        text = _show("english-main", path)
        if not text:
            continue
        try:
            _, body = frontmatter.split(text)
            hs = anchors.headings(body)
        except Exception:
            continue  # 結構殘缺檔由 validate 負責，不是本測試的對象
        for _, t in hs:
            seen += 1
            m = narrow.search(t)
            assert anchors.existing_anchor(t) == (m.group(1) if m else None), (path, t)
    assert seen > 1000  # 防止「一個檔都沒掃到卻綠燈」的空轉
```

檔頂補 `import re`（若尚未匯入）。

- [ ] **Step 3: 跑測試確認通過**

```bash
source .venv/bin/activate && pytest tests/test_anchors_realworld.py -v
```

Expected: 全 PASS。若 `english-main` 分支不存在，先 `git fetch origin english-main:english-main` 再跑。

- [ ] **Step 4: Commit**

```bash
git add tests/test_anchors_realworld.py
git commit -m "test(anchors): 釘住放寬判準對真實語料為 no-op（zh + en 兩側）"
```

---

### Task 5: 管線不會自己長出 CJK anchor + check_repo 統計

**Files:**
- Modify: `scripts/zh_tw/check_repo.py:38`（`main()` 內，接在 scan-only 區塊之後）
- Test: `tests/test_anchor_single_source.py`（Task 2 建立的檔，附加）、`tests/test_check_repo.py`（既有檔；若不存在則附加到 `tests/test_anchor_single_source.py`）

**Interfaces:**
- Consumes: `anchors.existing_anchor`、`anchors.headings`（Task 1）
- Produces: `check_repo.cjk_anchor_hits(files: dict[str, str]) -> list[tuple[str, str]]` — 回傳 `(路徑, anchor id)`，id 含 CJK 才列入。

- [ ] **Step 1: 寫失敗測試**

附加到 `tests/test_anchor_single_source.py`：

```python
from scripts.zh_tw import check_repo


def test_pipeline_never_derives_a_cjk_anchor():
    """tier 3（衍生）一律由英文標題 slugify 而來，結構上不可能是 CJK。
    放寬判準只開啟「沿用人工寫進語料的 CJK id」，不開啟「自己產生」。"""
    zh = "# 中止與斷言 (Abort and Assert)\n\n## 斷言 (Assert)\n"
    en = "# Abort and Assert\n\n## Assert\n"
    out = anchors.inject(zh, en)
    ids = [anchors.existing_anchor(t) for _, t in anchors.headings(out)]
    assert ids == ["abort-and-assert", "assert"]


def test_existing_cjk_anchor_is_carried_forward_verbatim():
    """tier 1：已寫進語料的 id 是已發佈契約，原封不動。"""
    zh = "# 中止 {#中止}\n"
    en = "# Abort\n"
    out = anchors.inject(zh, en)
    assert anchors.existing_anchor(anchors.headings(out)[0][1]) == "中止"


def test_cjk_anchor_hits_reports_nothing_on_the_current_corpus():
    """baseline 0。數字一變就要有人看一眼是誰手動寫了 CJK anchor
    （比照 glossary scan-only 的 baseline 做法：沒有 baseline 的警告
    等於沒人看的噪音）。"""
    assert check_repo.cjk_anchor_hits(check_repo.collect()) == []


def test_cjk_anchor_hits_finds_a_planted_one():
    files = {"book/x.md": "# 中止 {#中止}\n"}
    assert check_repo.cjk_anchor_hits(files) == [("book/x.md", "中止")]
```

- [ ] **Step 2: 跑測試確認失敗**

```bash
source .venv/bin/activate && pytest tests/test_anchor_single_source.py -v
```

Expected: `test_cjk_anchor_hits_*` 兩條以 `AttributeError: module ... has no attribute 'cjk_anchor_hits'` FAIL；另兩條應該已 PASS（Task 1 之後行為就對了，它們是回歸守衛）。

- [ ] **Step 3: 實作**

在 `scripts/zh_tw/check_repo.py` 的 import 加入 `anchors`：

```python
from . import anchors, frontmatter, glossary, validate
```

在 `main()` 之前新增：

```python
def cjk_anchor_hits(files: dict[str, str]) -> list[tuple[str, str]]:
    """含 CJK 的顯式 anchor id。回傳 (路徑, id)，路徑排序。

    管線的衍生路徑（tier 3）由英文標題 slugify，結構上產不出 CJK id；
    所以這裡的命中一定是人手動寫進語料的。那不是錯誤——docusaurus 吃得下，
    沿用它也是正確的 tier 1 行為——但它會產出 CJK URL，值得有人看一眼。
    比照 scan-only：只提醒，不計入 exit code。
    """
    hits: list[tuple[str, str]] = []
    for path, text in sorted(files.items()):
        _, body = frontmatter.split(text)
        try:
            hs = anchors.headings(body)
        except Exception:
            continue  # 結構問題由 check_links / check_file 負責報
        for _, t in hs:
            aid = anchors.existing_anchor(t)
            if aid and validate.CJK.search(aid):
                hits.append((path, aid))
    return hits
```

在 `main()` 裡，緊接在 scan-only 那個 for 迴圈之後、gate 11 區塊之前插入：

```python
    # CJK anchor 統計：不計入 exit code（見 cjk_anchor_hits 的 docstring）。
    for path, aid in cjk_anchor_hits(files):
        print(f"{path}: ⚠️  CJK anchor id {{#{aid}}}", file=sys.stderr)
```

**不要改摘要行與 return 值** —— `0/0/0/0` 的格式與語意是既有驗收契約。

- [ ] **Step 4: 跑測試確認通過**

```bash
source .venv/bin/activate && pytest tests/test_anchor_single_source.py -v && python -m scripts.zh_tw.check_repo; echo "exit=$?"
```

Expected: 測試全 PASS；`check_repo` 印出 `連結問題 0 個，違禁詞共 0 處，簡體殘留字共 0 個，列表序號重複 0 處`，`exit=0`，且沒有任何 `⚠️  CJK anchor` 行。

- [ ] **Step 5: Commit**

```bash
git add scripts/zh_tw/check_repo.py tests/test_anchor_single_source.py
git commit -m "feat(check_repo): CJK anchor id 的 informational 統計（baseline 0）"
```

---

### Task 6: mutation 驗證與最終驗收

**Files:**
- 不改任何檔案（每個 mutation 都要還原）
- Test: 全套

**Interfaces:**
- Consumes: Task 1-5 的全部產出
- Produces: `tasks/notes.md` 的一則裁決紀錄與 `tasks/progress.md` 的 TODO 結清

- [ ] **Step 1: mutation A —— 把判準改回窄版**

把 `scripts/zh_tw/anchors.py` 的 `_ANCHOR` 暫時改回 `re.compile(r"\s*\{#([A-Za-z0-9_-]+)\}\s*$")`，然後：

```bash
source .venv/bin/activate && pytest tests/test_anchors_upstream_parity.py tests/test_anchors_slug.py -q
```

Expected: **FAIL**（至少 `test_parity_on_curated_cases`、`test_existing_anchor_accepts_cjk_id`）。還原：`git checkout -- scripts/zh_tw/anchors.py`。

- [ ] **Step 2: mutation B —— validate 改回自己持有 regex**

把 `scripts/zh_tw/validate.py` 的 `ANCHOR_SUFFIX = anchors.ANCHOR_SUFFIX` 暫時改回 `ANCHOR_SUFFIX = re.compile(r"\s*\{#[\w-]+\}\s*$")`，然後：

```bash
source .venv/bin/activate && pytest tests/test_anchor_single_source.py -q
```

Expected: **FAIL**（`test_validate_reuses_the_anchors_pattern_object` 與 `test_only_anchors_module_compiles_an_anchor_regex`）。還原：`git checkout -- scripts/zh_tw/validate.py`。

- [ ] **Step 3: mutation C —— 版本號漂移**

把 `tests/test_anchors_upstream_parity.py` 的 `UPSTREAM_VERSION` 暫時改成 `"3.11.0"`：

```bash
source .venv/bin/activate && pytest tests/test_anchors_upstream_parity.py::test_docusaurus_version_has_not_drifted -q
```

Expected: **FAIL**。還原：`git checkout -- tests/test_anchors_upstream_parity.py`。

- [ ] **Step 4: mutation D —— tier 3 允許 CJK**

把 `scripts/zh_tw/anchors.py` 的 `inject_report` 內

```python
    derived = slugify_all([en_h[i][1] for i in derive_idx], reserved=reserved)
```

暫時改成 `derived = slugify_all([zh_h[i][1] for i in derive_idx], reserved=reserved)`（改用中文標題衍生），然後：

```bash
source .venv/bin/activate && pytest tests/test_anchor_single_source.py::test_pipeline_never_derives_a_cjk_anchor -q
```

Expected: **FAIL**。還原：`git checkout -- scripts/zh_tw/anchors.py`。

- [ ] **Step 5: 確認四個 mutation 都已還原**

```bash
git status --porcelain scripts tests
```

Expected: 無輸出。

- [ ] **Step 6: 最終驗收（逐條對 spec 第七節）**

```bash
source .venv/bin/activate
pytest -q
python -m scripts.zh_tw.check_repo; echo "check_repo exit=$?"
git diff --stat book reference
grep -rn 'r["'"'"'][^"'"'"']*\\{#' scripts/zh_tw/ | grep -v anchors.py
```

Expected 逐條：
1. `pytest -q` 全綠，總數 = 531 + 7（Task 1）+ 5（Task 2）+ 5（Task 3）+ 2（Task 4）+ 4（Task 5）= **554**，0 skip。若實際數字不同，逐條核對是哪個測試沒被收集，不要調整期望值了事。
2. `check_repo` 印 `連結問題 0 個，違禁詞共 0 處，簡體殘留字共 0 個，列表序號重複 0 處`、`exit=0`。
3. `git diff --stat book reference` 無輸出。
4. 最後那條 `grep` 無輸出（`scripts/zh_tw/` 底下只剩 `anchors.py` 有 `{#` 的 regex 字面值）。

- [ ] **Step 7: 派 verifier（fresh context，不吃實作者自述）**

依 `~/.claude/docs/delegation-templates.md` 派 `verifier` agent：重新讀 `anchors.py` / `validate.py` / `fake.py` / `check_repo.py` 的實際改動，獨立重跑上面四條驗收指令，並**獨立確認四個 mutation 各自讓指定測試轉紅**。白名單：所有寫入/執行只能發生在 `$(mktemp -d)`，repo 內一律唯讀（mutation 驗證請在 `$(mktemp -d)` 的 `git worktree` 副本裡跑）。

- [ ] **Step 8: dual-review**

依 `dual-review` skill 跑內部 + 外部兩輪。Red Team Protocol 不適用（無使用者資料／auth／金流／刪改路徑，見 spec 第十節）。findings 分級：C 修完才算完成，B 進 `tasks/progress.md` 的 `## 觀察（不排程）`，A 不記。verdict 未出現 `Ship as-is` / `Ship with B-nits` 前不得標記完成。

- [ ] **Step 9: 收尾紀錄**

- `tasks/notes.md` 新增一則：T3 的原始動機為何消失、收斂後的不變式、各輪 findings 計數（如「ext C0/B1、int C0」）。
- `tasks/progress.md`：T3 從 `## 未結清 TODO 索引` 移除，`Recently Completed` 加一則；回報「開場 N → 收尾 M（使用者新增 K）」。
- Commit：

```bash
git add tasks/notes.md tasks/progress.md
git commit -m "docs(tasks): T3 結清 —— anchor id 判準收斂為單一真相來源"
```
