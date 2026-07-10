import subprocess

import pytest

from scripts.zh_tw import anchors

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
    """除了兩個已知的人工選定 anchor，slugify(英文標題) 應重現全部既有 anchor。"""
    divergent, reproduced = set(), 0
    for path in _files():
        zh, en = _show(PRE_FIX, path), _show(MERGE_BASE, path)
        if not zh or not en or "{#" not in zh:
            continue
        zh_h, en_h = anchors.headings(zh), anchors.headings(en)
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

    assert reproduced == 46
    assert divergent == KNOWN_DIVERGENT
