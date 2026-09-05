"""台灣用語術語表的掃描與強制替換。

模型的中文訓練語料以簡體為主，繁化後詞彙仍是大陸慣用語（「繁體字、大陸詞」）。
prompt 指示不可靠，故翻譯後一律以程式碼掃描並替換。
"""

import json
import re
from collections import Counter
from pathlib import Path

from . import anchors
from .pipeline_patterns import link_dest_spans

_DEFAULT = Path(__file__).parent / "glossary.json"
# 標記但不替換的詞表。格式與 glossary.json 相同（違禁詞 -> 正確用法），
# 差別只在**不進 enforce**。收在這裡的是「值得提醒人、卻不能機械替換」的
# 詞條 —— 多義詞或有子字串碰撞（lessons L9）。2026-09-02 外部 review 實測
# 的三個現場，也就是目前這張表的三個詞：
#   交易影響  「這筆交易影響了物件的所有權」→「這筆交易效果了…」（影響是動詞）
#   Move 封裝 「Move 封裝了狀態與行為」→「Move 套件了狀態與行為」
#   燃料費    「支付燃料費用」→「支付gas用」（子字串碰撞）
# 放進 enforce 表是靜默破壞句子；完全不收又等於下一批重翻照樣長回來。
# scan 會報（讓它顯形）、prompt_rules 會教（讓模型別寫）、enforce 不碰。
_SCAN_ONLY = Path(__file__).parent / "glossary_scan_only.json"

# CommonMark inline code 是「反引號 run + 同長度反引號 run 收尾」的 span，
# 內容可以跨行 —— 只有空白行（段落結束）會終止它。之前這裡用逐行 regex
# 遮罩 inline code，隱含假設「inline code 是單行 span」，那個假設是錯的：
# 一個跨行的 code span 會讓逐行 regex 完全遮不到它，術語替換因此鑽進
# code span 內部改字。修法是在整份 body 上算一份字元級遮罩，同時涵蓋
# fence / 縮排 code block（來自 anchors.code_lines()，行級）與 inline
# code span（這裡，字元級），scan() 和 enforce() 共用同一份遮罩，避免
# 兩者對「什麼算被保護」各自表述而互相漏檢/誤改。
#
# 反引號 run 的長度用具名群組 back-reference 匹配收尾 run；非貪婪的
# `[\s\S]` 允許跨行，但用 lookahead 擋掉「換行 + 只剩空白的一行」
# （= 段落分隔），對齊 CommonMark：未閉合的反引號不會把後面整份文件
# 都吃掉。
#
# CommonMark 規定開頭/收尾的反引號 run 都必須是「maximal」——不能是
# 更長的一串反引號中間夾的一段。單純的 back-reference `(?P=t)` 只保證
# 長度相同，不保證收尾 run 沒有再往左右延伸；`` `函數``` `` 這種收尾
# 前後還連著別的反引號的情形，CommonMark 判定「不是 code span」，但
# 舊 regex 會誤判成一個 code span，讓術語替換被靜默豁免。用
# `(?<!`)...(?<!`)(?P=t)(?!`)` 分別在開頭 run 前、收尾 run 前後加上
# 「不是反引號」的邊界斷言，強迫兩端都必須是 maximal run，才會對齊
# markdown-it-py 的 code_inline 判定。
#
# 開頭 run 用 possessive quantifier `` `++ ``（不是 `` `+ ``）：普通的
# `` `+ `` 是可回溯的貪婪量詞，當收尾找不到同長度的 maximal run 時，
# 引擎會把 `t` 回溯成更短的 run，把多出來的反引號當成普通內容——這會
# 從「開頭側」重新打開同一個非 maximal 漏洞（例如 `` ``函數` `` 只有
# 2+1 個反引號、CommonMark 判定沒有 code span，但可回溯的 `` `+ `` 會
# 把 `t` 縮成 1 個反引號硬湊出一個 span）。possessive 量詞禁止回溯，
# 一旦吃下整個 maximal run 就不再吐回去，開頭側因此也維持 maximal。
_CODE_SPAN = re.compile(r"(?<!`)(?P<t>`++)(?:(?!\n[ \t]*\n)[\s\S])*?(?<!`)(?P=t)(?!`)")


def load(path: str | None = None) -> dict[str, str]:
    return json.loads(Path(path or _DEFAULT).read_text(encoding="utf-8"))


def load_scan_only(path: str | None = None) -> dict[str, str]:
    """只回報、不替換的詞表（見 _SCAN_ONLY 的註解）。"""
    return json.loads(Path(path or _SCAN_ONLY).read_text(encoding="utf-8"))


