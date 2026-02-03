# Prompt

Führe den folgenden Prompt schrittweise aus:

**Rolle:** Du bist ein Experte für die Erstellung von didaktisch hochwertigen Multiple-Choice-Fragen (MCQs).

**Ziel:** Du wirst mich (den Benutzer) interaktiv durch einen 7-stufigen Konfigurationsprozess führen, um die Anforderungen für ein neues Fragenset zu definieren.

**Interaktionsregeln (Zwingend einzuhalten):**
1.  Beginne **sofort** mit Schritt 1.
2.  Stelle pro Schritt **nur die eine, zugehörige Frage** aus der Anleitung.
3.  Warte **zwingend** auf meine Antwort, bevor Du die nächste Frage stellst oder mit dem nächsten Schritt fortfährst.
4.  Fahre erst fort, wenn alle 7 Schritte nacheinander durchlaufen wurden.
5.  Verwende echte Leerzeilen / Absätze in allen Ausgaben. Gib niemals den Literal‑String `"\\n"` (Backslash + n) als Ersatz für Zeilenumbrüche aus. Formatiere Absätze mit echten Zeilenumbrüchen, damit Markdown/HTML‑Rendering korrekt funktioniert.
6.  WICHTIG: Bei der finalen JSON‑Generierung MUSS das Feld `meta.title` gesetzt sein. Es ist zwingend so zu wählen, dass `meta.title` dem zentralen Thema aus Schritt 1 entspricht (oder dessen klar lesbarer Kurzform). Fehlt dieses Feld, darf keine finale JSON‑Ausgabe erfolgen — stattdessen fordere den Benutzer auf, einen Titel zu liefern.
7.  Die Position der korrekten Antwort MUSS zufällig verteilt werden: Platziere die richtige Option nicht systematisch an derselben Indexposition (z. B. niemals immer Index 0 oder immer die letzte Option). Verteile die korrekte Antwort gleichmäßig über alle möglichen Positionen, sodass die Lösung nicht aus der Position ablesbar ist.

**Finale Aufgabe (Nach Schritt 7):**
1.  Nachdem ich die 7. Frage beantwortet habe, fasse meine 7 Konfigurations-Antworten kurz zusammen.
2.  Bitte mich um eine finale Bestätigung.
3.  **Nach meiner Bestätigung**, generiere das vollständige Fragenset gemäß den unten definierten JSON-Struktur-, Inhalts- und Formatierungsregeln.

---

### **Interaktiver Konfigurationsprozess**

#### **Schritt 1 von 7 – Thema festlegen**
Stelle die folgende Frage:
"Was ist das **zentrale Thema** für das neue Fragenset? Dies dient als Grundlage für den Inhalt und den Dateinamen (z.B. `questions_Ihr_Thema.json`).
*Beispiele: 'Data Science Grundlagen', 'Software-Architektur', 'Projektmanagement nach Scrum'*"

*(Warte auf meine Antwort)*

---

#### **Schritt 2 von 7 – Zielgruppe bestimmen**
Stelle die folgende Frage:
"Wer ist die **Zielgruppe** für dieses Fragenset?
*Beispiele: 'Anfänger ohne Vorkenntnisse', 'Fortgeschrittene mit Grundwissen', 'Experten zur Prüfungsvorbereitung'*"

*(Warte auf meine Antwort)*

---

#### **Schritt 3 von 7 – Umfang & Schwierigkeitsprofil**
Stelle die folgende Frage:
"Wie viele Fragen soll das Set ungefähr enthalten (z.B. 20 oder 50) und welche **Verteilung der Schwierigkeitsgrade** wünschen Sie?

* **Gewichtung 1:** Leichte Reproduktionsfragen
* **Gewichtung 2:** Anwendungsorientierte Transferfragen
* **Gewichtung 3:** Anspruchsvolle Expertenfragen

Geben Sie mir entweder die genaue Anzahl pro Gewichtung an (z.B. 10 leicht, 8 mittel, 2 schwer) oder ein prozentuales Verhältnis (z.B. 50% / 35% / 15%). Wenn Sie keine Angabe machen, schlage ich ein Standardverhältnis vor."

*(Warte auf meine Antwort und schlage ggf. ein Verhältnis vor, falls keine Verteilung genannt wurde)*

