import subprocess
import sys

import pytest

from scripts.zh_tw import anchors
from scripts.zh_tw.backends import base, fake


def test_fake_backend_is_deterministic():
    b = fake.FakeBackend()
    assert b.translate("hello") == b.translate("hello")


def test_fake_backend_preserves_structure():
    """fake 後端把英文標題換成假中文，但保留標題數與 fence 數，讓 pipeline 測試可用。

    用 anchors.headings()/anchors.fence_lines() 量測，不用 .count("#")——
    後者對垃圾輸出一樣會過。
    """
    b = fake.FakeBackend()
    src = "# Title\n\n```move\nx\n```\n\n## Sub\n"
    out = b.translate(src)
    assert len(anchors.headings(out)) == len(anchors.headings(src)) == 2
    assert anchors.fence_lines(out) == anchors.fence_lines(src) == 2


def test_fake_backend_tilde_fence_untouched():
    b = fake.FakeBackend()
    src = "# Heading\n\n~~~move\nlet Foo = 1;\n~~~\n"
    out = b.translate(src)
    assert "let Foo = 1;\n" in out
    assert anchors.fence_lines(out) == anchors.fence_lines(src) == 2


def test_fake_backend_four_backtick_fence_with_nested_three_backtick():
    b = fake.FakeBackend()
    src = "# Heading\n\n````move\nExample code with ```nested``` fence.\n````\n"
    out = b.translate(src)
    assert "Example code with ```nested``` fence.\n" in out
    assert anchors.fence_lines(out) == anchors.fence_lines(src) == 2


def test_fake_backend_fence_inside_html_comment_untouched():
    b = fake.FakeBackend()
    src = "# Heading\n\n<!--\n```move\nCommentedOutCode\n```\n-->\n\nSome text here.\n"
    out = b.translate(src)
    assert "```move\nCommentedOutCode\n```" in out


def test_fake_backend_bare_string_no_markdown_translates_without_raising():
    """kind='text' 路徑：frontmatter 的值是裸字串，沒有 frontmatter 本身，
    不該讓 anchors.code_lines() 誤判成整份文件而炸 FrontmatterPassedIn。"""
    b = fake.FakeBackend()
    out = b.translate("Vectors in Move.", kind="text")
    assert out != "Vectors in Move."
    assert "中文" in out


def test_fake_backend_inline_code_not_translated():
    b = fake.FakeBackend()
    src = "Call `MoveFunction` to do the thing."
    out = b.translate(src)
    assert "`MoveFunction`" in out


def test_get_resolves_fake():
    assert isinstance(base.get("fake"), fake.FakeBackend)


def test_get_rejects_unknown_backend():
    with pytest.raises(ValueError, match="unknown backend"):
        base.get("nope")


def test_system_prompt_embeds_glossary_rules():
    assert "函式" in base.SYSTEM_PROMPT
    assert "迴圈" in base.SYSTEM_PROMPT


def test_get_imports_backends_lazily(monkeypatch):
    """base.get() 只在真的要用到某個後端時才 import 它——即使 google SDK
    整個被打掉，'fake' 後端仍然能正常解析。"""
    monkeypatch.setitem(sys.modules, "google", None)
    assert isinstance(base.get("fake"), fake.FakeBackend)


# --- claude_cli.ClaudeCLIBackend ---------------------------------------
#
# subprocess.run 一律被 monkeypatch 掉：測試只斷言「會呼叫什麼」與
# 「回傳/例外怎麼處理」，絕不真的 shell 出去執行 `claude`（我們本來就
# 跑在 Claude 底下，遞迴呼叫沒有意義而且可能真的打 API）。


