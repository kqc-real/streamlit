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
        # Accept legacy German keys if present
        if 'question' not in q and 'frage' in q:
            q['question'] = q.get('frage')
        if 'options' not in q and 'optionen' in q:
            q['options'] = q.get('optionen')
        if 'answer' not in q and 'loesung' in q:
            q['answer'] = q.get('loesung')
        if 'explanation' not in q and 'erklaerung' in q:
            q['explanation'] = q.get('erklaerung')
        if 'weight' not in q and 'gewichtung' in q:
            q['weight'] = q.get('gewichtung')
        if 'topic' not in q and 'thema' in q:
            q['topic'] = q.get('thema')

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
        tags = ' '.join(str(x).replace(' ', '_') for x in [meta.get('title', ''), q.get('topic', '') or q.get('thema', '')]).strip()

        # Use numeric 'gewichtung' if present for backward compatibility
        weight_val = q.get('gewichtung') if 'gewichtung' in q else q.get('weight', '')

        row = [
            frage,
            options_html,
            correct,
            erklaerung,
            extended,
            '',
            meta.get('title', ''),
            q.get('topic', '') or q.get('thema', ''),
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
