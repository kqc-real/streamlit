# Conventions

- UI-Texte deutsch, kurz, fuer Studierende ohne IT-Vorkenntnisse verstaendlich; i18n ueber `i18n/*.json` und `i18n.context` respektieren.
- Fragenset-Schema: Pflichtfelder je Frage `question`, `options`, `answer`, `explanation`, `weight`, `topic`, `concept`; `answer` ist 0-basiert; `options` 3-5; `weight` 1-3.
- `meta.language`, `meta.title`, `meta.question_count` sind Pflicht nach Validator-Konvention; `difficulty_profile`, `time_per_weight_minutes`, `test_duration_minutes` moeglichst konsistent halten.
- `config._build_question_set` normalisiert/renummeriert Fragen, synchronisiert alte deutsche Aliasfelder (`frage`, `optionen`, `loesung`, ...), saniert HTML und setzt berechnete Metadaten neu.
- Inhaltliche Arbeit an Fragensets: `concept` fuellen, Laengen-Bias der richtigen Antwort reduzieren, `mini_glossary` auf 2-6 Eintraege, Lernziele pro Frage, `cognitive_level` mit Lernzielen syncen.
- Cognitive-Level: `Reproduktion`, `Anwendung`, `Strukturelle Analyse`; Micro-Lernziele mit genau einem Verb pro Frage.
- LaTeX nicht in Backticks; in Formeln kein `<`/`>`, stattdessen `\\langle`/`\\rangle`.
- User-Uploads laufen durch Groessenlimit, Kodierungsfallback, JSON-Sanitizing, HTML-Sanitizing und Ablehnung von Inline-Zitationsmarkern.
- DB-Reset/Admin-Loeschaktionen sind destruktiv; vor solchen Aenderungen Backup-Hinweis bzw. explizite Nutzerfreigabe einholen.
- Keine echten Personendaten/API-Keys hardcoden; Admin-Key lokal via `.env`, Cloud via Streamlit Secrets.