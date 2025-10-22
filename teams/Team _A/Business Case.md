# MARKTANALYSE — Anki & Quizlet

**Phase 1: Marktrecherche & Business-Analyse**

---

## Executive Summary

**Empfehlung:**
- **Implementieren (Quizlet Export):** Quizlet hat eine deutlich größere, schulnahe Nutzerbasis und ein etabliertes Freemium-/Abo-Modell — ein direkter Export (Push / erzeugte Karteikartensätze) bietet hohen kurzfristigen Nutzen für viele unserer Personas (MINT-, BWL-Studenten, Dozent:innen).  
- **Implementieren (Anki Import-Ready Export — bevorzugt als .apkg/.csv + Anleitung):** Anki ist in spezialisierten Studiengruppen (Medizin, MINT) sehr beliebt; Integration ist technisch einfacher (standardisierte Importe) und eröffnet anspruchsvolle Power-User.  

**Kurzbegründung (3–5 Sätze):**
Quizlet verfügt über deutlich mehr aktive Nutzer im Massenmarkt (Schule, Sprachen) — ein sauberer Export erhöht Verbreitung und Conversion (Cross‑Use). Anki spricht vor allem Power‑User mit hohem Engagement; ein Export im richtigen Format (apkg/csv) steigert Nutzungsintensität und bindet anspruchsvolle Lernende. Beide Integrationen ergänzen sich: Quizlet für Volumen & Marketing, Anki für Tiefe & Retention.

**Priorität:**
- **Quizlet Export:** HIGH
- **Anki Export:** MEDIUM

---

## 1. Marktanalyse

### 1.1 Marktposition (Schätzungen & Quellenlage)
- **Quizlet — Aktive Nutzer (weltweit):** *Schätzung / öffentlich berichtete Werte* liegen im Bereich **~50–60 Mio. monatliche aktive Nutzer**. (stark schulaffin, hohe Verbreitung in Sekundarbereich und Sprachlernenden).  
- **Anki — Aktive Nutzer (weltweit):** Keine offiziellen MAU-Angaben; Anki ist Open‑Source, mit Millionen von Downloads (Desktop/AnkiDroid/AnkiMobile). Nutzer sind tendenziell engagierte Einzelanwender (Medizin, Fremdsprachen, Examensvorbereitung).
- **DACH-Region (Deutschland/Österreich/CH):** Für Quizlet plausibel **0.5–3 Mio.** aktive Nutzer (grobe Schätzung basierend auf Marktanteil und Schulpenetration). Anki in DACH: **niedrigere, aber hoch engagierte Nische** (100k–500k aktive Nutzer geschätzt).
- **Marktanteil Bildungssektor:** Quizlet: **hoher Anteil im schulischen Selbststudium**; Anki: **nischig, stark in universitärer/medizinischer Ausbildung**.

### 1.2 Zielgruppe & Pricing-Modelle
- **Quizlet:** Freemium + Quizlet Plus (Abo) + Lösungen/School & Teacher Accounts (Enterprise/School). Zielgruppen: Sekundarstufe, Sprachlernende, Lehrkräfte.  
- **Anki:** Open‑source Desktop & Web (kostenfrei), AnkiMobile (iOS einmalig kostenpflichtig), AnkiDroid kostenlos. Zielgruppen: Studierende (insb. Medizin, Naturwissenschaften), Professionals.

### 1.3 Typische Nutzungsszenarien & Pain Points
- **Quizlet:** schnelles Erstellen & Teilen von Sets, Spielen/Gruppe; Pain Points: begrenzte Offenheit für Massenimporte, kommerzielle API‑Limits, Verlust von Metadaten beim Import/Export.  
- **Anki:** sehr flexible Karten (Templates, Cloze, Medien), starkes Spaced‑Repetition‑Engagement; Pain Points: steilere Lernkurve, UX bei Bulk‑Importen, Multimedia‑Handling, Synchronisationsfragen.

---

## 2. Business Case

### 2.1 Potentielle Nutzer für Export (Schätzung)
- **Quizlet Export (wenn verfügbar):** Schätzung **5–15%** unserer aktiven Nutzer würden regelmäßig Exportfunktionen nutzen (abhängig von Produktfit). Bei N Nutzern bedeutet das unmittelbares Upside in Reichweite/Retention.  
- **Anki Export:** Schätzung **3–8%** (Power‑User-Kanal; aber hoher CLTV pro Nutzer).

### 2.2 Mehrwert
- **Zeitersparnis:** Lehrende und Lernende sparen Zeit beim Re‑Use von Fragen/MC-Tests als Karteikarten (Bulk-Export statt manueller Erstellung).  
- **Neue Use Cases:**  
  - Lehrende exportieren Prüfungsfragen als Lernsets für Studierende (Blended Learning).  
  - Lernende konvertieren Übungsfragen in persönliches SRS‑Material.  
  - Marketing/Onboarding: vorgefertigte Quizlet‑Sets erhöhen Auffindbarkeit in Suchergebnissen.

