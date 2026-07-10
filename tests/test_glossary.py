from scripts.zh_tw import glossary


def test_enforce_replaces_mainland_terms():
    assert glossary.enforce("這個函數會返回一個值") == "這個函式會回傳一個值"


def test_enforce_skips_fenced_code_block():
    body = "呼叫函數\n\n```move\n// 函數 stays\n```\n"
    out = glossary.enforce(body)
    assert "呼叫函式" in out
    assert "// 函數 stays" in out


def test_enforce_skips_inline_code():
    assert glossary.enforce("使用 `函數` 這個詞") == "使用 `函數` 這個詞"


def test_enforce_handles_multiple_terms():
    assert glossary.enforce("循環中調用變量") == "迴圈中呼叫變數"


def test_scan_counts_violations_outside_code():
    body = "函數\n\n```\n函數\n```\n\n`函數`\n"
    assert glossary.scan(body) == {"函數": 1}


def test_scan_returns_empty_when_clean():
    assert glossary.scan("這是乾淨的中文") == {}


def test_prompt_rules_lists_every_pair():
    rules = glossary.prompt_rules()
    for bad, good in glossary.load().items():
        assert f"{good}" in rules and f"{bad}" in rules
