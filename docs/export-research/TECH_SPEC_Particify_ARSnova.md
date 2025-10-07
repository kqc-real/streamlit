# Technical Specification: Particify + arsnova.click

**Team:** Academic Tools Specialists  
**Datum:** [DATUM]  
**Bearbeiter:** [Namen]

---

## 🎴 Particify

### Import-Formate

**Unterstützte Formate:**
- [ ] TXT (Tab-separated)
- [ ] CSV
- [ ] APKG (Particify Package)
- [ ] JSON
- [ ] Andere: [beschreiben]

**Empfohlenes Format:** [Format mit Begründung]

**Offizielle Dokumentation:** [Link zur Particify-Docs]

---

### Datenstruktur

**Beispiel-Format (TXT):**
```
Frage [TAB] Antwort
Was ist 2+2? [TAB] 4
Hauptstadt von Frankreich? [TAB] Paris
```

**Beispiel-Format (CSV):**
```csv
"Frage","Antwort"
"Was ist 2+2?","4"
"Hauptstadt von Frankreich?","Paris"
```

**Pflichtfelder:**
- Frage (Front)
- Antwort (Back)

**Optionale Felder:**
- Tags (Themen)
- Deck-Name
- Card-Type

---

### LaTeX-Support

**Unterstützt:** ✅ Ja / ❌ Nein

**Syntax:**
- Inline: `[$]E=mc^2[/$]`
- Display: `[$$]\int_0^1 x^2 dx[/$$]`

**Test-Ergebnis:**
- [ ] Einfache Formel getestet (z.B. E=mc²)
- [ ] Komplexe Formel getestet (z.B. Integral)
- [ ] Screenshot im Ordner `export-examples/`

**Limitierungen:**
- [Welche LaTeX-Befehle funktionieren nicht?]

---

### Metadaten-Mapping

**Wie mappen wir MC-Test-App-Felder auf Particify-Felder?**

| MC-Test-App Feld | Particify-Feld | Transformation | Fallback |
|------------------|-----------|----------------|----------|
| `question_text` | Front | Direkt | - |
| `correct_answer` | Back | Nur richtige Antwort | - |
| `explanation` | Back (Zusatz) | Nach `---` anhängen | Weglassen |
| `difficulty` | Tags | 1→`easy`, 2→`medium`, 3→`hard` | - |
| `topics` | Tags | Direkt (Liste) | - |
| `mini_glossary` | Back (Zusatz) | Als "Glossar: ..." | Weglassen |

---

### Limitierungen & Herausforderungen

**Was kann NICHT exportiert werden?**
- [ ] Multiple-Choice-Optionen (Particify = Karteikarten, kein MC)
- [ ] Gewichtung (kein Particify-Feld)
- [ ] Bilder (möglich, aber aufwendig)

**Workarounds:**
- MC-Fragen umwandeln: "Was ist die richtige Antwort auf X?" → Antwort direkt
- Bilder als Base64 einbetten (optional)

**Breaking Changes:**
- [Gibt es bekannte Particify-Updates, die Format ändern?]

---

### Implementierungs-Empfehlung

**Story Points:** [Schätzung: 3, 5, 8, 13]

**Priorität:** HIGH / MEDIUM / LOW

**Risk-Level:** LOW / MEDIUM / HIGH

**Begründung:** [2-3 Sätze]

---

## 🎓 arsnova.click

[Gleiche Struktur wie Particify]

### Import-Formate
[...]

### Datenstruktur
[...]

### LaTeX-Support
[...]

### Metadaten-Mapping
[...]

### Limitierungen & Herausforderungen
[...]

### Implementierungs-Empfehlung
[...]

---

## 📂 Beispiel-Export-Dateien

**Erstellt im Ordner `export-examples/`:**
- [ ] `particify_example.json` (5 Fragen aus PDF_Test.json)
- [ ] `arsnova_example.json` (5 Fragen aus PDF_Test.json)

**Test-Import:**
- [ ] Particify: Import erfolgreich? ✅ / ❌
- [ ] arsnova.click: Import erfolgreich? ✅ / ❌
- [ ] Screenshots dokumentiert

---

## 🔗 Ressourcen

- [Particify Import-Docs]
- [arsnova.click Import-Docs]
- [GitHub: Particify-Connector (falls vorhanden)]
- [Community-Forum (für LaTeX-Support)]
