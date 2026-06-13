# Style Guidelines

Diese Leitlinien buendeln Produkt-, Inhalts- und UI-Konventionen fuer MC-Test. Sie ergaenzen `AGENTS.md` und sollen helfen, neue Beitraege konsistent, pruefbar und fuer Studierende gut nutzbar zu halten.

## Produkt- und UI-Sprache

- UI-Texte sind auf Deutsch, klar und handlungsnah.
- Fachbegriffe sind erlaubt, muessen aber dort erklaert werden, wo Studierende ohne IT-Vorkenntnisse sie brauchen.
- Texte sollen kurz bleiben: erst die Handlung, dann die Konsequenz.
- Fehlermeldungen nennen Ursache und naechsten Schritt.
- Keine Marketing-Sprache in Arbeitsoberflaechen. Die App ist ein Lern- und Pruefwerkzeug, keine Landingpage.
- Mehrsprachige Texte muessen idiomatisch sein, nicht wortwoertlich uebersetzt.

## Externe LLM-Prompts

- Prompt-Dateien in `prompts/` sind in US English.
- Externe LLMs duerfen kein Wissen ueber MC-Test, diese App, das Repo oder lokale Dateipfade voraussetzen.
- Der Prompt beschreibt das Ziel-JSON vollstaendig und eigenstaendig.
- Die Inhaltssprache wird ueber Nutzerauftrag und `meta.language` gesteuert. JSON-Feldnamen bleiben Englisch.
- Prompt-Preview in der App ist read-only und gerendert. Copy/Download liefern immer den rohen, ungerenderten Prompt.
- Postproduction-Prompts sollen konkrete Pruefschritte und harte Output-Regeln enthalten, damit heutige LLMs reproduzierbare Ergebnisse liefern.

## Fragensets

- Neue Fragensets verwenden die kanonische Struktur `meta` plus `questions`.
- Neue Fragensets verwenden englische Keys: `question`, `options`, `answer`, `explanation`, `weight`, `topic`, `concept`.
- Deutsche Legacy-Aliasse sind nur Import-Kompatibilitaet.
- `answer` ist 0-basiert, `options` enthaelt 3 bis 5 Optionen, `weight` ist 1, 2 oder 3.
- Pro Frage ist genau eine fachlich eindeutig richtige Antwort vorgesehen.
- Distraktoren sind plausibel, gleichartig formuliert und nicht durch Laenge oder Grammatik leicht eliminierbar.
- `mini_glossary` enthaelt 2 bis 6 relevante Begriffe, wenn es genutzt wird.
- `cognitive_level` folgt der Taxonomie Reproduktion, Anwendung, Strukturelle Analyse.

## Markdown, HTML und LaTeX

- Markdown soll die Lesbarkeit verbessern, nicht die Frage ueberfrachten.
- Antwortoptionen duerfen Markdown enthalten, muessen aber in App, PDF, Anki und arsnova.eu robust bleiben.
- Markdown-Tabellen sind in Antwortoptionen zu vermeiden, weil Zielsysteme sie unterschiedlich rendern.
- Sichere HTML-Tags wie `code`, `sub`, `sup`, `strong` und `em` sind erlaubt, wenn sie didaktisch helfen.
- Unsicheres HTML, Skripte und Event-Handler sind verboten.
- LaTeX steht in `$...$` oder `$$...$$`, nie in Backticks.
- In LaTeX keine rohen `<` oder `>` verwenden; stattdessen `\langle` und `\rangle`.

## Export-Stil

- Unterstützte Exportziele sind PDF, CSV/Analyse, Anki und arsnova.eu.
- Kahoot und arsnova.click sind keine Zielsysteme mehr.
- Anki-Exporte duerfen keine verschachtelte ABCD-Struktur erzeugen, die Antwortoptionen neu sortiert oder missverstaendlich gruppiert.
- arsnova.eu-Exporte sollen Beschreibung, Topics, Schwierigkeitsprofil, Mini-Glossar und didaktische Hinweise so vollstaendig wie moeglich in lesbarer Form abbilden.
- Wenn ein Zielsystem Markdown nur teilweise unterstuetzt, soll der Export robust lesbar bleiben, auch wenn einzelne Formatierungen entfallen.

## Streamlit- und Layout-Stil

- Streamlit-UI orientiert sich an Version 1.58.
- Neue Breitenangaben verwenden `width="stretch"` oder `width="content"`, nicht `use_container_width`.
- Neue HTML-Einbettungen verwenden `st.html` oder `st.iframe`, nicht `st.components.v1.html`.
- Keine verschachtelten Expander.
- Widget-Keys muessen eindeutig und stabil sein.
- Vertikale Abstaende kompakt halten, ohne Buttons, Antwortoptionen oder Header gedrueckt wirken zu lassen.
- Button-Labels muessen vertikal mittig erscheinen.
- Auf Mobile keine virtuelle Tastatur oeffnen, wenn kein echter Texteingabefall vorliegt.
- Timer-, Pacer- und Warnhinweise muessen zur aktuell sichtbaren Restzeit passen.
- Dark Theme braucht ausreichenden Kontrast; zusaetzliche Hintergruende oder Umrandungen nur einsetzen, wenn sie wirklich benoetigt werden.

## QA-Stil

- Code-Aenderungen mit passenden Pytest-Tests absichern.
- Fragen-JSON mit `python validate_sets.py data/<set>.json` pruefen.
- i18n-Aenderungen mit `python scripts/i18n/check_i18n.py` pruefen.
- UI-Aenderungen im Browser testen, bei Layout- oder Mobile-Themen mit kleinem und grossem Viewport.
- Prompt-Aenderungen mit den Prompt-Architekturtests pruefen.
- Export-Aenderungen mit einem Markdown-Stress-Fragenset gegen PDF, Anki und arsnova.eu validieren, wenn die Aenderung Markdown oder Antwortoptionen betrifft.

## Repository-Hygiene

- Keine Secrets, echten Personendaten, lokalen Datenbanken, Downloads oder temporaeren Dateien committen.
- `.streamlit/secrets.toml` bleibt lokal; `.streamlit/secrets.example.toml` ist die Vorlage.
- `tmp/` und generierte Export-Artefakte bleiben ausserhalb der Versionierung.
- EDULEARN26-Bezuege sollen auf das PDF in `docs/mc-test-paper/mc-test-edulearn26.pdf` zeigen.
