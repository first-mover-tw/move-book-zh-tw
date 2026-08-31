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


def test_join_always_ends_with_newline():
    """backend 常吐出沒有結尾換行的 body，八道 gate 都是內容檢查、prettier
    又不在 CI 上，於是「檔尾缺換行」每一輪自動翻譯都原樣長回來
    （2026-08-31 連兩批 PR #16/#17 共 6 檔）。join 是所有 .md 產出的唯一
    匯流點，補在這裡才是一次修完。"""
    assert fm.join({"description": "你好"}, "# 標題").endswith("標題\n")
    assert fm.join({}, "# 標題").endswith("標題\n")


def test_join_does_not_invent_a_newline_for_empty_output():
    """空字串維持空字串：憑空生出一個只有換行的檔案不是修復，是製造差異。"""
    assert fm.join({}, "") == ""


def test_join_does_not_stack_newlines():
    assert fm.join({}, "# 標題\n") == "# 標題\n"
    assert fm.join({"description": "你好"}, "# 標題\n").endswith("標題\n")
    assert not fm.join({"description": "你好"}, "# 標題\n").endswith("\n\n")
