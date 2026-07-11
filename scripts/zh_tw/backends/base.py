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

# kind="text"（frontmatter title/description 等短字串）專用。markdown prompt
# 對單詞技術名詞 title（'Friends | Reference'）會保守不翻，gate 4 攔下後
# retry 也翻不動 —— 短字串需要明確指示「必須翻、單一名詞也要翻」。
TEXT_PROMPT = (
    "你是專業的技術文件翻譯者。請將以下短字串（文件標題或描述）翻譯成台灣繁體中文。\n"
    "即使只是單一技術名詞也必須翻譯，技術名詞格式為「中文 (English)」，"
    "保留原文英文於括號內。\n"
    "若字串結尾本來就有「| Reference」，把那一段翻成「| 參考手冊」；"
    "原文沒有的話，絕對不要自行加上任何「| ...」後綴。\n"
    f"{glossary.prompt_rules()}\n"
    "只回傳翻譯結果，不要任何解釋、不要加引號。"
)


class Backend(Protocol):
    """kind 的三個合法值與各自的 prompt 契約（新 backend 必須遵守三向分流）：

    - "markdown"（預設）：chunk 內文，外包 SYSTEM_PROMPT。
    - "text"：frontmatter title/description 等裸短字串，外包 TEXT_PROMPT。
    - "sidebar"：sidebar.translate 的 payload，**自帶** SIDEBAR_PROMPT 與
      編號清單 —— backend 不得再外包任何 prompt，否則兩層指令互相矛盾
      （TEXT_PROMPT「單一名詞必翻」vs SIDEBAR_PROMPT「專有名詞維持原文」），
      且 sidebar 的格式 guard 擋不住這種語意流出。
    """

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
