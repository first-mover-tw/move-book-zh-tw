"""`doc_ids` 的差分測試：判定權交給真正的消費者，不由我推論。

背景：`doc_ids` 的判準連續四輪被外部 review 改（R6 太窄 → R7 太寬 → R8 太窄
→ R9 撞鍵），每一輪都是拿當下語料的樣本反推語法規格（lessons L20）。第五次
去查規格才發現爭論的那個區分本身不存在 —— `site/src/plugins/yaml-sidebar.ts`
會在交給 docusaurus 前補上 `type: 'doc'`，所以 docusaurus 的 category
shorthand 在這條管線裡結構上不可達。

與其再調一次判準，這裡把「哪些字串是 doc id」的判定權還給消費鏈本身：
`tests/oracle/sidebar_doc_ids.mjs` 用**上游自己的程式碼**算出同一份 YAML 的
doc id，本檔逐一比對。判準再變，紅的是這裡，不是三個月後的 build。

沒有 `site/node_modules` 就 skip —— 但這不是一道從不執行的守衛：
`.github/workflows/pytest.yml` 的 `sidebar-oracle` job 每個 PR 都會裝 site
依賴並帶著 `SIDEBAR_ORACLE_REQUIRED=1` 跑本檔，那個變數會讓「整批 skip」
直接變成錯誤。
"""

import hashlib
import os
import random
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from zh_tw import sidebar  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ORACLE = ROOT / "tests" / "oracle" / "sidebar_doc_ids.mjs"
LOADER = ROOT / "site" / "src" / "plugins" / "yaml-sidebar.ts"

# 沒裝 site 依賴時本地 skip，但在 CI 必須是**硬失敗**：一個在 CI 全部 skip
# 卻照樣綠燈的差分測試，跟沒有這個檔一樣（`pytest.yml` 開頭記的正是同一種
# 事故 —— 守衛寫了，但沒有任何 workflow 執行過它）。
_HAVE_NODE = (ROOT / "site" / "node_modules").is_dir()
if os.environ.get("SIDEBAR_ORACLE_REQUIRED") and not _HAVE_NODE:
    raise RuntimeError(
        "SIDEBAR_ORACLE_REQUIRED=1 但找不到 site/node_modules —— "
        "差分測試會整批 skip，等於這道 gate 沒跑。"
    )

needs_node = pytest.mark.skipif(
    not _HAVE_NODE,
    reason="需要 site/node_modules（CI 由 pytest.yml 的 sidebar-oracle job 跑）",
)


def oracle_doc_ids(text: str, tmp_path: Path) -> list[str] | None:
    """上游消費鏈算出的 doc id；輸入非法（上游會 throw）時回 None。"""
    p = tmp_path / "sidebar.yml"
    p.write_text(text, encoding="utf-8")
    r = subprocess.run(
        ["node", str(ORACLE), str(p)],
        capture_output=True, text=True, cwd=ROOT, stdin=subprocess.DEVNULL,
    )
    if r.returncode != 0:
        return None
    return r.stdout.splitlines()


# --- 上游 loader 的變動偵測 ----------------------------------------------


def test_the_oracle_is_pinned_to_the_loader_it_transcribes():
    """oracle 手抄了 `yaml-sidebar.ts::processSidebar`。上游改那個檔時，
    抄本會靜默失準 —— 差分測試從此比對的是一個過期的規格，而它還是綠的。

    所以把 loader 的 sha256 釘在這裡：上游一動就紅，強迫人回去看抄本。
    這道測試本身不需要 node。"""
    digest = hashlib.sha256(LOADER.read_bytes()).hexdigest()
    assert digest == (
        "e7b5c1fdadd8d9ef7e7c53409bbb6530e51be1f4d8413ca363dad969d87c7f95"
    ), (
        f"{LOADER.relative_to(ROOT)} 已變動（實際 {digest}）。"
        f"請比對 {ORACLE.relative_to(ROOT)} 裡 processSidebar 的抄本後更新此值。"
    )


# --- 真實語料 -------------------------------------------------------------


@needs_node
@pytest.mark.parametrize("rel", ["book/sidebar.yml", "reference/sidebar.yml"])
def test_doc_ids_matches_upstream_on_the_real_corpus(rel, tmp_path):
    text = (ROOT / rel).read_text(encoding="utf-8")
    want = oracle_doc_ids(text, tmp_path)
    assert want is not None, f"{rel} 連上游都吃不下去，語料本身壞了"
    assert sidebar.doc_ids(text) == want


# --- 定點案例（每一個都對應一輪 review 的爭議） ---------------------------

