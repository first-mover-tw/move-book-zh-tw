"""按 H2 語意邊界切段，避免整檔送模型時輸出 token 用盡而靜默截斷。

切段邊界一律取自 anchors.heading_lines()，不得自己掃 fence —— 見 Global Constraints。
"""

from . import anchors


def chunk(body: str, max_lines: int = 250) -> list[str]:
    lines = body.splitlines(keepends=True)
    if len(lines) <= max_lines:
        return [body]

    starts = [i for i, level in anchors.heading_lines(body) if level == 2]

    if not starts:
        return [body]

    bounds = [0, *starts, len(lines)]
    seen, out = set(), []
    for a, b in zip(bounds, bounds[1:]):
        if a == b or (a, b) in seen:
            continue
        seen.add((a, b))
        out.append("".join(lines[a:b]))
    return [c for c in out if c]


def join(chunks: list[str]) -> str:
    return "".join(chunks)
