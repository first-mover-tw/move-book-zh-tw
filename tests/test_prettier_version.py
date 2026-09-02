"""prettier 的版本字串散在三個檔，這裡守住「實際執行的命令」都釘死且一致。

為什麼需要：translate workflow 的 `prettier --write` 與 prettier.yml gate 的
`prettier --check` 若解析到不同版本，管線剛格式化過的 PR 會被自己的 gate 擋下
（3.x 的 minor 是可以改變 markdown/YAML 輸出的 —— 「不在 python 端手刻 prettier
的 printer 演算法」正是拿版本漂移當理由）。原本這三處靠人工同步，下次升版漏改
一處就完全重現那個缺陷。

刻意**不**用「掃全檔找 prettier@x.y.z」：那會把註解、docstring、YAML comment
一起算進去，而 workflow 裡談版本釘死的註解就緊貼著它要守的那行命令。於是把
`npx --yes prettier@3.9.6 --write` 改成 `npx --yes prettier --write`、同時在註解裡
留一句「原本釘 3.9.6」，守衛照樣全綠而釘死已經沒了 —— 觀測的維度（檔案提過這個
版本號）不等於它宣稱保護的性質（執行的命令帶著這個版本號），lessons L2。
"""

import json
import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKFLOWS = {
    "translate-zh-tw.yml": ROOT / ".github/workflows/translate-zh-tw.yml",
    "prettier.yml": ROOT / ".github/workflows/prettier.yml",
}
# 只認 npx/npm exec 起手的呼叫；--write/--check 二選一必須在同一行，
# 確保抓到的是真的會執行的那行，不是散文。
_INVOCATION = re.compile(r"\b(?:npx|npm exec)\b[^\n]*\bprettier(@[^\s]+)?\b[^\n]*--(?:write|check)\b")
_EXACT = re.compile(r"^@(\d+\.\d+\.\d+)$")


def _command_lines(text: str) -> list[str]:
    """去掉註解後，回傳含 prettier 呼叫的命令列。"""
    out = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if _INVOCATION.search(stripped):
            out.append(stripped)
    return out


def _invocations() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for name, path in WORKFLOWS.items():
        doc = yaml.safe_load(path.read_text())
        runs = [
            step["run"]
            for job in doc["jobs"].values()
            for step in job["steps"]
            if isinstance(step, dict) and isinstance(step.get("run"), str)
        ]
        found[name] = _command_lines("\n".join(runs))
    pkg = json.loads((ROOT / "package.json").read_text())
    found["package.json"] = _command_lines("\n".join(pkg["scripts"].values()))
    return found


def test_every_prettier_invocation_exists():
    """三個檔都必須真的有 prettier 呼叫 —— 否則下面兩條會 vacuously 綠。"""
    for where, lines in _invocations().items():
        assert lines, f"{where} 找不到任何 npx/npm exec 的 prettier --write/--check 呼叫"


def test_every_prettier_invocation_is_pinned():
    """每一個呼叫都要帶 exact version，不能是浮動的 `prettier` 或 `prettier@3`。"""
    for where, lines in _invocations().items():
        for line in lines:
            m = _INVOCATION.search(line)
            spec = m.group(1) or ""
            assert _EXACT.match(spec), f"{where} 的呼叫未釘死 exact version：{line}"


def test_all_prettier_invocations_share_one_version():
    """三處版本必須一模一樣。"""
    versions = {
        _INVOCATION.search(line).group(1)
        for lines in _invocations().values()
        for line in lines
    }
    assert len(versions) == 1, f"prettier 版本不一致：{versions}"
