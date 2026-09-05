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
    # 換行字元無法用任何 flow scalar 引號安全還原 —— YAML 的單/雙引號
    # flow scalar 遇到字面換行會 fold 成空白，值會被悄悄改掉。與其引號
    # 出一個看似安全、實則失真的結果，這裡直接視為不可寫入而擋下來。
    if "\n" in v or "\r" in v:
        raise ValueError(f"label 含有換行字元，無法安全寫入 YAML: {v!r}")
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


def _assert_labels_equal(parsed_labels: list, intended: list[str]) -> None:
    """postcondition：解析後的 label 必須逐一等於原本要寫入的值。

    只檢查型別/非空是不夠的 —— 一個值改變但型別仍是非空字串的寫入
    （例如換行被 YAML flow scalar fold 成空白）會直接漏網。這裡逐一比對
    「解析後的值」是否真的等於「當初打算寫入的值」，兩者缺一都擋下來。
    """
    if len(parsed_labels) != len(intended):
        raise ValueError(
            f"label 數不符（解析後 {len(parsed_labels)}, 預期 {len(intended)}）"
        )
    for i, (got, want) in enumerate(zip(parsed_labels, intended)):
        if not isinstance(got, str) or got == "" or got != want:
            raise ValueError(
                f"label 值不符（index {i}）: 預期 {want!r}, 實際解析出 {got!r}"
            )


def _validate_new_label_format(pairs: list[tuple[str, str]]) -> None:
    """驗證這批「新翻譯」（非沿用）label 是否符合「中文 (English)」慣例。

    不符合慣例的新 label 下次同步時 `_zh_label_key` 對不回英文 label，
    會被誤判成「新」而永遠重翻（與 finding 1 的鍵值 bug 同一種後果，
    肇因不同：這裡是格式漂移）。

    嚴格逐筆檢查，沒有批次一致性的例外：一個真實 backend 若沒有遵循
    「中文 (English)」的格式指示，最典型的失效模式就是整批新 label
    都漏掉括號後綴 —— 這正是最需要擋下來的情況，不能因為「整批都錯」
    反而被放行。`_zh_label_key` 對沒有括號的字串會直接回傳原字串本身
    當 key，所以一個被 backend 正確保留原文的專有名詞（例如 "BCS"、
    "Move 2024"）在 dst == src 時天生就會通過這個檢查，不需要另外
    特判 —— 只有 backend 把它翻掉、括號後綴又漏掉時才會真的不符。
    """
    for src, dst in pairs:
        if _zh_label_key(dst) != src:
            raise ValueError(
                "新翻譯 label 不符合「中文 (English)」慣例，"
                f"下次同步將無法沿用: 英文={src!r} 譯文={dst!r}"
            )


# --- 過濾「上游有、我們還沒翻」的章節 ------------------------------------
#
# sidebar 每次都從 english-main 全量重建，所以上游新增而我們還沒翻的章節
# 一定會被寫回 `book/sidebar.yml`，docusaurus build 因為 doc id 找不到對應
# `.md` 而失敗（2026-09-05 `programmability/scratchpad` 實證）。這裡在翻譯
# **之前**先把那些條目從英文原文剪掉，讓下游一切（label 沿用、skeleton
# 不變式、寫檔）都以剪過的版本為準。
#
# 剪掉的章節不會遺失：下次同步時只要 `.md` 已經存在就會被重新加回，而它的
# 中文 label 仍留在舊檔的沿用表裡（`_zh_label_key`），不需要重新呼叫 backend。


def _mapping(node) -> dict:
    """把 MappingNode 轉成 {key: 子節點}；非 mapping 回空 dict。"""
    if not isinstance(node, yaml.nodes.MappingNode):
        return {}
    return {k.value: v for k, v in node.value if isinstance(k, yaml.nodes.ScalarNode)}


def _doc_id(node) -> str | None:
    v = _mapping(node).get("id")
    return v.value if isinstance(v, yaml.nodes.ScalarNode) else None


def _label_of(node) -> str | None:
    v = _mapping(node).get("label")
    return v.value if isinstance(v, yaml.nodes.ScalarNode) else None


def _link_id(node) -> str | None:
    link = _mapping(node).get("link")
    return _doc_id(link) if link is not None else None


