# Before/After-Vergleich: EDULEARN26 (Original vs. optimiert)

> Hinweis: In jeder Sektion steht zuerst **BEFORE** (Originaltext), dann **AFTER** (optimierte Fassung). Abbildungslinks sind identisch, damit die Bilder später ohne Anpassung zugeführt werden können.

## Titelblock

### BEFORE (Original)

# Von summativen Multiple-Choice-Tests zu formativer Übung: KI-gestützte Fragengenerierung, kognitive Analysen und adaptive Taktung

**R. Bimberg, P. Kubica, K. Quibeldey-Cirkel**  
Technische Hochschule Mittelhessen (DEUTSCHLAND)  
IU Internationale Hochschule (DEUTSCHLAND)

### AFTER (Optimiert)

# Von summativen Multiple-Choice-Prüfungen zur formativen Übung: KI-gestützte Item-Generierung, kognitive Lernanalytik und adaptives Pacing

**R. Bimberg, P. Kubica, K. Quibeldey-Cirkel**  
Technische Hochschule Mittelhessen (Deutschland); IU Internationale Hochschule (Deutschland)

## Zusammenfassung

### BEFORE (Original: Zusammenfassung)

Multiple-Choice-Prüfungen (MC) skalieren gut für große Kohorten, doch viele Plattformen liefern nur eine Punktzahl und bergen beim Einsatz von Cloud‑KI Datenschutzrisiken. Diese Arbeit stellt MC‑Test vor, eine datenschutzkonforme Webplattform für formatives MC‑Training, die LLM‑gestützte Itemgenerierung mit strukturiertem Feedback, lernendenzentrierten Analysen und zeitbewusster Taktung verbindet. Eine lokale On‑Premises‑Architektur (Ollama) stellt sicher, dass Prompts und Lerndaten innerhalb der institutionellen Infrastruktur verbleiben.

MC-Test verwendet ein didaktisches Itemmodell, das jedes Item mit einem Lernziel, Thema, Gewichtung und einer operationalisierten kognitiven Stufe verknüpft. Die kognitiven Stufen sind auf Bloom‑Stufen 1–3 beschränkt (Reproduktion, Anwendung, Analyse). Items werden durch einen endlichen Prompt-Workflow erzeugt und als schema-valide JSON ausgegeben; automatisierte Validierung und Reparatur erhöhen die Robustheit und ermöglichen nachgelagerte Itemstatistiken.

Nach jeder Sitzung erhalten Lernende Begründungen für jede Antwortoption, ein Mini‑Glossar sowie exportierbare Lernziele und Lernressourcen. Dashboards visualisieren die Leistung nach Thema und kognitiver Stufe. Verwendet werden Themenleistungsdiagramm, kognitives Radarprofil, Konzeptbeherrschungsspalten und Themen‑×‑Kognitiv‑Heatmap. Um Schnellraten zu reduzieren, wendet MC‑Test konfigurierbare Wartezeiten vor und nach der Antwort an. Der Panikmodus lockert die Taktung, wenn die verbleibende Zeit pro Item kritisch wird. Pseudonyme ermöglichen anonyme Teilnahme. Eine Pilot‑Usability‑Studie mit der System Usability Scale (SUS, N = 20) zeigt gute Akzeptanz mit einem Mittelwert von 70,38 (Adjektiv‑Kategorie „OK“ [1]). Die Plattform ist als Open‑Source‑Software unter MIT‑Lizenz verfügbar.

**Schlüsselwörter:** Künstliche Intelligenz in der Bildung, Multiple-Choice-Fragengenerierung, Bloom‑Taxonomie, lernendenzentrierte Lernanalysen, selbstreguliertes Lernen, Erkennung von Schnellraten, adaptive Taktung, datenschutzwahrende lokale Sprachmodelle, formative Bewertung.

### AFTER (Optimiert)

Multiple-Choice-(MC-)Prüfungen sind in großen Kohorten effizient. In der Praxis endet die Rückmeldung jedoch oft bei einer Punktzahl. Lernende sehen zwar richtige und falsche Antworten, erhalten aber wenig Hilfe dabei, Wissenslücken zu verstehen, Lernziele abzuleiten und ihre Prüfungsvorbereitung zu steuern.

Wir stellen **MC-Test** vor, eine Webplattform für **formative MC-Übungssitzungen**. MC-Test kombiniert (1) ein didaktisches Itemmodell (Lernziele, Topics, Bloom-Stufen 1–3), (2) eine robuste, schema-gebundene LLM-Pipeline zur Item-Erzeugung und (3) lernendenzentrierte Dashboards, die Leistung nach Topic und kognitiver Stufe sichtbar machen. Nach jeder Sitzung erhalten Lernende Begründungen zu *jeder* Antwortoption sowie ein Mini-Glossar. Um impulsives Klicken und **Rapid Guessing** zu reduzieren, ergänzt MC-Test pädagogische Tempo-Steuerungen (Pre-Answer-Cooldown, Reflexionsfenster) und einen konfigurierbaren **Panikmodus**.

MC-Test entstand zunächst mit kommerziellen LLM-APIs und wurde anschließend auf ein lokales LLM-Backend (**Ollama**) migriert, sodass Prompts und Lerndaten innerhalb der institutionellen Infrastruktur verbleiben. Eine erste Usability-Erhebung (SUS, *N* = 20) ergibt einen Mittelwert von **70,38** (Kategorie „OK“). Weitere Arbeit fokussiert eine logbasierte Wirkungsanalyse sowie vertiefte psychometrische Prüfungen der generierten Items.

**Schlüsselwörter:** KI in der Hochschullehre; Multiple-Choice; Item-Generierung; Bloom-Taxonomie; Lernanalytik; formative Bewertung; Datenschutz; lokale Sprachmodelle.

---

## 1. Einleitung

### BEFORE (Original: 1. EINLEITUNG)

Multiple-Choice-Fragen (MC) werden an Hochschulen häufig eingesetzt, da sie gut skalieren, objektive Bewertung ermöglichen und sich in großen Kohorten leicht durchführen lassen. Typische MC-Plattformen liefern jedoch kaum mehr als eine Gesamtpunktzahl und itemweise Korrektheit. Dadurch entsteht wenig Unterstützung für metakognitive Reflexion und strategische Prüfungsvorbereitung. Lernende erhalten häufig Feedback, das zu grob ist, um Lernstrategien zu informieren. Gründe für Fehlleistungen bleiben damit häufig unklar.

Große Sprachmodelle (LLMs) können MC-Items in großem Umfang generieren. Dies verlagert den Engpass vom Verfassen zur Qualitätssicherung. Items müssen valide, angemessen schwierig und auf Lernziele abgestimmt sein. Wenn Metadaten wie Thema, Schwierigkeit und kognitive Stufe explizit erfasst werden, kann MC-Training lernendenzentrierte Analysen statt nur Punktzahlen liefern. Frühere Arbeiten zeigen, dass LLM-generierte MCQs in manchen Kontexten wettbewerbsfähige psychometrische Eigenschaften erreichen können. Sie unterstreichen aber die Notwendigkeit systematischer Validierung auf Itemebene, statt die Qualität allein aus der Generierung abzuleiten [2]. LLM-basierte Coding-Assistenten reduzieren zudem den Implementierungsaufwand und ermöglichen Fachexperten die Entwicklung maßgeschneiderter Bildungstools [3].

MC-Test ist eine webbasierte Plattform, die folgende Elemente kombiniert:

- Ein didaktisches Itemmodell, das jedes Item mit Lernzielen, Thema und kognitiven Stufenlabels gemäß Bloom‑Stufen 1–3 verknüpft.
- Eine LLM-Pipeline, die schema-valides JSON über eine endliche Zustandsinteraktion und automatisierte Validierung/Reparatur erzeugt.
- Lernendenzentrierte Analysen, die Leistung nach Thema und kognitiver Stufe visualisieren.
- Pädagogische Kontrollen in Form von Wartezeiten, Reflexionsfenstern und adaptiver Taktung zur Verringerung von Schnellraten.

