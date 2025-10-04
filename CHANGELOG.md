# Changelog

Alle bemerkenswerten Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).

## [1.0.0] - 2025-10-04

### 🎉 Initial Stable Release

Erste stabile Version der MC-Test-App mit vollständigem Feature-Set.

### ✨ Added

#### Core Features
- **Authentifizierung**: Pseudonym-basiertes Login ohne Registrierung
- **Fragenset-Verwaltung**: JSON-basierte Fragensets mit 8+ vordefinierten Sets
- **Test-Durchführung**: Zwei Scoring-Modi (Leicht/Schwer) mit drei Schwierigkeitsgraden
- **Navigation & UX**: Sidebar mit Fortschrittsanzeige und Bookmark-System

#### PDF-Export System (1.607 Zeilen Code)
- **LaTeX-Rendering**: QuickLaTeX API mit 1200 DPI Auflösung
- **Parallel-Processing**: ThreadPoolExecutor für schnelles Formel-Rendering
- **Durchschnittsvergleich**: "Du vs. Ø" Feature mit SQL-basierter Berechnung
- **Mini-Glossar**: Automatische Extraktion und Darstellung von Begriffen
  - Zebra-Streifen Design (alternierende Hintergründe)
  - Bold-Begriffe (font-weight: 800)
  - LaTeX-Support in Definitionen
  - Alphabetische Sortierung
- **Bookmarks-Overview**: Zusammenfassung markierter Fragen
- **Difficulty-Badges**: Farbcodierte Schwierigkeitsgrade (★/★★/★★★)
- **Dual Numbering**: Test-Position + Original-Fragenummer
- **Color Coding**: Grün (korrekt) / Rot (falsch)
- **QR-Code**: Link zur App im PDF
- **Performance-Stats**: Gesamtergebnis und Breakdown nach Schwierigkeit

#### Admin-Panel & Analytics
- **Itemanalyse**: Schwierigkeitsindex und Trennschärfe pro Frage
- **Distraktor-Analyse**: Effektivität falscher Antwortoptionen
- **Feedback-Management**: User-Feedback mit Status-Tracking
- **Datenexport**: CSV und SQL-Dump für externe Analyse

#### Datenbank & Persistenz
- **SQLite mit WAL-Mode**: Concurrent Reads während Writes
- **4 Tabellen**: test_sessions, answers, users, feedback
- **Indexes**: Optimierte Queries für User-History
- **Connection-Pooling**: Context Manager für Transaktionen

#### Fragenset-Format
- **JSON-Schema**: Strukturierte Fragen mit LaTeX-Support
- **Pflichtfelder**: frage, optionen, korrekte_antwort, schwierigkeit, punkte, erklaerung
- **Optionale Felder**: mini_glossary (neu in v1.0.0), quelle, tags
- **LaTeX-Pakete**: amsmath, amssymb verfügbar

### 🔧 Technical Specifications

#### Module (13 insgesamt)
- `app.py`: Streamlit Main-Entrypoint
- `auth.py`: Authentifizierungs-Logik
- `main_view.py`: Test-Durchführung
- `admin_panel.py`: Admin-Interface (~800 Zeilen)
- `pdf_export.py`: PDF-Generierung (1.607 Zeilen)
- `logic.py`: Core-Business-Logik (~500 Zeilen)
- `database.py`: SQLite-Interface (~400 Zeilen)
- `data_manager.py`: Fragenset-Verwaltung
- `components.py`: Wiederverwendbare UI-Komponenten
- `helpers.py`: Utility-Funktionen
- `config.py`: Konfiguration und Konstanten
- `_paths.py`: Dateipfad-Management
- `__init__.py`: Package-Definition

