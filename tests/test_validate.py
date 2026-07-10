import subprocess

import pytest

from scripts.zh_tw import anchors, frontmatter, validate

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


# --- Finding 1 / gate 5: phantom slug from unioning explicit id with derived slug ---


def test_check_links_rejects_phantom_slug_from_explicit_heading():
    """Docusaurus 只為帶 {#custom-id} 的標題發出 custom-id 這一個 id，
    不會同時發出從標題文字衍生出的 slug。連到那個衍生 slug 的連結必須報錯，
    否則會通過驗證但在真實網站 404。"""
    files = {"a.md": "# 標題 {#custom-id}\n\n[link](#標題)\n"}
    errs = validate.check_links(files)
    assert len(errs) == 1 and "標題" in errs[0]


def test_check_links_explicit_anchor_still_resolves():
    files = {"a.md": "# 標題 {#custom-id}\n\n[link](#custom-id)\n"}
    assert validate.check_links(files) == []


def test_check_links_derived_slug_still_resolves_without_explicit_id():
    files = {"a.md": "# 標題 XY\n\n[link](#標題-xy)\n"}
    assert validate.check_links(files) == []


def test_check_links_derived_slug_dedup_matches_inject():
    """兩個標題文字衍生出同一個 base slug 時，第二個要靠 -1 尾碼消歧，
    順序與 slugify_all() 遞增去重的規則要一致（inject() 也是靠這個規則
    決定衍生 anchor，兩邊的去重結果不能各說各話）。"""
    files = {
        "a.md": "# 標題\n\n## 標題\n\n[first](#標題)\n\n[second](#標題-1)\n"
    }
    assert validate.check_links(files) == []


# --- Finding 2 / gate 6: anchor reassignment, not just disappearance ---


def test_gate6_detects_reassignment_when_heading_moves():
    prev_en = "# H0\n\n## Alpha\n\n## Beta\n"
    prev_zh = "# H0 {#h0}\n\n## 甲 {#alpha-id}\n\n## 乙 {#beta-id}\n"
    en = "# H0\n\n## Gamma\n\n## Alpha\n"

    # Alpha moved from heading index 1 to index 2; the Chinese heading at
    # index 2 correctly carries {#alpha-id} forward.
    zh_ok = "# H0 {#h0}\n\n## 丙\n\n## 甲 {#alpha-id}\n"
    assert validate.check_file(zh_ok, en, prev_zh, prev_en) == []

    # Same move, but the Chinese body left the id on the wrong heading (or
    # dropped it) -- gate 6 must name the id.
    zh_bad = "# H0 {#h0}\n\n## 甲 {#alpha-id}\n\n## 丙\n"
    errs = validate.check_file(zh_bad, en, prev_zh, prev_en)
    assert any("alpha-id" in e for e in errs)


def test_gate6_retirement_produces_no_error():
    prev_en = "# H0\n\n## Alpha\n\n## Beta\n"
    prev_zh = "# H0 {#h0}\n\n## 甲 {#alpha-id}\n\n## 乙 {#beta-id}\n"
    en = "# H0\n\n## Gamma\n"  # Alpha's English heading is gone entirely.
    zh = "# H0 {#h0}\n\n## 丙\n"
    assert validate.check_file(zh, en, prev_zh, prev_en) == []


def test_gate6_falls_back_to_disappearance_check_without_prev_en():
    prev_en = "# H0\n\n## Alpha\n\n## Beta\n"
    prev_zh = "# H0 {#h0}\n\n## 甲 {#alpha-id}\n\n## 乙 {#beta-id}\n"
    en = "# H0\n\n## Gamma\n"
    zh = "# H0 {#h0}\n\n## 丙\n"
    errs = validate.check_file(zh, en, prev_zh, "")
    assert any("alpha-id" in e for e in errs)
    assert any("beta-id" in e for e in errs)


MERGE_BASE = "f2c0a93e1a0422078d3d051e4410ac3edc612016"
PRE_FIX = "0d4b8bea77f1a6195b589ded4067d287adb4379a"


