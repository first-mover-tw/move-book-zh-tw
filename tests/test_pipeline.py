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
            return "# 標題\n\n這個函數會返回值\n"

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


def test_glossary_rewrites_function_term():
    en = '---\ndescription: "d"\n---\n\n# T\n'

    class FuncBackend:
        def translate(self, text, *, kind="markdown"):
            if kind == "text":
                return "中文"
            return "# 標題\n\n這是一個函數\n"

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
