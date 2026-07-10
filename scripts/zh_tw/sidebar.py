"""sidebar.yml 的 label 翻譯。

只有 label 的值需要翻譯；其餘每一行都必須與英文檔逐位元組相同。
慣例格式為「繁體中文 (Original English)」。
"""

import re

import yaml

from .backends.base import Backend

_LABEL = re.compile(r"^(\s*-?\s*label:\s*)(.+)$", re.M)
_YAML_SPECIAL = ":{}[],'\"&*?|>!%@`#"

# 中文 label 慣例格式為「(可選的編號前綴) 中文譯文 (Original English)」，
# 例如 "2.1 整數 (Integers)" 對應英文 label "2.1 Integers"（編號前綴屬於
# 英文原文的一部分，不會出現在括號內）。抓出編號前綴 + 括號內文字，
# 兩者相接才是能對回 en label 全文的 key。
#
# 前綴有兩種形狀：純數字（含點分層級，例如 "1." / "2.1"）或單一字母加句點
# （附錄用的 "A." ... "F."）。兩者都不能直接假設「前綴不在括號內」——
# 像 "2024 遷移指南 (2024 Migration Guide)" 這種標籤，開頭的 "2024 " 其實是
# 名稱本身的一部分，剛好長得像編號前綴，而括號內已經完整包含它。用「括號內
# 文字是否已經以偵測到的前綴開頭」來判斷要不要把前綴另外接上去，藉此同時
# 處理「前綴在括號外」（附錄、章節編號）與「前綴其實在括號內」（2024 Migration
# Guide）兩種形狀，不需要為特例硬編碼。
_ZH_PAREN = re.compile(r"^(?P<rest>.*)\((?P<eng>[^()]+)\)\s*$")
_CHAPTER_PREFIX = re.compile(r"^(?P<prefix>\d+(?:\.\d+)*\.?|[A-Za-z]\.)\s+")

_YAML_BOOL_NULL = {"true", "false", "yes", "no", "on", "off", "null", "~"}

SIDEBAR_PROMPT = (
    "翻譯以下每個側邊欄標籤為台灣繁體中文，保留「中文 (原文 English)」格式，"
    "專有名詞與縮寫（BCS、Move 2024）維持原文，"
    "使用台灣用語（套件、函式、模組）。"
    "輸入每行一個編號標籤，回傳相同編號。"
)


def _zh_label_key(zh_label: str) -> str:
    """把舊中文檔的一個 label 轉成能對回英文 label 全文的 key。

    有括號的：抓出括號內文字；若括號前偵測到編號/字母前綴，且括號內文字
    尚未包含該前綴，才把前綴接到 key 前面（見上方模組註解的理由）。
    沒有括號的（專有名詞/縮寫，依約定保持原樣不譯）：用自己當 key。
    """
    m = _ZH_PAREN.match(zh_label)
    if not m:
        return zh_label
    eng = m.group("eng").strip()
    pm = _CHAPTER_PREFIX.match(m.group("rest"))
    if pm:
        prefix = pm.group("prefix")
        if not eng.startswith(prefix):
            return f"{prefix} {eng}"
    return eng


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


def _needs_quote(v: str) -> bool:
    """判斷 unquoted `v` 放進 `label: v` 是否無法安全還原成原字串。

    寧可多引號、不可少：任何會讓 yaml.safe_load 炸掉（例如開頭 `- `）、
    或讓型別/內容跑掉（例如 "123" 變 int、"true" 變 bool、"null" 變 None，
    或整段被解成 mapping）的情形都要引號。
    """
    if v == "":
        return True
    if v != v.strip():
        return True
    if v[0] in "-?: ":
        return True
    if v.lower() in _YAML_BOOL_NULL:
        return True
    if any(c in v for c in _YAML_SPECIAL):
        return True
    try:
        loaded = yaml.safe_load(v)
    except yaml.YAMLError:
        return True
    return not isinstance(loaded, str) or loaded != v


def _quote(v: str) -> str:
    if not _needs_quote(v):
        return v
    return "'" + v.replace("'", "''") + "'"


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
            idx = int(m.group(1))
            if idx in got:
                raise ValueError(f"翻譯結果編號重複: {idx}")
            got[idx] = m.group(2)
    missing = [i for i in range(1, n + 1) if i not in got]
    if missing:
        raise ValueError(f"翻譯結果缺少編號: {missing}")
    return [got[i] for i in range(1, n + 1)]


def _walk_labels(node):
    """遞迴走訪解析後的 YAML 結構，收集所有 `label` 鍵的值。"""
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "label":
                yield v
            else:
                yield from _walk_labels(v)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_labels(item)


def translate(en_text: str, prev_zh_text: str, backend: Backend) -> str:
    en_labels = labels(en_text)

    # 沿用：把舊中文檔的「中文 (English)」label 拆出 English -> 中文 label 的對照表，
    # 之後每個英文 label 若在表中就直接沿用，不呼叫 backend。
    carried: dict[str, str] = {}
    if prev_zh_text:
        for zh_l in labels(prev_zh_text):
            carried[_zh_label_key(zh_l)] = zh_l

    todo = [l for l in en_labels if l not in carried]
    if todo:
        # kind="text" 的真實 backend（claude_cli/gemini）已經在自己內部把
        # SYSTEM_PROMPT 包在文字外面（見 backends/claude_cli.py、gemini.py），
        # 但那是給 Markdown 用的通用 prompt，沒有交代 sidebar 特有的格式
        # 要求（保留編號、保留「中文 (English)」括號、專有名詞不譯）。
        # 把 SIDEBAR_PROMPT 當成一段「編號區塊之前」的說明文字接上去 ——
        # 純文字不會被 _parse_numbered 的 `^\s*\d+[.)]\s` 誤判成翻譯結果，
        # 所以不會重演 Deviation 2 那次把說明文字也編號、搞壞解析的問題。
        numbered = "\n".join(f"{i + 1}. {l}" for i, l in enumerate(todo))
        payload = f"{SIDEBAR_PROMPT}\n\n{numbered}"
        raw = backend.translate(payload, kind="text")
        for src, dst in zip(todo, _parse_numbered(raw, len(todo))):
            carried[src] = dst

    out = apply(en_text, [carried[l] for l in en_labels])
    if skeleton(out) != skeleton(en_text):
        raise ValueError("sidebar 結構被更動")

    # skeleton 相等只證明「位置」沒被動到，證明不了型別 —— _quote 沒引號時
    # 一個看起來正常的字串仍可能被 yaml.safe_load 成 int/bool/None。這裡
    # 真的解析一次輸出，確保每個 label 都還原成非空字串。
    try:
        parsed = yaml.safe_load(out)
    except yaml.YAMLError as e:
        raise ValueError(f"輸出無法解析為 YAML: {e}") from e
    if parsed is None:
        raise ValueError("輸出無法解析為 YAML")
    for lv in _walk_labels(parsed):
        if not isinstance(lv, str) or lv == "":
            raise ValueError(f"label 型別或內容不正確（非空字串）: {lv!r}")

    return out
