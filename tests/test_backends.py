import subprocess
import sys
from pathlib import Path

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
    assert argv[3] == "sonnet"  # Task 17 A/B 選定的預設 model
    assert "hello" in argv[4]
    assert claude_cli.SYSTEM_PROMPT in argv[4]
    assert captured["kwargs"]["timeout"] == 600
    assert out == "翻譯結果\n"


def test_claude_cli_backend_reads_model_env_after_import(monkeypatch):
    """MODEL 不能是 module-level 常數：import 之後改環境變數必須立即生效
    (Defect 2)。"""
    from scripts.zh_tw.backends import claude_cli

    # 覆蓋值必須異於預設值（sonnet），否則本測試驗不出 env 有生效。
    monkeypatch.setenv("ZH_TW_CLAUDE_MODEL", "opus")

    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        return subprocess.CompletedProcess(argv, 0, stdout="ok", stderr="")

    monkeypatch.setattr(claude_cli.subprocess, "run", fake_run)
    claude_cli.ClaudeCLIBackend().translate("hello")

    assert captured["argv"][3] == "opus"


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


# --- kind="text" 專用 prompt（短字串：frontmatter title/description） ----
#
# 實測（2026-07-11，47 檔 A 層 dry-run）：markdown prompt 對單詞技術名詞
# title（'Friends | Reference'、'Address | Reference'）會保守不翻，
# gate 4 攔下後 retry 也翻不動 —— 需要明確指示「短字串也必須翻」。


def test_claude_cli_backend_uses_text_prompt_for_kind_text(monkeypatch):
    from scripts.zh_tw.backends import base, claude_cli

    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        return subprocess.CompletedProcess(argv, 0, stdout="友元 (Friends) | 參考手冊", stderr="")

    monkeypatch.setattr(claude_cli.subprocess, "run", fake_run)
    claude_cli.ClaudeCLIBackend().translate("Friends | Reference", kind="text")

    prompt = captured["argv"][4]
    assert base.TEXT_PROMPT in prompt
    assert base.SYSTEM_PROMPT not in prompt


def test_claude_cli_backend_uses_markdown_prompt_by_default(monkeypatch):
    from scripts.zh_tw.backends import base, claude_cli

    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        return subprocess.CompletedProcess(argv, 0, stdout="翻譯", stderr="")

    monkeypatch.setattr(claude_cli.subprocess, "run", fake_run)
    claude_cli.ClaudeCLIBackend().translate("# Heading\n\nbody\n")

    assert base.SYSTEM_PROMPT in captured["argv"][4]


def test_gemini_backend_uses_text_prompt_for_kind_text(monkeypatch):
    from scripts.zh_tw.backends import base, gemini

    captured = {}

    class _Resp:
        text = "友元 (Friends) | 參考手冊"

    class _Models:
        def generate_content(self, model, contents):
            captured["contents"] = contents
            return _Resp()

    class _StubClient:
        models = _Models()

    b = object.__new__(gemini.GeminiBackend)
    b._client = _StubClient()
    b.translate("Friends | Reference", kind="text")

    assert base.TEXT_PROMPT in captured["contents"]
    assert base.SYSTEM_PROMPT not in captured["contents"]


# --- kind="sidebar"：payload 自帶 SIDEBAR_PROMPT，backend 不得再外包 ----
#
# dual-review finding：sidebar payload 若走 kind="text" 會被 TEXT_PROMPT
# 外包，兩層指令矛盾（TEXT_PROMPT「單一名詞必翻」vs SIDEBAR_PROMPT
# 「BCS 等專有名詞維持原文」），且這種語意流出 _validate_new_label_format
# 擋不住。


def test_claude_cli_backend_no_wrap_for_kind_sidebar(monkeypatch):
    from scripts.zh_tw.backends import base, claude_cli

    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        return subprocess.CompletedProcess(argv, 0, stdout="1. 中文 (Label)", stderr="")

    monkeypatch.setattr(claude_cli.subprocess, "run", fake_run)
    payload = "自帶完整指令的 payload\n\n1. Label"
    claude_cli.ClaudeCLIBackend().translate(payload, kind="sidebar")

    assert captured["argv"][4] == payload
    assert base.TEXT_PROMPT not in captured["argv"][4]
    assert base.SYSTEM_PROMPT not in captured["argv"][4]


