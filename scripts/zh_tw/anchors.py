"""標題 anchor 的解析與注入。

anchor 是已發佈的 URL，是對外契約。既有的 {#id} 一律沿用，永不重算。

區塊結構(標題、fence、HTML block、縮排程式碼)一律交給 markdown-it-py 判定。
手刻的 fence 切換迴圈連續三輪出現 CommonMark 規格落差，且失效簽名都是
「假陽性 + 假陰性互相抵消」——  數量相符的守衛因此全部變綠。本模組是全專案
唯一的 markdown 區塊真相來源；其他模組必須呼叫這裡的 helper。
"""

import re

from markdown_it import MarkdownIt

from . import frontmatter

_MD = MarkdownIt("commonmark")

_ANCHOR = re.compile(r"\s*\{#([A-Za-z0-9_-]+)\}\s*$")
_INLINE_CODE = re.compile(r"`([^`]+)`")
_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_FENCE_MARK = re.compile(r"^ {0,3}(`{3,}|~{3,})")

_OPAQUE = ("fence", "code_block", "html_block")


class FrontmatterPassedIn(ValueError):
    """呼叫者傳了完整文件而非 body。"""


def _require_body(text: str) -> str:
    """CommonMark 會把 `---\ndescription: x\n---` 解析成 setext 標題,憑空多一個 h2。"""
    meta, _ = frontmatter.split(text)
    if meta:
        raise FrontmatterPassedIn("headings/visible_lines/fence_lines 需要 body，不是完整文件")
    return text


def _tokens(body: str):
    return _MD.parse(body)


def heading_lines(body: str) -> list[tuple[int, int]]:
    """(0-based 行號, 標題層級)，只含實際會渲染的標題。"""
    _require_body(body)
    return [
        (t.map[0], int(t.tag[1]))
        for t in _tokens(body)
        if t.type == "heading_open" and t.map
    ]


def headings(body: str) -> list[tuple[int, str]]:
    """(層級, 標題原始文字)。文字保留 inline code 與 {#anchor}。"""
    _require_body(body)
    toks = _tokens(body)
    return [
        (int(t.tag[1]), toks[i + 1].content)
        for i, t in enumerate(toks)
        if t.type == "heading_open"
    ]


def visible_lines(body: str) -> list[tuple[int, str]]:
    """不在 fence / HTML block / 縮排程式碼內的行，附 0-based 行號。"""
    _require_body(body)
    hidden: set[int] = set()
    for t in _tokens(body):
        if t.type in _OPAQUE and t.map:
            hidden.update(range(t.map[0], t.map[1]))
    return [(i, l) for i, l in enumerate(body.splitlines()) if i not in hidden]


def fence_lines(body: str) -> int:
    """實際會渲染的 fence 分隔行數(不含 HTML 註解內的 fence)。"""
    _require_body(body)
    lines = body.splitlines()
    return sum(
        1
        for t in _tokens(body)
        if t.type == "fence" and t.map
        for l in lines[t.map[0]:t.map[1]]
        if _FENCE_MARK.match(l)
    )


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
