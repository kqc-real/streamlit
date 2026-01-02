# Mini-Glossar Schema für Fragensets

## Übersicht

Jede Frage kann ein optionales `mini_glossary` Feld enthalten, das wichtige Begriffe und deren Definitionen für diese spezifische Frage dokumentiert. Diese Einträge werden im PDF-Export gesammelt und als Nachschlagewerk am Ende angezeigt.

## Begriffe-Hierarchie

Um die Struktur der Fragensets zu verstehen:

- **title** (in meta): Generalthema des Sets (z. B. "Mathematik").
- **topic** (pro Frage): Unterthema, das mehrere Fragen umfassen kann (z. B. "Lineare Algebra").
- **concept** (pro Frage): Zentrales Konzept, oft eine misconception (z. B. "Determinante").
- **mini_glossary** (pro Frage): 1-4 Schlüsselbegriffe mit Definitionen (z. B. "Determinante": "Eine Zahl, die einer Matrix zugeordnet wird...").

## JSON-Schema

```json
{
  "frage": "...",
  "optionen": [...],
  "loesung": 0,
  "erklaerung": "...",
  "gewichtung": 1,
  "topic": "...",
  "concept": "...",
  "mini_glossary": {
    "Begriff 1": "Definition des Begriffs 1. Kann LaTeX enthalten: $x^2$",
    "Begriff 2": "Definition des Begriffs 2.",
    "Begriff 3": "Definition des Begriffs 3."
  }
}
```

## Regeln für mini_glossary

### ✅ Best Practices:

1. **Kernbegriffe**: Nur die wichtigsten 2-4 Begriffe pro Frage
2. **Präzise Definitionen**: Kurz und prägnant (1-3 Sätze)
3. **Konsistenz**: Gleiche Begriffe sollten gleich definiert sein
4. **LaTeX-Support**: Formeln mit `$...$` oder `$$...$$` möglich
5. **Erkenntnisgewinn**: Was lernt der User durch diese Frage?

### ❌ Zu vermeiden:

- Zu lange Definitionen (> 5 Sätze)
- Triviale Begriffe, die jeder kennt
- Redundante Wiederholungen aus der Erklärung
- Begriffe ohne Bezug zur Frage

## Beispiele

### Gut ✅

```json
"mini_glossary": {
  "Surjektivität": "Eine Abbildung ist surjektiv, wenn jedes Element der Zielmenge mindestens einmal getroffen wird. Die Bildmenge entspricht der gesamten Zielmenge.",
  "Injektivität": "Eine Abbildung ist injektiv, wenn verschiedene Elemente der Definitionsmenge auf verschiedene Elemente der Zielmenge abgebildet werden.",
  "Bijektivität": "Eine Abbildung ist bijektiv, wenn sie sowohl injektiv als auch surjektiv ist und somit umkehrbar."
}
```

### Nicht ideal ❌

```json
"mini_glossary": {
  "Abbildung": "Eine Abbildung ist eine Funktion.", // Zu trivial
  "Surjektivität": "Surjektivität ist eine wichtige Eigenschaft von Abbildungen, die besagt, dass alle Elemente der Zielmenge mindestens einmal als Funktionswert vorkommen müssen, wobei dies besonders wichtig für die Umkehrbarkeit ist..." // Zu lang
}
```

## PDF-Export

Im PDF werden alle `mini_glossary` Einträge:
- Gesammelt und dedupliziert (erste Definition hat Priorität)
- Alphabetisch sortiert
- In einer eigenen Sektion am Ende angezeigt
- Mit professionellem Kartenlayout dargestellt

## Verwendung

```python
# Automatische Extraktion im PDF-Export
glossary_terms = _extract_glossary_terms(questions)
# Returns: {"Begriff": "Definition", ...}
```

## Migration bestehender Fragensets

Füge `mini_glossary` zu bestehenden Fragen hinzu:

```bash
# Beispiel: Mathematik_I.json
# Füge nach "thema" ein:
"thema": "1. Mengen und Abbildungen",
"mini_glossary": {
  "Schnittmenge": "Die Schnittmenge $A \\cap B$ enthält alle Elemente, die sowohl in $A$ als auch in $B$ enthalten sind.",
  "Differenzmenge": "Die Differenzmenge $A \\setminus B$ enthält alle Elemente aus $A$, die nicht in $B$ enthalten sind."
}
```

## Qualitätskontrolle

Prüfe regelmäßig:
- [ ] Sind alle wichtigen Begriffe abgedeckt?
- [ ] Sind Definitionen klar und verständlich?
- [ ] Gibt es Duplikate mit unterschiedlichen Definitionen?
- [ ] Ist das Glossar für Lernende hilfreich?

## Zukünftige Erweiterungen

- **Glossar-Datenbank**: Zentrale Glossar-Tabelle mit Begriffen
- **Auto-Linking**: Begriffe in Fragen automatisch verlinken
- **Mehrsprachigkeit**: Glossar in verschiedenen Sprachen
- **Kategorisierung**: Glossar nach Themen gruppieren