def test_gemini_backend_no_wrap_for_kind_sidebar(monkeypatch):
    from scripts.zh_tw.backends import base, gemini

    captured = {}

    class _Resp:
        text = "1. 中文 (Label)"

    class _Models:
        def generate_content(self, model, contents):
            captured["contents"] = contents
            return _Resp()

    class _StubClient:
        models = _Models()

    b = object.__new__(gemini.GeminiBackend)
    b._client = _StubClient()
    payload = "自帶完整指令的 payload\n\n1. Label"
    b.translate(payload, kind="sidebar")

    assert captured["contents"] == payload


def test_fake_backend_numbered_branch_dispatches_on_kind_sidebar():
    from scripts.zh_tw.backends.fake import FakeBackend

    out = FakeBackend().translate("說明\n\n1. Label One\n2. Label Two", kind="sidebar")
    assert out.splitlines() == [
        f"1. {FakeBackend()._substitute('Label One')} (Label One)",
        f"2. {FakeBackend()._substitute('Label Two')} (Label Two)",
    ]


def test_claude_cli_backend_runs_outside_project_cwd(monkeypatch):
    """claude CLI 會載入 cwd 的專案 context（CLAUDE.md、SessionStart hook
    注入的 tasks/progress.md）—— 在本專案目錄執行時，模型看得到「翻譯管線
    工程」的上下文，間歇性放棄翻譯、改成扮演工程師回答（實測 'Abort' 回
    「Bug 找到了…根因：HEADING_PRO…」）。翻譯呼叫必須在中性目錄執行。"""
    import os

    from scripts.zh_tw.backends import claude_cli

    captured = {}

    def fake_run(argv, **kwargs):
        cwd = kwargs.get("cwd")
        captured["cwd_ok"] = (
            cwd is not None
            and os.path.isdir(cwd)  # 呼叫當下必須存在（結束後會被清掉）
            and not os.path.exists(os.path.join(cwd, "CLAUDE.md"))
            and not os.path.exists(os.path.join(cwd, "tasks"))
        )
        captured["stdin"] = kwargs.get("stdin")
        return subprocess.CompletedProcess(argv, 0, stdout="翻譯", stderr="")

    monkeypatch.setattr(claude_cli.subprocess, "run", fake_run)
    claude_cli.ClaudeCLIBackend().translate("hello")

    assert captured["cwd_ok"]
    # stdin 必須斷開：claude -p 會把非 tty 的殘留 stdin 整段讀進當輸入
    assert captured["stdin"] == subprocess.DEVNULL


def test_gemini_backend_skips_to_next_model_on_daily_quota(monkeypatch):
    """日配額 429 不該對同一 model 重試 3 次（等 60 秒不會恢復），
    要立刻換下一個 model —— 這正是 CI 連續紅燈時燒掉的時間。"""
    from scripts.zh_tw.backends import gemini as gemini_mod

    monkeypatch.setattr(
        gemini_mod.time, "sleep", lambda *_: pytest.fail("日配額耗盡不該 sleep")
    )
    calls = []

    class _Resp:
        text = "結構"

    class _Models:
        def generate_content(self, model, contents):
            calls.append(model)
            if model == gemini_mod.MODELS[0]:
                raise RuntimeError(
                    "429 RESOURCE_EXHAUSTED quotaId: GenerateRequestsPerDayPerProjectPerModel-FreeTier"
                )
            return _Resp()

    class _StubClient:
        models = _Models()

    b = object.__new__(gemini_mod.GeminiBackend)
    b._client = _StubClient()
    assert b.translate("hello") == "結構"
    assert calls == [gemini_mod.MODELS[0], gemini_mod.MODELS[1]]


def test_gemini_model_gone_404_skips_to_next_model_without_retry(monkeypatch):
    """model 下架回 404（2026-08-29 gemini-2.5-flash-lite 實例）：重試三次無意義，
    要立刻換下一個 model，而且不能 sleep。"""
    from scripts.zh_tw.backends import gemini as gemini_mod

    monkeypatch.setattr(
        gemini_mod.time, "sleep", lambda *_: pytest.fail("404 不該 sleep")
    )
    calls = []

    class _Resp:
        text = "結構"

    class _Models:
        def generate_content(self, model, contents):
            calls.append(model)
            if model == gemini_mod.MODELS[0]:
                raise RuntimeError(
                    "404 NOT_FOUND. This model models/x is no longer available to new users."
                )
            return _Resp()

    class _StubClient:
        models = _Models()

    b = object.__new__(gemini_mod.GeminiBackend)
    b._client = _StubClient()
    assert b.translate("hello") == "結構"
    assert calls == [gemini_mod.MODELS[0], gemini_mod.MODELS[1]]


