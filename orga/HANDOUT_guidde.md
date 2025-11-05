# Handout: User Journeys in **MC-Test-App** mit **guidde** dokumentieren

**Rahmen:** Alle Videos sind **public** und werden **bei guidde gehostet**. Keine PII (MC-Test ohne Account, vordefinierte Pseudonyme). **Jedes Team dokumentiert alle User Journeys**. Unterschied nur beim **Export-Ziel**:  

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

1) **Aufnahme starten:** guidde-Extension öffnen → „Capture“ → Journey in der MC-Test-App einmal sauber durchlaufen → Stop.  
2) **Nachbearbeiten:**  
   - Titel und Schritttexte präzisieren (Was/Wieso in 1–2 Sätzen).  
   - Unnötige Schritte löschen, Zoom/Highlight bei kleinen UI-Elementen.  
   - Untertitel aktivieren **und** KI-Voiceover hinzufügen.  
3) **Veröffentlichen:** Sichtbarkeit **Public** (Pflicht, da Einbettung in App).  

**Pflicht pro Video:** Startzustand, klare Schrittfolge (1 Aktion = 1 Schritt), Ergebnis-Slide mit erwarteter Ansicht/Datei.

---

## 4) Team-Aufgaben (Export-Ziel)

- **Team A → Anki**: Export/Import (apkg und tsv).  
- **Team B → Kahoot**: Export/Import (Spreadsheet).  
- **Team C → arsnova.click**: Export/Import (JSON).

---

## 5) Namensschema, Tags, Ablage

- **Guidde-Titel:** `mc-test | <Persona> | <Journey> | v<APPVERSION> | <YYYY-MM-DD>`  
  *Beispiel:* `mc-test | Dozent/in | Export nach Anki | v1.3 | 2025-11-04`  
- **Guidde-Tags:** `mc-test`, `dozent`/`student`, `export`, `anki`/`kahoot`/`arsnova`, `v<version>`  
- **Dateien (falls zusätzlich exportiert):** `mc-test_<persona>_<journey>_<version>_<datum>.<ext>`

---

## 7) Abgabe

- **Für jede Journey:**  
  - **Guidde-Link (Public)**  
  - Kurzdokument (max. 1 Seite) mit: *Purpose, Inputs, Expected Output, Known Pitfalls*  
- **Team-spezifisch:** je ein Import-Video im Ziel-Tool (Anki/Kahoot/arsnova.click) zusätzlich.
- **Evaluationsbericht** zur Nützlichkeit von guidde für die Erstellung von How-to-Videos

---

## 8) Bewertungsraster (Kurzform)

| Kriterium | Gewicht |
|---|---:|
| Vollständigkeit & Reihenfolge der Schritte | 30 % |
| Korrektheit (Export/Import reproduzierbar) | 30 % |
| Verständlichkeit (Titel, Schritttexte, Visuals) | 20 % |
| Wiederverwendbarkeit (neutral, stabil, getaggt) | 10 % |
| Evaluationsbericht | 10 % |

---

## 9) Checkliste pro Video

- [ ] Persona & Journey korrekt benannt (Titel/Tags)  
- [ ] Startzustand → Endzustand vollständig  
- [ ] Untertitel **und** KI-Voiceover aktiv  
- [ ] Public-Link dokumentiert  
- [ ] Export-/Import-Schritte (teamabhängig) enthalten  
