"""測試用後端。保留結構，把英文字母換成固定的中文字，不打任何 API。"""

import re


class FakeBackend:
    def translate(self, text: str, *, kind: str = "markdown") -> str:
        out, in_fence = [], False
        for line in text.splitlines(keepends=True):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                out.append(line)
                continue
            if in_fence:
                out.append(line)
                continue
            out.append(re.sub(r"[A-Za-z]{2,}", "中文", line))
        return "".join(out)