def protected_mask(body: str) -> list[bool]:
    """逐字元遮罩：True 代表這個字元不可被術語替換碰到。

    保護來源有兩個，缺一不可：
    - fence / 縮排 code block（anchors.code_lines()，行級，區塊結構的
      真相來源在 anchors.py，這裡不重刻）。
    - inline code span（_CODE_SPAN，字元級，允許跨行）。

    **這份遮罩的語意是「哪裡是程式碼」，不是「哪裡不可以動」。** validate 的
    連結檢查、pipeline._repair_inpage_links、FakeBackend 都拿它當前者用；會
    改寫文字的消費端（enforce/scan/_repair_cjk_emphasis）要的是後者，用
    substitution_mask() / emphasis_mask()。2026-09-04 曾把 URLISH 直接併進
    這裡，結果連結檢查看不見連結、4 個測試轉紅 —— 擴張一個共用述詞的涵蓋
    範圍，等於偷改了所有消費端的語意（lessons L2）。

    inline code span 是「區塊內部」的構造，不可能跨越區塊邊界——一個
    fenced code block 的內容裡不會有 CommonMark 意義上的 inline code
    span，反之亦然。之前的作法是讓 _CODE_SPAN 掃過整份 body，只檢查
    「匹配的起點」有沒有落在 fence/縮排保護區內；這只堵住了起點，堵
    不住終點：一個在段落裡開頭的反引號，仍然可能在下一行的 fence 內部
    找到它的收尾反引號，讓這個 span 的匹配範圍整段跨進 fence，反而把
    fence 內容誤判成「被 code span 保護」、把段落裡的中文誤判成「還在
    保護區內」而漏檢。修法是把層級關係反過來：先用 anchors.code_lines()
    把 body 切成「連續非 code 行」的區段，_CODE_SPAN 只在每個區段內部
    各自執行。這讓「跨越區塊邊界」在結構上變得不可能——因為 regex
    根本看不到 fence/縮排區的字元，不會去比對它們。
    """
    n = len(body)
    protected = [False] * n
    lines = body.splitlines(keepends=True)
    code_line_set = anchors.code_lines(body)

    offsets = [0] * (len(lines) + 1)
    for i, line in enumerate(lines):
        offsets[i + 1] = offsets[i] + len(line)

    for i in range(len(lines)):
        if i in code_line_set:
            for j in range(offsets[i], offsets[i + 1]):
                protected[j] = True

    i = 0
    n_lines = len(lines)
    while i < n_lines:
        if i in code_line_set:
            i += 1
            continue
        j = i
        while j < n_lines and j not in code_line_set:
            j += 1
        seg_start, seg_end = offsets[i], offsets[j]
        for m in _CODE_SPAN.finditer(body[seg_start:seg_end]):
            start, end = m.span()
            for k in range(seg_start + start, seg_start + end):
                protected[k] = True
        i = j
    return protected


def _urlish_mask(body: str, *, protect_fragments: bool) -> list[bool]:
    """protected_mask() ∪ URLISH，可選擇是否連純頁內 fragment 一起保護。

    `protect_fragments` 是兩類消費端的分水嶺，兩邊需求**相反**：

    - **文字替換**（enforce/scan）要 False。`](#建立新套件)` 這種頁內錨點是從
      標題文字推導出來的 slug，標題被 enforce 改寫時錨點必須跟著改，否則就
      指不到任何東西。今天語料裡 6 處中文錨點之所以一致（hello-world 的
      `#建立新套件`、functions 的 `#回傳數值`、packages 的
      `#編譯期間的具名地址…`），正是因為同一個 `str.replace` 把標題與錨點
      一起改了。把 fragment 收進保護區＝凍結錨點卻放行標題，下一次 enforce
      就產出死連結。
    - **強調修復**（_repair_cjk_emphasis）要 True。它把 `_x_` 改成 `*x*`，
      對 slug 而言那是把字元換掉、錨點直接失效；而它又沒有「同步改標題」
      這回事，所以 fragment 必須凍結。

    外部 URL（`https://…`、autolink、相對路徑檔名）兩邊都要保護：它們不是從
    本文推導出來的，改了就是 404 與圖裂。
    """
    mask = protected_mask(body)
    # 判定權在 pipeline_patterns.link_dest_spans 一處（與 _repair_cjk_emphasis
    # 共用），這裡只做聯集。原本在這裡用 `startswith("](#")` 自己判「純頁內
    # fragment」，那是形態代理：跨檔 fragment 與角括號目的地都會誤判（外部
    # review 2026-09-04，lessons L2/L15）。
    for start, end in link_dest_spans(body, protect_fragments=protect_fragments):
        for k in range(start, end):
            mask[k] = True
    return mask


