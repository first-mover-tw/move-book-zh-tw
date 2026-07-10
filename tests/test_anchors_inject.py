import pytest
from markdown_it import MarkdownIt

from scripts.zh_tw import anchors

_MD = MarkdownIt("commonmark")


def _heading_level_seq(body: str) -> list[int]:
    return [int(t.tag[1]) for t in _MD.parse(body) if t.type == "heading_open"]


def _has_hr(body: str) -> bool:
    return any(t.type == "hr" for t in _MD.parse(body))


def _anchor_ids(body: str) -> list[str]:
    """每個標題各自求一次 anchor id(anchors._ANCHOR 沒有 re.MULTILINE，
    對整份文字 findall 只會抓到最後一行，不能拿來對多標題文件用)。"""
    return [
        aid
        for _, text in anchors.headings(body)
        if (aid := anchors.existing_anchor(text)) is not None
    ]


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


# --- Finding 1: 衍生 slug 不得撞上 carried-forward anchor ---


def test_inject_derived_slug_does_not_collide_with_carried_anchor():
    zh = "## 設定\n\n## 別的\n"
    en = "## Setup\n\n## Other\n"
    prev = "## 舊標題\n\n## 別的 {#setup}\n"
    out = anchors.inject(zh, en, prev)

    ids = _anchor_ids(out)
    assert len(ids) == len(set(ids)), f"重複 anchor id: {ids}"
    assert "{#setup}" in out  # carried 保留在原本擁有它的標題上
    # 第二個標題(索引 1)必須保有 carried anchor `setup`
    assert out.splitlines()[-1] == "## 別的 {#setup}"


def test_inject_carried_anchor_equals_other_headings_natural_slug_carried_first():
    """carried anchor 恰好等於「另一個標題」衍生後會產生的 slug；carried 排前面。"""
    zh = "## 設定\n\n## 別的\n"
    en = "## Other\n\n## Setup\n"  # 注意：英文順序對調，衍生 slug 分別是 other / setup
    prev = "## 舊標題 {#setup}\n\n## 舊別的\n"  # 索引 0 carried = setup
    out = anchors.inject(zh, en, prev)

    ids = _anchor_ids(out)
    assert len(ids) == len(set(ids)), f"重複 anchor id: {ids}"
    lines = out.splitlines()
    assert lines[0] == "## 設定 {#setup}"
    assert lines[-1] != "## 別的 {#setup}"


def test_inject_carried_anchor_equals_other_headings_natural_slug_carried_second():
    zh = "## 設定\n\n## 別的\n"
    en = "## Setup\n\n## Other\n"
    prev = "## 舊設定\n\n## 舊別的 {#setup}\n"  # 索引 1 carried = setup
    out = anchors.inject(zh, en, prev)

    ids = _anchor_ids(out)
    assert len(ids) == len(set(ids)), f"重複 anchor id: {ids}"
    lines = out.splitlines()
    assert lines[-1] == "## 別的 {#setup}"
    assert lines[0] != "## 設定 {#setup}"


def test_inject_raises_duplicate_anchor_when_tier1_anchors_collide():
    """兩個標題在中文檔裡本身就已經帶有相同 anchor(tier 1)—— 衍生階段救不了，必須顯式炸掉。"""
    zh = "## 設定 {#dup}\n\n## 別的 {#dup}\n"
    en = "## Setup\n\n## Other\n"
    with pytest.raises(anchors.DuplicateAnchor):
        anchors.inject(zh, en)


# --- Finding 2: setext 標題正規化為 ATX，底線行整行移除 ---


def test_inject_normalizes_setext_level2_no_phantom_hr():
    zh = "標題\n----\n\n內文\n"
    en = "Title\n-----\n\nBody\n"
    out = anchors.inject(zh, en)

    assert _heading_level_seq(out) == _heading_level_seq(zh) == [2]
    assert not _has_hr(out)
    assert "----" not in out
    assert out.splitlines()[0] == "## 標題 {#title}"


