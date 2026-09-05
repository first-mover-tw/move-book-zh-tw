"""sidebar.yml 的 label 翻譯。

只有 label 的值需要翻譯；其餘每一行都必須與英文檔逐位元組相同。
慣例格式為「繁體中文 (Original English)」。
"""

import re
from pathlib import Path

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

# 「剪掉超過半數」這道啟發式的最小樣本數，見 _assert_prune_is_faithful。
_RATIO_GUARD_MIN_LABELS = 10

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
# 剪掉的章節不會遺失，但復原不是自動發生的：寫出去的就是剪過的檔案，所以
# 那個 label 也從沿用表消失了，回來時要重新呼叫一次 backend。真正讓它回來
# 的是 `manifest.sidebar_resync_needed()` —— 只看 manifest 的英文 blob SHA
# 的話，sidebar 被記成最新之後就再也不會被列為 stale。


class FailClosed(ValueError):
    """語料處於「需要人工處理」的合法中間態，不是程式缺陷。

    與其他 ValueError 的差別：其他的表示**判準或輸入壞了**（anchor/alias、
    flow style、exists 疑似有誤），這一個表示**程式判斷正確、但沒有安全的
    自動動作可做**。呼叫端（尤其是拿真實語料跑的測試）要能區分這兩者——
    把「不會 raise」當斷言等於斷言語料狀態（L3）。
    """


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


def _keep(node, path, exists, drops: list, seen: set, text: str) -> bool:
    """判定一個 sidebar 條目留不留，並把要刪的**子**條目記進 drops。

    判定只有這一處（L15：不讓修剪與驗證各自實作一份「什麼算缺陷」）。
    注意這**不是**後置條件的來源——後置條件獨立重算，才抓得到這裡判錯
    （見 `_assert_prune_is_faithful`）。
    """
    if id(node) in seen:
        # PyYAML 對 alias 回傳同一個 node 物件，start/end_mark 都指向 anchor
        # 的位置 —— 兩筆 drop 會拿到相同 span，刪兩次就刪掉別人的行
        # （外部 review B4）。sidebar.yml 不用 anchor，直接擋下。
        raise ValueError("不支援使用 YAML anchor/alias 的 sidebar")
    seen.add(id(node))

    # docusaurus 允許把 doc id 直接寫成字串（`- concepts/intro`），與
    # `- {id: concepts/intro}` 完全等價。不認它的話這種條目會走完整個
    # `_keep`（`_mapping` 回 {} → own/items/own_pages 全空）然後回 True，
    # 而且 `doc_ids()` 也看不到它 —— 剪枝、四條後置條件、baseline gate
    # 三處同時盲掉，build 照樣掛在原本要修的那個症狀上（外部 review B2）。
    if isinstance(node, yaml.nodes.ScalarNode):
        return exists(node.value)

    own = _doc_id(node)
    items = _mapping(node).get("items")
    if isinstance(items, yaml.nodes.SequenceNode):
        child_drops: list = []
        kept = 0
        for i, child in enumerate(items.value):
            if _keep(child, path + ["items", i], exists, child_drops, seen, text):
                kept += 1
            else:
                child_drops.append((path + ["items", i], _span(child, text), child))
        # 一個條目自己的頁面可能寫成 `link.id`（category）或直接 `id`
        # ——兩個都要檢查。第一版的 items 分支只看 link，帶 `id` 又帶
        # `items` 的節點永遠不會被檢查（外部 review B1）。
        own_pages = [i for i in (own, _link_id(node)) if i is not None]
        missing = [i for i in own_pages if not exists(i)]
        # 三種收尾，共同判準是「刪掉會不會讓一個**已經翻好**的頁面從側邊欄
        # 消失」——會的話一律 fail-closed 交回人工（L16：判定與修復不是同一
        # 個資訊量時，寧可死鎖也不要自動做一個不完整的決定）。
        if missing:
            if kept:
                raise FailClosed(
                    f"category 自己的頁面不存在但底下還有已翻好的項目: {missing}"
                    "（整個 category 刪掉會讓那些頁面從側邊欄消失，保留又會讓 build 失敗；"
                    "請先補上該檔或手動處理）"
                )
            return False  # 自己與所有子項都還沒翻 —— 整個 category 一起走
        if kept == 0:
            if own_pages:
                raise FailClosed(
                    f"category 的子項全都還沒翻，但它自己的頁面已存在: {own_pages}"
                    "（空的 items 會讓 build 失敗，刪掉整個 category 又會讓該頁面"
                    "從側邊欄消失；請先補上任一子項或手動處理）"
                )
            return False
        drops.extend(child_drops)
        return True

    # 葉節點：自己的 id 與 link.id 都算它的頁面。
    for doc_id in (own, _link_id(node)):
        if doc_id is not None and not exists(doc_id):
            return False
    return True


