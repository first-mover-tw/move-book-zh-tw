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
    if not meta:
        return body
    dumped = yaml.safe_dump(
        meta, allow_unicode=True, default_flow_style=False, sort_keys=False
    ).rstrip("\n")
    return f"---\n{dumped}\n---\n\n{body}"
