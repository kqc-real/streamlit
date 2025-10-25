---
# 🛠️ Technische Analyse: Importformat-Analyse – Anki 

**Primärquelle:**  
🌐 [Anki Manual – Importing](https://docs.ankiweb.net/importing/intro.html?highlight=import#importing) (Stand 03.06.2024)

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

Alle KI-generierten Inhalte wurden manuell geprüft, angepasst und durch Tests validiert.
(generiert mit Chat GPT)

---
