import json

from scripts.zh_tw import heal_manifest, manifest

# 已知在真實 manifest 裡結構指紋吻合 merge-base 的可修復路徑，
# 以及唯一結構不符、留給全譯的路徑（見 task-13-brief.md）。
KNOWN_HEALABLE_PATH = "book/move-basics/vector.md"
KNOWN_UNRECOVERABLE_PATH = "book/object/index.md"
DANGLING_SHA = "0" * 40  # 不存在於任何 repo 的假 blob SHA


def test_heal_dry_run_reports_30_healable_1_unrecoverable():
    healed, unrecoverable = heal_manifest.heal(dry_run=True)
    assert len(healed) == 30
    assert len(unrecoverable) == 1
    assert unrecoverable == [KNOWN_UNRECOVERABLE_PATH]


def test_heal_dry_run_does_not_write():
    before = manifest.MANIFEST_PATH.read_text(encoding="utf-8")
    heal_manifest.heal(dry_run=True)
    after = manifest.MANIFEST_PATH.read_text(encoding="utf-8")
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