def _walk(node, path, exists, drops: list, seen: set, text: str) -> None:
    """走訪整棵樹；只有序列的元素能被刪（mapping 的值刪掉會破壞結構）。"""
    if isinstance(node, yaml.nodes.MappingNode):
        for k, v in node.value:
            _walk(v, path + [k.value], exists, drops, seen, text)
    elif isinstance(node, yaml.nodes.SequenceNode):
        # _keep 已經遞迴處理完整棵子樹（含 category 的 items），這裡不能再
        # 往下走，否則同一個條目會被記錄兩次。
        for i, child in enumerate(node.value):
            if not _keep(child, path + [i], exists, drops, seen, text):
                drops.append((path + [i], _span(child, text), child))


def _span(node, text: str) -> tuple[int, int]:
    """條目佔用的行區間 [start, end)，行號由 YAML 解析器給、不靠 regex 猜邊界。

    flow style（`- {label: A, id: a}`）整個條目在同一行，行刪除無法表達
    「刪掉這個 mapping 但留下同一行的其他內容」——直接擋下，不要靜默刪錯
    （外部 review B2：原本會退化成 span 寬度 0，什麼都沒刪卻回報成功）。

    `end_mark` 平常落在**下一個 token** 的起點（所以那一行不屬於本條目），
    但整份文件的最後一個節點沒有下一個 token，`end_mark` 會停在自己最後一行
    的行尾——檔案又沒有尾端換行時 `end_mark.line == start_mark.line`，區間
    寬度 0，那一行永遠刪不掉（外部 review B3）。用「這個位置之後還有沒有
    非空白內容」區分這兩種情形，而不是猜行號。
    """
    if getattr(node, "flow_style", False):
        raise ValueError("不支援 flow style 的 sidebar 條目（無法用行區間刪除）")
    start, end = node.start_mark.line, node.end_mark.line
    # `-` 單獨一行、內容縮排在下一行的寫法，節點的 start_mark 落在第一個
    # 鍵上，那個 `-` 不在區間裡，刪完會留下一個 null 條目。期望樹守衛擋得住
    # 但訊息指向刪除演算法，看不出是輸入寫法的問題（外部 review A1）。
    # 往回掃到第一個非空白字元，必須是同一行上的 `-`。固定看 col-2 會把
    # `-   id: a`（dash 後多個空白，完全合法）誤判成分行寫法，訊息還指向
    # 一個不存在的成因（外部 review B2）。
    head = text.splitlines()[start][:node.start_mark.column].rstrip()
    if not head.endswith("-"):
        raise ValueError(
            "不支援 `-` 與條目內容分行的 block sequence 寫法"
            f"（第 {start + 1} 行）：無法用行區間表達這個條目"
        )
    if isinstance(node, yaml.nodes.ScalarNode):
        # 純量條目（docusaurus 的 doc id 字串簡寫）的 `end_mark` 落在**自己的
        # 結尾**，不是下一個 token —— 直接用會得到寬度 0 的區間，那一行永遠
        # 刪不掉。它自己的最後一行要算進去。這與上面 EOF 那個情形同源：
        # 「end_mark 指向下一個 token」這個前提並非永遠成立。
        end = node.end_mark.line + 1
    if not text[node.end_mark.index:].strip():
        end = len(text.splitlines())
    return start, end


