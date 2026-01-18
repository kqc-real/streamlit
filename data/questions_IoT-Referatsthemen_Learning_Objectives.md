# Übergeordnete Lernziele: IoT-Referatsthemen: Grundlagen, Protokolle und Sicherheit

## MQTT und Publish-Subscribe-Architektur
**Das MQTT-Protokoll und seine Funktionsweise verstehen**

Du verstehst, dass MQTT das Publish-Subscribe-Muster verwendet, um Geräte über einen zentralen Broker zu entkoppeln. Du erkennst, dass dieses Architekturmuster effizienter für instabile Netzwerke ist als das klassische Request-Response-Muster und kannst die Rolle des Brokers als Vermittler zwischen Publishern und Subscribern beschreiben.

---

## IoT-Hardware-Komponenten
**Sensoren und Aktoren unterscheiden und ihre Rollen verstehen**

Du kannst die grundlegenden Hardware-Komponenten eines IoT-Systems unterscheiden: Sensoren erfassen physikalische Messgrößen aus der Umgebung, während Aktoren digitale Steuerbefehle in physische Aktionen umsetzen. Du verstehst, dass beide Komponenten als Transducer (Wandler) fungieren, jedoch in entgegengesetzten Richtungen.

---

## Edge Computing vs. Cloud Computing
**Die Vorteile dezentraler Datenverarbeitung erkennen**

Du verstehst, dass Edge Computing die Datenverarbeitung nahe an der Quelle der Datenerzeugung verlagert, statt alle Daten zentral in entfernten Rechenzentren zu verarbeiten. Du erkennst die Vorteile: Reduktion von Latenzzeiten, Bandbreitennutzung und Kosten, besonders bei datenintensiven Anwendungen.

---

## IoT-Netzwerktechnologien kontextabhängig auswählen
**Passende Protokolle basierend auf Reichweite, Energie und Datenrate wählen**

Du kannst IoT-Netzwerktechnologien anhand der Anforderungen auswählen: LoRaWAN für große Reichweiten bei geringem Energieverbrauch und niedriger Datenrate, WLAN für hohe Datenraten bei begrenzter Reichweite, Bluetooth Low Energy für kurze Distanzen mit Energieeffizienz. Du verstehst das Konzept von LPWAN (Low-Power Wide-Area Networks) für batteriebetriebene Sensoren über große Flächen.

---

## Netzwerktopologien und Ausfallsicherheit
**Mesh-Netzwerke als robuste Alternative zu Stern-Topologien verstehen**

Du verstehst, dass Mesh-Topologien höhere Ausfallsicherheit bieten, da Geräte Nachrichten untereinander weiterleiten können und alternative Routen bei Ausfällen automatisch gefunden werden. Du erkennst den Gegensatz zur Stern-Topologie, bei der der Ausfall des zentralen Hubs (Single Point of Failure) zum Totalausfall führt.

---

## IT-Sicherheit: CIA-Triade im IoT-Kontext
**Die Schutzziele Vertraulichkeit, Integrität und Verfügbarkeit anwenden**

Du kannst die drei Schutzziele der CIA-Triade auf IoT-Szenarien anwenden: Vertraulichkeit (Confidentiality) wird durch Klartextübertragung verletzt, Integrität (Integrity) durch unbemerkte Datenveränderung, Verfügbarkeit (Availability) durch Systemausfälle. Du erkennst, dass Klartextübertragung per HTTP primär die Vertraulichkeit gefährdet, da Dritte die Daten mitlesen können.

---

## IoT-spezifische Sicherheitsrisiken
**Die besonderen Gefahren von Standard-Passwörtern und Botnets verstehen**

Du verstehst, warum IoT-Geräte besonders anfällig für Angriffe sind: Sie sind oft direkt mit dem Internet verbunden, schwer patchbar (headless devices ohne Updates) und werden mit Standard-Passwörtern ausgeliefert. Du erkennst die Gefahr von Botnets wie Mirai, die automatisiert das Internet nach solchen Geräten scannen.

---

## Architekturen für High-Volume IoT-Daten
**Edge Computing für datenintensive Anwendungen begründen**

Du kannst analysieren, wann Edge-Computing-Architekturen notwendig sind: bei extrem hohen Datenraten (z.B. 10 GB/s bei Vibrationssensoren), wo Cloud-Übertragung zu teuer wäre, Latenz kritisch ist oder Echtzeitreaktionen erforderlich sind. Du verstehst das Konzept der Vorverarbeitung am Edge, um nur "Smart Data" statt "Big Data" zu übertragen.

---

## Netzwerksegmentierung als Sicherheitsprinzip
**Die Notwendigkeit der Trennung von IoT-Geräten und sensiblen Systemen verstehen**

Du kannst analysieren, warum IoT-Geräte in separaten Netzwerksegmenten (VLANs) betrieben werden sollten, um "Lateral Movement" von Angreifern zu verhindern. Du verstehst das Zero-Trust-Prinzip, das davon ausgeht, dass Geräte kompromittiert werden können, und erkennst, wie Segmentierung den "Blast Radius" eines Angriffs begrenzt.

---

## IPv6 als Zukunft des IoT
**Die Notwendigkeit von IPv6 für Massive IoT begründen**

Du kannst die Limitierung von IPv4 (ca. 4,3 Milliarden Adressen) analysieren und verstehst, warum IPv6 mit 128-Bit-Adressen für IoT-Szenarien mit Milliarden von Geräten zwingend erforderlich ist. Du erkennst, dass IPv6 echte End-to-End-Konnektivität ermöglicht, während IPv4 auf komplexe NAT-Workarounds angewiesen ist.

---

# Detaillierte Lernziele

Im Kontext des Themas **IoT-Referatsthemen: Grundlagen, Protokolle und Sicherheit** soll dir dieses Fragenset helfen, die folgenden detaillierten Lernziele zu erreichen:

### Reproduktion
**Du kannst …**

1. das Publish-Subscribe-Muster als Architektur von MQTT benennen
2. die Hauptaufgabe eines Aktors als Umwandlung elektrischer Signale in physische Aktionen beschreiben
3. Edge Computing als dezentrale Datenverarbeitung nahe an der Quelle definieren

### Anwendung
**Du kannst …**

1. LoRaWAN für batteriebetriebene Sensoren mit hoher Reichweite und niedriger Datenrate auswählen
2. Mesh-Topologie zur Erhöhung der Ausfallsicherheit bei Smart-Home-Systemen einsetzen
3. bei Klartextübertragung per HTTP die Verletzung der Vertraulichkeit (CIA-Triade) identifizieren
4. das erhöhte Risiko von Standard-Passwörtern bei IoT-Geräten durch direkte Internetanbindung und fehlende Updates erkennen

### Strukturelle Analyse
**Du kannst …**

1. Edge-Computing-Architekturen für High-Volume-Datenströme (z.B. Predictive Maintenance) begründen und Bandbreiten-/Latenz-/Kostenprobleme reiner Cloud-Lösungen ableiten
2. die Notwendigkeit der Netzwerksegmentierung (VLANs) analysieren, um Lateral Movement nach Kompromittierung eines IoT-Geräts zu verhindern
3. IPv6 als zwingende Voraussetzung für Massive IoT durch Vergleich der Adressräume von IPv4 (32-Bit) und IPv6 (128-Bit) begründen und NAT-Limitierungen ableiten
