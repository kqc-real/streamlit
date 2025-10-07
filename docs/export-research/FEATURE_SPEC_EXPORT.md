# Feature-Spezifikation: Export-Funktionen

**Sprint:** Warm-Up Sprint  
**Datum:** [DATUM]  
**Erstellt von:** Alle Teams gemeinsam

---

## 📋 User Stories

### US-1: Export zu Anki

**Als** Dozent  
**möchte ich** meine Fragensets als Anki-Deck exportieren  
**um** sie für Spaced Repetition Learning zu nutzen.

**Akzeptanzkriterien:**
- [ ] Export-Button im Admin-Panel (bei Fragenset-Auswahl)
- [ ] Download startet als `fragenset_anki.txt`
- [ ] Anki-Format korrekt (TXT mit Tabs)
- [ ] LaTeX-Formeln werden konvertiert
- [ ] Erfolgs-Feedback angezeigt

**Story Points:** [8]  
**Priorität:** MUST-HAVE  
**Team:** Flashcard Experts

---

### US-2: Export zu Quizlet

[Gleiche Struktur]

---

### US-3: Export zu Kahoot

[Gleiche Struktur]

---

[...weitere User Stories...]

---

## 🗺️ Roadmap-Empfehlung

**Sprint 1 (MUST-HAVE):**
- [ ] Anki Export (8 SP)
- [ ] Quizlet Export (8 SP)

**Sprint 2 (SHOULD-HAVE):**
- [ ] Kahoot Export (13 SP)
- [ ] Socrative Export (5 SP)

**Sprint 3 (COULD-HAVE):**
- [ ] Particify Export (8 SP)

**Backlog (WON'T-HAVE aktuell):**
- [ ] arsnova.click Export (5 SP)

**Gesamt-Story-Points:** 47 SP

---

## 🎨 UI-Mockup

**Export-Button-Platzierung:**
```
[Admin-Panel]
├── Fragenset auswählen: [Dropdown ▼]
├── Aktionen:
│   ├── [📝 Bearbeiten]
│   ├── [🗑️ Löschen]
│   └── [📤 Exportieren ▼]  ← NEU
│       ├── Anki (.txt)
│       ├── Quizlet (.csv)
│       ├── Kahoot (.xlsx)
│       └── ...
```

**Export-Dialog (Modal):**
```
╔══════════════════════════════════════╗
║  📤 Export: Fragenset "Mathe I"      ║
╠══════════════════════════════════════╣
║  Zielformat: [Anki ▼]                ║
║  ☑ LaTeX-Formeln konvertieren        ║
║  ☑ Erklärungen einbeziehen           ║
║  ☐ Mini-Glossar einbeziehen          ║
║                                      ║
║  [Abbrechen]  [📥 Exportieren]       ║
╚══════════════════════════════════════╝
```

**Erfolgs-Feedback:**
```
✅ 42 Fragen erfolgreich exportiert!
📥 Download: Mathe_I_anki.txt
```

---

## 📊 Priorisierungs-Matrix

| Plattform | Business Value | Tech Effort | Risk | Priorität | Story Points |
|-----------|----------------|-------------|------|-----------|--------------|
| Anki | HIGH | MEDIUM | LOW | MUST | 8 |
| Quizlet | HIGH | MEDIUM | LOW | MUST | 8 |
| Kahoot | MEDIUM | HIGH | MEDIUM | SHOULD | 13 |
| Socrative | MEDIUM | LOW | LOW | SHOULD | 5 |
| Particify | LOW | MEDIUM | MEDIUM | COULD | 8 |
| arsnova.click | LOW | LOW | HIGH | WON'T | 5 |

---

## 🔗 Links zu Detail-Specs

- [MARKTANALYSE_Anki_Quizlet.md](./MARKTANALYSE_Anki_Quizlet.md)
- [TECH_SPEC_Anki_Quizlet.md](./TECH_SPEC_Anki_Quizlet.md)
- [MARKTANALYSE_Kahoot_Socrative.md](./MARKTANALYSE_Kahoot_Socrative.md)
- [TECH_SPEC_Kahoot_Socrative.md](./TECH_SPEC_Kahoot_Socrative.md)
- [MARKTANALYSE_Particify_ARSnova.md](./MARKTANALYSE_Particify_ARSnova.md)
- [TECH_SPEC_Particify_ARSnova.md](./TECH_SPEC_Particify_ARSnova.md)
