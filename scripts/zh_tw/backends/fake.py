"""測試用後端。保留結構，把英文字母換成固定的中文字，不打任何 API。

不自己刻 fence 掃描器 —— fence / inline code 的判定一律交給
glossary.protected_mask()（它本身建立在 anchors.code_lines() 之上）。
FakeBackend 只收 chunk body 或裸字串（kind="text"，沒有 frontmatter），
所以 protected_mask() 不會因為看到 frontmatter 而炸掉。

sidebar 呼叫 backend 時走 kind="sidebar"，payload 是 SIDEBAR_PROMPT
接編號清單（"1. Label\n2. Label"）；frontmatter 欄位是「裸字串、
非編號」的 kind="text"（見 pipeline.translate_body）。兩者以 kind
分流（真實 backend 對 sidebar 不外包 prompt、對 text 外包 TEXT_PROMPT，
fake 對應地走編號分支/替換分支）。sidebar 分支把每個 label 原文整段
接在括號內回傳（"中文譯文 (Original Label)"），讓 FakeBackend 成為
sidebar.translate 那個「中文 (English)」格式 guard 眼中忠實的假
backend，不必為了遷就它而放寬 production 的 guard（Task 14 的教訓）。
"""

import re

from .. import glossary

_NUMBERED_LINE = re.compile(r"^\s*(\d+)[.)]\s+(.+?)\s*$")


class FakeBackend:
    def translate(self, text: str, *, kind: str = "markdown") -> str:
        if kind == "sidebar":
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

    # 標題行要模擬合規 backend 的「中文 (English)」格式（validate gate 9 驗
    # 後綴值 == 英文標題文字）。fake 存在是為了模擬真實 backend，真實 backend
    # 被 SYSTEM_PROMPT 要求產出這個格式，所以 fake 也要 —— 不是放寬守衛去
    # 遷就 fake（Task 14 / lessons L5 的教訓）。
    _HEADING = re.compile(r"^(#+)\s+(.*?)\s*$")
    _EXPLICIT_ANCHOR = re.compile(r"\s*(\{#[\w-]+\})\s*$")

    def _substitute(self, text: str) -> str:
        mask = glossary.protected_mask(text)
        lines = text.splitlines(keepends=True)
        out = []
        pos = 0
        for line in lines:
            protected = pos < len(mask) and mask[pos]
            m = None if protected else self._HEADING.match(line.rstrip("\n"))
            if m:
                hashes, title = m.group(1), m.group(2)
                am = self._EXPLICIT_ANCHOR.search(title)
                anchor = f" {am.group(1)}" if am else ""
                if am:
                    title = title[: am.start()].rstrip()
                nl = "\n" if line.endswith("\n") else ""
                out.append(f"{hashes} {self._latin(title)} ({title}){anchor}{nl}")
            else:
                out.append(self._sub_masked(line, mask, pos))
            pos += len(line)
        return "".join(out)

    def _sub_masked(self, line: str, mask: list[bool], start: int) -> str:
        n = len(line)
        out = []
        i = 0
        while i < n:
            protected = start + i < len(mask) and mask[start + i]
            j = i
            while j < n and (start + j < len(mask) and mask[start + j]) == protected:
                j += 1
            seg = line[i:j]
            if not protected:
                seg = self._latin(seg)
            out.append(seg)
            i = j
        return "".join(out)

    @staticmethod
    def _latin(text: str) -> str:
        return re.sub(r"[A-Za-z]{2,}", "中文", text)