MC-Test wurde zunächst mit kommerziellen LLM-APIs entwickelt und später zu einem lokalen LLM-Backend über Ollama migriert. Die Arbeit adressiert drei Forschungsfragen:

- **RQ1:** Wie können Klassifikationen kognitiver Stufen in einer lernendenzentrierten Bewertungsplattform operationalisiert werden?
- **RQ2:** Wie können LLMs über robustes Prompt-Engineering eingebettet werden, um psychometrische Qualitätsprüfungen und zuverlässige Itemgenerierung zu unterstützen?
- **RQ3:** Welche Designüberlegungen ergeben sich bei der Migration zu einem lokalen LLM-Backend?

Die Arbeit berichtet über Design und Implementierung von MC-Test und liefert erste Usability-Befunde (SUS, N = 20, Mittelwert = 70,38). Abschnitt 6 skizziert die geplante logbasierte Evaluation von Verhaltenseffekten, insbesondere Schnellraten, und lernbezogenen Ergebnissen. Die Hauptbeiträge sind:

- Operationalisierung der Bloom‑Stufen 1–3 in einem didaktischen Itemmodell und Darstellung durch vier lernendenzentrierte Ansichten (Themenleistungsdiagramm, kognitives Radardiagramm, Konzeptbeherrschungsspalten, Themen-×-Kognitiv-Heatmap) (RQ1).
- Implementierung einer kontextoptimierten, schema-beschränkten Itemgenerierungs-Pipeline (endliche Zustandsinteraktion + JSON-Validierung/Reparatur), die robuste Generierung und nachgelagerte psychometrische Prüfungen unterstützt (RQ2).
- Ableitung von Design- und Deployment-Erkenntnissen aus der Migration von kommerziellen APIs zu einem datenschutzwahrenden lokalen LLM-Backend (Ollama) in einer containerisierten On-Premises-Architektur mit Fokus auf Robustheit und Datensouveränität (RQ3).

MC-Test zielt auf formatives MC-Training in MINT-Fächern ab und beschränkt sich auf Bloom‑Stufen 1–3; höherstufige Aufgaben werden aufgrund aktueller LLM-Limitierungen ausgeschlossen [4]. Die Usability wurde in einer Pilotstudie erhoben (SUS = 70,38, Kategorie „OK“ [1]); Lerneffekte und Verhaltensänderungen erfordern Folgestudien (Abschnitt 6). Kognitive Labels werden doppelt codiert, und menschliche Itemprüfung bleibt obligatorisch. Die Taktung ist kurskonfigurierbar zur Unterstützung von Barrierefreiheit.

### AFTER (Optimiert)

MC-Fragen sind in der Hochschullehre verbreitet, weil sie objektiv auswertbar sind und große Gruppen abdecken. Viele Plattformen liefern jedoch vor allem **Summenwerte**. Dadurch bleibt häufig unklar, *warum* Lernende Fehler machen und *woran* sie gezielt arbeiten sollten.

Große Sprachmodelle (LLMs) können MC-Items heute in großer Menge erzeugen. Damit verschiebt sich der Engpass von der Erstellung zur **Qualitätssicherung**: Items müssen formal korrekt, fachlich stimmig, angemessen schwierig und didaktisch passend sein. Gleichzeitig werfen kommerzielle LLM-APIs im Bildungsbereich Fragen zu Datenschutz, Governance und Kosten auf.

Vor diesem Hintergrund entwickeln wir **MC-Test**, eine Webplattform für formative MC-Übung, die drei Bausteine integriert:

- **Didaktisches Itemmodell** mit Lernzielen, Topics und Bloom-Labels (1–3),
- **robuste LLM-Generierungspipeline** (Schema-Constraints, Validierung, Repair),
- **lernendenzentrierte Analysen** (Dashboards) für Reflexion und Selbstregulation,
  ergänzt um **Pacing** (Cooldowns, Reflexionsfenster, Panikmodus).

### Forschungsfragen

- **RQ1:** Wie lassen sich kognitive Niveaus (Bloom 1–3) so operationalisieren, dass sie in einer lernendenzentrierten Assessment-Plattform interpretierbar und nutzbar werden?
- **RQ2:** Wie können LLMs mittels robuster Prompt-Architektur (Schema-Constraints, Validierung, Repair) verlässlich in Item-Generierung und Qualitätsprüfung eingebettet werden?
- **RQ3:** Welche Design- und Betriebserfahrungen ergeben sich bei der Migration von kommerziellen APIs zu einem lokalen LLM-Backend (Ollama) in einer On-Premises-Architektur?

### Beiträge

1. **Operationalisierung** von Bloom 1–3 in einem didaktischen Itemmodell und Bereitstellung über vier Analyse-Views (RQ1).
2. **Implementierung** einer kontext-engineerten, schema-gebundenen Generierungspipeline (Finite-State-Interaktion + JSON-Validierung/Repair) als Grundlage für nachgelagerte Qualitätschecks (RQ2).
3. **Ableitung** von Design- und Deployment-Lessons aus der Migration zu einem lokalen, privacy-preserving LLM-Backend (Ollama) in containerisiertem On-Premises-Betrieb (RQ3).

MC-Test richtet sich auf formative Übungsszenarien, insbesondere in MINT-Fächern. Wir fokussieren Bloom 1–3, da höhere Stufen im MC-Format und im Kontext aktueller LLMs weniger verlässlich abbildbar sind.

---

## 2. Theoretischer Hintergrund und Related Work

### BEFORE (Original: 2. THEORETISCHER HINTERGRUND UND VERWANDTE ARBEITEN)

**Kognitive Taxonomien und KI-Validität:** Die Bloom‑Taxonomie liefert seit langem einen Rahmen zur Differenzierung kognitiver Komplexität. Während LLMs gut darin sind, Inhalte für niedrigere taxonomische Stufen zu generieren (Erinnern, Verstehen), zeigen aktuelle Studien erhebliche Zuverlässigkeitsprobleme, wenn Modelle versuchen, Aufgaben für höherstufige Bewertung oder Kreation ohne Human-in-the-Loop-Verifikation zu erzeugen [4]. Daher erfordert automatisierte MC-Generierung strenge Einschränkungen zur Sicherstellung semantischer Validität [5].

**Lernendenzentrierte Lernanalysen und Selbstregulation:** Lernendenzentrierte Lernanalysen-Dashboards zielen darauf ab, Lernenden interpretierbare Visualisierungen zur Unterstützung selbstregulierten Lernens bereitzustellen [6]. Die Forschung legt jedoch nahe, dass reine Datenvisualisierung oft unzureichend ist. Effektive Systeme müssen aktive Anleitung oder Nudges bieten, um Erkenntnisse in Verhaltensänderung zu übersetzen [7]. Frühere Arbeiten liefern zudem Design- und Evaluierungsempfehlungen für lernendenzentrierte Lernanalysen-Dashboards [8]. MC-Test adressiert dies durch die Kombination von Analysen mit aktiven Taktungsmechanismen.

**Testbearbeitungsaufwand und Schnellraten:** Bei computergestützter Bewertung können ungewöhnlich kurze Antwortzeiten auf reduzierten Testbearbeitungsaufwand statt auf Wissensmangel hindeuten, etwa in Form von Schnellraten. Antwortzeit-Aufwandsmetriken und aufwandsmoderierte Modelle nutzen Antwortzeiten, um solche Antworten zu markieren oder abzuwerten, und liefern praktische Orientierung für die Festlegung von Antwortzeitenschwellen und die Interpretation von Schnellraten‑Indikatoren in Low-Stakes-Kontexten [9], [10].

