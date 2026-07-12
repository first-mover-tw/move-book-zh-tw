from scripts.zh_tw import check_repo, frontmatter, glossary, validate


def test_collect_finds_book_and_reference():
    files = check_repo.collect()
    assert "book/404.md" in files
    assert any(p.startswith("reference/") for p in files)
    assert len(files) >= 142  # PR 3 刪了孤兒 transfer-restrictions.md（147→146 檔上下）


def test_main_over_real_corpus_is_clean_modulo_debt():
    """backfill 完成：全部殘留違規都在 debt.LEGACY_BODY_DEBT 內（原始計數
    76+3 仍在此重算釘住當文件），main() 對債務放行 → exit 0 —— 這是
    translate workflow validate 步驟能綠的前提。"""
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

    assert glossary_total == 76, glossary_total  # backfill 完成（126→76）；殘留全在 reference/ legacy body
    assert simplified_total == 3, simplified_total  # PR 6 再清 1 字

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


def test_main_green_when_violations_confined_to_debt_files(monkeypatch, capsys):
    """自動化前提：check_repo 對「使用者裁決保留的 legacy 債務」必須放行
    （exit 0），否則 translate workflow 的 validate 步驟每次必紅——
    債務範圍外的違規才擋。單一權威清單在 scripts/zh_tw/debt.py。"""
    from scripts.zh_tw import debt

    files = {
        sorted(debt.LEGACY_BODY_DEBT)[0]: "---\ntitle: 標題\n---\n\n# 標題 {#t}\n\n這裡有循環。\n",
        "book/clean.md": "---\ntitle: 乾淨\n---\n\n# 乾淨 {#c}\n\n沒有問題。\n",
    }
    monkeypatch.setattr(check_repo, "collect", lambda: files)
    assert check_repo.main() == 0  # 債務檔的違規：報告但放行
    assert "循環" in capsys.readouterr().err


def test_main_red_when_violation_outside_debt_files(monkeypatch):
    files = {
        "book/clean.md": "---\ntitle: 乾淨\n---\n\n# 乾淨 {#c}\n\n這裡有循環。\n",
    }
    monkeypatch.setattr(check_repo, "collect", lambda: files)
    assert check_repo.main() == 1
