"""本地後端：呼叫 headless 的 claude CLI。不需要 API key 環境變數。"""

import os
import subprocess

from .base import SYSTEM_PROMPT


class ClaudeCLIBackend:
    def translate(self, text: str, *, kind: str = "markdown") -> str:
        model = os.environ.get("ZH_TW_CLAUDE_MODEL", "haiku")
        timeout = int(os.environ.get("ZH_TW_TIMEOUT", "600"))
        prompt = f"{SYSTEM_PROMPT}\n\n要翻譯的內容：\n\n{text}"
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