**Datenschutz bei generativer KI:** Die Verwendung kommerzieller LLM-APIs in der Bildung wirft erhebliche Datenschutzbedenken bezüglich Datenlecks und DSGVO-Konformität auf [11]. Aktuelle Arbeiten heben das „Privacy Paradox" von LLMs hervor und legen nahe, dass On-Premises-Deployment (lokale LLMs) eine starke Minderungsoption für sensible Bildungskontexte darstellt [12].

### AFTER (Optimiert)

**Bloom-Taxonomie und Validität KI-generierter Items.** Bloom’s Taxonomie dient zur Einordnung kognitiver Komplexität. Für KI-generierte Items ist entscheidend, Bloom-Labels nicht nur zu behaupten, sondern transparent zu operationalisieren und empirisch zu prüfen (z. B. via Expert:innen-Ratings und psychometrische Analysen) [3], [5].

**Learner-Facing Learning Analytics und Selbstregulation.** Lernanalytik-Dashboards unterstützen Planung, Monitoring und Reflexion, wenn sie verständlich sind und konkrete Handlungen nahelegen. Relevante Gestaltungsprinzipien betreffen Interpretierbarkeit, Handlungsbezug und die Einbettung in Lernprozesse [6]–[8].

**Rapid Guessing und Testanstrengung.** Sehr kurze Antwortzeiten sind ein etablierter Hinweis auf reduzierte Anstrengung. In Low-Stakes-Kontexten sind sowohl Interface-Interventionen als auch logbasierte Indikatoren zur Identifikation von Rapid Guessing sinnvoll [9], [10].

**Datenschutz in generativer KI.** Kommerzielle LLM-APIs können Risiken durch Datenabfluss, unklare Datenverarbeitung und Abhängigkeiten (Kosten, Rate Limits) erzeugen. Lokale Deployments sind eine praktikable Privacy-by-Design-Option, erfordern jedoch Governance für Modell- und Sicherheitsupdates [11], [12].

---

## 3. Systemdesign: die Plattform MC-Test

### BEFORE (Original: 3. SYSTEMDESIGN: DIE MC-TEST-PLATTFORM)

### 3.1 Pädagogische Anforderungen

MC-Test wurde für formative Bewertung in MINT-Kursen konzipiert. Zentrale Anforderungen umfassten:

- **Kognitive Transparenz:** Items müssen nach kognitiver Stufe klassifiziert sein.
- **Umsetzbares Feedback:** Erklärungen müssen an Lernziele anknüpfen.
- **Prüfungsbereitschaft:** Unterstützung für Zeitmanagementfähigkeiten.
- **Didaktische Kontrolle:** Lehrende benötigen Kontrolle über die Itemqualität. Dazu gehören itemdiagnostische Hinweise wie Konfidenz‑Muster, die eine gezielte Überarbeitung missverständlicher Items unterstützen.

### 3.2 Systemarchitektur

Die Anwendung ist mit dem Python-Framework Streamlit implementiert und wurde von einem cloudbasierten Prototyp zu einer robusten, containerisierten Microservice-Architektur migriert. Der gesamte Stack wird über Docker Compose orchestriert und auf einem institutionellen On-Premises-Server bereitgestellt, um volle Datensouveränität zu gewährleisten. Zentrale Komponenten umfassen:

- **Datenpersistenz:** Eine PostgreSQL-Datenbank ersetzt leichtgewichtige dateibasierte Speicherung, um gleichzeitige Benutzersitzungen und komplexe relationale Daten (Benutzerprofile, Audit-Logs) zuverlässig zu verarbeiten.
- **Datenschutzkonforme Darstellung:** Um Datenlecks an externe Content Delivery Networks (CDNs) zu vermeiden, werden mathematische Formeln mit einer selbst gehosteten lokalen MathJax-Instanz dargestellt.
- **Lokale Inferenz-Engine:** Eine zentrale architektonische Änderung ist die Integration von Ollama als lokales LLM-Backend. Dies ermöglicht der Plattform, Open-Weight-Modelle vollständig innerhalb der Universitätsinfrastruktur auszuführen und stellt sicher, dass weder Studierendendaten noch Prompt-Logik die sichere Umgebung verlassen.

### 3.3 Didaktisches Datenmodell

Der Kern ist ein striktes JSON-Datenmodell. Zentrale Felder umfassen:

- `topic` und `learning_objective`
- `weight` (1–3) und `cognitive_level` (Reproduktion, Anwendung, Analyse)
- `mini_glossary`: Kontextuelle Definitionen zur Unterstützung von Just-in-Time-Lernen
- `rationales`: Detaillierte Erklärungen, warum jede Option korrekt oder inkorrekt ist
- Antwort‑Selbsteinschätzung vor der Abgabe in den Kategorien sicher und unsicher zur metakognitiven Analyse und Kalibrierung auf Itemebene

### 3.4 Taxonomie kognitiver Stufen für KI-generierte MCQs

MC-Test verwendet eine eingeschränkte dreistufige Taxonomie, inspiriert von der Bloom‑Taxonomie: (1) **Reproduktion** (Gewicht 1): Abruf von Fakten, Definitionen oder einfachen Algorithmen; (2) **Anwendung** (Gewicht 2): Anwendung bekannter Konzepte in leicht variierten Kontexten; und (3) **Analyse** (Gewicht 3): Interpretation von Daten, Vergleiche oder Schlussfolgerungen. Die Stufen 4–6 (Bewertung, Kreation) sind ausgeschlossen. Frühere Arbeiten berichten, dass aktuelle Modelle Schwierigkeiten haben, höherstufige Aufgaben in geschlossenen MC-Formaten zuverlässig zu validieren [4] und dass strikte Einschränkungen für semantisch valide MC-Generierung nötig sind [5]. Die Beschränkung auf Stufen 1–3 verbessert die Überprüfbarkeit und reduziert semantische Halluzinationen, aber menschliche Prüfung und Itemanalyse bleiben für faktische und psychometrische Qualität notwendig.

#### 3.4.1 Operationalisierung und Label-Zuverlässigkeit

Lernendenzentrierte Analysen erfordern stabile kognitive Stufenlabels. MC-Test operationalisiert daher Bloom‑Stufen 1–3 mit einer kurzen Rubrik und einem Verifikationsschritt. Der Workflow umfasst drei Schritte. Erstens spezifizieren Lehrende Lernziel und Zielstufe. Zweitens generiert das LLM ein Item und Begründungen, die auf dieses Ziel abgestimmt sind. Drittens prüfen Lehrende das Item vor Freigabe. Zur Quantifizierung der Label‑Zuverlässigkeit wird eine Stichprobe von zwei Lehrenden mit derselben Rubrik doppelt codiert. Es werden prozentuale Übereinstimmung und Cohens Kappa berichtet. Niedrige Übereinstimmung wird als Warnsignal behandelt, bevor kognitive Profile im großen Maßstab interpretiert werden.

### 3.5 Prompt-Architektur

Die Itemgenerierung wird durch einen kontextoptimierten Systemanweisungssatz gesteuert, der das Modell als „Interactive MCQ Generator" rahmt. Hier bezieht sich Kontextoptimierung auf das bewusste Design von (i) einem Interaktionsprotokoll, das alle Generierungsparameter erfragt, und (ii) harten Output-Einschränkungen, die Ergebnisse maschinenprüfbar machen.

MC-Test verwendet einen endlichen Zustandsworkflow mit drei Phasen. (1) **Konfiguration:** Das Modell sammelt Parameter schrittweise und fragt nach expliziter Bestätigung. Erfragt werden Thema, Zielgruppe, Itemanzahl, Schwierigkeits- und Gewichtsprofil, Optionsformat sowie optionaler curricularer Kontext. (2) **Interne Blaupausenerstellung:** Das Modell führt eine interne Konsistenzprüfung durch, etwa ob Schwierigkeitsgewichte dem angeforderten Profil entsprechen und Options- sowie Antworteinschränkungen erfüllbar sind, ohne Zwischenschritte offenzulegen. (3) **Schema-gesteuerte Ausgabe:** Das Modell gibt ein einzelnes, strikt parsbares JSON-Objekt zurück, das explizite Escape- und Formatierungsregeln befolgt, einschließlich stabiler `question_ids` und einer `schema_version` für Vorwärtskompatibilität. Der Workflow ist in Abb. 1 dargestellt.

