import subprocess

import pytest
from markdown_it import MarkdownIt

from scripts.zh_tw import anchors, frontmatter

_MD = MarkdownIt("commonmark")


def _heading_level_seq(body: str) -> list[int]:
    return [int(t.tag[1]) for t in _MD.parse(body) if t.type == "heading_open"]


def _has_hr(body: str) -> bool:
    return any(t.type == "hr" for t in _MD.parse(body))


def _anchor_ids(body: str) -> list[str]:
    """每個標題各自求一次 anchor id(anchors._ANCHOR 沒有 re.MULTILINE，
    對整份文字 findall 只會抓到最後一行，不能拿來對多標題文件用)。"""
    return [
        aid
        for _, text in anchors.headings(body)
        if (aid := anchors.existing_anchor(text)) is not None
    ]


def test_inject_adds_slug_from_english_heading():
    zh = "# 向量\n\n內文\n"
    en = "# Vector\n\nBody\n"
    assert anchors.inject(zh, en) == "# 向量 {#vector}\n\n內文\n"


def test_inject_carries_forward_existing_anchor():
    """人工選定的 anchor 必須原樣保留，即使它不等於英文 slug。

    身分匹配需要 prev_en_body 才能沿用（見設計規則 4）；這裡英文標題文字
    在新舊之間沒變，所以身分匹配與舊版的 by-index 行為結果一致。
    """
    zh = "## 不可變狀態\n"
    en = "## Immutable (Frozen) State\n"
    prev_zh = "## 不可變狀態 {#immutable-frozen-object}\n"
    prev_en = "## Immutable (Frozen) State\n"
    assert (
        anchors.inject(zh, en, prev_zh, prev_en)
        == "## 不可變狀態 {#immutable-frozen-object}\n"
    )


def test_inject_preserves_anchor_already_in_zh():
    zh = "## 群組 {#party}\n"
    en = "## Party\n"
    assert anchors.inject(zh, en) == "## 群組 {#party}\n"


def test_inject_deduplicates_repeated_slugs():
    zh = "## 設定\n\n## 設定\n"
    en = "## Setup\n\n## Setup\n"
    out = anchors.inject(zh, en)
    assert "{#setup}" in out
    assert "{#setup-1}" in out


def test_inject_raises_on_heading_count_mismatch():
    """這正是 reference/variables.md 的失效模式：21 個英文標題、6 個中文標題。"""
    with pytest.raises(anchors.HeadingMismatch):
        anchors.inject("# 一\n", "# One\n\n## Two\n")


def test_inject_ignores_headings_inside_code_fences():
    zh = "# 標題\n\n```move\n# 註解\n```\n"
    en = "# Title\n\n```move\n# comment\n```\n"
    out = anchors.inject(zh, en)
    assert out.count("{#") == 1
    assert "# 註解" in out


# --- Finding 1: 衍生 slug 不得撞上 carried-forward anchor ---


def test_inject_derived_slug_does_not_collide_with_carried_anchor():
    zh = "## 設定\n\n## 別的\n"
    en = "## Setup\n\n## Other\n"
    prev_zh = "## 舊標題\n\n## 別的 {#setup}\n"
    prev_en = "## Old Title\n\n## Other\n"
    out = anchors.inject(zh, en, prev_zh, prev_en)

    ids = _anchor_ids(out)
    assert len(ids) == len(set(ids)), f"重複 anchor id: {ids}"
    assert "{#setup}" in out  # carried 保留在原本擁有它的標題上
    # 第二個標題(索引 1)必須保有 carried anchor `setup`
    assert out.splitlines()[-1] == "## 別的 {#setup}"


