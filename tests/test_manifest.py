import ast
import subprocess
import sys
from pathlib import Path

from scripts.zh_tw import manifest


def test_manifest_imports_only_stdlib():
    """AST-based import guard: localises which import broke the rule.

    This test is a fast, precise localisation aid for detecting unwanted imports.
    The real guarantee that manifest.py does not import Gemini/backend SDKs is
    test_detect_runs_without_genai_installed, which proves it at runtime.

    This AST localiser catches:
    - Direct imports: `import google.genai` → adds "google"
    - Absolute ImportFrom: `from google import genai` → adds "google"
    - Relative imports: `from . import anchors` → adds "anchors"

    It does NOT catch importlib.import_module() with computed names;
    only the behavioural test catches that at runtime.
    """
    src = Path("scripts/zh_tw/manifest.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:  # relative import: from . import X or from .. import X
                for alias in node.names:
                    imported.add(alias.name.split(".")[0])
            elif node.module:  # absolute import: from X import Y
                imported.add(node.module.split(".")[0])
    assert imported == {"json", "subprocess", "pathlib"}


def test_detect_runs_without_genai_installed():
    """在沒有 google-genai 的乾淨環境裡，stale_files 必須能跑並回傳整數。
    具體數字隨 backfill 遞減，屬 stale 計數測試的職責，不在這裡重複釘死。

    This is the behavioural test: it proves that manifest.stale_files() actually
    works without the Gemini SDK, including catching any transitive imports through
    modules whose names don't contain 'genai' or 'backends'.
    """
    r = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.modules['google']=None;"
         "from scripts.zh_tw import manifest; print(len(manifest.stale_files('english-main')))"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip().isdigit(), f"Expected an integer count, got {r.stdout.strip()!r}"


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


def test_tracked_files_handles_space_and_nonascii_paths():
    """Regression: .split() splits on any whitespace, silently breaking paths with spaces.
    -z flag disables path quoting and gives unambiguous null separator.
    """
    import os
    import tempfile
    import subprocess as sp

    # Create scratch tree with space-containing and non-ASCII paths
    with tempfile.TemporaryDirectory() as tmpdir:
        index_file = os.path.join(tmpdir, "index")
        # Create blob objects
        space_blob = sp.run(
            ["git", "hash-object", "-w", "--stdin"],
            input=b"# space path\n",
            capture_output=True, check=True,
        ).stdout.decode().strip()
        nonascii_blob = sp.run(
            ["git", "hash-object", "-w", "--stdin"],
            input=b"# non-ascii path\n",
            capture_output=True, check=True,
        ).stdout.decode().strip()

        # Build tree via temporary index
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = index_file
        sp.run(
            ["git", "update-index", "--add", "--cacheinfo",
             "100644", space_blob, "book/path with space.md"],
            env=env, check=True, capture_output=True,
        )
        sp.run(
            ["git", "update-index", "--add", "--cacheinfo",
             "100644", nonascii_blob, "book/漢.md"],
            env=env, check=True, capture_output=True,
        )
        tree_sha = sp.run(
            ["git", "write-tree"],
            env=env, check=True, capture_output=True, text=True,
        ).stdout.strip()
        commit_sha = sp.run(
            ["git", "commit-tree", tree_sha, "-m", "test"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()

        # Verify tracked_files returns both paths intact (not split on space)
        files = manifest.tracked_files(commit_sha)
        assert "book/path with space.md" in files
        assert "book/漢.md" in files
        assert len(files) == 2
