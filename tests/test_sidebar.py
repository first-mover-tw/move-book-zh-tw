import re
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
        out = []
        for line in text.strip().splitlines():
            m = re.match(r"^\s*(\d+)\.\s+(.+)$", line)
            if m:
                out.append(f"{m.group(1)}. 譯{m.group(2)}")
        return "\n".join(out)


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


# --- Finding 1: reuse-map key derivation ---------------------------------


class RecordingBackend:
    """記錄實際被要求翻譯（新）的 label，用來斷言沒被誤判成「新」。"""

    def __init__(self):
        self.calls: list[str] = []

    def translate(self, text, *, kind="markdown"):
        lines = [l for l in text.strip().splitlines() if l.strip() and l.strip()[0].isdigit()]
        sent = [l.split(". ", 1)[-1] if ". " in l else l for l in lines]
        self.calls += sent
        return "\n".join(f"{i + 1}. 譯{s}" for i, s in enumerate(sent))


@pytest.mark.parametrize(
    "zh_label,en_label",
    [
        ("A. 術語表 (Glossary)", "A. Glossary"),
        ("2024 遷移指南 (2024 Migration Guide)", "2024 Migration Guide"),
        ("2.1 整數 (Integers)", "2.1 Integers"),
        ("BCS", "BCS"),
    ],
)
def test_zh_label_key_matches_english_label(zh_label, en_label):
    assert sidebar._zh_label_key(zh_label) == en_label


def test_translate_reuses_appendix_letter_and_2024_migration_labels():
    """字母前綴（附錄）與 "2024 " 這種「看起來像編號但其實是名稱一部分」的
    label 都必須沿用舊譯文，不重新呼叫 backend（finding 1 的迴歸測試）。"""
    en = (
        "sidebar:\n"
        "  - label: A. Glossary\n"
        "  - label: F. Acknowledgements\n"
        "  - label: 2024 Migration Guide\n"
        "  - label: 2.1 Integers\n"
        "  - label: BCS\n"
    )
    prev_zh = (
        "sidebar:\n"
        "  - label: A. 術語表 (Glossary)\n"
        "  - label: F. 致謝 (Acknowledgements)\n"
        "  - label: 2024 遷移指南 (2024 Migration Guide)\n"
        "  - label: 2.1 整數 (Integers)\n"
        "  - label: BCS\n"
    )
    backend = RecordingBackend()
    out = sidebar.translate(en, prev_zh, backend)
    assert out == prev_zh
    assert backend.calls == []


def test_translate_real_book_sidebar_reuses_appendix_and_migration_labels():
    """對照真實 HEAD/english-main 資料：附錄 6 個 label 與 2024 Migration Guide
    都不應出現在被送去 backend 的清單中。"""
    en = _git_show("english-main", "book/sidebar.yml")
    prev = _git_show("HEAD", "book/sidebar.yml")
    backend = RecordingBackend()
    sidebar.translate(en, prev, backend)
    appendix_words = [
        "Glossary", "Reserved Addresses", "Transfer Functions",
        "Publications", "Contributing", "Acknowledgements",
    ]
    appendix_sent = [c for c in backend.calls if any(w in c for w in appendix_words)]
    migration_sent = [c for c in backend.calls if "Migration" in c]
    assert appendix_sent == []
    assert migration_sent == []


# --- Finding 2: YAML-safe quoting -----------------------------------------


@pytest.mark.parametrize(
    "label",
    ["- leading dash", "123", "true", "null", "key: value", "'quoted'"],
)
def test_apply_quotes_labels_yaml_safe_roundtrip(label):
    out = sidebar.apply("a:\n  - label: X\n", [label])
    parsed = yaml.safe_load(out)
    got = parsed["a"][0]["label"]
    assert isinstance(got, str)
    assert got == label


def test_apply_quotes_empty_label_roundtrips():
    out = sidebar.apply("a:\n  - label: X\n", [""])
    parsed = yaml.safe_load(out)
    got = parsed["a"][0]["label"]
    # empty label must not silently vanish or turn into None
    assert isinstance(got, str)
    assert got == ""


def test_translate_keeps_type_changing_backend_output_as_string():
    """backend 若翻出「123」這種看起來像數字的字，apply 的引號 + translate
    的 postcondition 要合力保住它是字串，而不是讓輸出被 yaml 解成 int。"""
    class TypeChangingBackend:
        def translate(self, text, *, kind="markdown"):
            return "1. 123"

    en_plus = EN + "  - label: Numeric New\n    id: c\n"
    out = sidebar.translate(en_plus, PREV_ZH, TypeChangingBackend())
    parsed = yaml.safe_load(out)
    new_label = parsed["bookSidebar"][2]["label"]
    assert isinstance(new_label, str)
    assert new_label == "123"


def test_translate_output_labels_are_all_nonempty_strings():
    out = sidebar.translate(EN, PREV_ZH, EchoBackend())
    parsed = yaml.safe_load(out)

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "label":
                    yield v
                else:
                    yield from walk(v)
        elif isinstance(node, list):
            for item in node:
                yield from walk(item)

    for lv in walk(parsed):
        assert isinstance(lv, str)
        assert lv != ""


# --- Finding 3: duplicate numbered lines ------------------------------------


def test_parse_numbered_raises_on_duplicate_index():
    with pytest.raises(ValueError):
        sidebar._parse_numbered("1. 甲\n2. 乙\n2. 丙", 3)


def test_parse_numbered_raises_on_missing_index():
    with pytest.raises(ValueError):
        sidebar._parse_numbered("1. 甲\n3. 丙", 3)


def test_translate_raises_on_duplicate_numbered_response():
    class DupBackend:
        def translate(self, text, *, kind="markdown"):
            return "1. 甲\n1. 乙"

    en_plus = EN + "  - label: One\n    id: a\n  - label: Two\n    id: b\n"
    with pytest.raises(ValueError):
        sidebar.translate(en_plus, PREV_ZH, DupBackend())


# --- Sidebar instructions reach the backend --------------------------------


class EchoingBackend:
    """把送進來的 payload 原封不動記下來，用來檢查 sidebar 指示是否送達。"""

    def __init__(self):
        self.payload = ""

    def translate(self, text, *, kind="markdown"):
        self.payload = text
        lines = [l for l in text.strip().splitlines() if l.strip() and l.strip()[0].isdigit()]
        sent = [l.split(". ", 1)[-1] for l in lines]
        return "\n".join(f"{i + 1}. 譯{s}" for i, s in enumerate(sent))


def test_translate_sends_sidebar_instruction_to_backend():
    en_plus = EN + "  - label: Brand New\n    id: new\n"
    backend = EchoingBackend()
    sidebar.translate(en_plus, PREV_ZH, backend)
    assert "中文" in backend.payload
    assert "English" in backend.payload
    assert "編號" in backend.payload
    assert backend.payload.startswith(sidebar.SIDEBAR_PROMPT)
    assert "Brand New" in backend.payload