def test_inject_carried_anchor_equals_other_headings_natural_slug_carried_first():
    """carried anchor 恰好等於「另一個標題」衍生後會產生的 slug；carried 排前面。"""
    zh = "## 設定\n\n## 別的\n"
    en = "## Other\n\n## Setup\n"  # 注意：英文順序對調，衍生 slug 分別是 other / setup
    prev_zh = "## 舊標題 {#setup}\n\n## 舊別的\n"  # 索引 0 carried = setup
    prev_en = "## Other\n\n## Setup\n"  # 身分匹配：舊標題 0 對應 "Other"
    out = anchors.inject(zh, en, prev_zh, prev_en)

    ids = _anchor_ids(out)
    assert len(ids) == len(set(ids)), f"重複 anchor id: {ids}"
    lines = out.splitlines()
    assert lines[0] == "## 設定 {#setup}"
    assert lines[-1] != "## 別的 {#setup}"


def test_inject_carried_anchor_equals_other_headings_natural_slug_carried_second():
    zh = "## 設定\n\n## 別的\n"
    en = "## Setup\n\n## Other\n"
    prev_zh = "## 舊設定\n\n## 舊別的 {#setup}\n"  # 索引 1 carried = setup
    prev_en = "## Setup\n\n## Other\n"  # 身分匹配：舊標題 1 對應 "Other"
    out = anchors.inject(zh, en, prev_zh, prev_en)

    ids = _anchor_ids(out)
    assert len(ids) == len(set(ids)), f"重複 anchor id: {ids}"
    lines = out.splitlines()
    assert lines[-1] == "## 別的 {#setup}"
    assert lines[0] != "## 設定 {#setup}"


def test_inject_raises_duplicate_anchor_when_tier1_anchors_collide():
    """兩個標題在中文檔裡本身就已經帶有相同 anchor(tier 1)—— 衍生階段救不了，必須顯式炸掉。"""
    zh = "## 設定 {#dup}\n\n## 別的 {#dup}\n"
    en = "## Setup\n\n## Other\n"
    with pytest.raises(anchors.DuplicateAnchor):
        anchors.inject(zh, en)


# --- Finding 2: setext 標題正規化為 ATX，底線行整行移除 ---


def test_inject_normalizes_setext_level2_no_phantom_hr():
    zh = "標題\n----\n\n內文\n"
    en = "Title\n-----\n\nBody\n"
    out = anchors.inject(zh, en)

    assert _heading_level_seq(out) == _heading_level_seq(zh) == [2]
    assert not _has_hr(out)
    assert "----" not in out
    assert out.splitlines()[0] == "## 標題 {#title}"


def test_inject_normalizes_setext_level1_no_phantom_hr():
    zh = "標題\n====\n\n內文\n"
    en = "Title\n=====\n\nBody\n"
    out = anchors.inject(zh, en)

    assert _heading_level_seq(out) == _heading_level_seq(zh) == [1]
    assert not _has_hr(out)
    assert "====" not in out
    assert out.splitlines()[0] == "# 標題 {#title}"


# --- Finding 3: CRLF 行尾必須原樣保留 ---


def test_inject_preserves_crlf_line_ending():
    zh = "# 標題\r\n\r\n內文\r\n"
    en = "# Title\r\n\r\nBody\r\n"
    out = anchors.inject(zh, en)

    assert out.splitlines(keepends=True)[0] == "# 標題 {#title}\r\n"
    # 檔案裡不該出現裸的 \n(沒有前導 \r)
    assert "\r\n" in out
    bare_lf = out.replace("\r\n", "")
    assert "\n" not in bare_lf, "混用行尾: 標題行被降級為 LF"


# --- Round-trip: 混合 ATX 標題、fence、HTML 註解 ---


# --- Finding 4: 巢狀標題(blockquote/list item)必須顯式炸掉，不得靜默拉升到頂層 ---


def test_inject_raises_on_atx_heading_inside_blockquote():
    with pytest.raises(anchors.NestedHeading):
        anchors.inject("> ## 標題\n", "> ## Title\n")


def test_inject_raises_on_setext_heading_inside_blockquote():
    with pytest.raises(anchors.NestedHeading):
        anchors.inject("> 標題\n> ----\n", "> Title\n> -----\n")


