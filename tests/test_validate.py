import subprocess

import pytest

from pathlib import Path

from scripts.zh_tw import anchors, frontmatter, validate

_REPO_ROOT = Path(__file__).resolve().parent.parent

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
    """gate 6 需要 prev_zh *與* prev_en 同時在場才會檢查身分（見
    check_file 對 gate 6 的說明）；沒有 prev_en 時無法分辨「翻譯弄丟了
    anchor」與「上游刪掉了對應章節」，因此這裡也要給 prev_en，讓
    T 這個英文標題在新舊版之間保持不變，才能真正驗證「消失」被抓到。"""
    prev_en = '---\ndescription: "d"\n---\n\n# T\n'
    prev = '---\ndescription: "描述"\n---\n\n# 標 {#custom-id}\n'
    en = '---\ndescription: "d"\n---\n\n# T\n'
    zh = '---\ndescription: "描述"\n---\n\n# 標 {#t}\n'
    errs = validate.check_file(zh, en, prev, prev_en)
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


def test_check_links_ignores_links_inside_fenced_code_block():
    """gate 5 掃連結前必須先遮蔽 code（比照 gate 8）：fence 內的
    [x](./foo#bar) 是範例文字，不是真連結，不遮蔽會產生假陽性擋寫檔。"""
    files = {
        "book/a.md": "# A {#a}\n\n```md\n[x](./nonexistent#bar)\n```\n"
    }
    assert validate.check_links(files) == []


def test_check_links_ignores_links_inside_inline_code_span():
    files = {
        "book/a.md": "# A {#a}\n\n寫成 `[x](./nonexistent#bar)` 這樣。\n"
    }
    assert validate.check_links(files) == []


def test_check_links_still_checks_prose_link_next_to_code_block():
    """遮蔽只能吃掉 code 內的連結；同一檔散文裡的壞連結仍要報。"""
    files = {
        "book/a.md": (
            "# A {#a}\n\n```md\n[x](./nonexistent#bar)\n```\n\n[real](./b#missing)\n"
        ),
        "book/b.md": "# B {#target}\n",
    }
    errs = validate.check_links(files)
    assert len(errs) == 1 and "missing" in errs[0]


# --- F2 / gate 9: body 標題必須帶「中文 (English)」後綴（僅新翻譯路徑） ---


def test_heading_suffix_passes_when_value_matches_english():
    zh = "# 區域變數 (Local Variables) {#x}\n\n## `let` 綁定 (`let` bindings)\n"
    en = "# Local Variables\n\n## `let` bindings\n"
    assert validate.check_heading_suffix(zh, en) == []


def test_heading_suffix_reports_dropped_suffix():
    zh = "# 區域變數 (Local Variables) {#x}\n\n## 何時需要標註型別\n"
    en = "# Local Variables\n\n## When annotations are necessary\n"
    errs = validate.check_heading_suffix(zh, en)
    assert len(errs) == 1 and "When annotations are necessary" in errs[0]


def test_heading_suffix_reports_wrong_value_not_just_presence():
    """L2：驗值不驗形。括號在、值錯（配到別的標題文字）必須報。"""
    zh = "# 區域變數 (Scope) {#x}\n"
    en = "# Local Variables\n"
    errs = validate.check_heading_suffix(zh, en)
    assert len(errs) == 1 and "Local Variables" in errs[0]


def test_heading_suffix_allows_untranslated_proper_noun():
    zh = "# BCS {#bcs}\n"
    en = "# BCS\n"
    assert validate.check_heading_suffix(zh, en) == []


def test_heading_suffix_allows_untranslated_pure_code_heading():
    zh = "## `copy` {#copy}\n"
    en = "## `copy`\n"
    assert validate.check_heading_suffix(zh, en) == []


