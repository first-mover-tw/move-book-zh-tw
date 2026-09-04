import itertools
import subprocess
from collections import Counter
from pathlib import Path

from markdown_it import MarkdownIt

from scripts.zh_tw import frontmatter, glossary, validate

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


def test_corpus_has_no_banned_terms():
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
    assert total == 0  # 2026-07-12 債務全清（126→76→0，stash 手工翻譯合併 + 機械修復）


# --- scan-only 詞表：標記但不自動替換 ---
#
# 有些詞條「值得提醒人」但「不能機械替換」，因為它們是多義詞或有子字串碰撞
# （lessons L9：「循環→迴圈」誤傷 cycle 語意的前科）。2026-09-02 外部 review
# 實測三個現場：
#   交易影響→交易效果  「這筆交易影響了物件的所有權」→「這筆交易效果了…」
#   Move 封裝→Move 套件 「Move 封裝了狀態與行為」→「Move 套件了狀態與行為」
#   燃料費→gas         「支付燃料費用」→「支付gas用」（子字串碰撞）
# 這些放進 enforce 表就是靜默破壞句子；完全不收又等於下一批重翻照樣長回來。


def test_scan_only_terms_are_reported_but_not_replaced():
    from scripts.zh_tw import glossary

    text = "這筆交易影響了物件的所有權，支付燃料費用。"
    assert glossary.enforce(text) == text, "scan-only 詞條不得被機械替換"
    # 走獨立通道，不混進 scan()：scan() 的結果會被 validate 轉成 error，
    # 而 scan-only 沒有自動修復路徑，當成 error 就是合法中文擋住整條管線。
    assert glossary.scan(text) == {}
    hits = glossary.scan_only_hits(text)
    assert "交易影響" in hits and "燃料費" in hits


def test_scan_only_and_enforce_tables_are_disjoint():
    """同一個詞不能同時在兩張表 —— 那會讓「要不要替換」取決於載入順序。"""
    from scripts.zh_tw import glossary

    assert not (set(glossary.load()) & set(glossary.load_scan_only()))


def test_scan_only_terms_do_not_fail_the_write_gate():
    """複驗輪 C2：scan-only 洩漏進 validate 的 gate 7 → 「這筆交易影響了
    物件的所有權」這種**完全正確的中文**會讓整個檔案的翻譯硬失敗，而
    enforce 依設計不碰它 → 沒有任何自動修復路徑，每輪都要人工。
    修前是「靜默改壞句子」，修後變成「合法句子讓管線炸掉」，兩者都不是
    「標記但不替換」該有的行為。scan-only 只能是 warn，不能是 fail。"""
    from scripts.zh_tw import validate

    zh = "---\ntitle: 標題 (T)\ndescription: 說明\n---\n\n# 標題 (T) {#t}\n\n這筆交易影響了物件的所有權。\n"
    en = "---\ntitle: T\ndescription: d\n---\n\n# T {#t}\n\nThis transaction affected ownership.\n"
    assert not [e for e in validate.check_file(zh, en) if "交易影響" in e]


def test_scan_only_terms_are_still_surfaced():
    """但它必須被看見 —— 不然等於沒收。"""
    from scripts.zh_tw import glossary

    assert "交易影響" in glossary.scan_only_hits("這筆交易影響了物件的所有權。")


# --- 2026-09-03 PR #24 審查產出的詞條（run 33730438417） ---


def test_pr24_regressions_are_surfaced():
    """四個缺陷各自對應 PR #24 機翻產出的一處真實回歸。沒有詞表，
    check_repo 對這些句子回報乾淨（實測：CI 6/6 綠、check_repo 0/0/0）。

    只有「開發人員」進 enforce（無碰撞）；其餘三個有子字串碰撞，只能顯形。
    """
    assert glossary.scan("Move 允許開發人員編寫程式。").get("開發人員") == 1
    for bad, sentence in {
        "常試": "為了常試解決這個問題，有一些常見的模式。",
        "說明瞭": "貢獻附錄則說明瞭如何加入他們。",
        "創始人": "— Sam Blackshear，Move 創始人",
    }.items():
        assert glossary.scan_only_hits(sentence).get(bad) == 1, (bad, sentence)


