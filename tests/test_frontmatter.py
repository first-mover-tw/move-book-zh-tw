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


def test_join_indents_sequences_for_prettier():
    """pyyaml 預設把 list item 頂格輸出（`- Move`），prettier 要求縮排兩格。
    上游 2026-08 起在 frontmatter 加了 keywords/questions 兩個 list 欄位，
    於是每個經管線產出的檔案都永久停在 prettier 不合規——2026-09-01 掃描
    15 個含 `questions:` 的檔案，15 個全紅，1:1 對應。prettier 不在 CI 上，
    所以 PR #16/#17/#21 三批都沒被任何 gate 攔下。"""
    out = fm.join({"keywords": ["Move", "Sui"]}, "# 標題\n")
    assert "\n  - Move\n" in out
    assert "\n- Move\n" not in out


def test_join_does_not_wrap_long_plain_values():
    """prettier 對 plain scalar（無引號的值）一律留單行，不管多長；pyyaml 預設
    的 80 欄折行對它們就是純粹的不合規（2026-09-01 實測 glossary/manifest 兩檔）。

    範圍限定在 plain scalar 是刻意的：值含 `: ` 時 YAML 強制加引號，而 prettier
    對 quoted scalar 反過來會折行（greedy fill + east-asian 顯示寬度）。那半不在
    這裡斷言，也不在 python 端複製 —— 由 translate workflow 的 `prettier --write`
    收斂（見 _PrettierDumper 的 docstring）。舊版本測試斷言「長值一律單行」，
    等於把錯誤前提釘死，正是它讓 constants/references 兩檔從綠變紅。
    """
    long_value = "Learn about addresses in Sui — " + "32-byte unique identifiers " * 4 + "here"
    assert ": " not in long_value  # 前提：這個值不會被 YAML 加引號
    out = fm.join({"description": long_value}, "# 標題\n")
    assert f"description: {long_value}\n" in out


def test_join_round_trips_nested_structures():
    """縮排/引號/寬度三個調整都不得改變語意：上游的 goal 欄位是巢狀
    dict + list，dump 壞掉會靜默弄丟 frontmatter 內容。"""
    meta = {
        "title": "地址 (Address)",
        "keywords": ["Move", "Sui"],
        "goal": {
            "description": "Reader understands addresses: the 32-byte kind",
            "requires": [
                {"has_frontmatter": ["title", "description"], "label": "Has fields"},
                {"min_words": 50, "label": "Needs depth"},
            ],
        },
    }
    parsed, body = fm.split(fm.join(meta, "# 標題\n"))
    assert parsed == meta
    assert body == "# 標題\n"