def _show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def test_gate6_real_data_ownership_and_epoch_and_time():
    """Feeds real merge-base/english-main/pre-fix content through inject(),
    exercising the actual identity-carry path (commits 90043922, e24322bc)
    rather than a hand-rolled scenario."""
    cases = {
        "book/object/ownership.md": (
            """# 所有權 (Ownership)

Sui 為物件引入了五種不同的所有權類型。

## 帳戶所有者 (或單一所有者) (Account Owner / Single Owner)

內容。

## 共享狀態 (Shared State)

內容。

## 派對物件 (Party Objects)

新章節內容。

## 不可變 (凍結) 狀態 (Immutable / Frozen State)

內容。

## 物件所有者 (Object Owner)

內容。

## 總結 (Summary)

內容。

## 下一步 (Next Steps)

內容。
""",
            "immutable-frozen-object",
            "## 不可變 (凍結) 狀態 (Immutable / Frozen State)",
            "## 派對物件 (Party Objects)",
        ),
        "book/programmability/epoch-and-time.md": (
            """# Epoch 與時間 (Epoch and Time)

內容。

## Epoch (週期)

內容。

## 時間 (Time)

內容。

## 測試 (Testing)

內容。

## 總結 (Summary)

新內容。

## 延伸閱讀 (Further Reading)

新內容。
""",
            "clock",
            "## 時間 (Time)",
            "## 測試 (Testing)",
        ),
    }
    for path, (zh_body, anchor_id, from_heading, to_heading) in cases.items():
        prev_en_full = _show(MERGE_BASE, path)
        prev_zh_full = _show(PRE_FIX, path)
        en_full = _show("english-main", path)
        if not prev_en_full or not prev_zh_full or not en_full:
            pytest.skip(f"{path} unavailable in this checkout")
        _, prev_en_body = frontmatter.split(prev_en_full)
        prev_zh_meta, prev_zh_body = frontmatter.split(prev_zh_full)
        _, en_body = frontmatter.split(en_full)

        out = anchors.inject(zh_body, en_body, prev_zh_body, prev_en_body)
        zh_text_out = frontmatter.join(prev_zh_meta, out)
        errs = validate.check_file(zh_text_out, en_full, prev_zh_full, prev_en_full)
        assert not any("anchor" in e for e in errs), (path, errs)

        # Mutate: move the tracked anchor off its correct heading.
        mutated = out.replace(f"{from_heading} {{#{anchor_id}}}", from_heading, 1)
        mutated = mutated.replace(to_heading, f"{to_heading} {{#{anchor_id}}}", 1)
        mutated_text = frontmatter.join(prev_zh_meta, mutated)
        m_errs = validate.check_file(mutated_text, en_full, prev_zh_full, prev_en_full)
        assert any(anchor_id in e and "anchor" in e for e in m_errs), (path, m_errs)


# --- Finding 3 / gate 8: simplified glyphs in prose ---


@pytest.mark.parametrize("ch", ["个", "麽", "况", "这", "种"])
def test_gate8_flags_simplified_chars(ch):
    body = f"這是一段包含 {ch} 字的文字。\n"
    hits = validate.simplified_chars(body)
    assert any(c == ch for _, c in hits)


@pytest.mark.parametrize("ch", ["台", "游", "了", "群", "才", "峰"])
def test_gate8_does_not_flag_allowlisted_or_non_simplified_chars(ch):
    body = f"這是一段包含 {ch} 字的文字。\n"
    hits = validate.simplified_chars(body)
    assert not any(c == ch for _, c in hits)


def test_gate8_skips_fenced_code():
    body = "文字\n\n```move\nlet 个 = 1;\n```\n"
    assert validate.simplified_chars(body) == []


def test_gate8_skips_inline_code():
    body = "這是 `个` 這個變數。\n"
    assert validate.simplified_chars(body) == []


def test_gate8_reports_correct_line_index():
    body = "第一行\n第二行有 个 字\n第三行\n"
    hits = validate.simplified_chars(body)
    assert hits == [(1, "个")]


def test_gate8_corpus_exactly_five_chars_four_files():
    files = _files_at(PRE_FIX)
    hits_by_file = {}
    for path in files:
        zh = _show(PRE_FIX, path)
        if not zh:
            continue
        _, body = frontmatter.split(zh)
        hits = validate.simplified_chars(body)
        if hits:
            hits_by_file[path] = hits
    total = sum(len(v) for v in hits_by_file.values())
    assert total == 5
    assert len(hits_by_file) == 4


def _files_at(ref: str) -> list[str]:
    r = subprocess.run(
        ["git", "ls-tree", "-r", "-z", "--name-only", ref, "book", "reference"],
        capture_output=True, text=True, check=True,
    )
    return [f for f in r.stdout.split("\0") if f.endswith(".md")]


# --- Finding 4 / gate 4: non-string frontmatter values ---


def test_detects_non_string_frontmatter_value():
    en = '---\ndescription: "d"\n---\n\n# T\n'
    zh = '---\ndescription: true\n---\n\n# 標 {#t}\n'
    errs = validate.check_file(zh, en)
    assert any("description" in e for e in errs)


# --- Finding 5 / check_links: absolute and directory-style targets ---


def test_check_links_resolves_absolute_target():
    files = {
        "book/a.md": "# A {#a}\n\n[see](/book/b#target)\n",
        "book/b.md": "# B {#target}\n",
    }
    assert validate.check_links(files) == []


def test_check_links_resolves_directory_style_target():
    files = {
        "book/a.md": "# A {#a}\n\n[see](./sub#target)\n",
        "book/sub/index.md": "# Sub {#target}\n",
    }
    assert validate.check_links(files) == []
