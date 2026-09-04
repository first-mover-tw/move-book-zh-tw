from scripts.zh_tw import check_repo, frontmatter, glossary, validate


def test_collect_finds_book_and_reference():
    files = check_repo.collect()
    assert "book/404.md" in files
    assert any(p.startswith("reference/") for p in files)
    assert len(files) >= 142  # PR 3 刪了孤兒 transfer-restrictions.md（147→146 檔上下）


def test_main_over_real_corpus_is_clean():
    """2026-07-12 債務全清（LEGACY_BODY_DEBT 豁免機制已移除）：全語料
    違禁詞 0、簡體 0、連結問題 0，main() → exit 0 —— 這是 translate
    workflow validate 步驟能綠的前提。"""
    files = check_repo.collect()

    # 過渡 404 已於 PR 7（backfill 最終批）全數清空 —— 恢復嚴格斷言。
    # 歷程：PR 3 引入 11 條 → PR 4-7 逐批解掉 + 2 個 legacy anchor 更名
    # （{#clock}→{#time}、{#immutable-frozen-object}→{#immutable-frozen-state}）
    # + reference/functions.md 補顯式 {#return-expression}。
    link_errs = validate.check_links(files)
    assert link_errs == []

    glossary_total = 0
    for text in files.values():
        _, body = frontmatter.split(text)
        glossary_total += sum(glossary.scan(body).values())

    simplified_total = 0
    for text in files.values():
        _, body = frontmatter.split(text)
        simplified_total += len(validate.simplified_chars(body))

    assert glossary_total == 0, glossary_total  # 2026-07-12 債務全清（126→76→0）
    assert simplified_total == 0, simplified_total

    assert check_repo.main() == 0


def test_clean_file_set_passes_the_underlying_checks():
    """Construct an in-memory clean corpus (no violations, no simplified
    glyphs, all links resolving) and confirm the same logic main() uses
    would return 0 for it. Does not touch the real corpus or collect()."""
    files = {
        "book/a.md": "---\ntitle: 標題\n---\n\n# 標題 {#biao-ti}\n\n看看 [連結](./a.md#biao-ti)。\n",
        "book/b.md": "---\ntitle: 另一個標題\n---\n\n乾淨的中文內容，沒有違禁詞，也沒有簡體字。\n",
    }

    link_errs = validate.check_links(files)
    assert link_errs == []

    glossary_total = 0
    for text in files.values():
        _, body = frontmatter.split(text)
        glossary_total += sum(glossary.scan(body).values())
    assert glossary_total == 0

    simplified_total = 0
    for text in files.values():
        _, body = frontmatter.split(text)
        simplified_total += len(validate.simplified_chars(body))
    assert simplified_total == 0

    errs = link_errs
    assert (1 if (errs or glossary_total or simplified_total) else 0) == 0


def test_main_catches_forbidden_word_in_frontmatter_value(monkeypatch, capsys):
    """check_repo 是「語料乾淨」的批次守門員：實測 5 個現有檔的違禁詞
    藏在 description/title 值裡，body-only 掃描會對它們回 0（假乾淨）。"""
    files = {
        "book/a.md": '---\ntitle: "循環"\ndescription: "乾淨。"\n---\n\n# 標題 {#t}\n\n乾淨內文。\n'
    }
    monkeypatch.setattr(check_repo, "collect", lambda: files)
    assert check_repo.main() == 1
    assert "循環" in capsys.readouterr().err


def test_main_catches_simplified_char_in_frontmatter_value(monkeypatch, capsys):
    files = {
        "book/a.md": '---\ntitle: "这个标题"\n---\n\n# 標題 {#t}\n\n乾淨內文。\n'
    }
    monkeypatch.setattr(check_repo, "collect", lambda: files)
    assert check_repo.main() == 1
    assert "簡體" in capsys.readouterr().err


def test_main_red_on_any_glossary_violation(monkeypatch):
    files = {
        "book/clean.md": "---\ntitle: 乾淨\n---\n\n# 乾淨 {#c}\n\n這裡有循環。\n",
    }
    monkeypatch.setattr(check_repo, "collect", lambda: files)
    assert check_repo.main() == 1


def test_main_reports_ordered_list_numbering(tmp_path, monkeypatch, capsys):
    """gate 11 必須掛進 check_repo，而且要計入 exit code。

    PR #24 的教訓正是「check_repo 0/0/0 卻有缺陷」：只掛 check_file 等於
    只防未來重譯，不防已經落地的語料。拆掉計數（numbering_total 不累加）
    這條就要紅。
    """
    bad = '---\ndescription: "d"\n---\n\n# T {#t}\n\n1. **1. 預設安全性:** 甲\n'
    monkeypatch.setattr(check_repo, "collect", lambda: {"book/x.md": bad})
    rc = check_repo.main()
    err = capsys.readouterr().err
    assert "序號重複" in err
    assert rc == 1
