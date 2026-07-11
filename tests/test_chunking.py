import subprocess

from scripts.zh_tw import chunking, frontmatter


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


def test_recurses_into_h3_when_h2_section_is_oversized():
    body = (
        "# T\n\nintro\n\n"
        "## A\n\n### A1\n\n" + "line\n" * 3 +
        "### A2\n\n" + "line\n" * 3 +
        "## B\n\nbbb\n"
    )
    max_lines = 8
    chunks = chunking.chunk(body, max_lines=max_lines)
    assert all(len(c.splitlines()) <= max_lines for c in chunks)
    assert any(c.startswith("### A1") for c in chunks)
    assert any(c.startswith("### A2") for c in chunks)
    assert chunking.join(chunks) == body


def test_recurses_to_h4_through_three_levels():
    max_lines = 6
    body = (
        "# T\n\n"
        "## A\n\n"
        "### B\n\n"
        "#### C1\n\n" + "x\n" * 2 +
        "#### C2\n\n" + "x\n" * 2
    )
    chunks = chunking.chunk(body, max_lines=max_lines)
    assert all(len(c.splitlines()) <= max_lines for c in chunks)
    assert any(c.startswith("#### C1") for c in chunks)
    assert any(c.startswith("#### C2") for c in chunks)
    assert chunking.join(chunks) == body


def test_oversized_section_with_no_deeper_heading_is_emitted_as_is():
    max_lines = 5
    body = "# T\n\n## A\n\n" + "line\n" * 10
    chunks = chunking.chunk(body, max_lines=max_lines)
    assert len(chunks) == 2
    assert chunks[1].startswith("## A")
    assert len(chunks[1].splitlines()) > max_lines
    assert chunking.join(chunks) == body


def test_round_trip_on_recursive_path_for_various_max_lines():
    body = (
        "# T\n\nintro\n\n"
        "## A\n\n### A1\n\n" + "line\n" * 3 +
        "### A2\n\n" + "line\n" * 3 +
        "## B\n\n### B1\n\n#### B1a\n\n" + "y\n" * 4 +
        "bbb\n"
    )
    for n in (1, 2, 10, 250):
        assert chunking.join(chunking.chunk(body, max_lines=n)) == body


def test_heading_inside_fence_or_html_comment_is_not_a_split_boundary():
    body = (
        "# T\n\nintro\n\n"
        "## A\n\n"
        "```move\n## not a heading\n```\n\n"
        "<!--\n### also not a heading\n-->\n\n"
        + "line\n" * 10
        + "\n## B\n\nbbb\n"
    )
    chunks = chunking.chunk(body, max_lines=4)
    assert not any(c.strip().startswith("## not a heading") for c in chunks)
    assert not any(c.strip().startswith("### also not a heading") for c in chunks)
    assert chunking.join(chunks) == body


def test_real_data_variables_md_all_chunks_fit_budget():
    text = subprocess.run(
        ["git", "show", "english-main:reference/variables.md"],
        capture_output=True, text=True, check=True, cwd=".",
    ).stdout
    _, body = frontmatter.split(text)
    chunks = chunking.chunk(body, max_lines=250)
    assert max(len(c.splitlines()) for c in chunks) <= 250
    assert chunking.join(chunks) == body
