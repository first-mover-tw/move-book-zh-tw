"""prettier 的版本字串散在三個檔，這裡守住它們一致。

為什麼需要：translate workflow 的 `prettier --write` 與 prettier.yml gate 的
`prettier --check` 若解析到不同版本，管線剛格式化過的 PR 會被自己的 gate 擋下
（3.x 的 minor 是可以改變 markdown/YAML 輸出的 —— 「不在 python 端手刻 prettier
的 printer 演算法」正是拿版本漂移當理由）。原本這三處靠人工同步，下次升版漏改
一處就完全重現那個缺陷。
"""

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
_PINNED = re.compile(r"prettier@(\d+\.\d+\.\d+)")


def _versions() -> dict[str, set[str]]:
    pkg = json.loads((ROOT / "package.json").read_text())
    scripts = " ".join(pkg["scripts"].values())
    return {
        ".github/workflows/translate-zh-tw.yml": set(
            _PINNED.findall((ROOT / ".github/workflows/translate-zh-tw.yml").read_text())
        ),
        ".github/workflows/prettier.yml": set(
            _PINNED.findall((ROOT / ".github/workflows/prettier.yml").read_text())
        ),
        "package.json": set(_PINNED.findall(scripts)),
    }


def test_prettier_version_is_pinned_everywhere():
    """三處都必須釘死 exact version，不能出現浮動的 `prettier@3`。"""
    for where, found in _versions().items():
        assert found, f"{where} 沒有釘死的 prettier@x.y.z（浮動版本或漏寫）"


def test_prettier_version_is_identical_everywhere():
    """三處版本必須一模一樣。"""
    found = _versions()
    all_versions = set().union(*found.values())
    assert len(all_versions) == 1, f"prettier 版本不一致：{found}"
