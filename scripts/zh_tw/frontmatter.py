"""Frontmatter 的拆解與規範化重建。

輸出一律以 yaml.safe_dump 產生，故 LLM 不再有機會弄壞這段結構。
"""

import re

import yaml

TRANSLATABLE_KEYS = frozenset({"description", "title"})

_FENCE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


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
    dumped = yaml.safe_dump(
        meta, allow_unicode=True, default_flow_style=False, sort_keys=False
    ).rstrip("\n")
    return _end_with_newline(f"---\n{dumped}\n---\n\n{body}")


def _end_with_newline(text: str) -> str:
    """空字串維持空字串：憑空生出一個只有換行的檔案不是修復，是製造差異。"""
    return text if not text or text.endswith("\n") else text + "\n"
