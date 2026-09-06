"""與消費者 docusaurus 的 {#id} 判準對拍。

判準只要還是「我維護的一份推論」，就會有第五輪(lessons L23)。這裡不推論:
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
    沒有這條守衛，上游改了判準我們不會知道(靜默腐化)。"""
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
    rng = random.Random(20260906)
    for _ in range(20000):
        s = _gen(rng)
        assert anchors.existing_anchor(s) == upstream_parse_id(s), repr(s)
