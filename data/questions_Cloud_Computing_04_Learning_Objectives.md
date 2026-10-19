# Übergeordnete Lernziele: Cloud Computing – MC-Test Themenblock TB04: Serverless Computing und Workload-Eignung

## **Serverless-Modelle und Verantwortlichkeiten**
**Serverless-Dienste nach Betriebsmodell und Verantwortungsgrenzen einordnen.**

Du unterscheidest FaaS und BaaS, ordnest Auslöser und Zustandsverwaltung ein und erkennst, welche Betriebsaufgaben beim Anbieter und welche beim Anwendungsteam liegen.

---

## **Zuverlässige ereignisgesteuerte Verarbeitung**
**Wiederholungen und parallele Trigger sicher behandeln.**

Du nutzt stabile Ereigniskennungen, idempotente Verarbeitung, Versionsbezüge und verteilte Koordination, damit erneute oder überlappende Ausführungen keine unbeabsichtigte Fachwirkung erzeugen.

---

## **Laufzeit, Abhängigkeiten und Messung**
**Laufzeitgrenzen und Kaltstarts anhand realistischer Messungen bewerten.**

Du berücksichtigst Initialisierung, Paketgröße, zulässige Maximalfälle und Abhängigkeiten. Dadurch kannst du erkennen, wann ein einzelner erfolgreicher Test nicht für den produktiven Betrieb ausreicht.

---

## **Eignung konkreter Arbeitslasten**
**Arbeitslasten mit den Betriebsgrenzen von Functions vergleichen.**

Du prüfst Zustandsbedarf, Laufzeit, Verbindungsmuster, Nebenläufigkeit und Datenbankgrenzen. Du berücksichtigst auch den Schutz nachgelagerter Dienste bei automatischer Skalierung.

---

## **Kosten und Skalierung**
**Serverless-Kosten und Leistungsziele auf einer gemeinsamen Grundlage vergleichen.**

Du berechnest nutzungsabhängige Rechenkosten, bestimmst einen fairen Vergleichspunkt und beziehst Latenz, Dauerlast sowie Schutzmaßnahmen gegen Ereignisschleifen ein.

---

## **Portabilität und Architekturentscheidung**
**Lock-in, Ausstieg und Eignung anhand prüfbarer Evidenz beurteilen.**

Du begrenzt Anbieterkopplung durch klare Schnittstellen und testbare Ausstiegspfade. Eine belastbare Entscheidung verbindet Messungen, Risiken, Gegenargumente und Gültigkeitsgrenzen.

---

# Detaillierte Lernziele

Im Kontext von **Cloud Computing – MC-Test Themenblock TB04: Serverless Computing und Workload-Eignung** hilft dir dieses Fragenset, die folgenden detaillierten Lernziele zu erreichen:

### Anwendung

**Du kannst …**

1. die Betriebsabstraktion von Serverless anhand der verbleibenden Infrastruktur bestimmen.
2. FaaS und BaaS anhand ihrer jeweiligen Dienste einordnen.
3. HTTP-Aufruf, Queue-Nachricht und Zeitplan als Trigger klassifizieren.
4. die passende Ablage für dauerhaften Funktionszustand bestimmen.
5. verbleibende Kundenverantwortung bei einer verwalteten Function erkennen.
6. eine Webhook-Verarbeitung mit Ereigniskennung idempotent gestalten.
7. mindestens einmal zugestellte Queue-Nachrichten sicher behandeln.
8. überlappende Zeittrigger mit verteilter Koordination begrenzen.
9. Objekttrigger anhand von Schlüssel, Version und Verarbeitungsstatus prüfen.
10. Wiederholungen nach einem unklaren HTTP-Ergebnis absichern.
11. eine erhöhte Latenz nach Inaktivität als möglichen Kaltstart erkennen.
12. ein Messverfahren für Kaltstarts an seltene Aufrufe anpassen.

### Strukturelle Analyse

**Du kannst …**

1. einen zulässigen Maximalfall mit einer harten Laufzeitgrenze vergleichen.
2. schwere Laufzeitabhängigkeiten anhand von Paketgrenzen und Betriebsfolgen bewerten.
3. den Schutz einer begrenzten Datenbank vor automatisch wachsender Nebenläufigkeit begründen.
4. eine kurze, zustandslose Objektverarbeitung als möglichen FaaS-Einsatz einordnen.
5. die Eignung einer PDF-Function anhand paralleler Datenbanklast bewerten.
6. die Grenzen kurzlebiger Functions für ein zustandsbehaftetes Yjs-Relay begründen.
7. die Eignung eines begrenzten, idempotenten Bereinigungsjobs beurteilen.
8. Worker und Serverless-Alternative mit gleichen Anforderungen vergleichen.
9. Pay-per-use-Kosten für eine dauerhafte Grundlast beurteilen.
10. den GB-Sekunden-Verbrauch einer Function berechnen.
11. einen Break-even-Vergleich anhand gleicher Kosten- und Lastgrenzen herleiten.
12. Kosten und 95-%-Latenz gegen ein Dienstgüteziel abwägen.
13. Schutzmaßnahmen für eine kostentreibende Ereignisschleife auswählen.
14. Anbieterkopplung durch Trennung von Fachlogik und Adaptern begrenzen.
15. die wichtigsten Ausstiegsrisiken eines Identitätsdienstes bewerten.
16. die Grenzen einer gemeinsamen Schnittstelle für die Portabilität analysieren.
17. eine Ereigniskette anhand datensparsamer Beobachtungsdaten rekonstruieren.
18. eine Serverless-Entscheidung mit Eignung, Kosten, Restrisiko und Gegenargument begründen.
