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


def _installed(path: pathlib.Path) -> dict[str, set[str]]:
    """**逐 job** 回傳裝了哪些套件。

    不能把整個檔案的 pip install 併成一個集合：只要任一個 job（哪怕是
    `if: false`、或一個永遠不跑的 lint job）裝了某套件，真正跑翻譯的 job
    沒裝，測試照樣綠而管線照樣 ModuleNotFoundError —— 觀測維度（檔案裡
    有人裝過）不等於宣稱保護的性質（跑 python 的那個 job 裝了）。
    """
    doc = yaml.safe_load(path.read_text())
    return {
        name: _pkgs_in(
            "\n".join(
                step["run"]
                for step in job.get("steps", [])
                if isinstance(step, dict) and isinstance(step.get("run"), str)
            )
        )
        for name, job in doc["jobs"].items()
    }


def _runs_python(path: pathlib.Path, job_name: str) -> bool:
    """這個 job 有沒有真的執行 scripts.zh_tw？沒有就不必裝依賴。"""
    doc = yaml.safe_load(path.read_text())
    job = doc["jobs"][job_name]
    text = "\n".join(
        step["run"]
        for step in job.get("steps", [])
        if isinstance(step, dict) and isinstance(step.get("run"), str)
    )
    return "scripts.zh_tw" in text


def _pkgs_in(text: str) -> set[str]:
    pkgs: set[str] = set()
    for line in text.splitlines():
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
        checked = 0
        for job, pkgs in _installed(path).items():
            if not _runs_python(path, job):
                continue
            checked += 1
            missing = _runtime_deps() - pkgs
            assert not missing, (
                f"{path.name} 的 job `{job}` 執行了 scripts.zh_tw 但 pip install "
                f"少了 {sorted(missing)} —— 管線會在 import 時 ModuleNotFoundError"
            )
        # 防 vacuous：每個 workflow 至少有一個 job 被檢查到，而不是
        # `_runs_python` 的條件把所有 job 都篩掉了。用「至少一個」而非
        # 「恰好 N 個」——後者把「每個 workflow 恰好一個跑 python 的 job」
        # 寫死成不變式，加第二個這種 job 就會噴無關的紅。
        assert checked, f"{path.name} 沒有任何 job 被檢查到（_runs_python 全篩掉了）"


# --- 容忍部分失敗的步驟必須真的關掉 errexit ---


def _step(path: pathlib.Path, name: str) -> str:
    doc = yaml.safe_load(path.read_text())
    for job in doc["jobs"].values():
        for s in job.get("steps", []):
            if isinstance(s, dict) and s.get("name") == name:
                return s["run"]
    raise AssertionError(f"{path.name} 找不到步驟 {name}")


def test_translate_step_disables_errexit():
    """GitHub 的預設 shell 是 `bash --noprofile --norc -eo pipefail {0}`——
    **`-e` 本來就開著**，而 `set -uo pipefail` 只會「加」選項，關不掉它。

    Translate 步驟的整個設計是「部分失敗不中斷」：配額用盡時 xargs 回 123，
    但已翻成功的檔案要照常 commit/PR，殘量隔日 cron 接手。它寫的是
    `set -uo pipefail` 並在後面接 `rc=$?`，看起來像關掉了 errexit，其實沒有。
    2026-09-03 run 33697227425 實證：`成功 2，失敗 1` → 步驟仍以 123 轉紅 →
    後面全 skip → 那 2 個翻好的檔案整批丟掉，正是註解裡寫的「前車之鑑」。
    這個容錯從第一天就沒生效過，只是之前每次都剛好全部成功。
    """
    run = _step(ROOT / ".github/workflows/translate-zh-tw.yml", "Translate")
    assert re.search(r"^\s*set \+e\b", run, re.M), (
        "Translate 步驟要容忍部分失敗，就必須顯式 `set +e`——"
        "GitHub 預設 shell 已經帶 -e，`set -uo pipefail` 關不掉"
    )
    # 前提斷言：它真的有在自己判斷 rc（否則關掉 -e 只是讓失敗靜默）
    assert "rc=$?" in run
