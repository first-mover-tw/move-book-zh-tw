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
    if prev_zh_text and prev_en_text:
        _, prev_zh_body = frontmatter.split(prev_zh_text)
        _, prev_en_body = frontmatter.split(prev_en_text)
        prev_zh_h = anchors.headings(prev_zh_body)
        prev_en_h = anchors.headings(prev_en_body)

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
            if i >= len(prev_keys):
                continue
            k = prev_keys[i]
            j = new_key_index.get(k)
            if j is None:
                # 對應的英文標題在新版消失了：anchor 退場，人工核准，不算錯誤。
                continue
            if now_ids_by_idx.get(j) != aid:
                en_text_i = prev_en_h[i][1] if i < len(prev_en_h) else "?"
                actual = now_ids_by_idx.get(j)
                errs.append(
                    f"既有 anchor 被重新指派: {{#{aid}}}（原標題「{en_text_i}」）"
                    f"未出現在對應標題上，實際為 {f'{{#{actual}}}' if actual else '無'}"
                )
    elif prev_zh_text:
        # 沒有英文側可比對身分，退回舊的「消失偵測」。
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
    """
    _, body = frontmatter.split(text)
    hs = anchors.headings(body)
    derived_all = anchors.slugify_all([t for _, t in hs])
    ids = set()
    for (_, t), derived in zip(hs, derived_all):
        explicit = anchors.existing_anchor(t)
        ids.add(explicit if explicit else derived)
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