CASES = {
    # 真實語料的主要形狀：沒有 type 的 mapping，loader 會補成 doc。
    "typeless doc item": {"s": [{"label": "L", "id": "a"}]},
    "字串簡寫": {"s": ["a", "b"]},
    "category + link": {"s": [
        {"type": "category", "label": "C",
         "link": {"type": "doc", "id": "c/index"},
         "items": [{"label": "X", "id": "c/x"}, "c/y"]},
    ]},
    # 第七輪 B1：customProps 底下的字串陣列不是 doc id。
    "customProps 不是 doc 引用": {"s": [
        {"label": "L", "id": "a", "customProps": {"badges": ["new", "green"], "id": "nope"}},
    ]},
    "enumerate 這個非 docusaurus 鍵": {"s": [{"label": "L", "id": "a", "enumerate": False}]},
    "type: ref": {"s": [{"type": "ref", "id": "a"}]},
    "外部連結沒有 doc id": {"s": [{"type": "link", "label": "L", "href": "https://x"}]},
}

# docusaurus 官方支援、但這條管線到不了的寫法（loader 會先補上 type）。
# 這些不能只用 skip 帶過 —— skip 不是斷言，等於沒有守衛（L5）。
UNREACHABLE = {
    # 第九輪 C1 舉的兩個形狀。
    "label 當鍵的 mapping": "s:\n  - label:\n      - a\n",
    "customProps 當鍵的 mapping": "s:\n  - customProps:\n      - a\n",
    "category shorthand（條目位置）": "s:\n  - Getting started:\n      - a\n",
    "category shorthand（根的值）": "s:\n  Getting started:\n    - a\n",
    "沒有 type 卻有 items": "s:\n  - label: C\n    items:\n      - a\n",
}


@needs_node
@pytest.mark.parametrize("name", list(UNREACHABLE))
def test_upstream_rejects_the_shapes_we_return_nothing_for(name, tmp_path):
    """上游**確實**拒收這些寫法（build 掛在 validateSidebars），所以
    `doc_ids` 回空不是漏抓，是「不替一個 build 不起來的 sidebar 編造答案」。

    這是 `test_sidebar.py::test_category_shorthand_does_not_exist_in_this_pipeline`
    的另一半：那邊釘我們的行為，這邊拿上游程式碼釘「上游真的不收」。
    """
    text = UNREACHABLE[name]
    assert oracle_doc_ids(text, tmp_path) is None, "上游竟然收下了 —— 判準要重看"
    assert sidebar.doc_ids(text) == []


@needs_node
@pytest.mark.parametrize("name", list(CASES))
def test_doc_ids_matches_upstream_on_fixed_cases(name, tmp_path):
    text = yaml.safe_dump(CASES[name], allow_unicode=True, sort_keys=False)
    want = oracle_doc_ids(text, tmp_path)
    assert want is not None, f"{name} 應該是合法 sidebar，上游卻拒收了"
    assert sidebar.doc_ids(text) == want


# --- 差分 fuzz ------------------------------------------------------------


def _rand_items(rng: random.Random, depth: int, ctr: list[int]) -> list:
    out = []
    for _ in range(rng.randint(1, 4)):
        ctr[0] += 1
        i = ctr[0]
        kind = rng.choice(["str", "typeless", "doc", "ref", "link", "cat"])
        if kind == "str":
            out.append(f"d{i}")
        elif kind == "typeless":
            it = {"label": f"L{i}", "id": f"d{i}"}
            if rng.random() < 0.3:
                it["enumerate"] = False
            if rng.random() < 0.3:
                it["customProps"] = {"badges": [f"b{i}", "green"], "id": f"nope{i}"}
            out.append(it)
        elif kind == "doc":
            out.append({"type": "doc", "id": f"d{i}", "label": f"L{i}"})
        elif kind == "ref":
            out.append({"type": "ref", "id": f"d{i}"})
        elif kind == "link":
            out.append({"type": "link", "label": f"L{i}", "href": f"https://e/{i}"})
        else:
            cat = {"type": "category", "label": f"C{i}"}
            if rng.random() < 0.6:
                cat["link"] = {"type": "doc", "id": f"c{i}/index"}
            cat["items"] = (
                _rand_items(rng, depth - 1, ctr) if depth > 0 else [f"leaf{i}"]
            )
            out.append(cat)
    return out


@needs_node
def test_doc_ids_matches_upstream_on_random_sidebars(tmp_path):
    """定點案例只覆蓋我想得到的形狀 —— 前四輪的缺陷正好都在我想不到的形狀上
    （L15 的推論：fuzz 的負面結果只在 generator 生得出該類輸入時才有意義，
    所以 generator 的 atom 表照著 `yaml-sidebar.ts` 會分支的每個型別列）。"""
    rng = random.Random(20260906)
    checked = 0
    for n in range(120):
        doc = {f"s{k}": _rand_items(rng, rng.randint(0, 3), [n * 1000])
               for k in range(rng.randint(1, 2))}
        text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False)
        want = oracle_doc_ids(text, tmp_path)
        if want is None:
            continue
        assert sidebar.doc_ids(text) == want, (
            f"第 {n} 例分歧：\n{text}\n上游={want}\n我們={sidebar.doc_ids(text)}"
        )
        checked += 1
    # generator 若因為改壞而只生出上游拒收的輸入，上面的迴圈會全部 continue
    # 而靜默全綠 —— 這正是 L5 講的「從未紅過的守衛」。
    assert checked >= 100, f"只有 {checked} 例真的被比對，generator 可能壞了"
