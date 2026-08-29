"""CI 後端。import 延遲到建構時，讓 manifest/detect 不必安裝 google-genai。"""

import os
import time

from .base import HEADING_PROMPT, SYSTEM_PROMPT, TEXT_PROMPT

# 這份清單只驗證過在舊腳本裡沿用的 gemini-2.5-flash；
# gemini-3.0-flash-preview / gemini-2.0-flash-exp 是未經確認的 preview/experimental
# 名稱，故不予保留。啟用 CI workflow（PR 1）前，必須先跑：
#   uv run --with google-genai python -c \
#     "from google import genai; import os; \
#      [print(m.name) for m in genai.Client(api_key=os.environ['GEMINI_API_KEY']).models.list()]"
# 用實際回傳的模型目錄重新確認/擴充這份清單。
# free tier 的 RPD 配額是 per model 計，兩個 model = 兩份額度。
# 2026-08-29：gemini-2.5-flash-lite 對新用戶回 404「no longer available, use
# gemini-3.5-flash-lite」（run 33227490688），故換成官方指名的後繼者。
MODELS = ["gemini-2.5-flash", "gemini-3.5-flash-lite"]
# model 不存在/已下架的 404：重試無意義，直接換下一個。
_MODEL_GONE_MARKERS = ("404", "NOT_FOUND")
MAX_RETRIES = 3
RATE_LIMIT_WAIT = 60
# 日配額用盡的 429 帶這個 quotaId；等 60 秒不會恢復，直接換下一個 model。
_DAILY_QUOTA_MARKERS = ("PerDay", "per_day")


class GeminiBackend:
    def __init__(self) -> None:
        from google import genai  # noqa: PLC0415 — 延遲 import 是刻意的

        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        self._client = genai.Client(api_key=key)

    def translate(self, text: str, *, kind: str = "markdown") -> str:
        if kind in ("sidebar", "raw"):
            # 同 claude_cli：sidebar payload 自帶完整指令，不外包。
            msg = text
        else:
            system = {"text": TEXT_PROMPT, "heading": HEADING_PROMPT}.get(kind, SYSTEM_PROMPT)
            msg = f"{system}\n\n要翻譯的內容：\n\n{text}"
        last: Exception | None = None
        for model in MODELS:
            for attempt in range(MAX_RETRIES):
                try:
                    resp = self._client.models.generate_content(model=model, contents=msg)
                    if not resp.text or not resp.text.strip():
                        raise RuntimeError("Gemini 回傳空字串（可能被安全過濾攔截）")
                    return resp.text
                except Exception as e:  # noqa: BLE001
                    last = e
                    err = str(e)
                    print(f"    [{model} attempt {attempt + 1}] {err[:160]}")
                    if any(m in err for m in _DAILY_QUOTA_MARKERS):
                        break  # 日配額耗盡：此 model 今天不會再成功，換下一個
                    if any(m in err for m in _MODEL_GONE_MARKERS):
                        break  # model 已下架：換下一個
                    if model == MODELS[-1] and attempt == MAX_RETRIES - 1:
                        break  # 最後一次，不用再等
                    is_rate_limited = "429" in err or "RESOURCE_EXHAUSTED" in err
                    time.sleep(RATE_LIMIT_WAIT if is_rate_limited else 5)
        raise RuntimeError(f"所有模型皆失敗: {last}")