![](images/fsm_workflow.png)

Abb. 1: Endlicher Zustandsworkflow der Itemgenerierung.

Für Robustheit über Cloud- und lokale Backends hinweg wird das JSON einer automatisierten Schema- und semantischen Validierung unterzogen. Geprüft werden erforderliche Felder, eindeutige Optionen und gültige Antwortindizes. Optional folgt eine Reparaturschleife, die das Modell zu minimalen Änderungen auffordert, wenn Verstöße erkannt werden.

**Nachgelagerte Lernziele:** Nach der Generierung eines Fragensatzes schlägt das LLM eine kleine Menge von Themenlabels vor. In der Regel sind etwa zehn Labels ausreichend, um die Itembank zu strukturieren. Ein zweiter Prompt leitet Bloom‑ausgerichtete Lernziele pro Item aus Thema und kognitiver Stufe ab. Die Lernziele werden in einer lernendenzentrierten Lernressource kompiliert, die Ziele über Themen und Stufen hinweg zusammenfasst.

### AFTER (Optimiert)

### 3.1 Pädagogische Anforderungen

MC-Test ist für formative Übungssituationen gebaut. Das System soll Lernenden nicht nur Ergebnisse zeigen, sondern **verständliches Feedback** liefern und **Selbstregulation** unterstützen. Daraus ergeben sich fünf Anforderungen:

- **Kognitive Transparenz:** Items tragen ein Bloom-Label (1–3), das Lernende im Dashboard nutzen können.
- **Umsetzbares Feedback:** Erklärungen verknüpfen Antworten mit Lernzielen und typischen Fehlkonzepten.
- **Prüfungsbereitschaft:** Die Sitzung unterstützt Zeitmanagement und reflektiertes Bearbeiten.
- **Didaktische Kontrolle:** Lehrende konfigurieren Tempo-Mechanismen (Cooldowns/Reflexionsfenster) und Schwellenwerte.
- **Messbarkeit:** Logs und strukturierte Itemdaten ermöglichen nachgelagerte Analysen und Iteration.

Wir beschränken uns bewusst auf Bloom 1–3 (Reproduktion, Anwendung, Analyse), weil höhere Niveaus im Kontext aktueller LLMs und im MC-Format weniger zuverlässig abbildbar sind [3].

### 3.2 Systemarchitektur

MC-Test ist als Webanwendung in **Streamlit** umgesetzt. Die Plattform verwaltet Item-Sets, Sitzungen, Antwort-Logs und Exporte. Für die Generierung bindet MC-Test ein LLM-Backend an. Nach der Migration läuft dieses Backend lokal über **Ollama** im containerisierten On-Premises-Betrieb.

Diese Architektur erfüllt zwei Ziele: (1) sie reduziert Datenschutzrisiken, weil Prompts und Lerndaten im institutionellen Netz bleiben, und (2) sie macht Betriebskosten besser planbar. Gleichzeitig entstehen neue Betriebsaufgaben (Monitoring, Ressourcenplanung, Update-Governance).

### 3.3 Didaktisches Datenmodell

Jedes Item enthält:

- **Lernziel(e)**,
- **Topic-Label(s)**,
- **Gewichtung**,
- **Bloom-Level (1–3)**,
- **Antwortoptionen** (inkl. korrekter Option),
- **Erklärungen/Rationales** zu jeder Option,
- optional **Mini-Glossar** und Ressourcen-Hinweise.

Das Modell dient zwei Zwecken zugleich: Es begrenzt die Generierung über ein Schema (Robustheit) und ermöglicht differenzierte, lernendenzentrierte Analytik.

### 3.4 Operationalisierung kognitiver Niveaus

Wir operationalisieren Bloom 1–3 mit konkreten sprachlichen und strukturellen Kriterien:

- **Bloom 1 (Reproduktion):** Abruf von Fakten/Definitionen; Distraktoren prüfen Grundwissen.
- **Bloom 2 (Anwendung):** Anwendung eines Konzepts auf ein Beispiel oder eine Rechen-/Code-Situation.
- **Bloom 3 (Analyse):** Analyse eines Szenarios (z. B. Fehlerdiagnose, Vergleich, Ursache-Wirkung) mit begründeter Auswahl.

Die Labels werden im Interface sichtbar gemacht und als Designannahme behandelt. Für die geplante Evaluation sichern wir die Reliabilität über **Double-Coding** und klar dokumentierte Label-Regeln.

### 3.5 Prompt-Architektur

Die Item-Generierung folgt einer endlichen Interaktionssequenz (**Finite-State-Workflow**):

1. **Kontextaufbau** (Kurs/Topic/Lernziel, gewünschtes Bloom-Level),
2. **Item-Entwurf**,
3. **Schema-Validierung** des JSON-Ergebnisses,
4. **Repair** bei Verstößen (gezielte Nachbesserung statt Neu-Generierung).

Das Ergebnis ist strikt JSON-konform. Dadurch lassen sich nachgelagerte Checks automatisieren (z. B. Distraktorqualität, Konsistenz zwischen Frage und Erklärung).


Der Workflow ist in Abb. 1 dargestellt.

![](images/fsm_workflow.png)

*Abb. 1. Endlicher Zustandsworkflow der Itemgenerierung.*

---

## 4. Learner-Facing Analytics und pädagogische Steuerung

### BEFORE (Original: 4. LERNENDENZENTRIERTE ANALYSEN UND PÄDAGOGISCHE KONTROLLE)

Nach einem Test zeigt MC-Test ein lernendenzentriertes Analyse-Dashboard zur Unterstützung metakognitiver Reflexion. Statt einer einzelnen Punktzahl bietet es vier Ansichten, die curriculare Themen, kognitive Stufen und Konzeptbeherrschung abdecken. In diesem Abschnitt sind Themen grobe Curriculumseinheiten; Konzepte sind feinkörnige Lernziele innerhalb eines Themas.

Die vier Ansichten bilden einen diagnostischen Trichter von Überblick zu Detail. Die Heatmap unterstützt die Mustersuche über Thema × Stufe (einschließlich Vermeidung). Themenbalken und das Radar trennen Inhaltslücken von Prozesslücken, während die Konzeptspalten Muster in konkrete Förderungsziele übersetzen. Das Ziel ist, Lernende von globalen Selbsteinschätzungen zu umsetzbaren Diagnosen zu bewegen [13].

### 4.1 Themenleistungsdiagramm

Abb. 2 zeigt das Themenleistungsdiagramm, das Ergebnisse nach Themenbereich aggregiert, etwa Regression, Klassifikation oder Evaluation. Jeder gestapelte Balken zeigt korrekte, inkorrekte und unbeantwortete Items; die x-Achsenbeschriftungen berichten beantwortet/gesamt, um das Beweisvolumen anzuzeigen. Diese Ansicht hebt Themen hervor, die Förderung benötigen, und Themen, die möglicherweise übersprungen wurden.

![](images/thematic_competence_bar.png)

Abb. 2: Themenleistungsdiagramm (Beispiel).

### 4.2 Kognitives Radardiagramm

Abb. 3 zeigt das kognitive Radardiagramm, das Leistung über die drei Stufen zusammenfasst. Es zeigt an, ob Lernende hauptsächlich Fakten abrufen oder Wissen übertragen und damit argumentieren können. Ausgewogene Formen deuten auf gleichmäßige Entwicklung hin; starke Asymmetrien heben gezielte Entwicklungszonen hervor. Zur Reflexion werden charakteristische Muster interpretativen, nicht-diagnostischen Lernendenarchetypen zugeordnet, etwa Theoretiker, Praktiker und Analytiker.