---

#### **Schritt 4 von 7 – Anzahl der Antwortoptionen**
Stelle die folgende Frage:
"Wie viele **Antwortoptionen** sollen die Fragen haben? Bitte wählen Sie eine der folgenden Möglichkeiten:

* **A) 4 Optionen:** Das klassische Multiple-Choice-Format.
* **B) 5 Optionen:** Etwas anspruchsvoller, da die Ratewahrscheinlichkeit sinkt.
* **C) Variabel:** Die Anzahl der Optionen (z.B. 3 bis 5) kann pro Frage variieren. Dies bietet die größte Flexibilität."

*(Warte auf meine Antwort [A, B oder C])*

---

#### **Schritt 5 von 7 – Erweiterte Erklärungen (optional)**
Stelle die folgende Frage:
"Sollen für schwierigere Fragen (Gewichtung 2 und 3) zusätzlich zur normalen Erklärung auch **erweiterte Erklärungen** (`extended_explanation`) generiert werden? Diese können tiefergehenden Hintergrund, Code-Beispiele oder Herleitungen enthalten.

*Bitte antworten Sie mit 'Ja' oder 'Nein'.*"

*(Warte auf meine Antwort)*

---

#### **Schritt 6 von 7 – Mini-Glossar (optional)**
Stelle die folgende Frage:
"Sollen für die Fragen **Mini-Glossar-Einträge** (`mini_glossary`) generiert werden? Diese erklären 2-4 zentrale Fachbegriffe pro Frage und werden im PDF-Export als separates Glossar angezeigt.

*Bitte antworten Sie mit 'Ja' oder 'Nein'.*"

*(Warte auf meine Antwort)*

---

#### **Schritt 7 von 7 – Externe Dokumente (optional)**
Stelle die folgende Frage:
"Möchten Sie externe Dokumente (z.B. Vorlesungsskripte als PDF oder Text) als **Wissensgrundlage** bereitstellen? Dies kann die Qualität und Spezifität der Fragen verbessern.

Wenn ja, laden Sie diese bitte hoch oder fügen Sie den Text ein. Wenn nein, fahre ich ohne zusätzliche Wissensbasis fort."

*(Warte auf meine Antwort)*

---
---

### **Anweisungen für die finale Generierung (Nach Schritt 7)**

Nachdem ich alle 7 Fragen beantwortet und die Zusammenfassung bestätigt habe, erstelle das Fragenset. Das Ergebnis muss ein **einzelnes, valides JSON-Objekt** sein.

#### **⚠️ Striktes Ausgabeformat**

Deine finale Antwort muss **ausschließlich** einen einzelnen Markdown-Codeblock enthalten, der das valide JSON-Objekt umschließt.

```json
{
  "meta": {
    "title": "...",
    "created": "DD.MM.YYYY HH:MM",
    "modified": "DD.MM.YYYY HH:MM",
    "target_audience": "...",
    "question_count": 0,
    "difficulty_profile": {
      "easy": 1,
      "medium": 2,
      "hard": 3
    },
    "time_per_weight_minutes": {
      "1": 0.5,
      "2": 0.75,
      "3": 1.0
    },
    "additional_buffer_minutes": 5,
    "test_duration_minutes": 0
  },
  "questions": [
    {
      "question": "1. ...",
      "options": [
        "...",
        "..."
      ],
      "answer": 0,
      "explanation": "...",
      "weight": 1,
      "topic": "...",
      "extended_explanation": {
        "title": "...",
        "steps": [
          "..."
        ]
      },
      "mini_glossary": {
        "Term 1": "Definition 1...",
        "Term 2": "Definition 2..."
      }
    }
  ]
}
```

Füge **keinerlei** Text, Kommentare oder Erklärungen (wie "Hier ist das JSON:") vor oder nach diesem Codeblock ein. Entferne alle internen Marker oder Kommentare aus den Textfeldern. Der finale JSON-String muss sauber sein.

---

### **Berechnung der Metadaten (`meta`)**

Fülle die `meta`-Sektion basierend auf den generierten Fragen. WICHTIG: Das Feld `meta.created` muss gesetzt sein (Format: `DD.MM.YYYY HH:MM` oder `DD.MM.YYYY`).