def test_heading_suffix_rejects_untranslated_prefix_with_correct_suffix():
    """「記得格式、忘了翻譯」的相鄰變體：後綴值正確但前綴仍是英文散文。
    合法前綴要嘛含 CJK（一般譯文），要嘛去 code 後無小寫（縮寫，如
    BCS (Binary Canonical Serialization)）。"""
    en = "## Scopes\n"
    assert len(validate.check_heading_suffix("## Scopes (Scopes) {#s}\n", en)) == 1
    assert len(validate.check_heading_suffix("## Le scope (Scopes) {#s}\n", en)) == 1


def test_heading_suffix_allows_acronym_prefix_without_cjk():
    zh = "# BCS (Binary Canonical Serialization) {#bcs}\n"
    en = "# Binary Canonical Serialization\n"
    assert validate.check_heading_suffix(zh, en) == []


def test_heading_suffix_rejects_verbatim_prose_heading():
    """Task 17 A/B 的另一半失效模式：sonnet 把「Scopes」整個沒翻、verbatim
    複製。zh == en 豁免只能給「去 inline code 後無小寫」的標題（專有名詞、
    縮寫、純 code —— english-main 實測 1154 個標題中僅 14 個），含小寫散文
    的標題 verbatim 複製 = 沒翻譯，必須報。"""
    zh = "## Scopes {#scopes}\n"
    en = "## Scopes\n"
    errs = validate.check_heading_suffix(zh, en)
    assert len(errs) == 1 and "Scopes" in errs[0]


def test_heading_suffix_handles_english_heading_with_parens():
    zh = "# 中文 (Foo (bar)) {#x}\n"
    en = "# Foo (bar)\n"
    assert validate.check_heading_suffix(zh, en) == []


def test_heading_suffix_rejects_empty_prefix():
    """只有 (English) 沒有譯文，等於沒翻，必須報。"""
    zh = "# (Local Variables) {#x}\n"
    en = "# Local Variables\n"
    assert len(validate.check_heading_suffix(zh, en)) == 1


def test_heading_suffix_abstains_on_count_mismatch():
    """by-index 配對只在標題數一致時成立；不一致由 gate 1 負責報錯，
    本 gate 棄權（鏡射 gate 6 對 by-index 前提的處理）。"""
    zh = "# 甲 {#a}\n"
    en = "# A\n\n## B\n"
    assert validate.check_heading_suffix(zh, en) == []


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


def test_gate6_abstains_without_prev_en():
    """D-deadlock repro: without prev_en, inject() correctly declines to carry
    any anchor forward (index matching would risk the D10 bug). Gate 6 must
    not then report those same anchors as having disappeared -- its
    precondition for checking anything is the same as inject()'s precondition
    for carrying anything: prev_en must be present."""
    prev_en = "# H0\n\n## Alpha\n\n## Beta\n"
    prev_zh = "# H0 {#h0}\n\n## 甲 {#alpha-id}\n\n## 乙 {#beta-id}\n"
    en = "# H0\n\n## Gamma\n"
    zh = "# H0 {#h0}\n\n## 丙\n"
    assert validate.check_file(zh, en, prev_zh, "") == []


def test_gate6_deadlock_reproduction_no_prev_en():
    """The exact deadlock from the task spec: a file with anchors and no
    recoverable prev_en must not be permanently unwritable."""
    en = '---\ndescription: "Vectors."\n---\n\n# Vector\n\nBody.\n\n## Syntax\n\nMore.\n'
    prev_zh = '---\ndescription: "描述"\n---\n\n# 甲 {#alpha}\n\n## 乙 {#beta}\n'
    _, en_body = frontmatter.split(en)
    _, prev_zh_body = frontmatter.split(prev_zh)

    zh_meta = {"description": "向量相關內容。"}
    zh_body_translated = "# 向量\n\n內容。\n\n## 語法\n\n更多內容。\n"
    zh_body = anchors.inject(zh_body_translated, en_body, prev_zh_body, "")
    zh = frontmatter.join(zh_meta, zh_body)

    assert validate.check_file(zh, en, prev_zh, "") == []


MERGE_BASE = "f2c0a93e1a0422078d3d051e4410ac3edc612016"
PRE_FIX = "0d4b8bea77f1a6195b589ded4067d287adb4379a"


