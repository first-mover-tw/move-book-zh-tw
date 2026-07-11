"""編排：分層 -> 翻譯 -> 注入 anchor -> 強制術語 -> 驗證 -> 寫檔。

驗證失敗一律 raise，絕不寫檔。
"""

import re
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
    # 同一 blob 的 delta 是 0；`git diff --numstat` 對它輸出空字串，
    # 不擋在這裡會掉進下面的 fail-closed 哨兵，把已 heal 的檔案誤判 B。
    if old_sha == new_sha:
        return 0
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
            # enforce 與 check_frontmatter 的值掃描同進退：backend 翻出違禁詞
            # 是決定性可修的，炸掉會把 B 路徑變成無自動出路的死鎖。
            zh_meta[key] = glossary.enforce(backend.translate(en_meta[key], kind="text").strip())
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

    # 標題修復在 anchor 注入之前（注入以最終標題文字為準）。
    zh_body = _repair_headings(zh_body, en_body, backend)
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


_TRAILING_PAREN = re.compile(r"\s*[（(]([^()（）]*)[)）]\s*$")


def _repair_headings(zh_body: str, en_body: str, backend: base.Backend) -> str:
    """gate 9 缺陷的修復 pass（enforce 與 gate 同進退：gate 擋得住的、backend
    又常犯的缺陷，必須有自動修復路徑，否則是結構性死鎖）。

    - 已翻譯只缺「(English)」後綴 → 決定性補上（Model vs Code 分工：格式化
      不指望 LLM）；先剝掉結尾與英文標題重複的括號組，避免疊床架屋。
    - verbatim 未翻 → 單標題重譯（kind="heading"，短輸入可靠得多）。
    - 修復候選仍過不了 heading_suffix_error 就保留原樣，交給 gate 9 擋。
    - 標題數不符不修（by-index 配對不成立），交給 gate 1。
    - 判定與 gate 9 共用 validate.heading_suffix_error（單一權威實作）。
    """
    zh_h = anchors.headings(zh_body)
    en_h = anchors.headings(en_body)
    spans = anchors._heading_spans(zh_body)
    if len(zh_h) != len(en_h) or len(spans) != len(zh_h):
        return zh_body

    lines = zh_body.splitlines(keepends=True)
    for (start, end, level, markup), (_, zh_t), (_, en_t) in zip(spans, zh_h, en_h):
        if markup not in ("#", "##", "###", "####", "#####", "######") and not markup.startswith("#"):
            continue  # setext 標題（兩行）不在此修，交給 gate
        if end - start != 1:
            continue
        if validate.heading_suffix_error(zh_t, en_t) is None:
            continue
        en_clean = en_t.strip()
        if validate.CJK.search(zh_t):
            base_txt = zh_t.strip()
            # 剝掉結尾與英文標題重複的括號組（「… (Tags and Releases) (Git)」）
            while (m := _TRAILING_PAREN.search(base_txt)):
                inner = m.group(1).strip()
                stripped = base_txt[: m.start()].rstrip()
                if inner and stripped and inner.lower() in en_clean.lower():
                    base_txt = stripped
                else:
                    break
            candidate = f"{base_txt} ({en_clean})"
        else:
            candidate = backend.translate(en_clean, kind="heading").strip()
        if candidate and validate.heading_suffix_error(candidate, en_clean) is None:
            ending = anchors._line_ending(lines[start])
            lines[start] = f"{'#' * level} {candidate}{ending}"
    return "".join(lines)


def rebuild_frontmatter_only(
    en_text: str, zh_text: str, backend: base.Backend, prev_en_text: str = ""
) -> str:
    """A 層：內文原封不動，只接管上游 frontmatter。

    寫檔 gate 只涵蓋本函式生成的部分（結構 + frontmatter）：body 是 legacy
    舊譯文，拿它的既有違禁詞/簡體當否決會讓 A 層檔 hard-fail 且無自動修復
    路徑（body 不重譯、tier 也不會降級）——與 tier 只看 check_structure
    （spec §五）是同一組設計，兩邊一起改才不會死鎖。

    欄位值沿用優先於重算（與 anchors 的 carry-forward 同原則）：英文原文
    未變且既有值已是中文的欄位，沿用舊值（過 glossary.enforce）——第一次
    apply 實測 53 個欄位被白重翻，損失既有審定術語（友元 → 朋友）。舊值
    帶簡體字（無決定性修法）或沿用前提不成立時，退回重翻。"""
    en_meta, _ = frontmatter.split(en_text)
    zh_meta_old, zh_body = frontmatter.split(zh_text)
    prev_en_meta, _ = frontmatter.split(prev_en_text) if prev_en_text else ({}, "")
    zh_meta = dict(en_meta)
    for key in frontmatter.TRANSLATABLE_KEYS & set(en_meta):
        if not isinstance(en_meta[key], str):
            continue
        old = zh_meta_old.get(key)
        if (
            prev_en_meta.get(key) == en_meta[key]
            and isinstance(old, str)
            and validate._CJK.search(old)
        ):
            carried = glossary.enforce(old)
            if not validate.simplified_chars(carried) and not glossary.scan(carried):
                zh_meta[key] = carried
                continue
        zh_meta[key] = glossary.enforce(backend.translate(en_meta[key], kind="text").strip())
    out = frontmatter.join(zh_meta, zh_body)
    errs = validate.check_structure(out, en_text) + validate.check_frontmatter(out, en_text)
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
                out = rebuild_frontmatter_only(en, prev, backend, _prev_en(path, m))
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