def _trim(lines: list[str], start: int, end: int, indent: int) -> int:
    """把 span 尾端回縮到真正屬於這個條目的最後一行。

    `end_mark` 落在**下一個 token**，中間的空行與註解要判斷歸屬：空行不屬於
    任何人，一律回縮；註解則看縮排——比條目起始欄位**淺**的是下一項的前導
    註解（回縮保留），與條目同深或更深的是這個條目自己的尾註（留在 span 裡
    一起刪掉）。只看「是不是註解」會把被刪條目的尾註留在原地變成縮排錯亂的
    孤兒行（外部 review B6）。
    """
    while end - 1 > start:
        line = lines[end - 1]
        stripped = line.strip()
        if not stripped:
            end -= 1
            continue
        if stripped.startswith("#") and len(line) - len(line.lstrip()) < indent:
            end -= 1
            continue
        break
    return end


def prune_missing(text: str, exists) -> tuple[str, list[str]]:
    """剪掉 doc id 無法解析成實體檔案的條目。

    回傳 `(剪過的 YAML 文字, 被剪掉的 doc id 清單)`。`exists(doc_id) -> bool`
    由呼叫端提供（pipeline 傳「磁碟上有沒有那個 .md，或這一批正要翻的」）。

    後置條件（L18：症狀消失不等於內容正確）。前兩條是**內容**判準，而且
    刻意不從 `_keep` 產生的 drops 推導——直接拿輸入與輸出各自重新抽一次
    doc id 集合再對 `exists` 比對，所以「`_keep` 判錯」本身抓得到。第一版
    四條後置條件全部由同一份 drops 推導，結構上不可能抓到過度刪除
    （外部 review C3，實測四條全拿掉測試不變色）：

      1. 不足刪：輸出裡每個 doc id 都通過 `exists`。
      2. 過度刪：輸入裡**通過** `exists` 的 doc id，一個都不能在輸出裡消失。
      3. 行刪除與樹修剪一致：`safe_load(輸出)` 等於對解析結果套用同一批
         刪除的期望樹（這條只交叉驗證兩種刪法，不驗判定，見上）。

    「只刪整行、不改任何一行的位元組」是實作的結構性質（唯一的寫入是
    `del kept_lines[start:end]`），不是後置條件——寫成 assert 也永遠不可能
    紅（外部 review A1）。它由黑箱測試 `test_prune_kept_lines_are_a_
    subsequence_of_the_original` 涵蓋。

    這四條都**無條件**執行，包括沒有任何東西要刪的路徑——早退會讓一個
    `_keep` 看不到的壞 doc id 完全不受檢查（外部 review B1）。
    """
    try:
        root = yaml.compose(text)
    except yaml.YAMLError as e:
        raise ValueError(f"sidebar 無法解析為 YAML: {e}") from e
    if root is None:
        raise ValueError("sidebar 無法解析為 YAML")

    drops: list = []
    _walk(root, [], exists, drops, set(), text)

    lines = text.splitlines(keepends=True)
    spans = sorted(
        (_trim(lines, s, e, n.start_mark.column), s)
        for _p, (s, e), n in drops
    )
    kept_lines = list(lines)
    for end, start in reversed(spans):
        del kept_lines[start:end]
    out = "".join(kept_lines)

    # 整個 category 被刪時它自己沒有 doc id，用 label 回報才看得懂是哪一塊。
    dropped_ids = [
        _doc_id(n) or _link_id(n) or _label_of(n) or "/".join(map(str, path))
        for path, _s, n in drops
    ]

    _assert_prune_is_faithful(text, out, exists, dropped_ids)

    if drops:
        expected = yaml.safe_load(text)
        for path, _s, _n in sorted(drops, key=lambda d: d[0], reverse=True):
            _drop_from_data(expected, path)
        try:
            got = yaml.safe_load(out)
        except yaml.YAMLError as e:
            raise ValueError(f"剪枝後的輸出無法解析為 YAML: {e}") from e
        if got != expected:
            raise ValueError("剪枝後的 YAML 與期望樹不符（行刪除與樹修剪不一致）")

    return out, dropped_ids


def _drop_from_data(data, path):
    """對 safe_load 出來的結構套用同一條 path 的刪除，產生期望樹。"""
    cur = data
    for key in path[:-1]:
        cur = cur[key]
    del cur[path[-1]]


