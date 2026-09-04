"""寫檔前的守門員。任一條不過就不寫檔。

八道關卡對修復前的 HEAD 執行即會變紅（19 檔結構、89 檔 description），
無需另行製造缺陷來驗證守衛有效。
"""

import json
import os
import re
from pathlib import Path

import commonmark
from html.parser import HTMLParser
from opencc import OpenCC

from . import anchors, frontmatter, glossary
from .pipeline_patterns import UNDERSCORE_EM as _UNDERSCORE_EM

_CJK = re.compile(r"[一-鿿]")
CJK = _CJK  # 公開別名：pipeline 的沿用/修復判斷與 gate 4 用同一個 pattern
#  anchor 字元集對齊 anchors.slugify() 的輸出字元集（\w 含 unicode，加上連字號）。
# 舊版只允許 ASCII，中文衍生 slug（沒有明確 {#id} 的標題）的連結永遠比對不到，
# 連 gate 5 的檢查都進不去，等於整批這種連結被靜默放行。
_LINK = re.compile(r"\]\((?!https?:|mailto:)([^)#\s]*)#([\w-]+)\)")

# gate 8 對簡體殘留的白名單。glossary 管詞彙（函數→函式），這裡管字形——
# 兩個不同層次的問題，混在一起會讓 glossary 的違禁詞表塞進字形規則。
#
# 用 OpenCC("s2tw")（不是 s2t）逐字轉換：s2t 只朝「正統繁體」靠攏，會對
# 「了→瞭」「群→羣」「才→纔」「峰→峯」這類台灣日常就寫簡筆的字產生大量
# 假陽性（實測 143 檔中 35 檔會中）。s2tw 已經處理了這些，但逐字套用時
# 仍有兩個字被它的「詞語規則」錯誤地套到單字上，需要另外允許：
#
# 這份白名單只收「OpenCC 轉換本身是錯的」的字，不是收「OpenCC 會轉換的
# 每一個字」。判斷標準是教育部（MOE）標準字形，不是「這個字看起來眼熟／
# 台灣人常這樣寫」。凡是 s2tw 的轉換結果本身就是 MOE 標準字形，一律
# 不進白名單，即使原字在其他中文地區（港澳、中國大陸）通行——那正是
# gate 8 要攔的東西。
#
# 「裏→裡」「着→著」不在白名單裡，是刻意的：MOE 標準字形是「裡」「著」，
# 「裏」「着」是港澳／中國大陸的字形，s2tw 把它們轉掉是本關卡的設計目的，
# 不是假陽性，不要因為「看起來也是常見寫法」就加進來。
#
# 字元層級沒有一條乾淨規則能同時判對所有情況：round-trip 規則
# `s2tw(c) != c and tw2s(s2tw(c)) == c` 可以救回「裏」，但會誤判真正的
# 簡體字「麽」為非簡體（tw2s(s2tw('麽')) == '麽' 但『麽』確實是簡體），
# 同時仍然攔不住「台」「游」。因此改用逐字白名單，而非嘗試找一條規則。
_ALLOWED_VARIANTS = frozenset({
    # 「台」與「臺」在台灣同為正字（教育部異體字審訂通過兩者並存），
    # s2tw 逐字會把「台」轉成「臺」，但「台」本身不是簡體字，不該被攔。
    "台",
    # 「游→遊」是 OpenCC 的詞語規則（旅游→旅遊）被逐字套用時的誤判；
    # 「上游」「游標」這類詞裡的「游」是正確用字，轉成「上遊」「遊標」反而錯。
    "游",
})

ALLOWED_VARIANTS = _ALLOWED_VARIANTS

# 詞級白名單：這些字單獨看會被 s2tw 逐字轉換（干→乾/幹、准→準），但在
# 下列詞裡是合法繁體。不進 _ALLOWED_VARIANTS 做字級豁免 —— 干/准 的簡體
# 誤用（你在干什麼、瞄准）極常見，字級放行等於關掉這兩個字的偵測。
# 判定：被攔的字元若落在任一白名單詞的出現範圍內 → 放行。
_WORD_ALLOWED = {
    "干": ("若干", "干擾", "干預", "干涉"),
    "准": ("批准", "准許", "准入", "核准", "獲准", "准駁"),
}

