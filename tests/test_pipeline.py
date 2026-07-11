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


def _tier_fixture(path):
    """回傳 (zh@HEAD, en@merge-base)，供測試斷言前置條件仍成立——
    避免 repo 狀態改變後測試變 vacuous（宣稱的缺陷早已不存在卻照樣綠）。"""
    import subprocess

    zh = subprocess.run(
        ["git", "show", f"HEAD:{path}"], capture_output=True, text=True, check=True
    ).stdout
    en = subprocess.run(
        ["git", "show", f"{pipeline.MERGE_BASE}:{path}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return zh, en


def test_tier_a_when_only_body_forbidden_words():
    """reference/constants.md：結構一致，內文帶違禁詞「循環」。內文品質
    缺陷不在 validate 第 1、2 條，不構成降級。"""
    zh, en = _tier_fixture("reference/constants.md")
    assert validate.check_structure(zh, en) == []
    assert any("違禁詞" in e for e in validate.check_file(zh, en))
    assert pipeline.tier("reference/constants.md") == "A"


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