| | | |
|---|---|---|
| ![](images/crammer_radar.png) | ![](images/practitioner_radar.png) | ![](images/theorist_radar.png) |

Abb. 3: Kognitives Radardiagramm (Beispielprofile).

### 4.3 Konzeptbeherrschungsspalten

Abb. 4 zeigt die Konzeptbeherrschungsspalten. MC-Test gruppiert Items nach getaggten Konzepten, etwa Kreuzvalidierung oder Regularisierung, und klassifiziert jedes Konzept als verstanden, nicht verstanden oder nicht versucht. Ein Konzept gilt als verstanden, wenn mindestens 70 % seiner Items korrekt sind; andernfalls wird es markiert, um Missverständnisse sichtbar zu machen, ohne einzelne Items überzuinterpretieren. Diese Mikroebenen-Ansicht verwandelt Testergebnisse in konkrete Lernziele.

![](images/concept_performance.png)

Abb. 4: Konzeptbeherrschungsspalten (Beispiel).

### 4.4 Themen-×-Kognitiv-Heatmap

Abb. 5 zeigt die Themen-×-Kognitiv-Heatmap, die Themen (Zeilen) und kognitive Stufen (Spalten) kombiniert. Zellen kodieren Leistung und Beweisvolumen: Unbeantwortete Items zählen als 0, und jede Zelle berichtet beantwortet/gesamt. Dies entmutigt strategisches Überspringen und hilft Lernenden zu lokalisieren, ob Schwierigkeiten themenspezifisch oder stufenspezifisch sind.

![](images/topic_cognition_heatmap.png)

Abb. 5: Themen-×-Kognitiv-Heatmap (Beispiel).

Zusammen sind die Ansichten orthogonal. Themenleistung zeigt, was abgedeckt wurde; das Radar zeigt, wie der Lernende über Stufen hinweg abschneidet; die Heatmap verknüpft beide; und Konzeptbeherrschung zoomt in feinkörnige Ziele. Triangulation reduziert blinde Flecken und kann strategische Verhaltensweisen wie das Überspringen höherstufiger Items offenbaren. Abb. 6 zeigt eine exemplarische UI‑Ansicht der Plattform.

![](images/screenshot_mc-test-app.png)

Abb. 6: Exemplarische UI‑Ansicht von MC‑Test.

### 4.5 Feedback und Erklärungen

Für komplexe Items werden Erklärungen um schrittweise Argumentation erweitert. Zur Unterstützung des Vokabularewerbs wird ein zweistufiges Glossarkonzept verwendet: ein Mini-Glossar-Feld für sofortige Hilfe und ein zusammenfassendes PDF-Glossar für die Nachbetrachtung.

Zusätzlich können Lernziele und der Testbericht als PDF exportiert werden. Diese Artefakte bündeln Ergebnisse, Begründungen und Lernziele und dienen der nachgelagerten Reflexion und Planung der nächsten Lernschritte.

### 4.6 Pädagogische Kontrolle: Wartezeiten und Panikmodus

MC-Test steuert die Taktung, um Lesen und Reflexion zu fördern und impulsive Antworten abzuschrecken. Die Taktungsinterventionen werden als Designhypothesen behandelt und ihre Verhaltenseffekte empirisch evaluiert, statt eine erzwungene tiefe Verarbeitung zu behaupten.

Die pädagogische Kontrollschicht bietet drei Mechanismen. **Pre‑Answer‑Wartezeit (Leseunterstützung):** Die Absende‑Schaltfläche bleibt nach dem Laden für eine kurze, itemspezifische Zeit deaktiviert; die Dauer hängt von Itemgewicht und Textlänge ab. **Post‑Answer‑Wartezeit (Reflexionsunterstützung):** Nach Abgabe wird die Navigation zum nächsten Item verzögert, um ein Prüfungsfenster für formatives Feedback zu schaffen [14]; die Dauer skaliert mit der Erklärungslänge (Standard plus zehn Sekunden, erweitert plus zwanzig Sekunden). **Adaptive Fairness (Panikmodus):** Taktung kann Lernende unter Zeitdruck behindern; das System kann Wartezeiten deaktivieren, wenn die Zeit kritisch wird.

Das System überwacht die verbleibende Zeit pro Frage. Fällt sie unter einen Schwellenwert, etwa weniger als 15 s pro Frage, überschreibt der Panikmodus Wartezeiten, sodass Lernende den Versuch beenden können. Da feste Taktung manche Lernende benachteiligen kann, etwa Nutzer von Hilfstechnologien oder Studierende mit Nachteilsausgleich, sind alle Wartezeiten pro Kurs konfigurierbar und können deaktiviert oder angepasst werden. Zusammenfassend priorisiert der Panikmodus Fertigstellung und Fairness bei hohem Zeitdruck.

### 4.7 Itemdiagnostik über Konfidenz-Matrix

Ergänzend zu lernendenzentrierten Dashboards stellt MC-Test eine instruktorenseitige Itemdiagnostik bereit. Pro Frage kann eine kumulierte Konfidenz‑Matrix angezeigt werden, die die Kategorien sicher und unsicher mit richtig und falsch kombiniert. Die Darstellung macht potenziell problematische Items sichtbar und unterstützt die Diagnose von Fehlkalibrierung, etwa wenn hohe Anteile sicher und falsch auf Missverständnisse oder fehlerhafte Lösungsschlüssel hinweisen. Die Aggregation schließt Autoreneinschätzungen aus, um Verzerrungen zu reduzieren. Der Zugriff ist rollenbasiert. Admins sehen die Matrix stets. Autorinnen und Autoren temporärer Sets sehen sie nur in der aktiven Session oder, bei reserviertem Pseudonym, innerhalb der Löschfrist.

### AFTER (Optimiert)

Die Dashboards bilden einen „Trichter“: Sie beginnen mit Überblick und führen zu konkreten Handlungen. Alle Views sind so gestaltet, dass Lernende sofort sehen, *was* sie wiederholen sollten und *warum*.

### 4.1 Topic Performance

Gestapelte Balken zeigen pro Topic den Anteil korrekter, falscher und nicht beantworteter Items. So können Lernende Themen priorisieren und Wiederholungen planen.


![](images/thematic_competence_bar.png)


*Abb. 2. Topic-Performance-Chart: Leistung nach Themen, getrennt nach korrekt/falsch/unbeantwortet.*

### 4.2 Kognitives Radar

Radar-Charts fassen Leistung über Bloom 1–3 zusammen. Sie machen ein „kognitives Profil“ sichtbar: Lernende erkennen, ob sie vor allem Reproduktion beherrschen oder auch Anwendung/Analyse stabil gelingt.


| | | |
|---|---|---|
| ![](images/crammer_radar.png) | ![](images/practitioner_radar.png) | ![](images/theorist_radar.png) |


*Abb. 3. Kognitives Radar: Beispielhafte Performance über Bloom 1–3 (Reproduktion, Anwendung, Analyse).*

### 4.3 Konzept-Spalten

Feingranulare Konzepte werden in drei Spalten gruppiert: **verstanden**, **nicht verstanden** und **nicht versucht**. Schwellenwerte sind kurskonfigurierbar. Die Darstellung erleichtert es, aus Ergebnissen konkrete Lernschritte abzuleiten.


![](images/concept_performance.png)


*Abb. 4. Konzept-Spalten: Gruppierung feingranularer Konzepte in verstanden, nicht versucht und nicht verstanden.*

### 4.4 Topic×Cognitive-Heatmap

Die Heatmap kombiniert Topics (Zeilen) und Bloom-Levels (Spalten). Farbcodierung zeigt Performance, Overlays die Item-Anzahl pro Zelle. Lernende sehen damit schnell, *wo* es hängt und *welche kognitive Art* von Aufgaben besonders schwierig ist.


