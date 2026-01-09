from pathlib import Path

from helpers.text import load_markdown_file


def test_load_markdown_file_supports_cp1252(tmp_path: Path):
    # Simulate a Windows-authored markdown file that is not UTF-8.
    content = "Lernziele: ökonomisches Prinzip\n"
    path = tmp_path / "lo.md"
    path.write_bytes(content.encode("cp1252"))

    loaded = load_markdown_file(str(path))
    assert loaded == content

