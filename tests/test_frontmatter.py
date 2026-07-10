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