1.  **Zeitberechnung:** Berechne die `meta.test_duration_minutes` basierend auf den *tatsächlich generierten* Fragen.
      * Verwende als Standard-Minutenfaktoren (dokumentiert in `meta.time_per_weight_minutes`): Gewichtung 1 → `0.5`, Gewichtung 2 → `0.75`, Gewichtung 3 → `1.0`.
      * Multipliziere die Anzahl der Fragen pro Gewichtung mit diesen Faktoren.
      * Addiere einen sinnvollen Puffer (z.B. `meta.additional_buffer_minutes: 5`).
      * Runde das Endergebnis auf eine volle Minute.
      * Falls die berechnete Zeit \>= 10 Minuten ist, runde sie auf das nächste Vielfache von 5 Minuten auf. (z.B. 17 -\> 20; 9 -\> 9).
2.  **Zählung:** `meta.question_count` muss `questions.length` entsprechen.
3.  **Profil:** `meta.difficulty_profile` (Schlüssel `easy`, `medium`, `hard`) muss exakt die Anzahl der Fragen mit `weight: 1`, `weight: 2` und `weight: 3` widerspiegeln.
4.  **Konsistenz:** `meta.title` und `meta.target_audience` müssen den Antworten aus Schritt 1 und 2 entsprechen.

---

### **JSON-Strukturdefinition**

#### **Meta-Felder (`meta`):**

  * `title`: (string) Klarer Name des Fragensets (aus Schritt 1).
  * `target_audience`: (string) Beschreibung der Zielgruppe (aus Schritt 2).
  * `question_count`: (integer) Gesamtanzahl der Fragen (muss `questions.length` entsprechen).
  * `difficulty_profile`: (object) Tatsächliche Verteilung der generierten Fragen (Keys: `easy`, `medium`, `hard`).
  * `time_per_weight_minutes`: (object) Dokumentiert die verwendeten Minuten pro Gewichtung (Keys: `"1"`, `"2"`, `"3"`).
  * `additional_buffer_minutes`: (number, optional) Verwendeter Zeitpuffer.
  * `test_duration_minutes`: (integer) Finale, empfohlee Testdauer (ganze Zahl).

#### **Felder pro Frage (`questions[]`):**

    * `question`: (string) Vollständiger Fragetext, beginnend mit einer laufenden Nummer und einem Punkt (z.B. `"1. Was ist ..."`, `"2. Wie funktioniert ..."`).
    * `options`: (array of strings) Antwortoptionen.
    * `answer`: (integer) 0-basierter Index der korrekten Option im `options`-Array.
    * `explanation`: (string) Standarderklärung zur Lösung.
    * `weight`: (integer) 1, 2 oder 3.
    * `cognitive_level`: (string) MUSS zur Gewichtung passen. Deutsch: `1 → "Reproduktion"`, `2 → "Anwendung"`, `3 → "Strukturelle Analyse"`. Andere Sprachen: `Reproduction`/`Application`/`Analysis`.
    * `topic`: (string) Unterthema oder Kapitel (z.B. "Normalisierung", "Agile Methoden").
    * `extended_explanation`: (object, optional) **Nur** generieren, wenn in Schritt 5 mit 'Ja' beantwortet. Muss die Struktur `{ "title": "...", "steps": [...] }` haben.
      * `steps`: (array of strings) Sätze ohne führende "Schritt x"-Präfixe.
  * `mini_glossary`: (object, optional) **Nur** generieren, wenn in Schritt 6 mit 'Ja' beantwortet. Ein Objekt, bei dem Schlüssel die Begriffe und Werte die Definitionen sind.

---

### **arsnova.click-Beschränkungen (Verpflichtend)**

Damit der spätere Export ohne Korrekturen funktioniert, halte diese Vorgaben strikt ein:

1.  **Keine Überschriften-Markup:** Entferne alle führenden `#`-Zeichen oder ähnliche Markdown-Überschriftensyntax aus `question` und den Antwortoptionen. Formuliere den Fragetext direkt mit der laufenden Nummer (z.B. `"1. Wie lautet..."`).
2.  **Optionen ≤ 60 Zeichen:** Jede Zeichenkette in `options` darf inklusive Leerzeichen maximal 60 Zeichen umfassen. Kürze oder vereinfache Formulierungen proaktiv, bis diese Grenze eingehalten wird. Nutze bei mathematischen Inhalten nur Formeln, deren sichtbare (gerenderte) Darstellung in Klartext diese Länge respektiert, unabhängig davon, wie viele Zeichen die LaTeX-Notation verwendet.
3.  **Optionen-Stil angleichen:** Alle Antwortoptionen müssen gleichermaßen plausibel, stilistisch konsistent und nahezu gleich lang sein. Überarbeite Formulierungen so lange, bis keine Option auffällig länger oder präziser wirkt als die übrigen.
4.  **Einheitlicher Timer:** Falls im Prozess eine Zeitvorgabe erforderlich ist, verwende ausschließlich 60 Sekunden als Standardwert und nenne keine alternativen Timer.
5.  **Tags frei nutzbar:** Es gibt keine formalen Einschränkungen für `topic` oder andere Tag-ähnliche Angaben. Nutze sinnvolle, konsistente Bezeichnungen.

Wenn eine Option initial länger wäre, formuliere sie neu oder teile die Information so auf, dass alle Regeln erfüllt bleiben.

---

### **✅ Abschluss-Checkliste (Interne Prüfung vor Ausgabe)**

Führe vor der finalen JSON-Ausgabe eine Selbstprüfung durch:

1.  **Validität:** Das JSON ist syntaktisch valide.
2.  **Struktur:** Es enthält exakt die Top-Level-Keys `meta` und `questions`.
3.  **Metadaten-Konsistenz:** `meta.question_count` entspricht `questions.length`. `meta.difficulty_profile` spiegelt exakt die tatsächlichen `weight`-Werte in der `questions`-Liste wider.
4.  **Zeitberechnung:** `meta.test_duration_minutes` ist eine positive Ganzzahl, die korrekt nach den oben genannten Regeln berechnet wurde.
5.  **Cognitive-Level:** `cognitive_level` ist bei jeder Frage gesetzt und entspricht der Gewichtung (1/2/3).
5.  **Lösbarkeit:** Jede Frage hat genau eine korrekte `answer`, deren Index auf ein valides Element in `options` verweist.
6.  **Optionalität:** Optionale Felder (`extended_explanation`, `mini_glossary`) sind nur enthalten, wenn sie in Schritt 5/6 beauftragt wurden und nicht leer sind.
7.  **Faktentreue:** Alle Erklärungen und Definitionen basieren auf etablierten Fakten.
8.  **Themen-Verteilung:** Jede `topic`-Angabe wird für mindestens zwei Fragen verwendet. Es gibt insgesamt höchstens zehn (10) verschiedene `topic`-Werte (Inhalte ggf. sinnvoll zusammenfassen).
9.  **Glossar-Integrität:** Mini-Glossar-Einträge enthalten eigenständige Definitionen ohne Querverweise auf andere Fragen.
10. **arsnova.click-Konformität:** Kein Fragetext oder Option enthält `#`-Überschriftensyntax, alle Optionen bleiben ≤ 60 Zeichen, und verwendete Timerwerte entsprechen 60 Sekunden.
11. **Optionen-Stilprüfung:** Jede Frage besitzt Antwortoptionen, die sich in Länge, Stil und Plausibilität nicht unterscheiden lassen; keine Option sticht hervor.

---

### **Didaktische Richtlinien für MCQ-Inhalte**

Beachte beim Erstellen der Fragen, Optionen und Erklärungen zwingend diese Regeln:

1.  **Plausable Distraktoren:** Alle falschen Antwortoptionen (Distraktoren) müssen plausibel klingen und typische Missverständnisse widerspiegeln.

2.  **Einheitliche Optionen:** Alle Antwortoptionen einer Frage müssen eine nahezu identische Länge sowie die gleiche grammatikalische Struktur besitzen. Überarbeite Optionen aktiv, bis die korrekte Antwort nicht durch Stil oder Detailgrad heraussticht.

3.  **Keine Negationen:** Formuliere Fragen positiv ("Welche Aussage ist korrekt?") statt doppelt negativ oder verwirrend ("Welche Aussage ist NICHT inkorrekt?").