def _assert_prune_is_faithful(text: str, out: str, exists, dropped_ids: list) -> None:
    """獨立於 drops 重新抽 doc id 集合，驗證「該刪的刪了、不該刪的都還在」。"""
    try:
        before, after = doc_ids(text), doc_ids(out)
    except yaml.YAMLError as e:  # 刪錯行導致輸出解析不了 —— 收斂成本模組的契約
        raise ValueError(f"剪枝後的輸出無法解析為 YAML: {e}") from e

    lost = [i for i in before if exists(i) and i not in after]
    if lost:
        raise ValueError(f"剪枝刪掉了本來存在的 doc id（過度刪除）: {lost[:5]}")

    bad = [i for i in after if not exists(i)]
    if bad:
        raise ValueError(f"剪枝後仍有無法解析的 doc id: {bad[:5]}")

    # `exists` 是這裡唯一的真相來源，判準本身寫錯（路徑相對錯目錄、副檔名
    # 打錯）沒有任何內部檢查抓得到——只剩「剪掉的比例異常」這個啟發式。
    # 分母與分子必須同單位：第一版拿「條目筆數」比「label 總數」，一個
    # category 被刪算 1 筆但帶走整串子項，實測 110 個 label 剪到剩 1 個
    # 仍然不觸發（外部 review C2）。這裡兩邊都數 label。
    #
    # 兩段判準：
    #   * 全空是無歧義的不變式——一份沒有任何條目的 sidebar 永遠不對。
    #   * 比例只在條目夠多時才有意義。翻譯早期「三章翻了一章」是完全正常的
    #     狀態，小樣本套比例會把它誤判成判準有誤（外部 review B5）；真實的
    #     book/reference sidebar 分別是 110 與 40 個 label，遠在門檻之上。
    total, kept = len(_LABEL.findall(text)), len(_LABEL.findall(out))
    if total and kept == 0:
        raise ValueError(f"剪枝後 sidebar 一個條目都不剩：{dropped_ids[:5]}")
    if total >= _RATIO_GUARD_MIN_LABELS and kept * 2 < total:
        raise ValueError(
            f"剪掉的條目過多（剩 {kept}/{total} 個 label），"
            f"疑似 exists 判準有誤：{dropped_ids[:5]}"
        )


def _item_type(node) -> str | None:
    """條目的**有效**型別。

    沒寫 `type` 時是 `doc` —— 這是 `site/src/plugins/yaml-sidebar.ts` 補的
    （`if (item.type === undefined) item.type = 'doc'`），不是 docusaurus 的
    預設。真實語料的多數條目正是這個形狀。
    """
    t = _mapping(node).get("type")
    if t is None:
        return "doc"
    return t.value if isinstance(t, yaml.nodes.ScalarNode) else None


def doc_ids(text: str) -> list[str]:
    """會被 docusaurus 檢查「這個 doc 存不存在」的 id，依出現順序。

    這個函式的判準必須逐段等於 `collectSidebarDocIds`
    （`@docusaurus/plugin-content-docs/lib/sidebars/utils.js`）—— 那正是
    產生 `These sidebar document ids do not exist` 這個 build 失敗的函式，
    也就是 `prune_missing` 存在的唯一理由。所以：

      * `type: doc`（含省略 type 的預設）→ 收 `id`
      * 序列裡的字串簡寫 `- some/doc` → 收（normalizeItem 會轉成 doc 條目）
      * `type: category` → 只在 `link.type == 'doc'` 時收 `link.id`，再遞迴
        `items`
      * `type: ref` / `type: link` / 未知型別 → **不收**。ref 的 id 不在
        `collectSidebarDocIds` 裡，dangling ref 不會觸發那個 build 失敗；
        多收等於讓合法 sidebar 被 fail-closed 擋死，而那個方向沒有自動
        修復路徑（lessons L21）。
      * `customProps` 是任意使用者資料（`Record<string, unknown>`），
        整棵子樹不看（第七輪 B1、第八輪 B2）。

    判準不再由我推論：`tests/test_sidebar_oracle.py` 拿上游程式碼當 oracle
    對真實語料與隨機 sidebar 逐一比對（R6→R9 四輪震盪的根因，見 L20）。
    """
    root = yaml.compose(text)
    out: list[str] = []

    def walk_item(node) -> None:
        m = _mapping(node)
        t = _item_type(node)
        if t == "category":
            # `link` 也可以是 `{type: 'generated-index'}`，那個沒有 doc id。
            link = m.get("link")
            if link is not None and _mapping(link).get("type") is not None:
                lt = _mapping(link)["type"]
                if isinstance(lt, yaml.nodes.ScalarNode) and lt.value == "doc":
                    did = _doc_id(link)
                    if did is not None:
                        out.append(did)
            walk_items(m.get("items"))
        elif t == "doc":
            did = _doc_id(node)
            if did is not None:
                out.append(did)

    def walk_items(node) -> None:
        """`node` 是條目序列。字串簡寫只在這個位置成立 —— 對「任何序列裡的
        任何純量」都套用的話，`customProps` 底下的字串陣列（docusaurus 官方
        例子的 `badges: ['new', 'green']`）會被當成 doc id，一個**合法**的
        sidebar 就被 fail-closed 擋死（第七輪 B1）。"""
        if not isinstance(node, yaml.nodes.SequenceNode):
            return
        for c in node.value:
            if isinstance(c, yaml.nodes.ScalarNode):
                out.append(c.value)
            elif isinstance(c, yaml.nodes.MappingNode):
                walk_item(c)

    # 根 mapping 的每個值都是條目序列（key 是 sidebar id，如 `bookSidebar`）。
    if isinstance(root, yaml.nodes.MappingNode):
        for _k, v in root.value:
            walk_items(v)
    else:
        walk_items(root)
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