### 2.3 Priorisierungsempfehlung
- **Kurzfristig (MVP):** Implementiere einen stabilen CSV/QTI‑Export und einen spezialisierten Quizlet‑Export (API/one‑click) — **Quizlet → MUST‑HAVE**.  
- **Mittelfristig:** .apkg-Export / Anki‑Optimierungen (Templates, Media packaging) — **Anki → SHOULD‑HAVE**.

---

## 3. Detaillierte Analyse (Plattform‑weise)

### Quizlet (detailliert)
**Stärken:** große Reichweite, starke Nutzung in Schulen, einfache Sharing‑Funktionalität, Monetarisierung (Plus, Teacher/School).  
**Schwächen:** API‑Zugänglichkeit eingeschränkt; kommerzielle Lizenzfragen; mögliche Duplicate‑Content/Moderation.  
**Technische Anforderungen für Export:**
- Exportformat: CSV/TSV (Term/Definition), optional Quizlet‑API or bulk import link; Media‑Handling (Audio/Bilder) über CDN/Presigned URLs.  
**Empfohlener Funktionsumfang (MVP):**
- One‑click „Export to Quizlet“ (erstellt set auf Nutzerkonto via OAuth/API oder erzeugt downloadable CSV + import instructions).  
- Mapping: Frage → Karte (front/back), Tags (Deck), Bilder → URL.  
**Priorität:** HIGH

### Anki (detailliert)
**Stärken:** mächtiges SRS, flexibles Kartenformat, starke Bindung bei Power‑Usern.  
**Schwächen:** weniger „mainstream“; UX für Einsteiger anspruchsvoll; Desktop‑zentriert.  
**Technische Anforderungen für Export:**
- Export als **.apkg** (empfohlen) oder CSV mit klaren Templates; Media packaging (ZIP) oder hosting für Bilder/audio; optionaler Import‑Guide für Anki‑Neulinge.  
**Empfohlener Funktionsumfang (MVP):**
- CSV + Anleitung (schnell bereitstellbar).  
- Medium‑term: native .apkg builder (inkl. Stile/Templates).  
**Priorität:** MEDIUM

---

## 4. Vergleich & Empfehlung (2–3 Absätze)
Quizlet liefert das größte Volumen an potenziellen Nutzern und ist stark in Schulen verankert; ein Export hier zahlt sich in größerer Sichtbarkeit, einfacher Verbreitung von Inhalten und direkter Nutzerbindung aus. Technisch lässt sich ein Quizlet‑MVP über CSV + OAuth/API lösen; rechtliche/Rate‑Limit‑Checks sind allerdings erforderlich.  
Anki wiederum bedient eine kleinere, aber sehr loyale Nutzergruppe, die von hochwertigen Exports (apkg + Medien) stark profitiert. Die technische Komplexität (paketierte Medien, Templates) ist höher, der unmittelbare Marketing‑Hebel jedoch geringer.  
**Empfehlung:** Priorisiere Quizlet‑Export als erstes Produktprojekt (High priority, MUST‑HAVE), parallel Planung eines Anki‑MVP (CSV + guide) mit Ziel: Release im Q2 nach Quizlet‑Launch.

---

## 1.2 Competitive Analysis — Tabelle (Kurz)  
*(ausführlichere Tabelle im Anhang / separater MARKTANALYSE.md)*

| Tool / Produkt | Export zu Quizlet | Export zu Anki | UX – Export/Import | Was wir besser machen können |
|---|---:|---:|---|---|
| Moodle | ❌ (kein native Quizlet push) / CSV/QTI export möglich | ✅ (CSV/QTI → Anki via conversion) | technisch robust, aber nicht user‑friendly | One‑click export + presets for cards |
| Canvas | ❌ (CSV/QTI) | ✅ (via CSV/QTI) | Institution‑centric; instructors need steps | Simple UI for teachers: ‚Export to flashcards‘ |
| Kahoot | ❌ (not direct) | ❌ | Game‑oriented, export limited | Provide export with mapping to QA cards |
| Quizizz | ❌ (CSV export only) | ❌ | Good teacher UX, no direct flashcard push | Direct push to Quizlet / Anki export presets |
| ClassMarker / Testmoz | ❌ (CSV) | ❌ | Lightweight; few integrations | Export templates for card creation |

---

## Appendix / Next Steps
1. **Technische Spec (MVP):** CSV exporter (front/back/tags/media_url), OAuth flow for Quizlet API, .apkg generator spec.  
2. **Legal/Compliance:** API‑TOS check mit Quizlet; Rate limits & commercial reuse.  
3. **Pilot:** 1–2 institutionelle Partner (Dozenten), A/B test: Export vs. no‑export on retention & NPS.  
4. **Metrics to track:** Anzahl Exporte, Imports completed, Nutzer‑Retention nach Export, Konversion zu Premium.

---

*Ende MARKTANALYSE_Anki_Quizlet.md*

