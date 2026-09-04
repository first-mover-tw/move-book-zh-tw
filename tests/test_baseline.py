"""backfill 完成後的全 repo 不變式（原基線測試的改寫，plan Task 22）。

修復前基線（本測試曾釘 PRE_FIX=0d4b8bea 的普查值，見 git history）：
結構殘缺 15、未翻 description 88、違禁詞 126、簡體 5、anchor 問題 56。

2026-07-12：LEGACY_BODY_DEBT 債務全清（stash acb51154 手工翻譯合併 +
機械修復），豁免機制（scripts/zh_tw/debt.py）已移除，全語料零違規。
"""

import subprocess

from scripts.zh_tw import check_repo, frontmatter, glossary, manifest, validate


def _show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def _recorded_source(path: str, sha: str) -> str | None:
    r = subprocess.run(["git", "cat-file", "blob", sha], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def test_every_file_is_a_valid_translation_of_its_recorded_source():
    """全 repo 對**各自 manifest 記錄的那個英文 blob** 過全量 check_file，零豁免。

    2026-09-04 改寫（使用者裁決）。原本這裡是三條「翻譯零積壓」的斷言：
    `stale_files(english-main) == []`、`check_file(zh, english-main:HEAD)`、
    `zh 檔案集 == english-main 檔案集`。它們測的是**語料狀態不是程式行為**
    —— 上游一 sync 就全紅、翻完就綠，紅了也沒有任何程式碼要修（lessons L4
    定義的壞測試）。實測上游前進 131 檔之後，每個過期檔都「驗不過」，但那
    只是因為它是**舊版英文**的譯文，frontmatter key 與強調數本來就會不同。

    真正的不變式是這條：**每個中文檔都是它自己來源的合法譯文。** manifest
    存的就是 path → 英文 blob sha，資料本來就在。這條在上游前進時保持綠，
    在有人改壞中文檔、或 validate 迴歸時才紅 —— 那才是有程式碼要修的時候。

    這條測試上線時挖出 29 檔 85 處失效強調（被 131 條積壓噪音蓋住看不見），
    一度用 `_KNOWN_EMPHASIS_GAPS` 逐檔逐數字釘成基線。2026-09-04 已全部清完，
    豁免機制隨之移除 —— **回到零豁免**。要再加豁免請先讀 lessons L5：豁免額度
    只要不會因為「已經不需要了」而紅，就等於守衛從沒對它命名的缺陷紅過。

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
        if errs:
            failures[path] = errs
    assert failures == {}, failures


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
