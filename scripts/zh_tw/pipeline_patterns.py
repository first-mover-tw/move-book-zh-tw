"""pipeline 與 validate 共用的 pattern。

單獨一個模組是為了避免 import 迴圈：validate 不能 import pipeline
（pipeline import validate），但兩邊必須用**同一個** pattern —— 修復 pass
與它的 fail-closed gate 若各刻一份底線強調的定義，就會出現「修復認為不用
修、gate 認為要擋」或反過來的死鎖（lessons L7 那個 inject/gate 永久死鎖
就是兩份獨立實作的不變式前置條件不一致）。
"""

import re

# 底線強調：`_文字_`。允許內部有空白與括號，但不跨行、不含反引號。
UNDERSCORE_EM = re.compile(r"_([^_\n`]+)_")

# 連結／圖片 destination、autolink、裸 URL。修復 pass 必須把這些也當保護區：
# glossary.protected_mask 只保護 code span 與 fence，而含 CJK 的 URL
# （`zh.wikipedia.org/wiki/區塊鏈_(技術)`、中文檔名的圖片）在中文譯文裡完全
# 可能出現，底線被改成星號就是 404 與圖裂，而且 gate 10 看不到（<em> 不減反增）。
URLISH = re.compile(
    r"\]\([^)\n]*\)"           # ](destination "title")
    r"|<[a-zA-Z][a-zA-Z0-9+.-]*:[^>\s]*>"   # <autolink>
    r"|[a-zA-Z][a-zA-Z0-9+.-]*://[^\s)\]]+"  # 裸 URL
)