def test_enforce_never_damages_a_legitimate_sentence():
    """守衛的維度要等於它承擔的風險（lessons L2）。

    「詞表看得見這個缺陷」與「詞表機械替換起來是安全的」是兩件事。
    2026-09-04 外部 review 就是從這個缺口抓到三個 blocker：常試 撞
    通常試/非常試/正常試、說明瞭 撞 說明+瞭解、創始人 撞 founder 的
    正確用法。這些句子每一條都必須原封不動地通過 enforce。
    """
    intact = [
        "通常試圖使用 assert! 來檢查條件。",  # 通常 + 試圖
        "開發者非常試著避免這種寫法。",  # 非常 + 試著
        "這在正常試驗中不會發生。",  # 正常 + 試驗
        "本節說明瞭解物件模型的方式。",  # 說明 + 瞭解
        "他是這家公司的創始人。",  # founder，不是 creator
        "`public_*` 轉移函式接受它們作為引數。",  # transfer functions
        "能力宣告必須以分號終止：",  # terminated with a semicolon
    ]
    for s in intact:
        assert glossary.enforce(s) == s, s

    # enforce 表裡的詞條也要有正向覆蓋：它們該改的時候必須真的改。
    assert glossary.enforce("Move 允許開發人員編寫程式。") == "Move 允許開發者編寫程式。"
    assert glossary.enforce("如果這激勵了您，請繼續閱讀。") == "如果這激勵了你，請繼續閱讀。"
    assert glossary.enforce("Move 是一種智能合約語言。") == "Move 是一種智慧合約語言。"


def test_enforce_is_a_noop_on_the_existing_corpus():
    """enforce 表是無邊界的 str.replace。任何新詞條若會改動既有語料，
    要嘛那處本來就錯（該一併修掉），要嘛就是子字串碰撞（不該進表）。
    兩種情況都不該靜默通過。"""
    files = [p for base in ("book", "reference") for p in (_REPO_ROOT / base).rglob("*.md")]
    for path in sorted(files):
        body = frontmatter.split(path.read_text(encoding="utf-8"))[1]
        assert glossary.enforce(body) == body, path


def test_liao_over_conversion_is_not_reachable_by_the_simplified_gate():
    """「說明瞭」為什麼只能靠詞表顯形：gate 8 用 OpenCC s2tw 逐字轉換，而
    「了→瞭」正是它的已知假陽性來源（validate.py 開頭的白名單註解），
    字形那一側永遠攔不到它。兩道關卡的分工要有測試釘住。
    """
    assert validate.simplified_chars("則說明瞭如何加入。\n") == []
    assert glossary.scan_only_hits("則說明瞭如何加入。").get("說明瞭") == 1


def test_polysemous_terms_stay_out_of_the_enforce_table():
    """lessons L9：多義詞與子字串碰撞不進 enforce 表。

    終止 看起來該機械替換（語料 中止 175 : 終止 5），但 reference/ 有 5 處
    英文原文就是 terminate（enums「terminated with a semicolon」、generics
    「terminate for any given input」、uses、references「program terminates」×2）。
    傳輸 同理撞 transfer functions。scan 讓它們顯形、prompt_rules 教模型，
    enforce 不碰。
    """
    enforce_table = glossary.load()
    scan_only = glossary.load_scan_only()
    for term in ("終止", "傳輸", "常試", "說明瞭", "創始人"):
        assert term not in enforce_table, term
        assert term in scan_only, term


def test_scan_only_warnings_have_a_known_baseline():
    """scan-only 是永遠不會 fail 的頻道，久了就變成沒人看的噪音：真正的新
    誤用會混在固定幾行 ⚠️ 裡看不出來（外部 review 2026-09-04）。

    釘住預期筆數 —— 數字一變就得有人看一眼是新誤用還是清掉了舊的。
    目前的 5 處全部是**正確**的「終止」（英文原文就是 terminate）。

    範圍限 .md —— check_repo.collect() 也只收 .md。`reference/sidebar.yml`
    的側邊欄標籤不在任何 gate 的視野內，改術語時要人工同步（2026-09-04
    第三輪外部 review 就是在那裡抓到一處漏改的「終止與斷言」）。
    """
    files = [p for base in ("book", "reference") for p in (_REPO_ROOT / base).rglob("*.md")]
    hits: Counter[str] = Counter()
    for path in files:
        body = frontmatter.split(path.read_text(encoding="utf-8"))[1]
        hits.update(glossary.scan_only_hits(body))
    assert dict(hits) == {"終止": 5}, dict(hits)


def test_substitution_mask_covers_link_destinations_and_urls():
    """enforce/scan 不得碰外部連結目的地與 URL（2026-09-04）。

    `位址`→`地址`、`字符串`→`字串` 這類詞條在 URL 裡出現時，機械替換會直接
    產出 404 與圖裂，而且**沒有任何 gate 看得見**：gate 10 只看 <em> 有沒有
    變少，連結壞掉不影響 <em>；prettier 不管語意；check_repo 的連結檢查只驗
    repo 內相對路徑，外部 URL 不在視野內。

    對稱地，scan() 也必須一起豁免——否則含這些字的合法外部 URL 會讓
    check_repo 永久紅，而 enforce 又（正確地）不去修它，變成 L16 說的
    「有守衛沒有修復路徑」的死鎖。
    """
    cases = [
        "詳見 [說明](https://example.com/位址/字符串.html) 一節。",
        "![圖](../assets/位址圖.png)",
        "見 <https://zh.wikipedia.org/wiki/記憶體位址> 。",
        "參考 https://example.com/docs?q=字符串 的說明。",
    ]
    for body in cases:
        assert glossary.enforce(body) == body, body
        assert glossary.scan(body) == {}, body