def test_inject_raises_on_heading_inside_list_item():
    with pytest.raises(anchors.NestedHeading):
        anchors.inject("- ## 標題\n", "- ## Title\n")


def test_inject_raises_on_nested_heading_only_in_english():
    """中文乾淨,但英文有巢狀標題——兩邊都要檢查。"""
    with pytest.raises(anchors.NestedHeading):
        anchors.inject("# 標題\n", "> # Title\n")


def test_inject_blockquote_without_heading_survives_untouched():
    zh = "> 一般引言\n>\n> 內文\n"
    en = "> A normal quote\n>\n> Body\n"
    out = anchors.inject(zh, en)
    assert out == zh


def test_inject_fenced_code_that_looks_like_nested_heading_does_not_raise():
    zh = "# 標題\n\n```\n> ## 看起來像標題\n```\n"
    en = "# Title\n\n```\n> ## looks like heading\n```\n"
    out = anchors.inject(zh, en)
    assert "{#title}" in out
    assert "> ## 看起來像標題" in out


def test_inject_nested_heading_error_message_contains_heading_text():
    with pytest.raises(anchors.NestedHeading, match="巢狀標題"):
        anchors.inject("> ## 巢狀標題\n", "> ## Nested Title\n")


def test_inject_roundtrip_heading_levels_and_anchor_count():
    zh = (
        "# 標題一\n\n"
        "<!-- # 不是標題 -->\n\n"
        "```move\n# 也不是標題\n```\n\n"
        "## 標題二\n\n內文\n"
    )
    en = (
        "# Title One\n\n"
        "<!-- # not a heading -->\n\n"
        "```move\n# not a heading either\n```\n\n"
        "## Title Two\n\nBody\n"
    )
    out = anchors.inject(zh, en)

    zh_levels = [lvl for _, lvl in anchors.heading_lines(zh)]
    out_levels = [lvl for _, lvl in anchors.heading_lines(out)]
    assert out_levels == zh_levels

    out_headings = anchors.headings(out)
    assert len(out_headings) == len(anchors.headings(zh))
    for _, text in out_headings:
        ids = anchors._ANCHOR.findall(text)
        assert len(ids) == 1, f"標題應恰好帶一個 anchor: {text!r}"


# --- Identity-based carry-forward (Task 4 review remedy) ---
#
# `inject()` 過去用「第 i 個標題」配對舊 anchor 與新標題，一旦英文標題序列
# 增刪，carried anchor 就會靜默套到錯的標題上。以下測試改以英文標題「文字」
# 當作身分鍵，重現該迴歸並鎖住修好後的行為。


def test_inject_carries_anchor_by_identity_not_index_after_heading_insertion():
    """迴歸測試：上游在 B 之前插入新標題，carried anchor 必須跟著 B 走。"""
    prev_en = "# A\n\n# B\n\n# C\n"
    new_en = "# A\n\n# NEW\n\n# B\n\n# C\n"
    prev_zh = "# 一\n\n# 二 {#b-anchor}\n\n# 三\n"
    zh = "# 甲\n\n# 新\n\n# 乙\n\n# 丙\n"

    out = anchors.inject(zh, new_en, prev_zh, prev_en)
    out_headings = anchors.headings(out)

    assert anchors.existing_anchor(out_headings[2][1]) == "b-anchor"
    assert out_headings[2][1].startswith("乙")
    # 舊程式碼會把它套到索引 1(NEW)上——明確排除這個錯誤結果。
    assert anchors.existing_anchor(out_headings[1][1]) != "b-anchor"


def test_inject_retires_anchor_for_heading_removed_upstream():
    prev_en = "# A\n\n# Gone\n\n# C\n"
    new_en = "# A\n\n# C\n"
    prev_zh = "# 一\n\n# 走 {#gone}\n\n# 三\n"
    zh = "# 甲\n\n# 丙\n"

    out, notes = anchors.inject_report(zh, new_en, prev_zh, prev_en)

    assert "{#gone}" not in out
    assert any("gone" in n and "retired" in n for n in notes), notes