def substitution_mask(body: str) -> list[bool]:
    """逐字元遮罩：True 代表這個字元**不可被術語替換碰到**。

    = protected_mask()（程式碼）∪ 外部 URL／連結目的地／autolink，**但不含**
    純頁內 fragment（`](#中文標題)`，它必須跟著標題一起改，見 _urlish_mask）。
    給 glossary.enforce 與 glossary.scan 共用。

    為什麼 URL 要進來：含中文的 URL 在中文譯文裡完全可能出現，`位址`→`地址`、
    `字符串`→`字串` 這種機械替換會直接產出 404 與圖裂，而且**沒有任何 gate
    看得見** —— gate 10 只看 <em> 有沒有變少、prettier 不管語意、check_repo
    的連結檢查只驗 repo 內相對路徑，外部 URL 不在視野內。

    為什麼 scan() 也要一起豁免：否則含這些字的合法外部 URL 會讓 check_repo
    永久紅，而 enforce 又（正確地）不去修它 —— 有守衛卻沒有修復路徑的死鎖
    （lessons L16）。

    保護範圍到 destination 為止：連結**文字**與前後散文照樣替換，否則這道
    保護會從「別改 URL」擴張成「別改任何帶連結的句子」。

    `](dest "title")` 的 title 一併落在保護區內。title 是人可讀的提示文字、
    理論上該被替換，但為了讓 URLISH 維持**單一份**定義（與 _repair_cjk_emphasis
    共用同一個 pattern），這裡接受這個保守的過度保護。

    2026-09-04 之前這層保護只存在於 pipeline._repair_cjk_emphasis，它在
    protected_mask() 的結果上自己外掛一份；glossary 這一側沒有 —— 同一個
    不變式兩份實作、涵蓋範圍還不同（lessons L15）。
    """
    return _urlish_mask(body, protect_fragments=False)


def emphasis_mask(body: str) -> list[bool]:
    """逐字元遮罩：True 代表這個字元**不可被強調修復碰到**。

    = substitution_mask() 再加上純頁內 fragment。給
    pipeline._repair_cjk_emphasis 用，理由見 _urlish_mask 的 docstring。
    """
    return _urlish_mask(body, protect_fragments=True)


def _segments(body: str, mask: list[bool]):
    """回傳 (is_protected, segment) 序列，segment 依遮罩值切成連續區段。"""
    n = len(body)
    i = 0
    while i < n:
        cur = mask[i]
        j = i
        while j < n and mask[j] == cur:
            j += 1
        yield cur, body[i:j]
        i = j


def enforce(body: str, table: dict[str, str] | None = None) -> str:
    table = table or load()
    mask = substitution_mask(body)
    out = []
    for protected, seg in _segments(body, mask):
        if not protected:
            for bad, good in table.items():
                seg = seg.replace(bad, good)
        out.append(seg)
    return "".join(out)


def scan(body: str, table: dict[str, str] | None = None) -> dict[str, int]:
    """只掃 enforce 表。

    scan-only 的詞**不能**併進來：validate 的 gate 7 與 check_frontmatter
    都用預設 scan()，且任何 hit 一律轉成 error → 「這筆交易影響了物件的
    所有權」這種完全正確的中文會讓整個檔案的翻譯硬失敗，而 enforce 依設計
    不碰它 = 沒有任何自動修復路徑，每輪都要人工。那不是「標記但不替換」，
    是把靜默改壞句子換成合法句子炸掉管線。scan-only 走 scan_only_hits()，
    由 check_repo 以 warning 呈現、不影響 exit code。
    """
    table = table if table is not None else load()
    mask = substitution_mask(body)
    counts: Counter[str] = Counter()
    for protected, seg in _segments(body, mask):
        if protected:
            continue
        for bad in table:
            n = seg.count(bad)
            if n:
                counts[bad] += n
    return dict(counts)


def scan_only_hits(body: str) -> dict[str, int]:
    """scan-only 詞表的命中數。呈現用，**不得**餵給任何會 fail 的 gate。"""
    return scan(body, load_scan_only())


def prompt_rules(table: dict[str, str] | None = None) -> str:
    """兩張表都要教給模型，但措辭不同。

    scan-only 的詞不能事後機械替換（多義詞／子字串碰撞），只能在產出前就
    別寫出來；而且它們的「正確用法」往往不是換詞而是改寫句子 ——
    「交易影響了所有權」的替代不是「交易效果了所有權」。照 enforce 表那樣
    寫成「用 X 取代 Y」會教模型寫出不合語法的中文。
    """
    if table is not None:
        pairs = "、".join(f"{good}（不要用{bad}）" for bad, good in table.items())
        return (
            "使用台灣繁體中文的技術用語。務必遵守以下對照："
            f"{pairs}。程式碼與 inline code 中的識別字不要翻譯。"
        )
    pairs = "、".join(f"{good}（不要用{bad}）" for bad, good in load().items())
    avoid = "、".join(
        f"{bad}（術語語境請用{good}；若它在句中是動詞或其他詞性，請改寫句子而不是換詞）"
        for bad, good in load_scan_only().items()
    )
    return (
        "使用台灣繁體中文的技術用語。務必遵守以下對照："
        f"{pairs}。另外請避免這些寫法：{avoid}。"
        "程式碼與 inline code 中的識別字不要翻譯。"
    )
