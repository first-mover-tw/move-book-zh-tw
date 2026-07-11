import json
import subprocess

from scripts.zh_tw import heal_manifest, manifest

# 已知在真實 manifest 裡結構指紋吻合 merge-base 的可修復路徑，
# 以及唯一結構不符、留給全譯的路徑（見 task-13-brief.md）。
KNOWN_HEALABLE_PATH = "book/move-basics/vector.md"
KNOWN_UNRECOVERABLE_PATH = "book/object/index.md"
DANGLING_SHA = "0" * 40  # 不存在於任何 repo 的假 blob SHA

# heal 前的 manifest 快照（Task 13 --apply 之前的最後一個 commit）。
# 這是一次性普查（像 test_baseline.py 一樣釘死在固定 commit），
# 不可用 live 的 scripts/translation-manifest.json 取代 —— 那份已經被
# heal --apply 修復過，任何時候讀它都不會再有 30 筆懸空條目。
PRE_HEAL_MANIFEST_REF = "ba52a152"


def _manifest_at(tmp_path, ref):
    content = subprocess.run(
        ["git", "show", f"{ref}:scripts/translation-manifest.json"],
        capture_output=True, text=True, check=True,
    ).stdout
    tmp_manifest = tmp_path / "translation-manifest.json"
    tmp_manifest.write_text(content, encoding="utf-8")
    return tmp_manifest


def test_heal_census_pinned_to_pre_heal_manifest(tmp_path, monkeypatch):
    """凍結的一次性普查：在 heal --apply 修復前（ba52a152）的 manifest 快照上
    跑 heal 的判定邏輯，應得到 30 筆可修復、1 筆不可修復。

    這不是即時查詢 —— 釘死在 ba52a152，類比 test_baseline.py。live 的
    scripts/translation-manifest.json 已在 Task 13 第二個 commit 被
    --apply 修復，讀它只會得到 0 筆懸空條目，不能用來驗證這個普查。
    """
    tmp_manifest = _manifest_at(tmp_path, PRE_HEAL_MANIFEST_REF)
    monkeypatch.setattr(manifest, "MANIFEST_PATH", tmp_manifest)

    healed, unrecoverable = heal_manifest.heal(dry_run=True)

    assert len(healed) == 30
    assert len(unrecoverable) == 1
    assert unrecoverable == [KNOWN_UNRECOVERABLE_PATH]


def test_heal_dry_run_does_not_write(tmp_path, monkeypatch):
    """dry_run=True 不得修改它讀取的 manifest。用 pre-heal 快照（含真正的
    懸空條目）跑，這樣如果 dry_run 沒守住,測試才會真的抓到寫入。
    """
    tmp_manifest = _manifest_at(tmp_path, PRE_HEAL_MANIFEST_REF)
    monkeypatch.setattr(manifest, "MANIFEST_PATH", tmp_manifest)
    before = tmp_manifest.read_text(encoding="utf-8")

    healed, _ = heal_manifest.heal(dry_run=True)
    assert len(healed) > 0  # 確認這次跑真的會進入「可修復」分支，不是空跑

    after = tmp_manifest.read_text(encoding="utf-8")
    assert before == after


def test_constructed_dangling_entries_healable_vs_unrecoverable(tmp_path, monkeypatch):
    """用臨時 manifest 建構兩筆懸空條目：一筆指紋吻合 merge-base（可修復），
    一筆指紋不符（不可修復）。不動真正的 manifest 檔案。
    """
    tmp_manifest = tmp_path / "translation-manifest.json"
    tmp_manifest.write_text(
        json.dumps(
            {
                KNOWN_HEALABLE_PATH: DANGLING_SHA,
                KNOWN_UNRECOVERABLE_PATH: DANGLING_SHA,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(manifest, "MANIFEST_PATH", tmp_manifest)

    healed, unrecoverable = heal_manifest.heal(dry_run=True)

    assert healed == [KNOWN_HEALABLE_PATH]
    assert unrecoverable == [KNOWN_UNRECOVERABLE_PATH]


def test_healed_entry_written_with_merge_base_blob_sha(tmp_path, monkeypatch):
    """--apply 後,已修復條目記錄的 SHA 必須是該路徑在 merge-base 的 blob SHA。"""
    tmp_manifest = tmp_path / "translation-manifest.json"
    tmp_manifest.write_text(
        json.dumps({KNOWN_HEALABLE_PATH: DANGLING_SHA}, indent=2),
        encoding="utf-8",
    )
    monkeypatch.setattr(manifest, "MANIFEST_PATH", tmp_manifest)

    healed, unrecoverable = heal_manifest.heal(dry_run=False)

    assert healed == [KNOWN_HEALABLE_PATH]
    assert unrecoverable == []

    expected_sha = manifest.blob_sha(heal_manifest.MERGE_BASE, KNOWN_HEALABLE_PATH)
    written = json.loads(tmp_manifest.read_text(encoding="utf-8"))
    assert written[KNOWN_HEALABLE_PATH] == expected_sha
    assert expected_sha != DANGLING_SHA