_S2TW = OpenCC("s2tw")


class ValidationError(Exception):
    pass


def simplified_chars(body: str) -> list[tuple[int, str]]:
    """8. 找出 body 裡（跳過 code）的簡體殘留字，回傳 (0-based 行號, 字元)。"""
    mask = glossary.protected_mask(body)
    lines = body.splitlines(keepends=True)
    offsets = [0] * (len(lines) + 1)
    for i, line in enumerate(lines):
        offsets[i + 1] = offsets[i] + len(line)

    out: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        start = offsets[i]
        for j, ch in enumerate(line):
            pos = start + j
            if pos < len(mask) and mask[pos]:
                continue
            if ch in _ALLOWED_VARIANTS:
                continue
            if _S2TW.convert(ch) != ch:
                words = _WORD_ALLOWED.get(ch)
                if words and any(
                    w in line[max(0, j - len(w) + 1) : j + len(w)] for w in words
                ):
                    continue
                out.append((i, ch))
    return out


def check_structure(zh_text: str, en_text: str) -> list[str]:
    """只跑 gate 1、2（標題層級序列、fence 數）。這是 spec §五 A 層分層的
    唯一依據：未翻 frontmatter、違禁詞等其餘 gate 是 backfill 要修的缺陷，
    拿來降級會把待修檔誤送整篇重譯。pipeline.tier 用這個，不要用 check_file。"""
    errs: list[str] = []
    _, zh_body = frontmatter.split(zh_text)
    _, en_body = frontmatter.split(en_text)

    zh_h = anchors.headings(zh_body)
    en_h = anchors.headings(en_body)

    # 1. 標題層級序列
    if [lv for lv, _ in zh_h] != [lv for lv, _ in en_h]:
        errs.append(f"標題層級序列不符: 中文 {len(zh_h)} 個, 英文 {len(en_h)} 個")

    # 2. code fence 數量
    if anchors.fence_lines(zh_body) != anchors.fence_lines(en_body):
        errs.append(
            f"程式碼 fence 數不符: 中文 {anchors.fence_lines(zh_body)}, "
            f"英文 {anchors.fence_lines(en_body)}"
        )
    return errs


def check_frontmatter(zh_text: str, en_text: str) -> list[str]:
    """gate 3、4 + 對可翻譯欄位「值」掃違禁詞/簡體（gate 7、8 的 frontmatter 版）。

    這是 A 路徑（pipeline.rebuild_frontmatter_only）的寫檔 gate 之一：A 層的
    body 是 legacy 舊譯文，其既有債務不當寫檔否決（比照 gate 9 不進 check_file
    的先例）；但 frontmatter 值是管線每次新生成的內容，必須受完整品質檢查
    ——實測 5 個現有檔的 description/title 帶違禁詞流出，body-only 掃描擋不住。"""
    errs: list[str] = []
    zh_meta, _ = frontmatter.split(zh_text)
    en_meta, _ = frontmatter.split(en_text)

    # 3. frontmatter key 集合
    if set(zh_meta) != set(en_meta):
        errs.append(f"frontmatter key 不符: {sorted(set(zh_meta))} vs {sorted(set(en_meta))}")

    # 4. 可翻譯欄位必須含 CJK，且必須是字串
    for key in frontmatter.TRANSLATABLE_KEYS & set(zh_meta):
        value = zh_meta[key]
        if not isinstance(value, str):
            errs.append(f"frontmatter {key} 不是字串: {value!r}")
            continue
        if not _CJK.search(value):
            errs.append(f"frontmatter {key} 未翻譯: {value!r}")
        for bad, n in sorted(glossary.scan(value).items()):
            errs.append(f"frontmatter {key} 違禁詞 {bad} 出現 {n} 次")
        for _line, ch in simplified_chars(value):
            errs.append(f"frontmatter {key} 簡體殘留字 {ch!r}")
    return errs


