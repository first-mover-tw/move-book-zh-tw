import re
import subprocess
import pytest

from scripts.zh_tw import anchors, frontmatter, manifest, pipeline, validate
from scripts.zh_tw.backends.fake import FakeBackend

EN = '---\ndescription: "Vectors."\n---\n\n# Vector\n\nBody text here.\n\n## Syntax\n\nMore text.\n'
PREV_ZH = '---\ndescription: "向量。"\n---\n\n# 向量 {#vector}\n\n舊內文。\n\n## 語法 {#custom-syntax}\n\n舊文字。\n'
PREV_EN = '---\ndescription: "Vectors."\n---\n\n# Vector\n\nOld body.\n\n## Syntax\n\nOld text.\n'


def test_translate_body_preserves_heading_count():
    out = pipeline.translate_body(EN, FakeBackend())
    _, body = frontmatter.split(out)
    assert len(anchors.headings(body)) == 2


def test_anchor_injection_runs_after_chunk_join():
    """切段後拼回，anchor 序號必須以全域序列為準。"""
    out = pipeline.assemble(EN, PREV_ZH, PREV_EN, FakeBackend(), max_lines=1)
    assert "{#vector}" in out
    assert "{#custom-syntax}" in out  # 沿用，不是 {#syntax}


def test_glossary_enforced_on_output():
    en = '---\ndescription: "desc"\n---\n\n# T\n'

    class BadBackend:
        def translate(self, text, *, kind="markdown"):
            if kind == "text":
                return "中文"
            return "# 標題 (T)\n\n這個函數會返回值\n"

    out = pipeline.assemble(en, "", "", BadBackend())
    _, zh_body = frontmatter.split(out)
    assert "函式" in zh_body and "回傳" in zh_body
    assert "函數" not in zh_body


def test_assemble_raises_when_backend_truncates():
    en = '---\ndescription: "d"\n---\n\n# One\n\n## Two\n\n## Three\n'

    class TruncatingBackend:
        def translate(self, text, *, kind="markdown"):
            return "# 一\n"

    with pytest.raises(Exception):
        pipeline.assemble(en, "", "", TruncatingBackend())


def test_tier_a_for_frontmatter_only_delta():
    """book/404.md：上游只加了 frontmatter，中英文標題數相符 -> A 層。"""
    assert pipeline.tier("book/404.md") == "A"


# tier 的結構降級（B-強制）fixture 已絕跡：PR 3 修復了全部 15 個結構殘缺檔。
# 降級邏輯由 check_structure 合成 unit tests 與 tier 的 A 判定測試覆蓋。


# --- additional coverage required by Task 11 brief ---


def test_assemble_preserves_heading_and_fence_count():
    en = (
        '---\ndescription: "desc"\n---\n\n# One\n\n'
        '```rust\nlet x = 1;\n```\n\n## Two\n\nsome text\n'
    )
    out = pipeline.assemble(en, "", "", FakeBackend())
    _, en_body = frontmatter.split(en)
    _, zh_body = frontmatter.split(out)
    assert len(anchors.headings(zh_body)) == len(anchors.headings(en_body))
    assert anchors.fence_lines(zh_body) == anchors.fence_lines(en_body)


def test_backend_dropping_heading_raises():
    """這是 variables.md 截斷事故的縮影：backend 少吐一個標題就必須整份炸掉，
    不能悄悄寫出一份結構殘缺的檔案。"""
    en = '---\ndescription: "d"\n---\n\n# One\n\n## Two\n\n## Three\n'

    class DroppingBackend:
        def translate(self, text, *, kind="markdown"):
            if kind == "text":
                return "中文"
            return "# 一\n\n## 二\n"  # 少了 Three

    with pytest.raises(anchors.HeadingMismatch):
        pipeline.assemble(en, "", "", DroppingBackend())


def test_glossary_rewrites_function_term():
    en = '---\ndescription: "d"\n---\n\n# T\n'

    class FuncBackend:
        def translate(self, text, *, kind="markdown"):
            if kind == "text":
                return "中文"
            return "# 標題 (T)\n\n這是一個函數\n"

    out = pipeline.assemble(en, "", "", FuncBackend())
    assert "函式" in out
    assert "函數" not in out


def test_anchor_from_later_heading_correct_after_chunking():
    """建構一份夠長需要切段的內文，確認後段標題衍生出的 anchor 正確 —— 證明
    inject 是在 chunking.join 之後對整份文件跑一次，而不是逐段各自注入。"""
    body_lines = ["# Intro\n\n"]
    for i in range(300):
        body_lines.append(f"filler line {i}\n")
    body_lines.append("\n## Later Heading\n\nmore text\n")
    en = '---\ndescription: "desc"\n---\n\n' + "".join(body_lines)

    out = pipeline.assemble(en, "", "", FakeBackend(), max_lines=50)
    _, zh_body = frontmatter.split(out)
    headings = anchors.headings(zh_body)
    assert len(headings) == 2
    assert anchors.existing_anchor(headings[1][1]) == "later-heading"
    assert "{#later-heading}" in out


def test_assemble_carries_anchor_across_inserted_english_heading():
    """D10 regression: 上游在舊標題之前插入一個新標題，anchor 仍須沿用身分
    比對（by slug），而不是位移到錯誤的標題上。"""
    prev_en = (
        '---\ndescription: "desc"\n---\n\n# Vector\n\nold\n\n## Syntax\n\nold text\n'
    )
    prev_zh = (
        '---\ndescription: "desc"\n---\n\n# 向量 {#vector}\n\n舊\n\n## 語法 {#custom-syntax}\n\n舊文字\n'
    )
    en = (
        '---\ndescription: "desc"\n---\n\n# Vector\n\nnew\n\n'
        '## Inserted\n\ninserted text\n\n## Syntax\n\nnew text\n'
    )
    out = pipeline.assemble(en, prev_zh, prev_en, FakeBackend())
    _, zh_body = frontmatter.split(out)
    headings = anchors.headings(zh_body)
    assert len(headings) == 3
    # Syntax 現在是第三個標題（index 2），anchor 必須仍是 custom-syntax。
    assert anchors.existing_anchor(headings[2][1]) == "custom-syntax"
    assert "{#vector}" in out


def test_assemble_without_prev_en_carries_nothing():
    """有 prev_zh 但沒有 prev_en：anchors._identity_carry 不得退回位置配對，
    衍生 anchor 一律來自英文標題本身。用 anchors 直接驗證這一點（inject_report
    的 tier-1/2/3 分層邏輯），不透過 validate 的 gate 6。"""
    _, en_body = frontmatter.split(EN)
    _, prev_zh_body = frontmatter.split(PREV_ZH)
    zh_body = pipeline.translate_body(EN, FakeBackend())
    _, zh_body = frontmatter.split(zh_body)
    injected, notes = anchors.inject_report(zh_body, en_body, prev_zh_body, "")
    injected_headings = anchors.headings(injected)
    ids = [anchors.existing_anchor(t) for _, t in injected_headings]
    assert "custom-syntax" not in ids  # 不沿用舊中文檔的自訂 id
    assert ids[1] == "syntax"  # 衍生自英文標題本身，不是位置配對
    assert any("not carried forward" in n for n in notes)


def test_assemble_succeeds_when_prev_en_missing_carrying_no_old_anchors():
    """Deadlock fix at the assemble level: 有 prev_zh、沒有 prev_en 時，
    inject() 正確地拒絕沿用任何既有 anchor（避免 D10 的位置配對 bug），
    gate 6 對同樣缺席的 prev_en 棄權，不再把 inject 的保守選擇回報成
    「anchor 消失」的錯誤。輸出必須成功寫出，且不含 PREV_ZH 裡的舊 id
    （custom-syntax 是自訂 id，重新衍生絕不可能巧合算出同一個字串，
    是比 vector/syntax 更乾淨的「沒有沿用」證據）。"""
    out = pipeline.assemble(EN, PREV_ZH, "", FakeBackend())
    _, zh_body = frontmatter.split(out)
    ids = {
        aid for _, t in anchors.headings(zh_body)
        if (aid := anchors.existing_anchor(t))
    }
    assert "custom-syntax" not in ids  # 舊自訂 id，沒有 prev_en 就不可能沿用得到
    assert ids == {"vector", "syntax"}  # 兩者皆為對 en 標題文字重新衍生的結果


