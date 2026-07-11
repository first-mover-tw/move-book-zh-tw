"""翻譯後端介面。LLM 只在這一層出現。"""

from typing import Protocol

from .. import glossary

SYSTEM_PROMPT = (
    "你是專業的技術文件翻譯者。請將以下 Markdown 翻譯成台灣繁體中文。\n"
    "保留所有 Markdown 結構、連結、圖片與程式碼區塊。\n"
    "不要翻譯程式碼本身，但要翻譯程式碼區塊內的註解。\n"
    "不要增加或刪除任何標題，標題數量必須與原文完全相同。\n"
    "標題格式為「中文 (English)」，保留原文英文於括號內。\n"
    f"{glossary.prompt_rules()}\n"
    "只回傳翻譯後的 Markdown，不要任何解釋。"
)


class Backend(Protocol):
    def translate(self, text: str, *, kind: str = "markdown") -> str: ...


def get(name: str) -> Backend:
    if name == "fake":
        from .fake import FakeBackend
        return FakeBackend()
    if name == "claude":
        from .claude_cli import ClaudeCLIBackend
        return ClaudeCLIBackend()
    if name == "gemini":
        from .gemini import GeminiBackend
        return GeminiBackend()
    raise ValueError(f"unknown backend: {name}")