def test_gemini_models_do_not_include_retired_flash_lite():
    from scripts.zh_tw.backends import gemini as gemini_mod

    assert "gemini-2.5-flash-lite" not in gemini_mod.MODELS


# --- codex CLI backend（2026-09-04 本機批量排乾用） -------------------------


def _fake_codex_run(captured, *, rc=0, answer="翻譯結果", write_file=True, stderr=""):
    """模擬 codex exec：答案寫進 --output-last-message 指定的檔案，
    stdout 只有雜訊（真實 codex 會印 session id / tokens used 之類）。"""

    def run(argv, **kwargs):
        captured["argv"] = argv
        captured["kwargs"] = kwargs
        if write_file:
            with open(argv[argv.index("-o") + 1], "w", encoding="utf-8") as fh:
                fh.write(answer)
        return subprocess.CompletedProcess(
            argv, rc, stdout="model: x\nsession id: y\ntokens used\n11602\n", stderr=stderr
        )

    return run


def test_codex_backend_constructs_expected_argv(monkeypatch):
    from scripts.zh_tw.backends import codex_cli

    monkeypatch.delenv("ZH_TW_CODEX_MODEL", raising=False)
    monkeypatch.delenv("ZH_TW_TIMEOUT", raising=False)
    captured = {}
    monkeypatch.setattr(codex_cli.subprocess, "run", _fake_codex_run(captured))

    out = codex_cli.CodexCLIBackend().translate("hello")
    argv = captured["argv"]

    assert argv[0] == "codex"
    assert argv[1] == "exec"
    # 每一個旗標都對應 docstring 裡一條實測過的理由，少一個就是一個回歸
    for flag in ("--ephemeral", "--ignore-user-config", "--skip-git-repo-check"):
        assert flag in argv, flag
    assert argv[argv.index("-s") + 1] == "read-only"
    assert argv[argv.index("--color") + 1] == "never"
    assert "-o" in argv
    # prompt 是最後一個位置引數，且必須外包 SYSTEM_PROMPT
    assert argv[-1].endswith("hello")
    assert codex_cli.SYSTEM_PROMPT in argv[-1]
    assert captured["kwargs"]["timeout"] == 600
    assert out == "翻譯結果\n"


def test_codex_backend_answer_comes_from_file_not_stdout(monkeypatch):
    """codex exec 的 stdout 混著 session id 與 token 統計，答案只能從
    --output-last-message 取。用 stdout 剝殼是 L2 的典型犯案（拿「輸出長
    什麼樣」代理「哪一段是答案」）。"""
    from scripts.zh_tw.backends import codex_cli

    captured = {}
    monkeypatch.setattr(
        codex_cli.subprocess, "run", _fake_codex_run(captured, answer="真正的譯文")
    )
    assert codex_cli.CodexCLIBackend().translate("hello") == "真正的譯文\n"


def test_codex_backend_taiwanese_glossary_rules_reach_the_prompt(monkeypatch):
    """台灣用語不是靠 codex 自己知道，是靠 prompt 帶 glossary 規則進去。
    `--ignore-user-config` 讓 prompt 成為唯一指令來源，這條就必須成立。"""
    from scripts.zh_tw import glossary
    from scripts.zh_tw.backends import codex_cli

    captured = {}
    monkeypatch.setattr(codex_cli.subprocess, "run", _fake_codex_run(captured))
    codex_cli.CodexCLIBackend().translate("hello")

    prompt = captured["argv"][-1]
    assert "台灣繁體中文" in prompt
    assert glossary.prompt_rules() in prompt


def test_codex_backend_uses_text_prompt_for_kind_text(monkeypatch):
    from scripts.zh_tw.backends import codex_cli

    captured = {}
    monkeypatch.setattr(codex_cli.subprocess, "run", _fake_codex_run(captured))
    codex_cli.CodexCLIBackend().translate("Vectors", kind="text")
    assert codex_cli.TEXT_PROMPT in captured["argv"][-1]
    assert codex_cli.SYSTEM_PROMPT not in captured["argv"][-1]


