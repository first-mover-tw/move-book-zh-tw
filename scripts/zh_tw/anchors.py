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


def code_lines(body: str) -> frozenset[int]:
    """0-based 行號集合，屬於 fence 或縮排 code_block 的行。

    刻意不含 html_block：HTML 註解不是程式碼——草稿裡被註解掉的中文
    敘述仍應套用術語正規化，一旦之後取消註解，用詞就必須已經是對的。
    這正是為什麼這個函式不能只是 `visible_lines()` 的補集（visible_lines
    連 html_block 也一併隱藏）。
    """
    _require_body(body)
    hidden: set[int] = set()
    for t in _tokens(body):
        if t.type in ("fence", "code_block") and t.map:
            hidden.update(range(t.map[0], t.map[1]))
    return frozenset(hidden)


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


def slugify_all(
    texts: list[str], reserved: "set[str] | frozenset[str]" = frozenset()
) -> list[str]:
    """依 github-slugger 規則去重：每個候選 slug 都要對照「已產出集合」，
    衝突就一直遞增到找到空位為止（而不是各自獨立計數），避免產生的
    `-N` 尾碼撞上另一個字面上就長那樣的 slug。

    `reserved` 讓呼叫端預先佔位既有的 id（例如 carried-forward anchor），
    使衍生出來的 slug 不會撞上一個它完全看不到的命名空間。
    """
    used: set[str] = set(reserved)
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


class HeadingMismatch(Exception):
    """中文與英文的標題數量不符，通常代表翻譯被截斷。"""


class DuplicateAnchor(Exception):
    """兩個標題最終算出同一個 anchor id——防禦性守衛，理論上不該發生。"""


class NestedHeading(Exception):
    """標題巢狀在 blockquote 或 list item 裡——inject() 只會輸出頂層 ATX 標題，
    硬寫會把容器前綴（`>`、`-`）整行吃掉，讓標題被拉升到頂層。無法正確轉換的
    檔案不寫出去，直接炸掉。"""


def _nested_heading_texts(body: str) -> list[str]:
    """回傳所有巢狀（level > 0）標題的原始文字，供錯誤訊息使用。"""
    toks = _tokens(body)
    return [
        toks[i + 1].content
        for i, t in enumerate(toks)
        if t.type == "heading_open" and t.level > 0
    ]


def _anchor_map(body: str) -> dict[int, str]:
    """以標題序號為鍵，取出既有的 anchor id。"""
    return {
        i: aid
        for i, (_, text) in enumerate(headings(body))
        if (aid := existing_anchor(text)) is not None
    }


def _heading_spans(body: str) -> list[tuple[int, int, int, str]]:
    """(起始行, 結束行(不含), 層級, markup)。markup 為 `=`/`-` 代表 setext
    標題(佔兩行：文字行 + 底線行)，其餘(`#`...`######`)代表 ATX。
    行號與層級的真相來源同樣是 markdown-it-py 的 token，不另起掃描。
    """
    return [
        (t.map[0], t.map[1], int(t.tag[1]), t.markup)
        for t in _tokens(body)
        if t.type == "heading_open" and t.map
    ]


def _line_ending(line: str) -> str:
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    return ""


def _identity_carry(
    prev_zh_body: str, prev_en_body: str, en_texts: list[str]
) -> tuple[dict[int, str], list[str]]:
    """依英文標題文字身分，把 prev_zh 的既有 anchor 對應到新標題序號。

    回傳 (carried: 新標題序號 -> anchor id, notes: 人類可讀的沿用/退場說明)。
    絕不做 by-index 的猜測性 fallback —— 缺少 prev_en_body 就什麼都不沿用。
    """
    notes: list[str] = []
    if not prev_zh_body:
        return {}, notes

    prev_anchor_map = _anchor_map(prev_zh_body)

    if not prev_en_body:
        if prev_anchor_map:
            notes.append(
                f"no prev_en_body given; {len(prev_anchor_map)} existing anchors "
                "were not carried forward"
            )
        return {}, notes

    prev_zh_h = headings(prev_zh_body)
    prev_en_h = headings(prev_en_body)
    if len(prev_zh_h) != len(prev_en_h):
        notes.append(
            f"prev heading count mismatch (zh={len(prev_zh_h)}, en={len(prev_en_h)}); "
            "nothing carried forward"
        )
        return {}, notes

    prev_en_texts = [t for _, t in prev_en_h]

    matched_prev_idx: set[int] = set()
    carried: dict[int, str] = {}
    for j, u_text in enumerate(en_texts):
        found = None
        for i, t in enumerate(prev_en_texts):
            if i in matched_prev_idx:
                continue
            if t == u_text:
                found = i
                break
        if found is None:
            continue
        matched_prev_idx.add(found)
        aid = prev_anchor_map.get(found)
        if aid is not None:
            carried[j] = aid

    for i, aid in prev_anchor_map.items():
        if i not in matched_prev_idx:
            notes.append(
                f"anchor {{#{aid}}} retired: heading '{prev_en_texts[i]}' "
                "no longer exists in the English source"
            )

    return carried, notes


