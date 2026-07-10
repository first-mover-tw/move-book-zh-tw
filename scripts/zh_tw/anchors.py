"""標題 anchor 的解析與注入。

anchor 是已發佈的 URL，是對外契約。既有的 {#id} 一律沿用，永不重算。
"""

import re

_ANCHOR = re.compile(r"\s*\{#([A-Za-z0-9_-]+)\}\s*$")
_INLINE_CODE = re.compile(r"`([^`]+)`")
_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_FENCE = re.compile(r"^(`{3,}|~{3,})(.*)$")


def _scan(body: str) -> list[tuple[int, str | None, bool]]:
    """單趟掃描，同時追蹤 fence 與 HTML comment 巢狀狀態。

    兩種狀態互斥、且「先進去的那個優先」：目前若在 fence 裡，`<!--` 只是
    程式碼文字；目前若在 comment 裡，fence marker 只是註解文字。任何一方
    都不會在對方內部被觸發或提前關閉。

    回傳每一行的 (line_no_0based, visible_text_or_None, is_fence_delim)：
    - visible_text 為 None 表示這一行完全被 fence 或 comment 吃掉，不可見。
    - is_fence_delim 表示這一行是「comment 之外」的 fence 開/關界線（用於
      fence_lines()）；comment 內部的 fence marker 一律不計。
    """
    result: list[tuple[int, str | None, bool]] = []
    state = "normal"  # normal | fence | comment
    fence_char = ""
    fence_len = 0

    for i, line in enumerate(body.splitlines()):
        if state == "fence":
            stripped = line.strip()
            m = _FENCE.match(stripped)
            closes = bool(
                m
                and m.group(1)[0] == fence_char
                and len(m.group(1)) >= fence_len
                and m.group(2).strip() == ""
            )
            if closes:
                state = "normal"
                result.append((i, None, True))
            else:
                result.append((i, None, False))
            continue

        if state == "comment":
            idx = line.find("-->")
            if idx == -1:
                result.append((i, None, False))
                continue
            # comment 在這一行關閉；剩餘部分當成普通內容繼續處理
            state = "normal"
            line = line[idx + 3:]

        # state == "normal"（可能是 comment 剛關閉後的剩餘片段）
        ls = line.lstrip()
        mf = _FENCE.match(ls)
        if mf:
            state = "fence"
            fence_char = mf.group(1)[0]
            fence_len = len(mf.group(1))
            result.append((i, None, True))
            continue

        cidx = line.find("<!--")
        if cidx == -1:
            result.append((i, line, False))
            continue

        eidx = line.find("-->", cidx + 4)
        if eidx != -1:
            # 整段 inline comment 在同一行內開關，只把中間挖掉
            visible = line[:cidx] + line[eidx + 3:]
            result.append((i, visible, False))
            continue

        # comment 在這一行開啟，但沒在同一行關閉
        state = "comment"
        result.append((i, line[:cidx], False))

    return result


def visible_lines(body: str) -> list[tuple[int, str]]:
    """回傳不在 fence、也不在 HTML comment 內的所有行。

    給 headings() 自己用，也給其他模組（Task 6 依 H2 切 chunk、Task 8 數
    code fence）重用，避免每個模組各自重新實作一次 fence/comment 掃描器。
    """
    return [(i, text) for i, text, _ in _scan(body) if text is not None]


def fence_lines(body: str) -> int:
    """回傳「不在 HTML comment 內」的 fence 界線（開或關）行數。

    給 Task 8 驗證 code fence 數量用。位於 comment 內部的 fence marker（例如
    被整段註解掉的範例程式碼）不計入 —— 它們從未真的界定過一個 fence。
    """
    return sum(1 for _, _, is_delim in _scan(body) if is_delim)


def headings(body: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for _, text in visible_lines(body):
        m = _HEADING.match(text)
        if m:
            out.append((len(m.group(1)), m.group(2)))
    return out


def slugify(heading: str) -> str:
    text = _ANCHOR.sub("", heading)
    text = _LINK.sub(r"\1", text)
    text = _INLINE_CODE.sub(r"\1", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", "-", text).strip("-")


def slugify_all(texts: list[str]) -> list[str]:
    """依 github-slugger 規則去重：每個候選 slug 都要對照「已產出集合」，
    衝突就一直遞增到找到空位為止（而不是各自獨立計數），避免產生的
    `-N` 尾碼撞上另一個字面上就長那樣的 slug。
    """
    used: set[str] = set()
    out: list[str] = []
    for t in texts:
        base = slugify(t)
        candidate = base
        n = 1
        while candidate in used:
            candidate = f"{base}-{n}"
            n += 1
        used.add(candidate)
        out.append(candidate)
    return out


def existing_anchor(heading: str) -> str | None:
    m = _ANCHOR.search(heading)
    return m.group(1) if m else None
