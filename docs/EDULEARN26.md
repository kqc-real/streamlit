# Von summativen Multiple-Choice-Tests zu formativer Übung: KI-gestützte Fragengenerierung, kognitive Analysen und adaptive Taktung

**R. Bimberg, P. Kubica, K. Quibeldey-Cirkel**  
Technische Hochschule Mittelhessen (DEUTSCHLAND)  
IU Internationale Hochschule (DEUTSCHLAND)

## Zusammenfassung

Multiple-Choice-Prüfungen (MC) skalieren gut für große Kohorten, doch viele Plattformen liefern nur eine Punktzahl. Wir stellen MC-Test vor, eine datenschutzkonforme Webplattform für formatives MC-Training, die LLM-gestützte Itemgenerierung mit strukturiertem Feedback, lernendenzentrierten Analysen und zeitbewusster Taktung verbindet.

MC-Test verwendet ein didaktisches Itemmodell, das jedes Item mit einem Lernziel, Thema, Gewichtung und einer operationalisierten kognitiven Stufe verknüpft (Bloom 1-3: Reproduktion, Anwendung, Analyse). Items werden durch einen endlichen Prompt-Workflow erzeugt und als schema-valides JSON ausgegeben; automatisierte Validierung und Reparatur erhöhen die Robustheit und ermöglichen nachgelagerte Itemstatistiken.

