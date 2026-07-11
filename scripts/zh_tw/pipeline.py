"""編排：分層 -> 翻譯 -> 注入 anchor -> 強制術語 -> 驗證 -> 寫檔。

驗證失敗一律 raise，絕不寫檔。
"""

import subprocess
from pathlib import Path

from . import anchors, chunking, frontmatter, glossary, manifest, sidebar, validate
from .backends import base

MERGE_BASE = "f2c0a93e1a0422078d3d051e4410ac3edc612016"
FRONTMATTER_ONLY_DELTA = 6
CHUNK_MAX_LINES = 250


def _show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def _prev_en(path: str, m: dict[str, str]) -> str:
    """取回這個中文檔當初賴以翻譯的英文原檔內容。

    manifest 記的是英文 blob SHA。31 筆 provenance 曾經斷掉（Task 13 修復）；
    仍然取不到時退回 merge-base 的同路徑內容。兩者皆失敗則回傳空字串，
    inject 會因此不沿用任何 anchor —— 這是安全的降級，位置猜測不是。
    """
    sha = m.get(path)
    if sha:
        r = subprocess.run(["git", "cat-file", "-p", sha], capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout
    return _show(MERGE_BASE, path) or ""


def _delta_lines(old_sha: str, new_sha: str) -> int:
    r = subprocess.run(
        ["git", "diff", "--numstat", old_sha, new_sha], capture_output=True, text=True
    )
    parts = r.stdout.split()
    return int(parts[0]) + int(parts[1]) if len(parts) >= 2 else 10_000


def tier(path: str, en_ref: str = "english-main") -> str:
    """A 層的前提是中文內文與其英文來源結構一致；不通過者強制降級 B 層。"""
    m = manifest.load()
    new_sha = manifest.blob_sha(en_ref, path)
    old_sha = m.get(path)
    zh = _show("HEAD", path)
    if zh is None or new_sha is None or old_sha is None:
        return "B"

    # provenance 損壞（blob 不在 repo）→ 以 merge-base 為代理
    if subprocess.run(["git", "cat-file", "-e", old_sha], capture_output=True).returncode:
        old_sha = manifest.blob_sha(MERGE_BASE, path)
        if old_sha is None:
            return "B"

    if _delta_lines(old_sha, new_sha) > FRONTMATTER_ONLY_DELTA:
        return "B"

    en_old = _show(MERGE_BASE, path)
    # spec §五：分層只看 gate 1、2。用全量 check_file 會把「description 未翻」
    # 這種 backfill 本身要修的缺陷當成降級理由（實測誤降 30 檔）。
    if en_old is None or validate.check_structure(zh, en_old):
        return "B"  # 結構驗證未過（例：reference/variables.md）
    return "A"


def translate_body(en_text: str, backend: base.Backend, max_lines: int = CHUNK_MAX_LINES) -> str:
    en_meta, en_body = frontmatter.split(en_text)
    zh_chunks = [backend.translate(c) for c in chunking.chunk(en_body, max_lines)]
    zh_body = chunking.join(zh_chunks)

    zh_meta = dict(en_meta)
    for key in frontmatter.TRANSLATABLE_KEYS & set(en_meta):
        if isinstance(en_meta[key], str):
            zh_meta[key] = backend.translate(en_meta[key], kind="text").strip()
    return frontmatter.join(zh_meta, zh_body)


def assemble(
    en_text: str,
    prev_zh_text: str,
    prev_en_text: str,
    backend: base.Backend,
    max_lines: int = CHUNK_MAX_LINES,
) -> str:
    """prev_en_text 是這個中文檔當初翻譯所依據的英文原檔。

    沒有它，anchors.inject 只能退回「不沿用任何 anchor」；**絕不可**退回位置配對。
    上游 #223 改動了 19/35 個含 anchor 檔案的標題序列，位置配對會把 anchor 靜默
    貼到錯誤的標題上，而 gate 6 的集合差看不出來（spec D10）。
    """
    translated = translate_body(en_text, backend, max_lines)
    zh_meta, zh_body = frontmatter.split(translated)
    _, en_body = frontmatter.split(en_text)
    _, prev_zh_body = frontmatter.split(prev_zh_text) if prev_zh_text else ({}, "")
    _, prev_en_body = frontmatter.split(prev_en_text) if prev_en_text else ({}, "")

    # 拼接完成後才注入 anchor：切段後每段的標題序列只是全域序列的子區間。
    zh_body, notes = anchors.inject_report(zh_body, en_body, prev_zh_body, prev_en_body)
    zh_body = glossary.enforce(zh_body)
    out = frontmatter.join(zh_meta, zh_body)

    errs = validate.check_file(out, en_text, prev_zh_text, prev_en_text)
    # gate 9 只掛這裡（新翻譯），不進 check_file：A 層的 body 是 legacy
    # 舊譯文（110/147 檔無後綴），掛進去會整批誤擋 —— 見 gate 9 docstring。
    errs += validate.check_heading_suffix(out, en_text)
    if errs:
        raise validate.ValidationError("; ".join(errs))
    for n in notes:
        print(f"  note: {n}")  # anchor 退役等資訊，警告但不阻斷
    return out


def rebuild_frontmatter_only(en_text: str, zh_text: str, backend: base.Backend) -> str:
    """A 層：內文原封不動，只接管上游 frontmatter。"""
    en_meta, _ = frontmatter.split(en_text)
    _, zh_body = frontmatter.split(zh_text)
    zh_meta = dict(en_meta)
    for key in frontmatter.TRANSLATABLE_KEYS & set(en_meta):
        if isinstance(en_meta[key], str):
            zh_meta[key] = backend.translate(en_meta[key], kind="text").strip()
    out = frontmatter.join(zh_meta, zh_body)
    errs = validate.check_file(out, en_text)
    if errs:
        raise validate.ValidationError("; ".join(errs))
    return out


def run(
    paths: list[str], backend_name: str, en_ref: str = "english-main", apply: bool = False
) -> tuple[int, dict[str, list[str]]]:
    backend = base.get(backend_name)
    m = manifest.load()
    ok, failed = 0, {}

    for path in paths:
        en = _show(en_ref, path)
        if en is None:
            failed[path] = [f"{path} 不存在於 {en_ref}"]
            continue
        prev = _show("HEAD", path) or ""
        try:
            if path in manifest.SIDEBAR_FILES:
                out = sidebar.translate(en, prev, backend)
            elif prev and tier(path, en_ref) == "A":
                out = rebuild_frontmatter_only(en, prev, backend)
            else:
                prev_en = _prev_en(path, m) if prev else ""
                out = assemble(en, prev, prev_en, backend)
        except Exception as e:  # noqa: BLE001
            failed[path] = [str(e)]
            continue

        if apply:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(out, encoding="utf-8")
            manifest.record(m, path, en_ref)
        ok += 1

    if apply:
        manifest.save(m)
    return ok, failed