def check_file(
    zh_text: str, en_text: str, prev_zh_text: str = "", prev_en_text: str = ""
) -> list[str]:
    """gate 6（anchor 身分）的執行前提鏡射 anchors._identity_carry：prev_en_text
    缺席，或 prev_zh_text 與 prev_en_text 的標題數不對齊，兩種情況都讓 gate 6
    完全棄權，不做任何檢查（不會退化成別的部分檢查）——理由見 gate 6 區塊的
    註解。"""
    errs: list[str] = list(check_structure(zh_text, en_text))
    errs += check_frontmatter(zh_text, en_text)
    _, zh_body = frontmatter.split(zh_text)
    _, en_body = frontmatter.split(en_text)

    zh_h = anchors.headings(zh_body)
    en_h = anchors.headings(en_body)

    # 6. 既有 anchor 不得消失，也不得被重新指派到別的標題上
    #
    # 這個 guard 執行與否，必須完全鏡射 anchors._identity_carry 的棄權
    # 前提——兩邊是同一個判斷邏輯的兩處實作，改一邊沒改另一邊就會重現
    # 這個 gate 曾經卡死的 deadlock，這次是換一個分支。_identity_carry
    # 在以下兩種情況都拒絕沿用任何 anchor，gate 6 必須在同樣兩種情況下
    # 完全棄權、不做任何檢查（不是退化成別的檢查方式）：
    #
    #   1) prev_en_text 缺席 → inject() 沒有身分依據去分辨「翻譯弄丟了
    #      anchor」與「上游刪掉了對應章節、anchor 退場」，本來就拒絕沿用
    #      任何 anchor。這裡看到的「消失」其實是 inject 正確的保守選擇。
    #   2) prev_zh 與 prev_en 標題數不對齊 → prev_keys 是用 prev_en 的
    #      標題文字算出來的，「第 i 個中文標題對應第 i 個英文標題」這個
    #      by-index 假設只在數量一致時成立。_identity_carry 遇到落差時
    #      「什麼都不沿用」，gate 6 必須對稱地「什麼都不驗證」——不能落回
    #      舊版的消失檢查，那個檢查同樣是 by-index 假設之下才有意義的
    #      東西，假設不成立時它一樣會誤報 inject 正確拒絕沿用的 anchor。
    #
    # 兩種棄權情況都不設 disappearance fallback；第三條路徑（棄權失敗、
    # 退化成別的部分檢查）不存在，也不該被加回來。
    #
    # 已發佈 URL 真正依賴的保護在 gate 5（check_links）：無論 gate 6 因為
    # 上述哪一種情況棄權，只要新 anchor id 仍能被連結解析，壞掉的連結就
    # 不會流出去；gate 6 棄權不代表已發佈 URL 失去保護。
    if prev_zh_text and prev_en_text:
        _, prev_zh_body = frontmatter.split(prev_zh_text)
        _, prev_en_body = frontmatter.split(prev_en_text)
        prev_zh_h = anchors.headings(prev_zh_body)
        prev_en_h = anchors.headings(prev_en_body)

        if len(prev_zh_h) == len(prev_en_h):
            prev_keys = anchors.slugify_all([t for _, t in prev_en_h])
            new_keys = anchors.slugify_all([t for _, t in en_h])
            new_key_index = {k: j for j, k in enumerate(new_keys)}

            now_ids_by_idx = {
                j: aid for j, (_, t) in enumerate(zh_h) if (aid := anchors.existing_anchor(t))
            }

            for i, (_, t) in enumerate(prev_zh_h):
                aid = anchors.existing_anchor(t)
                if aid is None:
                    continue
                k = prev_keys[i]
                j = new_key_index.get(k)
                if j is None:
                    # 對應的英文標題在新版消失了：anchor 退場，人工核准，不算錯誤。
                    continue
                if now_ids_by_idx.get(j) != aid:
                    en_text_i = prev_en_h[i][1]
                    actual = now_ids_by_idx.get(j)
                    errs.append(
                        f"既有 anchor 被重新指派: {{#{aid}}}（原標題「{en_text_i}」）"
                        f"未出現在對應標題上，實際為 {f'{{#{actual}}}' if actual else '無'}"
                    )
        # else: 標題數不對齊，完全棄權（見上方註解情況 2）——不做任何檢查。
    # 7. glossary
    for bad, n in sorted(glossary.scan(zh_body).items()):
        errs.append(f"違禁詞 {bad} 出現 {n} 次")

    # 8. 簡體殘留字
    for line, ch in simplified_chars(zh_body):
        errs.append(f"簡體殘留字 {ch!r}（第 {line + 1} 行）")

    # 10. 強調在翻譯中消失（見 check_cjk_emphasis）
    errs += check_cjk_emphasis(zh_text, en_text)

    # 11. 有序列表序號被重複寫進內文（見 check_ordered_list_numbering）
    errs += check_ordered_list_numbering(zh_text)

    return errs


