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

# CommonMark inline code 是「反引號 run + 同長度反引號 run 收尾」的 span，
# 內容可以跨行 —— 只有空白行（段落結束）會終止它。之前這裡用逐行 regex
# 遮罩 inline code，隱含假設「inline code 是單行 span」，那個假設是錯的：
# 一個跨行的 code span 會讓逐行 regex 完全遮不到它，術語替換因此鑽進
# code span 內部改字。修法是在整份 body 上算一份字元級遮罩，同時涵蓋
# fence / 縮排 code block（來自 anchors.code_lines()，行級）與 inline
# code span（這裡，字元級），scan() 和 enforce() 共用同一份遮罩，避免
# 兩者對「什麼算被保護」各自表述而互相漏檢/誤改。
#
# 反引號 run 的長度用具名群組 back-reference 匹配收尾 run；非貪婪的
# `[\s\S]` 允許跨行，但用 lookahead 擋掉「換行 + 只剩空白的一行」
# （= 段落分隔），對齊 CommonMark：未閉合的反引號不會把後面整份文件
# 都吃掉。
#
# CommonMark 規定開頭/收尾的反引號 run 都必須是「maximal」——不能是
# 更長的一串反引號中間夾的一段。單純的 back-reference `(?P=t)` 只保證
# 長度相同，不保證收尾 run 沒有再往左右延伸；`` `函數``` `` 這種收尾
# 前後還連著別的反引號的情形，CommonMark 判定「不是 code span」，但
# 舊 regex 會誤判成一個 code span，讓術語替換被靜默豁免。用
# `(?<!`)...(?<!`)(?P=t)(?!`)` 分別在開頭 run 前、收尾 run 前後加上
# 「不是反引號」的邊界斷言，強迫兩端都必須是 maximal run，才會對齊
# markdown-it-py 的 code_inline 判定。
#
# 開頭 run 用 possessive quantifier `` `++ ``（不是 `` `+ ``）：普通的
# `` `+ `` 是可回溯的貪婪量詞，當收尾找不到同長度的 maximal run 時，
# 引擎會把 `t` 回溯成更短的 run，把多出來的反引號當成普通內容——這會
# 從「開頭側」重新打開同一個非 maximal 漏洞（例如 `` ``函數` `` 只有
# 2+1 個反引號、CommonMark 判定沒有 code span，但可回溯的 `` `+ `` 會
# 把 `t` 縮成 1 個反引號硬湊出一個 span）。possessive 量詞禁止回溯，
# 一旦吃下整個 maximal run 就不再吐回去，開頭側因此也維持 maximal。
_CODE_SPAN = re.compile(r"(?<!`)(?P<t>`++)(?:(?!\n[ \t]*\n)[\s\S])*?(?<!`)(?P=t)(?!`)")


def load(path: str | None = None) -> dict[str, str]:
    return json.loads(Path(path or _DEFAULT).read_text(encoding="utf-8"))


def _protected_mask(body: str) -> list[bool]:
    """逐字元遮罩：True 代表這個字元不可被術語替換碰到。

    保護來源有兩個，缺一不可：
    - fence / 縮排 code block（anchors.code_lines()，行級，區塊結構的
      真相來源在 anchors.py，這裡不重刻）。
    - inline code span（_CODE_SPAN，字元級，允許跨行）。

    若一個 code span 匹配的起點已經落在 fence/縮排保護區內，就跳過這個
    匹配 —— 避免用 inline span 的規則去覆寫/延伸區塊結構已經界定好的
    範圍。
    """
    n = len(body)
    protected = [False] * n
    code_line_set = anchors.code_lines(body)
    if code_line_set:
        offset = 0
        for i, line in enumerate(body.splitlines(keepends=True)):
            if i in code_line_set:
                for j in range(offset, offset + len(line)):
                    protected[j] = True
            offset += len(line)
    for m in _CODE_SPAN.finditer(body):
        start, end = m.span()
        if protected[start]:
            continue
        for j in range(start, end):
            protected[j] = True
    return protected


def _segments(body: str, mask: list[bool]):
    """回傳 (is_protected, segment) 序列，segment 依遮罩值切成連續區段。"""
    n = len(body)
    i = 0
    while i < n:
        cur = mask[i]
        j = i
        while j < n and mask[j] == cur:
            j += 1
        yield cur, body[i:j]
        i = j


def enforce(body: str, table: dict[str, str] | None = None) -> str:
    table = table or load()
    mask = _protected_mask(body)
    out = []
    for protected, seg in _segments(body, mask):
        if not protected:
            for bad, good in table.items():
                seg = seg.replace(bad, good)
        out.append(seg)
    return "".join(out)


def scan(body: str, table: dict[str, str] | None = None) -> dict[str, int]:
    table = table or load()
    mask = _protected_mask(body)
    counts: Counter[str] = Counter()
    for protected, seg in _segments(body, mask):
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
