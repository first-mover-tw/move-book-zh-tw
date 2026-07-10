import pytest

from scripts.zh_tw import anchors


def test_code_lines_covers_fence_body():
    body = "prose\n\n```move\ncode line 1\ncode line 2\n```\n\nmore prose\n"
    lines = body.splitlines()
    assert lines[3] == "code line 1"
    assert lines[4] == "code line 2"
    result = anchors.code_lines(body)
    assert 3 in result
    assert 4 in result
    assert 0 not in result
    assert 7 not in result


def test_code_lines_covers_indented_code_block():
    body = "prose\n\n    indented code\n\nmore prose\n"
    lines = body.splitlines()
    assert lines[2] == "    indented code"
    result = anchors.code_lines(body)
    assert 2 in result
    assert 0 not in result


def test_code_lines_excludes_html_block():
    body = "prose\n\n<!--\n函數\n-->\n\nmore prose\n"
    lines = body.splitlines()
    assert lines[3] == "函數"
    result = anchors.code_lines(body)
    assert 3 not in result


def test_code_lines_raises_on_frontmatter_document():
    doc = "---\ndescription: x\n---\n\nbody\n"
    with pytest.raises(anchors.FrontmatterPassedIn):
        anchors.code_lines(doc)
