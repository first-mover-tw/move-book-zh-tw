"""與消費者 docusaurus 的 {#id} 判準對拍。

判準只要還是「我維護的一份推論」，就會有第五輪(lessons L23)。這裡不推論:
把上游 regex 原文移植過來對拍，並用版本漂移守衛逼人在升級時回去看一眼。

誠實的範圍聲明：UPSTREAM_REGEX（下面 compile 出來的版本）與
anchors._ANCHOR 是同一個 pattern 字串、upstream_parse_id() 與
anchors.existing_anchor() 是逐行相同的邏輯，所以 CASES / fuzz 對拍在
數學上是恆等式，測不出「pattern 字串本身抄錯上游」——它只抓得到
「_ANCHOR 之後漂離了這個字串」的迴歸。真正釘住「這串字串等不等於上游
原始碼」的是 UPSTREAM_PATTERN 常數 + test_docusaurus_version_has_not_drifted
裡的身分斷言，加上人工回看 markdownHeadingIdUtils.ts 原始碼。
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

# 上游 pattern 的 Python 移植，以**字串**形式釘死。刻意不在這裡 re.compile ——
# 一旦 compile 並拿來對拍，這個檔案就成了同一個不變式的第二份實作，
# 而那正是整條分支要消滅的東西（見 spec 第三節）。
UPSTREAM_PATTERN = r"\s*\{#((?:.(?!\{#|\}))*.)\}$"
UPSTREAM_REGEX = re.compile(UPSTREAM_PATTERN)


def upstream_parse_id(heading: str) -> str | None:
    """上游 parseMarkdownHeadingId 的 id 部分。上游對 heading 的前提是
    「已被 markdown 解析器 trim 過」，所以這裡先 rstrip。"""
    m = UPSTREAM_REGEX.search(heading.rstrip())
    return m.group(1).strip() if m else None


def test_docusaurus_version_has_not_drifted():
    """升級 docusaurus 時這條會紅 —— 去看 markdownHeadingIdUtils.ts 的
    customHeadingIdRegex 有沒有變，確認後再改 UPSTREAM_VERSION。
    沒有這條守衛，上游改了判準我們不會知道(靜默腐化)。

    第二個斷言是這個檔案裡唯一不是恆等式的檢查：CASES / fuzz 對拍測的是
    「_ANCHOR 有沒有漂離 UPSTREAM_PATTERN」，這條測的是「UPSTREAM_PATTERN
    這串字串本身有沒有漂離 anchors._ANCHOR 目前的 pattern」——兩者合起來
    才覆蓋得到 anchors._ANCHOR 被改動但沒人回頭核對上游原始碼的情況。"""
    pkg = json.loads(Path("site/package.json").read_text(encoding="utf-8"))
    assert pkg["dependencies"]["@docusaurus/core"] == UPSTREAM_VERSION
    assert anchors.ANCHOR_SUFFIX.pattern == UPSTREAM_PATTERN


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
# 否則負面結果沒有意義(lessons L15 推論：fuzz 的負面結果只在 generator
# 生得出該類輸入時才有效)。test_generator_covers_the_curated_repros 驗這件事。
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
    """誠實聲明：UPSTREAM_REGEX 與 anchors._ANCHOR 目前是同一個 pattern
    字串，upstream_parse_id() 與 anchors.existing_anchor() 逐行邏輯相同，
    所以這 20000 次 fuzz 對拍是恆等式——它能抓到的是「_ANCHOR 漂離了
    UPSTREAM_PATTERN 這個釘死的字串」，抓不到「這個字串本身就抄錯了
    上游」。後者由 test_docusaurus_version_has_not_drifted 的
    pattern == UPSTREAM_PATTERN 斷言 + 人工回看上游原始碼負責，
    這裡的高次數不代表已經驗證過正確性本身。"""
    rng = random.Random(20260906)
    for _ in range(20000):
        s = _gen(rng)
        assert anchors.existing_anchor(s) == upstream_parse_id(s), repr(s)
