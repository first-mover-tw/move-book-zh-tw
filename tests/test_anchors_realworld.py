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

# english-main 在收斂 {#id} 判準當下的 tip。釘固定 sha，不用可移動的分支名 ——
# 這是回歸基線，不是上游追蹤器。
EN_CENSUS_SHA = "29e332267ecbebb7682b5e8df186e1059664cf3d"
EN_CENSUS_FILES = 156
EN_CENSUS_HEADINGS = 1164


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


def test_english_source_has_no_explicit_anchor_ids():
    """`slugify()` 的輸入端不會被放寬判準影響 —— 因為英文原檔一個顯式 {#id} 都沒有。

    這條刻意**不**寫成「新舊 regex 判定全等」的對拍：英文語料裡沒有任何標題含
    字面 `{#`，那種對拍在這個語料上恆為 None == None，把 _ANCHOR 換成任何東西
    它都會綠（review 實測）。守衛要觀測它真正宣稱的性質（lessons L2），所以這裡
    直接數「含字面 `{#` 的標題有幾個」與「解析得出 id 的標題有幾個」，兩者都必須是 0。
    數字一變，代表英文上游開始使用顯式 anchor —— 那時 slugify 的輸入端假設就變了，
    要有人回來看一眼。
    """
    files = _files_at(EN_CENSUS_SHA)
    scanned = headings = literal_brace = explicit_ids = 0
    for path in files:
        text = _show(EN_CENSUS_SHA, path)
        if not text:
            continue
        _, body = frontmatter.split(text)
        hs = anchors.headings(body)   # 不吞例外：解析失敗就是要紅
        scanned += 1
        for _, t in hs:
            headings += 1
            if "{#" in t:
                literal_brace += 1
            if anchors.existing_anchor(t) is not None:
                explicit_ids += 1

    assert scanned == EN_CENSUS_FILES
    assert headings == EN_CENSUS_HEADINGS
    assert literal_brace == 0
    assert explicit_ids == 0
