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


@pytest.mark.parametrize("ch", ["台", "游", "了", "群", "才", "峰"])
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
