import re
import subprocess

import pytest

from scripts.zh_tw import anchors, frontmatter

MERGE_BASE = "f2c0a93e1a0422078d3d051e4410ac3edc612016"
# 修復前的 zh-tw-main tip。釘死不動，否則 backfill 合併後這個測試會因為
# 「我們修好了東西」而變紅 —— 基線必須是固定靶。
PRE_FIX = "0d4b8bea77f1a6195b589ded4067d287adb4379a"

# 這兩個 anchor 是人工刻意選定的，與英文 slug 不同。
# 它們的存在正是 inject() 必須「沿用優先於重算」的理由。
KNOWN_DIVERGENT = {
    ("book/object/ownership.md", "immutable-frozen-object"),
    ("book/programmability/epoch-and-time.md", "clock"),
}


def _show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def _files() -> list[str]:
    r = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", PRE_FIX, "book", "reference"],
        capture_output=True, text=True, check=True,
    )
    return [f for f in r.stdout.split() if f.endswith(".md")]


def test_slugify_reproduces_existing_anchors():
    """除了兩個已知的人工選定 anchor，slugify(英文標題) 應重現全部既有 anchor。

    47 而非 46：初版 headings() 把 HTML 註解裡的標題也算進去，導致
    book/move-basics/string.md 的中英文標題數不符（10 vs 11）而被跳過。
    修好 parser 後該檔重新納入，貢獻一個正確配對的 {#ascii-strings}。
    """
    divergent, reproduced = set(), 0
    for path in _files():
        zh, en = _show(PRE_FIX, path), _show(MERGE_BASE, path)
        if not zh or not en or "{#" not in zh:
            continue
        _, zh_body = frontmatter.split(zh)
        _, en_body = frontmatter.split(en)
        zh_h, en_h = anchors.headings(zh_body), anchors.headings(en_body)
        if len(zh_h) != len(en_h):
            continue  # 結構殘缺檔，由 validate 負責
        for (_, zt), (_, et) in zip(zh_h, en_h):
            aid = anchors.existing_anchor(zt)
            if aid is None:
                continue
            if aid == anchors.slugify(et):
                reproduced += 1
            else:
                divergent.add((path, aid))

    assert reproduced == 47
    assert divergent == KNOWN_DIVERGENT


# 收斂 {#id} 判準（2026-09-06）當下的語料狀態。釘固定 sha，不讀 working tree
# —— census 測試讀活狀態會在下一次排乾後永久紅（lessons L3）。
ANCHOR_CENSUS_SHA = "5759c28ec0ef5c7b9e638093659baccd6f5f196f"
ANCHOR_CENSUS_HEADINGS = 1102
ANCHOR_CENSUS_WITH_ID = 1102


def _files_at(ref: str, *roots: str) -> list[str]:
    r = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, *roots],
        capture_output=True, text=True, check=True,
    )
    return [f for f in r.stdout.split() if f.endswith(".md")]


def test_widened_anchor_pattern_is_a_noop_on_the_real_corpus():
    """放寬到上游判準之後，全語料每個標題的 id 判定都不能變。

    收斂前的窄版 regex 是 [A-Za-z0-9_-]+；語料裡的 id 全是 ASCII，所以
    正確的收斂應該是 byte 級 no-op。這條測試把「應該」變成可判定的事實。
    """
    narrow = re.compile(r"\s*\{#([A-Za-z0-9_-]+)\}\s*$")
    total = with_id = 0
    for path in _files_at(ANCHOR_CENSUS_SHA, "book", "reference"):
        _, body = frontmatter.split(_show(ANCHOR_CENSUS_SHA, path) or "")
        for _, t in anchors.headings(body):
            total += 1
            new = anchors.existing_anchor(t)
            m = narrow.search(t)
            old = m.group(1) if m else None
            assert new == old, (path, t, new, old)
            if new:
                with_id += 1
    assert total == ANCHOR_CENSUS_HEADINGS
    assert with_id == ANCHOR_CENSUS_WITH_ID
    assert with_id == total  # 全語料每個標題都已帶顯式 anchor


def test_widened_anchor_pattern_is_a_noop_on_the_english_source():
    """english-main 的英文原檔顯式 id 數為 0；slugify 的輸入端不因放寬而改變。"""
    narrow = re.compile(r"\s*\{#([A-Za-z0-9_-]+)\}\s*$")
    seen = 0
    for path in _files_at("english-main"):
        text = _show("english-main", path)
        if not text:
            continue
        try:
            _, body = frontmatter.split(text)
            hs = anchors.headings(body)
        except Exception:
            continue  # 結構殘缺檔由 validate 負責，不是本測試的對象
        for _, t in hs:
            seen += 1
            m = narrow.search(t)
            assert anchors.existing_anchor(t) == (m.group(1) if m else None), (path, t)
    assert seen > 1000  # 防止「一個檔都沒掃到卻綠燈」的空轉