def test_substitution_mask_still_enforces_link_text_and_surrounding_prose():
    """保護只到 destination 為止：連結**文字**與前後散文照樣要被替換，
    否則這道保護就從『別改 URL』擴張成『別改任何帶連結的句子』。"""
    body = "這個字符串見 [字符串說明](https://example.com/字符串) 的位址欄位。"
    got = glossary.enforce(body)
    assert got == "這個字串見 [字串說明](https://example.com/字符串) 的地址欄位。", got


def test_substitution_mask_does_not_freeze_inpage_anchors():
    """頁內 fragment `](#中文標題)` 必須跟著標題一起被替換，不可凍結。

    slug 是從標題文字推導的：enforce 改「## 創建新套件」→「## 建立新套件」時，
    `](#創建新套件)` 也必須變成 `](#建立新套件)`，否則錨點指不到任何東西。
    語料現有 6 處中文錨點（hello-world `#建立新套件`、functions `#回傳數值`、
    packages `#編譯期間的具名地址…`）之所以一致，正是因為同一個 str.replace
    把兩邊一起改了。

    這條與上一條是一對**相反**的需求：外部 URL 凍結、頁內 fragment 跟動。
    2026-09-04 加 URL 保護時差點把 fragment 一起凍結，那會讓下一次 enforce
    靜默產出死錨點。
    """
    body = "## 創建新套件\n\n見 [上面](#創建新套件) 與 [外部](https://example.com/創建).\n"
    got = glossary.enforce(body)
    assert "## 建立新套件" in got, got
    assert "](#建立新套件)" in got, got
    assert "](https://example.com/創建)" in got, got  # 外部 URL 不動


def test_emphasis_mask_freezes_inpage_anchors_but_substitution_mask_does_not():
    """強調修復相反：它把 `_x_` 換成 `*x*`，沒有「同步改標題」這回事，
    所以頁內 fragment 必須凍結，否則 slug 直接失效。"""
    body = "見 [連結](#所有權_模型_說明) 一節。\n"
    # 判準取 destination 本身，不含 `](` 與 `)` 這兩個分隔符 —— 分隔符不可能是
    # 底線或術語，把它們算進斷言等於拿形態當真實性質（L2）。
    i = body.index("#所有權")
    j = body.index(")", i)
    assert all(glossary.emphasis_mask(body)[i:j]), "頁內 fragment 應落在強調保護區內"
    assert not any(glossary.substitution_mask(body)[i:j]), "頁內 fragment 不應落在替換保護區內"


def test_cross_file_fragment_tracks_the_target_heading():
    """跨檔 fragment `](./other.md#中文錨點)` 也必須跟著標題一起被替換。

    外部 review 2026-09-04 抓到：原本用 `startswith("](#")` 判「頁內 fragment」，
    跨檔的一律落進保護區 → 錨點被凍結，但 enforce 對**每個檔**都跑，目標檔的
    `## 創建新套件` 照樣被改成 `## 建立新套件` → 死錨點。語料有 3 處活實例
    （pattern-matching.md、macros.md ×2），只是恰好不含術語表詞條，屬潛伏未爆。

    路徑部分必須凍結（那是檔案系統路徑，改了就 404），只有 `#` 之後讓出來。
    """
    body = "見 [x](./創建/other.md#創建新套件) 一節。\n"
    got = glossary.enforce(body)
    assert got == "見 [x](./創建/other.md#建立新套件) 一節。\n", got


def test_reference_style_link_definition_destination_is_protected():
    """`[標籤]: ./路徑.md` 的 destination 也是連結目的地，不可被術語替換。

    外部 review 2026-09-04：URLISH 三個 alternation 全部漏掉**沒有 scheme** 的
    ref-def destination，實測 `enforce('[標籤]: ./創建_套件.md')` 會改成
    `./建立_套件.md`。語料 `book/storage/key-ability.md:51-56` 有 6 個相對路徑
    ref-def（今天不含術語表詞條，潛伏未爆）。
    """
    body = "[標籤]: ./創建_套件.md\n[外部]: https://example.com/位址\n"
    assert glossary.enforce(body) == body, glossary.enforce(body)


def test_angle_bracket_destination_fragment_still_tracks():
    """`](<#錨點>)` 角括號目的地：判準是解析出 destination 看有沒有 scheme，
    不是比對 `](#` 前綴，所以這個形態一樣要跟著標題走。"""
    body = "見 [x](<#創建新套件>) 一節。\n"
    assert glossary.enforce(body) == "見 [x](<#建立新套件>) 一節。\n", glossary.enforce(body)


def test_external_url_fragment_stays_frozen():
    """帶 scheme 的 fragment 是外部網站的錨點，不由我們的標題決定 → 凍結。"""
    body = "見 [x](https://example.com/p#創建新套件) 一節。\n"
    assert glossary.enforce(body) == body, glossary.enforce(body)