def test_run_routes_sidebar_through_sidebar_module_not_markdown():
    """sidebar.yml 不得走 markdown 路徑，否則整份 YAML 會被當內文翻譯（Task 14）。
    Task 11 曾讓這條路直接失敗；sidebar.py 落地後這裡改為驗證它成功且產出
    合法 YAML，結構與 english-main 的 skeleton 相同。"""
    import yaml

    from scripts.zh_tw import sidebar as sidebar_mod

    path = manifest.SIDEBAR_FILES[0]
    ok, failed = pipeline.run([path], "fake", apply=False)
    assert failed == {}
    assert ok == 1

    en = pipeline._show("english-main", path)
    prev = pipeline._show("HEAD", path) or ""
    out = sidebar_mod.translate(en, prev, pipeline.base.get("fake"))
    assert sidebar_mod.skeleton(out) == sidebar_mod.skeleton(en)
    assert yaml.safe_load(out) is not None


def test_run_routes_sidebar_to_sidebar_module(monkeypatch, tmp_path):
    """sidebar.yml 不得走 markdown 路徑，否則整份 YAML 會被當內文翻譯。"""
    called = []
    monkeypatch.setattr(
        pipeline.sidebar, "translate",
        lambda en, prev, backend: called.append("sidebar") or "ok\n",
    )
    monkeypatch.setattr(pipeline, "_show", lambda ref, path: "bookSidebar:\n  - label: X\n")
    ok, failed = pipeline.run(["book/sidebar.yml"], "fake", apply=False)
    assert called == ["sidebar"]
    assert ok == 1 and failed == {}


def test_run_dry_run_writes_nothing_and_leaves_manifest_untouched(tmp_path, monkeypatch):
    manifest_before = manifest.MANIFEST_PATH.read_text(encoding="utf-8")
    ok, failed = pipeline.run(["book/404.md"], "fake", apply=False)
    manifest_after = manifest.MANIFEST_PATH.read_text(encoding="utf-8")
    assert manifest_before == manifest_after
    assert ok + len(failed) == 1


def test_run_validation_error_on_one_file_does_not_stop_others():
    paths = ["book/404.md", "nonexistent/does-not-exist.md"]
    ok, failed = pipeline.run(paths, "fake", apply=False)
    assert "nonexistent/does-not-exist.md" in failed
    assert ok == 1


def test_tier_a_when_only_body_forbidden_words():
    """結構一致、內文帶違禁詞「循環」：內文品質缺陷不在 validate 第 1、2
    條，不構成降級。合成資料——原活檔 fixture（reference/constants.md 的
    legacy 債務）已在債務全清後永久失去前提。"""
    en = '---\ndescription: "Constants."\n---\n\n# Constants\n\nText.\n'
    zh = '---\ndescription: "常數。"\n---\n\n# 常數 {#constants}\n\n這段有循環。\n'
    assert validate.check_structure(zh, en) == []
    assert any("違禁詞" in e for e in validate.check_file(zh, en))


def test_rebuild_frontmatter_only_ignores_legacy_body_defects():
    """dual-review blocker：A 層檔帶 legacy body 違禁詞時，改前會 hard-fail
    且無任何自動修復路徑（body 不重譯、tier 又不降級）。body 既有債務
    不當寫檔否決（比照 gate 9 先例），留待人工/後續 PR。"""
    en = '---\ndescription: "Constants."\n---\n\n# Constants\n\nText.\n'
    zh = '---\ndescription: "常數。"\n---\n\n# 常數 {#constants}\n\n這段有循環。\n'
    out = pipeline.rebuild_frontmatter_only(en, zh, FakeBackend())
    _, body = frontmatter.split(out)
    assert "循環" in body  # body 原封不動，含缺陷


def test_rebuild_frontmatter_only_enforces_glossary_on_values():
    """backend 新翻的 frontmatter 值帶違禁詞 → 決定性修正，不是炸掉
    （loops.md 的 title 就是「循環」，真實 backend 高機率重現）。"""

    class LoopyBackend:
        def translate(self, text, *, kind="markdown"):
            return "循環"

    en = '---\ndescription: "Loops."\n---\n\n# Loops\n\nText.\n'
    zh = '---\ndescription: "舊。"\n---\n\n# 迴圈 {#loops}\n\n內文。\n'
    out = pipeline.rebuild_frontmatter_only(en, zh, LoopyBackend())
    meta, _ = frontmatter.split(out)
    assert meta["description"] == "迴圈"


def test_rebuild_frontmatter_only_rejects_simplified_in_values():
    """簡體字沒有決定性修法（OpenCC 例外表風險），值裡出現就必須炸掉。"""

    class SimplifiedBackend:
        def translate(self, text, *, kind="markdown"):
            return "这是简体"

    en = '---\ndescription: "X."\n---\n\n# X\n\nText.\n'
    zh = '---\ndescription: "舊。"\n---\n\n# 某 {#x}\n\n內文。\n'
    with pytest.raises(validate.ValidationError):
        pipeline.rebuild_frontmatter_only(en, zh, SimplifiedBackend())


def test_translate_body_enforces_glossary_on_values():
    """B 路徑同款漏洞：值翻譯沒過 glossary.enforce，check_file 補上值掃描後
    會變成 B 路徑的 deadlock —— enforce 與 gate 必須同進退。"""

    class LoopyBackend:
        def translate(self, text, *, kind="markdown"):
            if kind == "text":
                return "循環"
            return "中文內文。\n"

    en = '---\ndescription: "Loops."\n---\n\nBody.\n'
    out = pipeline.translate_body(en, LoopyBackend())
    meta, _ = frontmatter.split(out)
    assert meta["description"] == "迴圈"


def test_run_a_tier_file_with_legacy_body_defects_succeeds():
    """組合層驗證（lessons L7）：constants.md 結構一致、body 帶「循環」，
    整條 A 路徑（tier → rebuild → gate）必須產出成功，不是 failed。"""
    assert pipeline.tier("reference/constants.md") == "A"  # 釘住走的是 A 路徑
    ok, failed = pipeline.run(["reference/constants.md"], "fake")
    assert failed == {}
    assert ok == 1


# --- A 層 frontmatter 沿用優先於重算（與 anchor carry-forward 同原則） ---
#
# 實測（2026-07-11 第一次 apply）：47 檔中 53 個欄位「舊值已是中文、英文
# 原文完全沒變」卻被整批重翻，損失既有審定術語（友元 (Friends) → 朋友）。


class _ExplodingBackend:
    def translate(self, text, *, kind="markdown"):
        raise AssertionError(f"en 未變的欄位不得重翻: {text!r}")


def test_rebuild_frontmatter_carries_translation_when_en_unchanged():
    en = '---\ndescription: "Same."\n---\n\n# T\n\nText.\n'
    zh = '---\ndescription: "既有翻譯。"\n---\n\n# 標題 {#t}\n\n內文。\n'
    out = pipeline.rebuild_frontmatter_only(en, zh, _ExplodingBackend(), prev_en_text=en)
    meta, _ = frontmatter.split(out)
    assert meta["description"] == "既有翻譯。"


def test_rebuild_frontmatter_retranslates_when_en_changed():
    class Backend:
        def translate(self, text, *, kind="markdown"):
            return "新翻譯。"

    prev_en = '---\ndescription: "Old."\n---\n\n# T\n\nText.\n'
    en = '---\ndescription: "New."\n---\n\n# T\n\nText.\n'
    zh = '---\ndescription: "舊翻譯。"\n---\n\n# 標題 {#t}\n\n內文。\n'
    out = pipeline.rebuild_frontmatter_only(en, zh, Backend(), prev_en_text=prev_en)
    meta, _ = frontmatter.split(out)
    assert meta["description"] == "新翻譯。"


def test_rebuild_frontmatter_translates_when_prev_value_untranslated():
    class Backend:
        def translate(self, text, *, kind="markdown"):
            return "補上翻譯。"

    en = '---\ndescription: "Same."\n---\n\n# T\n\nText.\n'
    zh = '---\ndescription: "Same."\n---\n\n# 標題 {#t}\n\n內文。\n'  # 未翻，沒有可沿用的
    out = pipeline.rebuild_frontmatter_only(en, zh, Backend(), prev_en_text=en)
    meta, _ = frontmatter.split(out)
    assert meta["description"] == "補上翻譯。"