def _emphases(text: str) -> tuple[str, ...]:
    """渲染後的強調**型別序列**（document order），**排除標題**。

    回傳例：`("em", "em", "strong")`。用序列不用計數，因為計數是位置盲的
    代理量（lessons L2）：把英文的 `*em*` 與 `**strong**` 對調，兩邊的
    (em 數, strong 數) 都還是 (1, 1)，數字判準完全看不見，序列判準一眼就看到。

    問 commonmark 本人，不重刻 CommonMark 的 left/right-flanking 規則。

    為什麼排除標題：本專案的標題慣例是「中文譯文 (英文原文)」，英文原文
    一字不差地重複一次 —— 英文標題裡若有強調，中文標題必然算到兩次（譯文
    一次、括號內原文一次），再加上 `{#anchor}` 在裸 commonmark 下是普通文字、
    裡面的底線也會被算進去。`enum-and-match.md` 的
    `### 技巧 #1 - _任意_ 條件 (Trick #1 - _any_ Condition) {#trick-1---_any_-condition}`
    對英文的 1 個 em 產出 3 個。這是慣例的必然結果不是缺陷，標題格式另有
    gate 9 管，所以這道 gate 只看內文。全語料實測只有這一個檔受影響。
    """
    class _Counter(HTMLParser):
        """在**渲染後的 HTML** 上數，並跳過 <h1>–<h6> 內部。

        刻意不引入第二個 markdown 實作：生產端一律用 `commonmark`，測試端才用
        `markdown_it`。同一個不變式兩份實作必然漂移（lessons L15），所以這裡
        接的是 commonmark 自己的輸出。
        """

        def __init__(self):
            super().__init__()
            self.seq: list[str] = []
            self._depth = 0

        def handle_starttag(self, tag, attrs):
            if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                self._depth += 1
            elif self._depth == 0 and tag in ("em", "strong"):
                self.seq.append(tag)

        def handle_endtag(self, tag):
            if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._depth:
                self._depth -= 1

    body = frontmatter.split(text)[1]
    c = _Counter()
    c.feed(commonmark.commonmark(body))
    return tuple(c.seq)


