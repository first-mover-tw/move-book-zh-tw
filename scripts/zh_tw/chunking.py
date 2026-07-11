"""按 H2 語意邊界切段，避免整檔送模型時輸出 token 用盡而靜默截斷。

切段邊界一律取自 anchors.heading_lines()，不得自己掃 fence —— 見 Global Constraints。
"""

from . import anchors


_MAX_HEADING_LEVEL = 6


def chunk(body: str, max_lines: int = 250) -> list[str]:
    lines = body.splitlines(keepends=True)
    if len(lines) <= max_lines:
        return [body]
    return _split(body, max_lines, level=2)


def _split(body: str, max_lines: int, level: int) -> list[str]:
    """遞迴切段：先在 `level` 層級的標題切一刀，任何切完仍超過 max_lines
    的片段，再往下一層標題遞迴切。層級用完（無更深標題可切）就原樣送出。
    """
    lines = body.splitlines(keepends=True)
    if len(lines) <= max_lines:
        return [body]
    if level > _MAX_HEADING_LEVEL:
        return [body]

    starts = [i for i, lv in anchors.heading_lines(body) if lv == level]
    if not starts:
        return _split(body, max_lines, level + 1)

    bounds = [0, *starts, len(lines)]
    seen, out = set(), []
    for a, b in zip(bounds, bounds[1:]):
        if a == b or (a, b) in seen:
            continue
        seen.add((a, b))
        out.append("".join(lines[a:b]))

    result: list[str] = []
    for c in out:
        if c:
            result.extend(_split(c, max_lines, level + 1))
    return result


def join(chunks: list[str]) -> str:
    return "".join(chunks)
