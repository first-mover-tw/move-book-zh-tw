import subprocess

import pytest

from scripts.zh_tw.backends import base, fake


def test_fake_backend_is_deterministic():
    b = fake.FakeBackend()
    assert b.translate("hello") == b.translate("hello")


def test_fake_backend_preserves_structure():
    """fake 後端把英文標題換成假中文，但保留標題數與 fence 數，讓 pipeline 測試可用。"""
    b = fake.FakeBackend()
    out = b.translate("# Title\n\n```move\nx\n```\n\n## Sub\n")
    assert out.count("#") >= 3
    assert out.count("```") == 2


def test_get_resolves_fake():
    assert isinstance(base.get("fake"), fake.FakeBackend)


def test_get_rejects_unknown_backend():
    with pytest.raises(ValueError, match="unknown backend"):
        base.get("nope")


def test_system_prompt_embeds_glossary_rules():
    from scripts.zh_tw import glossary
    assert "函式" in base.SYSTEM_PROMPT
    assert "迴圈" in base.SYSTEM_PROMPT


# --- claude_cli.ClaudeCLIBackend ---------------------------------------
#
# subprocess.run 一律被 monkeypatch 掉：測試只斷言「會呼叫什麼」與
# 「回傳/例外怎麼處理」，絕不真的 shell 出去執行 `claude`（我們本來就
# 跑在 Claude 底下，遞迴呼叫沒有意義而且可能真的打 API）。


def test_claude_cli_backend_constructs_expected_argv(monkeypatch):
    from scripts.zh_tw.backends import claude_cli

    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(argv, 0, stdout="翻譯結果", stderr="")

    monkeypatch.setenv("ZH_TW_CLAUDE_MODEL", "sonnet")
    monkeypatch.setenv("ZH_TW_TIMEOUT", "42")
    monkeypatch.setattr(claude_cli.subprocess, "run", fake_run)
    b = claude_cli.ClaudeCLIBackend()
    out = b.translate("hello")

    argv = captured["argv"]
    assert argv[0] == "claude"
    assert argv[1] == "-p"
    assert argv[2] == "--model"
    assert argv[3] == "sonnet"
    assert "hello" in argv[4]
    assert claude_cli.SYSTEM_PROMPT in argv[4]
    assert captured["kwargs"]["timeout"] == 42
    assert out == "翻譯結果\n"


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
        return subprocess.CompletedProcess(argv, 0, stdout="   \n", stderr="")

    monkeypatch.setattr(claude_cli.subprocess, "run", fake_run)
    b = claude_cli.ClaudeCLIBackend()
    with pytest.raises(RuntimeError, match="空字串"):
        b.translate("hello")


# --- gemini.GeminiBackend -----------------------------------------------
#
# __init__ 從不在測試中真正跑：要嘛用 monkeypatch 蓋掉 google.genai.Client
# 的建構子，要嘛用 object.__new__ 繞過 __init__ 直接組出一個帶假
# _client 的實例。兩者都不連網、不需要 GEMINI_API_KEY。


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