def test_rebuild_frontmatter_enforces_glossary_on_carried_value():
    """沿用不是免檢：舊值帶違禁詞（5 檔實測）沿用時決定性修正。"""
    en = '---\ndescription: "Loops."\n---\n\n# T\n\nText.\n'
    zh = '---\ndescription: "循環概念。"\n---\n\n# 標題 {#t}\n\n內文。\n'
    out = pipeline.rebuild_frontmatter_only(en, zh, _ExplodingBackend(), prev_en_text=en)
    meta, _ = frontmatter.split(out)
    assert meta["description"] == "迴圈概念。"


def test_rebuild_frontmatter_retranslates_when_carried_value_has_simplified():
    """簡體無決定性修法：舊值帶簡體字就退回重翻，不沿用。"""

    class Backend:
        def translate(self, text, *, kind="markdown"):
            return "乾淨的新翻譯。"

    en = '---\ndescription: "X."\n---\n\n# T\n\nText.\n'
    zh = '---\ndescription: "这是旧的。"\n---\n\n# 標題 {#t}\n\n內文。\n'
    out = pipeline.rebuild_frontmatter_only(en, zh, Backend(), prev_en_text=en)
    meta, _ = frontmatter.split(out)
    assert meta["description"] == "乾淨的新翻譯。"


