import itertools
import subprocess
from collections import Counter
from pathlib import Path

from markdown_it import MarkdownIt

from scripts.zh_tw import frontmatter, glossary

_REPO_ROOT = Path(__file__).resolve().parent.parent
_MD = MarkdownIt("commonmark")


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


def test_enforce_protects_multiline_inline_code_span():
    # Review finding repro: 之前的逐行 regex 假設 inline code 是單行 span，
    # CommonMark 其實允許 code span 跨行（只有空白行會終止）。
    body = "prose `code line one\n函數 line two` more prose\n"
    assert glossary.scan(body) == {}
    assert glossary.enforce(body) == body


def test_enforce_protects_double_backtick_code_span_with_embedded_backtick():
    body = "prose ``code with ` inside 函數`` more prose\n"
    assert glossary.scan(body) == {}
    assert glossary.enforce(body) == body


def test_blank_line_terminates_code_span():
    # 未閉合的反引號不會把後面整份文件都吃掉：空白行結束段落，
    # 也結束尚未閉合的 code span 保護。
    body = "prose `unterminated\n\n函數 after blank line\n"
    out = glossary.enforce(body)
    assert "函式 after blank line" in out


def test_banned_term_adjacent_to_code_span_is_still_replaced():
    body = "函數`code`函數\n"
    out = glossary.enforce(body)
    assert out == "函式`code`函式\n"


def test_code_span_inside_html_comment_protected_but_prose_replaced():
    body = "<!--\n這個函數 `函數` 會返回一個值\n-->\n"
    out = glossary.enforce(body)
    assert "`函數`" in out  # code span 內未被改動
    assert "這個函式" in out  # 註解裡的 prose 仍被替換
    assert "會返回" not in out


def test_scan_rejects_non_maximal_closing_run():
    # Review finding repro: `` `函數``` `` 的收尾反引號跑左邊還連著一個
    # 反引號 —— 不是 maximal run，CommonMark 判定這裡完全沒有 code span，
    # 「函數」是 prose，必須被掃到、被替換。
    body = "prose ``函數``` more text"
    assert glossary.scan(body) == {"函數": 1}
    assert glossary.enforce(body) == "prose ``函式``` more text"


def test_scan_rejects_non_maximal_opening_run_variant():
    body = "a ``x``` y"
    assert glossary.scan(body) == {}
    assert glossary.enforce(body) == body


def test_scan_rejects_backtick_run_with_trailing_extra_backtick():
    body = "`x``"
    assert glossary.scan(body) == {}
    assert glossary.enforce(body) == body


def test_scan_rejects_non_maximal_opening_run():
    # 開頭側鏡像：`` ``函數` `` 是 2 個開頭反引號 + 1 個收尾反引號，
    # CommonMark 判定沒有 code span（收尾 run 太短）。可回溯的 `+ 會把
    # 開頭 run 縮成 1 個硬湊出 span，讓「函數」被靜默豁免；possessive
    # `++ 禁止回溯，開頭 run 維持 maximal，「函數」是 prose 必須被替換。
    body = "``函數`"
    assert glossary.scan(body) == {"函數": 1}
    assert glossary.enforce(body) == "``函式`"


def test_scan_rejects_non_maximal_opening_run_variants():
    for body in ("``x`", "``unterminated`"):
        assert glossary.scan(body) == {}
        assert glossary.enforce(body) == body


def _md_code_regions(body: str):
    """回傳 (code_inline 內容集合, fence/code_block 內容集合)，供差分測試比對。"""
    inline_contents = []
    block_contents = []

    def walk(tokens):
        for t in tokens:
            if t.type == "code_inline":
                inline_contents.append(t.content)
            if t.type in ("fence", "code_block"):
                block_contents.append(t.content)
            if t.children:
                walk(t.children)

    walk(_MD.parse(body))
    return inline_contents, block_contents


def test_scan_agrees_with_markdown_it_code_regions():
    # 差分測試：每個測資裡，凡是 markdown-it-py 判定為落在 code_inline
    # 或 fence/code_block token 內的術語，且該術語在整份 body 只出現在
    # 該保護區內（不與其他出現位置重疊），scan() 就必須回報 0。
    table = glossary.load()
    bodies = [
        "prose `code line one\n函數 line two` more prose\n",
        "呼叫函數\n\n```move\n// 函數 stays\n```\n",
        "prose ``code with ` inside 函數`` more prose\n",
        "<!--\n這個函數 `函數` 會返回一個值\n-->\n",
    ]
    for body in bodies:
        inline_contents, block_contents = _md_code_regions(body)
        counts = glossary.scan(body)
        for bad in table:
            protected_hits = sum(c.count(bad) for c in inline_contents)
            protected_hits += sum(c.count(bad) for c in block_contents)
            total_hits = body.count(bad)
            if protected_hits and protected_hits == total_hits:
                assert counts.get(bad, 0) == 0


def _md_prose_text(body: str) -> str:
    """把所有 inline token 裡「非 code_inline」的 text/純文字節點內容串接起來，
    當作 markdown-it-py 認定的 prose 真相來源（供差分測試比對 scan()）。
    """
    parts: list[str] = []

    def walk(tokens):
        for t in tokens:
            if t.type == "code_inline":
                pass  # 不算 prose
            elif t.type == "text":
                parts.append(t.content)
            elif t.type in ("softbreak", "hardbreak"):
                parts.append("\n")
            if t.children:
                walk(t.children)

    walk(_MD.parse(body))
    return "".join(parts)


