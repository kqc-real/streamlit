# Übergeordnete Lernziele: Cloud Computing – MC-Test Themenblock TB12: Kumulative Cloud-Synthese und Verteidigung

## **Cloud-Merkmale und Verantwortungsmodelle**
**Cloud-Dienste anhand ihrer Merkmale und Verantwortungsgrenzen einordnen.**

Du unterscheidest Cloud-Merkmale von Service- und Deployment-Modellen. Dabei ordnest du Aufgaben von Anbieter und Organisation bei PaaS, SaaS und gemessener Nutzung passend zu.

---

## **Container, IaC und ereignisbasierte Ausführung**
**Die Grenzen von Containerportabilität und die Eignung von Serverless-Bausteinen analysieren.**

Du beziehst Plattformverträge und Konfigurationsdrift in Infrastrukturentscheidungen ein. Für Funktionen berücksichtigst du Laufzeit, externe Zustände, Wiederholungen und Initialisierungslatenzen.

---

## **Datenhaltung, Backup und Recovery**
**Persistente und flüchtige Datenpfade sowie deren Wiederherstellbarkeit beurteilen.**

Du unterscheidest Zustandsrollen von PostgreSQL, Redis und anderen Komponenten. Restore-Tests, RPO und RTO sowie Datenminimierung und Schlüsselverwaltung gehören zu einer belastbaren Recovery- und Datenschutzbetrachtung.

---

## **Skalierung und verteilte Verarbeitung**
**Workloadform, Zustandsverteilung und Nutzerleistung gemeinsam betrachten.**

Du unterscheidest vertikale Skalierung von Scale-out und berücksichtigst Fan-out, Prozessgrenzen und Warteschlangen. Latenzquantile, Fehlerrate und Durchsatz bilden die Wirkung auf Nutzende besser ab als eine Einzelmetrik.

---

## **Sicherheit und verlässlicher Betrieb**
**Schutzmaßnahmen und Betriebsreaktionen an Risiken und Kernpfaden ausrichten.**

Du minimierst nicht benötigte Daten und Rechte, erhältst bei optionalen Ausfällen die Kernfunktion und deutest CI-Prüfungen als begrenzte Evidenz. SLI und SLO verbindest du mit tatsächlich beobachteter Dienstequalität.

---

## **Wirtschaftlichkeit, Evidenz und Synthese**
**Cloud-Entscheidungen über Kosten, Messqualität und Nachhaltigkeit integrieren.**

Du berücksichtigst TCO, Egress und Annahmen ebenso wie Kapazitätsnachweise und Agentenfehler. Eine tragfähige Verteidigung benennt Gegenoption, Beleggrenze und Auslöser für eine Neubewertung.

---

# Detaillierte Lernziele

Im Kontext von **Cloud Computing – MC-Test Themenblock TB12: Kumulative Cloud-Synthese und Verteidigung** hilft dir dieses Fragenset, die folgenden detaillierten Lernziele zu erreichen:

### Anwendung

**Du kannst …**

1. Cloud-Merkmale unabhängig vom Service-Modell erkennen.
2. die Verantwortungsgrenze eines PaaS-Angebots bestimmen.
3. Nutzung, Latenz und Fehler mit SLO und Unit Costs verknüpfen.
4. verbleibende Kundenverantwortung bei einem SaaS-Angebot zuordnen.
5. die Portabilitätsgrenze eines Containerimages bestimmen.
6. einen geeigneten Workload für FaaS auswählen.
7. Cold-Start-Latenz als Hypothese für Verzögerungen nach Inaktivität identifizieren.
8. persistente und flüchtige Datenrollen von PostgreSQL und Redis zuordnen.
9. einen Restore-Test als Nachweis der Wiederherstellbarkeit auswählen.
10. eine Maßnahme der vertikalen Skalierung auswählen.
11. SLI und SLO anhand von Messwert und Zielwert unterscheiden.
12. wesentliche Bestandteile eines kumulativen Architecture Decision Records auswählen.

### Strukturelle Analyse

**Du kannst …**

1. Hosting und nachgewiesene Cloud-Elastizität voneinander abgrenzen.
2. Configuration Drift anhand deklarierter und tatsächlicher Zustände diagnostizieren.
3. eine idempotente Zustandsstrategie für wiederholte FaaS-Aufrufe begründen.
4. RPO und RTO aus Sicherungsintervall und Restore-Test ableiten.
5. einen ML-Datenfluss hinsichtlich Datenminimierung und Privacy-Risiko bewerten.
6. die Grenzen eines Object-Storage-Backups für Konsistenz und Recovery analysieren.
7. Auswirkungen verschiedener Workloadformen auf verteilte Systeme vergleichen.
8. Fehler durch prozesslokalen Zustand im Scale-out-Betrieb diagnostizieren.
9. Nutzerleistung anhand von Latenzquantilen, Fehlern und Durchsatz bewerten.
10. eine Überlastreaktion mit Backpressure und kontrollierter Degradation begründen.
11. Antwortdaten nach Sessionphase serverseitig minimieren.
12. Betriebsrechte nach Least Privilege ausrichten.
13. eine Graceful-Degradation-Reaktion für einen optionalen ML-Pfad auswählen.
14. die Aussagegrenze von SBOM- und Image-Scans analysieren.
15. Betriebsmodelle auf einer einheitlichen TCO-Systemgrenze vergleichen.
16. die Egress-Sensitivität einer Providerentscheidung analysieren.
17. eine Kapazitätsbehauptung anhand gestufter Tests und begrenzter Evidenz bewerten.
18. eine integrierte Cloud-Entscheidung anhand begrenzter These, Evidenz und Gegenoption verteidigen.