def test_delta_lines_zero_for_identical_blobs():
    """manifest heal 之後 old_sha == new_sha；`git diff --numstat` 對同一
    blob 輸出空字串，原本走進 fail-closed 哨兵（10000）→ 已 heal 的檔案
    全被誤判 B。同 blob 的 delta 就是 0，不需要問 git。"""
    sha = subprocess.run(
        ["git", "rev-parse", "english-main:reference/constants.md"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert pipeline._delta_lines(sha, sha) == 0


# --- gate 9 的修復 pass：決定性補後綴 / 單標題重譯（enforce 與 gate 同進退） ---


def test_repair_headings_appends_missing_suffix_without_backend():
    class ExplodingBackend2:
        def translate(self, text, *, kind="markdown"):
            raise AssertionError("已翻譯只缺後綴的標題不得動用 backend")

    zh = "# 中文標題\n\n內文。\n"
    en = "# Title\n\nText.\n"
    out = pipeline._repair_headings(zh, en, ExplodingBackend2())
    assert "# 中文標題 (Title)\n" in out


def test_repair_headings_strips_duplicated_trailing_parens():
    """實測失效：「標籤與發布 (Tags and Releases) (Git)」直接補後綴會疊床架屋。"""
    zh = "## 標籤與發布 (Tags and Releases) (Git)\n"
    en = "## Tags and Releases (Git)\n"
    out = pipeline._repair_headings(zh, en, FakeBackend())
    assert out.splitlines()[0] == "## 標籤與發布 (Tags and Releases (Git))"


def test_repair_headings_retranslates_verbatim_heading():
    class HeadingBackend:
        def translate(self, text, *, kind="markdown"):
            assert kind == "heading"
            return f"VecSet 集合 ({text})"

    zh = "## VecSet\n\n內文。\n"
    en = "## VecSet\n\nText.\n"
    out = pipeline._repair_headings(zh, en, HeadingBackend())
    assert out.splitlines()[0] == "## VecSet 集合 (VecSet)"


def test_repair_headings_leaves_exempt_and_count_mismatch_alone():
    class ExplodingBackend3:
        def translate(self, text, *, kind="markdown"):
            raise AssertionError("豁免標題不得動用 backend")

    assert pipeline._repair_headings("# BCS\n", "# BCS\n", ExplodingBackend3()) == "# BCS\n"
    # 數量不符：交給 gate 1，不修
    zh = "# 一\n"
    en = "# One\n\n## Two\n"
    assert pipeline._repair_headings(zh, en, ExplodingBackend3()) == zh


def test_assemble_repairs_suffix_dropping_backend():
    """gate 9 擋的「掉後綴」是決定性可修：修復 pass 補上，assemble 成功。
    （原 test_assemble_raises_when_backend_drops_heading_suffix 的失效輸入，
    現在的正確結局是被修好而不是炸掉。）"""
    en = '---\ndescription: "d"\n---\n\n# One\n\n## Two\n'

    class SuffixDroppingBackend2:
        def translate(self, text, *, kind="markdown"):
            if kind == "text":
                return "中文"
            if kind == "heading":
                return f"中文 ({text})"
            return "# 一 (One)\n\n## 二\n"

    out = pipeline.assemble(en, "", "", SuffixDroppingBackend2())
    _, body = frontmatter.split(out)
    assert "## 二 (Two)" in body


def test_assemble_raises_when_heading_unrepairable():
    """修復 pass 修不動（重譯仍 verbatim）時 gate 9 仍須擋下——修復不是放寬。"""
    en = '---\ndescription: "d"\n---\n\n# Scopes\n'

    class StubbornBackend:
        def translate(self, text, *, kind="markdown"):
            if kind == "text":
                return "中文"
            if kind == "heading":
                return text  # 重譯也 verbatim
            return "# Scopes\n"

    with pytest.raises(validate.ValidationError, match="未翻譯"):
        pipeline.assemble(en, "", "", StubbornBackend())


def test_repair_headings_strips_anchor_suffix_like_the_judge():
    """review F1：headings() 回傳的文字含 {#anchor}，判定（heading_suffix_error）
    有剝、修復沒剝 → 前提漂移，anchor 字面量會被嵌進標題中段。修復必須與
    判定同一前處理；backend 幻覺出的 anchor 在此丟棄（inject 才是 anchor
    的唯一權威來源）。"""
    zh = "## 迴圈 {#loops}\n"
    en = "## Loops\n"
    out = pipeline._repair_headings(zh, en, FakeBackend())
    assert out.splitlines()[0] == "## 迴圈 (Loops)"

    zh2 = "## 迴圈\n"
    en2 = "## Loops {#loops}\n"
    out2 = pipeline._repair_headings(zh2, en2, FakeBackend())
    assert out2.splitlines()[0] == "## 迴圈 (Loops)"


def test_repair_headings_skips_nested_headings():
    """review F2：blockquote/list 容器內的標題整行替換會吃掉容器前綴，
    讓 inject 的 NestedHeading fail-closed 失效。巢狀標題不修，交給 inject 炸。"""
    zh = "> ## 迴圈\n"
    en = "## Loops\n"
    assert pipeline._repair_headings(zh, en, FakeBackend()) == zh


def test_run_passes_max_lines_to_assemble(monkeypatch):
    """--max-lines：長檔掉標題時縮小 chunk 的逃生口（PR 3 實測 sonnet 對
    250 行 chunk 決定性丟 4/53 個標題）。"""
    captured = {}

    def fake_assemble(en, prev, prev_en, backend, max_lines=pipeline.CHUNK_MAX_LINES):
        captured["max_lines"] = max_lines
        return en

    monkeypatch.setattr(pipeline, "assemble", fake_assemble)
    monkeypatch.setattr(pipeline, "tier", lambda *a, **k: "B")
    pipeline.run(["reference/constants.md"], "fake", max_lines=60)
    assert captured["max_lines"] == 60


def test_translate_body_retries_chunk_that_drops_headings():
    """PR 3 診斷：sonnet 對長檔穩定吞小節標題（variables.md 21→16，換
    chunk 尺寸與整檔重跑都救不了）。chunk 級標題序列檢查 + 重試把失效
    定位到小範圍 —— 單一 chunk 重試便宜且成功率遠高於整檔賭運氣。"""
    calls = {"n": 0}

    class FlakyBackend:
        def translate(self, text, *, kind="markdown"):
            if kind == "text":
                return "中文"
            calls["n"] += 1
            if calls["n"] == 1:
                return "# 一 (One)\n\n內文。\n"  # 吞掉 ## Two
            return "# 一 (One)\n\n內文。\n\n## 二 (Two)\n\n更多。\n"

    en = '---\ndescription: "d"\n---\n\n# One\n\nbody\n\n## Two\n\nmore\n'
    out = pipeline.translate_body(en, FlakyBackend())
    _, body = frontmatter.split(out)
    assert [lv for lv, _ in anchors.headings(body)] == [1, 2]
    assert calls["n"] == 2  # 第一次不合格，重試一次成功


def test_translate_body_keeps_last_attempt_when_retries_exhausted():
    """重試耗盡仍不符 → 保留最後一次輸出交給 gate 1 整檔擋下（fail-closed
    不變，重試只是加自動修復路徑，不是放寬）。"""
    calls = {"n": 0}

    class StubbornBackend:
        def translate(self, text, *, kind="markdown"):
            if kind == "text":
                return "中文"
            calls["n"] += 1
            return "# 一 (One)\n"  # 永遠吞掉 ## Two

    en = '---\ndescription: "d"\n---\n\n# One\n\nbody\n\n## Two\n\nmore\n'
    out = pipeline.translate_body(en, StubbornBackend())
    _, body = frontmatter.split(out)
    assert len(anchors.headings(body)) == 1  # 依然殘缺 —— gate 1 會擋
    assert calls["n"] == pipeline.CHUNK_RETRIES


def test_translate_chunk_retries_on_fence_mismatch():
    """L7 組合缺陷實錄：chunk N 輸出掉了收尾 ```，自身標題檢查照過，join
    後 chunk N+1 的標題全被吞進未閉合 fence（variables.md 21→19，單獨翻
    每個 chunk 都正常）。chunk 級檢查必須同時驗 gate 1+2 兩個維度。"""
    calls = {"n": 0}

    class FenceDroppingBackend:
        def translate(self, text, *, kind="markdown"):
            calls["n"] += 1
            if calls["n"] == 1:
                return "# 一 (One)\n\n```move\nlet x = 1;\n"  # 掉了收尾 ```
            return "# 一 (One)\n\n```move\nlet x = 1;\n```\n"

    en = "# One\n\n```move\nlet x = 1;\n```\n"
    out = pipeline._translate_chunk(en, FenceDroppingBackend())
    assert calls["n"] == 2
    assert anchors.fence_lines(out) == anchors.fence_lines(en)


# --- fence 註解修復 pass：批次翻譯 code 內的英文散文註解 ---
#
# PR 3 實測：sonnet 對 fence 註解 186/213 未翻（語料慣例是翻，抽樣舊檔
# 0/6、0/6、3/5 已翻）。與標題修復同理：LLM 系統性忽略的指令，用專用
# 小呼叫補—— 批次編號清單一檔一呼叫（沿用 sidebar 的成熟模式）。


class _CommentBackend:
    def __init__(self):
        self.calls = []

    def translate(self, text, *, kind="markdown"):
        self.calls.append(kind)
        import re as _re
        out = []
        for line in text.splitlines():
            m = _re.match(r"^\s*(\d+)[.)]\s+(.+?)\s*$", line)
            if m:
                out.append(f"{m.group(1)}. 中文註解（{m.group(2)}）")
        return "\n".join(out)


def test_repair_fence_comments_translates_english_prose():
    zh = "# 一 (One)\n\n```move\n// create a new instance\nlet x = 1; // and assign it\n```\n"
    out = pipeline._repair_fence_comments(zh, _CommentBackend())
    assert "// 中文註解（create a new instance）" in out
    assert "let x = 1;" in out  # code 本體不動
    assert anchors.fence_lines(out) == anchors.fence_lines(zh)


def test_repair_fence_comments_skips_directives_and_translated():
    b = _CommentBackend()
    zh = (
        "```move\n"
        "// ANCHOR: main\n"
        "// highlight-start\n"
        "// 已翻好的註解\n"
        "```\n"
    )
    out = pipeline._repair_fence_comments(zh, b)
    assert out == zh
    assert b.calls == []  # 沒東西要翻就不呼叫 backend


def test_repair_fence_comments_ignores_prose_outside_code():
    b = _CommentBackend()
    zh = "散文提到 // this is not code 的寫法。\n"
    assert pipeline._repair_fence_comments(zh, b) == zh
    assert b.calls == []


def test_repair_fence_comments_keeps_original_when_reply_lacks_cjk():
    class BadBackend:
        def translate(self, text, *, kind="markdown"):
            import re as _re
            return "\n".join(
                f"{m.group(1)}. still english"
                for line in text.splitlines()
                if (m := _re.match(r"^\s*(\d+)[.)]\s+(.+?)\s*$", line))
            )

    zh = "```move\n// create a new instance\n```\n"
    out = pipeline._repair_fence_comments(zh, BadBackend())
    assert "// create a new instance" in out  # 壞回覆 → 保留原文


def test_repair_fence_comments_skips_move_attributes():
    """`#[test] // ...` 的 `#` 開頭是 Move 屬性不是註解 —— 送去翻譯若回覆
    含 CJK 會直接把屬性行改壞（編譯層級的損毀）。屬性行整行跳過；其行內
    // 註解的翻譯由 chunk 翻譯本身負責。"""
    b = _CommentBackend()
    zh = "```move\n#[test] // will fail to compile\n#[test_only]\n```\n"
    assert pipeline._repair_fence_comments(zh, b) == zh
    assert b.calls == []


def test_translate_chunk_treats_hallucinated_frontmatter_as_failed_attempt():
    """review F1：backend 幻覺出 YAML frontmatter 時，_require_body 的
    FrontmatterPassedIn 不該逃出重試迴圈炸掉整檔 —— 這正是重試該吸收的
    垃圾輸出。"""
    calls = {"n": 0}

    class HallucinatingBackend:
        def translate(self, text, *, kind="markdown"):
            calls["n"] += 1
            if calls["n"] == 1:
                return "---\ntitle: 變數\n---\n\n# 一 (One)\n"
            return "# 一 (One)\n"

    out = pipeline._translate_chunk("# One\n", HallucinatingBackend())
    assert calls["n"] == 2
    assert out == "# 一 (One)\n"


def test_repair_fence_comments_bails_on_reply_numbering_drift():
    """review F2：backend 合併重複行重新編號時，第 i 條會拿到第 i+1 條的
    譯文 —— fence 內的靜默內容損毀，所有 gate 都看不到。編號集合不完整
    就整個 pass 放棄（fail-open 到 no-op）。"""

    class DriftingBackend:
        def translate(self, text, *, kind="markdown"):
            return "1. 中文一\n3. 中文三"  # 缺 2：編號集合不完整

    zh = "```move\n// alpha comment\n// beta comment\n// gamma comment\n```\n"
    assert pipeline._repair_fence_comments(zh, DriftingBackend()) == zh


def test_repair_fence_comments_accepts_cjk_numbering_without_space():
    """review F4：中文模型常輸出「1.譯文」無空格 —— 在 F2 的完整性守衛
    之下放寬分隔符是安全的。"""

    class NoSpaceBackend:
        def translate(self, text, *, kind="markdown"):
            return "1.建立新實例"

    zh = "```move\n// create a new instance\n```\n"
    out = pipeline._repair_fence_comments(zh, NoSpaceBackend())
    assert "// 建立新實例" in out


def test_repair_fence_comments_rejects_simplified_reply():
    """review F5：本 pass 大規模把 CJK 寫進 code 行，而 gate 8 遮蔽 code
    —— 簡體回覆必須在這裡擋，否則直通發佈輸出。"""

    class SimplifiedReplyBackend:
        def translate(self, text, *, kind="markdown"):
            return "1. 创建新实例"

    zh = "```move\n// create a new instance\n```\n"
    out = pipeline._repair_fence_comments(zh, SimplifiedReplyBackend())
    assert "// create a new instance" in out  # 保留原文


def test_repair_headings_retries_llm_path():
    """單標題重譯間歇性 verbatim/垃圾（實測 'Abort' 第一次回幻覺文字、
    第二次即正確）——LLM 路徑比照 chunk 重試就地驗證重試。"""
    calls = {"n": 0}

    class FlakyHeadingBackend:
        def translate(self, text, *, kind="markdown"):
            assert kind == "heading"
            calls["n"] += 1
            if calls["n"] == 1:
                return "執行結果：亂七八糟的幻覺輸出"
            return f"中止 ({text})"

    out = pipeline._repair_headings("## Abort\n", "## Abort\n", FlakyHeadingBackend())
    assert out.splitlines()[0] == "## 中止 (Abort)"
    assert calls["n"] == 2


def test_run_apply_saves_only_own_updates(tmp_path, monkeypatch):
    """PR 5 實測的 manifest 競態：兩個 apply 行程平行跑，後結束者用啟動時
    載入的舊快照整檔覆寫，把先結束者剛記錄的 provenance 洗掉（2 檔被誤判
    stale，重跑會覆蓋已 merge 的好譯文）。run() 必須在 save 前重新載入
    on-disk 狀態、只套用自己處理過的路徑。"""
    import json

    from scripts.zh_tw import manifest as mf

    tmp_manifest = tmp_path / "translation-manifest.json"
    tmp_manifest.write_text(json.dumps({"other/path.md": "aaa"}), encoding="utf-8")
    monkeypatch.setattr(mf, "MANIFEST_PATH", tmp_manifest)

    m = mf.load()  # 模擬本行程啟動時載入
    # 模擬另一個行程在我們執行期間寫入了新紀錄
    tmp_manifest.write_text(
        json.dumps({"other/path.md": "aaa", "their/new.md": "bbb"}), encoding="utf-8"
    )
    # 本行程記錄自己的檔案後 save
    m["mine/file.md"] = "ccc"
    pipeline._save_manifest_updates(m, {"mine/file.md"})

    final = json.loads(tmp_manifest.read_text(encoding="utf-8"))
    assert final == {
        "other/path.md": "aaa",
        "their/new.md": "bbb",  # 別的行程的紀錄不得被洗掉
        "mine/file.md": "ccc",
    }


def test_repair_inpage_links_restores_english_slugs():
    """兩個 PR 各自出現（visibility.md、bcs.md×2）：模型把頁內連結的
    slug 翻譯成中文（#格式-format），目標 anchor 卻是英文 slug（anchor
    一律衍生自英文標題）。決定性修法：與英文原文的頁內連結按順序配對、
    取回英文 slug —— 順序配對的前提是兩邊頁內連結數一致，不一致就不修
    （交給 check_repo 顯形）。"""
    zh = "# 標題 (T)\n\n見[格式](#格式-format)與[解碼](#解碼-decoding)。\n"
    en = "# T\n\nSee [Format](#format) and [Decoding](#decoding).\n"
    out = pipeline._repair_inpage_links(zh, en)
    assert "(#format)" in out and "(#decoding)" in out
    assert "#格式" not in out


def test_repair_inpage_links_skips_on_count_mismatch_and_code():
    zh = "```\n[x](#不要動)\n```\n\n[a](#甲)\n"
    en = "```\n[x](#keep)\n```\n\n[a](#a) 與 [b](#b)\n"
    out = pipeline._repair_inpage_links(zh, en)
    assert out == zh  # 頁內連結數不一致（1 vs 2）→ 不修；code 內不算連結


# --- run() 自報成果：進展判定不再由 workflow 從檔案系統推論 ---
#
# 為什麼要有這個輸出：translate workflow 的「本輪有沒有進展」判定連續三輪
# review 各出一個 blocker，全部同源 —— 它一直在拿代理量推論真實性質：
#   輪一 `git diff --cached` 非空 → prettier 對既有髒檔的純格式改動能撐起假 diff
#   輪二 同上 → `_save_manifest_updates` 無條件 save 的正規化噪音也能
#   輪三 「工作區有檔案變動」 → 反方向漏掉本測試釘住的這個情境
# 三次的失效形式都是「job 全綠但管線靜默停擺」。真正的原始量從頭到尾是
# run() 自己手上的 ok 與 touched，manifest 與工作區 diff 都只是它們的影子。
# 這個輸出讓 workflow 直接讀本體，把推論整段刪掉（lessons L2）。


def _byte_identical_apply(tmp_path, monkeypatch, result_path=None):
    from scripts.zh_tw import manifest as mf

    monkeypatch.chdir(tmp_path)
    (tmp_path / "book").mkdir()
    same = "---\ntitle: 標題 (T)\n---\n\n內文。\n"
    (tmp_path / "book" / "x.md").write_text(same, encoding="utf-8")

    monkeypatch.setattr(mf, "MANIFEST_PATH", tmp_path / "m.json")
    monkeypatch.setattr(mf, "blob_sha", lambda ref, path: "newsha")
    monkeypatch.setattr(pipeline, "_show", lambda ref, path: same)
    monkeypatch.setattr(pipeline, "tier", lambda *a, **k: "B")
    monkeypatch.setattr(pipeline, "assemble", lambda *a, **k: same)

    return pipeline.run(
        ["book/x.md"], "fake", apply=True, result_path=result_path
    ), same


def test_run_reports_success_even_when_output_is_byte_identical(tmp_path, monkeypatch):
    """tier A 沿用 HEAD 的中文 body + carry-forward frontmatter 時，產出可以與
    磁碟 byte-identical。此時工作區零 diff，但 manifest 的 provenance 更新是
    本輪唯一且真實的成果 —— stale 判定只看英文 blob SHA（manifest.py:51）。
    run() 的回報必須說「成功 1、touched 含該檔」，不能跟著工作區一起說零。
    """
    import json

    result = tmp_path / "result.jsonl"
    (ok, failed), same = _byte_identical_apply(tmp_path, monkeypatch, str(result))

    assert (ok, failed) == (1, {})
    # 前提斷言（防 vacuous）：檔案內容確實沒變，工作區看不出任何進展。
    assert (tmp_path / "book" / "x.md").read_text(encoding="utf-8") == same

    line = json.loads(result.read_text(encoding="utf-8").strip())
    assert line["ok"] == 1
    # touched 才是消費端（CI）該讀的：它是「落盤了幾檔」，ok 是「產出了幾份
    # 譯文字串」，`ok += 1` 在 `if apply:` 之外，dry-run 也會累加。
    assert line["touched"] == ["book/x.md"]
    assert line["failed"] == {}


def test_run_result_is_appended_not_overwritten(tmp_path, monkeypatch):
    """xargs 在清單超過 ARG_MAX 時會把同一批拆成多次呼叫。覆寫式輸出會讓
    最後一批洗掉前面幾批的成果，workflow 讀到的 ok 數就少算 —— 少算到 0
    就是「本輪零成功」誤判轉紅、已翻好的檔全丟。BATCH_SIZE=3 現在碰不到
    ARG_MAX，但這正是「靠外部不變式撐正確性」的老毛病，不留。
    """
    import json

    result = tmp_path / "result.jsonl"
    result.write_text(
        '{"ok": 2, "touched": ["book/old.md", "book/old2.md"], "failed": {}}\n',
        encoding="utf-8",
    )
    _byte_identical_apply(tmp_path, monkeypatch, str(result))

    lines = [json.loads(x) for x in result.read_text(encoding="utf-8").splitlines() if x]
    assert [len(l["touched"]) for l in lines] == [2, 1]
    assert sum(len(l["touched"]) for l in lines) == 3


def test_run_without_result_path_writes_nothing(tmp_path, monkeypatch):
    """不給 result_path 就不該生出檔案（dry-run 與既有呼叫端不受影響）。"""
    _byte_identical_apply(tmp_path, monkeypatch, None)
    assert list(tmp_path.glob("*.jsonl")) == []


def test_dry_run_reports_ok_but_empty_touched(tmp_path, monkeypatch):
    """釘住 ok 與 touched 的語意差：dry-run 產出了譯文（ok=1）但什麼都沒落盤
    （touched 空）。CI 判「本輪有沒有進展」必須讀 touched —— 讀 ok 的話，
    日後誰加一個不帶 --apply 的冒煙步驟，就會判成「有進展」而 index 是空的，
    `git commit` 以 nothing to commit 在 set -e 下轉紅。
    """
    import json

    from scripts.zh_tw import manifest as mf

    monkeypatch.chdir(tmp_path)
    (tmp_path / "book").mkdir()
    same = "---\ntitle: 標題 (T)\n---\n\n內文。\n"
    (tmp_path / "book" / "x.md").write_text(same, encoding="utf-8")
    monkeypatch.setattr(mf, "MANIFEST_PATH", tmp_path / "m.json")
    monkeypatch.setattr(pipeline, "_show", lambda ref, path: same)
    monkeypatch.setattr(pipeline, "tier", lambda *a, **k: "B")
    monkeypatch.setattr(pipeline, "assemble", lambda *a, **k: same)

    result = tmp_path / "result.jsonl"
    ok, failed = pipeline.run(
        ["book/x.md"], "fake", apply=False, result_path=str(result)
    )

    assert (ok, failed) == (1, {})
    line = json.loads(result.read_text(encoding="utf-8").strip())
    assert line["ok"] == 1
    assert line["touched"] == []


# --- 底線強調在 CJK 相鄰時不會渲染（決定性修復 pass）---
#
# PR #22 實測：backend 從 `*文字*` 改用 `_文字_`，3 個檔的 5 處強調全部
# 不再渲染（改動前後整檔跑 commonmark，<em> 由 5 變 0）。CommonMark 規定
# `_` 不能在「詞內」開合，而 CJK 算 word char —— `進行_升級_：`、
# `包括_所有權的變更_；`、`_簽署_交易` 全中。八道 gate 全是結構/術語檢查、
# prettier 不管語意，所以這種「產出合法 Markdown、但渲染結果少了東西」的
# 回歸沒有任何東西攔得住，只有人眼看得到。


def test_repair_cjk_underscore_emphasis_rewrites_to_asterisk():
    """CJK 相鄰的 `_..._` 改寫成 `*...*`，渲染結果才會有 <em>。"""
    import commonmark

    zh = "但套件可以進行_升級 (upgraded)_：升級會在新地址發布。\n"
    assert "<em>" not in commonmark.commonmark(zh)  # 前提：修之前真的壞掉

    out = pipeline._repair_cjk_emphasis(zh)
    assert out == "但套件可以進行*升級 (upgraded)*：升級會在新地址發布。\n"
    assert "<em>升級 (upgraded)</em>" in commonmark.commonmark(out)


def test_repair_cjk_underscore_emphasis_leaves_working_emphasis_alone():
    """本來就渲染得出來的不要動 —— 修復 pass 不該製造無謂 diff。
    `_` 兩側都是空白/標點時是合法的強調，ASCII 詞也沒有這個問題。"""
    for text in [
        "這是 _emphasis_ 測試。\n",
        "前面有空白 _強調_ 後面也有。\n",
        "*星號本來就對*，不要動。\n",
    ]:
        assert pipeline._repair_cjk_emphasis(text) == text


def test_repair_cjk_emphasis_never_touches_code():
    """snake_case 識別字與 code span/fence 內的底線絕對不能動 ——
    `object_id`、`std::string::String` 這類東西被改成星號就是編譯層級的破壞。"""
    cases = [
        "呼叫 `sui::coin::from_balance` 與 `tx_context` 兩個東西。\n",
        "```move\nlet _x = foo_bar(_y);\n```\n",
        "變數 `some_var_name` 不該被動到。\n",
        "行內 `a_b_c` 與中文相鄰的_強調_混在一起。\n",
    ]
    for text in cases:
        out = pipeline._repair_cjk_emphasis(text)
        # code 內容逐字不變
        import re

        assert re.findall(r"`[^`]*`|```.*?```", out, flags=re.S) == re.findall(
            r"`[^`]*`|```.*?```", text, flags=re.S
        ), text


def test_repair_cjk_emphasis_never_touches_urls_and_identifiers():
    """真實語料的假陽性：`Lambda_(computer_function)` 這種 URL、
    `_failureabort_` 這種識別字碎片，底線對看起來就是強調。第一版修復 pass
    對全語料掃出 192 處「失效強調」，全是這類 —— 把它們改成星號就是內容
    破壞。判準加上「強調內容必須含 CJK」：中文段落裡的強調必然含中文，
    URL 與識別字不會（lessons L2：觀測量要等於宣稱保護的性質）。"""
    cases = [
        "巨集 (macro) 見 [Lambda](https://en.wikipedia.org/wiki/Lambda_(computer_function))。\n",
        "測試狀態 _failureabort_ 與 _status-u64_ 是識別字碎片。\n",
    ]
    for text in cases:
        assert pipeline._repair_cjk_emphasis(text) == text, text


def test_repair_cjk_emphasis_never_touches_link_destinations():
    """外部 review C1：`protected_mask` 只保護 code，不保護連結／圖片的
    destination。而「內容含 CJK」那條過濾是為 ASCII URL 設計的，對**含中文的
    URL** 完全失效 —— 偏偏含中文的 URL 只會出現在中文譯文裡（模型把英文維基
    連結換成 `zh.wikipedia.org/wiki/區塊鏈_(技術)`、或引入中文檔名的圖片）。
    改成星號 → href 帶著 `*` → 404、圖裂，而 gate 10 看不到（<em> 數不減反增）。
    """
    cases = [
        "見[文件](https://example.com/wiki/中文_頁面_說明)。\n",
        "![說明](./img/中文_圖_1.png)\n",
        "見 <https://example.com/中文_頁_說明> 一文。\n",
        "裸連結 https://example.com/中文_頁_說明 也一樣。\n",
    ]
    for text in cases:
        assert pipeline._repair_cjk_emphasis(text) == text, text


def test_repair_cjk_emphasis_never_crosses_identifier_boundary():
    """外部 review C2：regex 是逐一非貪婪配對，一行內底線數為奇數時，
    第一個 `_` 會跟真正強調的**起始** `_` 配成一對，把中間整段吃掉 ——
    識別字被拆、強調錯位、尾巴留下裸底線。gate 10 同樣看不到（<em> 由 0 變 1，
    是增加）。判準：底線緊鄰 ASCII 英數時一律不碰，那是識別字不是強調。
    """
    # 正確行為是「識別字不動、強調照修」，不是「整行放棄」——後者是第一版
    # 過度保守的修法，會讓合法強調永遠修不掉、gate 10 每輪都紅。
    out = pipeline._repair_cjk_emphasis("本節說明 tx_context 與_所有權_的關係。\n")
    assert out == "本節說明 tx_context 與*所有權*的關係。\n"
    assert "tx_context" in out  # 識別字逐字不變


def test_repair_cjk_emphasis_never_downgrades_strong():
    """外部 review C3：`__粗體__` 會被匹配到內層 `_粗體_`，外層兩個底線
    原地留下 → `_*粗體*_`，<strong> 降級成 <em> 且畫面多出兩個裸底線。
    這個很可能已經會發生：本次事故就是 backend 從 `*` 換成 `_`，
    對 `**bold**` 的自然對應就是 `__bold__`。
    """
    text = "這是__粗體強調__的說明。\n"
    assert pipeline._repair_cjk_emphasis(text) == text


def test_repair_cjk_emphasis_pairs_delimiters_per_line():
    """複驗輪 C1：上一版只擋「底線緊鄰 ASCII 英數」，但跨強調邊界的錯誤配對
    根本不需要 ASCII 相鄰 —— 被跳過的匹配仍然**消耗掉**那個底線，finditer
    從匹配尾端續掃，下一次配對就跨過真正的邊界：

        說明 tx_context 與_所有權_的關係，也講_物件_模型。
        → 說明 tx_context 與_所有權*的關係，也講*物件_模型。

    兩處強調被拆掉、憑空造出一個 `*的關係，也講*`，而 gate 10 綠燈放行
    （英文 1 處、破壞後的中文也剛好渲染出 1 處，數量守恆）。
    根因是「逐一配對」本身，不是相鄰條件 —— 改成逐行 tokenize + 成對決議。
    """
    text = "說明 tx_context 與_所有權_的關係，也講_物件_模型。\n"
    assert (
        pipeline._repair_cjk_emphasis(text)
        == "說明 tx_context 與*所有權*的關係，也講*物件*模型。\n"
    )


def test_repair_cjk_emphasis_still_fixes_emphasis_next_to_strong():
    """複驗輪 B1：上一版為了擋 `__粗體__` 而過度保守，把同行的合法強調
    一起放棄 → gate 10 每輪都紅、人工介入率上升，而且 B4 的「可疑位置」
    還會指向 `_粗體_`，人照著改會把粗體拆掉。粗體不動、強調要修。"""
    assert (
        pipeline._repair_cjk_emphasis("這是__粗體__和_強調_。\n")
        == "這是__粗體__和*強調*。\n"
    )
    assert (
        pipeline._repair_cjk_emphasis("見 https://e.com/中文_頁 後面_重點_說明。\n")
        == "見 https://e.com/中文_頁 後面*重點*說明。\n"
    )


def test_repair_cjk_emphasis_ignores_isolated_underscores():
    """終驗輪 B1：兩側皆為空白的底線既不是有效的 CommonMark 分隔符（開頭
    分隔符後面不能是空白、收尾前面不能是空白），也沒被前三條規則排除，
    parity 照樣算它一份 → 又跨過真正的邊界：

        見 _ 標記 和_重點_說明 _ 結束。
        → 見 * 標記 和*重點*說明 * 結束。

    散文裡憑空多出星號，gate 10 全程綠燈（<em> 不減反增）。這本書大量在講
    Move 的 `_` 萬用字元，譯文散文出現孤立 `_` 是可預期的。
    """
    cases = [
        "見 _ 標記 和_重點_說明 _ 結束。\n",
        "填 _ 值，這是_重點_，另 _ 欄。\n",
        "見 _ 這裡 _ 說明。\n",
    ]
    expected = [
        "見 _ 標記 和*重點*說明 _ 結束。\n",   # 孤立底線不動，真強調照修
        "填 _ 值，這是*重點*，另 _ 欄。\n",
        "見 _ 這裡 _ 說明。\n",               # 全是孤立底線，整行不動
    ]
    for text, want in zip(cases, expected):
        assert pipeline._repair_cjk_emphasis(text) == want, text


def test_repair_cjk_emphasis_skips_line_when_delimiters_cannot_be_paired():
    """配不成對就整行放棄（fail-safe）。寧可漏修讓 gate 10 擋下來人工處理，
    也不要猜一個配對然後靜默改壞。"""
    text = "只有一個_底線的中文行。\n"
    assert pipeline._repair_cjk_emphasis(text) == text


def test_gate_flags_emphasis_lost_in_translation():
    """fail-closed 的判準是「跟英文原文比，中文渲染出來的強調變少了」——
    不是「有沒有可疑的底線對」。前者是真實性質（翻譯弄丟了強調），後者是
    代理量，實測對全語料噴 192 個假陽性（URL 與 snake_case 識別字）。"""
    from scripts.zh_tw import validate

    en = "# T {#t}\n\nIncluding *ownership changes*; and more.\n"
    bad = "# 標題 (T) {#t}\n\n包括_所有權的變更_；還有別的。\n"
    good = "# 標題 (T) {#t}\n\n包括*所有權的變更*；還有別的。\n"

    assert validate.check_cjk_emphasis(bad, en)
    assert validate.check_cjk_emphasis(good, en) == []

    # URL 裡的底線不得被算成強調，也不得因此報錯
    en2 = "# T {#t}\n\nSee [Lambda](https://en.wikipedia.org/wiki/Lambda_(computer_function)).\n"
    zh2 = "# 標題 (T) {#t}\n\n見 [Lambda](https://en.wikipedia.org/wiki/Lambda_(computer_function))。\n"
    assert validate.check_cjk_emphasis(zh2, en2) == []


# --- gate 11 的修復 pass ---


def test_repair_ol_numbering_removes_the_duplicated_marker():
    """沒有修復路徑的 gate 是結構性死鎖：pipeline 對 check_file 的任一錯誤
    直接 raise，該檔就永久寫不出來（同 _repair_headings docstring 的規矩）。"""
    body = "1.  **1. 預設安全性 (Secure by default):** 內文\n\n2.  **2. 表達力:** 內文\n"
    out = pipeline._repair_ol_numbering(body)
    assert out == "1.  **預設安全性 (Secure by default):** 內文\n\n2.  **表達力:** 內文\n"
    assert validate.check_ordered_list_numbering("---\nx: 1\n---\n\n" + out) == []


def test_repair_ol_numbering_matches_identity_not_shape():
    """只刪「與列表標記同一個數字」的那一份。合法內容一個字都不准動。"""
    for body in [
        "1. 1.0 版本引入了新語法\n",
        "1. 2024 版本\n",
        "1. `1.` 是有序列表標記\n",
        "2. 1. 這是不同的數字\n",
    ]:
        assert pipeline._repair_ol_numbering(body) == body, body


def test_repair_ol_numbering_never_touches_code():
    """fence 內是範例，不是散文。"""
    body = "```\n1. **1. 假的**\n```\n\n1. **1. 真的**\n"
    out = pipeline._repair_ol_numbering(body)
    assert "1. **1. 假的**" in out  # fence 內是範例，不動
    assert "1. **真的**" in out  # fence 外的真缺陷要修掉


def test_repair_ol_numbering_handles_emphasised_forms():
    assert pipeline._repair_ol_numbering("5. **5. 粗體**\n") == "5. **粗體**\n"
    assert pipeline._repair_ol_numbering("7. _7. 斜體_\n") == "7. _斜體_\n"
    assert pipeline._repair_ol_numbering("1. ***1. 三星***\n") == "1. ***三星***\n"


def test_repair_ol_numbering_never_flattens_a_nested_list():
    """`1. 1. 甲` 在 CommonMark 是**巢狀列表**，不是重複序號 —— gate 11 對它
    正確地不報錯。第一版的修復 pass 自己重刻了一套行首 regex，看不出巢狀，
    把它改寫成 `1. 甲`，靜默拆掉一層 <ol>：gate 前不紅、修完也不紅，沒有
    任何守衛看得見（2026-09-04 外部 review 實測）。

    這是 lessons L7 的形狀：同一個不變式的兩份獨立實作必然漂移。現在判定權
    只在 gate 那一側。
    """
    import commonmark

    for body in ["1. 1. 甲\n", "3. 3. 沒有強調\n", "1. 1) 甲\n", "1.  1. 甲\n"]:
        assert validate.check_ordered_list_numbering("---\nx: 1\n---\n\n" + body) == []
        out = pipeline._repair_ol_numbering(body)
        assert out == body, (body, out)
        assert commonmark.commonmark(out) == commonmark.commonmark(body)


def test_repair_ol_numbering_preserves_ordered_list_structure():
    """驗收條件之一是「有序列表的結構指紋不變」。拿掉它，修復就能靠改變
    列表結構去讓 gate 閉嘴。"""
    body = "1. **1. 甲**\n\n2. **2. 乙**\n\n   1. 內層\n"
    before = pipeline._ol_shape(body)
    out = pipeline._repair_ol_numbering(body)
    assert pipeline._ol_shape(out) == before
    assert validate.check_ordered_list_numbering("---\nx: 1\n---\n\n" + out) == []


def test_repair_ol_numbering_covers_the_forms_the_gate_flags():
    """gate 判紅、修復卻認不得 = 該檔永久寫不出來。這幾種形態外部 review
    實測過會死鎖（行尾、三星號、數字與分隔符間有空白、NBSP、全形頓號），
    現在都由 gate 驅動的候選涵蓋。"""
    for body in ["1. ***1. 甲***\n", "1. 1 . 甲\n", "1. 1.\u00a0甲\n", "1. 1、甲\n", "1. 1）甲\n"]:
        assert validate.check_ordered_list_numbering("---\nx: 1\n---\n\n" + body), body
        out = pipeline._repair_ol_numbering(body)
        assert validate.check_ordered_list_numbering("---\nx: 1\n---\n\n" + out) == [], (body, out)


def test_assemble_repairs_ol_numbering_end_to_end():
    """修復 pass 必須真的掛在 assemble 的鏈上。只測函式本身的話，把接線
    拆掉（assemble 不再呼叫它）測試仍會全綠 —— 而 gate 11 一擋就是該檔
    永久寫不出來。

    backend 必須真的產出缺陷形態：FakeBackend 把所有散文換成「中文」，
    所以要在它的輸出上動手，不能對原文做字串替換（那樣是空轉的測試）。
    """

    class DupNumberBackend(FakeBackend):
        def translate(self, text: str, *, kind: str = "markdown") -> str:
            out = super().translate(text, kind=kind)
            # 把 `1. 中文` 變成機翻實際產出的 `1. **1. 中文**`
            return re.sub(r"(?m)^(\d+)\. (?!\*)(.+)$", r"\1. **\1. \2**", out)

    en = '---\ndescription: "desc"\n---\n\n# One\n\n1. Alpha\n\n2. Beta\n'
    dup = DupNumberBackend().translate("# One\n\n1. Alpha\n\n2. Beta\n")
    assert "1. **1. " in dup, dup  # 先確認這個 backend 真的會製造缺陷

    out = pipeline.assemble(en, "", "", DupNumberBackend())
    assert "**1. " not in out, out
    assert validate.check_ordered_list_numbering(out) == []


def test_repair_ol_numbering_leaves_raw_html_lists_to_the_gate():
    """已知不涵蓋的殘餘情況要用測試釘住，不是靠註解宣稱。

    裸 HTML 列表 gate 11 看得見、這個 pass 認不得 → 檔案被擋下（fail-closed）。
    這是刻意的取捨：backend 翻譯 markdown、不產裸 HTML 列表，為了這種情況
    去放寬 gate 才是把守衛弄壞（lessons L5）。
    """
    body = "<ol><li>1. 重複</li></ol>\n"
    assert pipeline._repair_ol_numbering(body) == body  # 修不掉
    assert validate.check_ordered_list_numbering("---\nx: 1\n---\n\n" + body)  # 但擋得住


def test_repair_ol_numbering_preserves_shape_for_arbitrary_input():
    """性質測試：修復**永遠**不准改變渲染後的標籤骨架。

    atom 表要拼得出會出事的組合，否則這條就是會執行的註解（lessons L4）。
    第一版的 atom 全是單一 token，永遠拼不出「全形分隔符 + 不同數字的
    半形列表標記」（`1、2.`）這種複合形態，於是把 `_ol_shape` 驗收整條
    拿掉，這個測試仍然全綠——外部 review 用 20000 例差分 fuzz 才找到分歧。
    現在複合 atom 與會升格成 block 構造的字元都在表裡。
    """
    import random

    atoms = ["1.", "2.", "3.", "-", "**", "*", "_", "`", "甲", "\n", "\n\n", "   ",
             "1、", "1）", "0.", "5.", "1.0", "```", "> ", "１.", " ", "文字",
             # 複合：刪掉前綴後會露出另一個列表標記／區塊標記
             "1、2.", "1、3.", "1）2.", "1、# ", "1、> ", "1、- ", "1、```",
             # 數字被 inline 構造包住
             "**1.**", "*1.*", "_1._", "**1、**", "[1.](x)", "**1**."]
    random.seed(11)
    for _ in range(4000):
        body = "".join(random.choice(atoms) for _ in range(random.randint(1, 18)))
        out = pipeline._repair_ol_numbering(body)
        assert pipeline._ol_shape(out) == pipeline._ol_shape(body), (body, out)


def test_repair_ol_numbering_never_writes_literal_emphasis_markers():
    """`1. **1.** 甲` 刪掉 `1.` 之後，前後兩個 `**` 會黏成 `****`：強調整個
    消失、讀者看到字面的星號，而 gate 11 反而變安靜（錯誤數 1→0）、
    gate 10 也沒接住。這是靜默寫進語料，比原本的缺陷更難發現
    （2026-09-04 第三輪外部 review 實測）。

    現在標籤骨架驗收會擋下來：<strong>/<em> 消失就是結構改變。修不掉就
    保持原樣，交給 gate fail-closed。
    """
    for body in ["1. **1.** 預設安全性\n", "1. *1.* 甲\n", "1. _1._ 甲\n", "1. **1、** 甲\n"]:
        out = pipeline._repair_ol_numbering(body)
        assert out == body, (body, out)
        assert "****" not in out and "__" not in out


def test_repair_ol_numbering_never_promotes_text_to_a_block_construct():
    """刪掉的前綴原本在遮蔽後面的 block 標記，刪完那個字元就升格：
    `1. 1、# 大標題` → `1. # 大標題` 會在 li 裡長出 <h1>（`>` → blockquote、
    `-` → <ul>、``` → <pre> 同理）。序號序列指紋對這些零反應。
    """
    for body in ["1. 1、# 大標題\n", "1. 1、> 引言\n", "1. 1、- 項目\n"]:
        out = pipeline._repair_ol_numbering(body)
        assert out == body, (body, out)


def test_repair_ol_numbering_never_increases_gate_errors():
    """修復只准讓 gate 更安靜，不准製造新的缺陷。"""
    import random

    def errs(b):
        return len(validate.check_ordered_list_numbering("---\nx: 1\n---\n\n" + b))

    atoms = ["1.", "2.", "**", "甲", "\n", "\n\n", "   ", "1、", "1.0", "```", "1）",
             "1、2.", "**1.**", "[1.](x)"]
    random.seed(12)
    for _ in range(4000):
        body = "".join(random.choice(atoms) for _ in range(random.randint(1, 15)))
        assert errs(pipeline._repair_ol_numbering(body)) <= errs(body), body


def test_repair_ol_numbering_known_deadlocks_are_pinned():
    """gate 判紅、候選認不得 → 該檔永久寫不出來。這些形態目前修不掉，
    fail-closed 是刻意的（不為了消滅殘餘去弱化守衛，lessons L5），但要有
    測試釘住清單，別讓它悄悄變長。
    """
    for body in [
        "<ol><li>1. 重複</li></ol>\n",  # 裸 HTML 列表
        "1. **1**. 甲\n",  # 分隔符在強調外
        "1. [1.](x) 甲\n",  # 序號被連結包住
        "1. **1.** 甲\n",  # 刪掉會黏成 ****
    ]:
        assert validate.check_ordered_list_numbering("---\nx: 1\n---\n\n" + body), body
        assert pipeline._repair_ol_numbering(body) == body, body


def test_repair_ol_numbering_only_ever_deletes_the_duplicated_number():
    """最強的那條後置條件：渲染後的**文字**只准發生「刪除」，而且每一段被
    刪掉的都必須是「數字+分隔符」。不准有任何插入或替換。

    標籤骨架管結構，這條管內容 —— `_TAG` 只抓標籤名，屬性不在骨架裡
    （`<a href="X">` 與 `<a href="Y">` 骨架相同），所以光靠骨架擋不住
    「只改文字或屬性」的破壞。

    這條**不能**用「把兩側的數字都正規化掉再比對」來寫：那樣寫的話
    `1. 甲` → `2. 甲`（序號被改成另一個數字）與 `1. 甲 2. 乙` → `1. 甲 乙`
    （刪掉別人的序號）都會被判成相等，等於對「改壞」全盲。改用 difflib
    逐段檢查實際的編輯操作。
    """
    import difflib
    import html as _html
    import random
    import re as _re

    import commonmark

    tag = _re.compile(r"<[^>]+>")
    num = _re.compile(r"\d+\s*[.、．)）]\s*")

    def text(md):
        return _html.unescape(tag.sub("", commonmark.commonmark(md)))

    def only_number_deletions(before, after):
        sm = difflib.SequenceMatcher(None, before, after, autojunk=False)
        for op, i1, i2, _j1, _j2 in sm.get_opcodes():
            if op == "equal":
                continue
            if op != "delete":
                return False
            if not num.fullmatch(before[i1:i2]):
                return False
        return True

    # 先確認這個檢查抓得到已知的兩類破壞，否則它就是會執行的註解（L4）
    assert not only_number_deletions("1. 甲", "2. 甲")
    assert not only_number_deletions("第 1 節與第 2 節", "第 1 節與第 3 節")
    assert only_number_deletions("1.  1. 甲", "1.  甲")

    atoms = ["1.", "2.", "3.", "-", "**", "*", "_", "`", "甲", "乙", "\n", "\n\n", "   ",
             "1、", "1）", "0.", "5.", "1.0", "```", "> ", "１.", " ", "文字",
             "1、2.", "1、# ", "1、> ", "1、- ", "**1.**", "*1.*", "_1._",
             "[1.](x)", "**1**.", "[1. 甲](u)", "![1. a](i)", "&nbsp;", "1.&nbsp;"]
    random.seed(99)
    for _ in range(3000):
        body = "".join(random.choice(atoms) for _ in range(random.randint(1, 22)))
        out = pipeline._repair_ol_numbering(body)
        if out == body:
            continue
        assert only_number_deletions(text(body), text(out)), (body, out)