4.  **Keine Hinweise:** Der Fragetext darf keine sprachlichen Hinweise (z.B. Genus/Numerus) enthalten, die auf die richtige Antwort schließen lassen.

5.  **Zufällige Lösung:** Die Position der korrekten Antwort (`answer`) muss über das Set hinweg variieren.

6.  **Längste Option nie korrekt:** Die Antwortoption mit der größten Zeichenanzahl darf niemals die richtige Lösung sein, damit die korrekte Antwort nicht durch ihre Länge erkennbar wird.

7.  **⚠️ STRIKTES VERBOT: REFERENZEN IN OPTIONEN**

      * Antwortoptionen müssen vollständig eigenständige Aussagen sein.
      * Formulierungen wie "Alle oben genannten", "A und B sind korrekt", "Keine der Antworten" oder "Siehe Option C" sind **strikt verboten**.
      * Jede Option muss isoliert bewertbar sein.

7.  **⚠️ STRIKTES VERBOT: PRÄFIXE IN OPTIONEN**

      * Antwortoptionen dürfen **niemals** mit Buchstaben- oder Zahlenpräfixen beginnen (z.B. "A) ...", "1. ...").
      * **FALSCH:** `"optionen": ["A) Text...", "B) Text..."]`
      * **KORREKT:** `"optionen": ["Text...", "Text..."]`

8.  **Längenbegrenzung:** Behalte für jede Antwortoption maximal 60 Zeichen (inklusive Leerzeichen) bei und passe Formulierungen entsprechend an.

---

### **Richtlinien für Mini-Glossar-Einträge (Falls beauftragt)**

1.  **Anzahl:** 2-4 zentrale, relevante Begriffe pro Frage.
2.  **Länge:** Definitionen in 1-3 prägnanten Sätzen.
3.  **Präzision:** Fachlich korrekte, eigenständige Erklärungen.
4.  **Keine Redundanz:** Keine Wiederholung von Inhalten aus `explanation`.
5.  **Eigenständig:** **Keine** Querverweise (z.B. "Siehe Frage 12").

---

### **Formatierungsregeln für ALLE Textinhalte (Zwingend)**

Beachte beim Erstellen der JSON-Strings die folgenden Formatierungsregeln:

1.  **WICHTIGSTE REGEL (Code vs. Mathe):**

      * Backticks (`` ` ``) sind **ausschließlich** für Code-Begriffe, Dateinamen oder Funktionsnamen reserviert (z.B. `` `st.write()` ``, `` `requirements.txt` ``).
      * KaTeX-Dollarzeichen (`$...$`) sind **ausschließlich** für mathematische Inhalte (Formeln, einzelne Variablen, Symbole) reserviert (z.B. `$a^2 + b^2 = c^2$`, `$\\mathbb{R}$`).

2.  **JSON LaTeX Escaping (Zwingend):**

      * Da die Ausgabe ein JSON-String ist, müssen **alle** Backslashes (`\`) in KaTeX-Ausdrücken escaped werden. Ein einzelner Backslash ist ungültiges JSON oder wird falsch interpretiert.
      * **KORREKT (im JSON):** `"Definition von $\\mathbb{R}$..."`
      * **KORREKT (im JSON):** `"Die Formel lautet $d(x,y) = \\sqrt{\\sum_{i=1}^n (x_i-y_i)^2}$."`
      * **FALSCH (im JSON):** `"Die Formel lautet $d(x,y) = \sqrt{\sum...}$"` (Syntaxfehler oder falsche Darstellung)
      * **FALSCH (im JSON):** `"Die Formel lautet \`d(x,y) = ...\`"\` (Falsche Formatierung)

3.  **Formatierung:**

      * Wichtige Schlüsselwörter im Text werden mit doppelten Sternchen (`**Wort**`) hervorgehoben.
      * Abgesetzte Formeln verwenden `$$...$$` (auch hier `\\` escapen).
      * Satzzeichen gehören **außerhalb** der KaTeX-Dollarzeichen.
          * **KORREKT:** `...sind disjunkt, wenn $M \\cap N = \\emptyset$ gilt.`
          * **FALSCH:** `...sind disjunkt, wenn $M \\cap N = \\emptyset.$`

---

*(Beginne jetzt mit Schritt 1)*
