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
