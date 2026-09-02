"""prettier 的版本字串散在三個檔，這裡守住它們都釘死且一致。

為什麼需要：translate workflow 的 `prettier --write` 與 prettier.yml gate 的
`prettier --check` 若解析到不同版本，管線剛格式化過的 PR 會被自己的 gate 擋下
（3.x 的 minor 是可以改變 markdown/YAML 輸出的 —— 「不在 python 端手刻 prettier
的 printer 演算法」正是拿版本漂移當理由）。原本這三處靠人工同步，下次升版漏改
一處就完全重現那個缺陷。

判準刻意是**否定式**（「非註解行裡出現的每一個 prettier 都必須緊跟 @x.y.z」），
而不是「找得到一個釘死的呼叫」。前兩版都栽在肯定式上，兩次都是同一個病 ——
觀測維度是「文字裡出現過」，宣稱保護的性質是「會被執行的那行帶著版本」：
  v1 掃全檔 → 談版本釘死的註解就緊貼著它要守的那行命令，把命令的 @3.9.6
     拿掉、註解留著，守衛照樣全綠。
  v2 只掃 run 字串、要求 npx/npm exec 與 --write/--check 同一行 → 改用
     `pnpm dlx prettier --write`（不匹配 npx）並在旁邊留一行
     `echo "本機等價：npx --yes prettier@3.9.6 --write"`，守衛照樣全綠。
否定式沒有這個縫：任何未釘死的 prettier 字樣都會紅，繞不過去。代價是連
`echo "run prettier"` 這種散文也會紅 —— 可接受，寫 `prettier@3.9.6` 即可。
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
# 緊跟在 prettier 後面的 @x.y.z；沒有就是沒釘死。
_MENTION = re.compile(r"\bprettier(@\d+\.\d+\.\d+)?\b")


def _command_text(text: str) -> str:
    """去掉註解行，並把 shell 續行接回來。

    續行要先接：`npx --yes prettier@3.9.6 \\` + `--write --` 拆成兩行時，
    逐行判斷會看不出這是同一個命令。
    """
    joined = text.replace("\\\n", " ")
    return "\n".join(
        line for line in joined.splitlines() if not line.strip().startswith("#")
    )


def _mentions() -> dict[str, list[str | None]]:
    """每個檔裡「非註解的 prettier 字樣」對應的版本（None = 沒釘死）。"""
    found: dict[str, list[str | None]] = {}
    for name, path in WORKFLOWS.items():
        doc = yaml.safe_load(path.read_text())
        runs = [
            step["run"]
            for job in doc["jobs"].values()
            # reusable workflow 的 job 用 `uses:`，沒有 steps
            for step in job.get("steps", [])
            if isinstance(step, dict) and isinstance(step.get("run"), str)
        ]
        found[name] = [m.group(1) for m in _MENTION.finditer(_command_text("\n".join(runs)))]
    pkg = json.loads((ROOT / "package.json").read_text())
    scripts = _command_text("\n".join(pkg["scripts"].values()))
    found["package.json"] = [m.group(1) for m in _MENTION.finditer(scripts)]
    return found


def test_every_file_mentions_prettier():
    """三個檔都必須真的用到 prettier —— 否則下面兩條會 vacuously 綠。"""
    for where, mentions in _mentions().items():
        assert mentions, f"{where} 的 run/scripts 裡找不到 prettier，守衛失去意義"


def test_every_prettier_mention_is_pinned():
    """每一處都要帶 exact version，不能是浮動的 `prettier` 或 `prettier@3`。"""
    for where, mentions in _mentions().items():
        assert None not in mentions, (
            f"{where} 有未釘死版本的 prettier（浮動版本、或 pnpm dlx 之類的繞法）"
        )


def test_all_prettier_versions_are_identical():
    """三處版本必須一模一樣。"""
    versions = {v for mentions in _mentions().values() for v in mentions if v}
    assert len(versions) == 1, f"prettier 版本不一致：{versions}"
