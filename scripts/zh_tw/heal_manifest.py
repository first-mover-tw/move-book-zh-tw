"""修復 provenance 損壞的 manifest 條目。

31 筆指向不存在的 blob。以結構指紋（標題層級序列 + fence 數，透過
`anchors.headings()` / `anchors.fence_lines()` 計算——本專案唯一的
markdown 區塊真相來源）確認中文內文確實對應 merge-base 的英文，
再回填 merge-base 的 blob SHA。指紋不符者不動，留給 backfill 全譯。
"""

import subprocess
import sys

from . import anchors, frontmatter, manifest

MERGE_BASE = "f2c0a93e1a0422078d3d051e4410ac3edc612016"


def _show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def _fingerprint(text: str) -> tuple[tuple[int, ...], int]:
    _, body = frontmatter.split(text)
    return tuple(lv for lv, _ in anchors.headings(body)), anchors.fence_lines(body)


def heal(dry_run: bool = True) -> tuple[list[str], list[str]]:
    m = manifest.load()
    healed, unrecoverable = [], []

    for path, sha in list(m.items()):
        if not subprocess.run(["git", "cat-file", "-e", sha], capture_output=True).returncode:
            continue  # blob 存在，provenance 完好
        en_base, zh = _show(MERGE_BASE, path), _show("HEAD", path)
        base_sha = manifest.blob_sha(MERGE_BASE, path)
        if not (en_base and zh and base_sha):
            unrecoverable.append(path)
            continue
        if _fingerprint(en_base) == _fingerprint(zh):
            healed.append(path)
            if not dry_run:
                m[path] = base_sha
        else:
            unrecoverable.append(path)

    if not dry_run:
        manifest.save(m)
    return healed, unrecoverable


def main() -> int:
    healed, bad = heal(dry_run="--apply" not in sys.argv)
    print(f"可修復 {len(healed)}，無法修復 {len(bad)}")
    for p in bad:
        print(f"  結構不符，留給全譯: {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
