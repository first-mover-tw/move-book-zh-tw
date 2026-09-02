import argparse
import sys

from . import manifest, pipeline


def main() -> int:
    p = argparse.ArgumentParser(prog="python -m scripts.zh_tw")
    p.add_argument("--detect", action="store_true", help="列出需要翻譯的檔案（純 git，無 API 依賴）")
    p.add_argument("--orphans", action="store_true", help="列出上游已刪除的檔案")
    p.add_argument("--english-ref", default="english-main")
    p.add_argument("--backend", default="claude", choices=["fake", "claude", "gemini"])
    p.add_argument("--apply", action="store_true", help="實際寫檔（預設 dry-run）")
    p.add_argument("--limit", type=int, default=0, help="只處理前 N 個檔案，0 為不限")
    p.add_argument(
        "--max-lines", type=int, default=pipeline.CHUNK_MAX_LINES,
        help="翻譯 chunk 上限行數（長檔掉標題時可縮小）",
    )
    p.add_argument(
        "--result-jsonl", default=None,
        help="把本次執行的 ok/touched/failed 附加一行 JSON 到此檔（CI 用來判定"
             "「本輪有沒有進展」，不必從 git 狀態推論）",
    )
    p.add_argument("files", nargs="*")
    a = p.parse_args()

    if a.detect:
        for f in manifest.stale_files(a.english_ref):
            print(f)
        return 0
    if a.orphans:
        for f in manifest.orphans(a.english_ref):
            print(f)
        return 0

    paths = a.files or manifest.stale_files(a.english_ref)
    if a.limit:
        paths = paths[: a.limit]
    if not paths:
        print("沒有需要翻譯的檔案。")
        return 0

    ok, failed = pipeline.run(
        paths, a.backend, a.english_ref, a.apply, a.max_lines, a.result_jsonl
    )
    print(f"成功 {ok}，失敗 {len(failed)}")
    for path, errs in failed.items():
        print(f"  {path}: {'; '.join(errs)}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
