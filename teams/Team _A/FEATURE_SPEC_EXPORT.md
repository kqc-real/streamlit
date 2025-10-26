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

Alle KI-generierten Inhalte wurden manuell geprüft, angepasst und durch Tests validiert.
(generiert mit Chat GPT)