def _show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


# --- Finding 1 / gate 6: prev_en's slug keys indexed by prev_zh's heading index ---


def test_gate6_heading_count_drift_does_not_misfire():
    """一個插在 anchored 標題前面的多餘中文標題，不該讓 index-based
    比對把後面每個 anchor 都判成「被重新指派」。prev_zh 比 prev_en 多一個
    標題（「額外」），且新版 zh 已經正確對齊 en，不該報錯。"""
    prev_en = "# A\n\n## B\n\n## C\n"
    prev_zh = "# 甲\n\n## 額外\n\n## 乙 {#b}\n\n## 丙 {#c}\n"
    en = "# A\n\n## B\n\n## C\n"
    zh = "# 甲\n\n## 乙 {#b}\n\n## 丙 {#c}\n"
    assert validate.check_file(zh, en, prev_zh, prev_en) == []


def test_gate6_still_detects_reassignment_when_counts_match():
    """標題數對齊時，guard 不能把 gate 6 整個關掉——真正的重新指派仍要報錯。"""
    prev_en = "# H0\n\n## Alpha\n\n## Beta\n"
    prev_zh = "# H0 {#h0}\n\n## 甲 {#alpha-id}\n\n## 乙 {#beta-id}\n"
    en = "# H0\n\n## Alpha\n\n## Beta\n"
    # alpha-id 錯放到 Beta 對應的標題上。
    zh_bad = "# H0 {#h0}\n\n## 甲\n\n## 乙 {#alpha-id}\n"
    errs = validate.check_file(zh_bad, en, prev_zh, prev_en)
    assert any("alpha-id" in e for e in errs)


def test_gate6_real_data_heading_count_drift():
    """reference/variables.md（6 中文標題 vs 21 英文）與
    book/storage/storage-functions.md（11 vs 13）是修復前 zh-tw-main 上
    真實存在標題數落差的兩個已 anchor 檔案。inject() 產出的新版 zh 是正確
    對齊 en 的，gate 6 不該對它們報 anchor 重新指派。

    這個真實資料案例本身不足以證明修復有效：storage-functions.md 唯一的
    自訂 anchor `{#transfer}` 恰好等於它在新版英文標題上衍生出的 slug
    （tier-3 推導與明確 id 湊巧相同），所以就算 gate 6 誤判成「標題數對齊」
    去跑消失檢查，也剛好找不到任何消失的 id —— 綠燈是資料的巧合，不是程式
    碼正確。因此下面另外用一個建構出來的案例補上：舊中文 anchor 是 tier-3
    絕對推導不出來的 id（`{#custom-beta}` 掛在英文文字是 `Beta Heading`
    的標題上，slugify 只會推出 `beta-heading`），修復前的程式碼在這個案例
    上一定會報「消失」，修復後必須完全不報。"""
    for path in ("reference/variables.md", "book/storage/storage-functions.md"):
        prev_zh_full = _show(PRE_FIX, path)
        prev_en_full = _show(MERGE_BASE, path)
        en_full = _show("english-main", path)
        if not prev_zh_full or not prev_en_full or not en_full:
            pytest.skip(f"{path} unavailable in this checkout")

        _, prev_zh_body = frontmatter.split(prev_zh_full)
        _, prev_en_body = frontmatter.split(prev_en_full)
        zh_meta, en_body = frontmatter.split(en_full)

        zh_body = anchors.inject(en_body, en_body, prev_zh_body, prev_en_body)
        zh_text = frontmatter.join(zh_meta, zh_body)

        errs = validate.check_file(zh_text, en_full, prev_zh_full, prev_en_full)
        assert not any("anchor" in e for e in errs), (path, errs)

    # 建構案例：舊中文比舊英文多一個標題（4 vs 3），custom-beta / custom-gamma
    # 是 tier-3 永遠推導不出來的 id（衍生 slug 會是 beta-heading /
    # gamma-heading）。這是本次修復的原始 repro。
    prev_en = "# A\n\n## Beta Heading\n\n## Gamma Heading\n"
    prev_zh = (
        "# 甲\n\n## 額外 {#extra-id}\n\n## 乙 {#custom-beta}\n\n## 丙 {#custom-gamma}\n"
    )
    en = prev_en
    zh = anchors.inject(en, en, prev_zh, prev_en)
    assert validate.check_file(zh, en, prev_zh, prev_en) == []


