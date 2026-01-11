# Anleitung: Qualitätssicherung eines Fragensets (für Redakteure)

Kurz: Dieses Dokument erklärt, wie die automatische Qualitätsprüfung (QA) eines Fragensets funktioniert, wie Sie Fehlermeldungen verstehen und typische Probleme schnell beheben.

1) Was macht die QA?
- Prüft, ob das JSON korrekt aufgebaut ist (`meta` + `questions` oder reine Fragen-Liste).
- Validiert Pflichtfelder (Titel, Frage-Text, Antwortoptionen, Lösung, Erklärung, Thema, Gewichtung).
- Prüft logische Konsistenz (z. B. ob der `answer`-Index innerhalb der `options` liegt).
- Findet Formatfehler (z. B. LaTeX in Backticks, problematische `<`/`>` in Formeln).
- Erkennt unerwünschte Modell- oder Import-Zitationsmarker (z. B. `[1]`, `doi:`, `:contentReference[...]`) und lehnt solche Uploads ab.
- Gibt Hinweise zu didaktischen Problemen (z. B. Themenverteilung, zu wenige/zu viele Optionen, `Length-Bias` wenn richtige Antworten deutlich länger/kürzer sind).

2) Fehler vs. Warnungen — wie lesen?
- Fehler (Error): Muss behoben werden, das Set kann nicht übernommen werden (z. B. ungültiges JSON, fehlende Pflichtfelder, `answer` außerhalb der Optionen).
- Warnung (Warning): Hinweis auf Verbesserung; das Set kann meist gespeichert werden, aber bitte prüfen (z. B. ungewöhnliche Themenverteilung, zu viele Optionen).

3) Häufige Fehler und schnelle Fixes
- Ungültiges JSON / Syntaxfehler
  - Symptom: Parser-Fehler beim Laden ("Ungültiges JSON").
  - Fix: Achten Sie auf fehlende Kommata, falsche Anführungszeichen oder unescaped Zeichen. Verwenden Sie einen JSON-Linter oder Editor mit JSON-Highlighting.

- `answer` ist kein gültiger Index
  - Symptom: Fehler: "'answer' ist kein gültiger Index für N Optionen".
  - Fix: Zähle die Elemente in `options` und setze `answer` auf die 0-basierte Position der richtigen Antwort (erste Option = 0).

  Beispiel (korrigieren):
  ```json
  {
    "question": "Wie groß ist 2+2?",
    "options": ["3", "4", "5"],
    "answer": 1
  }
  ```

- Zu wenige Optionen
  - Symptom: Fehler wenn weniger als 2 Optionen.
  - Fix: Fügen Sie mindestens zwei Antwortoptionen hinzu.

- LaTeX in Backticks
  - Symptom: Fehler: "LaTeX darf nicht in Backticks stehen." (z. B. `\$x$` in `\` ` `).
  - Fix: Entfernen Sie die Backticks um LaTeX-Ausdrücke, z. B. `$x^2$` statt `` `$x^2$` ``.

- Smart-Quotes / unsichtbare Zeichen
  - Symptom: Probleme beim Parsen oder seltsame Zeichen in Texten.
  - Fix: Ersetzen Sie typografische Anführungszeichen durch gerade Anführungszeichen ("). Der Upload-Prozess ersetzt einige davon automatisch, aber prüfen Sie das Ergebnis.

- Verbotene Zitiermarker oder Modell-Provenance
  - Symptom: Upload wird abgewiesen mit Hinweis auf verbotene Inline-Verweise.
  - Fix: Entfernen Sie z. B. End-Referenzen wie "[1]", DOI-Angaben oder spezielle Import-Markup-Strings. Achten Sie besonders auf Inhalte, die von einer KI oder Import-Tool stammen könnten.

4) Minimales, sicheres JSON-Beispiel
Ändern Sie nur den Textwert innerhalb der Anführungszeichen nach dem Doppelpunkt (z. B. ändern Sie den Text nach `"question":`).

Beispiel (kopieren, nur Texte anpassen):
```json
{
  "meta": { "title": "Mein Testset", "question_count": 1 },
  "questions": [
    {
      "question": "Was ist 2+2?",
      "options": ["3","4"],
      "answer": 1,
      "explanation": "2+2 ergibt 4.",
      "weight": 1,
      "topic": "Mathematik"
    }
  ]
}
```

5) Upload / Validierung im System
- Im Editor/Upload-Bereich: Laden Sie die JSON-Datei hoch oder fügen Sie den Inhalt ein.
- Die QA läuft automatisch und listet Fehler/Warnungen. Beheben Sie die Fehler in Ihrem Editor und laden Sie neu.
- Wenn nur Warnungen verbleiben, können Sie das Set meist speichern — prüfen Sie die Hinweise trotzdem.

6) Für Power-User: lokale Prüfung (optional)
- CLI: Projekt-Root →
```bash
python validate_sets.py
```
- Einzelne Datei prüfen (Python-Konsole):
```python
import json
from question_set_validation import validate_question_set_data
s = json.load(open('data/questions_example.json','r',encoding='utf-8'))
errors, warnings = validate_question_set_data(s)
print('errors', errors)
print('warnings', warnings)
```

7) Tipps zur Fehlervermeidung
- Verwenden Sie einen JSON-fähigen Texteditor (z. B. VS Code) mit Auto-Format.
- Bearbeiten Sie nur die Textwerte in Anführungszeichen, nicht die Struktur (`[]`, `{}`, `:`).
- Vermeiden Sie Copy&Paste aus Word/PowerPoint ohne „smart-quote“-Bereinigung.
- Prüfen Sie besonders LaTeX-Formeln und ersetzen Sie problematische `<`/`>` in Formeln mit `\langle`/`\rangle`.

8) Hilfe & Support
- Wenn eine Meldung unklar ist, kopieren Sie die Fehlermeldung und öffnen ein Ticket oder fragen Sie im Redakteurs-Chat, angehängt: die JSON-Datei und die exakte Fehlermeldung.

---
Datei: `docs/fragenset_qa_user_guide.md`
