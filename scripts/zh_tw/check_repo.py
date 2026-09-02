"""對 working tree 執行 repo 級驗證：anchor 連結解析、glossary 違禁詞、簡體殘留字。

這是 validate.check_file 的批次對照組：check_file 是逐檔比對中英文兩側，
這裡是跨檔案／全語料層級的檢查（連結解析需要看到所有檔案的 anchor 集合，
glossary/簡體殘留字則是彙總全語料的違規數）。

刻意不跑 prettier。prettier 一致性是獨立的驗收關卡（Task 22 / 最終的
`prettier --check`），把它塞進這裡會讓 check_repo 在一次性正規化跑之前，
對現有 50 個殘留檔案（缺結尾換行、`-   ` 清單標記）常態性回紅。這裡管的
是內容正確性（連結、術語、字形），不是格式。
"""

import sys
from pathlib import Path

from . import frontmatter, glossary, validate


def collect() -> dict[str, str]:
    """走訪 working tree（不是 git ref），回傳 book/ 與 reference/ 下所有
    .md 檔案的 路徑 -> 內容。"""
    files: dict[str, str] = {}
    for root in ("book", "reference"):
        for p in Path(root).rglob("*.md"):
            files[str(p)] = p.read_text(encoding="utf-8")
    return files


def main() -> int:
    files = collect()

    link_errs = validate.check_links(files)
    for e in link_errs:
        print(e, file=sys.stderr)

    glossary_total = 0
    for path, text in sorted(files.items()):
        _, body = frontmatter.split(text)
        hits = glossary.scan(body)
        for bad, n in sorted(hits.items()):
            print(f"{path}: 違禁詞 {bad} x{n}", file=sys.stderr)
            glossary_total += n

    simplified_total = 0
    for path, text in sorted(files.items()):
        _, body = frontmatter.split(text)
        for line, ch in validate.simplified_chars(body):
            print(f"{path}: 簡體殘留字 {ch!r}（第 {line + 1} 行）", file=sys.stderr)
            simplified_total += 1

    # frontmatter 可翻譯欄位的值另掃一輪：實測 5 個檔的違禁詞藏在
    # description/title 裡，body-only 掃描對它們回報假乾淨。
    for path, text in sorted(files.items()):
        meta, _ = frontmatter.split(text)
        for key in sorted(frontmatter.TRANSLATABLE_KEYS & set(meta)):
            value = meta[key]
            if not isinstance(value, str):
                continue
            for bad, n in sorted(glossary.scan(value).items()):
                print(f"{path}: frontmatter {key} 違禁詞 {bad} x{n}", file=sys.stderr)
                glossary_total += n
            for _line, ch in validate.simplified_chars(value):
                print(f"{path}: frontmatter {key} 簡體殘留字 {ch!r}", file=sys.stderr)
                simplified_total += 1

    # gate 10（強調在翻譯中消失）刻意不在這裡跑：判準是「跟英文原文比
    # 少了幾處」，需要中英配對，而 check_repo 只看 working tree 的中文側。
    # 它是 validate.check_file 的寫檔 gate —— 擋在產出那一刻，不是事後盤點。

    print(
        f"連結問題 {len(link_errs)} 個，違禁詞共 {glossary_total} 處，"
        f"簡體殘留字共 {simplified_total} 個",
        file=sys.stderr,
    )

    return 1 if (link_errs or glossary_total or simplified_total) else 0


if __name__ == "__main__":
    sys.exit(main())
