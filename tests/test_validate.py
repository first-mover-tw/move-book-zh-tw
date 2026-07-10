from scripts.zh_tw import validate

EN = '---\ndescription: "Vectors in Move."\n---\n\n# Vector\n\n```move\nx\n```\n\n## Syntax\n\ntext\n'
ZH = '---\ndescription: "Move 中的向量。"\n---\n\n# 向量 {#vector}\n\n```move\nx\n```\n\n## 語法 {#syntax}\n\n文字\n'


def test_clean_file_passes():
    assert validate.check_file(ZH, EN) == []


def test_detects_truncation_via_heading_sequence():
    """reference/variables.md 的失效模式。"""
    truncated = '---\ndescription: "Move 中的向量。"\n---\n\n# 向量 {#vector}\n'
    errs = validate.check_file(truncated, EN)
    assert any("標題" in e for e in errs)


def test_detects_missing_code_fence():
    no_code = '---\ndescription: "Move 中的向量。"\n---\n\n# 向量 {#vector}\n\n## 語法 {#syntax}\n\n文字\n'
    errs = validate.check_file(no_code, EN)
    assert any("fence" in e or "程式碼" in e for e in errs)


def test_detects_untranslated_description():
    """D3：89 個檔案的 description 仍是英文。"""
    en_desc = ZH.replace("Move 中的向量。", "Vectors in Move.")
    errs = validate.check_file(en_desc, EN)
    assert any("description" in e for e in errs)


def test_detects_frontmatter_key_mismatch():
    en = '---\ndescription: "d"\nunlisted: true\n---\n\n# T\n'
    zh = '---\ndescription: "描述"\n---\n\n# 標 {#t}\n'
    errs = validate.check_file(zh, en)
    assert any("frontmatter" in e for e in errs)


def test_detects_dropped_existing_anchor():
    prev = '---\ndescription: "描述"\n---\n\n# 標 {#custom-id}\n'
    en = '---\ndescription: "d"\n---\n\n# T\n'
    zh = '---\ndescription: "描述"\n---\n\n# 標 {#t}\n'
    errs = validate.check_file(zh, en, prev)
    assert any("custom-id" in e for e in errs)


def test_detects_glossary_violation():
    en = '---\ndescription: "d"\n---\n\n# T\n'
    zh = '---\ndescription: "描述"\n---\n\n# 標 {#t}\n\n這個函數\n'
    errs = validate.check_file(zh, en)
    assert any("函數" in e for e in errs)


def test_check_links_resolves_internal_anchors():
    files = {
        "book/a.md": "# A {#a}\n\n[see](./b#target)\n",
        "book/b.md": "# B {#target}\n",
    }
    assert validate.check_links(files) == []


def test_check_links_reports_unresolvable_anchor():
    files = {"book/a.md": "# A {#a}\n\n[see](./b#missing)\n", "book/b.md": "# B {#target}\n"}
    errs = validate.check_links(files)
    assert len(errs) == 1 and "missing" in errs[0]


def test_check_links_strips_query_string():
    """book/move-basics/visibility.md 有一條 ?highlight=native 的連結。
    不剝掉 query string 就會產生假陽性。"""
    files = {
        "book/a.md": "# A {#a}\n\n[x](./b?highlight=native#target)\n",
        "book/b.md": "# B {#target}\n",
    }
    assert validate.check_links(files) == []


def test_check_links_ignores_external_urls():
    files = {"book/a.md": "# A {#a}\n\n[x](https://docs.suins.io/mvr-cli#installation)\n"}
    assert validate.check_links(files) == []