def test_scan_agrees_exactly_with_markdown_it_prose_text():
    # 差分測試：對不含 fence / HTML block 的測資，scan() 回報的每個術語
    # 次數必須精確等於「markdown-it-py 判定為 inline text（不含
    # code_inline）」的節點裡該術語出現的次數。這是能同時抓到「code 誤判
    # 成 prose」（先前那個 bug）與「prose 誤判成 code」（本次修的 bug）
    # 的測試：oracle 直接來自 token 樹，不靠自己刻的 regex 假設。
    table = glossary.load()
    bodies = [
        "這個函數會返回一個值",
        "循環中調用變量",
        "使用 `函數` 這個詞",
        "呼叫 `函數` 之後函數才會返回\n",
        "prose `code line one\n函數 line two` more prose\n",
        "prose ``函數``` more text",
        "a ``x``` y",
        "`x``",
        "``函數`",
        "``x`",
        "prose ``函數` still prose 調用\n",
        "``code ` inside 函數`` 函數",
        "函數`code`函數\n",
        "prose `unterminated\n\n函數 after blank line\n",
        "# 標題裡的函數\n\n段落裡的變量和調用\n",
        "- 列表項目的函數\n- 第二個調用\n",
        "> 引用裡的函數\n",
        "**加粗的函數** 和 *斜體的調用*\n",
    ]
    for body in bodies:
        prose = _md_prose_text(body)
        counts = glossary.scan(body)
        for bad in table:
            expected = prose.count(bad)
            assert counts.get(bad, 0) == expected, (
                f"body={body!r} bad={bad!r} expected={expected} got={counts.get(bad, 0)}"
            )


def test_enforce_idempotent():
    body = "prose `code line one\n函數 line two` more prose\n呼叫函數 之後函數才會返回\n"
    once = glossary.enforce(body)
    twice = glossary.enforce(once)
    assert once == twice


def test_enforce_preserves_crlf_line_endings():
    body = "呼叫函數\r\n`函數` 保持不變\r\n"
    out = glossary.enforce(body)
    assert out == "呼叫函式\r\n`函數` 保持不變\r\n"


def test_enforce_preserves_missing_trailing_newline():
    body = "呼叫函數"
    out = glossary.enforce(body)
    assert out == "呼叫函式"
    assert not out.endswith("\n")


def test_scan_ignores_span_opened_in_prose_closed_inside_fence():
    # Fuzz-found repro: `` ` `` opens in a paragraph line, and its closing
    # delimiter lives inside the fence on the next line. _CODE_SPAN used to
    # run over the whole body and only check the match's *start* against
    # the protected mask, so this cross-block span swallowed the fence's
    # backtick as its closer and hid the paragraph's "函數".
    body = "```函數`\n```"
    assert glossary.scan(body) == {"函數": 1}
    assert glossary.enforce(body) == "```函式`\n```"


def test_scan_ignores_span_opened_in_prose_closed_inside_fence_double_backtick():
    body = "```函數``\n```"
    assert glossary.scan(body) == {"函數": 1}
    assert glossary.enforce(body) == "```函式``\n```"


def test_scan_finds_both_occurrences_around_fence_crossing_span():
    body = "函數```函數\n```"
    assert glossary.scan(body) == {"函數": 2}
    assert glossary.enforce(body) == "函式```函式\n```"


def test_scan_ignores_span_opened_in_prose_with_leading_space_closed_in_fence():
    body = " x ```函數\n```"
    assert glossary.scan(body) == {"函數": 1}
    assert glossary.enforce(body) == " x ```函式\n```"


def test_scan_ignores_span_opened_in_prose_no_space_closed_in_fence():
    body = "y```函數\n```"
    assert glossary.scan(body) == {"函數": 1}
    assert glossary.enforce(body) == "y```函式\n```"


def _oracle_banned_counts(body: str, table: dict[str, str]) -> dict[str, int]:
    """Ground truth: walk markdown-it-py's own token tree. For every
    ``inline`` token, count banned terms in the ``content`` of every child
    whose type is *not* ``code_inline``. This is the direct source of
    truth glossary.scan() must agree with — no regex re-derivation.
    """
    counts: Counter[str] = Counter()

    def walk(tokens):
        for t in tokens:
            if t.type == "inline":
                for child in t.children or []:
                    if child.type != "code_inline":
                        for bad in table:
                            n = child.content.count(bad)
                            if n:
                                counts[bad] += n
            if t.children:
                walk(t.children)

    walk(_MD.parse(body))
    return dict(counts)


def test_scan_agrees_with_markdown_it_fuzz_sweep():
    """Fuzz test replacing hand-picked differential cases.

    This is the test that would have caught all three inline-code bugs
    fixed in this file's history (line-based masking assuming single-line
    spans, non-maximal backtick runs, and a code span crossing a fenced
    block boundary): it generates every combination of markdown-ish
    fragments up to length 5 and checks scan() against an oracle built
    directly from markdown-it's own token tree, rather than against a
    hand-picked list of bodies someone thought to write down.
    """
    table = glossary.load()
    fragments = ["`", "``", "```", "函數", " x ", "\n", "y"]
    checked = 0
    for length in range(2, 6):
        for combo in itertools.product(fragments, repeat=length):
            body = "".join(combo)
            if "\n\n" in body:
                continue
            expected = _oracle_banned_counts(body, table)
            actual = glossary.scan(body, table)
            assert actual == expected, f"body={body!r} expected={expected} got={actual}"
            checked += 1
    assert checked == 18234


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
    assert total == 87  # backfill 進度：PR 3-6 累計清 39 處（126→87）
