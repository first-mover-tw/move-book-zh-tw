"""寫檔前的守門員。任一條不過就不寫檔。

八道關卡對修復前的 HEAD 執行即會變紅（19 檔結構、89 檔 description），
無需另行製造缺陷來驗證守衛有效。
"""

import os
import re

from opencc import OpenCC

from . import anchors, frontmatter, glossary

_CJK = re.compile(r"[一-鿿]")
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
                out.append((i, ch))
    return out


def check_file(
    zh_text: str, en_text: str, prev_zh_text: str = "", prev_en_text: str = ""
) -> list[str]:
    """gate 6（anchor 身分）需要 prev_zh_text *與* prev_en_text 同時在場才會
    執行；只要其中一個缺席（尤其是 prev_en_text），gate 6 就完全棄權，不做
    任何檢查——理由見 gate 6 區塊的註解。"""
    errs: list[str] = []
    zh_meta, zh_body = frontmatter.split(zh_text)
    en_meta, en_body = frontmatter.split(en_text)

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

    # 3. frontmatter key 集合
    if set(zh_meta) != set(en_meta):
        errs.append(f"frontmatter key 不符: {sorted(set(zh_meta))} vs {sorted(set(en_meta))}")

    # 4. 可翻譯欄位必須含 CJK，且必須是字串
    for key in frontmatter.TRANSLATABLE_KEYS & set(zh_meta):
        value = zh_meta[key]
        if not isinstance(value, str):
            errs.append(f"frontmatter {key} 不是字串: {value!r}")
        elif not _CJK.search(value):
            errs.append(f"frontmatter {key} 未翻譯: {value!r}")

    # 6. 既有 anchor 不得消失，也不得被重新指派到別的標題上
    #
    # 三種情況，鏡射 anchors._identity_carry 的三個分支（同一份 guard，
    # 兩邊要一起改）：
    #   1) prev_zh 與 prev_en 都在，且標題數對齊 → 用身分（slugify_all
    #      比對）驗證每個既有 anchor 落在正確的新標題上，如下。
    #   2) prev_zh 與 prev_en 都在，但標題數不對齊 → by-index 的「第 i 個
    #      中文對應第 i 個英文」假設不成立，什麼都不驗證（與
    #      _identity_carry 遇到同樣落差時「什麼都不沿用」對稱）。
    #   3) prev_en 缺席 → 完全棄權，不做任何 gate 6 檢查。這不是「假設最壞
    #      情況」的舊行為（舊版會把 prev_zh 有、新 zh 沒有的 anchor 一律
    #      當消失來報錯）；那個假設是錯的，因為 inject() 面對同樣缺席的
    #      prev_en 時，本來就拒絕沿用任何 anchor（見 _identity_carry），
    #      所以這裡看到的「消失」其實是 inject 正確的保守選擇，不是一次
    #      翻譯把 anchor 弄丟。沒有 prev_en，gate 6 沒有身分依據去分辨
    #      「翻譯弄丟了 anchor」與「上游刪掉了對應章節、anchor 退場」，
    #      猜測任一邊都可能誤報或漏報，所以直接不猜。
    #      已發佈 URL 真正依賴的保護在 gate 5（check_links）：只要新 anchor
    #      id 仍能被連結解析，gate 6 棄權並不會讓壞掉的連結流出去。
    if prev_zh_text and prev_en_text:
        _, prev_zh_body = frontmatter.split(prev_zh_text)
        _, prev_en_body = frontmatter.split(prev_en_text)
        prev_zh_h = anchors.headings(prev_zh_body)
        prev_en_h = anchors.headings(prev_en_body)

        # prev_keys 是用 prev_en 的標題文字算出來的，只有在 prev_zh 與 prev_en
        # 標題數一致時，「第 i 個中文標題對應第 i 個英文標題」這個 by-index
        # 假設才成立。anchors._identity_carry 面對同一個問題時的作法是：
        # 數量不符就什麼都不猜、不沿用。這裡必須維持同一個 guard，兩邊要
        # 一起改——一旦其中一個放寬了對齊假設，另一個也要跟著檢查。
        if len(prev_zh_h) != len(prev_en_h):
            _, prev_body = frontmatter.split(prev_zh_text)
            prev_ids = {
                aid for _, t in anchors.headings(prev_body)
                if (aid := anchors.existing_anchor(t))
            }
            now_ids = {
                aid for _, t in zh_h if (aid := anchors.existing_anchor(t))
            }
            for lost in sorted(prev_ids - now_ids):
                errs.append(f"既有 anchor 消失: {{#{lost}}}")
        else:
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
    # 7. glossary
    for bad, n in sorted(glossary.scan(zh_body).items()):
        errs.append(f"違禁詞 {bad} 出現 {n} 次")

    # 8. 簡體殘留字
    for line, ch in simplified_chars(zh_body):
        errs.append(f"簡體殘留字 {ch!r}（第 {line + 1} 行）")

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


def check_links(files: dict[str, str]) -> list[str]:
    """5. 所有內部 anchor 連結可解析。files: 路徑 -> 內容。"""
    index = {p: _anchor_ids(c) for p, c in files.items()}
    errs = []
    for path, content in files.items():
        _, body = frontmatter.split(content)
        for target, anchor in _LINK.findall(body):
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
