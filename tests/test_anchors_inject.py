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