def test_gate6_heading_count_drift_repro_returns_empty():
    """The exact reproduction pasted in the task spec: prev_zh has 4 headings,
    prev_en has 3. inject() correctly carries nothing forward; gate 6 must not
    report the declined-to-carry anchors as disappeared."""
    prev_en = "# A\n\n## Beta Heading\n\n## Gamma Heading\n"
    prev_zh = (
        "# 甲\n\n## 額外 {#extra-id}\n\n## 乙 {#custom-beta}\n\n## 丙 {#custom-gamma}\n"
    )
    en = prev_en
    zh = anchors.inject(en, en, prev_zh, prev_en)
    assert zh_anchor_ids(zh) == ["a", "beta-heading", "gamma-heading"]
    assert validate.check_file(zh, en, prev_zh, prev_en) == []


def zh_anchor_ids(body: str) -> list[str]:
    return [aid for _, t in anchors.headings(body) if (aid := anchors.existing_anchor(t))]


def test_gate6_heading_count_drift_pipeline_assemble_succeeds():
    """pipeline.assemble must not raise ValidationError on the reproduction's
    inputs, and the anchors it produces must carry none of the previous
    custom ids forward (they cannot be identity-matched: prev_zh and prev_en
    have different heading counts)."""
    from scripts.zh_tw import pipeline
    from scripts.zh_tw.backends.fake import FakeBackend

    prev_en = "# A\n\n## Beta Heading\n\n## Gamma Heading\n"
    prev_zh = (
        "# 甲\n\n## 額外 {#extra-id}\n\n## 乙 {#custom-beta}\n\n## 丙 {#custom-gamma}\n"
    )
    en = prev_en

    out = pipeline.assemble(en, prev_zh, prev_en, FakeBackend())
    out_ids = set(zh_anchor_ids(out))
    assert out_ids.isdisjoint({"extra-id", "custom-beta", "custom-gamma"})


def test_gate6_real_deadlocked_files_no_prev_en():
    """book/testing/{test-scenario,test-utilities,testing-basics}.md were hand-
    translated from an upstream PR before it merged, are absent from the
    manifest, and have no English counterpart at the merge-base -- so
    pipeline._prev_en() returns "". Before this fix, gate 6's disappearance
    fallback reported every one of their anchors as lost, forever, because
    inject() correctly refuses to carry anchors without prev_en."""
    for path in (
        "book/testing/test-scenario.md",
        "book/testing/test-utilities.md",
        "book/testing/testing-basics.md",
    ):
        prev_zh_full = _show(PRE_FIX, path)
        en_full = _show("english-main", path)
        if not prev_zh_full or not en_full:
            pytest.skip(f"{path} unavailable in this checkout")

        _, prev_zh_body = frontmatter.split(prev_zh_full)
        zh_meta, en_body = frontmatter.split(en_full)

        zh_body = anchors.inject(en_body, en_body, prev_zh_body, "")
        zh_text = frontmatter.join(zh_meta, zh_body)

        errs = validate.check_file(zh_text, en_full, prev_zh_full, "")
        assert not any("anchor" in e for e in errs), (path, errs)


# --- Finding 2 / _anchor_ids: explicit ids not reserved before deriving ---


def test_anchor_ids_reserves_explicit_ids_before_deriving():
    """`## Custom` 是第一個 id-less 標題，`## Custom {#custom}` 明確佔用了
    `custom`。真相是 inject() 會把 id-less 那個標題衍生成 `custom-1`
    （因為 `custom` 已被明確 id 佔走），_anchor_ids 必須算出同一個結果，
    而不是各自獨立衍生後才發現撞名、直接聯集成只有兩個 id。"""
    body = "# T\n\n## Custom\n\n## Custom {#custom}\n"
    ids = validate._anchor_ids(body)
    assert "custom" in ids
    assert "custom-1" in ids

    injected = anchors.inject(body, body)
    injected_ids = {
        aid for _, t in anchors.headings(injected) if (aid := anchors.existing_anchor(t))
    }
    assert ids == injected_ids


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


