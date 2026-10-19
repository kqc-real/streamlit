# Übergeordnete Lernziele: Cloud Computing – MC-Test Themenblock TB02: Virtualisierung, Infrastructure as Code (IaC), Domain Name System (DNS) und Transport Layer Security (TLS)

## **Virtualisierung**
**Virtuelle Maschinen und Container anhand ihrer technischen Grenzen unterscheiden.**

Du erklärst die Rolle des Hypervisors und vergleichst Gast-Kernel und gemeinsam genutzten Host-Kernel. Außerdem beurteilst du Snapshots und Ressourcenkonkurrenz anhand ihrer tatsächlichen Auswirkungen.

---

## **Container und Images**
**Container für reproduzierbare und angemessen isolierte Ausführung einordnen.**

Du nutzt unveränderliche Images statt manueller Laufzeitänderungen und erkennst die Vorteile mehrstufiger Builds. Containergrenzen beurteilst du gemeinsam mit Kernel-, Rechte- und Laufzeitkontrollen.

---

## **Orchestrierung und Infrastructure as Code**
**Deklarierte Sollzustände und ihre Auswirkungen kontrolliert verwalten.**

Du beschreibst den Soll-Ist-Abgleich, Selbstheilung und Idempotenz und erkennst Konfigurationsdrift. Destruktive Planänderungen prüfst du vor einer Freigabe gezielt auf Zustand, Datenfolgen und Wiederherstellbarkeit.

---

## **Speicher und Zustände**
**Speicherarten nach Zugriffsform, Lebensdauer und Einsatzanforderungen auswählen.**

Du unterscheidest Block-, Datei- und Objektspeicher sowie kurzlebige Instanzdaten. Für Backups und geteilte Daten berücksichtigst du Konsistenz, Wiederherstellung und den Zugriff mehrerer Instanzen.

---

## **Netzwerk und DNS**
**Namensauflösung und Netzwerkgrenzen in Betriebssituationen analysieren.**

Du erklärst DNS-Caches und trennst Adressauflösung von TLS-Identität. Du bewertest außerdem Loopback-Bindungen, Proxy-Upgrades und Regeln für ausgehenden Netzwerkverkehr nach ihrer Sicherheitswirkung.

---

## **TLS und Lastverteilung**
**Verschlüsselte Verbindungspfade und Lastverteilung anhand ihrer tatsächlichen Eigenschaften beurteilen.**

Du prüfst Zertifikatsrotation, TLS-Terminierung und Integritätsprüfungen und erkennst Grenzen eines Load Balancers. Für horizontale Skalierung berücksichtigst du Verbindungszustand, Lastverteilung und Engpässe.

---

# Detaillierte Lernziele

Im Kontext von **Cloud Computing – MC-Test Themenblock TB02: Virtualisierung, Infrastructure as Code (IaC), Domain Name System (DNS) und Transport Layer Security (TLS)** unterstützt dich dieses Fragenset dabei, die folgenden detaillierten Lernziele zu erreichen:

### Anwendung

**Du kannst …**

1. die Ressourcengrenze virtueller Maschinen anhand der Hypervisorrolle bestimmen.
2. die Kernelgrenze zwischen einer typischen VM und einem Container beschreiben.
3. die Wiederherstellbarkeit eines nicht koordinierten VM-Snapshots beurteilen.
4. Virtualisierung von den zusätzlichen Cloud-Merkmalen unterscheiden.
5. eine Noisy-Neighbor-Ursache mit synchronen Host- und Gastmessungen prüfen.
6. eine dauerhafte Containeränderung einem geprüften, unveränderlichen Image zuordnen.
7. einen beweglichen Image-Tag durch einen unveränderlichen Digest ersetzen.
8. die Funktion getrennter Build- und Produktionsstufen eines Dockerfiles bestimmen.
9. die Containerisolation anhand der gemeinsam genutzten Kernelgrenze einordnen.
10. den Vorteil desselben Artefakts bei getrennten Laufzeitrollen erklären.
11. einen Cluster-Orchestrator anhand der fortlaufenden Sollzustandsabstimmung von Compose unterscheiden.
12. die Wiederherstellung eines fehlenden Replikats dem Controllerprinzip zuordnen.

### Strukturelle Analyse

**Du kannst …**

1. eine manuelle Firewalländerung als Konfigurationsdrift diagnostizieren.
2. die Risiken einer destruktiven IaC-Planänderung für eine produktive Datenbank bewerten.
3. wiederholte Firewallbereitstellung anhand stabiler Identitäten und Sollzustände analysieren.
4. Blockspeicher für eine Datenbank mit blockweisem Dateisystemzugriff auswählen.
5. Objektspeicher für langlebige, schlüsseladressierte Exporte auswählen.
6. verlorene Uploads dem kurzlebigen Container-Layer zuordnen.
7. ein Datenbankbackup während laufender Schreibvorgänge auf Konsistenz prüfen.
8. einen passenden gemeinsamen Speicher für mehrere App-Instanzen anhand seiner Zugriffssemantik beurteilen.
9. eine DNS-Änderung anhand zwischengespeicherter Einträge erklären.
10. einen Zertifikatsnamenfehler von einer fehlerhaften Namensauflösung abgrenzen.
11. die beabsichtigte Sicherheitswirkung einer Loopback-Bindung hinter einem Reverse Proxy beurteilen.
12. einen fehlgeschlagenen WebSocket-Handshake anhand der Proxy-Upgradeweiterleitung diagnostizieren.
13. ausgehenden Netzwerkverkehr eines Bereitstellungsagenten durch eine Positivliste erlaubter Netzwerkziele begrenzen.
14. eine wechselnde Zertifikatsansicht anhand uneinheitlicher TLS-Terminierungsknoten diagnostizieren.
15. den Klartextpfad nach einer TLS-Terminierung als Teil der Vertrauensgrenze bewerten.
16. einen ungeeigneten Integritätsprüfung als Ursache fehlerhafter Load-Balancer-Ziele diagnostizieren.
17. die Grenzen horizontaler Skalierung bei prozesslokal gehaltenen Sessions analysieren.
18. den Load-Balancer-Durchsatz bei ungleicher Anfragenverteilung berechnen.