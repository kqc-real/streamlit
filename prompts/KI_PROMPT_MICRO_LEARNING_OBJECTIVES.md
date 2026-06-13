# MC-Test-Prompt: Micro-Lernziele erzeugen

Du erzeugst kompetenzorientierte Micro-Lernziele aus einem MC-Test-Fragenset.
Dieser Prompt gehört zu Schritt 2 im Dialog **"Fragenset mit externem LLM erstellen"**:

1. Fragenset als MC-Test-JSON erzeugen und speichern
2. Lernziele als Markdown erzeugen und speichern
3. Fragenset per QA-Prompt optimieren
4. Lernziele per QA-Prompt an das optimierte Set anpassen

Du bekommst ein JSON-Objekt mit:

- `meta`
- `questions`

Typische Fragefelder:
- `question`
- `options`
- `answer`
- `explanation`
- `weight`
- `topic`
- `concept`
- `cognitive_level`
- `extended_explanation`
- `mini_glossary`

## Ziel

Erzeuge ein Markdown-Dokument mit:

- 5-10 übergeordneten Lernziel-Clustern
- genau **einem detaillierten Micro-Lernziel pro Frage**
- Gruppierung nach kognitivem Niveau
- logischer Progression von einfachen zu komplexeren Themen

## Sprache

Bestimme die Ausgabesprache aus `meta.language`.
Falls `meta.language` fehlt, leite die Sprache aus den Fragen ab.
Ignoriere die Chat-Sprache, wenn sie vom Fragenset abweicht.

Lokalisierte Level-Namen:
- Deutsch: Reproduktion / Anwendung / Strukturelle Analyse
- Englisch: Reproduction / Application / Analysis
- Andere Sprachen: Reproduction / Application / Analysis

## Kognitives Niveau

Nutze `weight` als primäre Quelle und prüfe `cognitive_level` auf Konsistenz.
Wenn `weight`, `cognitive_level` und tatsächliche Frage nicht zusammenpassen, ordne das Lernziel
nach dem tatsächlich geprüften Anspruch ein.

### Reproduktion / Reproduction (`weight = 1`)

Fakten, Begriffe, Definitionen.

Geeignete Verben:
- Deutsch: nennen, beschreiben, definieren, identifizieren, wiedergeben, benennen
- Englisch: name, describe, define, identify, state, list

### Anwendung / Application (`weight = 2`)

Wissen in einem Fall, Beispiel, Rechenschritt oder Kontext verwenden.

Geeignete Verben:
- Deutsch: anwenden, einsetzen, auswählen, bestimmen, zuordnen, klassifizieren, erkennen
- Englisch: apply, use, select, determine, classify, recognize

### Strukturelle Analyse / Analysis (`weight = 3`)

Zusammenhänge, Ursachen, Trade-offs, Begründungen oder Diagnosen.

Geeignete Verben:
- Deutsch: analysieren, vergleichen, begründen, diagnostizieren, bewerten, herleiten, ableiten
- Englisch: analyze, compare, justify, diagnose, evaluate, derive, assess

## Regeln für detaillierte Micro-Lernziele

- Genau ein Lernziel pro Frage.
- Ein Lernziel enthält genau **ein** beobachtbares Verb.
- Keine Verbketten wie "identifizieren und bewerten".
- Keine vagen Verben wie "verstehen", "kennen", "wissen".
- Das Lernziel muss spezifisch zum `concept` und `topic` der Frage passen.
- Das Lernziel soll nach "Du kannst ..." bzw. "You can ..." grammatisch funktionieren.
- Keine Quellenangaben oder Zitationsmarker.

## Übergeordnete Lernziele

Clustere verwandte Topics/Concepts zu 5-10 übergeordneten Lernzielen.
Diese Cluster dürfen mehrere Fragen bündeln und sollen Studierenden erklären, welche Kompetenz
sie mit dem Set aufbauen.

Jeder Cluster enthält:
- eine kurze Überschrift
- eine fett gesetzte Kompetenzformulierung
- 1-2 kurze Absätze zur integrierten Kompetenz

## Output

Gib genau einen vollständigen Markdown-Codeblock aus:

```markdown
# Übergeordnete Lernziele: <Titel>

## <Cluster 1>
**<Kompetenzformulierung>**

<1-2 kurze Absätze>

---

# Detaillierte Lernziele

Im Kontext des Themas **<Titel>** soll dir dieses Fragenset helfen, die folgenden detaillierten Lernziele zu erreichen:

### Reproduktion

**Du kannst ...**

1. <Lernziel>

### Anwendung

**Du kannst ...**

1. <Lernziel>

### Strukturelle Analyse

**Du kannst ...**

1. <Lernziel>
```

Passe Überschriften, Level-Namen und die Zeile "Du kannst ..." an die Sprache des Fragensets an.
Wenn ein Level keine Fragen enthält, lasse den Abschnitt weg.

## Interne Endprüfung vor Ausgabe

Prüfe still:

- Anzahl detaillierter Lernziele entspricht exakt der Anzahl der Fragen.
- Jedes detaillierte Lernziel hat genau ein Verb.
- Jedes Lernziel passt zum tatsächlichen Anspruch der Frage.
- Cluster sind nicht zu kleinteilig und nicht zu allgemein.
- Reihenfolge ist didaktisch sinnvoll.
- Kein Text außerhalb des einen Markdown-Codeblocks.

LETZTE ANWEISUNG: Gib ausschließlich den einen Markdown-Codeblock aus.
