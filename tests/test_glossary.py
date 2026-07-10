import subprocess
from pathlib import Path

from scripts.zh_tw import frontmatter, glossary

_REPO_ROOT = Path(__file__).resolve().parent.parent


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


def test_scan_ignores_nested_fence_inside_four_backtick_fence():
    body = "````\n```\n函數\n```\n````\n"
    assert glossary.scan(body) == {}


def test_enforce_leaves_four_backtick_fence_byte_identical():
    body = "````\n```\n函數\n```\n````\n"
    assert glossary.enforce(body) == body


def test_scan_ignores_tilde_fence():
    body = "~~~\n函數\n~~~\n"
    assert glossary.scan(body) == {}


def test_enforce_leaves_tilde_fence_untouched():
    body = "~~~\n函數\n~~~\n"
    assert glossary.enforce(body) == body


def test_indented_code_block_is_untouched():
    body = "prose\n\n    函數\n\nmore prose\n"
    assert glossary.scan(body) == {}
    assert glossary.enforce(body) == body


def test_html_comment_is_scanned_and_replaced():
    # 刻意行為：HTML 註解不是程式碼。草稿裡被註解掉的中文敘述仍要正規化
    # 用詞，否則之後取消註解時可能殘留大陸慣用語。
    body = "<!--\n這個函數會返回一個值\n-->\n"
    assert glossary.scan(body) == {"函數": 1, "返回": 1}
    assert glossary.enforce(body) == "<!--\n這個函式會回傳一個值\n-->\n"


def test_inline_code_protected_but_surrounding_prose_replaced():
    body = "呼叫 `函數` 之後函數才會返回\n"
    out = glossary.enforce(body)
    assert "`函數`" in out  # inline code 未被改動
    assert "之後函式才會回傳" in out  # 周圍的中文有被替換


def test_corpus_banned_term_total_is_126():
    files = [
        p
        for base in ("book", "reference")
        for p in (_REPO_ROOT / base).rglob("*.md")
    ]
    total = 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        _, body = frontmatter.split(text)
        total += sum(glossary.scan(body).values())
    assert total == 126
