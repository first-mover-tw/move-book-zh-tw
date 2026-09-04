"""翻譯後端介面。LLM 只在這一層出現。"""

from typing import Protocol

from .. import glossary

SYSTEM_PROMPT = (
    "你是專業的技術文件翻譯者。請將以下 Markdown 翻譯成台灣繁體中文。\n"
    "保留所有 Markdown 結構、連結、圖片與程式碼區塊。\n"
    "不要翻譯程式碼本身，但要翻譯程式碼區塊內的註解。\n"
    "不要增加或刪除任何標題，標題數量必須與原文完全相同。\n"
    "標題翻譯規則（違反任何一條整份重來）：\n"
    "- 每個標題一律輸出「中文譯文 (英文原文)」，結尾括號內的英文原文必須"
    "一字不差（含 inline code 反引號、大小寫、標點），不可改寫或翻譯括號內文字。\n"
    "- 專有名詞或型別名稱的標題也要有中文前綴，例：「## Bag」→"
    "「## Bag 通用容器 (Bag)」、「## Summary」→「## 總結 (Summary)」、"
    "「## Running Tests」→「## 執行測試 (Running Tests)」。\n"
    "- 只有全大寫縮寫標題（如 BCS）可原樣保留、不加括號。\n"
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


# kind="heading"（pipeline._repair_headings 的單標題重譯）專用：整份 markdown
# prompt 下 sonnet 對「VecSet」這類型別名標題常 verbatim 不翻；單標題呼叫 +
# 明確格式要求可靠得多。
HEADING_PROMPT = (
    "你是專業的技術文件翻譯者。請將以下文件標題翻譯成台灣繁體中文，"
    "輸出格式必須是「中文譯文 (英文原文)」——結尾括號內放英文原文一字不差"
    "（含 inline code 反引號、大小寫、標點）。\n"
    "專有名詞或型別名稱也要有中文前綴，例：「Bag」→「Bag 通用容器 (Bag)」、"
    "「Running Tests」→「執行測試 (Running Tests)」。\n"
    f"{glossary.prompt_rules()}\n"
    "只回傳結果，不要任何解釋、不要加引號。"
)


class Backend(Protocol):
    """kind 的四個合法值與各自的 prompt 契約（新 backend 必須遵守分流）：

    - "markdown"（預設）：chunk 內文，外包 SYSTEM_PROMPT。
    - "text"：frontmatter title/description 等裸短字串，外包 TEXT_PROMPT。
    - "heading"：單一標題重譯（修復 pass），外包 HEADING_PROMPT。
    - "raw" / "sidebar"：payload **自帶完整指令**（raw = 通用；sidebar =
      sidebar.translate 專用，payload 帶 SIDEBAR_PROMPT 與
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
    if name == "codex":
        from .codex_cli import CodexCLIBackend
        return CodexCLIBackend()
    raise ValueError(f"unknown backend: {name}")