@pytest.mark.parametrize("ch", ["台", "游", "祕", "了", "群", "才", "峰"])
def test_gate8_does_not_flag_allowlisted_or_non_simplified_chars(ch):
    body = f"這是一段包含 {ch} 字的文字。\n"
    hits = validate.simplified_chars(body)
    assert not any(c == ch for _, c in hits)


@pytest.mark.parametrize("ch", ["裏", "着"])
def test_gate8_flags_hk_mainland_variants_not_moe_standard(ch):
    """REJECTED finding: 有人主張 `裏`/`着` 該加進 ALLOWED_VARIANTS，理由是
    s2tw 誤判了合法台灣用字。這是錯的——教育部標準字形是 `裡`/`著`，
    `裏`/`着` 是港澳/中國大陸的字形，s2tw 把它們轉換掉是本關卡的目的，
    不是假陽性。不要把這兩個字加進白名單。"""
    body = f"這是一段包含 {ch} 字的文字。\n"
    hits = validate.simplified_chars(body)
    assert any(c == ch for _, c in hits)


def test_gate8_accepts_both_forms_of_the_secret_character():
    """「祕」與「秘」在台灣並存，兩個都不是簡體字，gate 都不該攔。

    教育部《異體字字典》以「祕」為正字（祕密、神祕），但 OpenCC 的 s2tw 會把
    祕→秘 —— 逐字套用時就變成「祕是簡體」的假陽性。實測後果：codex 寫「祕密」，
    `book/programmability/randomness.md` 連續三輪排乾都被這條擋掉，而現有語料
    2 處寫的是「秘密」。硬要統一得改語料又得加違禁詞，不值得 —— **gate 的職責
    是攔簡體，不是統一異體字選擇**（2026-09-05 使用者裁決）。

    對照組 `裏`/`着` 仍必須被攔：那兩個是港澳/中國大陸字形，教育部標準是
    `裡`/`著`，不是同一回事（見上面那條 REJECTED finding）。
    """
    for body in ["這是祕密資訊。\n", "這是秘密資訊。\n", "神祕的隨機性。\n"]:
        assert validate.simplified_chars(body) == [], body
    assert validate.simplified_chars("这是简体。\n"), "真簡體仍須被攔"


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


# --- tier 分層依據：spec §五「A 層前提是 validate 第 1、2 條」 ---


def test_check_structure_ignores_non_structural_defects():
    """未翻 frontmatter 與內文違禁詞是 backfill 要修的缺陷，不是結構問題；
    check_structure 不得回報它們（否則 tier 會把待修檔誤降 B 層全譯）。"""
    en = '---\ndescription: "Constants."\n---\n\n# Constants\n\nText.\n'
    zh = '---\ndescription: "Constants."\n---\n\n# 常數 {#constants}\n\n循環與返回。\n'
    assert validate.check_structure(zh, en) == []
    assert validate.check_file(zh, en)  # 全量 gate 仍須抓到這些缺陷


def test_check_structure_flags_heading_and_fence_mismatch():
    en = "# One\n\n## Two\n\n```move\nlet x;\n```\n"
    zh = "# 一\n"
    errs = validate.check_structure(zh, en)
    assert any("標題層級序列" in e for e in errs)
    assert any("fence" in e for e in errs)


# --- A 路徑寫檔 gate：check_frontmatter（gate 3/4 + 新翻值的品質掃描） ---


