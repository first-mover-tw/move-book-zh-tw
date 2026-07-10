"""CI 後端。import 延遲到建構時，讓 manifest/detect 不必安裝 google-genai。"""

import os
import time

from .base import SYSTEM_PROMPT

# 這份清單只驗證過在舊腳本裡沿用的 gemini-2.5-flash；
# gemini-3.0-flash-preview / gemini-2.0-flash-exp 是未經確認的 preview/experimental
# 名稱，故不予保留。啟用 CI workflow（PR 1）前，必須先跑：
#   uv run --with google-genai python -c \
#     "from google import genai; import os; \
#      [print(m.name) for m in genai.Client(api_key=os.environ['GEMINI_API_KEY']).models.list()]"
# 用實際回傳的模型目錄重新確認/擴充這份清單。
MODELS = ["gemini-2.5-flash"]
MAX_RETRIES = 3
RATE_LIMIT_WAIT = 60


class GeminiBackend:
    def __init__(self) -> None:
        from google import genai  # noqa: PLC0415 — 延遲 import 是刻意的

        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        self._client = genai.Client(api_key=key)

    def translate(self, text: str, *, kind: str = "markdown") -> str:
        msg = f"{SYSTEM_PROMPT}\n\n要翻譯的內容：\n\n{text}"
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
                    is_last_attempt = (
                        model == MODELS[-1] and attempt == MAX_RETRIES - 1
                    )
                    if is_last_attempt:
                        continue
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        time.sleep(RATE_LIMIT_WAIT)
                    else:
                        time.sleep(5)
        raise RuntimeError(f"所有模型皆失敗: {last}")
