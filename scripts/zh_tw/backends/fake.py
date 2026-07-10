"""測試用後端。保留結構，把英文字母換成固定的中文字，不打任何 API。

不自己刻 fence 掃描器 —— fence / inline code 的判定一律交給
glossary.protected_mask()（它本身建立在 anchors.code_lines() 之上）。
FakeBackend 只收 chunk body 或裸字串（kind="text"，沒有 frontmatter），
所以 protected_mask() 不會因為看到 frontmatter 而炸掉。

sidebar 呼叫 backend 時走的是 kind="text"，payload 是一段編號清單
（見 sidebar.SIDEBAR_PROMPT 之後接的 "1. Label\n2. Label"）。這與
frontmatter 欄位那種「裸字串、非編號」的 kind="text" 用法（見
pipeline.translate_body）不同形狀，必須用內容而非單靠 kind 分流：
只有偵測到編號清單時才走 sidebar 專用分支，其餘 kind="text" 仍走
一般的 Latin→中文替換，不影響既有 frontmatter 測試。sidebar 分支
把每個 label 原文整段接在括號內回傳（"中文譯文 (Original Label)"），
讓 FakeBackend 成為 sidebar.translate 那個「中文 (English)」格式
guard 眼中忠實的假 backend，不必為了遷就它而放寬 production 的
guard（Task 14 的教訓）。
"""

import re

from .. import glossary

_NUMBERED_LINE = re.compile(r"^\s*(\d+)[.)]\s+(.+?)\s*$")


class FakeBackend:
    def translate(self, text: str, *, kind: str = "markdown") -> str:
        if kind == "text":
            numbered = [
                (m.group(1), m.group(2))
                for line in text.splitlines()
                if (m := _NUMBERED_LINE.match(line))
            ]
            if numbered:
                return "\n".join(
                    f"{idx}. {self._substitute(label)} ({label})"
                    for idx, label in numbered
                )
        return self._substitute(text)

    def _substitute(self, text: str) -> str:
        mask = glossary.protected_mask(text)
        n = len(text)
        out = []
        i = 0
        while i < n:
            protected = mask[i]
            j = i
            while j < n and mask[j] == protected:
                j += 1
            seg = text[i:j]
            if not protected:
                seg = re.sub(r"[A-Za-z]{2,}", "中文", seg)
            out.append(seg)
            i = j
        return "".join(out)
