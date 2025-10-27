
# 🛠️ Technische Analyse: Importformat-Analyse – Anki 

---

**Primärquelle:**  
🌐 [Anki Manual – Importing](https://docs.ankiweb.net/importing/intro.html?highlight=import#importing) (Stand 03.06.2024)

---

## 🔹 1. Welche Dateiformate werden unterstützt?
| 🗂️ Formattyp | 📄 Dateiendung | 🧩 Beschreibung | 🔗 Offizielle Quelle |
|--------------|----------------|----------------|----------------------|
| 🧱 **Anki-Paket** | `.apkg` | Standardformat für den Austausch einzelner Decks inkl. Karten, Medien und Lernstatus. | [Importing](https://docs.ankiweb.net/importing/intro.html?highlight=import#importing) |
| 🗃️ **Anki-Collection-Paket** | `.colpkg` | Vollständige Sammlung (Decks, Notetypen, Statistiken, Medien). ⚠️ Überschreibt die bestehende Sammlung. | [Packaged Decks](https://docs.ankiweb.net/importing/packaged-decks.html) |
| 📑 **Textdateien (CSV / TSV / TXT)** | `.csv`, `.txt`, `.tsv` | UTF-8-kodierte Textdateien mit Komma-, Tab- oder Semikolon-Trennung. Jede Zeile = eine Karte. | [Importing](https://docs.ankiweb.net/importing/intro.html?highlight=import#importing) |
| 🗄️ **Mnemosyne-Datenbank** | `.db` | Import von Lernkarten aus Mnemosyne-2.0. | [Importing](https://docs.ankiweb.net/importing/intro.html?highlight=import#importing) |
| 💾 **SuperMemo-XML** | `.xml` | Import von SuperMemo-Karten (XML-Export). | [Importing](https://docs.ankiweb.net/importing/intro.html?highlight=import#importing) |

---

## ⚙️ 2. Offizielle Tools & APIs

| 🧰 Tool / Schnittstelle | 💡 Beschreibung | 🔗 Offizielle Quelle |
|------------------------|----------------|----------------------|
| 🖥️ **Anki GUI-Importer** | Direkt in der App (`Datei → Importieren`). Unterstützt alle offiziellen Formate. | [Importing](https://docs.ankiweb.net/importing/intro.html?highlight=import#importing) |
| 🔗 **AnkiConnect API (Add-on)** | Automatisierung via Python, Web oder andere Apps. Funktionen: `importPackage`, `addNote`, `findNotes`. | [AnkiConnect](https://foosoft.net/projects/anki-connect) |
| 💻 **Anki GitHub Repository** | Offizielle Implementierung der Importlogik (`importing.py`). Teil des Open-Source-Quellcodes. | [GitHub](https://github.com/ankitects/anki) |

---

## 🧠 3. Wichtige technische Hinweise

| ⚠️ Aspekt | 🧾 Beschreibung | 🔗 Offizielle Quelle |
|------------|----------------|----------------------|
| 🔤 **Kodierung** | Textdateien müssen UTF-8-kodiert sein, sonst Importfehler. | [Importing](https://docs.ankiweb.net/importing/intro.html?highlight=import#importing) |
| 📊 **Feldanzahl** | Jede Zeile einer Textdatei muss die gleiche Anzahl an Feldern wie die erste Zeile haben. | [Importing](https://docs.ankiweb.net/importing/intro.html?highlight=import#importing) |
| 🖼️ **Medienhandling** | Bilder, Audio, Video werden nur über `.apkg` oder `.colpkg` automatisch importiert. | [Packaged Decks](https://docs.ankiweb.net/importing/packaged-decks.html) |
| 💥 **Datenüberschreibung** | `.colpkg` überschreibt die gesamte Sammlung – Vorsicht bei bestehenden Daten! | [Packaged Decks](https://docs.ankiweb.net/importing/packaged-decks.html) |

---

## 🚫 4. Nicht unterstützte oder inoffizielle Formate

| 📁 Format | 🚫 Status | 💬 Begründung |
|-----------|-----------|---------------|
| JSON | ❌ Nicht offiziell unterstützt | Nur von Dritt-Tools verwendet, keine offizielle Spezifikation. |
| XML (außer SuperMemo) | ❌ Nicht allgemein unterstützt | Nur SuperMemo-XML ist offiziell dokumentiert. |
| Excel (`.xlsx` / `.xls`) | ❌ Nicht unterstützt | Muss zuerst als UTF-8-CSV exportiert werden. |

---

## ✅ Fazit – Offizielle Information

📦 **Offiziell unterstützte Formate:**  
`.apkg` | `.colpkg` | `.csv` / `.txt` / `.tsv` | `.db` | `.xml` (SuperMemo)

⚠️ **Nicht unterstützt:** JSON, Excel, allgemeine XML- oder SQL-Formate

🔧 **Automatisierung / API:** Nur über AnkiConnect Add-on möglich

🌐 **Verlässlichste Quelle:** [https://docs.ankiweb.net/](https://docs.ankiweb.net/)
---


# 🧠 Technische Spezifikation: Quizlet-Importformat

---

## 1️⃣ Unterstützte Import-Formate

### 📄 Offizielle Angaben
Gemäß der offiziellen Hilfe von Quizlet:  
- Beim Erstellen eines Sets auf der Website: *Create → Import* → Inhalte einfügen.  
  🔗 Quelle: [help.quizlet.com – Creating sets by importing content](https://help.quizlet.com/hc/en-us/articles/360029977151-Creating-sets-by-importing-content?utm_source=chatgpt.com)  
- Formatregeln:  
  > „Separate terms and definitions with a **comma, tab, or dash**. Separate rows with a **semicolon or new line**.“  
- Nur Web-Import ist möglich:  
  > „You can currently only import flashcard sets **on the website**.“  
- Keine offizielle Unterstützung für **JSON**, **XML**, **GIFT**, **CSV-Dateiuploads**.

---

### 💡 Schlussfolgerung – unterstützte Formate

| Format | Unterstützung durch Quizlet | Hinweise |
|:--|:--:|:--|
| **Plain Text** (Term / Definition) | ✅ Ja – offiziell | Textblock mit Trennzeichen |
| **CSV / TSV Dateiupload** | ❌ Nein | Kein Upload vorgesehen |
| **JSON** | ❌ Nein | Nicht erwähnt |
| **XML** | ❌ Nein | Nicht erwähnt |
| **GIFT** (z. B. Moodle) | ❌ Nein | Nicht unterstützt |

---

### ⚙️ Technische Anforderungen für den Import-Text
Damit ein Textblock korrekt importiert wird:
- Jede Karte = eine Zeile oder durch Semikolon getrennt.  
- Term und Definition → getrennt durch **Komma (,)**, **Tabulator (\t)** oder **Bindestrich (-)**.  
- Empfohlenes Encoding: **UTF-8**.  
- Keine Unterstützung für eingebettete Medien (z. B. Bilder oder Audio).  

---

## 2️⃣ Offizielle Import-Tools oder APIs

### 🖥️ Import über das Web-Interface
- Nur via Browser-UI: Einloggen → Neues Set → „Import“ → formatierten Text einfügen.  
  🔗 Quelle: [help.quizlet.com – Importing content](https://help.quizlet.com/hc/en-us/articles/360029977151-Creating-sets-by-importing-content?utm_source=chatgpt.com)

### 🔧 API-Status
- Die frühere Quizlet API wird **nicht mehr unterstützt**; neue API-Keys werden nicht ausgegeben.  
  🔗 Quelle: [stackoverflow.com – Quizlet API not available](https://stackoverflow.com/questions/60425101/quizlet-api-not-available?utm_source=chatgpt.com)  
  > „They are no longer supporting the Quizlet API … and are not currently issuing any new API keys.“  
- Fazit: **Kein offizieller API-Import mehr möglich.**

---

##  Zusammenfassung 🧾
- ✅ **Offiziell unterstützt:** Textblöcke mit Trennzeichen (, \t oder -).  
- ⚙️ **Nicht unterstützt:** Dateiuploads (JSON, XML, CSV, GIFT).  
- 🌐 **Kein API-Zugriff:** Import nur über Web-UI.  
- 💡 **Empfehlung:** Exportieren Sie einen UTF-8 Textblock, damit Nutzer ihn in Quizlet einfügen kann.  

---


## 3️⃣ Beispiel-Dateien / Textblöcke analysieren

### 📘 Beispiel-Textblock (laut offizieller Angabe)
> „Separate terms and definitions with a comma, tab, or dash.  
> Separate rows with a semicolon or new line.“  
> 🔗 [help.quizlet.com – Creating sets by importing content](https://help.quizlet.com/hc/en-us/articles/360029977151-Creating-sets-by-importing-content?utm_source=chatgpt.com)

#### 🧩 Beispiel 1 – Komma-getrennt

Begriff1,Definition1
Begriff2,Definition2
Begriff3,Definition3

#### 🧩 Beispiel 2 – Tabulator-getrennt

Begriff1<TAB>Definition1
Begriff2<TAB>Definition2
Begriff3<TAB>Definition3


#### 🧩 Beispiel 3 – Mit Bindestrich

Begriff1 - Definition1
Begriff2 - Definition2
Begriff3 - Definition3


---

### ⚙️ Empfohlene Spezifikation für Datei-Erzeugung
- **Dateiformat:** UTF-8 kodierte Textdatei (`.txt`)  
- **Zeilentrennung:** `\n` (LF) oder `\r\n` (CRLF)  
- **Trennzeichen zwischen Term und Definition:** Komma, Tabulator oder Bindestrich  
- **Zeilenweise Struktur:** Eine Karte = eine Zeile  
- **Escape-Regeln:** Falls Term/Definition das Trennzeichen enthält → Einträge in Anführungszeichen setzen  
- **Import-Vorgehen:**  
  1. Text in Datei öffnen  
  2. Inhalt kopieren  
  3. In Quizlet „Import“-Feld einfügen  
  4. Passenden Delimiter auswählen  
  5. Import starten  

---

## 📄 Beispiel-Datei `quizlet_import_example.txt`

Hauptstadt von Deutschland,Berlin
Zweitgrößte Stadt Deutschlands,Hamburg
Amtssprache in Spanien,Spanisch
Währung in Japan,Yen
Größter Planet im Sonnensystem,Jupiter

✅ Diese Datei wäre vollständig kompatibel mit dem offiziellen Quizlet-Importfeld  
(Trennzeichen: Komma · Zeilenende: LF · Encoding: UTF-8).

---

## 📅 Wissensstand

**Knowledge-Cutoff:** Juni 2024 

---

*"Technische Spezifikation: Quizlet-Importformat" mit Unterstützung von ChatGPT recherchiert.*

---

# 📚 Datenstruktur in Anki – Übersicht

---

## 1️⃣ Struktur von Fragen
In Anki heißen „Fragen“ **Karten (Cards)**, die auf **Notizen (Notes)** basieren.

### 📝 Note (Notiz)
- Grundlegende Einheit, die mehrere Karten erzeugen kann  
- Besteht aus **Felder (Fields)**  

### 📄 Fields (Felder)
- Textfelder wie **Front**, **Back**, **Beispiel**, **Kategorie**  
- Jede Karte zieht Informationen aus einem oder mehreren Feldern  

### 💳 Card (Karte)
- Wird aus einer Note abgeleitet  
- Nutzt ein **Kartentemplate**, das Front und Back formatiert  

--- 

## 2️⃣ Speicherung von Antwortoptionen
- ❌ Anki unterstützt **kein natives Multiple-Choice**  
- ✅ Workarounds:  
  - Alle Optionen in einem Feld speichern (durch Kommas getrennt)  
    Beispiel: `Optionen: Berlin, Paris, Rom, Madrid`  
  - Add-ons für Multiple-Choice nutzen („Multiple Choice for Anki“)  
  - Cloze-Karten für Lückentexte:  
    `Die Hauptstadt von Frankreich ist {{c1::Paris}}.`  

- **Hinweis:** Intern wird die richtige Antwort **als Text im Feld** gespeichert  

**Quellen:** Anki-Handbuch, Heise

---

## 3️⃣ Pflichtfelder vs. optionale Felder
- **⚠️ Pflichtfelder:** Mindestens ein Feld für **Front/Back** muss ausgefüllt sein  
- **✅ Optionale Felder:** Zusätzliche Felder (z. B. „Beispiel“, „Quelle“, „Kategorie“) können leer bleiben  
- Beim Import prüft Anki nur die Pflichtfelder  

**Quellen:** Anki-Handbuch, AMBOSS

---

## 4️⃣ Maximale Anzahl Antwortoptionen
- Standard-Anki: **keine Grenze** (Multiple-Choice nicht nativ)  
- Praktisch bei Add-ons oder selbstgebauten Multiple-Choice-Karten: **3–5 Optionen pro Frage** ✅  
- Praktisch gilt: 
Bei mehr als **10-12 Optionen** wird die Karte unübersichtlich und schwer lesbar (gerade auf Mobilgeräten)

**Quellen:** Anki-Handbuch, Heise

---

## 5️⃣ Zeichenlimits
- **Front/Back-Felder:** keine harte Grenze, mehrere Tausend Zeichen möglich  
- **Praktische Empfehlungen:**  
  - ✏️ **Front:** 200–500 Zeichen für schnelle Wiederholung  
  - 📖 **Back:** mehrere Tausend Zeichen für ausführliche Erklärungen  
  - ➕ **Zusätzliche Felder:** beliebig, solange sie lesbar bleiben  

- Intern speichert Anki Felder als Text in einer **SQLite-Datenbank** (theoretisches Limit: ca. 2 GB pro Feld)  

**Quellen:** Anki-Handbuch, AMBOSS, Ankizin

---

# 🧩 Technische Spezifikation – Quizlet-Export

---

## 📦 Grundprinzip

- Der Export erfolgt als **Plain-Text**.  
- Jede **Zeile entspricht einer Karte**.  
- Jede Karte besteht aus **zwei Spalten**: „**Term**“ und „**Definition**“.  
- Der **Export-Dialog** erlaubt, Trennzeichen und Reihenfolge zu bestimmen.  
- ⚠️ **Bilder werden nicht exportiert** („Image exports aren’t currently available due to copyright restrictions“).

🔗 **Quelle:** [Quizlet Help Center – *Exporting your sets*](https://help.quizlet.com/hc/en-us/articles/360034345672-Exporting-your-sets)

---

## 🧱 Struktur pro Karte

- **Linke Spalte →** `term` (Begriff oder Frage)  
- **Rechte Spalte →** `definition` (Antwort oder Erklärung)  
- 🔹 **Trennzeichen:** Tabulator (`\t`)  
- 🔹 **Zeilenende:** `\n` (neue Karte)  
- Beide Felder sind erforderlich.

**Beispiel:**
Photosynthese\tUmwandlung von Lichtenergie in chemische Energie\n
ATP\tEnergieüberträger der Zelle\n

🔗 **Quelle:** [Quizlet Help Center – *Importing your sets*](https://help.quizlet.com/hc/en-us/articles/360034652111-Importing-your-sets)  
*(Der Import-Artikel beschreibt dieselbe Struktur, die auch der Export verwendet.)*

---

## 🧾 Pflichtfelder vs. optionale Felder

| Typ | Feld | Beschreibung |
|------|-------|----------------|
| ✅ Pflicht | **term** | Nicht leer |
| ✅ Pflicht | **definition** | Nicht leer |
| ⚙️ Optional / nicht exportiert | Bilder, Audio, Rich-Text | Werden **nicht** exportiert |

> 📎 Erweiterte Felder wie Fragetypen, Tags oder Formatierungen werden im Export **nicht unterstützt**.

🔗 **Quelle:** [Quizlet Help Center – *Exporting your sets*](https://help.quizlet.com/hc/en-us/articles/360034345672-Exporting-your-sets)

---

## 🎯 Antwortoptionen

- Der Export enthält **nur Term + Definition**.  
- ❌ Keine Multiple-Choice- oder Alternativantworten.  
- Quizlet erzeugt Testformate intern — sie werden **nicht im Export gespeichert**.

🔗 **Quelle:** [Quizlet Help Center – *Exporting your sets*](https://help.quizlet.com/hc/en-us/articles/360034345672-Exporting-your-sets)

---

## 🚫 Maximale Anzahl Antwortoptionen

- Nicht anwendbar → **keine Antwortoptionen** im Exportformat.

---

## 🔠 Zeichenlimits

- Quizlet nennt **keine offiziellen Zeichenlimits** für Export oder Felder.  
- Du kannst aus technischer Vorsicht **≈ 2000 Zeichen pro Feld** (`term`, `definition`) als Obergrenze definieren.  
- 📌 Hinweis: Dieser Wert dient nur der Systemkompatibilität, **nicht** als offizielles Limit.

🔗 **Quelle:** Keine offizielle Angabe auf help.quizlet.com (Stand: 2025-10)

---

## 📋 Zusammenfassung (Regel-Checkliste)

| Nr. | Regel | Symbol |
|-----|--------|:------:|
| 1️⃣ | Format = Plain-Text | 📄 |
| 2️⃣ | Karte = eine Zeile | ↩️ |
| 3️⃣ | Spalten: Term / Definition | 🔀 |
| 4️⃣ | Trennzeichen: Tab `\t`; Zeilenumbruch `\n` | 🔹 |
| 5️⃣ | Pflichtfelder: beide nicht leer | ✅ |
| 6️⃣ | Keine Bilder/Audio/Formatierungen | ⚠️ |
| 7️⃣ | Keine Antwortoptionen / MC-Daten | ❌ |
| 8️⃣ | Zeichenlimits nicht offiziell → ca. ≤ 2000 Zeichen | 🔠 |

---

<html>
<body>
<!--StartFragment--><html><head></head><body>
<hr>
<h3>🧮 <strong>1. Werden mathematische Formeln unterstützt?</strong></h3>
<p>Ja — Anki unterstützt mathematische Formeln mittels LaTeX bzw. MathJax. Laut dem Handbuch von Anki („Math &amp; Symbols“) kann man unter „Generate LaTeX images“ LaTeX aktivieren. (Stand: Dokumentation zuletzt aktualisiert 2024 oder früher) (<a href="https://docs.ankiweb.net/math.html?utm_source=chatgpt.com" title="Math &amp; Symbols - Anki Manual">docs.ankiweb.net</a>)<br>
→ <strong>Aktualität:</strong> geprüft im Handbuch (Stand mindestens Mitte 2024)<br>
→ Damit ist klar: Ja, Formeln unterstützt.</p>
<hr>
<h3>✍️ <strong>2. Welche Syntax wird verwendet?</strong></h3>
<ul>
<li>
<p>Für MathJax in Anki werden typischerweise die Delimiter <code inline="">\( … \)</code> für Inline-Formeln und <code inline="">\[ … \]</code> für Display-Formeln verwendet. (<a href="https://forums.ankiweb.net/t/mathjax-not-displaying-correctly-in-anki-desktop-v24-06-3-inconsistent-rendering-issue/50238?utm_source=chatgpt.com" title="MathJax Not Displaying Correctly in Anki Desktop (v24.06.3)">Anki Forums</a>)</p>
</li>
<li>
<p>Für klassische LaTeX-Bild-Erzeugung (via installiertem LaTeX) gibt es in den Anki-Einstellungen eine Option „Generate LaTeX images“. (<a href="https://forums.ankiweb.net/t/latex-latex-doesnt-work/46523?utm_source=chatgpt.com" title="[latex][/latex] doesn't work - Help - Anki Forums">Anki Forums</a>)</p>
</li>
<li>
<p>Weitere Varianten: Einige Quellen nennen <code inline="">$ … $</code> und <code inline="">$$ … $$</code>, aber laut offiziellen Aussagen ist dies in manchen Fällen <strong>nicht empfohlen</strong> bei Anki-Importen. (<a href="https://forums.ankiweb.net/t/mathjax-breaks-with-txt-import/54903?utm_source=chatgpt.com" title="MathJax &quot;breaks&quot; with .txt import - Help - Anki Forums">Anki Forums</a>)<br>
→ <strong>Aktualität:</strong> Hinweise stammen aus Foren 2024/25, Handbuch ebenfalls aktuell (Stand 2024)<br>
→ Damit: Syntax klar definiert.</p>
</li>
</ul>
<hr>
<h3>🔄 <strong>3. Inline vs. Display-Formeln</strong></h3>

Typ | Beschreibung | Syntax Beispiel
-- | -- | --
Inline | Teil des Textflusses, kleiner | \( E = mc^2 \)
Display | Eigene Zeile, zentriert, größer dargestellt | \[\int_0^\infty e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}\]


<p>Diese Unterscheidung wird von Anki-Handbuch und Nutzern bestätigt. (<a href="https://geoffruddock.com/anki-math-typesetting/?utm_source=chatgpt.com" title="Typesetting math equations with Anki - Geoff Ruddock">geoffruddock.com</a>)<br>
→ <strong>Aktualität:</strong> Stand Handbuch (2024) + Blogbeiträge früher<br>
→ Damit: Inline vs Display klar.</p>
<hr>
<h3>🧪 <strong>4. Beispiel zum Testen</strong></h3>
<p><strong>Inline:</strong></p>
<pre><code>\( E = mc^2 \)
</code></pre>
<p><strong>Display:</strong></p>
<pre><code>\[
\int_0^\infty e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}
\]
</code></pre>
<p>Diese Beispiele entsprechen der gängigen LaTeX/MathJax-Notation, wie sie in Anki verwendet wird.<br>
→ <strong>Aktualität:</strong> allgemein gültige Notation, aktuell.<br>
→ Damit: Du kannst diese direkt ausprobieren.</p>
<hr>
<h3>⚙️ <strong>5. Tipps &amp; Hinweise</strong></h3>
<ul>
<li>
<p>Wenn du klassische LaTeX-Bild‐Erzeugung nutzt: Stelle sicher, dass in Einstellungen „Generate LaTeX images“ aktiviert ist. In neueren Versionen wurde diese Option verändert. (<a href="https://forums.ankiweb.net/t/latex-latex-doesnt-work/46523?utm_source=chatgpt.com" title="[latex][/latex] doesn't work - Help - Anki Forums">Anki Forums</a>)</p>
</li>
<li>
<p>Falls Formeln nicht angezeigt werden: Prüfe, ob du <strong>MathJax</strong> statt LaTeX verwendest — viele Nutzer berichten, dass MathJax-Syntax zuverlässiger funktioniert auf mehreren Geräten. (<a href="https://www.reddit.com/r/Anki/comments/xex68d/use_mathjax_on_desktop_mobile_and_web_reliably/?utm_source=chatgpt.com" title="Use MathJax on Desktop, Mobile, and Web reliably : r/Anki - Reddit">Reddit</a>)</p>
</li>
<li>
<p>Beim Import von Textdateien (.txt) mit Formeln: Achte darauf, dass du <strong>nicht</strong> die internen Tags wie <code inline="">&lt;anki-mathjax&gt;</code> verwendest, sondern die offiziellen Delimiter <code inline="">\(...\)</code> oder <code inline="">\[…\]</code>. Beispiel: ein Nutzer schrieb am 26. Jan 2025, dass <code inline="">&lt;anki-mathjax&gt;</code> nicht gilt beim Import. (<a href="https://forums.ankiweb.net/t/mathjax-breaks-with-txt-import/54903?utm_source=chatgpt.com" title="MathJax &quot;breaks&quot; with .txt import - Help - Anki Forums">Anki Forums</a>)</p>
</li>
</ul>
<hr>

</body></html><!--EndFragment-->
</body>
</html>

[1]: https://docs.ankiweb.net/math.html?utm_source=chatgpt.com "Math & Symbols - Anki Manual"
[2]: https://forums.ankiweb.net/t/mathjax-not-displaying-correctly-in-anki-desktop-v24-06-3-inconsistent-rendering-issue/50238?utm_source=chatgpt.com "MathJax Not Displaying Correctly in Anki Desktop (v24.06.3)"
[3]: https://forums.ankiweb.net/t/latex-latex-doesnt-work/46523?utm_source=chatgpt.com "[latex][/latex] doesn't work - Help - Anki Forums"
[4]: https://forums.ankiweb.net/t/mathjax-breaks-with-txt-import/54903?utm_source=chatgpt.com "MathJax \"breaks\" with .txt import - Help - Anki Forums"
[5]: https://geoffruddock.com/anki-math-typesetting/?utm_source=chatgpt.com "Typesetting math equations with Anki - Geoff Ruddock"
[6]: https://www.reddit.com/r/Anki/comments/xex68d/use_mathjax_on_desktop_mobile_and_web_reliably/?utm_source=chatgpt.com "Use MathJax on Desktop, Mobile, and Web reliably : r/Anki - Reddit"

---

### 🧮 **1. Werden mathematische Formeln (LaTeX) unterstützt?**

Kurzfassung: **Quizlet unterstützt keine native LaTeX-Syntax.**
Laut mehreren Quellen und Nutzerberichten kann Quizlet keine LaTeX-Renderung durchführen. Das bedeutet, dass Eingaben wie `\( E = mc^2 \)` oder `\[\int_0^\infty …\]` nicht automatisch als mathematische Formeln dargestellt werden.
Quelle: [[Matheducators StackExchange, 2023](https://matheducators.stackexchange.com/questions/26967/alternative-to-quizlet-live-that-supports-latex-formulas?utm_source=chatgpt.com)](https://matheducators.stackexchange.com/questions/26967/alternative-to-quizlet-live-that-supports-latex-formulas?utm_source=chatgpt.com)
→ **Aktualität:** Stand Oktober 2023
→ **Fazit:** Direkte LaTeX-Unterstützung ist in Quizlet derzeit nicht verfügbar.

---

### ✍️ **2. Welche Syntax bzw. Vorgehensweise kann verwendet werden?**

Da keine native LaTeX-Renderung vorhanden ist, gibt es nur **indirekte Lösungen**:

* Nutzerberichte zeigen, dass bei der Eingabe von LaTeX-Code dieser nicht korrekt angezeigt oder beim Speichern verändert wird.
  Quelle: [[Reddit – r/LaTeX, Diskussion von 2022](https://www.reddit.com/r/LaTeX/comments/ika7tg/latex_in_quizlet_converts_to_symbol_when_editing/?utm_source=chatgpt.com)](https://www.reddit.com/r/LaTeX/comments/ika7tg/latex_in_quizlet_converts_to_symbol_when_editing/?utm_source=chatgpt.com)
* Eine häufig genutzte Alternative besteht darin, Formeln extern (z. B. in LaTeX oder MathType) zu erstellen, als **Bild (PNG oder SVG)** zu exportieren und dieses in Quizlet als Medieninhalt einzufügen.
  Quelle: [[Quizlet-Hilfeseite, 2023](https://quizlet.com/615581429/how-to-create-a-quizlet-with-math-flash-cards/?utm_source=chatgpt.com)](https://quizlet.com/615581429/how-to-create-a-quizlet-with-math-flash-cards/?utm_source=chatgpt.com)

→ **Aktualität:** Nutzererfahrungen und Dokumentationen aus 2021 – 2023
→ **Schlussfolgerung:** Quizlet bietet keine speziellen LaTeX-Delimiter wie `\( … \)` oder `\[ … \)`, sondern erlaubt lediglich Bild-Uploads als Ersatzlösung.

---

### 🔄 **3. Inline- vs. Display-Formeln**

Da kein automatisches LaTeX-Rendering erfolgt, existiert auch keine Unterscheidung zwischen Inline- und Display-Formeln im technischen Sinn.
Formeln können lediglich als **eingebettete Bilder** eingefügt werden:

* Inline-ähnlich: kleinere Formel-Bilder, im Text platziert
* Display-ähnlich: größere, zentrierte Formel-Bilder

→ **Aktualität:** basierend auf Workarounds aus Foren 2022 – 2024
→ **Hinweis:** Diese Lösung hängt stark von Bildschirmgröße und Endgerät ab; die Darstellung kann variieren.

---

### 🧪 **4. Beispiel zum Testen**

Formeln können über externe LaTeX-Editoren oder Online-Generatoren (z. B. [[latex.codecogs.com](https://latex.codecogs.com/)](https://latex.codecogs.com)) erstellt werden.
Beispielhafte Formeln:

* Inline: `E = mc^2`
* Display: `\displaystyle \int_0^\infty e^{-x^2}\,dx = \frac{\sqrt\pi}{2}`

Diese können als PNG oder SVG exportiert und anschließend in Quizlet hochgeladen werden.
→ **Aktualität:** Methode bestätigt in Nutzerforen 2022 – 2023
→ **Einschränkung:** Keine dynamische Skalierung oder Anpassung durch Quizlet selbst.

---

### ⚙️ **5. Hinweise und Empfehlungen**

* Bei umfangreicher mathematischer Notation ist Quizlet **nicht optimal geeignet**, da keine native LaTeX-Integration existiert.
  Quelle: [[Matheducators StackExchange, 2023](https://matheducators.stackexchange.com/questions/26967/alternative-to-quizlet-live-that-supports-latex-formulas?utm_source=chatgpt.com)](https://matheducators.stackexchange.com/questions/26967/alternative-to-quizlet-live-that-supports-latex-formulas?utm_source=chatgpt.com)
* Bilder sollten in ausreichender Auflösung hochgeladen werden, um Lesbarkeit auf Mobilgeräten sicherzustellen.
* Vor der Nutzung in Unterrichts- oder Prüfungsvorbereitungskontexten empfiehlt sich eine Darstellungskontrolle auf verschiedenen Geräten (Desktop, Tablet, Smartphone).
* Für mathematisch orientierte Lernsets bieten sich Alternativen wie **Anki** oder **RemNote** an, da diese LaTeX nativ unterstützen.

→ **Aktualität:** Angaben überprüft anhand von Quellen aus 2022 – 2024
→ **Gesamtfazit:** Quizlet erlaubt derzeit keine direkte Eingabe und automatische Darstellung von LaTeX-Formeln; nur Bild-basierte Workarounds sind möglich.

---

# TECH SPEC — **Metadaten-Support** (Import) für **Anki** & **Quizlet**

> **Scope:** Umsetzung von *Phase 2 · 2.1 Import-Format-Analyse* **nur** für Abschnitt **4. Metadaten-Support**. Fokus: Wie können Metadaten unserer MC‑Test‑App beim **Import** in Anki/Quizlet erhalten/abgebildet werden?

## 🧭 Legende

- ✅ = nativ unterstützt
- ⚠️ = nicht nativ; **Workaround/Mapping** möglich
- ❌ = nicht unterstützt

## 🧩 Unsere kanonischen Metadaten (Quelle → Zielmapping)

| Metadatum (Quelle) | Beschreibung                                     |
| ------------------ | ------------------------------------------------ |
| **difficulty**     | Schwierigkeitsgrad (Skala 1–5)                   |
| **weight**         | Gewichtung in der Bewertung (0–1 oder %)         |
| **topics**         | Themen/Tags/Kategorien (hierarchisch möglich)    |
| **explanation**    | Erklärung/Feedback zur Frage oder Lösung         |
| **media**          | Bilder/Audio/Video, pro Frage oder Antwortoption |
| **mini\_glossary** | Kurze Begriffserklärungen (falls vorhanden)      |

---

## 🧠 **Anki** — Metadaten-Support (Import)

| Metadatum          | Support | Mapping-Empfehlung                                                                                                                                                               |
| ------------------ | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **difficulty**     | ⚠️      | Als **Tag** (`diff:3`) **oder** eigenes **Feld** `Difficulty` in benutzerdefiniertem Notetyp (z. B. *MC‑Card*). Anzeige optional im Back‑Template.                               |
| **weight**         | ⚠️      | **Tag** (`w:0.7`) **oder** Feld `Weight`. Für Auswertungen kann ein Add‑on/Export genutzt werden.                                                                                |
| **topics**         | ✅       | **Tags** in Anki (mehrere, Leerzeichen‑separiert). Hierarchien per `::` (z. B. `Mathe::Analysis`).                                                                               |
| **explanation**    | ✅       | Feld `Explanation` → in **Back‑Template** oder als `Extra` anzeigen.                                                                                                             |
| **media**          | ✅       | Bild/Audio als **Medienanhang** im `.apkg`; im Feld mit HTML (`<img src="file.png">`) oder `[sound:file.mp3]`. Beim CSV‑Import zuvor Medien in `collection.media` bereitstellen. |
| **mini\_glossary** | ⚠️      | Als zusätzl. Feld `Glossary` **oder** separate Notizen pro Begriff; Verknüpfung via Tags (`glossary`).                                                                           |

**Hinweise/Constraints:**

- CSV‑Import kann **Tags** aus einer Spalte übernehmen; **Note Type** mit Feldern `Front`, `Back`, `Explanation`, `Difficulty`, `Weight`, `Glossary` empfohlen.
- Für robuste Medienübernahme **.apkg‑Export** bevorzugen (Media‑Packaging inklusive).

---

## 📚 **Quizlet** — Metadaten-Support (Import)

> *Quizlet‑Import akzeptiert i. d. R. ****CSV/TSV**** mit ****Term**** & ****Definition****. Import von Bildern über Datei ist nicht vorgesehen; Bilder werden im UI manuell oder über API/Plus ergänzt.*

| Metadatum          | Support | Mapping-Empfehlung                                                                                                                                                                                                                   |
| ------------------ | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **difficulty**     | ❌       | In **Definition** als Präfix (`[D3] …`) oder in **Set‑Beschreibung** notieren. Alternativ pro Term als Suffix z. B. `— Diff:3/5`.                                                                                                    |
| **weight**         | ❌       | Wie oben: Präfix/Suffix in **Definition** (`(W:0.7)`). Bei bedarf zusätzlich in Set‑Beschreibung dokumentieren.                                                                                                                      |
| **topics**         | ⚠️      | **Set‑Beschreibung**: `#Analysis #LineareAlgebra`; je Term optional **Inline‑Hashtags** am Ende der Definition.                                                                                                                      |
| **explanation**    | ⚠️      | An **Definition** anhängen: `Antwort … \n\nErklärung: …`. (Leerzeile + Label).                                                                                                                                                       |
| **media**          | ⚠️      | **Nicht via CSV**. Workarounds: 1) Nach Import **manuell** Bilder je Term hinzufügen (Plus), 2) **API‑basierter Set‑Erstellungs‑Flow** mit Bild‑Upload/Zuordnung. Als Minimal‑Fallback **Bild‑URL** am Ende der Definition notieren. |
| **mini\_glossary** | ⚠️      | Als **separates Set** „Glossary – Kurs X“ importieren **oder** in der Set‑Beschreibung bündeln; Verlinkung über gemeinsamen *Class* oder Titelkonvention.                                                                            |

**Hinweise/Constraints:**

- Längere Definitionen sind erlaubt, dennoch kurze Präfix/Suffix‑Konventionen bevorzugen, um Lesbarkeit auf Mobilgeräten zu wahren.
- Einheitliche **Konventionen** wichtig (z. B. `[D3][W0.7] Antwort … \n\nErklärung: …`).

---

## 🔁 **Einheitliche Mapping‑Konventionen** (Quell‑→Ziel)

**Tags/Topics**

- `topics` → **Anki:** Tags (`Fach::Thema`).
- `topics` → **Quizlet:** `#Fach #Thema` in **Set‑Beschreibung** *und optional* pro Term (am Ende der Definition).

**Difficulty/Weight**

- **Anki:** Tags `diff:1..5`, `w:0..1` **oder** Felder `Difficulty`/`Weight`.
- **Quizlet:** Präfixe in Definition, z. B. `[D3][W0.7]`.

**Explanation**

- **Anki:** Feld `Explanation` → Back‑Template.
- **Quizlet:** Definition mit Abschnitt `Erklärung:` nach Leerzeile.

**Media**

- **Anki:** Medien anhängen und in Feld referenzieren.
- **Quizlet:** Manuell ergänzen *oder* per API; als Fallback **URL** in Definition.

**Mini‑Glossary**

- **Anki:** eigenes Feld/Notiztyp + Tag `glossary`.
- **Quizlet:** separates Glossar‑Set, im Kurs/der Class verlinken.

---

## 🧱 Kompakte **Metadaten‑Mapping‑Tabelle**

| Metadatum      | Anki (Empfehlung)                                 | Quizlet (Empfehlung)                                              |
| -------------- | ------------------------------------------------- | ----------------------------------------------------------------- |
| difficulty     | Tag `diff:N` **oder** Feld `Difficulty`           | Präfix `[D{N}]` in Definition oder Set‑Beschreibung               |
| weight         | Tag `w:X` **oder** Feld `Weight`                  | Präfix `[W{X}]` in Definition                                     |
| topics         | Tags mit Hierarchie `Fach::Thema`                 | Hashtags `#Fach #Thema` (Set‑Beschreibung + optional term‑inline) |
| explanation    | Feld `Explanation` → Back‑Template                | Abschnitt `\n\nErklärung: …` in Definition                        |
| media          | Medien im `.apkg` + `<img>`/`[sound:…]`           | manuell/API; Fallback: URL am Ende der Definition                 |
| mini\_glossary | Feld `Glossary` **oder** separate Glossar‑Notizen | Separates Glossar‑Set, per Titel/Klasse verknüpfen                |

---

## ✅ **Implementierungs‑Hinweise (MVP)**

1. **Exporter** erhält **Optionen**: `include_difficulty`, `include_weight`, `topics_as_tags`, `explanation_mode` (`field|inline`), `media_strategy` (`package|url|none`).
2. **Anki‑Preset**: Note‑Type `MC-Card` mit Feldern `Front, Back, Explanation, Difficulty, Weight, Glossary`; Export **.apkg** bevorzugt.
3. **Quizlet‑Preset**: CSV mit Spalten `Term, Definition`; **Definition-Composer** fügt Präfixe/Texte gemäß Konvention ein.
4. **Consistency Linter** vor Export: prüft Länge, verbotene Zeichen, fehlende Medien, leere Erklärungen.

---

# 📘 Anki – Übersicht für Selbststudium mit Karteikarten, Limitierungen

| **Aspekt** | **Beschreibung** |
|-------------|------------------|
| **Plattform** | Open-Source, Desktop-first (Windows, macOS, Linux), mobile Version: *AnkiMobile* (iOS, kostenpflichtig) & *AnkiDroid* (Android, kostenlos) |
| **Lernprinzip** | Spaced Repetition nach dem SM2-Algorithmus (wie SuperMemo). Optimiert Wiederholungen nach Vergessenskurve. |
| **Zielgruppe** | Power-User, Studierende, medizinische / sprachliche Lernende, alle mit Fokus auf Langzeitgedächtnis |
| **Offline-Fähigkeit** | Vollständig offline nutzbar (alle Plattformen) |
| **Datenhaltung** | Lokal auf Gerät gespeichert, optional Sync via *AnkiWeb* |
| **Exportformate** | `.apkg` (komplettes Deck inkl. Medien & Kartenstruktur), `.txt` / `.csv` (reine Textdaten) |
| **Was _nicht_ exportiert wird** | - Lernstatistiken (z. B. Wiederholungsintervall, Ease Factor) werden **nicht in CSV/TXT** exportiert<br>- Einige Add-on-spezifische Felder (z. B. „Image Occlusion Enhanced“) fehlen im Standardexport |
| **Importmöglichkeiten** | `.apkg`, `.csv`, `.txt`, *Quizlet*-Import (über Add-ons wie “CrowdAnki”, “Anki-Importer”, “Quizlet2Anki”) |
| **Add-ons / Erweiterbarkeit** | Sehr hoch – über 1000 Plugins (z. B. Image Occlusion, Heatmap, Review Statistics, Syntax Highlighting, LaTeX, Audio Recorder etc.) |
| **Automatisierung / Scripting** | Python-basiert, API über *AnkiConnect* (z. B. für automatische Karteierstellung aus Notizen, PDFs, ChatGPT etc.) |
| **Workarounds / Fallbacks** | 🔹 **Cloud-Sync:** über *AnkiWeb* (kostenlos)<br>🔹 **Versionierung:** regelmäßiger Export als `.apkg`<br>🔹 **Fehlerhafte Add-ons:** im „Safe Mode“ starten<br>🔹 **Backups:** automatische tägliche Sicherung im Profilordner |
| **Breaking Changes bei Updates** | - Core-Updates können Add-ons temporär inkompatibel machen<br>- Datenformat bleibt stabil (alte `.apkg` fast immer kompatibel)<br>- Add-on-Kompatibilität prüfen nach großen Versionen (z. B. 2.1.x → 2.2.x) |
| **Datensicherheit / Datenhoheit** | Sehr hoch – lokale Speicherung, Open-Source, keine Cloudpflicht |
| **Empfohlener Workflow** | 1️⃣ Karten in Desktop-Version erstellen<br>2️⃣ Regelmäßig `.apkg`-Backups exportieren<br>3️⃣ Optional Sync mit *AnkiWeb*<br>4️⃣ Mobile Nutzung über *AnkiDroid* oder *AnkiMobile* |
| **Langfristige Stabilität** | Hoch – Open-Source-Community sichert Weiterentwicklung, stabile Dateiformate seit über 10 Jahren |

---

## 💡 Fazit

- **Stärken:** Open-Source, voll konfigurierbar, starkes Spaced-Repetition-System, 100 % Datenhoheit.  
- **Schwächen:** Etwas höhere Lernkurve, Add-on-Pflege nach Updates nötig.  
- **Empfehlung:** Ideal als Hauptplattform für langfristiges Selbststudium – kombinierbar mit Quizlet für einfache Erstellung oder gemeinsames Lernen.

---

# 📗 Quizlet – Übersicht für Selbststudium mit Karteikarten

| **Aspekt** | **Beschreibung** |
|-------------|------------------|
| **Plattform** | Kommerzielle, cloudbasierte Lernplattform mit Web-App + Mobile Apps (iOS, Android) |
| **Lernprinzip** | Karteikarten, Multiple-Choice, Lernspiele („Match“, „Gravity“), Testmodus; **Spaced Repetition** nur mit *Quizlet Plus* (Premium-Abo) |
| **Zielgruppe** | Breite Lernerschaft: Schüler:innen, Studierende, Lehrkräfte, Einsteiger |
| **Fokus / Design** | Mobile-first, intuitive Oberfläche, schnell zu bedienen, starke Community-Funktion (geteilte Sets) |
| **Offline-Fähigkeit** | Nur mit *Quizlet Plus* (kostenpflichtig) verfügbar |
| **Datenhaltung** | Cloudbasiert (keine lokale Speicherung), Synchronisation automatisch über Konto |
| **Exportformate** | Nur **Text-/CSV-Export** – limitiert: <br> - Nur Text (Frage/Antwort)<br> - Keine Bilder, Audio oder Formatierungen |
| **Was _nicht_ exportiert werden kann** | ❌ Bilder / Audio-Dateien <br> ❌ Formatierungen (z. B. Markdown, Fett, Kursiv) <br> ❌ Lernstatistiken <br> ❌ Fortschritt & Wiederholungsdaten <br> ❌ „Spaced Repetition“-Informationen (auch mit Plus) |
| **Importmöglichkeiten** | CSV-/Tab-getrennter Textimport möglich (einfacher Text), kein Anki-Import |
| **Add-ons / Erweiterbarkeit** | Keine offiziellen Add-ons, API stark eingeschränkt (viele inoffizielle Tools regelmäßig deaktiviert) |
| **Workarounds / Fallbacks** | 🔹 **Quizlet → Anki:** via Tools wie *Quizlet2Anki*, *Anki-Importer*, *Memcode Export* (häufig durch API-Änderungen betroffen)<br>🔹 **Backup:** manuell als CSV-Export sichern<br>🔹 **Screenshots** für Inhalte mit Bildern als Notlösung |
| **Automatisierung / Scripting** | Keine offizielle API mehr für Free-User (seit 2020 stark eingeschränkt) |
| **Community-Funktionen** | Sehr groß – Sets können geteilt, kopiert und durchsucht werden (öffentlich oder privat) |
| **Breaking Changes bei Updates** | ⚠️ Häufig! Quizlet ändert regelmäßig API und Exportmechanismen → viele Tools (z. B. *Quizlet2Anki*) brechen ohne Vorwarnung |
| **Datensicherheit / Datenhoheit** | Niedrig – Inhalte liegen in der Cloud, kein garantierter Vollzugriff auf eigene Daten |
| **Empfohlener Workflow** | 1️⃣ Sets online oder mobil erstellen <br> 2️⃣ Regelmäßiger CSV-Export als Backup (Text-only) <br> 3️⃣ Optional: Konvertierung in Anki für Langzeitlernen |
| **Langfristige Stabilität** | Mittel – stabile App, aber häufige Feature-Änderungen und Exportrestriktionen |
| **Kostenmodell** | - Kostenlos: Basisfunktionen, Werbung<br>- *Quizlet Plus*: Spaced Repetition, Offline-Modus, keine Werbung |

---

## 💡 Fazit

- **Stärken:** Einfach, schnell, optisch ansprechend, perfekt für gemeinsames Lernen oder schnelles Wiederholen unterwegs.  
- **Schwächen:** Eingeschränkter Export, keine Datenhoheit, häufige API-Änderungen.  
- **Empfehlung:** Ideal als *Ergänzung* zu Anki – nutze Quizlet zum schnellen Erstellen oder Teilen von Sets, exportiere regelmäßig als Text, und sichere wichtige Inhalte zusätzlich in Anki.

---

Alle KI-generierten Inhalte wurden manuell geprüft, angepasst und durch Tests validiert.
(generiert mit Chat GPT)