def check_cjk_emphasis(zh_text: str, en_text: str) -> list[str]:
    """gate 10：翻譯過程中弄丟了強調。

    CommonMark 不允許 `_` 在詞內開合（避免 snake_case 被誤判成強調），而
    CJK 算 word char。於是 `進行_升級_：` 產出的是**合法 Markdown、卻完全
    沒有 <em>** —— 強調靜靜消失。PR #22 實測：backend 從 `*文字*` 改用
    `_文字_` 之後，3 個檔的 5 處強調全滅。結構檢查（標題層級、fence 數）、
    術語、簡體、prettier 全部看不到，只有人眼發現得了。

    判準是「跟英文原文比，中文渲染出來的強調變少了」——**不是**「有沒有
    可疑的底線對」。後者是代理量：第一版就是那樣寫的，對全語料噴 192 個
    假陽性，全是 URL（`Lambda_(computer_function)`）與識別字碎片
    （`_failureabort_`）（lessons L2）。

    修復由 pipeline._repair_cjk_emphasis 決定性完成，這道 gate 是
    fail-closed 的第二層：修復漏掉就擋下來，不靜默放行。
    """
    zh_seq, en_seq = _emphases(zh_text), _emphases(en_text)
    if zh_seq == en_seq:
        return []
    zh_em, en_em = zh_seq.count("em"), en_seq.count("em")
    zh_st, en_st = zh_seq.count("strong"), en_seq.count("strong")
    # 只報數字的話，人要自己在整份檔案裡找哪幾處壞掉。把渲染不出來的候選
    # 位置一併指出來（修復 pass 修不掉的通常就是這些）。
    body = frontmatter.split(zh_text)[1]
    mask = glossary.protected_mask(body)
    suspects = []
    for m in _UNDERSCORE_EM.finditer(body):
        if any(mask[i] for i in range(m.start(), m.end())):
            continue
        line = body[body.rfind("\n", 0, m.start()) + 1 :].split("\n", 1)[0]
        if f"<em>{m.group(1)}</em>" not in commonmark.commonmark(line):
            suspects.append(f"`_{m.group(1)}_`")
    hint = ("；可疑位置：" + "、".join(suspects[:5])) if suspects else ""
    parts = []
    if zh_em != en_em:
        parts.append(f"<em> 英文 {en_em} 中文 {zh_em}")
    if zh_st != en_st:
        parts.append(f"<strong> 英文 {en_st} 中文 {zh_st}")
    if not parts:
        # 數量都對、序列不對 = 某處的 em 與 strong 被對調了。指出第一個分歧點，
        # 否則人只會看到「數字都一樣」而找不到問題（這正是舊判準的盲區）。
        i = next(
            (k for k, (a, b) in enumerate(zip(en_seq, zh_seq)) if a != b),
            min(len(en_seq), len(zh_seq)),
        )
        parts.append(f"數量相同但順序不符：第 {i + 1} 個強調，英文是 {en_seq[i]}、中文是 {zh_seq[i]}")
    return [
        "強調與原文不符（" + "、".join(parts) + "）。"
        "少了：常見原因是 `_中文_`（CJK 相鄰時 `_` 不能開合強調）改用 `*中文*`、"
        "`**中文：**後接中文` 收尾分隔符前是標點後是 CJK 收不了尾（冒號移到 `**` 外面）、"
        "英文的 `_em_` 被譯成 `**粗體**`、譯者用「」取代強調。"
        "多了：中文自行加了原文沒有的強調" + hint
    ]