def _keep(node, path, exists, drops: list) -> bool:
    """判定一個 sidebar 條目留不留，並把要刪的**子**條目記進 drops。

    判定只有這一處（L15：不讓修剪與驗證各自實作一份「什麼算缺陷」）；
    文字刪除與後置條件用的期望樹都由這裡產生的 drops 推導。
    """
    items = _mapping(node).get("items")
    if isinstance(items, yaml.nodes.SequenceNode):
        child_drops: list = []
        kept = 0
        for i, child in enumerate(items.value):
            if _keep(child, path + ["items", i], exists, child_drops):
                kept += 1
            else:
                child_drops.append((path + ["items", i], _span(child), child))
        link = _link_id(node)
        # 三種收尾，共同判準是「刪掉會不會讓一個**已經翻好**的頁面從側邊欄
        # 消失」——會的話一律 fail-closed 交回人工（L16：判定與修復不是同一
        # 個資訊量時，寧可死鎖也不要自動做一個不完整的決定）。
        if link is not None and not exists(link):
            if kept:
                raise ValueError(
                    f"category 的 link doc 不存在但底下還有已翻好的項目: {link}"
                    "（整個 category 刪掉會讓那些頁面從側邊欄消失，保留又會讓 build 失敗；"
                    "請先補上該檔或手動處理）"
                )
            return False  # link 與所有子項都還沒翻 —— 整個 category 一起走
        if kept == 0:
            if link is not None:
                raise ValueError(
                    f"category 的子項全都還沒翻，但它自己的 link doc 已存在: {link}"
                    "（空的 items 會讓 build 失敗，刪掉整個 category 又會讓該頁面"
                    "從側邊欄消失；請先補上任一子項或手動處理）"
                )
            return False
        drops.extend(child_drops)
        return True

    doc_id = _doc_id(node)
    return True if doc_id is None else exists(doc_id)


def _walk(node, path, exists, drops: list) -> None:
    """走訪整棵樹；只有序列的元素能被刪（mapping 的值刪掉會破壞結構）。"""
    if isinstance(node, yaml.nodes.MappingNode):
        for k, v in node.value:
            _walk(v, path + [k.value], exists, drops)
    elif isinstance(node, yaml.nodes.SequenceNode):
        # _keep 已經遞迴處理完整棵子樹（含 category 的 items），這裡不能再
        # 往下走，否則同一個條目會被記錄兩次。
        for i, child in enumerate(node.value):
            if not _keep(child, path + [i], exists, drops):
                drops.append((path + [i], _span(child), child))


def _span(node) -> tuple[int, int]:
    """條目佔用的行區間 [start, end)，行號由 YAML 解析器給、不靠 regex 猜邊界。

    `end_mark` 落在**下一個 token**，所以尾端的空行與純註解行其實屬於下一個
    條目，必須回縮，否則會把別人的註解一起刪掉。
    """
    return node.start_mark.line, node.end_mark.line


def _trim(lines: list[str], start: int, end: int) -> int:
    while end - 1 > start and (
        not lines[end - 1].strip() or lines[end - 1].lstrip().startswith("#")
    ):
        end -= 1
    return end


def _drop_from_data(data, path):
    """對 safe_load 出來的結構套用同一條 path 的刪除，產生期望樹。"""
    cur = data
    for key in path[:-1]:
        cur = cur[key]
    del cur[path[-1]]


def prune_missing(text: str, exists) -> tuple[str, list[str]]:
    """剪掉 doc id 無法解析成實體檔案的條目。

    回傳 `(剪過的 YAML 文字, 被剪掉的 doc id 清單)`。`exists(doc_id) -> bool`
    由呼叫端提供（pipeline 傳「磁碟上有沒有那個 .md」）。

    後置條件兩條（L18：症狀消失不等於內容正確）：
      1. 症狀：輸出裡每個 doc id 都通過 `exists`。
      2. 內容不變式：輸出的行是輸入行的**子序列**（只刪整行、不改位元組），
         且 `safe_load(輸出)` 逐節點等於「對解析結果套用同一批刪除」的期望樹。
    """
    root = yaml.compose(text)
    if root is None:
        raise ValueError("sidebar 無法解析為 YAML")

    drops: list = []
    _walk(root, [], exists, drops)
    if not drops:
        return text, []

    lines = text.splitlines(keepends=True)
    spans = sorted((_trim(lines, s, e), s) for s, e in (sp for _, sp, _n in drops))
    kept_lines = list(lines)
    for end, start in sorted(((e, s) for (e, s) in spans), reverse=True):
        del kept_lines[start:end]
    out = "".join(kept_lines)

    # 整個 category 被刪時它自己沒有 doc id，用 label 回報才看得懂是哪一塊。
    dropped_ids = [
        _doc_id(n) or _link_id(n) or _label_of(n) or "/".join(map(str, path))
        for path, _, n in drops
    ]

    total = len(_LABEL.findall(text))
    if not _LABEL.findall(out) or len(drops) * 2 > total:
        raise ValueError(
            f"剪掉的條目過多（{len(drops)}/{total}），"
            f"疑似 exists 判準有誤：{dropped_ids[:5]}"
        )

    expected = yaml.safe_load(text)
    for path, _, _n in sorted(drops, key=lambda d: d[0], reverse=True):
        _drop_from_data(expected, path)
    if yaml.safe_load(out) != expected:
        raise ValueError("剪枝後的 YAML 與期望樹不符（行刪除與樹修剪不一致）")

    src = iter(text.splitlines())
    if not all(line in src for line in out.splitlines()):
        raise ValueError("剪枝改動了保留行的內容（應該只刪整行）")

    for doc_id in _doc_ids_of(out):
        if not exists(doc_id):
            raise ValueError(f"剪枝後仍有無法解析的 doc id: {doc_id}")

    return out, dropped_ids


