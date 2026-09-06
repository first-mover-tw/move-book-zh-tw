"""單一真相來源守衛：repo 內只准有一處 `{#id}` 的 regex 定義。

這條測試存在的理由是 2026-09-06 的實測狀態：anchors 用 [A-Za-z0-9_-]+、
validate 與 backends.fake 用 Unicode 的 [\\w-]+、消費者 docusaurus 用
[^{#}]+ —— 三份定義，零份等於消費者（lessons L15 / L23）。
"""

import re
from pathlib import Path

from scripts.zh_tw import anchors, validate
from scripts.zh_tw.backends import fake

SRC = Path("scripts/zh_tw")

# 產品程式碼裡「長得像在比對 {#id}」的 regex 字面值。
_REGEX_LITERAL = re.compile(r"""re\.compile\(\s*r?["'][^"']*\\\{#""")


def test_validate_reuses_the_anchors_pattern_object():
    assert validate.ANCHOR_SUFFIX is anchors.ANCHOR_SUFFIX


def test_fake_backend_reuses_the_anchors_pattern_object():
    assert fake.FakeBackend._EXPLICIT_ANCHOR is anchors.ANCHOR_SUFFIX


def test_only_anchors_module_compiles_an_anchor_regex():
    """tests/ 底下的上游移植字面值是刻意的第二份（對拍用），不在掃描範圍。"""
    offenders = sorted(
        str(p)
        for p in SRC.rglob("*.py")
        if p.name != "anchors.py" and _REGEX_LITERAL.search(p.read_text(encoding="utf-8"))
    )
    assert offenders == []


def test_gate_and_inject_agree_on_a_cjk_anchor():
    """收斂前的實證分歧：gate 的前處理剝得掉 CJK anchor，inject 認不得，
    於是同一份輸入產出兩套判定母體，inject 寫出兩個 {#id} 相連。"""
    heading = "中止與斷言 {#終止與斷言-abort-and-assert}"
    assert validate.ANCHOR_SUFFIX.sub("", heading).strip() == "中止與斷言"
    assert anchors.existing_anchor(heading) == "終止與斷言-abort-and-assert"

    zh = "# T {#a}\n\n## " + heading + "\n"
    en = "# T {#a}\n\n## Abort and Assert\n"
    out = anchors.inject(zh, en)
    assert out.count("{#") == 2  # 兩個標題各一個，不是三個
    assert "{#終止與斷言-abort-and-assert}" in out


from scripts.zh_tw import check_repo


def test_pipeline_never_derives_a_cjk_anchor():
    """tier 3（衍生）一律由英文標題 slugify 而來，結構上不可能是 CJK。
    放寬判準只開啟「沿用人工寫進語料的 CJK id」，不開啟「自己產生」。"""
    zh = "# 中止與斷言 (Abort and Assert)\n\n## 斷言 (Assert)\n"
    en = "# Abort and Assert\n\n## Assert\n"
    out = anchors.inject(zh, en)
    ids = [anchors.existing_anchor(t) for _, t in anchors.headings(out)]
    assert ids == ["abort-and-assert", "assert"]


def test_existing_cjk_anchor_is_carried_forward_verbatim():
    """tier 1：已寫進語料的 id 是已發佈契約，原封不動。"""
    zh = "# 中止 {#中止}\n"
    en = "# Abort\n"
    out = anchors.inject(zh, en)
    assert anchors.existing_anchor(anchors.headings(out)[0][1]) == "中止"


def test_cjk_anchor_hits_reports_nothing_on_the_current_corpus():
    """baseline 0。數字一變就要有人看一眼是誰手動寫了 CJK anchor
    （比照 glossary scan-only 的 baseline 做法：沒有 baseline 的警告
    等於沒人看的噪音）。"""
    assert check_repo.cjk_anchor_hits(check_repo.collect()) == []


def test_cjk_anchor_hits_finds_a_planted_one():
    files = {"book/x.md": "# 中止 {#中止}\n"}
    assert check_repo.cjk_anchor_hits(files) == [("book/x.md", "中止")]
