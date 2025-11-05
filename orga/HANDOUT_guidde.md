# Handout: User Journeys in **MC-Test-App** mit **guidde** dokumentieren

Das Tool [guidde](https://www.guidde.com/) positioniert sich als schlankes Aufnahme- und Publishing-Tool, das die Erstellung kurzer Schritt‑für‑Schritt‑Anleitungen erleichtert: direkte Bildschirm- und UI‑Aufzeichnung, einfache Nachbearbeitung (Schritttexte, Untertitel, Hervorhebungen) und die Möglichkeit, Inhalte schnell öffentlich bereitzustellen. Laut Produktseite sollen diese Features den Dokumentationsaufwand reduzieren, Wiederverwendbarkeit erhöhen und die Einarbeitungszeit neuer Teammitglieder deutlich verringern.

 Fallstudien bestätigen viele dieser Versprechen: Guidde beschleunigt die Aufnahme wiederkehrender Abläufe und macht Abläufe leichter reproduzierbar, erfordert aber anfangs etwas Planung und gelegentliches Feintuning bei Untertiteln bzw. KI‑Voiceovers. Datenschutzaspekte (keine persönlichen Daten aufnehmen) und der Wunsch nach sauber geplanten Aufnahmen sind die wichtigsten Vorbehalte. 
 
 Vor dem Hintergrund agilen Projektmanagements erweist sich guidde als besonders wertvoll: Kurze, gut dokumentierte User Journeys unterstützen Transparenz, schnelle Iteration und das Teilen von Wissen in Sprints — und sie reduzieren Kommunikationsaufwand und Reibungsverluste zwischen Teammitgliedern.

 Durch die praktische Anwendung von guidde in den User Journeys der MC-Test-App sollen Sie das Tool guidde professionell evaluieren.  

**Rahmen.** Alle Videos sind öffentlich ("public") und werden bei guidde gehostet. Es dürfen keine personenbezogenen Daten (PII — "Personally Identifiable Information") aufgezeichnet werden. Der MC-Test läuft ohne Account und verwendet vordefinierte Pseudonyme. Jedes Team dokumentiert alle User Journeys. Unterschied nur beim Export-Ziel:

- **Team A:** Anki | **Team B:** Kahoot | **Team C:** arsnova.click

---

## 1) Ziele, Rollen, Journeys

**Persona:** Dozent/in

**User Journeys:**

1. Anmeldung mit reserviertem Pseudonym
2. Testlauf mit dem vorhandenen Fragenset "Scrum"
3. Erstellen eines eigenen Fragensets "Scrum"
4. Export des Fragensets → Testbericht, Musterlösung, Export zum Ziel-Tool
5. Import des exportierten Fragensets im Ziel-Tool

---

## 2) Guidde-Workflow (minimal und verbindlich)

1) **Aufnahme starten:** Öffnen Sie die guidde-Extension, wählen Sie "Capture" und durchlaufen Sie die Journey in der MC-Test-App einmal vollständig und sauber; beenden Sie danach die Aufnahme.

2) **Nachbearbeiten:**
- Titel und Schritttexte präzisieren (Kurz: Was? / Warum? in 1–2 Sätzen).
- Unnötige Schritte löschen; bei kleinen UI-Elementen Zoom bzw. Hervorhebungen setzen.
- Untertitel aktivieren und ein KI-Voiceover ergänzen.

1) **Veröffentlichen:** Sichtbarkeit auf "public" setzen (Pflicht, damit das Video in der App eingebettet werden kann).

**Pflicht pro Video:** Dokumentieren Sie den Startzustand, stellen Sie eine klare Schrittfolge sicher (pro Schritt genau eine Aktion) und fügen Sie eine Abschlussfolie mit der erwarteten Ansicht oder Datei hinzu.

---

## 3) Team-Aufgaben (Export-Ziel)

- **Team A → Anki:** Export/Import (apkg und tsv)
- **Team B → Kahoot:** Export/Import (Spreadsheet)
- **Team C → arsnova.click:** Export/Import (JSON)

