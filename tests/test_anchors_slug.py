from pathlib import Path

from scripts.zh_tw import anchors

_REPO_ROOT = Path(__file__).resolve().parent.parent


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


def test_headings_one_time_witness_html_commented_fences_and_headings():
    """book/programmability/one-time-witness.md 有 11 個 fence marker 行（奇數），
    因為第 41-124 行被包在一個 HTML comment 裡，內含 7 個。該 comment 內還藏著
    兩個看起來像標題的行（`## Solving the Coin Problem`、`## Questions`），
    但它們永遠不會被渲染出來，headings() 必須忽略它們。
    """
    body = (_REPO_ROOT / "book/programmability/one-time-witness.md").read_text(encoding="utf-8")
    result = anchors.headings(body)
    texts = [t for _, t in result]
    assert texts == [
        "一次性見證 (One Time Witness)",
        "定義",
        "強制執行 OTW",
        "總結",
    ]
    assert "Solving the Coin Problem" not in texts
    assert "Questions" not in texts


def test_headings_references_still_seven():
    """references.md 的 fence 數量是偶數（沒有奇偶錯位的警訊），確認修好
    comment-aware 掃描後，這個原本就解析正確的檔案不會被改壞。
    """
    body = (_REPO_ROOT / "book/move-basics/references.md").read_text(encoding="utf-8")
    result = anchors.headings(body)
    assert len(result) == 7


def test_headings_tilde_fence_hides_contents():
    body = "# Real\n\n~~~move\n# not a heading\n~~~\n\n## Also Real\n"
    assert anchors.headings(body) == [(1, "Real"), (2, "Also Real")]


def test_headings_info_string_does_not_close_backtick_fence():
    body = "# Real\n\n```\n# not a heading\n```move\n# also not a heading\n```\n\n## Also Real\n"
    assert anchors.headings(body) == [(1, "Real"), (2, "Also Real")]


def test_headings_inline_comment_does_not_swallow_rest_of_file():
    body = "# Real\n\n<!-- comment -->\n\n## Also Real\n"
    assert anchors.headings(body) == [(1, "Real"), (2, "Also Real")]


def test_headings_fence_content_html_comment_marker_is_literal_code():
    body = "# Real\n\n```\n<!-- not a comment start -->\n```\n\n## Also Real\n"
    assert anchors.headings(body) == [(1, "Real"), (2, "Also Real")]


def test_slugify_all_dedup_when_generated_suffix_collides_with_literal_slug():
    assert len(set(anchors.slugify_all(["Setup-1", "Setup", "Setup"]))) == 3
    assert len(set(anchors.slugify_all(["Setup", "Setup-1", "Setup"]))) == 3


def test_headings_four_space_indented_fence_does_not_close():
    """4-space-indented fence marker is code-block content, not a fence delimiter."""
    body = "# A\n```\nExample of markdown:\n    ```\n## fake heading now visible?\n```\n## B\n"
    assert anchors.headings(body) == [(1, "A"), (2, "B")]
    assert anchors.fence_lines(body) == 2


def test_headings_three_space_indented_fence_is_real_fence():
    """3-space-indented fence marker is still a real fence (closes)."""
    body = "# A\n```\nHidden\n   ```\n## B\n"
    assert anchors.headings(body) == [(1, "A"), (2, "B")]


def test_headings_four_space_indented_fence_marker_does_not_toggle():
    """4-space-indented fence marker does not toggle fence state."""
    body = "# A\n```\nContent\n    ```\nMore content\n```\n## B\n"
    # The 4-space marker doesn't close, so everything up to the real closing ``` is hidden
    assert anchors.headings(body) == [(1, "A"), (2, "B")]


def test_headings_three_space_indented_atx_is_recognized():
    """ATX heading indented 3 spaces is recognized."""
    body = "# A\n   ## B\n# C\n"
    assert anchors.headings(body) == [(1, "A"), (2, "B"), (1, "C")]


def test_headings_four_space_indented_atx_is_not_recognized():
    """ATX heading indented 4 spaces is NOT recognized (indented code block)."""
    body = "# A\n    ## B\n# C\n"
    assert anchors.headings(body) == [(1, "A"), (1, "C")]


def test_headings_four_space_indented_tilde_fence():
    """4-space-indented tilde fence is not a delimiter."""
    body = "# A\n~~~\nContent\n    ~~~\nMore\n~~~\n## B\n"
    assert anchors.headings(body) == [(1, "A"), (2, "B")]
