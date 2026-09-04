"""backfill 完成後的全 repo 不變式（原基線測試的改寫，plan Task 22）。

修復前基線（本測試曾釘 PRE_FIX=0d4b8bea 的普查值，見 git history）：
結構殘缺 15、未翻 description 88、違禁詞 126、簡體 5、anchor 問題 56。

2026-07-12：LEGACY_BODY_DEBT 債務全清（stash acb51154 手工翻譯合併 +
機械修復），豁免機制（scripts/zh_tw/debt.py）已移除，全語料零違規。
"""

import subprocess

from markdown_it import MarkdownIt

from scripts.zh_tw import check_repo, frontmatter, glossary, manifest, validate


def _show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


# 「英文有 <em>、中文渲染不出來」的已知缺口，2026-09-04 全語料普查。
# 值 = 英文 <em> 數 − 中文 <em> 數。**只准縮小，不准長大，不准出現新檔案。**
#
# 成因兩類，都沒有自動修復路徑（判定與修復不是同一個資訊量，lessons L16）：
#   (a) `*中文 (English)*CJK` —— 收尾 `*` 前面是 `)`（標點）、後面是 CJK，
#       依 CommonMark 不算 right-flanking，強調收不了尾。這是本專案「中文
#       (English)」標題慣例自己造成的。修法是把括號移出強調範圍：
#       `被*移動 (moved)*進` → `被*移動* (moved) 進`（已在 entry-functions.md 示範）。
#   (b) 英文的 `_em_` 被譯成 `**粗體**` —— 渲染得出來，但元素錯了。
#
# 為什麼釘基線而不是直接全修：85 處要逐處對照英文原文判斷「這個 em 對應到
# 中文哪一段」，是人工工作不是機械替換。釘住讓它不能默默長回去，背景慢慢清。
# 清完一個檔就把它從這張表刪掉（測試會強迫你刪 —— 缺口變 0 而表上還有值會紅）。
#
# 2026-09-04 codex 排乾第一批順手清掉兩檔（重譯時強調寫對了）：
#   book/guides/upgradeability-practices.md  1 → 0
#   book/move-basics/copy-ability.md         3 → 0
# 第二批再清掉三檔：
#   book/move-basics/generics.md             4 → 0
#   book/move-basics/references.md           1 → 0
#   book/move-basics/struct-methods.md       3 → 0
# 第三批再清掉兩檔：
#   book/object/digital-assets.md            1 → 0
#   book/object/index.md                     1 → 0
# 是 test_known_emphasis_gaps_table_has_no_stale_entries 逼出來的。
_KNOWN_EMPHASIS_GAPS: dict[str, int] = {}


def _em_count(text: str) -> int:
    _, body = frontmatter.split(text)
    return MarkdownIt("commonmark").render(body).count("<em>")


