"""台灣用語術語表的掃描與強制替換。

模型的中文訓練語料以簡體為主，繁化後詞彙仍是大陸慣用語（「繁體字、大陸詞」）。
prompt 指示不可靠，故翻譯後一律以程式碼掃描並替換。
"""

import json
import re
from collections import Counter
from pathlib import Path

_DEFAULT = Path(__file__).parent / "glossary.json"

# 保護區：fenced code block 與 inline code
_PROTECTED = re.compile(r"(```.*?```|`[^`\n]*`)", re.S)


def load(path: str | None = None) -> dict[str, str]:
    return json.loads(Path(path or _DEFAULT).read_text(encoding="utf-8"))


def _split_protected(body: str) -> list[tuple[bool, str]]:
    """回傳 (is_protected, segment) 序列。"""
    parts, last = [], 0
    for m in _PROTECTED.finditer(body):
        if m.start() > last:
            parts.append((False, body[last:m.start()]))
        parts.append((True, m.group(0)))
        last = m.end()
    if last < len(body):
        parts.append((False, body[last:]))
    return parts


def enforce(body: str, table: dict[str, str] | None = None) -> str:
    table = table or load()
    out = []
    for protected, seg in _split_protected(body):
        if not protected:
            for bad, good in table.items():
                seg = seg.replace(bad, good)
        out.append(seg)
    return "".join(out)


def scan(body: str, table: dict[str, str] | None = None) -> dict[str, int]:
    table = table or load()
    counts: Counter[str] = Counter()
    for protected, seg in _split_protected(body):
        if protected:
            continue
        for bad in table:
            n = seg.count(bad)
            if n:
                counts[bad] += n
    return dict(counts)


def prompt_rules(table: dict[str, str] | None = None) -> str:
    table = table or load()
    pairs = "、".join(f"{good}（不要用{bad}）" for bad, good in table.items())
    return (
        "使用台灣繁體中文的技術用語。務必遵守以下對照："
        f"{pairs}。程式碼與 inline code 中的識別字不要翻譯。"
    )
