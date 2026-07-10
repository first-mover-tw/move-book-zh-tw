from scripts.zh_tw import chunking


def test_join_chunk_round_trip_is_identity():
    body = "# T\n\nintro\n\n## A\n\naaa\n\n## B\n\nbbb\n"
    assert chunking.join(chunking.chunk(body, max_lines=2)) == body


def test_short_body_is_single_chunk():
    body = "# T\n\nshort\n"
    assert chunking.chunk(body, max_lines=250) == [body]


def test_splits_on_h2_boundaries():
    body = "# T\n\nintro\n\n## A\n\naaa\n\n## B\n\nbbb\n"
    chunks = chunking.chunk(body, max_lines=2)
    assert len(chunks) == 3
    assert chunks[1].startswith("## A")
    assert chunks[2].startswith("## B")


def test_does_not_split_inside_code_fence():
    body = "# T\n\n```move\n## not a heading\n```\n\n## Real\n\nx\n"
    chunks = chunking.chunk(body, max_lines=1)
    assert any("## not a heading" in c for c in chunks)
    assert sum(c.startswith("## Real") for c in chunks) == 1


def test_round_trip_on_body_with_trailing_newline():
    body = "## A\n\nx\n"
    assert chunking.join(chunking.chunk(body, max_lines=1)) == body
