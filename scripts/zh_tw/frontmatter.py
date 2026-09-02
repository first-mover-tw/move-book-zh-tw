"""Frontmatter 的拆解與規範化重建。

輸出一律以 yaml.safe_dump 產生，故 LLM 不再有機會弄壞這段結構。
"""

import re

import yaml

TRANSLATABLE_KEYS = frozenset({"description", "title"})

_FENCE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


class _PrettierDumper(yaml.SafeDumper):
    """讓 safe_dump 的輸出盡量貼近 prettier 的 YAML 規則。

    pyyaml 預設與本 repo 的 prettier 設定不合，會讓每個帶 keywords/questions 的檔案
    永久停在 prettier 不合規（2026-09-01 掃描：15 個含 `questions:` 的檔案，15 個全紅，
    1:1 對應）。prettier 不在 CI 上，所以 PR #16/#17/#21 三批都沒被任何 gate 攔下。

    ⚠️ 這個 dumper 是 best-effort，不是合規保證 —— 權威是 translate workflow 裡
    真正跑的 `prettier --write`（見 .github/workflows/translate-zh-tw.yml）。
    理由：prettier 對 YAML 純量的處理取決於**型別**而非長度 ——
    plain scalar 多長都留單行，quoted scalar（值含 `: ` 時 YAML 強制加引號）
    則會用 east-asian 顯示寬度做 greedy fill 折行。在 python 這端把後者複製一遍
    等於手刻 prettier 的 printer 演算法，會隨 prettier 版本漂移（lessons L2：
    不要用廉價代理量代替真實性質）。所以這裡只做「不會錯」的那半，剩下交給 prettier。
    """

    def increase_indent(self, flow=False, indentless=False):
        # sequence 要縮排（pyyaml 預設 `- x` 頂格，prettier 要 `  - x`）
        return super().increase_indent(flow, False)


def split(text: str) -> tuple[dict, str]:
    m = _FENCE.match(text)
    if not m:
        return {}, text
    meta = yaml.safe_load(m.group(1)) or {}
    if not isinstance(meta, dict):
        return {}, text
    body = text[m.end():]
    return meta, body.lstrip("\n")


def join(meta: dict, body: str) -> str:
    # 結尾換行在這裡收斂，不留給呼叫端：backend 的輸出常常沒有結尾換行，
    # 而八道 gate 全是內容檢查、prettier 又不在 CI 上，於是「檔尾缺換行」
    # 每一輪自動翻譯都原樣長回來（2026-08-31 連兩批 PR #16/#17 共 6 檔）。
    # join 是所有 .md 產出的唯一匯流點，補在這裡才是一次修完。
    if not meta:
        return _end_with_newline(body)
    dumped = yaml.dump(
        meta,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        Dumper=_PrettierDumper,
        # 不要在 80 欄折行：prettier 對 plain scalar 一律留單行，pyyaml 預設的
        # 80 欄折行對它們就是純粹的不合規（2026-09-01 實測 glossary/manifest）。
        # quoted scalar 反過來該折，但折法由 prettier 決定，不在這裡猜。
        width=10**9,
    ).rstrip("\n")
    return _end_with_newline(f"---\n{dumped}\n---\n\n{body}")


def _end_with_newline(text: str) -> str:
    """空字串維持空字串：憑空生出一個只有換行的檔案不是修復，是製造差異。"""
    return text if not text or text.endswith("\n") else text + "\n"
