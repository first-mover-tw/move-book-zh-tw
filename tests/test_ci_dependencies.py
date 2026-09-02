"""workflow 的 `pip install` 清單必須涵蓋 pyproject 的 runtime 依賴。

為什麼需要：CI 不跑 `pip install -e .`，而是在兩個 workflow 裡各手寫一份
套件清單。清單與 `[project].dependencies` 是兩處必須一致、卻沒有任何東西
在檢查的耦合 —— 加一個 runtime import 而忘了改 workflow，管線就在
`Translate` 步驟以 ModuleNotFoundError 炸掉。2026-09-02 加 gate 10 時，
`commonmark` 本來就在 dev group、兩個 workflow 都沒裝，差一步就把整條
管線推上去（是自己回頭核對才發現，沒有任何測試會紅）。

判準刻意是「涵蓋」而非「相等」：workflow 多裝東西無害，少裝才會炸。
"""

import pathlib
import re
import tomllib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKFLOWS = [
    ROOT / ".github/workflows/translate-zh-tw.yml",
    ROOT / ".github/workflows/gemini-smoke.yml",
]
# `pkg>=1.2` / `pkg[extra]` → `pkg`
_DIST = re.compile(r"^([A-Za-z0-9._-]+)")


def _runtime_deps() -> set[str]:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    return {
        _DIST.match(d).group(1).lower().replace("_", "-")
        for d in pyproject["project"]["dependencies"]
    }


def _installed(path: pathlib.Path) -> set[str]:
    doc = yaml.safe_load(path.read_text())
    runs = [
        step["run"]
        for job in doc["jobs"].values()
        for step in job.get("steps", [])
        if isinstance(step, dict) and isinstance(step.get("run"), str)
    ]
    pkgs: set[str] = set()
    for line in "\n".join(runs).splitlines():
        line = line.strip()
        if line.startswith("#") or "pip install" not in line:
            continue
        tail = line.split("pip install", 1)[1]
        for tok in tail.split():
            if tok.startswith("-"):
                continue
            m = _DIST.match(tok)
            if m:
                pkgs.add(m.group(1).lower().replace("_", "-"))
    return pkgs


def test_pyproject_declares_runtime_deps():
    """前提斷言（防 vacuous）：runtime 依賴不得為空，否則下面那條恆真。"""
    assert _runtime_deps()


def test_workflows_install_every_runtime_dependency():
    for path in WORKFLOWS:
        missing = _runtime_deps() - _installed(path)
        assert not missing, (
            f"{path.name} 的 pip install 少了 {sorted(missing)} —— "
            f"管線會在 import 時以 ModuleNotFoundError 炸掉"
        )