![](images/topic_cognition_heatmap.png)


*Abb. 5. Topic×Cognitive-Heatmap (Topics × Bloom-Level) mit farbcodierter Performance und Item-Anzahlen.*

### 4.5 Feedback und Erklärungen

Nach jeder Sitzung liefert MC-Test Rationales zu jeder Antwortoption. Lernende erhalten so nicht nur „richtig/falsch“, sondern eine Begründung, die an Lernziele und typische Misskonzepte anschließt. Zusätzlich können Lernziele, Topics und Ressourcen exportiert werden.

### 4.6 Pacing

MC-Test reduziert Rapid Guessing durch zwei Mechanismen:

- **Pre-Answer-Cooldown:** ein kurzes Lesefenster vor der ersten Antwort (Lesesupport).
- **Reflexionsfenster:** kurze Wartezeit nach einer Antwort, die Reflexion erzwingt.

Der **Panikmodus** erlaubt es, Pacing in Zeitdrucksituationen zu deaktivieren. Alle Parameter sind kurskonfigurierbar (Barrierefreiheit, unterschiedliche Kurskulturen). Ziel ist nicht „Strafe“, sondern ein *Nudge* zu reflektiertem Bearbeiten.


![](images/screenshot_mc-test-app.png)


*Abb. 6. MC-Test-Oberfläche: Sitzungsfeedback und Topic-Performance im Dashboard.*

---

## 5. Implementierung und Migration zum lokalen LLM-Backend

### BEFORE (Original: 5. IMPLEMENTIERUNG UND MIGRATION ZU LOKALEM LLM-BACKEND)

Die Plattform wurde von kommerziellen Cloud-APIs zu einem institutionellen Server mit lokalem LLM-Backend (Ollama) migriert, um Datenschutz und Nachhaltigkeit zu adressieren.

- **Prompt-Refactoring:** Der Systemprompt wurde an lokale Modelleigenschaften angepasst und priorisiert JSON-Validität und Robustheit.
- **Datenschutz:** Lokales Deployment stellt sicher, dass keine Studierendendaten die Institution verlassen, entsprechend den Prinzipien von „Privacy by Design“ [11], [12].
- **Nachhaltigkeit:** On-Premises-Hosting mindert die Kosten und Rate-Limits kommerzieller API-Nutzung.
- **Datenminimierung und Logging:** Gespeichert wird nur, was für Bewertung und Analysen erforderlich ist (Antworten, Zeitstempel, aggregierte Punktzahlen) sowie minimale operative Metadaten und Sicherheits‑Audit‑Logs. Prompts vermeiden persönliche Identifikatoren, und das lokale Deployment hält sowohl Studierendendaten als auch Prompt‑Logik innerhalb der institutionellen Umgebung. Zugriff auf Logs und Datenbanken ist auf autorisiertes Personal beschränkt; Aufbewahrungsrichtlinien begrenzen die Speicherdauer.
- **Anonymität und Pseudonyme:** MC-Test unterstützt anonyme Teilnahme ohne persönliche Konten. Lernende wählen ein Pseudonym aus einer vordefinierten Liste, etwa Nobel‑ oder Turing‑Preisträger, um Sitzungsdaten für Fortschrittsanzeigen und aggregierte Analysen konsistent zu halten, ohne reale Identifikation zu ermöglichen.
- **Rollenbasierte Einsicht:** Itemdiagnostische Aggregationen sind ausschließlich für Admins sowie Autorinnen und Autoren sichtbar. Reguläre Lernende sehen keine Aggregationen.
- **Open-Source-Verfügbarkeit:** Zur Unterstützung von Transparenz und Reproduzierbarkeit wird die MC-Test-Streamlit-Anwendung unter MIT-Lizenz veröffentlicht; das Repository enthält Deployment- und Konfigurationsdokumentation, etwa Docker Compose, sowie die schema-gesteuerten Artefakte, die in der lokalen Inferenz-Pipeline verwendet werden.

### AFTER (Optimiert)

MC-Test wurde zunächst mit kommerziellen LLM-APIs prototypisiert und anschließend auf ein lokales LLM-Backend migriert. Diese Migration war mehr als ein „Backend-Tausch“: Sie erforderte Prompt-Refactoring (stärkere Fokussierung auf JSON-Validität), robuste Fehlerbehandlung sowie Anpassungen im Deployment.

On-Premises-Betrieb stärkt Datenschutz, senkt variable Kosten und reduziert Abhängigkeiten von Rate Limits. Gleichzeitig steigt die Verantwortung für Betrieb und Qualität: Monitoring, Ressourcenplanung und Governance für Modellupdates werden zentral.

---

## 6. Evaluationsdesign und Ausblick

### BEFORE (Original: 6. EVALUIERUNGSDESIGN UND AUSBLICK)

### 6.1 Geplantes Studiendesign

Geplant sind Piloteinsätze in MINT‑Modulen. Erhoben werden Systemlogs, darunter Taktungsentscheidungen, kognitive Profile und Antwortzeiten, sowie Vor‑ und Nach‑Fragebögen zu metakognitivem Bewusstsein und wahrgenommener Nützlichkeit. Ergänzend werden Interviews durchgeführt. Darauf folgen vergleichende Designs, etwa A/B‑Studien oder phasenweise Einführungen, um zu prüfen, ob pädagogische Kontrolle Schnellraten‑Indikatoren reduziert und Lernstrategien oder Lernergebnisse verändert. Zusätzlich wird Labelstabilität geprüft, und es werden grundlegende Itemstatistiken zur Unterstützung psychometrischer Interpretation berichtet.

Schnellraten‑Indikatoren werden aus Logs abgeleitet, darunter Antwortzeiten unter itemspezifischen Schwellenwerten, Antwortraten mit geringem Bearbeitungsaufwand pro Lernendem und Antwortzeitveränderungen vor und nach Taktung [9], [10]. Bedingungen werden verglichen, etwa aktivierte versus deaktivierte Taktung sowie gestaffelte Einführung, mit Kontrolle für Itemschwierigkeit und Position. Untersucht wird außerdem nachgelagertes Verhalten wie Feedback‑Betrachtungszeit und Optionsprüfung.

Zusätzlich ist geplant, kumulierte Konfidenz-Muster als Indikatoren der Itemdiagnostik zu analysieren und mit klassischen Itemstatistiken zu triangulieren, um potenziell missverständliche Items früh zu markieren.

Zur Sicherung der Interpretierbarkeit werden kognitive Stufenlabels als messbare Designannahme behandelt. Die Labels werden mit einer Rubrik doppelt codiert, und es wird Interrater‑Übereinstimmung berichtet, darunter prozentuale Übereinstimmung und Cohens Kappa. Zusätzlich werden grundlegende Itemstatistiken, etwa Schwierigkeit und Diskrimination, berechnet, um Items niedriger Qualität oder mehrdeutige Items zu markieren, bevor kognitive Profile im großen Maßstab interpretiert werden.

Vorläufige Beobachtungen deuten darauf hin, dass Lernende die Aufschlüsselung nach kognitiver Stufe und transparente Begründungen schätzen. Feedback zur Taktung war gemischt und motivierte den später hinzugefügten adaptiven Panikmodus. Diese Beobachtungen sind explorativ; vorgesehen sind kontrollierte Vergleiche unter Nutzung von Verhaltenslogs und selbstberichteten Maßen.

### 6.2 Vorläufige Ergebnisse: Systemusability

Um die Benutzererfahrung (UX) und technische Akzeptanz der Plattform zu validieren, wurde eine standardisierte Usability-Evaluation mit der System Usability Scale (SUS) [15] durchgeführt. Die Umfrage wurde an einer Pilotkohorte von 20 Teilnehmenden durchgeführt und ergab einen mittleren SUS-Score von 70,38.