def test_check_frontmatter_scans_translated_values():
    """frontmatter 值是管線新生成的內容，違禁詞/簡體必須被抓
    （實測 5 個現有檔的 description/title 帶違禁詞流出，body-only 掃描是漏洞）。"""
    en = '---\ndescription: "Loops."\ntitle: "Loops"\n---\n\n# Loops\n'
    zh = '---\ndescription: "循環結構。"\ntitle: "循環"\n---\n\n# 迴圈 {#loops}\n'
    errs = validate.check_frontmatter(zh, en)
    assert any("循環" in e for e in errs)


def test_check_frontmatter_ignores_legacy_body():
    """A 層 body 是 legacy 舊譯文，其既有債務不歸 check_frontmatter 管。"""
    en = '---\ndescription: "C."\n---\n\n# C\n\nText.\n'
    zh = '---\ndescription: "常數。"\n---\n\n# 常數 {#c}\n\n這段有循環。\n'
    assert validate.check_frontmatter(zh, en) == []


def test_check_file_reports_forbidden_word_in_frontmatter_value():
    en = '---\ndescription: "Loops."\n---\n\n# Loops\n'
    zh = '---\ndescription: "循環。"\n---\n\n# 迴圈 {#loops}\n'
    assert any("循環" in e for e in validate.check_file(zh, en))


# --- heading_suffix_error：gate 9 的單標題判定（與修復 pass 共用） ---


def test_heading_suffix_error_single_heading_cases():
    ok = validate.heading_suffix_error
    assert ok("迴圈 (Loops)", "Loops") is None
    assert ok("BCS", "BCS") is None  # 無小寫豁免
    assert ok("`copy`", "`copy`") is None  # code span 剝除後無小寫
    assert ok("Loops", "Loops")  # 含小寫 verbatim = 未翻
    assert ok("迴圈", "Loops")  # 缺後綴
    assert ok("Loop stuff (Loops)", "Loops")  # 前綴未翻


def test_heading_suffix_error_exempts_proper_noun_headings():
    """產品名沒有中文譯名，verbatim 才是正解。

    舊版只豁免「無小寫」（BCS），VSCode / Emacs / Github Codespaces 含小寫
    → 判未翻譯 → 修復 pass 只能叫 backend 硬掰中文前綴，實測產出
    「VSCode 整合開發環境 (VSCode)」這種贅語（run 33367759448 / PR #17）。
    """
    ok = validate.heading_suffix_error
    assert ok("VSCode", "VSCode") is None
    assert ok("Emacs", "Emacs") is None
    assert ok("Zed", "Zed") is None
    assert ok("Github Codespaces", "Github Codespaces") is None
    assert ok("IntelliJ IDEA", "IntelliJ IDEA") is None
    assert ok("Party", "Party") is None  # 2026-08-31 裁決：party 保留原文


def test_heading_suffix_error_proper_noun_exemption_is_not_a_blanket_pass():
    """豁免必須逐 token 全稱，否則等於把 gate 9 的 verbatim 判定廢掉。

    只要有一個 token 不是已知專有名詞，散文標題就仍要被擋 —— 這正是
    Task 17 A/B 觀測到的 backend 失效模式（sonnet 對 "Scopes"）。
    """
    ok = validate.heading_suffix_error
    assert ok("Set Up Your IDE", "Set Up Your IDE")  # Set/Up/Your 不在表內
    assert ok("Move Basics", "Move Basics")  # Move 在表內、Basics 不在
    assert ok("Scopes", "Scopes")
    assert ok("Loops", "Loops")


# --- 簡體偵測的詞級白名單：干/准 在特定詞裡是合法繁體 ---


def test_simplified_chars_allows_gan_zhun_in_whitelisted_words():
    """PR 3 實測：sonnet 輸出「若干差異」「收集批准」被 gate 8 決定性擋下，
    但 干（若干/干擾）與 准（批准/准許）是合法繁體。字級豁免風險太高
    （干=幹/乾、准=準 的簡體誤用極常見），改詞級白名單。"""
    assert validate.simplified_chars("這裡有若干差異。\n") == []
    assert validate.simplified_chars("必須收集批准。\n") == []
    assert validate.simplified_chars("訊號干擾與獲准進入。\n") == []


