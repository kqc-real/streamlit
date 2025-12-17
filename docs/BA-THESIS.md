# Aufgabenbeschreibung Bachelorarbeit  
**Thema:** Migration und Erweiterung der Streamlit-App „MC-Test“ mit lokal betriebenem LLM, KI-gestützter Weiterentwicklung und vergleichender Evaluation

## 1. Ausgangslage  
Die Streamlit-App **„MC-Test“** wird derzeit in der Streamlit Community Cloud betrieben: https://mc-test.streamlit.app/. Die Anwendung dient der Erstellung und Durchführung didaktisch strukturierter Multiple-Choice-Tests und wird bereits produktiv in mehreren Lehrveranstaltungen eingesetzt. Die vorhandenen Fragensets sowie der etablierte Test-Workflow belegen den praktischen Nutzen und die Reife des Systems.

Die App ist **weitgehend KI-gestützt entwickelt worden**. Der überwiegende Teil des Python-Codes und der zugehörigen Komponenten wurde durch iterative KI-Generierung erstellt (Größenordnung ca. 99 Prozent), mit einem Gesamtaufwand von etwa 80 Stunden KI-gestützter Entwicklungszeit. Dieses Vorgehen war ein Experiment, ob mit modernen KI-gestützten Entwicklungsansätzen („Vibe-Coding“) eine professionelle, produktive Anwendung mit realem Nutzwert entstehen kann. Das Ergebnis erreicht ein Niveau, das früher typischerweise eine eigenständige Bachelorarbeit zur vollständigen manuellen Entwicklung erfordert hätte.

