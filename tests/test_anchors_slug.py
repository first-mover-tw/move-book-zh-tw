import re
from pathlib import Path

import commonmark
import pytest

from scripts.zh_tw import anchors, frontmatter

_REPO_ROOT = Path(__file__).resolve().parent.parent

_H_TAG = re.compile(r"<h([1-6])>(.*?)</h\1>", re.S)
_TAG = re.compile(r"<[^>]+>")


def _reference_headings(body: str) -> list[tuple[int, str]]:
    """用 commonmark 參考渲染器算出 (level, text) 清單，剝掉 inline 標籤。"""
    html = commonmark.commonmark(body)
    out = []
    for m in _H_TAG.finditer(html):
        level = int(m.group(1))
        text = _TAG.sub("", m.group(2)).strip()
        out.append((level, text))
    return out


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
    _, body = frontmatter.split(body)
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
    _, body = frontmatter.split(body)
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


# --- 差分測試：與 commonmark 參考渲染器比對 --------------------------------

_DIFFERENTIAL_CASES = [
    "# A\n\t```\nhidden?\n```\n## B\n",
    "# A\n```\nhidden\n\t```\nstill?\n```\n## B\n",
    "# A\n```\nExample:\n    ```\n## fake?\n```\n## B\n",
    "# A\n<!-- ## Hidden\n```\nx\n```\n-->\n## B\n",
    "# A\n\n~~~move\n# not heading\n~~~\n\n## B\n",
    "# A\n    <!--\n\n## Real\n",
]


@pytest.mark.parametrize("body", _DIFFERENTIAL_CASES)
def test_headings_matches_commonmark_reference(body):
    assert anchors.headings(body) == _reference_headings(body)


def test_heading_lines_line_indices():
    body = "# A\n\n```\nfake ## heading\n```\n\n<!--\n## hidden\n-->\n\n## B\n"
    #      0    1  2   3               4  5   6   7        8   9   10
    assert anchors.heading_lines(body) == [(0, 1), (10, 2)]


def test_visible_lines_excludes_fence_indented_and_html_block():
    body = (
        "# A\n"
        "\n"
        "```\n"
        "fenced content\n"
        "```\n"
        "\n"
        "    indented code\n"
        "\n"
        "<!--\n"
        "hidden html\n"
        "-->\n"
        "\n"
        "## B\n"
    )
    lines = body.splitlines()
    result = anchors.visible_lines(body)
    result_idxs = {i for i, _ in result}
    for i, text in enumerate(lines):
        if text in ("fenced content", "    indented code", "hidden html") or text in ("```", "<!--", "-->"):
            assert i not in result_idxs, f"line {i!r} ({text!r}) should be hidden"
    assert (0, "# A") in result
    assert (12, "## B") in result


def test_fence_lines_one_time_witness():
    body = (_REPO_ROOT / "book/programmability/one-time-witness.md").read_text(encoding="utf-8")
    _, body = frontmatter.split(body)
    assert anchors.fence_lines(body) == 4


def test_headings_one_time_witness_body_only():
    body = (_REPO_ROOT / "book/programmability/one-time-witness.md").read_text(encoding="utf-8")
    _, body = frontmatter.split(body)
    texts = [t for _, t in anchors.headings(body)]
    assert texts == [
        "一次性見證 (One Time Witness)",
        "定義",
        "強制執行 OTW",
        "總結",
    ]


def test_headings_raises_when_passed_full_document_with_frontmatter():
    full_doc = '---\ndescription: "x"\n---\n\n# Real\n'
    with pytest.raises(anchors.FrontmatterPassedIn):
        anchors.headings(full_doc)


def test_heading_lines_raises_when_passed_full_document_with_frontmatter():
    full_doc = '---\ndescription: "x"\n---\n\n# Real\n'
    with pytest.raises(anchors.FrontmatterPassedIn):
        anchors.heading_lines(full_doc)


def test_visible_lines_raises_when_passed_full_document_with_frontmatter():
    full_doc = '---\ndescription: "x"\n---\n\n# Real\n'
    with pytest.raises(anchors.FrontmatterPassedIn):
        anchors.visible_lines(full_doc)


def test_fence_lines_raises_when_passed_full_document_with_frontmatter():
    full_doc = '---\ndescription: "x"\n---\n\n# Real\n```\nx\n```\n'
    with pytest.raises(anchors.FrontmatterPassedIn):
        anchors.fence_lines(full_doc)
