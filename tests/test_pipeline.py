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


def test_tier_b_when_structure_fails_even_if_delta_is_small():
    """reference/variables.md：上游只動 frontmatter，但中文只有 36 行 / 6 個標題
    （英文 824 行 / 21 個標題）。結構驗證擋下，強制降級 B 層全譯。
    這是分層閘門存在的理由 —— 純看 delta 大小會讓那 788 行永遠回不來。"""
    assert pipeline.tier("reference/variables.md") == "B"


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


def test_assemble_raises_when_backend_drops_heading_suffix():
    """Task 17 A/B 實測到的失效模式：真實 backend（sonnet）對 4/21 標題
    掉了「中文 (English)」後綴、其中一個整個沒翻，八道 gate 全數放行。
    gate 9 掛在 assemble 路徑上，這種輸出必須整份炸掉。"""
    en = '---\ndescription: "d"\n---\n\n# One\n\n## Two\n'

    class SuffixDroppingBackend:
        def translate(self, text, *, kind="markdown"):
            if kind == "text":
                return "中文"
            return "# 一 (One)\n\n## 二\n"  # 第二個標題掉後綴

    with pytest.raises(validate.ValidationError, match="後綴"):
        pipeline.assemble(en, "", "", SuffixDroppingBackend())


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
