"""編排：分層 -> 翻譯 -> 注入 anchor -> 強制術語 -> 驗證 -> 寫檔。

驗證失敗一律 raise，絕不寫檔。
"""

import json
import re
import subprocess

import commonmark
from pathlib import Path

from . import anchors, chunking, frontmatter, glossary, manifest, sidebar, validate
from .backends import base
from .pipeline_patterns import URLISH as _URLISH
from .pipeline_patterns import UNDERSCORE_EM as _UNDERSCORE_EM

MERGE_BASE = "f2c0a93e1a0422078d3d051e4410ac3edc612016"
FRONTMATTER_ONLY_DELTA = 6
CHUNK_MAX_LINES = 250


def _show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def _prev_en(path: str, m: dict[str, str]) -> str:
    """取回這個中文檔當初賴以翻譯的英文原檔內容。

    manifest 記的是英文 blob SHA。31 筆 provenance 曾經斷掉（Task 13 修復）；
    仍然取不到時退回 merge-base 的同路徑內容。兩者皆失敗則回傳空字串，
    inject 會因此不沿用任何 anchor —— 這是安全的降級，位置猜測不是。
    """
    sha = m.get(path)
    if sha:
        r = subprocess.run(["git", "cat-file", "-p", sha], capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout
    return _show(MERGE_BASE, path) or ""


def _delta_lines(old_sha: str, new_sha: str) -> int:
    # 同一 blob 的 delta 是 0；`git diff --numstat` 對它輸出空字串，
    # 不擋在這裡會掉進下面的 fail-closed 哨兵，把已 heal 的檔案誤判 B。
    if old_sha == new_sha:
        return 0
    r = subprocess.run(
        ["git", "diff", "--numstat", old_sha, new_sha], capture_output=True, text=True
    )
    parts = r.stdout.split()
    return int(parts[0]) + int(parts[1]) if len(parts) >= 2 else 10_000


def tier(path: str, en_ref: str = "english-main") -> str:
    """A 層的前提是中文內文與其英文來源結構一致；不通過者強制降級 B 層。"""
    m = manifest.load()
    new_sha = manifest.blob_sha(en_ref, path)
    old_sha = m.get(path)
    zh = _show("HEAD", path)
    if zh is None or new_sha is None or old_sha is None:
        return "B"

    # provenance 損壞（blob 不在 repo）→ 以 merge-base 為代理
    if subprocess.run(["git", "cat-file", "-e", old_sha], capture_output=True).returncode:
        old_sha = manifest.blob_sha(MERGE_BASE, path)
        if old_sha is None:
            return "B"

    if _delta_lines(old_sha, new_sha) > FRONTMATTER_ONLY_DELTA:
        return "B"

    en_old = _show(MERGE_BASE, path)
    # spec §五：分層只看 gate 1、2。用全量 check_file 會把「description 未翻」
    # 這種 backfill 本身要修的缺陷當成降級理由（實測誤降 30 檔）。
    if en_old is None or validate.check_structure(zh, en_old):
        return "B"  # 結構驗證未過（例：reference/variables.md）
    return "A"


CHUNK_RETRIES = 3


def _translate_chunk(chunk_text: str, backend: base.Backend) -> str:
    """單一 chunk 翻譯，標題層級序列不符就地重試（PR 3 診斷：sonnet 對長檔
    穩定吞小節標題，變更 chunk 尺寸與整檔重跑都救不了；chunk 級重試把失效
    定位到小範圍）。重試耗盡仍不符 → 保留最後一次輸出交給 gate 1 整檔擋，
    fail-closed 不變 —— 這裡是自動修復路徑，不是放寬。"""
    # 驗 gate 1+2 兩個維度：只驗標題會漏「掉收尾 ``` 的 chunk」——它自身
    # 標題照過，join 後卻把下一個 chunk 的標題吞進未閉合 fence（L7 實錄：
    # variables.md 21→19，單獨翻每個 chunk 都正常）。
    want = [lv for lv, _ in anchors.headings(chunk_text)]
    want_fences = anchors.fence_lines(chunk_text)
    out = ""
    for _ in range(CHUNK_RETRIES):
        out = backend.translate(chunk_text)
        try:
            ok = (
                [lv for lv, _ in anchors.headings(out)] == want
                and anchors.fence_lines(out) == want_fences
            )
        except anchors.FrontmatterPassedIn:
            # backend 幻覺出 YAML frontmatter —— 正是重試該吸收的垃圾輸出，
            # 不能讓例外逃出去炸掉整檔（review F1）。
            ok = False
        if ok:
            return out
    return out


def translate_body(en_text: str, backend: base.Backend, max_lines: int = CHUNK_MAX_LINES) -> str:
    en_meta, en_body = frontmatter.split(en_text)
    zh_chunks = [_translate_chunk(c, backend) for c in chunking.chunk(en_body, max_lines)]
    zh_body = chunking.join(zh_chunks)

    zh_meta = dict(en_meta)
    for key in frontmatter.TRANSLATABLE_KEYS & set(en_meta):
        if isinstance(en_meta[key], str):
            # enforce 與 check_frontmatter 的值掃描同進退：backend 翻出違禁詞
            # 是決定性可修的，炸掉會把 B 路徑變成無自動出路的死鎖。
            zh_meta[key] = glossary.enforce(backend.translate(en_meta[key], kind="text").strip())
    return frontmatter.join(zh_meta, zh_body)


def assemble(
    en_text: str,
    prev_zh_text: str,
    prev_en_text: str,
    backend: base.Backend,
    max_lines: int = CHUNK_MAX_LINES,
) -> str:
    """prev_en_text 是這個中文檔當初翻譯所依據的英文原檔。

    沒有它，anchors.inject 只能退回「不沿用任何 anchor」；**絕不可**退回位置配對。
    上游 #223 改動了 19/35 個含 anchor 檔案的標題序列，位置配對會把 anchor 靜默
    貼到錯誤的標題上，而 gate 6 的集合差看不出來（spec D10）。
    """
    translated = translate_body(en_text, backend, max_lines)
    zh_meta, zh_body = frontmatter.split(translated)
    _, en_body = frontmatter.split(en_text)
    _, prev_zh_body = frontmatter.split(prev_zh_text) if prev_zh_text else ({}, "")
    _, prev_en_body = frontmatter.split(prev_en_text) if prev_en_text else ({}, "")

    # 標題修復在 anchor 注入之前（注入以最終標題文字為準）。
    zh_body = _repair_headings(zh_body, en_body, backend)
    zh_body = _repair_fence_comments(zh_body, backend)
    zh_body = _repair_inpage_links(zh_body, en_body)
    zh_body = _repair_cjk_emphasis(zh_body)
    zh_body = _repair_ol_numbering(zh_body)
    # 拼接完成後才注入 anchor：切段後每段的標題序列只是全域序列的子區間。
    zh_body, notes = anchors.inject_report(zh_body, en_body, prev_zh_body, prev_en_body)
    zh_body = glossary.enforce(zh_body)
    out = frontmatter.join(zh_meta, zh_body)

    errs = validate.check_file(out, en_text, prev_zh_text, prev_en_text)
    # gate 9 只掛這裡（新翻譯），不進 check_file：A 層的 body 是 legacy
    # 舊譯文（110/147 檔無後綴），掛進去會整批誤擋 —— 見 gate 9 docstring。
    errs += validate.check_heading_suffix(out, en_text)
    if errs:
        raise validate.ValidationError("; ".join(errs))
    for n in notes:
        print(f"  note: {n}")  # anchor 退役等資訊，警告但不阻斷
    return out


_TRAILING_PAREN = re.compile(r"\s*[（(]([^()（）]*)[)）]\s*$")


def _repair_headings(zh_body: str, en_body: str, backend: base.Backend) -> str:
    """gate 9 缺陷的修復 pass（enforce 與 gate 同進退：gate 擋得住的、backend
    又常犯的缺陷，必須有自動修復路徑，否則是結構性死鎖）。

    - 已翻譯只缺「(English)」後綴 → 決定性補上（Model vs Code 分工：格式化
      不指望 LLM）；先剝掉結尾與英文標題重複的括號組，避免疊床架屋。
    - verbatim 未翻 → 單標題重譯（kind="heading"，短輸入可靠得多）。
    - 修復候選仍過不了 heading_suffix_error 就保留原樣，交給 gate 9 擋。
    - 標題數不符不修（by-index 配對不成立），交給 gate 1。
    - 判定與 gate 9 共用 validate.heading_suffix_error（單一權威實作）。
    """
    zh_h = anchors.headings(zh_body)
    en_h = anchors.headings(en_body)
    spans = anchors._heading_spans(zh_body)
    if len(zh_h) != len(en_h) or len(spans) != len(zh_h):
        return zh_body

    lines = zh_body.splitlines(keepends=True)
    for (start, end, level, markup), (_, zh_t), (_, en_t) in zip(spans, zh_h, en_h):
        if not markup.startswith("#"):
            continue  # setext 標題（兩行）不在此修，交給 gate
        if end - start != 1:
            continue
        # 巢狀（blockquote/list 內）標題不修：整行替換會吃掉容器前綴，
        # 讓 inject 的 NestedHeading fail-closed 失效（review F2）。
        if not lines[start].lstrip().startswith("#"):
            continue
        # 與判定（heading_suffix_error 內部）同一前處理：剝 {#anchor}。
        # backend 幻覺出的 anchor 在此丟棄 —— inject 才是 anchor 的唯一
        # 權威來源（review F1：不剝會把 anchor 字面量嵌進標題中段）。
        zh_t = validate.ANCHOR_SUFFIX.sub("", zh_t)
        en_t = validate.ANCHOR_SUFFIX.sub("", en_t)
        if validate.heading_suffix_error(zh_t, en_t) is None:
            continue
        en_clean = en_t.strip()
        if validate.CJK.search(zh_t):
            base_txt = zh_t.strip()
            # 剝掉結尾與英文標題重複的括號組（「… (Tags and Releases) (Git)」）
            while (m := _TRAILING_PAREN.search(base_txt)):
                inner = m.group(1).strip()
                stripped = base_txt[: m.start()].rstrip()
                if inner and stripped and inner.lower() in en_clean.lower():
                    base_txt = stripped
                else:
                    break
            candidate = f"{base_txt} ({en_clean})"
        else:
            # 單標題重譯間歇性 verbatim/垃圾（實測 'Abort' 第一次回幻覺、
            # 第二次即正確）—— 就地驗證重試，與 chunk 重試同哲學。
            candidate = ""
            for _ in range(CHUNK_RETRIES):
                candidate = backend.translate(en_clean, kind="heading").strip()
                if validate.heading_suffix_error(candidate, en_clean) is None:
                    break
        if candidate and validate.heading_suffix_error(candidate, en_clean) is None:
            ending = anchors._line_ending(lines[start])
            lines[start] = f"{'#' * level} {candidate}{ending}"
    return "".join(lines)


# `#(?!\[)`：`#[test]` 是 Move 屬性不是註解，送翻譯會把屬性行改壞（編譯
# 層級損毀）；屬性行的行內 // 註解由 chunk 翻譯本身負責。
_CODE_COMMENT = re.compile(r"^(\s*(?://+|#(?!\[))\s*)(.+?)(\s*)$")
_COMMENT_SKIP = re.compile(r"ANCHOR|highlight|prettier-ignore|noqa|docs::")
_LATIN_PROSE = re.compile(r"[a-z]{2,}")

_COMMENT_PROMPT = (
    "以下是程式碼註解的編號清單。把每一行翻譯成台灣繁體中文"
    "（保留行內 code 與專有名詞），輸出相同編號的清單，一行對一行，"
    "不要增減行數，不要任何解釋。\n"
    f"{glossary.prompt_rules()}"
)


def _repair_fence_comments(zh_body: str, backend: base.Backend) -> str:
    """code 內英文散文註解的批次補翻（PR 3 實測 sonnet 對 fence 註解
    186/213 未翻，語料慣例是翻）。與標題修復同理：LLM 系統性忽略的指令
    用專用小呼叫補 —— 一檔一個編號清單呼叫（沿用 sidebar 的成熟模式，
    kind="raw" 不外包 prompt）。

    - 只動 anchors.code_lines 認定的 code 行（單一權威 parser，散文裡的
      «//» 不會誤傷）；指令行（ANCHOR/highlight/…）與已含 CJK 的跳過。
    - 回覆行缺 CJK（沒翻或亂答）→ 該行保留原文，fail-open 到「維持現狀」。
    - 替換只動註解文字，縮排、註解符號、行數、fence 數都不變。
    """
    lines = zh_body.splitlines(keepends=True)
    code = anchors.code_lines(zh_body)
    todo: list[tuple[int, str, str, str]] = []  # (行號, prefix, text, trailing)
    for i in sorted(code):
        if i >= len(lines):
            continue
        m = _CODE_COMMENT.match(lines[i].rstrip("\r\n"))
        if not m:
            continue
        prefix, text, trail = m.groups()
        if _COMMENT_SKIP.search(text) or validate.CJK.search(text):
            continue
        if not _LATIN_PROSE.search(text):
            continue
        todo.append((i, prefix, text, trail))
    if not todo:
        return zh_body

    numbered = "\n".join(f"{n + 1}. {t}" for n, (_, _, t, _) in enumerate(todo))
    raw = backend.translate(f"{_COMMENT_PROMPT}\n\n{numbered}", kind="raw")
    replies: dict[int, str] = {}
    for line in raw.splitlines():
        m = re.match(r"^\s*(\d+)[.)]\s*(.+?)\s*$", line)  # \s*：容忍「1.譯文」無空格
        if m:
            replies[int(m.group(1))] = m.group(2)

    # 完整性守衛（review F2）：backend 合併重複行重新編號時，第 i 條會拿到
    # 第 i+1 條的譯文 —— fence 內的靜默內容損毀，gate 7/8 遮蔽 code 看不到。
    # 編號集合不是恰好 {1..n} 就整個 pass 放棄，fail-open 到 no-op。
    if set(replies) != set(range(1, len(todo) + 1)):
        return zh_body

    for n, (i, prefix, text, trail) in enumerate(todo, start=1):
        got = replies[n]
        if not validate.CJK.search(got) or validate.simplified_chars(got):
            continue  # 沒翻、亂答或帶簡體（gate 8 遮蔽 code，必須在這裡擋）：保留原文
        ending = anchors._line_ending(lines[i])
        lines[i] = f"{prefix}{glossary.enforce(got)}{trail}{ending}"
    return "".join(lines)


_INPAGE_LINK = re.compile(r"\]\(#([^)#\s]+)\)")


_IDENTISH = re.compile(r"[A-Za-z0-9_]")


def _repair_cjk_emphasis(zh_body: str) -> str:
    """把「因為與 CJK 相鄰而渲染不出來」的 `_..._` 改寫成 `*...*`。

    CommonMark 不允許 `_` 在詞內開合（避免 snake_case 被誤判成強調），而
    CJK 算 word char。於是 `進行_升級_：` 產出的是**合法 Markdown、卻完全
    沒有 <em>** —— 強調靜靜消失。PR #22 實測：backend 從 `*文字*` 改用
    `_文字_` 之後，3 個檔的 5 處強調全滅。八道 gate 全是結構／術語檢查，
    prettier 只管格式，這種回歸只有人眼看得到，所以修在產出這一側。

    **逐行 tokenize + 成對決議，不做逐一 regex 配對。** 逐一配對的第一版
    對真實輸入有三種靜默破壞（外部 review 兩輪實測）：連結內含中文的 URL
    被改成星號（404、圖裂）、識別字被拆、`__粗體__` 降級成 `_*粗體*_`；
    而且被跳過的匹配仍會**消耗掉**那個底線，讓下一次配對跨過真正的強調
    邊界（`與_所有權_的關係，也講_物件_模型` → `與_所有權*的關係，也講*物件_`）。
    gate 10 對這些全無覆蓋，因為它們讓 <em> 不減反增。

    排除規則（每一條都對應一個實測過的破壞）：
    - code span / fence：glossary.protected_mask，真相來源不重刻。
    - 連結/圖片 destination、autolink、裸 URL：URLISH。含中文的 URL 只會
      出現在中文譯文裡，而「內容含 CJK」那條過濾對它失效。
    - 緊鄰 ASCII 英數或底線的底線：那是識別字（`tx_context`）或 `__粗體__`
      的外層，不是強調分隔符 —— 直接不算進 token，而不是「跳過匹配」。
    - 一行的分隔符數為奇數：配不成對就整行放棄。寧可漏修讓 gate 10 擋下來
      人工處理，也不要猜一個配對然後靜默改壞。
    - 內容不含 CJK、或本來就渲染得出來：不動，不製造無謂 diff。
    """
    mask = glossary.protected_mask(zh_body)
    for u in _URLISH.finditer(zh_body):
        for i in range(u.start(), u.end()):
            mask[i] = True

    out, pos = [], 0
    line_start = 0
    for line in zh_body.splitlines(keepends=True):
        line_end = line_start + len(line)
        # 這一行的強調分隔符候選：非保護區、且兩側都不是 ASCII 英數/底線
        delims = []
        for i in range(line_start, line_end):
            if zh_body[i] != "_" or mask[i]:
                continue
            before = zh_body[i - 1] if i else ""
            after = zh_body[i + 1] if i + 1 < len(zh_body) else ""
            if _IDENTISH.match(before) or _IDENTISH.match(after):
                continue
            # 兩側皆空白（或行首/行尾）的底線，在 CommonMark 裡既不能當開頭
            # 分隔符（後面不能是空白）也不能當收尾（前面不能是空白）——它是
            # 散文裡的字面底線，最常見的來源就是本書在講 Move 的 `_` 萬用字元。
            # 不排除的話它照樣佔一個 parity 名額，配對又會跨過真正的邊界：
            # `見 _ 標記 和_重點_說明 _ 結束。` → `見 * 標記 和*重點*說明 * 結束。`
            if (not before or before.isspace()) and (not after or after.isspace()):
                continue
            delims.append(i)
        if len(delims) % 2 == 0:
            for a, b in zip(delims[::2], delims[1::2]):
                content = zh_body[a + 1 : b]
                # 內容不得以空白開頭/結尾：`_ x_` / `_x _` 都不是合法強調。
                if (
                    "_" in content
                    or not content
                    or content[0].isspace()
                    or content[-1].isspace()
                    or not validate.CJK.search(content)
                ):
                    continue
                if f"<em>{content}</em>" in commonmark.commonmark(line):
                    continue  # 本來就渲染得出來
                out.append(zh_body[pos:a])
                out.append(f"*{content}*")
                pos = b + 1
        line_start = line_end
    out.append(zh_body[pos:])
    return "".join(out)


# 只認「行首列表標記 + 同一個數字 + 分隔符 + 空白」，且允許數字被強調包住
# （實測的缺陷形態就是 `1.  **1. 文字**`）。判準與 gate 11 一樣是**身分**
# ——標記的數字要等於內文重複的那個數字，才動它。
_OL_DUP = re.compile(r"^(?P<indent>[ \t]*)(?P<n>\d+)(?P<mark>[.)])(?P<sp>[ \t]+)(?P<em>\*{1,2}|_{1,2})?(?P=n)[.、．)）][ \t]+")


def _repair_ol_numbering(zh_body: str) -> str:
    """gate 11 缺陷的修復 pass（enforce 與 gate 同進退，見 _repair_headings）。

    機翻把 markdown 的列表標記 `1.` 又抄進項目內文，讀者看到「1. 1. 前言」
    （2026-09-03 run 33730438417 / PR #24，foreword.md 三項全中）。沒有修復
    路徑的話，gate 11 一擋就是該檔永久寫不出來、每輪人工——那是 gate 6/inject
    那次死鎖的同一個家族。

    決定性刪除重複的那一份（Model vs Code 分工：格式化不指望 LLM）。只刪
    內文側，列表標記保持原樣，強調標記也保留。code fence 內不動。

    **已知不涵蓋**：裸 HTML 寫成的 `<ol><li>1. …</li></ol>`。gate 11 讀的是
    渲染後的 HTML（裸 HTML 也算），這個 pass 認的是行首的 markdown 列表
    標記，兩者範圍不等。6000 例隨機 fuzz 找到的 18 個「gate 紅但修不掉」
    全部落在這一類。backend 翻譯 markdown、不產裸 HTML 列表，所以留給
    gate 擋（fail-closed，同 _repair_headings「修不掉就交給 gate 9」的處置）
    ——不為了消滅殘餘情況去弱化守衛（lessons L5）。
    """
    protected = glossary.protected_mask(zh_body)
    out, pos = [], 0
    for line in zh_body.splitlines(keepends=True):
        end = pos + len(line)
        if not any(protected[pos:end]):
            m = _OL_DUP.match(line)
            if m:
                head = f"{m.group('indent')}{m.group('n')}{m.group('mark')}{m.group('sp')}{m.group('em') or ''}"
                line = head + line[m.end() :]
        out.append(line)
        pos = end
    return "".join(out)


def _repair_inpage_links(zh_body: str, en_body: str) -> str:
    """頁內連結 slug 的決定性修復：模型會把 `](#format)` 翻成 `](#格式-format)`，
    但 anchor 一律衍生自英文標題 slug（visibility.md、bcs.md 兩個 PR 各自
    實測）。與英文原文的頁內連結按出現順序配對、取回英文 slug；順序配對
    的前提是兩邊頁內連結數一致，不一致就不修（fail-open，check_repo 的
    gate 5 會顯形）。code 內的連結經 protected_mask 排除。"""

    def collect(body: str) -> list[tuple[int, int, str]]:
        mask = glossary.protected_mask(body)
        out = []
        for m in _INPAGE_LINK.finditer(body):
            if m.start() < len(mask) and mask[m.start()]:
                continue
            out.append((m.start(1), m.end(1), m.group(1)))
        return out

    zh_links = collect(zh_body)
    en_links = collect(en_body)
    if len(zh_links) != len(en_links) or not zh_links:
        return zh_body
    parts, pos = [], 0
    for (a, b, _), (_, _, en_slug) in zip(zh_links, en_links):
        parts.append(zh_body[pos:a])
        parts.append(en_slug)
        pos = b
    parts.append(zh_body[pos:])
    return "".join(parts)


def rebuild_frontmatter_only(
    en_text: str, zh_text: str, backend: base.Backend, prev_en_text: str = ""
) -> str:
    """A 層：內文原封不動，只接管上游 frontmatter。

    寫檔 gate 只涵蓋本函式生成的部分（結構 + frontmatter）：body 是 legacy
    舊譯文，拿它的既有違禁詞/簡體當否決會讓 A 層檔 hard-fail 且無自動修復
    路徑（body 不重譯、tier 也不會降級）——與 tier 只看 check_structure
    （spec §五）是同一組設計，兩邊一起改才不會死鎖。

    欄位值沿用優先於重算（與 anchors 的 carry-forward 同原則）：英文原文
    未變且既有值已是中文的欄位，沿用舊值（過 glossary.enforce）——第一次
    apply 實測 53 個欄位被白重翻，損失既有審定術語（友元 → 朋友）。舊值
    帶簡體字（無決定性修法）或沿用前提不成立時，退回重翻。"""
    en_meta, _ = frontmatter.split(en_text)
    zh_meta_old, zh_body = frontmatter.split(zh_text)
    prev_en_meta, _ = frontmatter.split(prev_en_text) if prev_en_text else ({}, "")
    zh_meta = dict(en_meta)
    for key in frontmatter.TRANSLATABLE_KEYS & set(en_meta):
        if not isinstance(en_meta[key], str):
            continue
        old = zh_meta_old.get(key)
        if (
            prev_en_meta.get(key) == en_meta[key]
            and isinstance(old, str)
            and validate._CJK.search(old)
        ):
            carried = glossary.enforce(old)
            if not validate.simplified_chars(carried) and not glossary.scan(carried):
                zh_meta[key] = carried
                continue
        zh_meta[key] = glossary.enforce(backend.translate(en_meta[key], kind="text").strip())
    out = frontmatter.join(zh_meta, zh_body)
    errs = validate.check_structure(out, en_text) + validate.check_frontmatter(out, en_text)
    if errs:
        raise validate.ValidationError("; ".join(errs))
    return out


def _append_result(
    result_path: str, ok: int, touched: set[str], failed: dict[str, list[str]]
) -> None:
    """把本次執行的成果自報成一行 JSON。

    存在的理由：translate workflow 需要知道「本輪有沒有進展」，而它唯一能看到的
    是 git 與檔案系統的狀態。那是影子不是本體 —— tier A 的產出可以與磁碟
    byte-identical，此時工作區零 diff，但 manifest 的 provenance 更新是真實成果；
    反過來，prettier 對既有髒檔的格式改動與 `_save_manifest_updates` 的正規化
    寫入都能在零翻譯成功時偽造出 diff。三輪 review 各在這條推論上抓到一個
    blocker，失效形式一律是「job 全綠但管線靜默停擺」。ok 與 touched 是本體，
    直接報出去，workflow 就不必推論（lessons L2）。

    **append 不是覆寫**：xargs 在清單超過 ARG_MAX 時會把同一批拆成多次呼叫，
    覆寫會讓最後一批洗掉前面幾批的成果。
    """
    # touched 才是「落盤了幾檔」的本體；ok 是「產出了幾份譯文字串」，
    # dry-run 下也會累加，兩者只在 apply 下恰好相等。消費端（CI）要判進展
    # 一律讀 touched，別讀 ok —— 這條等價關係是外部不變式，不是型別保證。
    # failed 連錯誤訊息一起留（sorted(dict) 只會取到 key），供 post-mortem。
    line = json.dumps(
        {"ok": ok, "touched": sorted(touched), "failed": failed},
        ensure_ascii=False,
        sort_keys=True,
    )
    with open(result_path, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def _save_manifest_updates(m: dict[str, str], touched: set[str]) -> None:
    """merge-on-save：save 前重新載入 on-disk manifest，只套用本行程處理過
    的路徑。兩個 apply 行程平行跑時，整檔覆寫會讓後結束者用啟動時的舊
    快照洗掉先結束者的紀錄（PR 5 實測：2 檔 provenance 回退、被誤判
    stale，重跑會覆蓋已 merge 的好譯文）。"""
    fresh = manifest.load()
    for path in touched:
        if path in m:
            fresh[path] = m[path]
        else:
            fresh.pop(path, None)
    manifest.save(fresh)


def run(
    paths: list[str],
    backend_name: str,
    en_ref: str = "english-main",
    apply: bool = False,
    max_lines: int = CHUNK_MAX_LINES,
    result_path: str | None = None,
) -> tuple[int, dict[str, list[str]]]:
    backend = base.get(backend_name)
    m = manifest.load()
    ok, failed = 0, {}
    touched: set[str] = set()

    for path in paths:
        en = _show(en_ref, path)
        if en is None:
            failed[path] = [f"{path} 不存在於 {en_ref}"]
            continue
        prev = _show("HEAD", path) or ""
        try:
            if path in manifest.SIDEBAR_FILES:
                out = sidebar.translate(en, prev, backend)
            elif prev and tier(path, en_ref) == "A":
                out = rebuild_frontmatter_only(en, prev, backend, _prev_en(path, m))
            else:
                prev_en = _prev_en(path, m) if prev else ""
                out = assemble(en, prev, prev_en, backend, max_lines)
        except Exception as e:  # noqa: BLE001
            failed[path] = [str(e)]
            continue

        if apply:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(out, encoding="utf-8")
            manifest.record(m, path, en_ref)
            touched.add(path)
        ok += 1

    if apply:
        _save_manifest_updates(m, touched)
    if result_path:
        _append_result(result_path, ok, touched, failed)
    return ok, failed