def test_inject_retires_anchor_for_heading_renamed_upstream():
    prev_en = "# A\n\n# OldName\n\n# C\n"
    new_en = "# A\n\n# NewName\n\n# C\n"
    prev_zh = "# 一\n\n# 舊 {#old-anchor}\n\n# 三\n"
    zh = "# 甲\n\n# 新名\n\n# 丙\n"

    out, notes = anchors.inject_report(zh, new_en, prev_zh, prev_en)

    assert "{#old-anchor}" not in out
    assert any("old-anchor" in n and "retired" in n for n in notes), notes
    out_headings = anchors.headings(out)
    assert anchors.existing_anchor(out_headings[1][1]) == "newname"


def test_inject_duplicate_heading_texts_match_left_to_right():
    prev_en = "# Setup\n\n# Setup\n"
    new_en = "# Setup\n\n# Setup\n"
    prev_zh = "# 設定甲 {#setup-0}\n\n# 設定乙 {#setup-1}\n"
    zh = "# 甲\n\n# 乙\n"

    out = anchors.inject(zh, new_en, prev_zh, prev_en)
    out_headings = anchors.headings(out)

    assert anchors.existing_anchor(out_headings[0][1]) == "setup-0"
    assert anchors.existing_anchor(out_headings[1][1]) == "setup-1"


def test_inject_no_prev_en_body_carries_nothing_even_with_prev_zh_body():
    """設計規則 4：缺 prev_en_body 絕不 fallback 回 by-index 猜測。"""
    zh = "# 甲\n"
    en = "# A\n"
    prev_zh = "# 舊 {#foo}\n"

    out, notes = anchors.inject_report(zh, en, prev_zh, "")

    assert "{#foo}" not in out
    assert any("prev_en_body" in n and "not carried forward" in n for n in notes), notes
    # 明確驗證：沒有發生 positional carry。
    out_headings = anchors.headings(out)
    assert anchors.existing_anchor(out_headings[0][1]) != "foo"


def test_inject_mismatched_prev_heading_counts_carries_nothing_no_exception():
    prev_zh = "# 一\n\n# 二\n"
    prev_en = "# A\n\n# B\n\n# C\n"
    zh = "# 甲\n"
    en = "# A\n"

    out, notes = anchors.inject_report(zh, en, prev_zh, prev_en)

    assert "{#" in out  # 仍然照常衍生 slug，只是沒有任何東西被沿用
    assert any("mismatch" in n for n in notes), notes


def test_inject_tier1_still_beats_carried_tier2():
    zh = "## 已有 {#existing}\n"
    en = "## Already\n"
    prev_zh = "## 舊有 {#carried}\n"
    prev_en = "## Already\n"

    out = anchors.inject(zh, en, prev_zh, prev_en)

    assert "{#existing}" in out
    assert "{#carried}" not in out


def test_inject_carried_anchor_reserves_id_over_colliding_derived_slug():
    prev_en = "# A\n\n# Setup\n"
    prev_zh = "# 舊甲\n\n# 設定 {#setup}\n"
    new_en = "# Setup\n\n# Setup\n"
    zh = "# 甲\n\n# 乙\n"

    out = anchors.inject(zh, new_en, prev_zh, prev_en)
    out_headings = anchors.headings(out)

    assert anchors.existing_anchor(out_headings[0][1]) == "setup"
    assert anchors.existing_anchor(out_headings[1][1]) == "setup-1"


# --- Real-data regression: book/object/ownership.md 與 epoch-and-time.md ---

_MERGE_BASE = "f2c0a93e1a0422078d3d051e4410ac3edc612016"
_PRE_FIX = "0d4b8bea77f1a6195b589ded4067d287adb4379a"


def _git_show(ref: str, path: str) -> str:
    import subprocess

    r = subprocess.run(
        ["git", "show", f"{ref}:{path}"], capture_output=True, text=True, check=True
    )
    return r.stdout


