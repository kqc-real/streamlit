<h2>🧩 <strong>Mapping-Tabelle – MC-Test-App → ANKI</strong></h2>

MC-Test-App Feldname | ANKI Feldname | Transformation | Fallback-Option
-- | -- | -- | --
question | Front | Keine | „Keine Frage angegeben“
correct_answer | Back | Keine | „Keine Antwort angegeben“
answers | Extra / Hint | Als kommagetrennte Liste (join(", ")) | „—“
difficulty | Tags | 1→Easy, 2→Medium, 3→Hard | „Medium“
category | Deck | Groß-/Kleinschreibung normalisieren (z. B. Mathematik → mathematik) | „Allgemein“
explanation | Extra / Notes | Markdown → HTML konvertieren | Leer lassen
id (falls vorhanden) | Note ID | Keine | Automatisch generieren



---

## 🧩 **Mapping-Tabelle – MC-Test-App → QUIZLET**

| MC-Test-App Feldname   | QUIZLET Feldname           | Transformation                       | Fallback-Option        |
| ---------------------- | -------------------------- | ------------------------------------ | ---------------------- |
| `question`             | **Term**                   | Keine                                | „N/A“                  |
| `correct_answer`       | **Definition**             | Keine                                | „N/A“                  |
| `answers`              | **Choices**                | Als Aufzählung (z. B. Bullet Points) | „—“                    |
| `difficulty`           | **Tags**                   | `1→Easy`, `2→Medium`, `3→Hard`       | „Medium“               |
| `category`             | **Set Name**               | Groß-/Kleinschreibung angleichen     | „General“              |
| `explanation`          | **Kommentar / Zusatzinfo** | Markdown → Plaintext                 | Leer lassen            |
| `id` (falls vorhanden) | **Card ID**                | Keine                                | Automatisch generieren |

---

<h2>🎨 UI-Mockup – Export nach Anki
  
*(Stand: 26. Oktober 2025)*
---
  
📍 Wo erscheint der Export-Button?

Der Export-Button befindet sich auf der Seite eines Fragensets (z. B. „Physik-Test 2025“).

Neben den Buttons „Bearbeiten“ und „Löschen“ erscheint ein Dropdown-Button „Exportieren“.

Klickt man darauf, öffnet sich ein Menü mit verschiedenen Plattformen (Anki, Quizlet).

<img width="661" height="433" alt="grafik" src="https://github.com/user-attachments/assets/e3bec551-76a8-47e3-a479-39d8114c8404" />

⚙️ Welche Optionen sieht der Nutzer?

Dialog: „Export nach Anki“

Auswahlbox für Exportziel (Anki / Quizlet / …)

Checkboxen:

✅ LaTeX-Formeln übernehmen

✅ Tags exportieren

🔲 Erklärungen hinzufügen

Button: „Export starten“

Hinweis: „Die Datei wird automatisch heruntergeladen.“

💬 Wie sieht das Feedback aus?

Bei Erfolg:

✅ „Export erfolgreich! Datei anki_export.txt wurde gespeichert.“

Bei Fehler:

❌ „Fehler: Keine Fragen im Set gefunden.“

Bei längeren Prozessen:
Fortschrittsanzeige („Export läuft… bitte warten“)


🎨 Skizze

🚀 Export-Funktionen

<img width="1024" height="1024" alt="0090845a-aa68-4dcb-ab96-1b7b194c67fc" src="https://github.com/user-attachments/assets/c8893efe-a1d7-4de3-bf99-b34651d00011" />

✅ Erfolgreicher Export

<img width="1536" height="1024" alt="f74e2e12-8388-4a56-80a8-737a4cf4f9e4" src="https://github.com/user-attachments/assets/3f77f99e-a594-49be-9c96-2f48fdd9f8e3" />

❌ Fehlgeschlagener Export / Fehler

<img width="1024" height="1024" alt="d5059619-30a9-45c9-8985-b2077087ff2e" src="https://github.com/user-attachments/assets/22662f94-d350-4a8d-961e-7fa0611999b5" />


<h2>🧭 Priorisierung & Roadmap für Export zu Anki und Quizlet
*(Stand: 27. Oktober 2025)*
  
---
  
🎯 Überblick

Ziel: Export aus der MC-Test-App in Anki und Quizlet, um Reichweite und Lernvielfalt zu erhöhen.
Beide Plattformen dienen dem Selbststudium (Spaced Repetition Learning) und decken unterschiedliche Nutzersegmente ab:

Anki → Open Source, Power User, Desktop/Offline.

Quizlet → Kommerziell, Mobile-first, Einsteigerfreundlich.

🔢 MoSCoW-Priorisierung

| Plattform   | Priorität   | Story Points (Schätzung) | Business Value                                            | Technical Effort | Risk Level | Begründung                                                                                   |
| ----------- | ----------- | ------------------------ | --------------------------------------------------------- | ---------------- | ---------- | -------------------------------------------------------------------------------------------- |
| **Anki**    | ✅ MUST HAVE | 13 SP                    | Sehr hoch (Power-User, Dozenten, Open Source Integration) | Mittel           | Niedrig    | Format klar dokumentiert (Anki .txt/.apkg), große Nutzergemeinde, einfacher CSV/Text-Export. |
| **Quizlet** | ✅ MUST HAVE | 21 SP                    | Hoch (Mainstream, Studierende, Reichweite)                | Mittel–hoch      | Mittel     | API limitiert, aber CSV-Import möglich. Relevanz hoch für Studierende, mobile Nutzung.       |


📊 Business Value Bewertung

| Kriterium                 | Anki                             | Quizlet                            |
| ------------------------- | -------------------------------- | ---------------------------------- |
| Zielgruppen-Fit           | 👨‍🏫 Dozenten, MINT-Studierende | 📱 BWL-Studierende, Erstsemester   |
| Reichweite                | Mittel                           | Hoch                               |
| Monetarisierungspotenzial | Gering (Open Source)             | Hoch (Pro-Lizenzen, Kooperationen) |
| Community-Unterstützung   | Hoch                             | Mittel                             |
| Integrationsaufwand       | Mittel                           | Hoch (API limitiert)               |
| Datenschutz/DSGVO         | Sehr gut                         | Mittel                             |


Empfehlung: Beide als MUST HAVE im ersten Entwicklungszyklus (Sprint 1), da sie verschiedene Kernzielgruppen abdecken.




Alle KI-generierten Inhalte wurden manuell geprüft, angepasst und durch Tests validiert.
(generiert mit Chat GPT)