#### Dependencies (Haupt-Packages)
- `streamlit==1.31.0`: Web-Framework
- `weasyprint==60.2`: PDF-Generierung
- `qrcode==7.4.2`: QR-Code-Generierung
- `Pillow==10.2.0`: Bildverarbeitung
- `requests==2.31.0`: HTTP-Client für APIs
- `pandas==2.2.0`: Datenanalyse (Admin)
- `numpy==1.26.3`: Numerische Berechnungen
- `scipy==1.12.0`: Statistische Funktionen

#### Deployment
- **Platform**: Streamlit Community Cloud (kostenlos)
- **Performance**: PDF-Export 30 Sek (10 Fragen)
- **Uptime**: ~99% (Sleep nach 7 Tagen Inaktivität)

### 📚 Documentation

- `README.md` (18KB): Hauptdokumentation mit LLM-Prompt für Fragenset-Erstellung
- `FEATURE_EXPOSE.md` (31KB): Umfassende Feature-Dokumentation (10 Abschnitte)
- `GLOSSARY_SCHEMA.md` (3.4KB): JSON-Schema und Guidelines für Mini-Glossar
- `AI_QUESTION_GENERATOR_PLAN.md` (55KB): Konzept für KI-Generator (v2.0.0 Preview)
- `DEPLOYMENT_FEASIBILITY_STUDY.md` (29KB): Infrastruktur-Optionen und TCO-Analyse
- `VISION_RELEASE_2.0.md` (30KB): Strategische Roadmap für zukünftige Releases
- `SCRUM_PRESENTATION_V2.0.md` (39KB): Sprint-Planning für Version 2.0.0
- `CHANGELOG.md`: Diese Datei

### 🎯 Metrics (v1.0.0)

- **Codebase**: ~5.000 Zeilen Python
- **Fragensets**: 8 vordefinierte Sets
- **Database**: SQLite mit 4 Tabellen
- **PDF-Export**: 1.607 Zeilen (komplexestes Modul)
- **Test-Coverage**: ~60% (Core-Logik)

### 🔒 Security & Privacy

- **Keine PII**: Nur Pseudonyme, keine E-Mails oder Namen
- **Keine Tracking-Cookies**: Datenschutz-freundlich
- **HTTPS-only**: Let's Encrypt SSL-Zertifikate
- **SQL-Injection-Schutz**: Parametrisierte Queries

### 🐛 Known Issues

- PDF-Generierung langsam auf Streamlit Cloud (30 Sek für 10 Fragen)
- Sleep-Modus nach 7 Tagen Inaktivität (Streamlit-Limitierung)
- Keine Multi-User-Editing-Funktionalität (geplant für v2.0.0)

### 🚀 Next Steps (v2.0.0 Preview)

Die nächste Major-Version wird folgende Features bringen:
- **KI-Generator**: Automatische Fragenset-Erstellung mit LLM (GPT-4o/Claude)
- **Community-Features**: Review-System, Versionskontrolle
- **Monetarisierung**: Freemium-Modell (Free vs. Pro für $4.99/Monat)
- **Performance**: Migration zu Railway/Render (8 Sek statt 30 Sek für PDFs)

Siehe `SCRUM_PRESENTATION_V2.0.md` für detaillierte Sprint-Planung.

---

## Version History

### [1.0.0] - 2025-10-04
- Initial stable release
- Git-Tag: `v1.0.0`

---

## Semantic Versioning

Dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/):

**MAJOR.MINOR.PATCH** (z.B. 2.0.0)

- **MAJOR**: Inkompatible API-Änderungen
- **MINOR**: Neue Features (rückwärtskompatibel)
- **PATCH**: Bugfixes (rückwärtskompatibel)

### Geplante Versionen

- **v1.0.x**: Bugfixes und kleinere Verbesserungen
- **v1.x.0**: Neue Features ohne Breaking Changes
- **v2.0.0**: KI-Generator, Community-Features, Monetarisierung (Q4 2025)

---

**Repository**: https://github.com/kqc-real/streamlit  
**Maintainer**: kqc-real  
**License**: [Lizenz einfügen]
