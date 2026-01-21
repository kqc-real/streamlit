# Übergeordnete Lernziele: Internet of Things (IoT) – Grundlagen und Anwendungen

## IoT-Architektur und Komponenten
**Den Aufbau von IoT-Systemen von der Hardware bis zur Plattform verstehen**

Du verstehst die grundlegende Architektur von IoT-Systemen, einschließlich der Wahrnehmungsschicht mit Sensoren und Aktoren sowie der Rolle von Gateways und Middleware. Du kannst ressourcenbeschränkte Geräte von klassischen Computern abgrenzen und die Bedeutung von Energieeffizienz im Systemdesign einordnen.

---

## Kommunikationsprotokolle und Vernetzung
**Geeignete Übertragungstechnologien für vernetzte Objekte auswählen**

Du kennst die spezifischen Anforderungen an IoT-Kommunikation und kannst Protokolle wie MQTT und CoAP gegenüber klassischem HTTP abgrenzen. Du verstehst die Bedeutung von IPv6 für die Adressierung massiver Gerätezahlen und kannst basierend auf Reichweite und Energiebedarf zwischen Technologien wie WLAN und LPWAN entscheiden.

---

## Edge Computing und Datenverarbeitung
**Die Verteilung von Rechenlast zwischen Edge und Cloud optimieren**

Du kannst analysieren, wann Datenverarbeitung lokal auf dem Gerät oder Gateway (Edge Computing) stattfinden sollte und wann die Cloud geeigneter ist. Du verstehst Konzepte wie Datenaggregation und Filterung zur Reduktion des Bandbreitenbedarfs sowie den Unterschied zwischen Streaming- und Batch-Verarbeitung.

---

## Sicherheit und Privacy
**IoT-Systeme gegen Angriffe härten und Daten schützen**

Du erkennst spezifische Sicherheitsrisiken wie Standardpasswörter und ungesicherte Übertragungswege. Du kannst Schutzmaßnahmen wie Verschlüsselung, zertifikatsbasierte Authentifizierung und Pseudonymisierung anwenden, um die Vertraulichkeit und Integrität von Sensordaten sowie die Privatsphäre der Nutzer zu gewährleisten.

---

## Anwendungsfelder und Systementwurf
**IoT-Lösungen für Smart Home und Industrie 4.0 konzipieren**

Du kannst typische Anwendungsfälle in Smart Homes und der Industrie 4.0 charakterisieren und Architekturentscheidungen für konkrete Szenarien wie Smart Metering oder Verkehrsmanagement treffen. Dabei wägst du Anforderungen an Skalierbarkeit, Latenz und Sicherheit gegeneinander ab.

---

# Detaillierte Lernziele

Im Kontext des Themas **Internet of Things (IoT) – Grundlagen und Anwendungen** soll dir dieses Fragenset helfen, die folgenden detaillierten Lernziele zu erreichen:

### Reproduktion

**Du kannst …**

1. den Begriff „Internet of Things (IoT)“ definieren und den Kern der Vernetzung physischer, sensorbasierter Objekte beschreiben
2. typische Eigenschaften ressourcenbeschränkter IoT-Geräte beschreiben und sie von allgemeinen Universalrechnern abgrenzen
3. Smart-Home-Szenarien als klassischen Anwendungsbereich des IoT erkennen und anhand typischer Geräte und Funktionen charakterisieren
4. erläutern, wie IoT-Lösungen in der Industrie 4.0 zur Transparenz und Effizienz von Produktionsprozessen beitragen
5. die grundlegenden Schichten einer IoT-Referenzarchitektur, insbesondere die Wahrnehmungs- bzw. Geräteschicht, benennen und kurz beschreiben
6. typische Komponenten der Geräte- bzw. Edge-Ebene wie RFID-Tags, Sensoren und Aktoren identifizieren
7. die Rolle von Gateways im IoT als Vermittler mit Protokollübersetzung, Vorverarbeitung und Datenbündelung beschreiben
8. erkennen, dass im IoT der Begriff „Thing“ für das vernetzte physische Objekt, zum Beispiel einen Sensor, steht
9. MQTT als leichtgewichtiges Publish/Subscribe-Protokoll für ressourcenarme IoT-Anwendungen benennen
10. die wesentlichen Eigenschaften von CoAP im Vergleich zu HTTP wiedergeben und dessen Eignung für ressourcenarme Geräte erläutern
11. erläutern, warum IPv6 mit seinem großen Adressraum für die Adressierung einer sehr großen Zahl von IoT-Geräten besonders bedeutsam ist
12. HTTP als typisches Protokoll für REST-basierte Schnittstellen zur Abfrage von Sensordaten identifizieren
13. den Begriff Edge Computing definieren und seine Rolle bei der lokalen Vorverarbeitung von Sensordaten beschreiben
14. grundlegende Funktionen typischer IoT-Plattformen wie Gerätemanagement, Datenstromverwaltung und Visualisierung von Messwerten beschreiben
15. Standardpasswörter als typisches Sicherheitsrisiko in IoT-Systemen erkennen
16. beschreiben, weshalb Energieeffizienz bei batteriebetriebenen oder schwer zugänglichen IoT-Geräten ein zentraler Entwurfsfaktor ist
17. die Rolle von Middleware in IoT-Systemen als abstrakte Vermittlungsschicht zwischen heterogenen Geräten, Protokollen und Anwendungen charakterisieren

### Anwendung

**Du kannst …**

1. die Datenwege von Sensoren zur Cloud den Ebenen Wahrnehmungs-, Netzwerk-/Transportschicht und Anwendungsschicht korrekt zuordnen
2. bei der Technologieauswahl für batteriebetriebene, weit verteilte Sensoren zwischen Wi-Fi und Low-Power-WAN abwägen und eine geeignete Funktechnologie auswählen
3. Szenarien mit zentralem Broker und abonnierenden Diensten dem Publish/Subscribe-Muster zuordnen
4. Maßnahmen wie Aggregation und Filterung auf Gateways einsetzen, um Datenvolumen und Bandbreitenbedarf in IoT-Systemen zu reduzieren
5. entscheiden, ob komplexe Mustererkennung in einem IoT-Projekt besser auf Edge-Gateways oder in der Cloud umgesetzt werden sollte
6. für Anwendungen mit nahezu Echtzeitanforderungen Streaming-Verarbeitung gezielt gegenüber Batch-Verarbeitung einsetzen
7. Pseudonymisierung oder Anonymisierung als Maßnahme zur Verbesserung des Datenschutzes in IoT-Szenarien mit personenbezogenen Sensordaten einsetzen
8. Verschlüsselung gezielt verwenden, um die Vertraulichkeit von Messdaten auf unsicheren Übertragungswegen zu schützen
9. durch Reduktion der Sendehäufigkeit und Aggregation von Messwerten die Batterielaufzeit eines IoT-Geräts verbessern
10. in verteilten IoT-Systemen Zertifikate oder individuelle Schlüsselpaaren zur sicheren Geräteidentifizierung und Authentifizierung verwenden

### Strukturelle Analyse

**Du kannst …**

1. Risiken einer vernetzten Gebäudeautomation hinsichtlich unbefugter Zugriffe, möglicher physischer Auswirkungen und Datenschutz systematisch analysieren
2. Architekturentscheidungen für ein Smart-Metering-System im Hinblick auf Skalierbarkeit und Datenschutz bewerten und die Wahl einer geeigneten Plattformlösung begründen
3. die Aufgabenteilung zwischen Edge und Cloud in einem Verkehrsmanagementsystem so analysieren, dass zeitkritische Steuerungen und langfristige Optimierungen sinnvoll verteilt werden
