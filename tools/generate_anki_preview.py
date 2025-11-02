"""Generiere eine serverseitige HTML-Vorschau aller Fragen (Anki-Card-Style).

Dieses kleine Tool rendert alle Fragen eines Fragensets zu einer einzelnen
HTML-Datei (`artifacts/anki_preview.html`) und versucht, Math serverseitig mit
PyKaTeX zu rendern. Falls PyKaTeX nicht installiert ist, wird KaTeX via CDN
eingebunden und der Browser rendert die Formeln beim Öffnen der Datei.

Benutzung (aus Projektroot):
    python -m tools.generate_anki_preview --questions questions_Data_Analytics.json

Ziel: der Nutzer muss nichts im Streamlit-UI verändern; die Datei zeigt exakt
wie Karten aussehen würden und kann in jedem Browser geöffnet werden.
"""
from __future__ import annotations

import argparse
import json
import os
from typing import List

from markdown_it import MarkdownIt

from examples.math_utils import render_markdown_with_math, pykatex_render  # type: ignore


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _load_questions(path: str) -> List[dict]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Allow wrapping object with meta
    if isinstance(data, dict) and 'questions' in data:
        return data['questions']
    return list(data)


def build_card_html(q: dict, meta_title: str, md: MarkdownIt) -> str:
    q_html = render_markdown_with_math(md, q.get('frage', '') or '')
    # Strip outer paragraph
    if q_html.startswith('<p>') and q_html.endswith('</p>'):
        q_html = q_html[3:-4]

    opts = q.get('optionen') or []
    options_html = ''
    if opts:
        options_html = '<ol type="A">' + ''.join(f"<li>{render_markdown_with_math(md, str(o)).strip()}</li>" for o in opts) + '</ol>'

    # Build back (answer + explanation)
    correct_html = ''
    try:
        lo = int(q.get('loesung', 0))
        correct = opts[lo] if lo < len(opts) else ''
        correct_html = render_markdown_with_math(md, str(correct)).strip()
    except Exception:
        correct_html = ''

    erklaerung_html = render_markdown_with_math(md, q.get('erklaerung', '') or '').strip() if q.get('erklaerung') else ''

    thema = q.get('thema', '') or ''

    front = f"""
    <div class="card card-front">
      <div class="meta">{meta_title} — {thema}</div>
      <div class="question">{q_html}</div>
      <div class="options">{options_html}</div>
    </div>
    """

    back = f"""
    <div class="card card-back">
      <div class="meta">{meta_title} — {thema}</div>
      <div class="answer">{correct_html}</div>
      <div class="explanation">{erklaerung_html}</div>
    </div>
    """

    return front + back


def generate_preview(questions_path: str, out_path: str):
    _ensure_dir(os.path.dirname(out_path) or '.')
    questions = _load_questions(questions_path)
    md = MarkdownIt()
    meta_title = os.path.basename(questions_path).replace('questions_', '').replace('.json', '')

    cards_html = []
    for q in questions:
        try:
            cards_html.append(build_card_html(q, meta_title, md))
        except Exception as e:
            cards_html.append(f"<div class='card error'>Fehler beim Rendern: {e}</div>")

    # If pykatex_render is not available, inject client-side renderers so the preview still shows math.
    math_assets = """
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
    """
    if not pykatex_render:
        math_assets += """
      <script src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
      <script src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>
      <script>
        (function () {
          var attempts = 0;
          function renderKaTeX() {
            if (window.renderMathInElement) {
              try {
                window.renderMathInElement(document.body, {
                  delimiters: [
                    {left: '\\(', right: '\\)', display: false},
                    {left: '\\[', right: '\\]', display: true},
                    {left: '$$', right: '$$', display: true},
                    {left: '$', right: '$', display: false}
                  ],
                  throwOnError: false
                });
                window.__ankiPreviewRenderedByKaTeX = true;
              } catch (err) {
                console.warn('KaTeX rendering failed', err);
              }
              return;
            }
            if (attempts < 20) {
              attempts += 1;
              setTimeout(renderKaTeX, 100);
            }
          }
          if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', renderKaTeX);
          } else {
            renderKaTeX();
          }
        })();
      </script>
      <script>
        window.MathJax = {
          tex: {
            inlineMath: [['\\(','\\)'], ['$', '$']],
            displayMath: [['\\[','\\]'], ['$$','$$']]
          },
          options: {
            skipHtmlTags: ['script','noscript','style','textarea','pre','code']
          },
          startup: {
            typeset: false,
            ready: () => {
              MathJax.startup.defaultReady();
              if (!window.__ankiPreviewRenderedByKaTeX) {
                MathJax.typesetPromise();
              }
            }
          }
        };
      </script>
      <script id="mathjax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
      <script>
        (function () {
          var attempts = 0;
          function typeset() {
            if (window.__ankiPreviewRenderedByKaTeX) {
              return;
            }
            if (window.MathJax && window.MathJax.typesetPromise) {
              MathJax.typesetPromise();
              return;
            }
            if (attempts < 20) {
              attempts += 1;
              setTimeout(typeset, 100);
            }
          }
          if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', typeset);
          } else {
            typeset();
          }
        })();
      </script>
      """

    html = f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Anki Preview - {meta_title}</title>
      <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background:#f6f6f8; }}
        .card {{ background: white; border-radius:8px; padding:12px; margin:12px 0; box-shadow:0 1px 4px rgba(0,0,0,0.06); }}
        .card-front {{ border-left: 4px solid #2563eb; }}
        .card-back {{ border-left: 4px solid #15803d; }}
        .meta {{ color:#666; font-size:0.85em; margin-bottom:6px }}
        .question {{ font-weight:600; margin-bottom:8px }}
        .options ol {{ padding-left:1.1em; margin:0 }}
        .answer {{ color:#15803d; font-weight:700 }}
    </style>
  {math_assets}
    </head>
    <body>
    <h2>Anki Preview for {meta_title}</h2>
    {''.join(cards_html)}
    </body>
    </html>
    """

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Preview written to: {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--questions', '-q', required=True, help='Path to questions JSON file')
    parser.add_argument('--out', '-o', default='artifacts/anki_preview.html', help='Output HTML file')
    args = parser.parse_args()
    generate_preview(args.questions, args.out)


if __name__ == '__main__':
    main()