def inject_report(
    zh_body: str,
    en_body: str,
    prev_zh_body: str = "",
    prev_en_body: str = "",
) -> tuple[str, list[str]]:
    nested = _nested_heading_texts(zh_body) + _nested_heading_texts(en_body)
    if nested:
        raise NestedHeading(
            f"標題巢狀在 blockquote 或 list item 裡，無法安全注入 anchor: {nested!r}"
        )

    zh_h, en_h = headings(zh_body), headings(en_body)
    if len(zh_h) != len(en_h):
        raise HeadingMismatch(
            f"標題數不符: 中文 {len(zh_h)}, 英文 {len(en_h)}"
        )

    carried, notes = _identity_carry(
        prev_zh_body, prev_en_body, [t for _, t in en_h]
    )
    current = _anchor_map(zh_body)

    # tier 1（zh_body 裡已有的 anchor）優先於 tier 2（依身分沿用自舊版中文檔）。
    fixed: dict[int, str] = {}
    for i in range(len(en_h)):
        aid = current.get(i)
        if aid is None:
            aid = carried.get(i)
        if aid is not None:
            fixed[i] = aid

    # 衍生（tier 3）前，先把 tier 1/2 已經佔用的 id 保留起來，
    # 讓 slugify_all 在它們看不到的命名空間裡也不會撞名。
    reserved = set(fixed.values())
    derive_idx = [i for i in range(len(en_h)) if i not in fixed]
    derived = slugify_all([en_h[i][1] for i in derive_idx], reserved=reserved)
    for i, aid in zip(derive_idx, derived):
        fixed[i] = aid

    wanted = [fixed[i] for i in range(len(en_h))]

    # 防禦性守衛：就算前面的邏輯都對，也不允許重複的 anchor 靜默流出去
    # （例如 tier 1 本身在 zh_body 裡就已經有兩個標題共用同一個 id）。
    seen: set[str] = set()
    for aid in wanted:
        if aid in seen:
            raise DuplicateAnchor(f"重複的 anchor id: {aid!r}")
        seen.add(aid)

    # 行號與層級一律取自共用的區塊解析器，不自己掃 fence。
    spans = _heading_spans(zh_body)
    at_line = {start: (idx, level, end, markup) for idx, (start, end, level, markup) in enumerate(spans)}
    # setext 標題的底線行整行丟棄（正規化成 ATX 後底線就不該存在）。
    setext_underline_lines = {
        end - 1 for _, end, _, markup in spans if markup in ("=", "-")
    }

    lines = zh_body.splitlines(keepends=True)
    out = []
    for i, line in enumerate(lines):
        if i in setext_underline_lines:
            continue
        if i not in at_line:
            out.append(line)
            continue
        idx, level, _, _ = at_line[i]
        text = _ANCHOR.sub("", zh_h[idx][1])
        nl = _line_ending(line)
        out.append(f"{'#' * level} {text} {{#{wanted[idx]}}}{nl}")
    return "".join(out), notes


def inject(
    zh_body: str,
    en_body: str,
    prev_zh_body: str = "",
    prev_en_body: str = "",
) -> str:
    body, _notes = inject_report(zh_body, en_body, prev_zh_body, prev_en_body)
    return body