def _body_at(ref: str, path: str) -> str:
    from scripts.zh_tw import frontmatter as fm

    _, body = fm.split(_git_show(ref, path))
    return body


@pytest.mark.parametrize(
    "path,anchor_id,heading_text",
    [
        ("book/object/ownership.md", "immutable-frozen-object", "Immutable (Frozen) State"),
        ("book/programmability/epoch-and-time.md", "clock", "Time"),
    ],
)
def test_inject_real_data_identity_carry_lands_on_correct_heading(
    path, anchor_id, heading_text
):
    """english-main 的英文本文當作「重新翻譯」的替身(每個標題逐一對應)，
    驗證身分匹配能把人工選定的 anchor 準確沿用到正確的新標題上。"""
    en_body = _body_at("english-main", path)  # 同時充當 zh_body 的替身與新英文
    prev_zh_body = _body_at(_PRE_FIX, path)
    prev_en_body = _body_at(_MERGE_BASE, path)

    out, notes = anchors.inject_report(en_body, en_body, prev_zh_body, prev_en_body)

    out_headings = anchors.headings(out)
    match = [
        text for _, text in out_headings
        if anchors.existing_anchor(text) == anchor_id
    ]
    assert len(match) == 1, f"{anchor_id!r} 未被沿用到恰好一個標題: {notes}"
    assert match[0].split(" {#")[0] == heading_text


# --- Slug-keyed identity (Task 4 refinement) ---
#
# 原始文字身分過嚴：標題文字只差大小寫仍是同一個標題，逐字比對卻會誤判
# 成「消失了」而讓 anchor 退場。身分鍵改成 slugify_all(標題文字)——
# slugify 本來就對大小寫/標點不敏感，slugify_all 的去重尾碼能正確處理
# 「同一份文件裡兩個標題文字完全相同」的情況。


def test_inject_carries_anchor_across_case_only_rename():
    """`Error constants` -> `Error Constants`：純大小寫變化，anchor 必須沿用，不能退場。"""
    prev_en = "# A\n\n# Error constants\n\n# C\n"
    new_en = "# A\n\n# Error Constants\n\n# C\n"
    prev_zh = "# 一\n\n# 錯誤常數 {#error-constants}\n\n# 三\n"
    zh = "# 甲\n\n# 錯誤常數\n\n# 丙\n"

    out, notes = anchors.inject_report(zh, new_en, prev_zh, prev_en)
    out_headings = anchors.headings(out)

    assert anchors.existing_anchor(out_headings[1][1]) == "error-constants"
    assert not any("retired" in n for n in notes), notes


def test_inject_carries_anchor_across_punctuation_only_rename():
    """`` `assert!` `` -> `assert!`：純標點/inline-code 差異，slug 相同，anchor 必須沿用。"""
    assert anchors.slugify("`assert!`") == anchors.slugify("assert!") == "assert"

    prev_en = "# A\n\n# `assert!`\n\n# C\n"
    new_en = "# A\n\n# assert!\n\n# C\n"
    prev_zh = "# 一\n\n# 判斷 {#assert}\n\n# 三\n"
    zh = "# 甲\n\n# 判斷\n\n# 丙\n"

    out, notes = anchors.inject_report(zh, new_en, prev_zh, prev_en)
    out_headings = anchors.headings(out)

    assert anchors.existing_anchor(out_headings[1][1]) == "assert"
    assert not any("retired" in n for n in notes), notes


