import pathlib

from examples.transform_to_anki import transform_to_anki_tsv


def test_transform_example_matches_expected():
    base = pathlib.Path(__file__).resolve().parent.parent / 'examples'
    in_path = base / 'sample_questions.json'
    expected_path = base / 'expected_output.tsv'

    json_bytes = in_path.read_bytes()
    actual = transform_to_anki_tsv(json_bytes)
    expected = expected_path.read_text(encoding='utf-8')

    # Normalize whitespace and line endings for comparison
    assert actual.strip() == expected.strip()
