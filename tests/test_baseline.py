"""對修復前的 repo 執行 validate，鎖定已知缺陷數量。

這不是一般的 TDD 測試——它不是先紅後綠地驅動新功能，而是把「修復前
的 HEAD 有多少已知缺陷」量測出來，鎖成具體數字，用以證明 validate 的
八道關卡真的會對真實缺陷發紅（而不是一條從未紅過、形同註解的斷言）。

backfill 完成後，Task 22 會把這個檔案改寫為「全綠」斷言。

PRE_FIX / MERGE_BASE 必須是固定 commit，不能用 zh-tw-main 分支名——
PR 一旦合併，分支上的缺陷數就變了，這個測試會因為「我們修好了東西」
而變紅，卻仍然頂著「基線」的名字。

- PRE_FIX：`zh-tw-main` 修復前的凍結 tip。中文檔案內容與現況的量測對象。
- MERGE_BASE：每個中文檔案翻譯當下對應的英文原檔（各檔案的 merge-base，
  不是 `english-main` 現在的 HEAD）。用 `english-main` 現在的內容當來源
  會讓幾乎每個檔案都因為上游後續變動而紅，量出來的數字就失去意義。

以下數字是以本專案的 `validate.check_file` / `glossary.scan` /
`validate.simplified_chars` 邏輯對 PRE_FIX 實測得出：

- 結構失敗（gate 1 標題層級序列、gate 2 code fence 數）：15 檔。
  （早期調查用有 bug 的 fence 掃描器數出 19，其中 4 個是假陽性——
  對應的英文原檔該區塊其實被 HTML 註解掉了。以此處量測的 15 為準。）
- 未翻譯 frontmatter description/title（gate 4）：88 檔。
  （spec 記的 89 來自 `grep '^description:'` 的粗略掃描，多算一個。）
- 大陸用語（gate 7，僅計 code block 之外）：126 處。
  （spec 記的 143 是含 code block 內文字的原始 grep 數；glossary.scan
  會跳過 fenced code 與 inline code，126 才是驗證關卡實際會擋的數量。）
- 簡體殘留字（gate 8）：5 字，分布在 4 個檔案。
- 內部 anchor 連結（gate 5，check_links）：0 個無法解析——這一項現況
  已經是綠的，backfill 過程中必須維持綠，不能被重譯洗掉。
"""

import subprocess

import pytest

from scripts.zh_tw import frontmatter as fm
from scripts.zh_tw import glossary, validate

MERGE_BASE = "f2c0a93e1a0422078d3d051e4410ac3edc612016"
PRE_FIX = "0d4b8bea77f1a6195b589ded4067d287adb4379a"


def _show(ref: str, path: str) -> str | None:
    r = subprocess.run(
        ["git", "show", f"{ref}:{path}"], capture_output=True, text=True
    )
    return r.stdout if r.returncode == 0 else None


def _zh_files() -> list[str]:
    r = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "-z", PRE_FIX, "book", "reference"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [f for f in r.stdout.split("\0") if f.endswith(".md")]


@pytest.fixture(scope="module")
def zh_docs() -> dict[str, str]:
    """路徑 -> PRE_FIX 的中文內容。gate 5/7/8 只需要中文側，不需要英文來源
    （en 是否存在，跟這份文件裡有沒有大陸用語、簡體殘留字、可解析的 anchor
    連結完全無關）。若在此處也要求 en 存在，會把 book/testing/good-tests.md
    這種在 MERGE_BASE 找不到英文原檔的中文檔案排除掉——而它正是 gate 8
    的四個違規檔案之一，排除它會讓簡體殘留字從 5 少算成 4。
    """
    out = {}
    for path in _zh_files():
        zh = _show(PRE_FIX, path)
        if zh is not None:
            out[path] = zh
    return out


@pytest.fixture(scope="module")
def corpus(zh_docs) -> dict[str, tuple[str, str]]:
    """路徑 -> (PRE_FIX 的中文內容, MERGE_BASE 的英文原檔內容)。缺一則跳過——
    gate 1/2/3/4/6（check_file）需要中英文兩側才能比對，結構性缺英文來源
    的檔案（例如 MERGE_BASE 當時尚未存在對應英文原檔）本來就無法做這類比對。
    """
    out = {}
    for path, zh in zh_docs.items():
        en = _show(MERGE_BASE, path)
        if en is not None:
            out[path] = (zh, en)
    return out


