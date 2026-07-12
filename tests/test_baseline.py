"""backfill 完成後的全 repo 不變式（原基線測試的改寫，plan Task 22）。

修復前基線（本測試曾釘 PRE_FIX=0d4b8bea 的普查值，見 git history）：
結構殘缺 15、未翻 description 88、違禁詞 126、簡體 5、anchor 問題 56。

與 plan Task 22 模板的差異（使用者裁決，2026-07-11 tier 決策）：
「全部歸零」不含 A 層檔的 legacy body 違禁詞/簡體 —— 該範圍與使用者的
reference/ 翻譯 WIP（stash acb51154）重疊，不機器重譯、待人工清理。
債務清單釘死於 LEGACY_BODY_DEBT：出現新檔或新錯誤類型即紅；清理一檔
就從清單移除一檔，直到空集合後刪除本豁免。
"""

import subprocess

from scripts.zh_tw import check_repo, frontmatter, glossary, manifest, validate

# 只允許「違禁詞 / 簡體殘留字」兩類 body 債務的檔案（2026-07-12 實測 16 檔）。
LEGACY_BODY_DEBT = frozenset({
    "book/appendix/glossary.md",
    "book/appendix/transfer-functions.md",
    "book/your-first-move/hello-world.md",
    "reference/constants.md",
    "reference/control-flow.md",
    "reference/control-flow/labeled-control-flow.md",
    "reference/control-flow/loops.md",
    "reference/equality.md",
    "reference/extensions.md",
    "reference/friends.md",
    "reference/functions.md",
    "reference/functions/macros.md",
    "reference/method-syntax.md",
    "reference/packages.md",
    "reference/primitive-types/vector.md",
    "reference/structs.md",
})


def _show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def test_no_stale_files():
    assert manifest.stale_files("english-main") == []


def test_no_orphans():
    assert manifest.orphans("english-main") == []


def test_every_file_passes_validation_modulo_pinned_body_debt():
    """全 repo 對 english-main 過全量 check_file；唯一豁免是 LEGACY_BODY_DEBT
    檔案的違禁詞/簡體錯誤。豁免以「檔案集合相等」斷言 —— 清理後必須同步
    收縮清單，新增債務檔或新錯誤類型都會紅。"""
    files = check_repo.collect()
    debt_files = set()
    other_failures = {}
    for path, zh in files.items():
        en = _show("english-main", path)
        if en is None:
            other_failures[path] = ["英文來源不存在"]
            continue
        errs = validate.check_file(zh, en)
        if not errs:
            continue
        rest = [
            e for e in errs
            if not (e.startswith("違禁詞") or e.startswith("簡體殘留字"))
        ]
        if rest:
            other_failures[path] = rest
        else:
            debt_files.add(path)
    assert other_failures == {}, other_failures
    assert debt_files == set(LEGACY_BODY_DEBT), {
        "新增債務檔": sorted(debt_files - LEGACY_BODY_DEBT),
        "已清理應移出清單": sorted(LEGACY_BODY_DEBT - debt_files),
    }


def test_all_anchor_links_resolve():
    assert validate.check_links(check_repo.collect()) == []


def test_glossary_violations_only_in_pinned_debt_files():
    for path, text in check_repo.collect().items():
        _, body = frontmatter.split(text)
        if glossary.scan(body) or validate.simplified_chars(body):
            assert path in LEGACY_BODY_DEBT, path


def test_file_set_matches_english_main():
    en = {f for f in manifest.tracked_files("english-main") if f.endswith(".md")}
    zh = set(check_repo.collect())
    assert zh == en, {"缺少": sorted(en - zh), "多出": sorted(zh - en)}