def _doc_ids_of(text: str) -> list[str]:
    root = yaml.compose(text)
    out: list[str] = []

    def walk(node):
        if isinstance(node, yaml.nodes.MappingNode):
            for k, v in node.value:
                if k.value == "id" and isinstance(v, yaml.nodes.ScalarNode):
                    out.append(v.value)
                else:
                    walk(v)
        elif isinstance(node, yaml.nodes.SequenceNode):
            for c in node.value:
                walk(c)

    walk(root)
    return out

def translate(
    en_text: str, prev_zh_text: str, backend: Backend, exists=None
) -> str:
    # 先剪掉上游有、我們還沒翻的章節，之後所有步驟（沿用表、skeleton
    # 不變式、寫檔）都以剪過的英文原文為準。exists 為 None 時完全不剪。
    if exists is not None:
        en_text, _ = prune_missing(en_text, exists)
    en_labels = labels(en_text)

    # 沿用：把舊中文檔的「中文 (English)」label 拆出 English -> 中文 label 的對照表，
    # 之後每個英文 label 若在表中就直接沿用，不呼叫 backend。
    carried: dict[str, str] = {}
    if prev_zh_text:
        for zh_l in labels(prev_zh_text):
            carried[_zh_label_key(zh_l)] = zh_l

    todo = [l for l in en_labels if l not in carried]
    if todo:
        # payload 自帶 SIDEBAR_PROMPT（sidebar 特有格式要求：保留編號、
        # 「中文 (English)」括號、專有名詞不譯），所以用 kind="sidebar"
        # 告訴 backend 不要再外包任何通用 prompt —— kind="text" 會被包
        # TEXT_PROMPT，其「單一名詞也必須翻」與這裡的「專有名詞維持原文」
        # 互相矛盾。SIDEBAR_PROMPT 是「編號區塊之前」的說明文字，不會被
        # _parse_numbered 的 `^\s*\d+[.)]\s` 誤判成翻譯結果，所以不會
        # 重演 Deviation 2 那次把說明文字也編號、搞壞解析的問題。
        numbered = "\n".join(f"{i + 1}. {l}" for i, l in enumerate(todo))
        payload = f"{SIDEBAR_PROMPT}\n\n{numbered}"
        raw = backend.translate(payload, kind="sidebar")
        new_pairs = list(zip(todo, _parse_numbered(raw, len(todo))))
        _validate_new_label_format(new_pairs)
        for src, dst in new_pairs:
            carried[src] = dst

    intended = [carried[l] for l in en_labels]
    out = apply(en_text, intended)
    if skeleton(out) != skeleton(en_text):
        raise ValueError("sidebar 結構被更動")

    # skeleton 相等只證明「位置」沒被動到，證明不了值本身 —— _quote 沒引號時
    # 一個看起來正常的字串仍可能被 yaml.safe_load 成 int/bool/None，或者
    # （即使型別仍是字串）被 YAML 的 flow scalar 規則悄悄改值（例如換行
    # fold 成空白）。這裡真的解析一次輸出，逐一比對每個 label 是否還原成
    # 當初打算寫入的值本身，不只是型別對。
    try:
        parsed = yaml.safe_load(out)
    except yaml.YAMLError as e:
        raise ValueError(f"輸出無法解析為 YAML: {e}") from e
    if parsed is None:
        raise ValueError("輸出無法解析為 YAML")
    _assert_labels_equal(list(_walk_labels(parsed)), intended)

    return out
