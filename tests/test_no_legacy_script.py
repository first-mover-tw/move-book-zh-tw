"""The legacy translate_to_zh_tw.py must stay deleted.

Its line-10 `from google import genai` was a top-level import, so `--detect`
(a pure-git operation) required the API dependency. In CI the detect step ran
before `pip install`, the ModuleNotFoundError was swallowed by
`2>/dev/null || true`, COUNT became 0, every later step was skipped, and the
job reported success while translating zero files for five months.

scripts/zh_tw/manifest.py is the replacement, and it imports only stdlib, so
`--detect` can never again depend on a backend. This guard makes the old
script's return a loud test failure.
"""

from pathlib import Path


def test_legacy_script_is_gone():
    assert not Path("scripts/translate_to_zh_tw.py").exists(), (
        "scripts/translate_to_zh_tw.py must remain deleted; use `python -m scripts.zh_tw`"
    )


def test_ci_workflow_does_not_reference_legacy_script():
    wf_text = Path(".github/workflows/translate-zh-tw.yml").read_text(encoding="utf-8")
    # The forbidden constructs must be gone from the *executed* YAML, not from a
    # comment that documents the old bug. Strip `#`-comment lines before scanning
    # (a `#` inside a run: command is not a comment, but none of the checks below
    # target such a line, and the workflow has none).
    exec_lines = [
        ln for ln in wf_text.splitlines() if not ln.lstrip().startswith("#")
    ]
    wf = "\n".join(exec_lines)

    assert "translate_to_zh_tw.py" not in wf, (
        "the workflow still calls the deleted legacy script"
    )
    # the workflow must run the module form and set up Python before detecting
    assert "python -m scripts.zh_tw --detect" in wf
    setup_idx = wf.index("Install dependencies")
    detect_idx = wf.index("Detect files needing translation")
    assert setup_idx < detect_idx, "Setup/Install must precede Detect"
    # the silencing that hid the five-month failure must be gone
    assert "2>/dev/null" not in wf
    # force-push that overwrote unmerged PRs must be gone
    assert "push -f" not in wf and "push --force" not in wf