def test_simplified_chars_still_flags_bare_gan_zhun():
    """白名單外的 干/准 仍攔：這正是它們的簡體誤用形態。"""
    assert validate.simplified_chars("你在干什麼。\n")  # 干=幹 的簡體用法
    assert validate.simplified_chars("瞄准目標。\n")  # 准=準 的簡體用法


# --- gate 11：有序列表序號被重複寫進內文 ---

_FM = '---\ndescription: "x"\n---\n\n'


def test_ordered_list_numbering_flags_duplicated_marker():
    """2026-09-03 run 33730438417 / PR #24 的 foreword.md：機翻把 markdown 的
    `1.` 又抄進粗體，讀者看到「1. 1. 預設安全性」。結構/術語/簡體/prettier
    全部看不到。"""
    bad = _FM + "1. **1. 預設安全性:** 內文\n\n2. **2. 表達力:** 內文\n"
    errs = validate.check_ordered_list_numbering(bad)
    assert len(errs) == 2, errs
    assert all("序號重複" in e for e in errs)


def test_ordered_list_numbering_silent_after_fix():
    good = _FM + "1. **預設安全性:** 內文\n\n2. **表達力:** 內文\n"
    assert validate.check_ordered_list_numbering(good) == []


def test_ordered_list_numbering_matches_identity_not_shape():
    """判準是身分（前導數字 == 這一項的序號），不是「開頭有數字」。

    lessons L2：用「開頭有沒有數字」這個廉價代理量，會把合法內容
    （`1. 2024 版本…`）判成缺陷。
    """
    assert validate.check_ordered_list_numbering(_FM + "1. 2024 版本引入了新語法\n") == []
    assert validate.check_ordered_list_numbering(_FM + "1. 甲\n2. 2024 版本\n") == []


def test_ordered_list_numbering_honours_start_and_nesting():
    """序號取自渲染後的 <ol>（含 start= 與巢狀重新計數），不重刻列表編號規則。"""
    assert validate.check_ordered_list_numbering(_FM + "5. **5. 壞的**\n")
    assert validate.check_ordered_list_numbering(_FM + "5. **1. 好的**\n") == []
    assert validate.check_ordered_list_numbering(_FM + "1. 外\n\n   1. **1. 內壞**\n")


def test_ordered_list_numbering_ignores_unordered_and_code():
    """無序列表沒有序號可重複；code fence 內是範例，不是散文。"""
    assert validate.check_ordered_list_numbering(_FM + "- 1. 這不是有序列表\n") == []
    assert validate.check_ordered_list_numbering(_FM + "```\n1. 1. 假的\n```\n") == []


def test_ordered_list_numbering_no_false_positive_on_corpus():
    """全語料實測偽陽性 0 —— 這條守衛開下去不會擋到現有內容。

    範圍必須等於 check_repo.collect() 的範圍（book + reference）：守衛只掃
    book/ 的話，覆蓋面就不等於它宣稱保護的語料（外部 review 2026-09-04）。
    """
    files = [p for base in ("book", "reference") for p in (_REPO_ROOT / base).rglob("*.md")]
    assert len(files) > 100, files  # 路徑寫錯時不要靜默通過
    hits = {
        str(p): errs
        for p in files
        if (errs := validate.check_ordered_list_numbering(p.read_text(encoding="utf-8")))
    }
    assert hits == {}


def test_ordered_list_numbering_needs_a_delimiter_then_whitespace():
    """誤報在這道 gate 的代價特別高：pipeline 對 check_file 的任一錯誤直接
    raise，該檔就永久寫不出來、每輪人工。所以前導數字後面必須是「分隔符 +
    空白/行尾」，`1.0 版本` 的小數點不算（外部 review 2026-09-04 實測）。
    """
    assert validate.check_ordered_list_numbering(_FM + "1. 1.0 版本引入了新語法\n") == []
    assert validate.check_ordered_list_numbering(_FM + "1. 甲\n2. 2.0 版本\n") == []
    # 全形分隔符刻意不收：「1、2、3 三種模式都支援」「1）與 2）的差別」是
    # 合法中文列舉，字面上與「重複的列表標記」無法區分。本 gate 沒有自動
    # 修復路徑，誤報一次就是該檔永久寫不出來，所以寧可漏報。
    assert validate.check_ordered_list_numbering(_FM + "1. 1、2、3 三種模式都支援\n") == []
    assert validate.check_ordered_list_numbering(_FM + "1. 1）與 2）的差別\n") == []
    assert validate.check_ordered_list_numbering(_FM + "1. **1. 真缺陷**\n")  # 仍要紅