Nach der Adjektiv‑Bewertungsskala von Bangor et al. [1] liegt der mittlere SUS‑Score von MC‑Test in der Kategorie „OK“, was auf gute Akzeptanz hindeutet. Abb. 7 zeigt individuelle Scores im Verhältnis zu Akzeptabilitätsbändern („Acceptable“, „Good“, „Excellent“) und weist eine linksschief verteilte Verteilung aus. Die meisten Teilnehmenden bewerteten das System als einfach zu bedienen, mit einigen niedrigeren Ausreißern.

![](images/sus_score_distribution.png)

Abb. 7: SUS-Score-Verteilung der Pilotstudie.

Wichtig ist, dass SUS primär wahrgenommene Usability erfasst; es etabliert keine Lernvorteile oder Verhaltenseffekte. Diese Aspekte werden in nachfolgenden Studien unter Verwendung logbasierter Schnellraten‑Indikatoren, Lernendenfeedback zu Fairness und Autonomie sowie, soweit möglich, Lernergebnismaßen untersucht.

### 6.3 Limitationen

Dieses Paper trägt ein Systemdesign und vorläufige Usability‑Befunde bei. Bei der Interpretation der Ergebnisse sind folgende Einschränkungen zu berücksichtigen:

1. **Fokus auf Usability statt Lerneffekt:** Die Pilotstudie (N = 20, SUS = 70,38) validiert technische Akzeptanz und Benutzerfreundlichkeit, liefert aber keinen empirischen Nachweis, dass Dashboards oder Taktungsmechanismen Lernergebnisse verbessern. Der kausale Zusammenhang zwischen Konzeptbeherrschungsspalten und Klausurleistung ist Gegenstand der nächsten Evaluationsphase.
2. **Spannungsfeld Autonomie vs. Taktung:** Die Wartezeiten (Pre‑/Post‑Answer) basieren auf der Annahme, dass erzwungene Entschleunigung Schnellraten reduziert. Diese Eingriffe können von leistungsstarken Studierenden als hinderlich wahrgenommen werden. Der Panikmodus mildert Zeitdruckeffekte, dennoch muss die Balance zwischen pädagogischer Lenkung und Frustration in A/B‑Tests weiter kalibriert werden.
3. **Interpretative KI‑Labels:** Trotz der Beschränkung auf Bloom‑Stufen 1–3 bleiben die vom LLM generierten Labels (Reproduktion, Anwendung, Analyse) interpretativ. Ohne menschliche Überprüfung besteht das Risiko von Fehlklassifikationen, die lernendenzentrierte Profile verzerren. Zukünftige Analysen berichten Interrater‑Übereinstimmung, z. B. Cohens Kappa.
4. **Technische Hürden lokaler LLMs:** Die lokale Inferenz (Ollama) gewährleistet Datensouveränität, kann aber höhere Latenzen verursachen. Dies kann die Skalierbarkeit bei hoher gleichzeitiger Generierung begrenzen und muss in Lasttests weiter untersucht werden.

Aktuelle Studien bewerten die psychometrischen Eigenschaften LLM‑generierter Fragen und verstärken die Notwendigkeit, Itemstatistiken auf Einzelitemebene zu berichten, wenn KI‑generierte MCQs in der Praxis verwendet werden [2]. Über klassische Itemanalyse hinaus kann zukünftige Arbeit auch generative Studierenden‑Simulationen nutzen, um mehrdeutige oder niedrig diskriminierende Items vor Einsatz zu markieren [16].

### AFTER (Optimiert)

### 6.1 Technische Akzeptanz (SUS)

Eine standardisierte SUS-Erhebung (*N* = 20) dient als erster Nachweis technischer Akzeptanz. Der Mittelwert liegt bei **70,38** und fällt damit in die Kategorie „OK“ [15].


![](images/sus_score_distribution.png)


*Abb. 7. Verteilung der SUS-Scores (*N* = 20) mit Adjektiv-Rating-Bändern nach Bangor et al. [15].*

### 6.2 Geplante Wirkungsanalyse (Logs + Verläufe)

Für die Wirkungsanalyse planen wir eine logbasierte Studie in Pilotveranstaltungen. Wir erfassen u. a. Antwortzeiten, Pacing-Interaktionen, kognitive Profile und Verlaufsmuster über Sitzungen hinweg. Rapid-Guessing-Indikatoren leiten wir aus Response Times und Mustern geringer Anstrengung ab.

### 6.3 Limitationen

1. **SUS misst Usability, nicht Lernzuwachs.** Aussagen zu Lernwirkungen erfordern ergänzende Designs (z. B. Vorher/Nachher, Kontrollgruppen, längsschnittliche Nutzungsdaten).
2. **Bloom-Labels sind eine zentrale Annahme.** Wir adressieren Reliabilität über Double-Coding und Auswertungsregeln, benötigen aber zusätzliche psychometrische Analysen.
3. **Scope: Bloom 1–3.** Höhere kognitive Niveaus sind im Kontext aktueller LLMs und im MC-Format weniger verlässlich abbildbar [3].

---

## 7. Fazit

### BEFORE (Original: 7. FAZIT)

MC-Test demonstriert, wie LLM-gestützte Itemgenerierung in eine formative Multiple-Choice-Übungsplattform integriert werden kann, ohne Lerndaten auszulagern. Das System kombiniert (i) ein didaktisches Itemmodell mit Labels der Bloom‑Stufen 1–3, (ii) schema-beschränkte Generierung über einen endlichen Zustandsworkflow und (iii) lernendenzentrierte Dashboards, die Leistung mit Lernzielen über Themen und kognitive Stufen hinweg verbinden. Eine konfigurierbare Taktungsschicht (Vor-/Nach-Antwort-Wartezeiten, Panikmodus) zielt auf Schnellraten ab und bewahrt gleichzeitig Fairness unter Zeitdruck.

Die Beiträge sind dreifach: (1) ein operationales didaktisches Itemmodell, das Lernziele, kognitive Stufen und formative Begründungen koppelt; (2) eine robuste Generierungspipeline, die parsbares JSON produziert und automatisierte Prüfungen unterstützt; und (3) eine On‑Premises‑Architektur für lokale, schema‑beschränkte LLM‑Inferenz mit Ollama, geeignet für datenschutzsensible Lehrumgebungen. Eine Pilot‑Usability‑Studie zeigt gute Akzeptanz (SUS 70,38, N = 20). Laufende Arbeiten evaluieren Verhaltenseffekte, Labelzuverlässigkeit und Item‑Psychometrie mittels vergleichender und logbasierter Studien.

### AFTER (Optimiert)

MC-Test zeigt, wie KI-gestützte Item-Generierung in eine Plattform für formative MC-Übung integriert werden kann, ohne sich auf eine Punktzahl zu beschränken. Das didaktische Itemmodell, die schema-gebundene Generierungspipeline, die lernendenzentrierten Dashboards und Pacing-Mechanismen adressieren zwei Kernprobleme: Qualitätssicherung bei skalierter Item-Erzeugung und lernförderliche Rückmeldung.

Die Migration zu einem lokalen LLM-Backend (Ollama) macht privacy-preserving Deployments praktikabel, verlangt jedoch sorgfältige Prompt- und Betriebsanpassungen. Als nächste Schritte planen wir eine logbasierte Wirkungsevaluation und vertiefte psychometrische Prüfungen der generierten Items.

---

## Literatur

### BEFORE (Original: LITERATUR)

[1] A. Bangor, P. T. Kortum, and J. T. Miller, "Determining what individual SUS scores mean: Adding an adjective rating scale," Journal of Usability Studies, vol. 4, no. 3, pp. 114-123, 2009.


[2] S. Bhandari, Y. Liu, Y. Kwak, and Z. A. Pardos, "Evaluating the psychometric properties of ChatGPT-generated questions," Computers and Education: Artificial Intelligence, vol. 7, Art. 100284, 2024, doi: 10.1016/j.caeai.2024.100284.


