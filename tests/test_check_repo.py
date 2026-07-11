from scripts.zh_tw import check_repo, frontmatter, glossary, validate


def test_collect_finds_book_and_reference():
    files = check_repo.collect()
    assert "book/404.md" in files
    assert any(p.startswith("reference/") for p in files)
    assert len(files) >= 142  # PR 3 刪了孤兒 transfer-restrictions.md（147→146 檔上下）


def test_main_over_real_corpus_is_not_yet_clean():
    """Pre-backfill state: 126 glossary violations + 5 simplified glyphs,
    as pinned in tests/test_baseline.py. main() must return 1."""
    files = check_repo.collect()

    # 過渡 404 清單（每個 backfill PR 更新，收尾必須為空）：
    # - PR 3 新譯文忠實翻出英文新增的跨檔連結，目標檔尚未翻新（英文端
    #   目標已逐一驗證存在）。PR 4 解掉 vector/struct 兩條。
    # - dynamic-fields→#struct 是 plan 預告的 anchor 退役 404（上游刪節，
    #   PR 4 重譯 struct.md 時 {#struct} 退場）；PR 5 重譯 dynamic-fields
    #   後消失。
    link_errs = validate.check_links(files)
    transitional = {
        "book/storage/storage-functions.md: anchor 無法解析 ./store-ability#relation-to-key",
        "book/storage/storage-functions.md: anchor 無法解析 ./../object/ownership#party-objects",
        "book/object/fast-path-and-consensus.md: anchor 無法解析 ./ownership#immutable-frozen-state",
        "book/object/fast-path-and-consensus.md: anchor 無法解析 ./ownership#party-objects",
        # PR 5 起：balance-and-coin 忠實翻出上游連結，目標 concepts（PR 7）
        "book/programmability/balance-and-coin.md: anchor 無法解析 ./../concepts/what-is-a-transaction#commands",
        # 舊 zh testing 檔連到 zh 自創的 {#clock}（上游從未有；epoch-and-time
        # 已改用上游的 auto-slug #time）；PR 6 重譯 using-system-objects 自癒
        "book/testing/using-system-objects.md: anchor 無法解析 ./../programmability/epoch-and-time.md#clock",
        "reference/variables.md: anchor 無法解析 ./functions#return-expression",
    }
    assert set(link_errs) == transitional

    glossary_total = 0
    for text in files.values():
        _, body = frontmatter.split(text)
        glossary_total += sum(glossary.scan(body).values())

    simplified_total = 0
    for text in files.values():
        _, body = frontmatter.split(text)
        simplified_total += len(validate.simplified_chars(body))

    assert glossary_total == 108, glossary_total  # PR 5 再清 4 處（112→108）
    assert simplified_total == 4, simplified_total  # PR 5 清掉 1 字

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