def test_inject_normalizes_setext_level1_no_phantom_hr():
    zh = "標題\n====\n\n內文\n"
    en = "Title\n=====\n\nBody\n"
    out = anchors.inject(zh, en)

    assert _heading_level_seq(out) == _heading_level_seq(zh) == [1]
    assert not _has_hr(out)
    assert "====" not in out
    assert out.splitlines()[0] == "# 標題 {#title}"


# --- Finding 3: CRLF 行尾必須原樣保留 ---


def test_inject_preserves_crlf_line_ending():
    zh = "# 標題\r\n\r\n內文\r\n"
    en = "# Title\r\n\r\nBody\r\n"
    out = anchors.inject(zh, en)

    assert out.splitlines(keepends=True)[0] == "# 標題 {#title}\r\n"
    # 檔案裡不該出現裸的 \n(沒有前導 \r)
    assert "\r\n" in out
    bare_lf = out.replace("\r\n", "")
    assert "\n" not in bare_lf, "混用行尾: 標題行被降級為 LF"


# --- Round-trip: 混合 ATX 標題、fence、HTML 註解 ---


# --- Finding 4: 巢狀標題(blockquote/list item)必須顯式炸掉，不得靜默拉升到頂層 ---


def test_inject_raises_on_atx_heading_inside_blockquote():
    with pytest.raises(anchors.NestedHeading):
        anchors.inject("> ## 標題\n", "> ## Title\n")


def test_inject_raises_on_setext_heading_inside_blockquote():
    with pytest.raises(anchors.NestedHeading):
        anchors.inject("> 標題\n> ----\n", "> Title\n> -----\n")


def test_inject_raises_on_heading_inside_list_item():
    with pytest.raises(anchors.NestedHeading):
        anchors.inject("- ## 標題\n", "- ## Title\n")


def test_inject_raises_on_nested_heading_only_in_english():
    """中文乾淨,但英文有巢狀標題——兩邊都要檢查。"""
    with pytest.raises(anchors.NestedHeading):
        anchors.inject("# 標題\n", "> # Title\n")


def test_inject_blockquote_without_heading_survives_untouched():
    zh = "> 一般引言\n>\n> 內文\n"
    en = "> A normal quote\n>\n> Body\n"
    out = anchors.inject(zh, en)
    assert out == zh


def test_inject_fenced_code_that_looks_like_nested_heading_does_not_raise():
    zh = "# 標題\n\n```\n> ## 看起來像標題\n```\n"
    en = "# Title\n\n```\n> ## looks like heading\n```\n"
    out = anchors.inject(zh, en)
    assert "{#title}" in out
    assert "> ## 看起來像標題" in out


def test_inject_nested_heading_error_message_contains_heading_text():
    with pytest.raises(anchors.NestedHeading, match="巢狀標題"):
        anchors.inject("> ## 巢狀標題\n", "> ## Nested Title\n")


def test_inject_roundtrip_heading_levels_and_anchor_count():
    zh = (
        "# 標題一\n\n"
        "<!-- # 不是標題 -->\n\n"
        "```move\n# 也不是標題\n```\n\n"
        "## 標題二\n\n內文\n"
    )
    en = (
        "# Title One\n\n"
        "<!-- # not a heading -->\n\n"
        "```move\n# not a heading either\n```\n\n"
        "## Title Two\n\nBody\n"
    )
    out = anchors.inject(zh, en)

    zh_levels = [lvl for _, lvl in anchors.heading_lines(zh)]
    out_levels = [lvl for _, lvl in anchors.heading_lines(out)]
    assert out_levels == zh_levels

    out_headings = anchors.headings(out)
    assert len(out_headings) == len(anchors.headings(zh))
    for _, text in out_headings:
        ids = anchors._ANCHOR.findall(text)
        assert len(ids) == 1, f"標題應恰好帶一個 anchor: {text!r}"