[3] T. Weber, M. Brandmaier, A. Schmidt, and S. Mayer, "Significant Productivity Gains through Programming with Large Language Models," Proc. ACM Hum.-Comput. Interact., vol. 8, EICS, Art. 256, 2024, doi:10.1145/3661145.


[4] N. Scaria, S. D. Chenna, and D. Subramani, "Automated Educational Question Generation at Different Bloom's Skill Levels Using Large Language Models: Strategies and Evaluation," in Artificial Intelligence in Education (AIED 2024), LNAI vol. 14830, pp. 165-179, 2024, doi: 10.1007/978-3-031-64299-9_12.


[5] P. Stalder, et al., "Ensuring Quality in AI-Generated Multiple-Choice Questions for Higher Education with the QUEST Framework," in Communications in Computer and Information Science, Springer, 2024.


[6] R. Bodily and K. Verbert, "Trends and issues in student-facing learning analytics reporting systems research," in Proc. 7th Int. Conf. Learning Analytics & Knowledge (LAK '17), Vancouver, BC, Canada, Mar. 2017, pp. 309-318, doi: 10.1145/3027385.3027403.


[7] L. de Vreugd, et al., "Learning Analytics Dashboard Design and Evaluation to Support Student Self-Regulation of Study Behavior," Journal of Learning Analytics, vol. 11, no. 3, 2024.


[8] I. Jivet, M. Scheffel, M. Specht, and H. Drachsler, "License to evaluate: Preparing learning analytics dashboards for educational practice," in Proc. 8th Int. Conf. Learning Analytics & Knowledge (LAK '18), Sydney, NSW, Australia, Mar. 2018, pp. 31-40, doi: 10.1145/3170358.3170421.


[9] S. L. Wise and C. E. DeMars, "An application of item response time: The effort-moderated model," Journal of Educational Measurement, vol. 43, pp. 19-38, 2006.


[10] S. L. Wise, "Rapid-guessing behavior: Its identification, interpretation, and implications," Educational Measurement: Issues and Practice, vol. 36, no. 4, pp. 52-61, 2017, doi:10.1111/emip.12165.


[11] H. Drachsler and W. Greller, "Privacy and Analytics: It's a DELICATE Issue-A Checklist for Trusted Learning Analytics," in Proceedings of the Sixth International Conference on Learning Analytics & Knowledge, Edinburgh, UK, 2016, pp. 89-98.


[12] Y. Shanmugarasa, M. Ding, M. A. P. Chamikara, and T. Rakotoarivelo, "SoK: The Privacy Paradox of Large Language Models: Advancements, Privacy Risks, and Mitigation," arXiv preprint arXiv:2506.12699, 2025.


[13] Z. Yan and D. Carless, "Self-Assessment Is About More Than Self: The Enabling Role of Feedback Literacy," Assessment & Evaluation in Higher Education, vol. 47, no. 7, pp. 1116-1128, 2022.


[14] N. E. Winstone and D. Carless, Designing Effective Feedback Processes in Higher Education: A Learning-Focused Approach. London: Routledge, 2019.


[15] J. Brooke, "SUS: A 'Quick and Dirty' Usability Scale," in Usability Evaluation in Industry, P. W. Jordan, B. Thomas, B. A. Weerdmeester, and I. L. McClelland, Eds. London, U.K.: Taylor & Francis, 1996, pp. 189-194.


[16] X. Lu and X. Wang, "Generative Students: Using LLM-Simulated Student Profiles to Support Question Item Evaluation," in Proc. 11th ACM Conf. on Learning @ Scale (L@S '24), 2024, pp. 16-27, doi: 10.1145/3657604.3662031.

### AFTER (Optimiert)

[1] T. Weber, M. Brandmaier, A. Schmidt, and S. Mayer, “Significant Productivity Gains through Programming with Large Language Models,” Proc. ACM Hum.-Comput. Interact., vol. 8, EICS, Art. 256, 2024, doi:10.1145/3661145.  
[2] S. Bhandari, Y. Liu, Y. Kwak, and Z. A. Pardos, “Evaluating the psychometric properties of ChatGPT-generated questions,” Computers and Education: Artificial Intelligence, vol. 7, Art. 100284, 2024, doi: 10.1016/j.caeai.2024.100284.  
[3] N. Scaria, S. D. Chenna, and D. Subramani, “Automated Educational Question Generation at Different Bloom’s Skill Levels Using Large Language Models: Strategies and Evaluation,” in Artificial Intelligence in Education (AIED 2024), LNAI vol. 14830, pp. 165-179, 2024, doi: 10.1007/978-3-031-64299-9_12.  
[4] P. Stalder, et al., “Ensuring Quality in AI-Generated Multiple-Choice Questions for Higher Education with the QUEST Framework,” in Communications in Computer and Information Science, Springer, 2024.  
[5] R. Bodily and K. Verbert, “Trends and issues in student-facing learning analytics reporting systems research,” in Proc. 7th Int. Conf. Learning Analytics & Knowledge (LAK ’17), Vancouver, BC, Canada, Mar. 2017, pp. 309-318, doi: 10.1145/3027385.3027403.  
[6] L. de Vreugd, et al., “Learning Analytics Dashboard Design and Evaluation to Support Student Self-Regulation of Study Behavior,” Journal of Learning Analytics, vol. 11, no. 3, 2024.  
[7] I. Jivet, M. Scheffel, M. Specht, and H. Drachsler, “License to evaluate: Preparing learning analytics dashboards for educational practice,” in Proc. 8th Int. Conf. Learning Analytics & Knowledge (LAK ’18), Sydney, NSW, Australia, Mar. 2018, pp. 31-40, doi: 10.1145/3170358.3170421.  
[8] S. L. Wise and C. E. DeMars, “An application of item response time: The effort-moderated model,” Journal of Educational Measurement, vol. 43, pp. 19-38, 2006.  
[9] S. L. Wise, “Rapid-guessing behavior: Its identification, interpretation, and implications,” Educational Measurement: Issues and Practice, vol. 36, no. 4, pp. 52-61, 2017, doi:10.1111/emip.12165.  
[10] H. Drachsler and W. Greller, “Privacy and Analytics: It’s a DELICATE Issue-A Checklist for Trusted Learning Analytics,” in Proceedings of the Sixth International Conference on Learning Analytics & Knowledge, Edinburgh, UK, 2016, pp. 89-98.  
[11] Y. Shanmugarasa, M. Ding, M. A. P. Chamikara, and T. Rakotoarivelo, “SoK: The Privacy Paradox of Large Language Models: Advancements, Privacy Risks, and Mitigation,” arXiv preprint arXiv:2506.12699, 2025.  
[12] Z. Yan and D. Carless, “Self-Assessment Is About More Than Self: The Enabling Role of Feedback Literacy,” Assessment & Evaluation in Higher Education, vol. 47, no. 7, pp. 1116-1128, 2022.  
[13] N. E. Winstone and D. Carless, Designing Effective Feedback Processes in Higher Education: A Learning-Focused Approach. London: Routledge, 2019.  
[14] J. Brooke, “SUS: A ‘Quick and Dirty’ Usability Scale,” in Usability Evaluation in Industry, P. W. Jordan, B. Thomas, B. A. Weerdmeester, and I. L. McClelland, Eds. London, U.K.: Taylor & Francis, 1996, pp. 189-194.  
[15] A. Bangor, P. T. Kortum, and J. T. Miller, “Determining what individual SUS scores mean: Adding an adjective rating scale,” Journal of Usability Studies, vol. 4, no. 3, pp. 114-123, 2009.  
[16] X. Lu and X. Wang, “Generative Students: Using LLM-Simulated Student Profiles to Support Question Item Evaluation,” in Proc. 11th ACM Conf. on Learning @ Scale (L@S ’24), 2024, pp. 16-27, doi: 10.1145/3657604.3662031.

---