Nach jeder Sitzung erhalten Lernende Begründungen für jede Antwortoption, ein Mini-Glossar sowie exportierbare Lernziele und Lernressourcen. Dashboards visualisieren die Leistung nach Thema und kognitiver Stufe (Themenleistungsdiagramm, kognitives Radarprofil, Konzeptbeherrschungsspalten, Themen-×-Kognitiv-Heatmap). Um schnelles Raten zu verhindern, wendet MC-Test konfigurierbare Wartezeiten vor und nach der Antwort an; der Panikmodus lockert die Taktung, wenn die verbleibende Zeit pro Item kritisch wird. MC-Test läuft containerisiert auf institutionellen Servern mit lokalem LLM-Backend, sodass Prompts und Lerndaten innerhalb der institutionellen Infrastruktur verbleiben; Pseudonyme ermöglichen anonyme Teilnahme. Eine Pilotusability-Studie (SUS, N = 20) zeigt gute Akzeptanz (Mittelwert 70,38/100, ‚OK' [15]). Open-Source (MIT): https://github.com/kqc-real/streamlit.

**Schlüsselwörter:** Künstliche Intelligenz in der Bildung, Multiple-Choice-Fragengenerierung, Blooms Taxonomie, lernendenzentrierte Lernanalysen, selbstreguliertes Lernen, Erkennung schnellen Ratens, adaptive Taktung, datenschutzwahrende lokale Sprachmodelle, formative Bewertung.

## 1. EINLEITUNG

Multiple-Choice-Fragen (MC) werden an Hochschulen häufig eingesetzt, da sie gut skalieren, objektive Bewertung ermöglichen und sich in großen Kohorten leicht durchführen lassen. Typische MC-Plattformen liefern jedoch kaum mehr als eine Gesamtpunktzahl und itemweise Korrektheit und bieten damit wenig Unterstützung für metakognitive Reflexion und strategische Prüfungsvorbereitung. Lernende erhalten oft Feedback, das zu grob ist, um ihre Lernstrategien zu informieren: Sie wissen, dass sie versagt haben, aber nicht warum.

Große Sprachmodelle (LLMs) können mittlerweile MC-Items in großem Umfang generieren. Dies verlagert den Engpass vom Verfassen zur Qualitätssicherung: Items müssen valide, angemessen schwierig und auf Lernziele abgestimmt sein. Wenn Metadaten wie Thema, Schwierigkeit und kognitive Stufe explizit erfasst werden, kann MC-Training auch lernendenzentrierte Analysen statt nur Punktzahlen liefern. Frühere Arbeiten zeigen, dass LLM-generierte MCQs in manchen Kontexten wettbewerbsfähige psychometrische Eigenschaften erreichen können, unterstreichen aber auch die Notwendigkeit systematischer Validierung auf Itemebene, statt die Qualität allein aus der Generierung abzuleiten [2]. LLM-basierte Coding-Assistenten reduzieren zudem den Implementierungsaufwand und ermöglichen Fachexperten die Entwicklung maßgeschneiderter Bildungstools [1].

Wir haben MC-Test entwickelt, eine webbasierte Plattform, die kombiniert:

- Ein didaktisches Itemmodell, das jedes Item mit Lernzielen, Thema und kognitiven Stufenlabeln (Bloom 1-3) verknüpft.
- Eine LLM-Pipeline, die schema-valides JSON über eine endliche Zustandsinteraktion und automatisierte Validierung/Reparatur erzeugt.
- Lernendenzentrierte Analysen, die Leistung nach Thema und kognitiver Stufe visualisieren.
- Pädagogische Kontrollen (Wartezeiten, Reflexionsfenster, adaptive Taktung) zur Verringerung schnellen Ratens.

MC-Test begann mit kommerziellen LLM-APIs und wurde später zu einem lokalen LLM-Backend über Ollama migriert. Wir adressieren drei Forschungsfragen:

- **RQ1:** Wie können Klassifikationen kognitiver Stufen in einer lernendenzentrierten Bewertungsplattform operationalisiert werden?
- **RQ2:** Wie können LLMs über robustes Prompt-Engineering eingebettet werden, um psychometrische Qualitätsprüfungen und zuverlässige Itemgenerierung zu unterstützen?
- **RQ3:** Welche Designüberlegungen ergeben sich bei der Migration zu einem lokalen LLM-Backend?

Wir berichten über Design und Implementierung von MC-Test und liefern erste Usability-Befunde (SUS, N = 20, Mittelwert = 70,38). Abschnitt 6 skizziert die geplante logbasierte Evaluation von Verhaltenseffekten (schnelles Raten) und lernbezogenen Ergebnissen. Die Hauptbeiträge sind:

- Operationalisierung von Bloom 1-3 in einem didaktischen Itemmodell und Darstellung durch vier lernendenzentrierte Ansichten (Themenleistungsdiagramm, kognitives Radardiagramm, Konzeptbeherrschungsspalten, Themen-×-Kognitiv-Heatmap) (RQ1).
- Implementierung einer kontextoptimierten, schema-beschränkten Itemgenerierungs-Pipeline (endliche Zustandsinteraktion + JSON-Validierung/Reparatur), die robuste Generierung und nachgelagerte psychometrische Prüfungen unterstützt (RQ2).
- Ableitung von Design- und Deployment-Erkenntnissen aus der Migration von kommerziellen APIs zu einem datenschutzwahrenden lokalen LLM-Backend (Ollama) in einer containerisierten On-Premises-Architektur mit Fokus auf Robustheit und Datensouveränität (RQ3).

MC-Test zielt auf formatives MC-Training in MINT-Fächern (Bloom 1-3) ab; höherstufige Aufgaben werden aufgrund aktueller LLM-Limitierungen ausgeschlossen [3]. Die Usability ist validiert (SUS = 70,38, ‚OK' [15]), aber Lerneffekte und Verhaltensänderungen erfordern Folgestudien (Abschnitt 6). Kognitive Labels werden doppelt codiert (Kappa geplant), und menschliche Itemprüfung bleibt obligatorisch. Die Taktung ist kurskonfigurierbar für Barrierefreiheit.

## 2. THEORETISCHER HINTERGRUND UND VERWANDTE ARBEITEN

**Kognitive Taxonomien und KI-Validität:** Blooms Taxonomie liefert seit langem einen Rahmen zur Differenzierung kognitiver Komplexität. Während LLMs gut darin sind, Inhalte für niedrigere taxonomische Stufen zu generieren (Erinnern, Verstehen), zeigen aktuelle Studien erhebliche Zuverlässigkeitsprobleme, wenn Modelle versuchen, Aufgaben für höherstufige Bewertung oder Kreation ohne Human-in-the-Loop-Verifikation zu erzeugen [3]. Daher erfordert automatisierte MC-Generierung strenge Einschränkungen zur Sicherstellung semantischer Validität [4].

**Lernendenzentrierte Lernanalysen & Selbstregulation:** Lernendenzentrierte (oft als studierendenzentriert bezeichnete) Lernanalysen-Dashboards zielen darauf ab, Lernenden interpretierbare Visualisierungen zur Unterstützung selbstregulierten Lernens bereitzustellen [5]. Die Forschung legt jedoch nahe, dass reine Datenvisualisierung oft unzureichend ist; effektive Systeme müssen aktive Anleitung oder „Nudges" bieten, um Erkenntnisse in Verhaltensänderung zu übersetzen [6]. Zudem liefern frühere Arbeiten Design- und Evaluierungsempfehlungen für lernendenzentrierte Lernanalysen-Dashboards [7]. MC-Test adressiert dies durch Kombination von Analysen mit aktiven Taktungsmechanismen.

**Testbearbeitungsaufwand und schnelles Raten:** Bei computergestützter Bewertung können ungewöhnlich kurze Antwortzeiten auf reduzierten Testbearbeitungsaufwand (z. B. schnelles Raten) statt auf Wissensmangel hindeuten. Antwortzeit-Aufwandsmetriken und aufwandsmoderierte Modelle nutzen Antwortzeiten, um solche Antworten zu markieren oder abzuwerten, und liefern praktische Orientierung für die Festlegung von Antwortzeitenschwellen und die Interpretation von Schnellrate-Indikatoren in Low-Stakes-Kontexten [8], [9].

**Datenschutz bei generativer KI:** Die Verwendung kommerzieller LLM-APIs in der Bildung wirft erhebliche Datenschutzbedenken bezüglich Datenlecks und DSGVO-Konformität auf [10]. Aktuelle Arbeiten heben das „Privacy Paradox" von LLMs hervor und legen nahe, dass On-Premises-Deployment (lokale LLMs) eine starke Minderungsoption für sensible Bildungskontexte darstellt [11].

## 3. SYSTEMDESIGN: DIE MC-TEST-PLATTFORM

### 3.1 Pädagogische Anforderungen

MC-Test wurde für formative Bewertung in MINT-Kursen konzipiert. Zentrale Anforderungen umfassten:

- **Kognitive Transparenz:** Items müssen nach kognitiver Stufe klassifiziert sein.
- **Umsetzbares Feedback:** Erklärungen müssen an Lernziele anknüpfen.
- **Prüfungsbereitschaft:** Unterstützung für Zeitmanagementfähigkeiten.
- **Didaktische Kontrolle:** Lehrende müssen Kontrolle über Itemqualität behalten, inkl. itemdiagnostischer Hinweise (z. B. Konfidenz-Muster), um missverständliche Items gezielt zu überarbeiten.

### 3.2 Systemarchitektur

Die Anwendung ist mit dem Python-Framework Streamlit implementiert und wurde von einem cloudbasierten Prototyp zu einer robusten, containerisierten Microservice-Architektur migriert. Der gesamte Stack wird über Docker Compose orchestriert und auf einem institutionellen On-Premises-Server bereitgestellt, um volle Datensouveränität zu gewährleisten. Zentrale Komponenten umfassen:

- **Datenpersistenz:** Eine PostgreSQL-Datenbank ersetzt leichtgewichtige dateibasierte Speicherung, um gleichzeitige Benutzersitzungen und komplexe relationale Daten (Benutzerprofile, Audit-Logs) zuverlässig zu verarbeiten.
- **Datenschutzkonforme Darstellung:** Um Datenlecks an externe Content Delivery Networks (CDNs) zu vermeiden, werden mathematische Formeln mit einer selbst gehosteten lokalen MathJax-Instanz dargestellt.
- **Lokale Inferenz-Engine:** Eine zentrale architektonische Änderung ist die Integration von Ollama als lokales LLM-Backend. Dies ermöglicht der Plattform, Open-Weight-Modelle (z. B. DeepSeek) vollständig innerhalb der Universitätsinfrastruktur auszuführen und stellt sicher, dass weder Studierendendaten noch Prompt-Logik die sichere Umgebung verlassen.

### 3.3 Didaktisches Datenmodell

Der Kern ist ein striktes JSON-Datenmodell, dessen Schema-Auszug in Abb. 1 gezeigt wird. Zentrale Felder umfassen:

- `topic` und `learning_objective`
- `weight` (1-3) und `cognitive_level` (Reproduktion, Anwendung, Analyse)
- `mini_glossary`: Kontextuelle Definitionen zur Unterstützung von Just-in-Time-Lernen
- `rationales`: Detaillierte Erklärungen, warum jede Option korrekt oder inkorrekt ist
- **Antwort-Selbsteinschätzung (sicher/unsicher)** zur metakognitiven Analyse auf Itemebene

### 3.4 Taxonomie kognitiver Stufen für KI-generierte MCQs

MC-Test verwendet eine eingeschränkte dreistufige Taxonomie, inspiriert von Bloom: (1) **Reproduktion** (Gewicht 1): Abruf von Fakten, Definitionen oder einfachen Algorithmen; (2) **Anwendung** (Gewicht 2): Anwendung bekannter Konzepte in leicht variierten Kontexten; und (3) **Analyse** (Gewicht 3): Interpretation von Daten, Vergleiche oder Schlussfolgerungen. Die Stufen 4-6 (Bewertung, Kreation) sind ausgeschlossen. Frühere Arbeiten berichten, dass aktuelle Modelle Schwierigkeiten haben, höherstufige Aufgaben in geschlossenen MC-Formaten zuverlässig zu validieren [3] und dass strikte Einschränkungen für semantisch valide MC-Generierung nötig sind [4]. Die Beschränkung auf Stufen 1-3 verbessert die Überprüfbarkeit und reduziert semantische Halluzinationen, aber menschliche Prüfung und Itemanalyse bleiben für faktische und psychometrische Qualität notwendig.

#### 3.4.1 Operationalisierung und Label-Zuverlässigkeit

Lernendenzentrierte Analysen erfordern stabile kognitive Stufenlabels. MC-Test operationalisiert daher Bloom 1-3 mit einer kurzen Rubrik und einem Verifikationsschritt. In unserem Workflow: (1) Lehrende spezifizieren Lernziel und Zielstufe; (2) das LLM generiert ein Item und Begründungen, die auf dieses Ziel abgestimmt sind; (3) Lehrende prüfen das Item vor Freigabe. Um Label-Zuverlässigkeit zu quantifizieren, werden zwei Lehrende eine Stichprobe mit derselben Rubrik doppelt codieren. Wir berichten prozentuale Übereinstimmung und Cohens Kappa und behandeln niedrige Übereinstimmung als Warnsignal, bevor kognitive Profile im großen Maßstab interpretiert werden.

### 3.5 Prompt-Architektur

Die Itemgenerierung wird durch einen kontextoptimierten Systemanweisungssatz gesteuert, der das Modell als „Interactive MCQ Generator" rahmt. Hier bezieht sich Kontextoptimierung auf das bewusste Design von (i) einem Interaktionsprotokoll, das alle Generierungsparameter erfragt, und (ii) harten Output-Einschränkungen, die Ergebnisse maschinenprüfbar machen.

MC-Test verwendet einen endlichen Zustandsworkflow mit drei Phasen. (1) **Konfiguration:** Das Modell sammelt Parameter schrittweise (Thema, Zielgruppe, Itemanzahl, Schwierigkeits-/Gewichtsprofil, Optionsformat, optionaler curricularer Kontext) und fragt nach expliziter Bestätigung. (2) **Interne Blaupausenerstellung:** Das Modell führt eine interne Konsistenzprüfung durch (z. B. Schwierigkeitsgewichte entsprechen dem angeforderten Profil; Options-/Antworteinschränkungen sind erfüllbar), ohne Zwischenschritte offenzulegen. (3) **Schema-gesteuerte Ausgabe:** Das Modell gibt ein einzelnes, strikt parsbares JSON-Objekt zurück, das explizite Escape- und Formatierungsregeln befolgt, einschließlich stabiler `question_ids` und einer `schema_version` für Vorwärtskompatibilität (Abb. 1).

Für Robustheit über Cloud- und lokale Backends hinweg wird das JSON einer automatisierten Schema- und semantischen Validierung unterzogen (z. B. erforderliche Felder, eindeutige Optionen, gültige Antwortindizes), mit einer optionalen Reparaturschleife, die das Modell auffordert, minimale Änderungen vorzunehmen, wenn Verstöße erkannt werden.

**Post-production Lernziele:** Nach der Generierung eines Fragensatzes schlägt das LLM eine kleine Menge von Themenlabels (typischerweise ~10) vor, um die Itembank zu strukturieren. Ein zweiter Prompt leitet Bloom-ausgerichtete Lernziele pro Item aus dessen Thema und kognitiver Stufe ab. Wir kompilieren diese Ziele in eine lernendenzentrierte Lernressource, die Lernziele über Themen und Stufen hinweg zusammenfasst.

## 4. LERNENDENZENTRIERTE ANALYSEN UND PÄDAGOGISCHE KONTROLLE

Nach einem Test zeigt MC-Test ein lernendenzentriertes Analyse-Dashboard zur Unterstützung metakognitiver Reflexion. Statt einer einzelnen Punktzahl bietet es vier Ansichten, die curriculare Themen, kognitive Stufen und Konzeptbeherrschung abdecken. In diesem Abschnitt sind Themen grobe Curriculumseinheiten; Konzepte sind feinkörnige Lernziele innerhalb eines Themas.

Die vier Ansichten bilden einen diagnostischen Trichter von Überblick zu Detail. Die Heatmap unterstützt die Mustersuche über Thema × Stufe (einschließlich Vermeidung). Themenbalken und das Radar trennen Inhaltslücken von Prozesslücken, während die Konzeptspalten Muster in konkrete Förderungsziele übersetzen. Das Ziel ist, Lernende von globalen Selbsteinschätzungen zu umsetzbaren Diagnosen zu bewegen [12].

### 4.1 Themenleistungsdiagramm

Abb. 2 zeigt das Themenleistungsdiagramm, das Ergebnisse nach Themenbereich aggregiert (z. B. Regression, Klassifikation, Evaluation). Jeder gestapelte Balken zeigt korrekte, inkorrekte und unbeantwortete Items; die x-Achsenbeschriftungen berichten beantwortet/gesamt, um das Beweisvolumen anzuzeigen. Diese Ansicht hebt Themen hervor, die Förderung benötigen, und Themen, die möglicherweise übersprungen wurden.

### 4.2 Kognitives Radardiagramm

Abb. 3 zeigt das kognitive Radardiagramm, das Leistung über die drei Stufen zusammenfasst (Reproduktion, Anwendung, Analyse). Es zeigt an, ob Lernende hauptsächlich Fakten abrufen oder Wissen übertragen und damit argumentieren können. Ausgewogene Formen deuten auf gleichmäßige Entwicklung hin; starke Asymmetrien heben gezielte Entwicklungszonen hervor. Zur Reflexion ordnen wir charakteristische Muster interpretativen (nicht-diagnostischen) Lernendenarchetypen zu (z. B. Theoretiker, Praktiker, Analytiker).

### 4.3 Konzeptbeherrschungsspalten

Abb. 4 zeigt die Konzeptbeherrschungsspalten. MC-Test gruppiert Items nach getaggten Konzepten (z. B. Kreuzvalidierung, Regularisierung) und klassifiziert jedes Konzept als verstanden, nicht verstanden oder nicht versucht. Ein Konzept gilt als verstanden, wenn mindestens 70 % seiner Items korrekt sind; andernfalls wird es markiert, um Missverständnisse sichtbar zu machen, ohne einzelne Items überzuinterpretieren. Diese Mikroebenen-Ansicht verwandelt Testergebnisse in konkrete Lernziele.

### 4.4 Themen-×-Kognitiv-Heatmap

Abb. 5 zeigt die Themen-×-Kognitiv-Heatmap, die Themen (Zeilen) und kognitive Stufen (Spalten) kombiniert. Zellen kodieren Leistung und Beweisvolumen: Unbeantwortete Items zählen als 0, und jede Zelle berichtet beantwortet/gesamt. Dies entmutigt strategisches Überspringen und hilft Lernenden zu lokalisieren, ob Schwierigkeiten themenspezifisch oder stufenspezifisch sind.

Zusammen sind die Ansichten orthogonal. Themenleistung zeigt, was abgedeckt wurde; das Radar zeigt, wie der Lernende über Stufen hinweg abschneidet; die Heatmap verknüpft beide; und Konzeptbeherrschung zoomt in feinkörnige Ziele. Triangulation reduziert blinde Flecken und kann strategische Verhaltensweisen wie das Überspringen höherstufiger Items offenbaren.

### 4.5 Feedback und Erklärungen

Für komplexe Items werden Erklärungen um schrittweise Argumentation erweitert. Zur Unterstützung des Vokabularewerbs wird ein zweistufiges Glossarkonzept verwendet: ein Mini-Glossar-Feld für sofortige Hilfe und ein zusammenfassendes PDF-Glossar für die Nachbetrachtung.

### 4.6 Pädagogische Kontrolle: Wartezeiten und Panikmodus

MC-Test steuert die Taktung, um Lesen und Reflexion zu fördern und impulsive Antworten (z. B. schnelles Raten) abzuschrecken. Wir behandeln diese Taktungs-Nudges als Designhypothesen und evaluieren ihre Verhaltenseffekte empirisch, statt zu behaupten, tiefe Verarbeitung zu erzwingen.

Die pädagogische Kontrollschicht bietet drei Mechanismen. **Pre-Answer-Wartezeit (Leseunterstützung):** Der Submit-Button bleibt nach dem Laden für eine kurze, itemspezifische Zeit deaktiviert; die Dauer hängt von Itemgewicht und Textlänge ab. **Post-Answer-Wartezeit (Reflexionsunterstützung):** Nach Abgabe wird die Navigation zum nächsten Item verzögert, um ein Prüfungsfenster für formatives Feedback zu schaffen [13]; die Dauer skaliert mit der Erklärungslänge (+10 s Standard, +20 s erweitert). **Adaptive Fairness („Panikmodus"):** Taktung kann Lernende unter Zeitdruck behindern, daher kann das System Wartezeiten deaktivieren, wenn die Zeit kritisch wird.

Das System überwacht die verbleibende Zeit pro verbleibende Frage. Fällt sie unter einen Schwellenwert (z. B. <15 s pro Frage), überschreibt der Panikmodus Wartezeiten, sodass Lernende den Versuch beenden können. Da feste Taktung manche Lernende benachteiligen kann (z. B. Nutzer von Hilfstechnologien oder Studierende mit Nachteilsausgleich), sind alle Wartezeiten pro Kurs konfigurierbar und können deaktiviert oder angepasst werden. Kurz gesagt: Der Panikmodus priorisiert Fertigstellung und Fairness bei hohem Zeitdruck.

### 4.7 Itemdiagnostik über Konfidenz-Matrix

Neben lernendenzentrierten Dashboards unterstützt MC-Test eine instruktorenseitige Itemdiagnostik: Für jede Frage kann eine kumulierte Konfidenz-Matrix (sicher/unsicher × richtig/falsch) angezeigt werden. So werden problematische Items sichtbar (z. B. hohe „sicher & falsch“-Anteile deuten auf Missverständnisse oder fehlerhafte Schlüssel). Die Aggregation schließt Autoreneinschätzungen aus, um Verzerrungen zu vermeiden. Zugriff ist rollenbasiert: Admins sehen die Matrix stets; Autoren temporärer Sets nur in der aktiven Session bzw. bei reserviertem Pseudonym innerhalb der Löschfrist.

## 5. IMPLEMENTIERUNG UND MIGRATION ZU LOKALEM LLM-BACKEND

Die Plattform wurde von kommerziellen Cloud-APIs zu einem institutionellen Server mit lokalem LLM-Backend (Ollama) migriert, um Datenschutz und Nachhaltigkeit zu adressieren.

- **Prompt-Refactoring:** Der Systemprompt wurde an lokale Modelleigenschaften angepasst und priorisiert JSON-Validität und Robustheit.
- **Datenschutz:** Lokales Deployment stellt sicher, dass keine Studierendendaten die Institution verlassen, entsprechend den Prinzipien von „Privacy by Design" [10], [11].
- **Nachhaltigkeit:** On-Premises-Hosting mindert die Kosten und Rate-Limits kommerzieller API-Nutzung.
- **Datenminimierung und Logging:** Wir speichern nur, was wir für Bewertung und Analysen benötigen (Antworten, Zeitstempel, aggregierte Punktzahlen) plus minimale operative Metadaten und Sicherheits-Audit-Logs. Prompts vermeiden persönliche Identifikatoren, und das lokale Deployment hält sowohl Studierendendaten als auch Prompt-Logik innerhalb der institutionellen Umgebung. Zugriff auf Logs und Datenbanken ist auf autorisiertes Personal beschränkt; Aufbewahrungsrichtlinien begrenzen die Speicherdauer.
- **Anonymität und Pseudonyme:** MC-Test unterstützt anonyme Teilnahme ohne persönliche Konten. Lernende wählen ein Pseudonym aus einer vordefinierten Liste (z. B. Nobel-/Turing-Preisträger), um Sitzungsdaten für Fortschrittsanzeigen und aggregierte Analysen konsistent zu halten, ohne reale Identifikation zu ermöglichen (Abb. 6).
- **Rollenbasierte Einsicht:** Itemdiagnostische Aggregationen (z. B. Konfidenz-Matrizen) sind nur für Admins und Autoren sichtbar; reguläre Lernende sehen keine Aggregationen.
- **Open-Source-Verfügbarkeit:** Zur Unterstützung von Transparenz und Reproduzierbarkeit wird die MC-Test-Streamlit-Anwendung unter MIT-Lizenz veröffentlicht und ist auf GitHub öffentlich verfügbar (https://github.com/kqc-real/streamlit). Das Repository enthält Deployment- und Konfigurationsdokumentation (z. B. Docker Compose) sowie die schema-gesteuerten Artefakte, die in der lokalen Inferenz-Pipeline verwendet werden.

## 6. EVALUIERUNGSDESIGN UND AUSBLICK

### 6.1 Geplantes Studiendesign

Wir planen Piloteinsätze in MINT-Modulen. Wir sammeln Systemlogs (Taktungsentscheidungen, kognitive Profile, Antwortzeiten), Vor-/Nach-Fragebögen zu metakognitivem Bewusstsein und wahrgenommener Nützlichkeit sowie Interviews. Als Nächstes führen wir vergleichende Designs (A/B oder phasenweise Einführung) durch, um zu testen, ob pädagogische Kontrolle Schnellrate-Indikatoren reduziert und Lernstrategien oder Lernergebnisse verändert. Wir prüfen auch Labelstabilität (Doppelcodierung) und berichten grundlegende Itemstatistiken zur Unterstützung psychometrischer Interpretation.

Wir leiten Schnellrate-Indikatoren aus Logs ab (z. B. Antwortzeiten unter itemspezifischen Schwellenwerten, Low-Effort-Antwortraten pro Lernendem und Antwortzeitveränderungen vor/nach Taktung) [8], [9]. Wir vergleichen Bedingungen (Taktung an/aus; gestaffelte Einführung), kontrollieren für Itemschwierigkeit und Position und untersuchen nachgelagertes Verhalten wie Feedback-Betrachtungszeit und Optionsprüfung.

Zusätzlich planen wir, kumulierte Konfidenz-Muster (z. B. „sicher & falsch“) als Itemdiagnostik-Indikatoren zu analysieren und mit klassischen Itemstatistiken zu triangulieren, um potenziell missverständliche Items früh zu markieren.

Um lernendenzentrierte Analysen interpretierbar zu halten, behandeln wir kognitive Stufenlabels als messbare Designannahme. Wir codieren daher Labels mit einer Rubrik doppelt und berichten Interrater-Übereinstimmung (prozentuale Übereinstimmung, Cohens Kappa). Zusätzlich berechnen wir grundlegende Itemstatistiken (Schwierigkeit, Diskrimination), um Items niedriger Qualität oder mehrdeutige Items zu markieren, bevor kognitive Profile im großen Maßstab interpretiert werden.

Informelle Versuche legen nahe, dass Lernende die Aufschlüsselung nach kognitiver Stufe und transparente Begründungen schätzen. Feedback zur Taktung war gemischt, was den später hinzugefügten adaptiven Panikmodus motivierte. Diese Beobachtungen sind explorativ; wir werden mit kontrollierten Vergleichen unter Nutzung von Verhaltenslogs und lernendenberichteten Maßen folgen.

### 6.2 Vorläufige Ergebnisse: Systemusability

Um die Benutzererfahrung (UX) und technische Akzeptanz der Plattform zu validieren, wurde eine standardisierte Usability-Evaluation mit der System Usability Scale (SUS) [14] durchgeführt. Die Umfrage wurde an einer Pilotkohorte von 20 Teilnehmern durchgeführt und ergab einen mittleren SUS-Score von 70,38.

Nach der Adjektiv-Bewertungsskala von Bangor et al. [15] platziert der mittlere SUS-Score MC-Test in der Kategorie ‚OK', was auf gute Akzeptanz hindeutet. Abb. 7 zeigt individuelle Scores im Verhältnis zu Akzeptabilitätsbändern (‚Acceptable', ‚Good', ‚Excellent') und zeigt eine linksschief verteilte Verteilung: Die meisten Teilnehmer bewerteten das System als einfach zu bedienen, mit einigen niedrigeren Ausreißern.

Wichtig ist, dass SUS primär wahrgenommene Usability erfasst; es etabliert keine Lernvorteile oder Verhaltenseffekte. Diese Aspekte werden in nachfolgenden Studien unter Verwendung logbasierter Schnellrate-Indikatoren, Lernendenfeedback zu Fairness/Autonomie und (wo machbar) Lernergebnismaßen untersucht.

### 6.3 Limitationen

Dieses Paper trägt ein Systemdesign und vorläufige Usability-Befunde bei. Erstens erfordern die intendierten Vorteile kognitiven Profilings und Taktungsunterstützung (z. B. reduziertes schnelles Raten, verbesserte metakognitive Regulation) empirische Validierung über SUS hinaus. Zweitens sind kognitive Stufenlabels interpretativ; Zuverlässigkeitsprüfungen (Doppelcodierung) und psychometrische Itemanalysen sind notwendig, bevor lernendenzentrierte Analysen im großen Maßstab interpretiert werden. Drittens können Taktungsmechanismen Lernendenautonomie und Barrierefreiheit beeinflussen; Kurse sollten Konfigurationsoptionen und Nachteilsausgleichswege bereitstellen, um unbeabsichtigte Benachteiligungen zu vermeiden.

Aktuelle Studien bewerten die psychometrischen Eigenschaften LLM-generierter Fragen und verstärken die Notwendigkeit, Itemstatistiken auf Einzelitemebene zu berichten, wenn KI-generierte MCQs in der Praxis verwendet werden [2]. Über klassische Itemanalyse hinaus kann zukünftige Arbeit auch ‚generative Studierenden'-Simulationen nutzen, um mehrdeutige oder niedrig diskriminierende Items vor Einsatz zu markieren [16].

## 7. FAZIT

MC-Test zeigt, wie LLM-gestützte Itemgenerierung in eine formative Multiple-Choice-Übungsplattform integriert werden kann, ohne Lerndaten auszulagern. Das System kombiniert (i) ein didaktisches Itemmodell mit Bloom-1-3-Labels, (ii) schema-beschränkte Generierung über einen endlichen Zustandsworkflow und (iii) lernendenzentrierte Dashboards, die Leistung mit Lernzielen über Themen und kognitive Stufen hinweg verbinden. Eine konfigurierbare Taktungsschicht (Vor-/Nach-Antwort-Wartezeiten, Panikmodus) zielt auf schnelles Raten ab und bewahrt gleichzeitig Fairness unter Zeitdruck.

Unsere Beiträge sind dreifach: (1) ein operationales didaktisches Itemmodell, das Lernziele, kognitive Stufen und formative Begründungen koppelt; (2) eine robuste Generierungspipeline, die parsbares JSON produziert und automatisierte Prüfungen unterstützt; und (3) eine On-Premises-Architektur für lokale, schema-beschränkte LLM-Inferenz (Ollama), geeignet für datenschutzsensible Lehrumgebungen. Eine Pilot-Usability-Studie zeigt gute Akzeptanz (SUS 70,38, N = 20). Laufende Arbeiten evaluieren Verhaltenseffekte (z. B. schnelles Raten), Labelzuverlässigkeit und Item-Psychometrie mittels vergleichender und logbasierter Studien.

## LITERATUR

[1] T. Weber, M. Brandmaier, A. Schmidt, and S. Mayer, "Significant Productivity Gains through Programming with Large Language Models," Proc. ACM Hum.-Comput. Interact., vol. 8, EICS, Art. 256, 2024, doi:10.1145/3661145.

[2] S. Bhandari, Y. Liu, Y. Kwak, and Z. A. Pardos, "Evaluating the psychometric properties of ChatGPT-generated questions," Computers and Education: Artificial Intelligence, vol. 7, Art. 100284, 2024, doi: 10.1016/j.caeai.2024.100284.

[3] N. Scaria, S. D. Chenna, and D. Subramani, "Automated Educational Question Generation at Different Bloom's Skill Levels Using Large Language Models: Strategies and Evaluation," in Artificial Intelligence in Education (AIED 2024), LNAI vol. 14830, pp. 165-179, 2024, doi: 10.1007/978-3-031-64299-9_12.

[4] P. Stalder, et al., "Ensuring Quality in AI-Generated Multiple-Choice Questions for Higher Education with the QUEST Framework," in Communications in Computer and Information Science, Springer, 2024.

[5] R. Bodily and K. Verbert, "Trends and issues in student-facing learning analytics reporting systems research," in Proc. 7th Int. Conf. Learning Analytics & Knowledge (LAK '17), Vancouver, BC, Canada, Mar. 2017, pp. 309-318, doi: 10.1145/3027385.3027403.

[6] L. de Vreugd, et al., "Learning Analytics Dashboard Design and Evaluation to Support Student Self-Regulation of Study Behavior," Journal of Learning Analytics, vol. 11, no. 3, 2024.

[7] I. Jivet, M. Scheffel, M. Specht, and H. Drachsler, "License to evaluate: Preparing learning analytics dashboards for educational practice," in Proc. 8th Int. Conf. Learning Analytics & Knowledge (LAK '18), Sydney, NSW, Australia, Mar. 2018, pp. 31-40, doi: 10.1145/3170358.3170421.

[8] S. L. Wise and C. E. DeMars, "An application of item response time: The effort-moderated model," Journal of Educational Measurement, vol. 43, pp. 19-38, 2006.

[9] S. L. Wise, "Rapid-guessing behavior: Its identification, interpretation, and implications," Educational Measurement: Issues and Practice, vol. 36, no. 4, pp. 52-61, 2017, doi:10.1111/emip.12165.

[10] H. Drachsler and W. Greller, "Privacy and Analytics: It's a DELICATE Issue-A Checklist for Trusted Learning Analytics," in Proceedings of the Sixth International Conference on Learning Analytics & Knowledge, Edinburgh, UK, 2016, pp. 89-98.

[11] Y. Shanmugarasa, M. Ding, M. A. P. Chamikara, and T. Rakotoarivelo, "SoK: The Privacy Paradox of Large Language Models: Advancements, Privacy Risks, and Mitigation," arXiv preprint arXiv:2506.12699, 2025.

[12] Z. Yan and D. Carless, "Self-Assessment Is About More Than Self: The Enabling Role of Feedback Literacy," Assessment & Evaluation in Higher Education, vol. 47, no. 7, pp. 1116-1128, 2022.

[13] N. E. Winstone and D. Carless, Designing Effective Feedback Processes in Higher Education: A Learning-Focused Approach. London: Routledge, 2019.

[14] J. Brooke, "SUS: A 'Quick and Dirty' Usability Scale," in Usability Evaluation in Industry, P. W. Jordan, B. Thomas, B. A. Weerdmeester, and I. L. McClelland, Eds. London, U.K.: Taylor & Francis, 1996, pp. 189-194.

[15] A. Bangor, P. T. Kortum, and J. T. Miller, "Determining what individual SUS scores mean: Adding an adjective rating scale," Journal of Usability Studies, vol. 4, no. 3, pp. 114-123, 2009.

[16] X. Lu and X. Wang, "Generative Students: Using LLM-Simulated Student Profiles to Support Question Item Evaluation," in Proc. 11th ACM Conf. on Learning @ Scale (L@S '24), 2024, pp. 16-27, doi: 10.1145/3657604.3662031.