def test_codex_backend_uses_heading_prompt_for_kind_heading(monkeypatch):
    from scripts.zh_tw.backends import codex_cli

    captured = {}
    monkeypatch.setattr(codex_cli.subprocess, "run", _fake_codex_run(captured))
    codex_cli.CodexCLIBackend().translate("Running Tests", kind="heading")
    assert codex_cli.HEADING_PROMPT in captured["argv"][-1]


def test_codex_backend_no_wrap_for_kind_sidebar_and_raw(monkeypatch):
    """kind='sidebar'/'raw' 的 payload 自帶完整指令，再外包任何 prompt 都會
    產生互相矛盾的兩層指令（見 base.Backend 的契約）。"""
    from scripts.zh_tw.backends import codex_cli

    for kind in ("sidebar", "raw"):
        captured = {}
        monkeypatch.setattr(codex_cli.subprocess, "run", _fake_codex_run(captured))
        codex_cli.CodexCLIBackend().translate("PAYLOAD", kind=kind)
        assert captured["argv"][-1] == "PAYLOAD", kind


def test_codex_backend_runs_outside_project_cwd_with_stdin_detached(monkeypatch):
    """L8：中性 cwd（codex 會讀 cwd 的 AGENTS.md）+ stdin 斷開（codex exec 會
    把導入的 stdin 當成附加的 <stdin> 區塊餵進 prompt）。

    這條**只做靜態檢查**（讀 kwargs 與 argv），不去變異 cwd 的來源 ——
    那個變數會流進清理路徑，變異它會真的刪東西（lessons L17）。
    """
    import os

    from scripts.zh_tw.backends import codex_cli

    captured = {}
    inner = {}

    def run(argv, **kwargs):
        cwd = kwargs.get("cwd")
        inner["cwd_ok"] = (
            cwd is not None
            and os.path.isdir(cwd)
            and not os.path.exists(os.path.join(cwd, "CLAUDE.md"))
            and not os.path.exists(os.path.join(cwd, "tasks"))
            and not os.path.exists(os.path.join(cwd, "AGENTS.md"))
        )
        inner["cd_flag_matches_cwd"] = argv[argv.index("--cd") + 1] == cwd
        return _fake_codex_run(captured)(argv, **kwargs)

    monkeypatch.setattr(codex_cli.subprocess, "run", run)
    codex_cli.CodexCLIBackend().translate("hello")

    assert inner["cwd_ok"]
    assert inner["cd_flag_matches_cwd"]
    assert captured["kwargs"]["stdin"] == subprocess.DEVNULL


def test_codex_backend_tempdir_is_scoped_not_manually_removed():
    """清理必須是 `with tempfile.TemporaryDirectory()`，不可以是
    `mkdtemp()` + `finally: shutil.rmtree(<變數>)`。

    2026-09-04 事故：後者做 mutation test 時把 mkdtemp 變異成 os.getcwd()，
    pytest 一跑就 rmtree 掉整個專案目錄。context manager 的作用域由 with
    決定，結構上不可能刪到別的地方（lessons L17）。這條是結構守衛，用讀
    原始碼的方式檢查 —— 因為「跑一次看它紅不紅」正是當初出事的做法。
    """
    import ast

    src = Path(__file__).resolve().parent.parent / "scripts/zh_tw/backends/codex_cli.py"
    tree = ast.parse(src.read_text(encoding="utf-8"))

    # 判準用 AST 的呼叫節點，不用字串比對 —— docstring 裡就寫著 `mkdtemp` 與
    # `rmtree`（事故敘述），文字比對會被自己的註解誤中（L2：別拿廉價可觀測量
    # 代理真實性質）。
    called = {
        ast.unparse(n.func)
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, (ast.Name, ast.Attribute))
    }
    assert "tempfile.TemporaryDirectory" in called, called
    assert not {c for c in called if c.endswith(("mkdtemp", "rmtree", "rmdir"))}, called

    # 而且它必須是 `with` 的 context manager，不是被指派給變數後手動清理
    withs = [
        ast.unparse(item.context_expr.func)
        for n in ast.walk(tree)
        if isinstance(n, ast.With)
        for item in n.items
        if isinstance(item.context_expr, ast.Call)
    ]
    assert "tempfile.TemporaryDirectory" in withs, withs