def resync_needed(path: str, upstream_text: str) -> bool:
    """這份 sidebar 是否該重新同步。兩個方向都要看：

      * **少列**：上游列著、我們沒列，而那個 `.md` 已經翻好 —— 上一批被剪掉
        的章節翻好了，該回來。
      * **多列**：我們列著、但那個 `.md` 不存在 —— `_doc_exists` 對「本批次
        正要翻的檔案」是樂觀判定（一律當存在），那個檔案要是翻譯失敗（配額
        用盡是 workflow 明確容忍的情況），sidebar 就帶著一個 dangling doc id
        落盤，docusaurus build 掛掉。只看少列的方向沒有任何回收機制
        （外部 review B3）。

    同步會剪掉「還沒翻」的章節，但判準只能看**當下**磁碟上有什麼，而 `run()`
    是分批的（CI `BATCH_SIZE: 3`）：`book/sidebar.yml` 在 `git ls-tree` 排序裡
    位於第 94 位，後面還有 22 個 `.md`。上游一次新增三章以上時（那必然也會動
    sidebar.yml），排在後面的章節在輪到 sidebar 時還沒落盤，會被剪掉；
    `manifest.record` 隨即把 sidebar 記成最新，而 `stale_files` 只比對英文
    blob SHA，於是那些章節即使後來翻好也永遠回不到側邊欄（外部 review C1）。

    **終止性**：正常路徑會終止 —— 少列的翻好後同步一次就進 `have`，多列的
    同步一次就被剪掉，兩個方向下輪都是 False。永遠不會翻的章節（本地沒有
    `.md`）不會讓它為真，所以不會每輪 cron 白燒一個批次額度；這是「剪到東西
    就不 record」那個做法的病理，刻意不採用。

    **但這不是無條件的**：`_keep` 的兩個 fail-closed 分支（category 自己的頁面
    缺失卻有存活子項 / 子項全缺但自己的頁面存在）會讓 `prune_missing` 拋例外，
    `run()` 記成 failed、不寫檔也不 record，於是狀態原封不動、下輪又被列出來
    —— 自環，要人工處理才離得開（外部 review B1）。斷路器（連續 N 輪同一個
    sidebar 失敗就告警／移出候選）是獨立工項，見 tasks/notes.md。
    """
    from . import manifest  # 延後 import：避免與 manifest 的載入順序耦合

    local = manifest.REPO_ROOT / path
    if not local.is_file():
        return False
    try:
        upstream = doc_ids(upstream_text)
        have = set(doc_ids(local.read_text(encoding="utf-8")))
    except Exception:  # noqa: BLE001 —— 讀不了/解析不了就交給正常的同步流程
        return False
    parent = local.parent

    def translated(doc_id: str) -> bool:
        return (parent / f"{doc_id}.md").is_file()

    missing_from_ours = any(i not in have and translated(i) for i in upstream)
    dangling_in_ours = any(not translated(i) for i in have)
    return missing_from_ours or dangling_in_ours