@pytest.fixture(scope="module")
def failures(corpus) -> dict[str, list[str]]:
    out = {}
    for path, (zh, en) in corpus.items():
        errs = validate.check_file(zh, en)
        if errs:
            out[path] = errs
    return out


def test_structural_failures_baseline(failures):
    """gate 1、2：15 檔的標題層級序列或 code fence 數與英文來源不符。

    19 是調查階段用有 bug 的 fence 掃描器算出來的；修正掃描邏輯後為 15，
    移除的 4 個假陽性其英文原檔對應區塊被 HTML 註解掉了，不該計入 fence 數。
    """
    structural = [
        p
        for p, errs in failures.items()
        if any("標題層級序列" in e or "fence" in e for e in errs)
    ]
    assert len(structural) == 15, sorted(structural)


def test_severe_truncation_is_present(failures):
    """最嚴重的兩個截斷案例：reference/variables.md 英文 824 行對中文 36 行
    （68 個 fence 只剩 1 個存活），book/guides/code-quality-checklist.md
    英文 592 行對中文 24 行。兩者都必須落在結構失敗集合裡。
    """
    assert "reference/variables.md" in failures
    assert "book/guides/code-quality-checklist.md" in failures


def test_untranslated_description_baseline(failures):
    """gate 4：88 檔的 frontmatter description 或 title 仍是英文（不含 CJK）。

    spec 記的 89 來自 `grep '^description:'` 的粗掃，多算了一個；
    88 是以 frontmatter.split + TRANSLATABLE_KEYS + CJK 判定實測的結果。
    """
    untranslated = [p for p, errs in failures.items() if any("未翻譯" in e for e in errs)]
    assert len(untranslated) == 88, len(untranslated)


def test_glossary_violation_baseline(zh_docs):
    """gate 7：程式碼區塊（fence + inline code）以外，共 126 處大陸用語。

    spec 記的 143 是含 code block 在內的原始 grep 數。glossary.scan 會用
    protected_mask 跳過 fenced/縮排 code block 與 inline code span，故以
    126 為準——這才是驗證關卡實際會擋下、要求人工修正的數量。

    掃描對象是全部中文檔案（zh_docs），不是只有能配對到 MERGE_BASE 英文
    來源的子集：大陸用語跟這份文件有沒有可比對的英文原檔無關。
    """
    total = 0
    for zh in zh_docs.values():
        _, body = fm.split(zh)
        total += sum(glossary.scan(body).values())
    assert total == 126, total


def test_simplified_chars_baseline(zh_docs):
    """gate 8：簡體殘留字，共 5 字，分布在恰好 4 個檔案，字元集合恰好如下：

    - book/programmability/witness-pattern.md: {"個"}          -> 簡體「个」
    - book/testing/good-tests.md:              {"麼"}          -> 簡體「麽」
    - reference/functions.md:                  {"況"}          -> 簡體「况」
    - reference/structs.md:                    {"這", "種"}    -> 簡體「这」「种」

    simplified_chars() 回傳的是「原字元本身」（尚未轉換的簡體字），
    而不是轉換後的繁體字——這裡直接比對它在 body 中抓到的原字元。

    掃描對象同樣是全部中文檔案：book/testing/good-tests.md 在 MERGE_BASE
    找不到對應英文原檔（該檔案在翻譯當下尚未有英文來源可比對結構），若只
    掃能配對到 corpus 的子集，會把這個檔案排除掉，讓總數從 5 少算成 4。
    """
    per_file: dict[str, set[str]] = {}
    total = 0
    for path, zh in zh_docs.items():
        _, body = fm.split(zh)
        hits = validate.simplified_chars(body)
        if hits:
            per_file[path] = {ch for _line, ch in hits}
            total += len(hits)

    assert total == 5, total
    assert len(per_file) == 4, sorted(per_file)
    assert per_file == {
        "book/programmability/witness-pattern.md": {"个"},
        "book/testing/good-tests.md": {"麽"},
        "reference/functions.md": {"况"},
        "reference/structs.md": {"这", "种"},
    }, per_file


def test_anchor_links_currently_resolve(zh_docs):
    """gate 5（check_links）：現況所有內部 anchor 連結皆可解析，0 個錯誤。

    這是唯一現況已經全綠的關卡，也是最容易在 backfill 中被無意破壞的一個：
    若重譯過程整段換掉標題文字卻沒保留既有 {#id}，會把手寫的 anchor 全部
    洗掉，這裡就會由 0 變紅——它的作用正是攔住這種情況。
    """
    errs = validate.check_links(zh_docs)
    assert errs == [], errs