---

## 4) Namensschema, Tags, Ablage

- **Guidde-Titel:** `mc-test | <Persona> | <Journey> | v<APPVERSION> | <YYYY-MM-DD>`
  - Beispiel: `mc-test | Dozent/in | Export nach Anki | v1.3 | 2025-11-04`
- **Guidde-Tags:** `mc-test`, `dozent`/`student`, `export`, `anki`/`kahoot`/`arsnova`, `v<version>`
- **Dateien (falls zusätzlich exportiert):** `mc-test_<persona>_<journey>_<version>_<datum>.<ext>`

---

## 5) Abgabe

- **Für jede Journey:**
  - Guidde-Link (public)
  - Kurzdokument (max. 1 Seite) mit: Purpose, Inputs, Expected Output, Known Pitfalls
- **Team-spezifisch:** je ein Import-Video im Ziel-Tool (Anki/Kahoot/arsnova.click) zusätzlich
- **Evaluationsbericht** zur Nützlichkeit von guidde für die Erstellung von How-to-Videos

---

## 6) Evaluationsansatz — Ansprüche an eine professionelle Tool‑Evaluation

Eine professionelle Evaluation von guidde sollte klare Zielsetzungen, reproduzierbare Methoden und messbare Metriken kombinieren. Ziel ist nicht nur zu prüfen, ob das Tool „funktioniert“, sondern ob es in der Praxis die erwarteten Effekte erzielt (z. B. Zeitersparnis, bessere Reproduzierbarkeit von Arbeitsabläufen, reduzierte Nachfragen). Vorgeschlagener Ansatz in Kurzform:

- Ziele & Fragestellungen: Formulieren Sie präzise Hypothesen (z. B. "Guidde reduziert die durchschnittliche Erstellungszeit einer How‑to‑Anleitung um X %").
- Realistische Aufgaben und Metriken: Nutzen Sie die definierten User Journeys als Aufgaben; messen Sie Ablaufzeit, Anzahl der Nachbearbeitungsschritte und die Qualität des Endprodukts (z. B. Lesbarkeit der Schritttexte, Vollständigkeit der Ergebnisse).
- Praxisorientierte Empfehlungen: Leiten Sie konkrete Handlungsempfehlungen für den Einsatz in Sprints ab — z. B. Standardaufnahmen, Checklisten für saubere Captures, Datenschutz‑Briefings.

Dieser Ansatz stellt sicher, dass die Evaluation belastbare, verwertbare Ergebnisse liefert und zugleich praktikabel in den Projekt‑ und Sprint‑Rhythmen des agilen Projektmanagements bleibt.

## 7) Bewertungsraster

| Kriterium | Gewicht |
|---|---:|
| Vollständigkeit & Reihenfolge der Schritte | 30 % |
| Korrektheit (Export/Import reproduzierbar) | 30 % |
| Verständlichkeit (Titel, Schritttexte, Visuals) | 20 % |
| Wiederverwendbarkeit (neutral, stabil, getaggt) | 10 % |
| Evaluationsbericht | 10 % |

---

## 8) Checkliste pro Video

- [ ] Persona & Journey korrekt benannt (Titel/Tags)
- [ ] Startzustand → Endzustand vollständig
- [ ] Untertitel **und** KI-Voiceover aktiv
- [ ] Public-Link dokumentiert
- [ ] Export-/Import-Schritte (teamabhängig) enthalten

---

## 9) Lernziele

Nach Abschluss dieser Aufgabe haben Sie nicht nur die User Journeys der MC-Test-App professionell dokumentiert, sondern auch praxisnahe Kompetenzen in der Evaluation und Anwendung von Dokumentations-Tools im agilen Projektmanagement erworben. Sie können den Nutzen von Werkzeugen wie guidde für die Wissensvermittlung und Prozessoptimierung bewerten und haben gelernt, klare, reproduzierbare Anleitungen zu erstellen, die die Zusammenarbeit im Team verbessern und den Einarbeitungsaufwand reduzieren.