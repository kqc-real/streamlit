"""Example: transform sample JSON to TSV using the minimal pipeline from README.
Run: python3.12 examples/transform_to_anki.py
"""
import json
import re
import io
import csv
from markdown_it import MarkdownIt
from examples.math_utils import render_markdown_with_math


def transform_to_anki_tsv(json_bytes: bytes) -> str:
    json_data = json.loads(json_bytes.decode('utf-8'))
    md = MarkdownIt()
    output = io.StringIO()
    writer = csv.writer(output, delimiter='\t', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')

    for q in json_data.get('questions', []):

        frage_html = render_markdown_with_math(md, q.get('question', ''))
        frage = frage_html.strip()
        if frage.startswith('<p>') and frage.endswith('</p>'):
            frage = frage[3:-4]

        optionen = q.get('options', []) or []
        options_html = (
            '<ol type="A">'
            + ''.join(f'<li>{render_markdown_with_math(md, opt).strip()}</li>' for opt in optionen)
            + '</ol>'
        )
        try:
            loesung_idx = int(q.get('answer', 0))
        except Exception:
            loesung_idx = 0
        correct = render_markdown_with_math(md, optionen[loesung_idx]) if optionen and 0 <= loesung_idx < len(optionen) else ''
        erklaerung = render_markdown_with_math(md, q.get('explanation', ''))
        extended = render_markdown_with_math(md, str(q.get('extended_explanation', '')))

        meta = json_data.get('meta', {})
        tags = ' '.join(str(x).replace(' ', '_') for x in [meta.get('title', ''), q.get('topic', '')]).strip()

        weight_val = q.get('weight', '')

        row = [
            frage,
            options_html,
            correct,
            erklaerung,
            extended,
            '',
            meta.get('title', ''),
            q.get('topic', ''),
            str(weight_val),
            tags,
        ]
        writer.writerow(row)

    return output.getvalue()


if __name__ == '__main__':
    import pathlib
    in_path = pathlib.Path(__file__).parent / 'sample_questions.json'
    out_path = pathlib.Path(__file__).parent / 'sample_output.tsv'
    json_bytes = in_path.read_bytes()
    tsv = transform_to_anki_tsv(json_bytes)
    out_path.write_text(tsv, encoding='utf-8')
    print('Wrote', out_path)
