"""本地後端：呼叫 headless 的 claude CLI。不需要 API key 環境變數。"""

import os
import subprocess

from .base import HEADING_PROMPT, SYSTEM_PROMPT, TEXT_PROMPT


class ClaudeCLIBackend:
    def translate(self, text: str, *, kind: str = "markdown") -> str:
        # Task 17 A/B（2026-07-11，reference/variables.md，見 tasks/notes.md）：
        # sonnet 譯文品質與台灣用語較好且快一倍；它掉標題後綴的失效模式由
        # validate gate 9（check_heading_suffix）擋下不寫檔。
        model = os.environ.get("ZH_TW_CLAUDE_MODEL", "sonnet")
        timeout = int(os.environ.get("ZH_TW_TIMEOUT", "600"))
        if kind == "sidebar":
            # sidebar payload 自帶 SIDEBAR_PROMPT 與編號清單，再外包任何
            # prompt 都會產生互相矛盾的指令（見 sidebar.SIDEBAR_PROMPT）。
            prompt = text
        else:
            system = {"text": TEXT_PROMPT, "heading": HEADING_PROMPT}.get(kind, SYSTEM_PROMPT)
            prompt = f"{system}\n\n要翻譯的內容：\n\n{text}"
        r = subprocess.run(
            ["claude", "-p", "--model", model, prompt],
            capture_output=True, text=True, timeout=timeout,
        )
        if r.returncode != 0:
            raise RuntimeError(f"claude CLI 失敗: {r.stderr[:400]}")
        out = r.stdout.strip()
        if not out:
            raise RuntimeError("claude CLI 回傳空字串")
        return out + "\n"
