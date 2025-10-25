
# 🛠️ Technische Analyse: Importformat-Analyse – Anki 


---

## 🔹 1. Welche Dateiformate werden Unterstützt
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

### 💡 Schlussfolgerung – Unterstützte Formate

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



