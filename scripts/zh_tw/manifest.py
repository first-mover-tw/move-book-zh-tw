"""翻譯 manifest:路徑 -> 該中文檔賴以翻譯的英文 blob SHA。

本模組刻意不 import 任何翻譯後端。`--detect` 是純 git 操作,
在沒有安裝翻譯 API SDK 的環境下必須可執行 —— 這是 CI 沉默五個月的根因。
"""

import json
import subprocess
from pathlib import Path

MANIFEST_PATH = Path("scripts/translation-manifest.json")
SIDEBAR_FILES = ("book/sidebar.yml", "reference/sidebar.yml")
DIRS = ("book", "reference")


def load() -> dict[str, str]:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {}


def save(m: dict[str, str]) -> None:
    MANIFEST_PATH.write_text(
        json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def blob_sha(ref: str, path: str) -> str | None:
    r = subprocess.run(
        ["git", "rev-parse", f"{ref}:{path}"], capture_output=True, text=True
    )
    return r.stdout.strip() if r.returncode == 0 else None


def tracked_files(ref: str) -> list[str]:
    r = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, *DIRS],
        capture_output=True, text=True, check=True,
    )
    return [
        f for f in r.stdout.split()
        if f.endswith(".md") or f in SIDEBAR_FILES
    ]


def stale_files(ref: str = "english-main") -> list[str]:
    m = load()
    out = []
    for path in tracked_files(ref):
        sha = blob_sha(ref, path)
        if sha is not None and m.get(path) != sha:
            out.append(path)
    return out


def orphans(ref: str = "english-main") -> list[str]:
    """manifest 或 zh 分支有、但英文來源已刪除的路徑。"""
    present = set(tracked_files(ref))
    r = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "HEAD", *DIRS],
        capture_output=True, text=True, check=True,
    )
    zh = {f for f in r.stdout.split() if f.endswith(".md")}
    return sorted((zh | set(load())) - present)


def record(m: dict[str, str], path: str, ref: str = "english-main") -> None:
    sha = blob_sha(ref, path)
    if sha is None:
        raise ValueError(f"{path} 不存在於 {ref}")
    m[path] = sha
