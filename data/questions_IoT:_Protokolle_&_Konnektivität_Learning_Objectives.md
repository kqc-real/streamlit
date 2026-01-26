# Übergeordnete Lernziele: IoT: Protokolle & Konnektivität

## 1. Architekturgrundlagen & IoT-Trilemma
**Die physikalischen und strukturellen Grenzen von IoT-Systemen verstehen**

Du entwickelst ein Verständnis für die grundlegenden Kompromisse im Internet of Things (Reichweite, Datenrate, Energie) und kennst die Basisarchitekturen der wichtigsten Protokolle (REST vs. Pub/Sub, Mesh vs. Star). Du weißt, wie Adressierung (IPv6 vs. proprietär) und Transport (TCP vs. UDP) das Systemdesign beeinflussen.

---

## 2. Technologie-Auswahl für Konnektivität
**Die passende Funktechnologie für spezifische Einsatzszenarien bestimmen**

Du erlernst die Fähigkeit, basierend auf Anforderungen wie Gebäudedurchdringung, Infrastrukturkosten und Bandbreitenbedarf die richtige Übertragungstechnologie auszuwählen. Dies umfasst die Abgrenzung von LPWAN-Technologien (LoRaWAN, NB-IoT), modernen Mobilfunkstandards (5G RedCap) und lokalen Netzwerken (Wi-Fi 6).

---

## 3. Protokoll-Optimierung & Performance
**Effiziente Datenübertragung auf Anwendungsebene gestalten**

Du kannst bewerten, wann verbindungsorientierte (MQTT) oder verbindungslose Protokolle (CoAP) effizienter arbeiten. Du verstehst Mechanismen zur Reduktion von Overhead und Latenz (z. B. Observe-Pattern, TWT) und kannst deren Auswirkungen auf Energieverbrauch und Netzwerklast in stabilen sowie instabilen Umgebungen analysieren.

---

## 4. Interoperabilität & Sicherheit
**Integrierbare und sichere IoT-Lösungen konzipieren**

Du bist in der Lage, Standards für die herstellerübergreifende Kommunikation im Smart Home (Matter) und in der Industrie (MQTT Sparkplug B) zielgerichtet einzusetzen. Zudem kannst du moderne kryptografische Verfahren (Lightweight Cryptography/Ascon) für ressourcenbeschränkte Hardware auswählen.

---

# Detaillierte Lernziele

Im Kontext des Themas **IoT: Protokolle & Konnektivität** soll dir dieses Fragenset helfen, die folgenden detaillierten Lernziele zu erreichen:

### Reproduktion

**Du kannst …**

1. die drei konkurrierenden Parameter des IoT-Trilemmas (Reichweite, Datenrate, Batterielaufzeit) benennen
2. das Transportprotokoll und das Architekturmodell von CoAP identifizieren
3. den architektonischen Hauptunterschied zwischen Thread und Zigbee bezüglich der IP-Adressierung benennen

### Anwendung

**Du kannst …**

1. MQTT als Protokoll für Szenarien mit einem Sender und vielen Empfängern auswählen
2. den Vorteil verbindungsloser Kommunikation (CoAP) in instabilen Netzwerken erkennen
3. den Nutzen von MQTT Sparkplug B für die semantische Interoperabilität in der Industrie bestimmen
4. Target Wake Time (TWT) als Schlüsselfunktion für den Batteriebetrieb in Wi-Fi-6-Netzwerken bestimmen
5. den Matter-Standard für herstellerübergreifende, lokale Smart-Home-Kompatibilität identifizieren
6. NB-IoT für Deep-Indoor-Szenarien unter Nutzung vorhandener Provider-Infrastruktur auswählen
7. 5G RedCap als Technologie für Mid-Tier-Anwendungen mit mittlerem Bandbreitenbedarf klassifizieren
8. den Algorithmus Ascon für die Verschlüsselung auf ressourcenbeschränkten Mikrocontrollern auswählen

### Strukturelle Analyse

**Du kannst …**

1. die Latenzvorteile von TCP gegenüber UDP-Applikationsprotokollen bei stabiler Verbindung begründen
2. die Effizienz des CoAP-Observe-Mechanismus im Vergleich zu HTTP-Polling herleiten
3. die Skalierungsgrenzen von Managed Flooding (BLE Mesh) gegenüber Routing (Thread) in großen Netzen bewerten
4. die strategische Entscheidung für private LoRaWAN-Netze aus ökonomischen und hoheitlichen Anforderungen ableiten
