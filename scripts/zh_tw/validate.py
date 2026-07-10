"""寫檔前的守門員。任一條不過就不寫檔。

七道關卡對修復前的 HEAD 執行即會變紅（19 檔結構、89 檔 description），
無需另行製造缺陷來驗證守衛有效。
"""

import os
import re

from . import anchors, frontmatter, glossary

_CJK = re.compile(r"[一-鿿]")
_LINK = re.compile(r"\]\((?!https?:|mailto:)([^)#\s]*)#([A-Za-z0-9_-]+)\)")


class ValidationError(Exception):
    pass


def check_file(zh_text: str, en_text: str, prev_zh_text: str = "") -> list[str]:
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

    # 4. 可翻譯欄位必須含 CJK
    for key in frontmatter.TRANSLATABLE_KEYS & set(zh_meta):
        value = zh_meta[key]
        if isinstance(value, str) and not _CJK.search(value):
            errs.append(f"frontmatter {key} 未翻譯: {value!r}")

    # 6. 既有 anchor 不得消失或改變
    if prev_zh_text:
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

    return errs


def _anchor_ids(text: str) -> set[str]:
    _, body = frontmatter.split(text)
    hs = anchors.headings(body)
    explicit = {aid for _, t in hs if (aid := anchors.existing_anchor(t))}
    derived = set(anchors.slugify_all([t for _, t in hs]))
    return explicit | derived


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
            else:
                t = target.rstrip("/")
                if not t.endswith(".md"):
                    t += ".md"
                tgt = os.path.normpath(os.path.join(os.path.dirname(path), t))
            if tgt not in index:
                errs.append(f"{path}: 連結目標不存在 {target}#{anchor}")
            elif anchor not in index[tgt]:
                errs.append(f"{path}: anchor 無法解析 {target}#{anchor}")
    return errs
