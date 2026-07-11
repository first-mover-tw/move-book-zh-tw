from scripts.zh_tw import check_repo, frontmatter, glossary, validate


def test_collect_finds_book_and_reference():
    files = check_repo.collect()
    assert "book/404.md" in files
    assert any(p.startswith("reference/") for p in files)
    assert len(files) >= 143


def test_main_over_real_corpus_is_not_yet_clean():
    """Pre-backfill state: 126 glossary violations + 5 simplified glyphs,
    as pinned in tests/test_baseline.py. main() must return 1."""
    files = check_repo.collect()

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

    assert glossary_total == 126, glossary_total
    assert simplified_total == 5, simplified_total

    assert check_repo.main() == 1


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
