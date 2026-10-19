# Übergeordnete Lernziele: Cloud Computing – MC-Test Themenblock TB03: Bereitstellung, Zustandsgrenzen und Härtung

## **Reproduzierbare Bereitstellung**
**Builds, Datenbankmigrationen und Backups auf überprüfbare Wiederholbarkeit ausrichten.**

Du bindest Bereitstellungen an eindeutige Artefakte und festgelegte Build-Eingaben. Versionierte Migrationen, idempotente Bereitstellung und bestandene Wiederherstellungstests bilden nachvollziehbare Betriebsschritte.

---

## **Single-Host-Architektur**
**Diensttopologie und Fehlergrenzen eines Einzelhosts bewerten.**

Du erkennst den Produktionskern und optionale Sidecars sowie den vorgesehenen Proxyzugang. Du berücksichtigst, dass Container auf einem gemeinsamen Host keine unabhängige Hochverfügbarkeit schaffen.

---

## **Zustand und Persistenz**
**Flüchtige, relationale und zeitnahe Zustände ihren passenden Diensten zuordnen.**

Du unterscheidest PostgreSQL, Redis und browserseitige Local-First-Datenhaltung. Bei Prozessausfällen und mehreren Instanzen berücksichtigst du, welche Zustände geteilt, dauerhaft oder rekonstruierbar sein müssen.

---

## **Speicher und Zustände**
**Speicherlösungen nach Zugriffsmuster und Lebensdauer auswählen.**

Du grenzt Block-, Datei- und Objektspeicher vom kurzlebigen Container-Layer ab. Backups und gemeinsam beschriebene Dateien bewertest du anhand von Konsistenz- und Zugriffsgarantien.

---

## **Vertrauensgrenzen**
**Sicherheitsgrenzen vom Worker bis zur Netzwerkverbindung nachvollziehen.**

Du prüfst Isolation, Datenfreigabe, Autorisierung und Proxyzugriff anhand der jeweiligen Vertrauensannahmen. Eine neue Instanz oder ein Load Balancer ersetzt weder geteilten Zustand noch eine geregelte Wiederverbindung.

---

## **Härtung und Betrieb**
**Betriebsfreigaben auf minimale Rechte und belastbare Nachweise stützen.**

Du begrenzt Ports und vertrauliche Werte, minimierst Protokolldaten und steuerst Fehlerfälle kontrolliert. Eine Freigabe setzt neben grünen Integritätsprüfungen auch geprüfte Wiederherstellung und dokumentierte Restabweichungen voraus.

---

# Detaillierte Lernziele

Im Kontext von **Cloud Computing – MC-Test Themenblock TB03: Bereitstellung, Zustandsgrenzen und Härtung** unterstützt dich dieses Fragenset dabei, die folgenden detaillierten Lernziele zu erreichen:

### Anwendung

**Du kannst …**

1. ein freigegebenes Containerartefakt anhand seines Image-Digests identifizieren.
2. die Reihenfolge von Datenbankstart, Migrationen und App-Start für ein sicheres Deployment bestimmen.
3. eine fehlende Festlegung der Zielarchitektur als Ursache eines unterschiedlichen Build-Ergebnisses diagnostizieren.
4. die Eignung eines Backups anhand eines erfolgreichen Wiederherstellungstests beurteilen.
5. eine wiederholte Bereitstellung anhand des Sollzustands als idempotent einordnen.
6. die obligatorischen Dienste des Produktions-Compose bestimmen.
7. die Loopback-Portbindung als Beschränkung des öffentlichen Einstiegs einordnen.
8. optionale NLP-Hilfsdienste dem aktivierten Compose-Profil zuordnen.
9. den gemeinsamen Host als verbleibende Ausfallgrenze bestimmen.
10. die Schema-Kompatibilität eines früheren Images nach einer Datenbankmigration beurteilen.
11. PostgreSQL als relationale Persistenz für den Live-Domänenzustand zuordnen.
12. Redis als Dienst für zeitnahe Hilfszustände und TTL-Daten einordnen.

### Strukturelle Analyse

**Du kannst …**

1. eine Local-First-Quizsammlung von ihrer serverseitigen Live-Sitzungskopie abgrenzen.
2. prozesslokale Ereignisverteilung als Skalierungsrisiko für mehrere Instanzen analysieren.
3. Auswirkungen eines Redis-Ausfalls anhand der getrennten Zustandsrollen bewerten.
4. getrennte WebSocket-Pfade anhand ihrer Protokoll- und Berechtigungsanforderungen beurteilen.
5. die Grenzen eines Load Balancers bei prozesslokalen Signalen, Verbindungen und Limits analysieren.
6. die Wiederherstellung lokalen Sitzungszustands nach einem Instanzausfall beurteilen.
7. ein instanzübergreifendes Kapazitätskonzept für die PDF-Erzeugung bewerten.
8. unterschiedliche Lastprofile anhand verteilter Sessions und einzelner Hotspots vergleichen.
9. einen PDF-Worker anhand seiner beschränkten Netzwerk- und Berechtigungswege als Vertrauensgrenze beurteilen.
10. die Wirkung unprivilegierter Containerrechte und eines schreibgeschützten Root-Dateisystems bewerten.
11. die Entfernung von Lösungsdaten vor der Auslieferung als serverseitige Vertrauensgrenze begründen.
12. eine Hostberechtigung anhand einer validierten Capability statt anhand einer URL beurteilen.
13. Proxykonfiguration und interne Ports als geschützten Eintrittspfad analysieren.
14. eine unnötige öffentliche Portfreigabe durch minimale Netzwerkregeln begrenzen.
15. produktive Secrets von versionierten und ausgelieferten Artefakten trennen.
16. datensparsame Rate-Limit-Protokollierung anhand notwendiger Diagnoseinformationen bestimmen.
17. einen hängenden PDF-Worker anhand eines fatalen Neustartpfads kontrolliert wiederherstellen.
18. eine Betriebsfreigabe anhand von Wiederherstellung, Negativtest und dokumentierten Restabweichungen beurteilen.