Parallel steht auf einem institutseigenen Server eine lokale LLM-Infrastruktur zur Verfügung, u.a. über **Ollama**, sodass verschiedene Modelle (z.B. **DeepSeek R1**) lokal ausführbar sind. Der bisherige Prompt zur Generierung von Fragensets (`KI_PROMPT.md`: https://github.com/kqc-real/streamlit/blob/main/KI_PROMPT.md) wurde bislang an externe KI-Dienste (z.B. ChatGPT, Gemini) übergeben.

## 2. Zielsetzung  
Ziel der Bachelorarbeit ist die **Technik- und Qualitätsmigration** der App hin zu einer produktiv einsetzbaren, lokal gehosteten Lösung mit **lokaler LLM-gestützter Generierung von Fragensets**.  

Die Arbeit umfasst:
1. **Migration** der Streamlit-App auf den institutseigenen Server inklusive Datenbank-Backend und lokaler MathJax-Instanz.  
2. **Integration** eines lokalen LLM-Backends über Ollama.  
3. **Prompt-Refactoring** für robuste API-Nutzung ohne Rückfragen.  
4. **Implementierung eines strukturierten Dialogs** in Streamlit zur Erhebung aller Parameter für die Generierung.  
5. **Systematische Evaluation** lokaler Modelle im Vergleich zu externen LLMs.  
6. **KI-gestützter Entwicklungsprozess** als Arbeitsmethode: Der Student setzt moderne KI-Entwicklungswerkzeuge ein und übernimmt dabei primär die Rolle der Qualitätssicherung und Steuerung.

## 3. Methodischer Rahmen: KI-gestützte Entwicklung  
Ein zentraler Bestandteil der Arbeit ist die **konsequente Nutzung moderner KI-Entwicklungswerkzeuge** zur Weiterentwicklung der bestehenden App. Der Student soll die Umsetzung der Arbeitspakete überwiegend mit Unterstützung eines integrierten, agentenbasierten KI-Systems (z.B. in Visual Studio Code, mit geeigneten Modellen und Assistenzsystemen) durchführen.

Der Fokus des studentischen Beitrags liegt damit weniger auf „klassischer“ manueller Implementierung, sondern auf:
- der **präzisen Formulierung von Entwicklungs- und Refactoring-Prompts**,  
- der **kritischen Bewertung** der generierten Änderungen,  
- der **iterativen Steuerung** der KI-Ausgaben,  
- der **Absicherung durch Tests** und reale Ausführungsprüfungen,  
- der **Dokumentation** von Vorgehen, Risiken, Grenzen und Nutzen des KI-gestützten Ansatzes.

Damit wird der Entwicklungsprozess selbst zu einem reflektierten Bestandteil der Bachelorarbeit.

## 4. Aufgaben und Arbeitspakete  

### 4.1 Migration der Anwendung  
- Analyse des aktuellen Hosting-Setups in der Streamlit Community Cloud.  
- Portierung der Anwendung auf den institutseigenen Server.  
- Einrichtung und Anbindung einer **relationalen Datenbank** (z.B. PostgreSQL).  
- Bereitstellung einer lokalen **MathJax-Instanz** zur datenschutzkonformen Formeldarstellung.
- Anpassung der Konfiguration (Secrets, Umgebungsvariablen) und Definition einer **Deployment-Strategie mittels Docker-Compose**.  
- Dokumentation des Deployments und der Betriebsanforderungen.

### 4.2 Lokaler LLM-Betrieb und API-Integration  
- Konsolidierung der vorhandenen Ollama-Installation auf dem Zielserver.  
- Auswahl und Test eines geeigneten lokalen Modells (z.B. DeepSeek R1 in aktueller Version).  
- Definition einer stabilen API-Schnittstelle aus Sicht der App (Request/Response-Vertrag).  
- Integration der lokalen LLM-Aufrufe in den bestehenden Generierungsworkflow.

### 4.3 Prompt-Refactoring für lokale Modelle  
- Analyse des bisherigen Prompts `KI_PROMPT.md` und des bisherigen externen Workflows.  
- Überarbeitung der **System-Message/Manager-Message** für lokale LLMs mit folgenden Anforderungen:  
  - Explizite Übermittlung von Kontextinformationen, die das Modell nicht automatisch kennt  
    (z.B. Datum/Uhrzeit, sofern für die Generierungslogik relevant).  
  - Kein Rückfrageverhalten:  
    Der Prompt muss vollständig spezifizieren, welche Eingaben erwartet werden und wie zu verfahren ist,  
    wenn Informationen fehlen.  
  - Priorisierung von **JSON-Validität**, stabilen Ausgabestrukturen und Fehlertoleranz.  
- Iteratives Testen und Verfeinern des Prompts anhand realer Eingabebeispiele.

### 4.4 Dialogführung in Streamlit  
- Entwurf und Implementierung eines **strukturierten Nutzer-Dialogs** zur Erhebung aller Parameter, z.B.:  
  - Themengebiet  
  - Anzahl der Fragen  
  - Schwierigkeitsstufe  
  - Anzahl und Art der Antwortoptionen  
  - optionaler Upload und Einbindung externer Dokumente  
- Validierung der Nutzereingaben (Pflichtfelder, Plausibilitätschecks).  
- Generierung des finalen API-Requests aus den Dialogdaten.  
- Saubere Trennung von UI-Logik, Prompt-Bausteinen und Kommunikationsschicht.

### 4.5 Test- und Qualitätssicherung  
- Aufbau einer **Teststrategie** mit Fokus auf:  
  - Unit-Tests für zentrale Logikmodule  
  - Integrationstests für LLM-API-Aufrufe  
  - Validierung der JSON-Ausgaben  
- Einführung oder Verbesserung von Logging und Fehlerbehandlung  
  (insbesondere für Prompting, Parsing und Datenbankzugriffe).  
- Reproduzierbare Testläufe mit dokumentierten Eingabeparametern.

### 4.6 Evaluationsstudie: Extern vs. Lokal  
- Entwicklung eines **Evaluationsdesigns** zur vergleichenden Beurteilung von:  
  - **Antwortqualität** (fachliche Relevanz, didaktische Angemessenheit, Verständlichkeit)  
  - **Strukturgüte** (Vollständigkeit und Konsistenz der Fragensets)  
  - **JSON-Validität** und Robustheit gegen Formatfehler  
  - **Reproduzierbarkeit** und Varianz bei wiederholten Läufen  
- Aufbau eines Testkorpus aus repräsentativen Themen und Parametereinstellungen.  
- Durchführung einer Versuchsreihe:  
  - identische Prompt-/Parameter-Inputs an externe Systeme (z.B. ChatGPT/Gemini)  
  - identische Inputs an das lokale LLM  
- Auswertung mit qualitativen und ggf. quantitativen Kriterien  
  (z.B. Fehlerquoten, Rubric-basierte Bewertung).  
- Ableitung von Empfehlungen für den produktiven Einsatz.

## 5. Erwartete Ergebnisse / Deliverables  
- Lauffähige Streamlit-App auf dem institutseigenen Server.  
- Funktionierende, via Docker-Compose orchestrierte Services (Streamlit, PostgreSQL, MathJax) inkl. Dokumentation.  
- Integrierte lokale LLM-Nutzung über Ollama mit klar definiertem Request/Response-Format.  
- Überarbeiteter, API-tauglicher Prompt (inkl. System-Message) für robuste, zielgerichtete Ausgabe.  
- Implementierter Streamlit-Dialog zur Parametrisierung der Fragenset-Generierung.  
- Testkonzept und implementierte Tests (Unit- und ausgewählte Integrationstests).  
- Evaluationsbericht mit Vergleich lokaler und externer Modelle.  
- Technische Dokumentation und kurze Betriebs-/Wartungsanleitung.  
- Reflexion des **KI-gestützten Entwicklungsprozesses** (Vorgehensmodell, Grenzen, Best Practices).

## 6. Qualitäts- und Randbedingungen  
- Fokus auf **Robustheit**, **Wartbarkeit** und eine klare Modularchitektur.  
- Nachvollziehbare Logging-Strategie für Prompting, JSON-Parsing und Fehlerfälle.  
- Berücksichtigung von Datenschutz- und Compliance-Aspekten, sofern Nutzerdaten verarbeitet werden.  
- Möglichst generisches Design, sodass Modellwechsel innerhalb Ollama ohne größere Codeänderungen möglich ist.  
- Der Student dokumentiert die **KI-Prompting-Strategie** zur Softwareentwicklung  
  (z.B. Arten von Prompts, Iterationszyklen, typische Fehlerklassen und deren Vermeidung).

## 7. Abgrenzung  
- Kein Ausbau der App zu einem vollständigen Lernmanagementsystem.  
- Keine Entwicklung neuer KI-Modelle; Fokus liegt auf **Integration, Prompt-Engineering, Betrieb, Test und Evaluation**.  
- UI-Verbesserungen nur insoweit, wie sie für den Dialog- und Generierungsprozess erforderlich sind.

## 8. Vorschlag für eine grobe Arbeitsschrittfolge  
1. Ist-Analyse der App, des bisherigen Prompt-Workflows und der lokalen LLM-Infrastruktur.  
2. Server-Deployment der Streamlit-App und Datenbankintegration.  
3. Integration des lokalen LLM-Backends über Ollama.  
4. Prompt-Refactoring für API-Betrieb ohne Rückfragen.  
5. Implementierung der Dialogführung in Streamlit.  
6. Aufbau von Unit- und Integrationstests sowie JSON-Validierungsmechanismen.  
7. Entwicklung des Testkorpus und des Evaluationsdesigns.  
8. Vergleichsexperimente durchführen und auswerten.  
9. Dokumentation des Systems und des KI-gestützten Entwicklungsprozesses.  
10. Schlussfolgerungen und Empfehlungskatalog.

---

**Kurzbeschreibung in einem Satz:**  
Die Arbeit migriert die KI-gestützt entwickelte Streamlit-App „MC-Test“ auf einen institutseigenen Server mit eigener Datenbank und lokaler MathJax-Instanz, integriert ein lokal betriebenes LLM über Ollama zur Fragenset-Generierung, überarbeitet den Prompt- und Dialogprozess für robuste API-Ausgaben, sichert die Lösung durch Tests ab und evaluiert die Ergebnisqualität im Vergleich zu externen KI-Systemen unter expliziter Nutzung eines KI-gestützten Entwicklungsprozesses.
