"""pipeline 與 validate 共用的 pattern。

單獨一個模組是為了避免 import 迴圈：validate 不能 import pipeline
（pipeline import validate），但兩邊必須用**同一個** pattern —— 修復 pass
與它的 fail-closed gate 若各刻一份底線強調的定義，就會出現「修復認為不用
修、gate 認為要擋」或反過來的死鎖（lessons L7 那個 inject/gate 永久死鎖
就是兩份獨立實作的不變式前置條件不一致）。
"""

import re

# 底線強調：`_文字_`。允許內部有空白與括號，但不跨行、不含反引號。
UNDERSCORE_EM = re.compile(r"_([^_\n`]+)_")

# 連結／圖片 destination、autolink、裸 URL、reference-style 連結定義。
# 會改寫文字的 pass（術語替換、強調修復）都必須把這些當保護區：含 CJK 的 URL
# （`zh.wikipedia.org/wiki/區塊鏈_(技術)`、中文檔名的圖片）在中文譯文裡完全可能
# 出現，術語被替換或底線被改成星號就是 404 與圖裂，而且 gate 10 看不到
# （<em> 不減反增）。
#
# **四個 alternation 各對應一種連結形態。** 2026-09-04 外部 review 指出原本漏掉
# reference-style 定義（`[標籤]: ./路徑.md`）中沒有 scheme 的 destination ——
# 實測 `enforce('[標籤]: ./創建_套件.md')` 會改寫成 `./建立_套件.md`，語料
# `book/storage/key-ability.md:51-56` 就有 6 個相對路徑 ref-def（今天恰好都不含
# 術語表詞條，屬潛伏未爆）。
LINK_DEST = re.compile(
    # ](dest) / ](<dest>) / ](dest "title")
    r"\]\(\s*(?P<inline><[^>\n]*>|[^\s)]*)"
    r"(?:\s+(?P<title>\"[^\"\n]*\"|'[^'\n]*'|\([^)\n]*\)))?\s*\)"
    # [label]: dest      （reference-style 連結定義，行首最多三個空白）
    r"|^[ ]{0,3}\[[^\]\n]+\]:[ \t]*(?P<refdef><[^>\n]*>|\S+)"
    # <scheme:...>       （autolink）
    r"|<(?P<autolink>[a-zA-Z][a-zA-Z0-9+.-]*:[^>\s]*)>"
    # scheme://...       （裸 URL）
    r"|(?P<bare>[a-zA-Z][a-zA-Z0-9+.-]*://[^\s)\]]+)",
    re.MULTILINE,
)

_DEST_GROUPS = ("inline", "refdef", "autolink", "bare")
_SCHEME = re.compile(r"<?[a-zA-Z][a-zA-Z0-9+.-]*:")


def _is_local_fragment_dest(dest: str) -> bool:
    """這個 destination 的 `#…` 是不是**從我們自己的語料推導出來**的 slug。

    是的話（`#錨點`、`./other.md#錨點`、`../a/b#錨點`），fragment 必須跟著標題
    一起被術語替換 —— 語料現有的中文錨點就是靠同一個 `str.replace` 把標題與
    錨點一起改才保持一致的。凍結 fragment 卻放行標題 = 死錨點。

    帶 scheme 的（`https://example.com/p#位址`）不是：那是外部網站的 fragment，
    不由我們的標題決定，必須凍結。
    """
    return "#" in dest and _SCHEME.match(dest) is None


def link_dest_spans(body: str, *, protect_fragments: bool):
    """產生「不可被文字改寫」的字元區間 (start, end)。

    `protect_fragments` 是兩類消費端的分水嶺，需求**相反**：

    - **文字替換**（glossary.enforce / scan）要 False —— 本地 fragment 讓出來，
      跟著標題一起改。
    - **強調修復**（pipeline._repair_cjk_emphasis）要 True —— 它把 `_x_` 換成
      `*x*`，對 slug 而言是把字元換掉、錨點直接失效，而它又沒有「同步改標題」
      這回事，所以連 fragment 都要凍結。

    判準是**解析出 destination 再看它有沒有 scheme**，不是比對前綴形態。
    原本用 `dest.startswith("](#")` 判「純頁內 fragment」，那是 L2 的代理量：
    跨檔 fragment（`](./structs#透過模式匹配銷毀結構體)`，語料有 3 處）與角括號
    目的地（`](<#錨點>)`）都會被誤判成「不是頁內錨點」而整段凍結，於是錨點被
    凍住、目標標題照樣被 enforce 改寫 —— 死錨點。
    """
    for m in LINK_DEST.finditer(body):
        for name in _DEST_GROUPS:
            dest = m.group(name)
            if dest is None:
                continue
            start, end = m.span(name)
            if not protect_fragments and _is_local_fragment_dest(dest):
                end = start + dest.index("#")  # `#` 之後讓出來
            if end > start:
                yield start, end
        if m.group("title") is not None:
            # title 是人可讀的提示文字、理論上該被替換，但語料實測**零個**帶
            # title 的連結（外部 review 2026-09-04 grep 確認），保守保護零成本。
            yield m.span("title")


# HTML 註解（可跨行）。註解掉的內容不會被渲染，裡面的連結與錨點都不是真的
# 連結 —— 例如 `reference/abilities.md` 的 `<!-- TODO：…[動機說明]
# (#motivating-walkthrough)… -->` 指向一個還沒寫的章節，**英文原文同樣是
# 懸空的**。舊譯文把整段註解漏譯，所以這個缺口一直沒被看見；2026-09-05 排乾
# 產出的新譯文把註解保留下來（比較忠實），gate 5 才第一次紅。
HTML_COMMENT = re.compile(r"<!--[\s\S]*?-->")


def html_comment_mask(body: str) -> list[bool]:
    """逐字元遮罩：True 代表這個字元在 HTML 註解裡。"""
    mask = [False] * len(body)
    for m in HTML_COMMENT.finditer(body):
        for i in range(*m.span()):
            mask[i] = True
    return mask
