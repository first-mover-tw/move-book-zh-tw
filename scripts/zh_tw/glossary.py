"""台灣用語術語表的掃描與強制替換。

模型的中文訓練語料以簡體為主，繁化後詞彙仍是大陸慣用語（「繁體字、大陸詞」）。
prompt 指示不可靠，故翻譯後一律以程式碼掃描並替換。
"""

import json
import re
from collections import Counter
from pathlib import Path

from . import anchors

_DEFAULT = Path(__file__).parent / "glossary.json"

# inline code 是單行 span，逐行的 regex 遮罩是正確的做法。
# fence / 縮排 code block 這類跨行的區塊結構一律交給 anchors.code_lines()
# （markdown-it-py 的 token stream），這裡不再自己刻 fence 偵測迴圈。
_INLINE_CODE = re.compile(r"`[^`\n]*`")


def load(path: str | None = None) -> dict[str, str]:
    return json.loads(Path(path or _DEFAULT).read_text(encoding="utf-8"))


def _visible_segments(line: str):
    """回傳單行內 (is_inline_code, segment) 序列，遮罩 inline code。"""
    last = 0
    for m in _INLINE_CODE.finditer(line):
        if m.start() > last:
            yield False, line[last:m.start()]
        yield True, m.group(0)
        last = m.end()
    if last < len(line):
        yield False, line[last:]


def enforce(body: str, table: dict[str, str] | None = None) -> str:
    table = table or load()
    code = anchors.code_lines(body)
    lines = body.splitlines(keepends=True)
    out = []
    for i, line in enumerate(lines):
        if i in code:
            out.append(line)
            continue
        buf = []
        for is_code, seg in _visible_segments(line):
            if not is_code:
                for bad, good in table.items():
                    seg = seg.replace(bad, good)
            buf.append(seg)
        out.append("".join(buf))
    return "".join(out)


def scan(body: str, table: dict[str, str] | None = None) -> dict[str, int]:
    table = table or load()
    code = anchors.code_lines(body)
    counts: Counter[str] = Counter()
    lines = body.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if i in code:
            continue
        for is_code, seg in _visible_segments(line):
            if is_code:
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