def test_claude_cli_backend_constructs_expected_argv(monkeypatch):
    from scripts.zh_tw.backends import claude_cli

    monkeypatch.delenv("ZH_TW_CLAUDE_MODEL", raising=False)
    monkeypatch.delenv("ZH_TW_TIMEOUT", raising=False)

    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(argv, 0, stdout="翻譯結果", stderr="")

    monkeypatch.setattr(claude_cli.subprocess, "run", fake_run)
    b = claude_cli.ClaudeCLIBackend()
    out = b.translate("hello")

    argv = captured["argv"]
    assert argv[0] == "claude"
    assert argv[1] == "-p"
    assert argv[2] == "--model"
    assert argv[3] == "haiku"
    assert "hello" in argv[4]
    assert claude_cli.SYSTEM_PROMPT in argv[4]
    assert captured["kwargs"]["timeout"] == 600
    assert out == "翻譯結果\n"


def test_claude_cli_backend_reads_model_env_after_import(monkeypatch):
    """MODEL 不能是 module-level 常數：import 之後改環境變數必須立即生效
    (Defect 2)。"""
    from scripts.zh_tw.backends import claude_cli

    monkeypatch.setenv("ZH_TW_CLAUDE_MODEL", "sonnet")

    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        return subprocess.CompletedProcess(argv, 0, stdout="ok", stderr="")

    monkeypatch.setattr(claude_cli.subprocess, "run", fake_run)
    claude_cli.ClaudeCLIBackend().translate("hello")

    assert captured["argv"][3] == "sonnet"


def test_claude_cli_backend_honours_timeout_env(monkeypatch):
    from scripts.zh_tw.backends import claude_cli

    monkeypatch.setenv("ZH_TW_TIMEOUT", "42")

    captured = {}

    def fake_run(argv, **kwargs):
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(argv, 0, stdout="ok", stderr="")

    monkeypatch.setattr(claude_cli.subprocess, "run", fake_run)
    claude_cli.ClaudeCLIBackend().translate("hello")

    assert captured["kwargs"]["timeout"] == 42


def test_claude_cli_backend_raises_on_nonzero_exit(monkeypatch):
    from scripts.zh_tw.backends import claude_cli

    def fake_run(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 1, stdout="", stderr="boom")

    monkeypatch.setattr(claude_cli.subprocess, "run", fake_run)
    b = claude_cli.ClaudeCLIBackend()
    with pytest.raises(RuntimeError, match="boom"):
        b.translate("hello")