def test_inject_duplicate_heading_dedup_key_retires_without_stealing():
    """身分鍵是 dedup 後的 slug（`references`/`references-1`），不是原始文字。

    舊 English 裡 `References` 出現兩次(索引 0 與 2)，anchor 掛在索引 2
    （去重後的鍵是 `references-1`）。新 English 只剩一個 `References`。
    索引 2 的身分在新版找不到對應，必須退場；存活下來的那個 `References`
    (鍵是 `references`，不是 `references-1`) 不能偷走這個 anchor。
    """
    prev_en = "# References\n\n# Layout\n\n# References\n"
    new_en = "# References\n\n# Other\n"
    prev_zh = "# 參照甲\n\n# 排版\n\n# 參照乙 {#references-1}\n"
    zh = "# 參照\n\n# 其他\n"

    out, notes = anchors.inject_report(zh, new_en, prev_zh, prev_en)

    assert "{#references-1}" not in out
    assert any("references-1" in n and "retired" in n for n in notes), notes
    out_headings = anchors.headings(out)
    assert anchors.existing_anchor(out_headings[0][1]) != "references-1"


def test_inject_retires_anchor_when_renamed_to_different_slug():
    """`Create and use an instance` -> `Creating an Instance`：真的改名，slug 也真的不同，仍要退場。"""
    prev_en = "# A\n\n# Create and use an instance\n\n# C\n"
    new_en = "# A\n\n# Creating an Instance\n\n# C\n"
    prev_zh = "# 一\n\n# 建立與使用 {#create-and-use-an-instance}\n\n# 三\n"
    zh = "# 甲\n\n# 建立實例\n\n# 丙\n"

    out, notes = anchors.inject_report(zh, new_en, prev_zh, prev_en)

    assert "{#create-and-use-an-instance}" not in out
    assert any(
        "create-and-use-an-instance" in n and "retired" in n for n in notes
    ), notes


def _tracked_md_files(ref: str) -> list[str]:
    r = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "-z", ref, "book", "reference"],
        capture_output=True, text=True, check=True,
    )
    return [f for f in r.stdout.split("\0") if f.endswith(".md")]


def _safe_show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def _safe_body_at(ref: str, path: str) -> str | None:
    raw = _safe_show(ref, path)
    if raw is None:
        return None
    _, body = frontmatter.split(raw)
    return body


def test_inject_real_data_sweep_carries_45_retires_4():
    """跨全部 35 個帶 anchor 的中文檔，用 merge-base 英文當 prev_en、
    english-main 英文當「重新翻譯」的替身，度量 carry-forward 的真實效果。

    slug 鍵應該把 43/6 提升到 45/4——多救回的兩個是純大小寫改名
    （error-constants、unpacking-a-struct），其餘四個退場都是上游真的
    改名或刪除章節。跳過 prev_zh/prev_en 標題數不符的檔案(gate 1 的工作，
    不是這個測試的工作)。
    """
    expected_retired = {
        "book/guides/2024-migration-guide.md::method-aliases",
        "book/move-basics/references.md::references",
        "book/move-basics/struct.md::struct",
        "book/move-basics/struct.md::create-and-use-an-instance",
    }

    carried = 0
    retired: set[str] = set()

    for path in _tracked_md_files(_PRE_FIX):
        zh_raw = _safe_show(_PRE_FIX, path)
        if not zh_raw or "{#" not in zh_raw:
            continue

        prev_zh = _safe_body_at(_PRE_FIX, path)
        prev_en = _safe_body_at(_MERGE_BASE, path)
        new_en = _safe_body_at("english-main", path)
        if prev_zh is None or prev_en is None or new_en is None:
            continue

        prev_zh_h = anchors.headings(prev_zh)
        prev_en_h = anchors.headings(prev_en)
        if len(prev_zh_h) != len(prev_en_h):
            continue  # gate 1 的工作，不是這個測試的工作

        _, notes = anchors.inject_report(new_en, new_en, prev_zh, prev_en)

        prev_anchor_count = sum(
            1 for _, t in prev_zh_h if anchors.existing_anchor(t) is not None
        )
        file_retired = 0
        for n in notes:
            if "retired" not in n:
                continue
            file_retired += 1
            aid = n.split("{#", 1)[1].split("}", 1)[0]
            retired.add(f"{path}::{aid}")
        carried += prev_anchor_count - file_retired

    assert carried == 45, f"carried={carried}, retired={retired}"
    assert retired == expected_retired