def test_codex_backend_cleans_up_its_tempdir(monkeypatch):
    from scripts.zh_tw.backends import codex_cli

    captured = {}
    monkeypatch.setattr(codex_cli.subprocess, "run", _fake_codex_run(captured))
    codex_cli.CodexCLIBackend().translate("hello")
    assert not Path(captured["kwargs"]["cwd"]).exists()


def test_codex_backend_cleans_up_tempdir_even_on_failure(monkeypatch):
    from scripts.zh_tw.backends import codex_cli

    captured = {}
    monkeypatch.setattr(codex_cli.subprocess, "run", _fake_codex_run(captured, rc=1))
    with pytest.raises(RuntimeError):
        codex_cli.CodexCLIBackend().translate("hello")
    assert not Path(captured["kwargs"]["cwd"]).exists()


def test_codex_backend_raises_on_nonzero_exit(monkeypatch):
    from scripts.zh_tw.backends import codex_cli

    captured = {}
    monkeypatch.setattr(
        codex_cli.subprocess, "run", _fake_codex_run(captured, rc=1, stderr="quota exhausted")
    )
    with pytest.raises(RuntimeError, match="quota exhausted"):
        codex_cli.CodexCLIBackend().translate("hello")


def test_codex_backend_raises_when_output_file_missing(monkeypatch):
    """rc=0 但沒寫出檔案：必須炸，不可以退回去讀 stdout —— 那會把
    `tokens used\\n11602` 之類的雜訊當成譯文寫進語料。"""
    from scripts.zh_tw.backends import codex_cli

    captured = {}
    monkeypatch.setattr(
        codex_cli.subprocess, "run", _fake_codex_run(captured, write_file=False)
    )
    with pytest.raises(RuntimeError, match="output-last-message"):
        codex_cli.CodexCLIBackend().translate("hello")


def test_codex_backend_raises_on_whitespace_only_answer(monkeypatch):
    from scripts.zh_tw.backends import codex_cli

    captured = {}
    monkeypatch.setattr(
        codex_cli.subprocess, "run", _fake_codex_run(captured, answer="   \n\n  ")
    )
    with pytest.raises(RuntimeError, match="空字串"):
        codex_cli.CodexCLIBackend().translate("hello")


def test_codex_backend_omits_model_flag_unless_env_set(monkeypatch):
    """不寫死 model 名：釘一個名字就會重演 gemini MODELS 清單的下架 404
    問題。不給 -m 用 codex 當下的預設，要固定版本才用環境變數。"""
    from scripts.zh_tw.backends import codex_cli

    monkeypatch.delenv("ZH_TW_CODEX_MODEL", raising=False)
    captured = {}
    monkeypatch.setattr(codex_cli.subprocess, "run", _fake_codex_run(captured))
    codex_cli.CodexCLIBackend().translate("hello")
    assert "-m" not in captured["argv"]

    monkeypatch.setenv("ZH_TW_CODEX_MODEL", "gpt-5.5")
    captured2 = {}
    monkeypatch.setattr(codex_cli.subprocess, "run", _fake_codex_run(captured2))
    codex_cli.CodexCLIBackend().translate("hello")
    assert captured2["argv"][captured2["argv"].index("-m") + 1] == "gpt-5.5"


def test_codex_backend_honours_timeout_env(monkeypatch):
    from scripts.zh_tw.backends import codex_cli

    monkeypatch.setenv("ZH_TW_TIMEOUT", "42")
    captured = {}
    monkeypatch.setattr(codex_cli.subprocess, "run", _fake_codex_run(captured))
    codex_cli.CodexCLIBackend().translate("hello")
    assert captured["kwargs"]["timeout"] == 42


def test_get_resolves_codex():
    from scripts.zh_tw.backends import codex_cli

    assert isinstance(base.get("codex"), codex_cli.CodexCLIBackend)


def test_cli_accepts_codex_backend_choice():
    """`--backend codex` 必須是合法選項，否則本機排乾根本叫不起來。"""
    r = subprocess.run(
        [sys.executable, "-m", "scripts.zh_tw", "--backend", "codex", "--detect"],
        capture_output=True, text=True,
    )
    assert "invalid choice" not in r.stderr, r.stderr
