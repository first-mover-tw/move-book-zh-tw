"""sidebar.yml 的 label 翻譯。

只有 label 的值需要翻譯；其餘每一行都必須與英文檔逐位元組相同。
慣例格式為「繁體中文 (Original English)」。
"""

import re

from .backends.base import Backend

_LABEL = re.compile(r"^(\s*-?\s*label:\s*)(.+)$", re.M)
_YAML_SPECIAL = ":{}[],'\"&*?|>!%@`#"

# 中文 label 慣例格式為「(可選的編號前綴) 中文譯文 (Original English)」，
# 例如 "2.1 整數 (Integers)" 對應英文 label "2.1 Integers"（編號前綴屬於
# 英文原文的一部分，不會出現在括號內）。抓出編號前綴 + 括號內文字，
# 兩者相接才是能對回 en label 全文的 key。
_ZH_LABEL = re.compile(r"^(?P<prefix>\d+(?:\.\d+)*\.?\s+)?.*\((?P<eng>[^()]+)\)\s*$")

SIDEBAR_PROMPT = (
    "你是專業的技術文件翻譯者。\n"
    "請將以下側邊欄標籤翻譯成台灣繁體中文。\n"
    "格式一律為「繁體中文翻譯 (Original English)」。\n"
    "使用台灣用語：套件（不是包）、函式（不是函數）、模組（不是模塊）。\n"
    "若標籤是專有名詞或縮寫（例如 BCS、Move 2024），保持原樣不譯。\n"
    "輸入為每行一個編號標籤，請以相同的編號格式回傳。\n"
    "只回傳編號後的翻譯結果，不要任何解釋。"
)


def _unquote(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        return v[1:-1]
    return v


def labels(text: str) -> list[str]:
    return [_unquote(m.group(2)) for m in _LABEL.finditer(text)]


def skeleton(text: str) -> str:
    """把 label 的值換成 <L>，用於證明結構未被更動。"""
    return _LABEL.sub(lambda m: f"{m.group(1)}<L>", text)


def _quote(v: str) -> str:
    return f"'{v}'" if any(c in v for c in _YAML_SPECIAL) else v


def apply(text: str, translated: list[str]) -> str:
    matches = list(_LABEL.finditer(text))
    if len(matches) != len(translated):
        raise ValueError(f"label 數不符: 檔案 {len(matches)}, 譯文 {len(translated)}")
    out, last = [], 0
    for m, new in zip(matches, translated):
        out.append(text[last:m.start()])
        out.append(m.group(1) + _quote(new))
        last = m.end()
    out.append(text[last:])
    return "".join(out)


def _parse_numbered(raw: str, n: int) -> list[str]:
    got: dict[int, str] = {}
    for line in raw.strip().splitlines():
        m = re.match(r"^\s*(\d+)[.)]\s*(.+?)\s*$", line)
        if m:
            got[int(m.group(1))] = m.group(2)
    missing = [i for i in range(1, n + 1) if i not in got]
    if missing:
        raise ValueError(f"翻譯結果缺少編號: {missing}")
    return [got[i] for i in range(1, n + 1)]


def translate(en_text: str, prev_zh_text: str, backend: Backend) -> str:
    en_labels = labels(en_text)

    # 沿用：把舊中文檔的「中文 (English)」label 拆出 English -> 中文 label 的對照表，
    # 之後每個英文 label 若在表中就直接沿用，不呼叫 backend。
    # 沒有括號的 label（專有名詞/縮寫，例如 "Move 2024"、"BCS"，依約定保持原樣
    # 不譯）視為英文 label 本身即是譯文，用自己當 key。
    carried: dict[str, str] = {}
    if prev_zh_text:
        for zh_l in labels(prev_zh_text):
            m = _ZH_LABEL.match(zh_l)
            if m:
                prefix = m.group("prefix") or ""
                carried[prefix + m.group("eng")] = zh_l
            else:
                carried[zh_l] = zh_l

    todo = [l for l in en_labels if l not in carried]
    if todo:
        # kind="text" 的真實 backend（claude_cli/gemini）已經在自己內部把
        # SYSTEM_PROMPT 包在文字外面（見 backends/claude_cli.py、gemini.py），
        # 這裡不重複包一層 —— 否則會把 SIDEBAR_PROMPT 的說明文字混進待翻譯
        # 內容，讓依賴「每行都是 N. 內容」格式的 backend 解析失敗。
        # SIDEBAR_PROMPT 仍是本模組對外匯出的常數，供未來 backend 依 kind
        # 分派專屬 prompt 時使用。
        numbered = "\n".join(f"{i + 1}. {l}" for i, l in enumerate(todo))
        raw = backend.translate(numbered, kind="text")
        for src, dst in zip(todo, _parse_numbered(raw, len(todo))):
            carried[src] = dst

    out = apply(en_text, [carried[l] for l in en_labels])
    if skeleton(out) != skeleton(en_text):
        raise ValueError("sidebar 結構被更動")
    return out
