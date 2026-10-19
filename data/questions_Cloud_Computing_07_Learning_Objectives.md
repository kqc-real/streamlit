# Übergeordnete Lernziele: Cloud Computing – MC-Test Themenblock TB07: Storage, Datenbanken und Recovery

## **Speicherarten und Zugriffsschnittstellen**
**Speicherarten anhand ihrer Zugriffssemantik passend einordnen.**

Du unterscheidest Block-, Datei- und Objektspeicher sowie ihre typischen Einsatzbereiche. Bei gemeinsamem Dateizugriff berücksichtigst du außerdem Sperren, Konsistenz und Fehlerverhalten.

---

## **PostgreSQL, Redis und Yjs**
**Die Zustands- und Wiederherstellungsgrenzen verteilter Datenspeicher beurteilen.**

Du trennst dauerhafte Daten, flüchtigen Hilfszustand und lokale Browserdaten. So kannst du Wiederaufbau und Synchronisierung an der jeweils maßgeblichen Quelle ausrichten.

---

## **Backups und Snapshots**
**Sicherungskopien nach Unabhängigkeit und Wiederherstellbarkeit bewerten.**

Du berücksichtigst gemeinsame Fehlerdomänen, Zugriffsschutz und unabhängige Schlüsselverwahrung. Bei einem möglichen Sicherungsvorfall schützt du den letzten guten Stand und prüfst die Integrität.

---

## **Konsistenz und Integrität**
**Die Aussagekraft von Sicherungen und Prüfungen für einen vollständigen Datenstand beurteilen.**

Du unterscheidest crash-konsistente von anwendungskonsistenten Sicherungen und prüfst Daten zusammen mit Konfiguration und Anwendungsversion. Hashwerte ergänzt du um fachliche Wiederherstellungstests.

---

## **RPO und RTO**
**Datenverlustziele und Wiederanlaufzeiten getrennt bestimmen.**

Du leitest Sicherungslücken und die Folgen engerer Ziele aus dem Sicherungsplan ab. Außerdem trennst du die definierte RTO-Messgrenze von der gesamten Zeit bis zur Wiederaufnahme des Betriebs.

---

## **Wiederherstellung und Disaster Recovery**
**Den Wiederanlauf nach einem Ausfall anhand belastbarer Tests planen.**

Du prüfst Wiederherstellung auf einem frischen Host, notwendiges Zugangsmaterial und Kompatibilität der Komponenten. Traffic wird erst nach erfolgreichen Daten-, Migrations- und Funktionstests umgeschaltet.

---

# Detaillierte Lernziele

Im Kontext von **Cloud Computing – MC-Test Themenblock TB07: Storage, Datenbanken und Recovery** unterstützt dich dieses Fragenset dabei, die folgenden detaillierten Lernziele zu erreichen:

### Anwendung

**Du kannst …**

1. die Zugriffsschnittstellen von Block-, Datei- und Objektspeicher zuordnen.
2. ein geeignetes Block-Volume für PostgreSQL-Datendateien auswählen.
3. die nötige Nebenläufigkeitssemantik eines gemeinsam genutzten Dateidienstes bestimmen.
4. Objektzugriff und POSIX-Dateisemantik unterscheiden.
5. eine unabhängige Ablage für unveränderliche Backup-Artefakte auswählen.
6. das Risiko eines Reconnects bei ausschließlich lokalem Sitzungszustand bestimmen.
7. die Aufgaben eines Load Balancers von der Zustandsreplikation abgrenzen.
8. die verbleibende Ausfalllücke bei Session-Affinität benennen.
9. eine globale Kapazitätsgrenze für mehrere App-Replikate auswählen.
10. die Voraussetzungen für Yjs-Scale-out bestimmen.
11. die Auswirkung eines Redis-Ausfalls auf PostgreSQL einordnen.
12. die Voraussetzung für einen wiederaufbaubaren Cache bestimmen.

### Strukturelle Analyse

**Du kannst …**

1. Snapshots als Sicherungsbaustein anhand von Unabhängigkeit, Zugriffsschutz und Wiederherstellungstests bewerten.
2. die gemeinsame Fehlerdomäne von verschlüsseltem Backup und Schlüssel analysieren.
3. bei möglicher Repository-Manipulation eine sichere Reaktion auswählen.
4. crash-konsistente und anwendungskonsistente Sicherungen vergleichen.
5. einen kompatiblen Recovery-Satz aus Daten, Konfiguration und Deployversion herleiten.
6. die Aussagekraft eines Hashes gegenüber fachlicher Vollständigkeit beurteilen.
7. einen kontrollierten Migrationspfad nach einer Datenwiederherstellung ableiten.
8. die Backup-Vollständigkeit anhand wiederhergestellter Kerntabellen und fachlicher Prüfungen bewerten.
9. RPO und RTO anhand ihrer jeweiligen Zielgrößen unterscheiden.
10. die maximale Sicherungslücke aus einem täglichen Sicherungsplan herleiten.
11. die RTO-Messgrenze von der Ende-zu-Ende-Wiederanlaufzeit abgrenzen.
12. die Folgen eines engeren RPO für Sicherungsfrequenz und Konsistenz ableiten.
13. Restorezeit und Host-Bereitstellungszeit in einer Ende-zu-Ende-Betrachtung einordnen.
14. die Unabhängigkeit eines Offsite-Backups mit einem Test auf frischem Host nachweisen.
15. Zugangsmaterial als Voraussetzung für eine Wiederherstellung einordnen.
16. den Zeitpunkt der Traffic-Umschaltung anhand von Wiederherstellungsnachweisen bewerten.
17. den zusätzlichen Nachweiswert eines Tests auf frischem Host gegenüber Container-Tests erklären.
18. eine sichere Reihenfolge für einen unabhängigen Recovery-Kontrollpfad herleiten.
