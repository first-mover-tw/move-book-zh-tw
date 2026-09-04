"""本地後端：呼叫非互動的 codex CLI。不需要 API key 環境變數。

用途是**本機批量排乾**（2026-09-04 使用者裁決）：cron 的 Gemini 免費層是
BATCH_SIZE=3／天，133 檔待翻要排 45 天。codex 走本機的登入憑證，不進 CI ——
GitHub Actions 裡的 codex 要的是 `OPENAI_API_KEY`，跟本機這份憑證是兩個計費
體系，所以 `translate-zh-tw.yml` 維持 gemini 不動。

與 claude_cli 的三個差別（每一條都是實測出來的）：

1. **答案要從檔案拿，不是 stdout。** `codex exec` 把 model/provider/session id、
   hook 事件、`tokens used` 統計全印在 stdout，最終答案只是夾在中間的一段。
   用 `-o/--output-last-message <FILE>` 讓 CLI 自己把最後一則訊息寫進檔案，
   拿到的就是純譯文，不必寫任何剝殼 regex（剝殼 regex 會是 L2 的典型犯案：
   用「輸出長什麼樣」代理「哪一段是答案」）。

2. **`--ignore-user-config`。** 這是 L8（LLM CLI 必須隔離 stdin 與 cwd）在
   codex 上的對應面：codex 會載入 `~/.codex/config.toml`（模型偏好、hooks）
   與工作目錄的 AGENTS.md。翻譯呼叫必須讓 prompt 成為**唯一**指令來源 ——
   台灣用語與術語表全靠 base.py 那三個 prompt（內嵌 glossary.prompt_rules()），
   被別的指令稀釋就會靜默劣化。auth 不受影響（`--ignore-user-config` 只跳過
   config.toml，憑證仍走 `CODEX_HOME`）。

3. **`-s read-only` + `--cd <中性 tempdir>` + `--skip-git-repo-check`。**
   codex 是 agent 不是單次補全，預設會想動檔案。read-only sandbox 讓它不能
   寫任何東西；中性 cwd 同 claude_cli（避免讀到本專案的 CLAUDE.md /
   tasks/progress.md 而改去扮演工程師）；中性目錄不是 git repo，所以要
   `--skip-git-repo-check`。

`--ephemeral` 不落 session 檔，避免批量跑幾百次之後在 `~/.codex` 堆垃圾。

**清理用 `TemporaryDirectory()` context manager，不要「對一個變數 rmtree」。**
2026-09-04 的事故：第一版寫成 `neutral = tempfile.mkdtemp(...)` + `finally:
shutil.rmtree(neutral)`，做 mutation test 時把 `mkdtemp(...)` 變異成
`os.getcwd()`，pytest 一跑就把整個專案目錄刪了。context manager 的作用域由
`with` 決定，結構上不可能刪到別的地方（lessons L17）。
"""

import os
import subprocess
import tempfile
from pathlib import Path

from .base import HEADING_PROMPT, SYSTEM_PROMPT, TEXT_PROMPT


class CodexCLIBackend:
    def translate(self, text: str, *, kind: str = "markdown") -> str:
        timeout = int(os.environ.get("ZH_TW_TIMEOUT", "600"))
        if kind in ("sidebar", "raw"):
            # 同 claude_cli/gemini：payload 自帶完整指令，不外包 prompt。
            # 兩層指令會互相矛盾（TEXT_PROMPT「單一名詞必翻」vs
            # SIDEBAR_PROMPT「專有名詞維持原文」），而 sidebar 的格式 guard
            # 擋不住這種語意流出。
            prompt = text
        else:
            system = {"text": TEXT_PROMPT, "heading": HEADING_PROMPT}.get(kind, SYSTEM_PROMPT)
            prompt = f"{system}\n\n要翻譯的內容：\n\n{text}"

        with tempfile.TemporaryDirectory(prefix="zh-tw-translate-") as neutral:
            out_path = Path(neutral) / "last-message.txt"
            argv = [
                "codex", "exec",
                "--ephemeral",
                "--ignore-user-config",
                "--skip-git-repo-check",
                "--color", "never",
                "-s", "read-only",
                "--cd", neutral,
                "-o", str(out_path),
            ]
            # model 不寫死預設值：釘一個名字就會重演 gemini 那份 MODELS 清單
            # 的問題（`gemini-2.5-flash-lite` 下架後對新用戶回 404）。不給 -m
            # 就用 codex 當下的預設 model；要固定版本時用環境變數。
            model = os.environ.get("ZH_TW_CODEX_MODEL")
            if model:
                argv += ["-m", model]
            argv.append(prompt)

            # stdin=DEVNULL：codex exec 在 prompt 為 `-` 或 stdin 被導入時會把
            # stdin 當成附加的 <stdin> 區塊餵進去（見 `codex exec --help`）。
            # 從 heredoc/管線呼叫本 backend 時，殘留的 stdin 會變成翻譯內容的
            # 一部分 —— 這正是 claude_cli 踩過的 L8。
            r = subprocess.run(
                argv,
                capture_output=True, text=True, timeout=timeout, cwd=neutral,
                stdin=subprocess.DEVNULL,
            )
            if r.returncode != 0:
                raise RuntimeError(f"codex CLI 失敗: {r.stderr[:400] or r.stdout[-400:]}")
            if not out_path.exists():
                # 不退回去讀 stdout：那會把 `tokens used\n11602` 這類雜訊當成
                # 譯文寫進語料。寧可炸掉讓上層的重試/跳過邏輯接手。
                raise RuntimeError(
                    "codex CLI 沒有寫出 --output-last-message 檔案："
                    f"{r.stderr[:200] or r.stdout[-200:]}"
                )
            out = out_path.read_text(encoding="utf-8").strip()

        if not out:
            raise RuntimeError("codex CLI 回傳空字串")
        return out + "\n"
