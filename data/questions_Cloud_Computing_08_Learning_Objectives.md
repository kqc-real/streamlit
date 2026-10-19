# Übergeordnete Lernziele: Cloud Computing – MC-Test Themenblock TB08: Elastizität, Skalierung und verteilte Systeme

## **Skalierungsstrategien**
**Skalierungsoptionen passend zu Last und Zustandsmodell auswählen.**

Du unterscheidest vertikale und horizontale Skalierung sowie Elastizität. Bei vorhersehbaren Lastspitzen berücksichtigst du die Reaktionszeit automatischer Skalierung und steuerst die Aufnahme neuer Arbeit.

---

## **Lastverteilung und Zustandsgrenzen**
**Die Folgen von Replikation für Routing und Anwendungszustand bestimmen.**

Du erkennst, dass Lastverteilung und Session-Affinität Prozesszustand nicht replizieren. Für mehrere Replikate klärst du deshalb Routing, gemeinsame Zuständigkeit und globale Kapazitätsgrenzen.

---

## **Warteschlangen und Backpressure**
**Überlast begrenzen, ohne wichtige Kernpfade zu blockieren.**

Du berücksichtigst Ankunftsrate, Warteschlangengröße, Wiederholungsversuche und Bearbeitungszeit. Begrenzte Warteschlangen, Priorisierung und Isolation schützen Kernfunktionen vor Überlastfolgen.

---

## **Caching und kontrollierte Degradation**
**Optionale Arbeit so gestalten, dass ihr Ausfall den Kernbetrieb nicht gefährdet.**

Du definierst wiederaufbaubare und versionsgebundene Cache-Einträge und verhinderst gleichzeitige Neuberechnungen. Bei Ausfällen nutzt du einen sichtbaren Fallback statt den Livebetrieb zu blockieren.

---

## **Leistungskennzahlen und SLOs**
**Leistungsziele mit mehreren aussagekräftigen Messgrößen beurteilen.**

Du interpretierst Perzentile und bewertest Durchsatz gemeinsam mit Latenz und Fehlerrate. Erwartete Schutzablehnungen trennst du von unerwarteten Fehlern des regulären Dienstpfads.

---

## **Lastprofile und verteilte Systeme**
**Lastnachweise an der tatsächlichen Verteilung und Systemgrenze ausrichten.**

Du berücksichtigst koordinierte Auslassung, Sitzungsverteilung, WebSocket-Verhalten und Instanzausfälle. Lokale Tests ordnest du als begrenzte Evidenz ein, nicht als uneingeschränkten Produktionsnachweis.

---

# Detaillierte Lernziele

Im Kontext von **Cloud Computing – MC-Test Themenblock TB08: Elastizität, Skalierung und verteilte Systeme** unterstützt dich dieses Fragenset dabei, die folgenden detaillierten Lernziele zu erreichen:

### Anwendung

**Du kannst …**

1. vertikale und horizontale Skalierung anhand ihrer Knoten- und Zustandsgrenzen unterscheiden.
2. für einen Single-Host-Dienst einen risikoarmen kurzfristigen Skalierungsschritt auswählen.
3. eine gesättigte Datenbank als Engpass nach dem Hinzufügen von App-Replikaten erkennen.
4. Elastizität von allgemeiner Skalierbarkeit unterscheiden.
5. eine kurzfristige Join-Welle vor der Autoscaling-Reaktion durch Vorabbereitstellung und Zulassungssteuerung abfangen.
6. die Auswirkung eines Reconnects bei instanzlokalem WebSocket-Zustand bestimmen.
7. die Grenze eines Load Balancers gegenüber Zustandsreplikation benennen.
8. die verbleibende Ausfalllücke von Session-Affinität erkennen.
9. eine globale Kapazitätsgrenze über mehrere Replikate hinweg auswählen.
10. die notwendigen Zustands- und Routingfragen vor dem Yjs-Scale-out bestimmen.
11. bei Überlast eine begrenzte Queue- und Backpressure-Reaktion auswählen.
12. die Lastverstärkung durch sofortige parallele Retries erkennen.

### Strukturelle Analyse

**Du kannst …**

1. Bestand, Durchsatz und Verweildauer mit Little’s Law in Beziehung setzen.
2. getrennte Queues und Budgets für Kernpfade und optionale Arbeit begründen.
3. die Ausfallfolgen einer unbegrenzten, speicherbasierten Queue analysieren.
4. die Wiederaufbaubarkeit eines Caches anhand seiner Quelle und Gültigkeitsregel beurteilen.
5. einen versionsgebundenen Cache-Schlüssel für Inferenzdaten herleiten.
6. Maßnahmen gegen gleichzeitige Cache-Neuberechnungen auswählen.
7. den lexikalischen Fallback bei Ausfall optionaler Inferenz bewerten.
8. kontrollierte Degradation anhand von Kernfunktion, Beobachtbarkeit und Rückkehrbedingungen beurteilen.
9. die Aussage von p50-, p95- und p99-Latenzwerten interpretieren.
10. Durchsatz, Tail-Latenz und Fehlerrate gemeinsam anhand definierter Ziele bewerten.
11. die Verzerrung von Lastmessungen durch einen geschlossenen Lastgenerator erklären.
12. erwartete Schutzablehnungen von Fehlern des normalen Servicepfads abgrenzen.
13. die Aussagegrenze eines erfolgreichen Produktions-Lastlaufs gegenüber einem verfehlten Latenzziel bestimmen.
14. die unterschiedlichen Lastprofile vieler kleiner Sessions und eines einzelnen Hotspots vergleichen.
15. einen Mehrinstanz-WebSocket-Test mit Fan-out, Reconnect und Zustandskonsistenz planen.
16. lokale Lasttestergebnisse gegenüber einer Produktionsfreigabe einordnen.
17. die erforderlichen Architekturänderungen für den Wechsel auf mehrere App-Replikate herleiten.
18. eine isolierte Degradation bei Ausfall des optionalen Inferenzdienstes bewerten.