def test_claude_cli_backend_raises_on_empty_stdout(monkeypatch):
    from scripts.zh_tw.backends import claude_cli

    def fake_run(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    monkeypatch.setattr(claude_cli.subprocess, "run", fake_run)
    b = claude_cli.ClaudeCLIBackend()
    with pytest.raises(RuntimeError, match="空字串"):
        b.translate("hello")


def test_claude_cli_backend_raises_on_whitespace_only_stdout(monkeypatch):
    from scripts.zh_tw.backends import claude_cli

    def fake_run(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, stdout="   \n", stderr="")

    monkeypatch.setattr(claude_cli.subprocess, "run", fake_run)
    b = claude_cli.ClaudeCLIBackend()
    with pytest.raises(RuntimeError, match="空字串"):
        b.translate("hello")


def test_claude_cli_backend_success_returns_stripped_stdout_with_trailing_newline(monkeypatch):
    from scripts.zh_tw.backends import claude_cli

    def fake_run(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, stdout="  翻譯結果  \n\n", stderr="")

    monkeypatch.setattr(claude_cli.subprocess, "run", fake_run)
    b = claude_cli.ClaudeCLIBackend()
    assert b.translate("hello") == "翻譯結果\n"


# --- gemini.GeminiBackend -----------------------------------------------
#
# __init__ 從不在測試中真正跑：要嘛用 monkeypatch 蓋掉 google.genai.Client
# 的建構子，要嘛用 object.__new__ 繞過 __init__ 直接組出一個帶假
# _client 的實例。兩者都不連網、不需要 GEMINI_API_KEY。


def test_gemini_import_is_deferred_into_init(monkeypatch):
    """manifest.py 的行為守衛同款手法：把 google 打掉，import 這個模組本身
    仍必須成功，因為 `from google import genai` 是 __init__ 內部的事。"""
    monkeypatch.setitem(sys.modules, "google", None)
    monkeypatch.delitem(sys.modules, "scripts.zh_tw.backends.gemini", raising=False)
    import scripts.zh_tw.backends.gemini  # noqa: F401


def test_gemini_backend_raises_when_api_key_unset(monkeypatch):
    from scripts.zh_tw.backends import gemini

    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        gemini.GeminiBackend()


def test_gemini_backend_raises_when_all_models_fail(monkeypatch):
    from scripts.zh_tw.backends import gemini

    monkeypatch.setattr(gemini.time, "sleep", lambda *_: None)

    class _FailingModels:
        def generate_content(self, model, contents):
            raise RuntimeError("503 unavailable")

    class _StubClient:
        models = _FailingModels()

    b = object.__new__(gemini.GeminiBackend)
    b._client = _StubClient()

    with pytest.raises(RuntimeError, match="所有模型皆失敗"):
        b.translate("hello")


def test_gemini_backend_raises_on_blank_response(monkeypatch):
    from scripts.zh_tw.backends import gemini

    monkeypatch.setattr(gemini.time, "sleep", lambda *_: None)

    class _Resp:
        text = "   "

    class _BlankModels:
        def generate_content(self, model, contents):
            return _Resp()

    class _StubClient:
        models = _BlankModels()

    b = object.__new__(gemini.GeminiBackend)
    b._client = _StubClient()

    with pytest.raises(RuntimeError, match="所有模型皆失敗"):
        b.translate("hello")


def test_gemini_backend_raises_on_empty_response(monkeypatch):
    from scripts.zh_tw.backends import gemini

    monkeypatch.setattr(gemini.time, "sleep", lambda *_: None)

    class _Resp:
        text = ""

    class _EmptyModels:
        def generate_content(self, model, contents):
            return _Resp()

    class _StubClient:
        models = _EmptyModels()

    b = object.__new__(gemini.GeminiBackend)
    b._client = _StubClient()

    with pytest.raises(RuntimeError, match="所有模型皆失敗"):
        b.translate("hello")


def test_gemini_backend_error_names_last_underlying_exception(monkeypatch):
    from scripts.zh_tw.backends import gemini

    monkeypatch.setattr(gemini.time, "sleep", lambda *_: None)

    calls = {"n": 0}

    class _FailingModels:
        def generate_content(self, model, contents):
            calls["n"] += 1
            raise RuntimeError(f"failure #{calls['n']}")

    class _StubClient:
        models = _FailingModels()

    b = object.__new__(gemini.GeminiBackend)
    b._client = _StubClient()

    with pytest.raises(RuntimeError) as exc_info:
        b.translate("hello")
    assert f"failure #{calls['n']}" in str(exc_info.value)


def test_gemini_backend_does_not_sleep_after_final_failed_attempt(monkeypatch):
    from scripts.zh_tw.backends import gemini

    sleep_calls = []
    monkeypatch.setattr(gemini.time, "sleep", lambda s: sleep_calls.append(s))

    total_attempts = len(gemini.MODELS) * gemini.MAX_RETRIES

    class _FailingModels:
        def generate_content(self, model, contents):
            raise RuntimeError("boom")

    class _StubClient:
        models = _FailingModels()

    b = object.__new__(gemini.GeminiBackend)
    b._client = _StubClient()

    with pytest.raises(RuntimeError):
        b.translate("hello")

    # 每次失敗都 sleep，除了最後一次嘗試——所以 sleep 次數必須比嘗試次數少一次。
    assert len(sleep_calls) == total_attempts - 1


def test_gemini_backend_returns_text_on_success(monkeypatch):
    from scripts.zh_tw.backends import gemini

    class _Resp:
        text = "翻譯結果"

    class _OkModels:
        def generate_content(self, model, contents):
            return _Resp()

    class _StubClient:
        models = _OkModels()

    b = object.__new__(gemini.GeminiBackend)
    b._client = _StubClient()

    assert b.translate("hello") == "翻譯結果"
