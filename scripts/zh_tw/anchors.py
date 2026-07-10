"""標題 anchor 的解析與注入。

anchor 是已發佈的 URL，是對外契約。既有的 {#id} 一律沿用，永不重算。
"""

import re

_ANCHOR = re.compile(r"\s*\{#([A-Za-z0-9_-]+)\}\s*$")
_INLINE_CODE = re.compile(r"`([^`]+)`")
_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")


def headings(body: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = _HEADING.match(line)
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
    seen: dict[str, int] = {}
    out: list[str] = []
    for t in texts:
        base = slugify(t)
        if base in seen:
            seen[base] += 1
            out.append(f"{base}-{seen[base]}")
        else:
            seen[base] = 0
            out.append(base)
    return out


def existing_anchor(heading: str) -> str | None:
    m = _ANCHOR.search(heading)
    return m.group(1) if m else None