def _ol_items(html: str) -> list[tuple[int, str]]:
    """從渲染後的 HTML 取出每個有序列表項的 (序號, 項目自身的前導文字)。

    自身：巢狀在項目裡的子列表不算——子列表有自己的序號序列，把它的文字
    併進來會讓「前導數字」對到錯誤的序號。
    """
    class _P(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.stack: list[dict] = []  # 每層列表：{"ol": bool, "n": 下一個序號}
            self.items: list[tuple[int, str]] = []
            self.buf: list[str] = []
            self.cur: int | None = None
            self.code = 0  # <code>/<pre> 巢狀深度

        def _flush(self):
            if self.cur is not None:
                self.items.append((self.cur, "".join(self.buf)))
            self.cur, self.buf = None, []

        def handle_starttag(self, tag, attrs):
            if tag in ("ol", "ul"):
                start = 1
                for k, v in attrs:
                    if k == "start" and v and v.isdigit():
                        start = int(v)
                self.stack.append({"ol": tag == "ol", "n": start})
            elif tag in ("code", "pre"):
                self.code += 1
            elif tag == "li" and self.stack:
                # 這個 flush 是巢狀正確性的支點：子列表的第一個 <li> 開啟時
                # 結掉外層項目，外層的「前導文字」因此不含子列表內容。
                self._flush()
                top = self.stack[-1]
                if top["ol"]:
                    self.cur = top["n"]
                top["n"] += 1

        def handle_endtag(self, tag):
            if tag in ("ol", "ul"):
                self._flush()
                if self.stack:
                    self.stack.pop()
            elif tag in ("code", "pre"):
                self.code = max(0, self.code - 1)
            elif tag == "li":
                self._flush()

        def handle_data(self, data):
            # 只收「這一項自己」的文字：子列表一開始就 _flush()，cur 歸 None，
            # 巢狀內容因此不會被算進外層項目。
            #
            # inline code 也不算：`1. `1.` 是有序列表標記` 是在講標記本身，
            # 不是把序號重複寫進內文。
            if self.cur is not None and not self.code:
                self.buf.append(data)

    p = _P()
    p.feed(html)
    p.close()
    p._flush()
    return p.items


# 只認**半形列表標記形態**：`N.` 或 `N)` 後面接空白或行尾。這正是實測到的
# 缺陷形態（機翻抄的是它看到的那個標記，`1.  **1. 前言**`）。
#
# 兩個刻意的收窄，都是為了不誤報：
# 1. 分隔符後必須有空白 —— 否則 `1.0 版本` 的小數點會被當成列表分隔符。
# 2. 不收全形 、．） —— 「1、2、3 三種模式都支援」「1）與 2）的差別」是
#    合法的中文列舉，和「重複的列表標記」在字面上無法區分（2026-09-04
#    第四輪外部 review 實測，兩者都會被判成缺陷）。
#
# 收窄的代價是漏掉「1. 1、預設安全性」這種形態。這是刻意的取捨：本 gate
# 沒有自動修復路徑（見下），誤報一次就是該檔永久寫不出來、每輪重翻重擋；
# 漏報則只是回到人工審 PR 抓的狀態。fail-closed 的守衛要對誤報格外保守。
_LEADING_NUM = re.compile(r"^\s*(\d+)\s*[.)](?=\s|$)")


def check_ordered_list_numbering(zh_text: str) -> list[str]:
    """gate 11：有序列表的序號被重複寫進項目文字裡。

    機翻把 markdown 的 `1.` 標記又抄進內文，於是 `1. **Secure by default:**`
    變成 `1.  **1. 預設安全性:**`，讀者看到的是「1. 1. 預設安全性」
    （2026-09-03 run 33730438417 / PR #24，foreword.md 三項全中）。
    結構檢查（標題層級、fence 數）、術語、簡體、prettier 全部看不到。

    判準是**身分**不是「開頭有沒有數字」（lessons L2）：項目自身的前導數字
    要等於這一項的序號才算重複。於是 `1. 2024 版本的…` 這種合法內容
    （2024 ≠ 1）不會誤判；既有 108 檔語料實測偽陽性 0。

    序號取自渲染後的 `<ol>`（含 `start=` 與巢狀重新計數），不重刻
    markdown 的列表編號規則——同 gate 10 的作法，問 commonmark 本人。

    **本 gate 沒有自動修復路徑，是刻意的。** 曾經有一個
    `pipeline._repair_ol_numbering`，四輪外部 review 抓到七個缺陷後移除。
    致命的兩個都不是實作瑕疵、而是這條路本身走不通：
    - lazy 編號列表（每項都寫 `1.`，語料 `reference/packages.md:35-40`
      真的這樣寫）裡，修好第一項就會讓 gate 轉綠，其餘各項的缺陷**靜默
      出貨** —— 修復把 fail-closed 的守衛變成假的全綠，比沒有它更糟。
    - 「刪掉的那段是重複的列表標記」與「那段是合法的中文列舉」在渲染
      結果上無法區分（`1. 1、2、3 三種模式`），任何後置條件都證明不了
      前者，因為資訊不在那裡。
    所以這道 gate 擋下來就是擋下來，交給人處理。相對地，判定要對誤報
    格外保守（見 _LEADING_NUM 的收窄）——誤報的代價是該檔永久寫不出來。
    """
    body = frontmatter.split(zh_text)[1]
    errs = []
    for n, text in _ol_items(commonmark.commonmark(body)):
        m = _LEADING_NUM.match(text)
        if m and int(m.group(1)) == n:
            errs.append(f"有序列表序號重複寫進內文：第 {n} 項的文字以「{m.group(0).strip()}」開頭")
    return errs

def _anchor_ids(text: str) -> set[str]:
    """Docusaurus 只為每個標題產出一個 id：有 {#id} 就只用它，
    沒有就用衍生 slug。兩者絕不會同時存在——舊版把兩者聯集起來，
    等於承認一個 Docusaurus 從未產生過的 phantom slug 也能通過連結檢查。

    必須與 anchors.inject() 的分層順序一致：先保留（reserve）每個明確 {#id}，
    再用 slugify_all(reserved=...) 對沒有明確 id 的標題衍生 slug，讓衍生出的
    slug 撞到明確 id 時會自動遞增尾碼，而不是各自獨立衍生後才發現撞名、
    直接聯集成看起來變少了一個的 id 集合。
    """
    _, body = frontmatter.split(text)
    hs = anchors.headings(body)
    ids: set[str] = set()
    derive_texts = []
    for _, t in hs:
        explicit = anchors.existing_anchor(t)
        if explicit:
            ids.add(explicit)
        else:
            derive_texts.append(t)
    derived = anchors.slugify_all(derive_texts, reserved=ids)
    ids.update(derived)
    return ids


_ANCHOR_SUFFIX = re.compile(r"\s*\{#[\w-]+\}\s*$")
ANCHOR_SUFFIX = _ANCHOR_SUFFIX  # 公開別名：pipeline._repair_headings 與判定同一前處理
# 標題內的 inline code span。單行標題文字用簡單配對即可，不需要
# glossary.protected_mask 的跨行/巢狀 backtick 處理。
_HEADING_CODE_SPAN = re.compile(r"`[^`]*`")

# gate 9 的專有名詞豁免表。「去 inline code 後無小寫」那條豁免是為縮寫
# （BCS）設計的，接不住 VSCode / Emacs / Zed / Github Codespaces 這類
# 本來就沒有中文譯名的產品名：它們含小寫，於是被判「未翻譯」，而修復
# pass 唯一的出路是叫 backend 硬掰一個中文前綴，實測產出
# 「VSCode 整合開發環境 (VSCode)」「Emacs 文字編輯器 (Emacs)」這種贅語
# （2026-08-31，run 33367759448 / PR #17）。gate 逼出來的缺陷手修沒用，
# 下一輪重翻會原樣長回來，所以豁免要開在 gate 這一側。
#
# 判定採 token 全稱：標題去掉 code span 與標點後，每個字母 token 都在表內
# 才豁免（"Github Codespaces" = Github + Codespaces 都在表內 → 過；
# "Set Up Your IDE" 只有 IDEA/IDE 之類在表內、Set/Up/Your 不在 → 仍擋）。
# 逐 token 而非整句比對，是為了讓多字產品名不必逐一列舉組合。
#
# 這張表刻意只收「產品／工具名」與使用者裁決過保留原文的專名（Party，
# 2026-08-31 裁決），不收 Bag / Balance / Coin / Clock 這類型別名——那是
# 另一個獨立裁決（型別名到底該不該保留原文），混進來會讓豁免悄悄擴權。
_PROPER_NOUNS = frozenset(
    json.loads((Path(__file__).parent / "proper_nouns.json").read_text(encoding="utf-8"))
)
_WORD = re.compile(r"[A-Za-z][A-Za-z0-9]*")


def _is_proper_noun_only(text: str) -> bool:
    """text 去掉 code span 後，所有字母 token 都是已知專有名詞。

    無字母 token 時回 False：那種標題走「無小寫」那條豁免，不該從這裡
    拿到第二張通行證（避免兩條豁免的前提互相漂移）。
    """
    words = _WORD.findall(_HEADING_CODE_SPAN.sub("", text))
    return bool(words) and all(w in _PROPER_NOUNS for w in words)


def check_heading_suffix(zh_text: str, en_text: str) -> list[str]:
    """9. 新翻譯的 body 標題必須是「中文 (English)」，後綴值等於對應的英文
    標題文字（驗值不驗形；只驗「有括號」擋不住配錯標題的後綴）。

    只掛在 pipeline.assemble（新翻譯）路徑，不進 check_file：legacy corpus
    有 110/147 檔、473 個標題無後綴（2026-07-11 實測），掛進 check_file 會
    讓 A 層 rebuild_frontmatter_only（body 原封不動是舊譯文）整批被擋。
    sidebar 的 label 有自己的守衛（sidebar._validate_new_label_format），
    不歸這裡管。

    棄權前提鏡射 gate 6 對 by-index 假設的處理：標題數不一致時「第 i 個
    中文標題對應第 i 個英文標題」不成立，本 gate 完全棄權——數量不符本身
    由 gate 1（標題層級序列）負責報錯，檔案不會因為本 gate 棄權而漏網。

    zh == en 的豁免只給「去 inline code 後無 ASCII 小寫」的標題（專有名詞、
    縮寫、純 code，如 "BCS"、"`copy`"；english-main 實測 1154 個標題中僅
    14 個）。含小寫散文的標題 verbatim 複製等於整個沒翻 —— 這是 Task 17
    A/B 觀測到的真實 backend 失效模式（sonnet 對 "Scopes"），無條件豁免
    zh == en 會讓它從八道 gate 加本 gate 全數漏網。
    """
    _, zh_body = frontmatter.split(zh_text)
    _, en_body = frontmatter.split(en_text)
    zh_h = anchors.headings(zh_body)
    en_h = anchors.headings(en_body)
    if len(zh_h) != len(en_h):
        return []

    errs = []
    for i, ((_, zh_t), (_, en_t)) in enumerate(zip(zh_h, en_h)):
        err = heading_suffix_error(zh_t, en_t)
        if err:
            errs.append(f"標題 {i} {err}")
    return errs


def heading_suffix_error(zh_t: str, en_t: str) -> str | None:
    """gate 9 的單標題判定。check_heading_suffix 的迴圈與
    pipeline._repair_headings（修復 pass）共用這一份 —— 判定與修復若各自
    實作，前提漂移就會重演 gate 6/inject 那次的死鎖家族。回 None = 合格。"""
    zh_t = _ANCHOR_SUFFIX.sub("", zh_t).strip()
    en_t = _ANCHOR_SUFFIX.sub("", en_t).strip()
    if zh_t == en_t:
        if not re.search(r"[a-z]", _HEADING_CODE_SPAN.sub("", en_t)):
            return None
        if _is_proper_noun_only(en_t):
            return None  # 產品名／裁決保留原文的專名：verbatim 才是正解
        return f"未翻譯（verbatim 複製英文原文）: {zh_t!r}"
    want = f"({en_t})"
    prefix = zh_t[: -len(want)].strip() if zh_t.endswith(want) else ""
    if not prefix:
        return f"缺「中文 (English)」後綴或後綴值不符: 預期以 {want!r} 結尾, 實際 {zh_t!r}"
    if not _CJK.search(prefix) and re.search(
        r"[a-z]", _HEADING_CODE_SPAN.sub("", prefix)
    ):
        # 後綴對了但前綴仍是英文散文 ——「記得格式、忘了翻譯」。
        # 無 CJK 且無小寫的前綴（縮寫，如 BCS）合法，鏡射 verbatim 豁免。
        return f"前綴未翻譯: {zh_t!r}"
    return None


def check_links(files: dict[str, str]) -> list[str]:
    """5. 所有內部 anchor 連結可解析。files: 路徑 -> 內容。"""
    index = {p: _anchor_ids(c) for p, c in files.items()}
    errs = []
    for path, content in files.items():
        _, body = frontmatter.split(content)
        # 與 gate 8 相同：code（fence / 縮排 / inline span）內的連結是範例
        # 文字，不是真連結，先遮蔽再掃，否則假陽性會擋寫檔。
        mask = glossary.protected_mask(body)
        for m in _LINK.finditer(body):
            if mask[m.start()]:
                continue
            target, anchor = m.group(1), m.group(2)
            target = target.split("?")[0]  # 剝掉 ?highlight=native 這類 query string
            if target == "":
                tgt = path
                candidates = [tgt]
            elif target.startswith("/"):
                # 絕對路徑相對於 repo 根目錄，不是相對於當前檔案。
                t = target.lstrip("/")
                if not t.endswith(".md"):
                    t += ".md"
                candidates = [os.path.normpath(t)]
            else:
                t = target.rstrip("/")
                base = os.path.normpath(os.path.join(os.path.dirname(path), t))
                if t.endswith(".md"):
                    candidates = [base]
                else:
                    # 先試 sub.md，再試目錄式的 sub/index.md（Docusaurus 的解析順序）。
                    candidates = [base + ".md", os.path.normpath(os.path.join(base, "index.md"))]

            tgt = next((c for c in candidates if c in index), None)
            if tgt is None:
                errs.append(f"{path}: 連結目標不存在 {target}#{anchor}")
            elif anchor not in index[tgt]:
                errs.append(f"{path}: anchor 無法解析 {target}#{anchor}")
    return errs