def _recorded_source(path: str, sha: str) -> str | None:
    r = subprocess.run(["git", "cat-file", "blob", sha], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def test_every_file_is_a_valid_translation_of_its_recorded_source():
    """全 repo 對**各自 manifest 記錄的那個英文 blob** 過全量 check_file。

    2026-09-04 改寫（使用者裁決）。原本這裡是三條「翻譯零積壓」的斷言：
    `stale_files(english-main) == []`、`check_file(zh, english-main:HEAD)`、
    `zh 檔案集 == english-main 檔案集`。它們測的是**語料狀態不是程式行為**
    —— 上游一 sync 就全紅、翻完就綠，紅了也沒有任何程式碼要修（lessons L4
    定義的壞測試）。實測上游前進 131 檔之後，每個過期檔都「驗不過」，但那
    只是因為它是**舊版英文**的譯文，frontmatter key 與強調數本來就會不同。

    真正的不變式是這條：**每個中文檔都是它自己來源的合法譯文。** manifest
    存的就是 path → 英文 blob sha，資料本來就在。這條在上游前進時保持綠，
    在有人改壞中文檔、或 validate 迴歸時才紅 —— 那才是有程式碼要修的時候。

    唯一的豁免是 `_KNOWN_EMPHASIS_GAPS`（見上方註解）：既有的 85 處強調缺口
    是人工待辦，不是程式缺陷。豁免是**逐檔逐數字**的，缺口長大或出現新檔
    一樣紅。

    積壓數字本身沒有消失，它在 `python -m scripts.zh_tw --detect` 與
    check_repo 的輸出裡，那是儀表板該待的地方，不是 pytest。
    """
    m = manifest.load()
    failures: dict[str, list[str]] = {}
    for path, zh in check_repo.collect().items():
        sha = m.get(path)
        if sha is None:
            # manifest 沒記錄 = 這個檔從沒被管線翻過（待翻佇列），不是缺陷
            continue
        en = _recorded_source(path, sha)
        if en is None:
            failures[path] = [f"manifest 記錄的英文 blob {sha[:8]} 不存在於 repo"]
            continue
        errs = validate.check_file(zh, en)
        non_em = [e for e in errs if "強調在翻譯中消失" not in e]
        if non_em:
            failures[path] = non_em
        if len(non_em) == len(errs):
            continue
        gap = _em_count(en) - _em_count(zh)
        allowed = _KNOWN_EMPHASIS_GAPS.get(path)
        if allowed is None:
            failures.setdefault(path, []).append(f"新出現的強調缺口 {gap} 處")
        elif gap > allowed:
            failures.setdefault(path, []).append(f"強調缺口從 {allowed} 長到 {gap}")
    assert failures == {}, failures


def test_known_emphasis_gaps_table_has_no_stale_entries():
    """清乾淨的檔案必須從 `_KNOWN_EMPHASIS_GAPS` 刪掉。

    沒有這條，那張表就會變成永遠不會縮小的免死金牌 —— 修好了也沒人知道，
    下一次回歸又躲進同一個豁免額度裡（lessons L5：豁免額度只要不會因為
    「已經不需要了」而紅，就等於守衛從沒對它命名的缺陷紅過）。
    """
    m = manifest.load()
    files = check_repo.collect()
    stale = {}
    for path, allowed in _KNOWN_EMPHASIS_GAPS.items():
        zh = files.get(path)
        sha = m.get(path)
        if zh is None or sha is None:
            stale[path] = "已不在語料/manifest 中"
            continue
        en = _recorded_source(path, sha)
        if en is None:
            continue
        gap = _em_count(en) - _em_count(zh)
        if gap < allowed:
            stale[path] = f"實際缺口已降到 {gap}，表上還寫 {allowed}"
    assert stale == {}, stale


def test_no_orphans():
    assert manifest.orphans("english-main") == []




def test_all_anchor_links_resolve():
    assert validate.check_links(check_repo.collect()) == []


def test_no_glossary_or_simplified_violations_anywhere():
    for path, text in check_repo.collect().items():
        _, body = frontmatter.split(text)
        assert not glossary.scan(body), path
        assert not validate.simplified_chars(body), path


def test_no_zh_file_lacks_an_english_source():
    """中文語料不得有英文端沒有的檔（孤兒）。

    2026-09-04 收斂（使用者裁決）：原本斷言 `zh 集合 == en 集合`，雙向都要
    相等。其中「en 有的 zh 都要有」是**積壓**方向 —— 上游新增一個檔就紅，
    但沒有任何程式碼要修，翻了就綠（實測紅在 `book/programmability/scratchpad.md`
    這個從沒翻過的檔）。真不變式只有反方向：中文端不該憑空多出檔案，那代表
    上游刪檔後我們沒跟上，或是有人手動加了不該加的東西。
    """
    en = {f for f in manifest.tracked_files("english-main") if f.endswith(".md")}
    zh = set(check_repo.collect())
    assert zh - en == set(), sorted(zh - en)
