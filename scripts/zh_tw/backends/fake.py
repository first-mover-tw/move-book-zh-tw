"""測試用後端。保留結構，把英文字母換成固定的中文字，不打任何 API。

不自己刻 fence 掃描器 —— fence / inline code 的判定一律交給
glossary.protected_mask()（它本身建立在 anchors.code_lines() 之上）。
FakeBackend 只收 chunk body 或裸字串（kind="text"，沒有 frontmatter），
所以 protected_mask() 不會因為看到 frontmatter 而炸掉。
"""

import re

from .. import glossary


class FakeBackend:
    def translate(self, text: str, *, kind: str = "markdown") -> str:
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
