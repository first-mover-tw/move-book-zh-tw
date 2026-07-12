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


def test_no_stale_files():
    assert manifest.stale_files("english-main") == []


def test_no_orphans():
    assert manifest.orphans("english-main") == []


def test_every_file_passes_validation():
    """全 repo 對 english-main 過全量 check_file，零豁免。"""
    files = check_repo.collect()
    failures = {}
    for path, zh in files.items():
        en = _show("english-main", path)
        if en is None:
            failures[path] = ["英文來源不存在"]
            continue
        errs = validate.check_file(zh, en)
        if errs:
            failures[path] = errs
    assert failures == {}, failures


def test_all_anchor_links_resolve():
    assert validate.check_links(check_repo.collect()) == []


def test_no_glossary_or_simplified_violations_anywhere():
    for path, text in check_repo.collect().items():
        _, body = frontmatter.split(text)
        assert not glossary.scan(body), path
        assert not validate.simplified_chars(body), path


def test_file_set_matches_english_main():
    en = {f for f in manifest.tracked_files("english-main") if f.endswith(".md")}
    zh = set(check_repo.collect())
    assert zh == en, {"缺少": sorted(en - zh), "多出": sorted(zh - en)}
