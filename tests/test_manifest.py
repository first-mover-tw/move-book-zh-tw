import subprocess
import sys

from scripts.zh_tw import manifest


def test_module_does_not_import_any_backend():
    """D1 的結構性根除:detect 路徑不得觸及 google-genai。"""
    src = manifest.__file__
    code = open(src, encoding="utf-8").read()
    assert "genai" not in code
    assert "backends" not in code


def test_detect_runs_without_genai_installed():
    """在沒有 google-genai 的乾淨環境裡,stale_files 必須能跑。"""
    r = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.modules['google']=None;"
         "from scripts.zh_tw import manifest; print(len(manifest.load()))"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr


def test_blob_sha_reads_from_ref_not_worktree():
    sha = manifest.blob_sha("english-main", "book/404.md")
    assert sha and len(sha) == 40


def test_blob_sha_returns_none_for_missing_path():
    assert manifest.blob_sha("english-main", "nope/missing.md") is None


def test_orphans_finds_upstream_deleted_file():
    """D9: 上游在 #223 刪除了 transfer-restrictions.md。"""
    assert "book/storage/transfer-restrictions.md" in manifest.orphans("english-main")


def test_stale_files_is_nonempty_before_backfill():
    assert len(manifest.stale_files("english-main")) == 151