def test_ordered_list_numbering_ignores_inline_code():
    """`` 1. `1.` 是有序列表標記 `` 是在講標記本身，不是把序號抄進內文。"""
    assert validate.check_ordered_list_numbering(_FM + "1. `1.` 是有序列表標記\n") == []
    assert validate.check_ordered_list_numbering(_FM + "1. <code>1.</code> x\n") == []


def test_ordered_list_numbering_is_wired_into_check_file():
    """gate 11 必須真的掛在寫檔守門員上。只測函式本身的話，把接線拆掉
    （check_file 不再呼叫它）測試仍會全綠 —— 守衛等於沒開。"""
    en = '---\ndescription: "x"\n---\n\n# T\n\n1. **Secure by default:** a\n'
    zh = '---\ndescription: "x"\n---\n\n# T {#t}\n\n1. **1. 預設安全性:** 甲\n'
    assert any("序號重複" in e for e in validate.check_file(zh, en))


def test_ol_items_does_not_attribute_nested_text_to_outer_item():
    """子列表有自己的序號序列。把它的文字併進外層，外層項目的「前導文字」
    就會變成子項目的文字 —— 前導數字對到錯誤的序號（偽陽性或漏報）。"""
    import commonmark

    items = validate._ol_items(commonmark.commonmark("1. 外\n\n   1. **1. 內壞**\n"))
    assert len(items) == 2
    (outer_n, outer_text), (inner_n, inner_text) = items
    assert (outer_n, inner_n) == (1, 1)
    assert "內壞" not in outer_text, outer_text
    assert inner_text.startswith("1. 內壞")


def test_gate5_skips_links_inside_html_comments():
    """註解掉的內容不會被渲染，裡面的懸空錨點無害，不該擋寫檔。

    實測現場（2026-09-05 排乾）：`reference/abilities.md` 的
    `<!-- TODO：…[動機說明](#motivating-walkthrough)… -->` 指向一個還沒寫的
    章節，**英文原文同樣是懸空的**。舊譯文把整段註解漏譯，所以這個缺口一直
    沒被看見；新譯文把註解保留下來（比較忠實），gate 5 才第一次紅。

    註解遮罩**不併進 `glossary.protected_mask`** —— 它的語意是「哪裡是程式
    碼」，被 5 個消費端共用，擴張它等於偷改所有消費端的語意（lessons L2，
    2026-09-04 已犯過一次：把 URLISH 併進去造成 4 個測試轉紅）。
    """
    files = {
        "a.md": (
            "# 標題 (T) {#t}\n\n"
            "<!-- TODO：這一段還沒寫\n\n"
            "或許可跳至[動機說明](#motivating-walkthrough)章節。 -->\n\n"
            "正文。\n"
        )
    }
    assert validate.check_links(files) == []


def test_gate5_still_flags_dangling_anchors_outside_comments():
    """對照組：註解**外面**的懸空錨點照樣要擋 —— 否則這道豁免就從
    「別管註解」擴張成「別管連結」。"""
    files = {
        "a.md": (
            "# 標題 (T) {#t}\n\n"
            "<!-- 註解裡的[連結](#nope-in-comment) -->\n\n"
            "正文裡的[連結](#nope-in-body)。\n"
        )
    }
    errs = validate.check_links(files)
    assert len(errs) == 1, errs
    assert "nope-in-body" in errs[0] and "nope-in-comment" not in errs[0], errs
