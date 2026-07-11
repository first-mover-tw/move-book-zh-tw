"""本地後端：呼叫 headless 的 claude CLI。不需要 API key 環境變數。"""

import os
import subprocess
import tempfile

from .base import HEADING_PROMPT, SYSTEM_PROMPT, TEXT_PROMPT


class ClaudeCLIBackend:
    def translate(self, text: str, *, kind: str = "markdown") -> str:
        # Task 17 A/B（2026-07-11，reference/variables.md，見 tasks/notes.md）：
        # sonnet 譯文品質與台灣用語較好且快一倍；它掉標題後綴的失效模式由
        # validate gate 9（check_heading_suffix）擋下不寫檔。
        model = os.environ.get("ZH_TW_CLAUDE_MODEL", "sonnet")
        timeout = int(os.environ.get("ZH_TW_TIMEOUT", "600"))
        if kind in ("sidebar", "raw"):
            # sidebar payload 自帶 SIDEBAR_PROMPT 與編號清單，再外包任何
            # prompt 都會產生互相矛盾的指令（見 sidebar.SIDEBAR_PROMPT）。
            prompt = text
        else:
            system = {"text": TEXT_PROMPT, "heading": HEADING_PROMPT}.get(kind, SYSTEM_PROMPT)
            prompt = f"{system}\n\n要翻譯的內容：\n\n{text}"
        # cwd 必須是中性目錄：claude CLI 會載入 cwd 的專案 context
        # （CLAUDE.md、SessionStart hook 注入的 tasks/progress.md）。在本
        # 專案目錄執行時模型看得到「翻譯管線工程」上下文，會間歇性放棄
        # 翻譯、改成扮演工程師回答（實測 'Abort' 回「Bug 找到了…」）。
        neutral = tempfile.mkdtemp(prefix="zh-tw-translate-")
        try:
            # stdin=DEVNULL：claude -p 對非 tty 的 stdin 會整段讀進當輸入，
            # 從 heredoc/管線呼叫本 backend 時，殘留的 stdin（例如呼叫者
            # 自己的 python script）會被當成翻譯內容的一部分 —— 實測模型
            # 回「疑似程式碼注入，未執行」。批次 xargs 跑不炸是因為 xargs
            # 恰好耗盡了 stdin。
            r = subprocess.run(
                ["claude", "-p", "--model", model, prompt],
                capture_output=True, text=True, timeout=timeout, cwd=neutral,
                stdin=subprocess.DEVNULL,
            )
        finally:
            os.rmdir(neutral)
        if r.returncode != 0:
            raise RuntimeError(f"claude CLI 失敗: {r.stderr[:400]}")
        out = r.stdout.strip()
        if not out:
            raise RuntimeError("claude CLI 回傳空字串")
        return out + "\n"
