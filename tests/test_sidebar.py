import subprocess

import pytest
import yaml

from scripts.zh_tw import sidebar

EN = """# comment
bookSidebar:
  - label: The Move Book
    id: index
  - type: category
    label: Before We Begin
    items:
      - label: Install Sui
        id: before-we-begin/install-sui
"""

PREV_ZH = """# comment
bookSidebar:
  - label: Move 寶典 (The Move Book)
    id: index
  - type: category
    label: 開始之前 (Before We Begin)
    items:
      - label: 安裝 Sui (Install Sui)
        id: before-we-begin/install-sui
"""


class EchoBackend:
    def __init__(self):
        self.calls: list[str] = []

    def translate(self, text, *, kind="markdown"):
        self.calls.append(text)
        return "\n".join(
            f"{i + 1}. 譯{line.split('. ', 1)[1]}"
            for i, line in enumerate(text.strip().splitlines())
            if ". " in line
        )


def _git_show(ref: str, path: str) -> str:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    if r.returncode != 0:
        pytest.skip(f"{ref}:{path} not available in this checkout")
    return r.stdout


def test_labels_extracts_in_order():
    assert sidebar.labels(EN) == ["The Move Book", "Before We Begin", "Install Sui"]


def test_skeleton_masks_label_values():
    assert sidebar.skeleton(EN) == sidebar.skeleton(PREV_ZH)


def test_skeleton_only_masks_labels_nothing_else():
    out = sidebar.skeleton(EN)
    assert "id: index" in out
    assert "type: category" in out
    assert "before-we-begin/install-sui" in out
    assert out.count("<L>") == 3


def test_apply_replaces_labels_preserving_structure():
    out = sidebar.apply(EN, ["甲", "乙", "丙"])
    assert sidebar.labels(out) == ["甲", "乙", "丙"]
    assert sidebar.skeleton(out) == sidebar.skeleton(EN)
    assert "id: before-we-begin/install-sui" in out


def test_apply_roundtrips_labels():
    xs = ["甲", "乙", "丙"]
    out = sidebar.apply(EN, xs)
    assert sidebar.labels(out) == xs
    assert sidebar.skeleton(out) == sidebar.skeleton(EN)


def test_apply_quotes_labels_with_yaml_special_chars():
    out = sidebar.apply("a:\n  - label: X\n", ["模組: 進階"])
    assert "label: '模組: 進階'" in out
    assert yaml.safe_load(out) is not None


def test_apply_raises_on_count_mismatch():
    with pytest.raises(ValueError):
        sidebar.apply(EN, ["只有一個"])


def test_translate_carries_forward_existing_labels():
    """英文 label 未變的項目，直接沿用舊譯文，不重新翻譯。"""
    backend = EchoBackend()
    out = sidebar.translate(EN, PREV_ZH, backend)
    assert out == PREV_ZH
    assert backend.calls == []  # 全部沿用，backend 完全沒被呼叫


def test_translate_only_calls_backend_for_new_labels():
    en_plus = EN + "  - label: Brand New\n    id: new\n"
    backend = EchoBackend()
    out = sidebar.translate(en_plus, PREV_ZH, backend)
    assert "Move 寶典 (The Move Book)" in out  # 舊的沿用
    assert "譯Brand New" in out  # 新的才翻
    assert sidebar.skeleton(out) == sidebar.skeleton(en_plus)
    assert len(backend.calls) == 1  # 只為新 label 呼叫一次


def test_translate_output_parses_as_yaml():
    out = sidebar.translate(EN, PREV_ZH, EchoBackend())
    parsed = yaml.safe_load(out)
    assert parsed is not None
    assert sidebar.skeleton(out) == sidebar.skeleton(EN)


def test_translate_raises_when_backend_breaks_skeleton():
    class BrokenBackend:
        def translate(self, text, *, kind="markdown"):
            # Return the wrong number of numbered entries -> _parse_numbered raises
            return "1. 只有一個"

    en_plus = EN + "  - label: One\n    id: a\n  - label: Two\n    id: b\n"
    with pytest.raises(ValueError):
        sidebar.translate(en_plus, PREV_ZH, BrokenBackend())


class RealFakeBackend:
    """用於 real-data 測試：模擬翻譯（避免對 API 依賴），保留編號格式。"""

    def translate(self, text, *, kind="markdown"):
        out = []
        for line in text.strip().splitlines():
            if ". " not in line:
                continue
            num, rest = line.split(". ", 1)
            if num.strip().isdigit():
                out.append(f"{num.strip()}. 譯{rest}")
        return "\n".join(out)


def test_translate_real_reference_sidebar():
    en = _git_show("english-main", "reference/sidebar.yml")
    prev = _git_show("HEAD", "reference/sidebar.yml")
    out = sidebar.translate(en, prev, RealFakeBackend())
    assert sidebar.skeleton(out) == sidebar.skeleton(en)
    assert yaml.safe_load(out) is not None
    assert all(l.strip() for l in sidebar.labels(out))


def test_translate_real_book_sidebar():
    en = _git_show("english-main", "book/sidebar.yml")
    prev = _git_show("HEAD", "book/sidebar.yml")
    out = sidebar.translate(en, prev, RealFakeBackend())
    assert sidebar.skeleton(out) == sidebar.skeleton(en)
    assert yaml.safe_load(out) is not None
    assert all(l.strip() for l in sidebar.labels(out))
