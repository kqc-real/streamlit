# Übergeordnete Lernziele: Cloud Computing – MC-Test Themenblock TB09: Security, Observability und Resilienz

## **IAM und Netzwerk**
**Identitäten und Netzpfade an der serverseitigen Vertrauensgrenze absichern.**

Du unterscheidest Session-Kennung von Berechtigung und beschränkst Rechte nach Aufgabe und Dauer. Private Endpunkte und passend gewählte Rate-Limits verringern unnötige Erreichbarkeit und Fehlblockaden.

---

## **Secrets und Software-Lieferkette**
**Zugangsdaten und Softwarekomponenten über ihren gesamten Lebenszyklus kontrollieren.**

Du bevorzugst kurzlebige Berechtigungen und unveränderliche Artefaktreferenzen. Softwarestücklisten unterstützen die Bestandsaufnahme; bei einem Vorfall verbindest du Eindämmung mit Neubau und Prüfung.

---

## **Datenschutz und Telemetrie**
**Betriebliche Diagnose mit Datenminimierung verbinden.**

Du beschränkst Telemetrie auf zweckgebundene Kategorien und erkennst Messlücken als unbekannten Zustand. Verteilte Traces helfen, Laufzeiten über Dienstgrenzen hinweg zu lokalisieren.

---

## **SLI, SLO und Alarmierung**
**Nutzerbezogene Zuverlässigkeitsziele messen und handlungsrelevant überwachen.**

Du wählst Kennzahlen für tatsächlich erfolgreiche Vorgänge und ordnest Fehlerbudgets korrekt ein. Zeitfenster, Schweregrade und Recovery-Meldungen begrenzen Alarmrauschen, ohne anhaltende Fehler zu verbergen.

---

## **Resilienz und kontrollierte Degradation**
**Ausfälle begrenzen und Kernfunktionen unter Belastung erhalten.**

Du erkennst gemeinsame Fehlerdomänen und begrenzt optionale Arbeit mit Backpressure und Ressourcenisolation. Wiederherstellungs- und Funktionstests zeigen, ob die Rückkehr in einen gesunden Betrieb tatsächlich gelingt.

---

## **Behebung und Verifikation**
**Sicherheitsmaßnahmen mit reproduzierbarer Evidenz und Regressionstests absichern.**

Du untersuchst Befunde im konkreten Artefakt und testest verbotene Netzpfade gezielt. Eine Maßnahme ist erst belastbar, wenn sie den Angriffspfad schließt und legitime Kernfunktionen erhält.

---

# Detaillierte Lernziele

Im Kontext von **Cloud Computing – MC-Test Themenblock TB09: Security, Observability und Resilienz** unterstützt dich dieses Fragenset dabei, die folgenden detaillierten Lernziele zu erreichen:

### Anwendung

**Du kannst …**

1. eine serverseitige Host-Autorisierung mit validiertem Host-Token auswählen.
2. einer CI-Identität kurzlebige und ressourcenbegrenzte Rechte zuordnen.
3. einen privaten Netzpfad mit minimaler Dienstfreigabe auswählen.
4. die serverseitige Identitätsprüfung für einen privilegierten Lesepfad bestimmen.
5. ein teilnehmerbezogenes Rate-Limit für gemeinsam genutzte NAT-Adressen auswählen.
6. eine kurzlebige Credential-Strategie für einen CI-Job auswählen.
7. einen Image-Digest als unveränderliche Build-Referenz erkennen.
8. den Nutzen eines SBOM für Komponenten- und Versionsinventare bestimmen.
9. nach einer Token-Offenlegung die unmittelbar schadenbegrenzende Maßnahme bestimmen.
10. eine datensparsame Telemetrie für Rate-Limit-Ereignisse auswählen.
11. einen verteilten Trace zur Laufzeitlokalisierung über mehrere Dienste einsetzen.
12. einen Fehlerbudgetwert in Bezug auf das festgelegte SLO-Fenster einordnen.

### Strukturelle Analyse

**Du kannst …**

1. den Umgang mit einer kompromittierten transitiven Abhängigkeit anhand von Inventur, Neubau und Verifikation begründen.
2. einen minimierten Snapshot für eine inhaltliche Q&A-Analyse auswählen.
3. eine zweckgebundene und zeitlich begrenzte Log-Aufbewahrung begründen.
4. einen Messausfall im Dashboard als unbekannten statt gesunden Zustand einordnen.
5. einen nutzerbezogenen Join-SLI für ein Zuverlässigkeitsziel auswählen.
6. ein handlungsrelevantes Alarmverhalten für wiederkehrende Reconnect-Fehler bewerten.
7. einen aktiven kritischen Alarm bei ausgefallener Monitoring-Probe beibehalten.
8. eine evidenzbasierte Runbook-Änderung für Ressourcenlimits herleiten.
9. die Grenzen mehrerer Instanzen in einer gemeinsamen Fehlerdomäne beurteilen.
10. kontrollierte Degradation bei langsamem optionalem Inferenzdienst auswählen.
11. Backpressure-Maßnahmen für eine überlastete optionale Queue bestimmen.
12. die Aussagekraft eines erfolgreichen Backups gegenüber einem ungetesteten Restore bewerten.
13. die Ressourcenkopplung eines ML-Workers an den Live-Prozess analysieren.
14. eine Behebungs- und Verifikationsfolge für einen exponierten Verwaltungsport auswählen.
15. einen Scannerbefund anhand von Artefakt, Version und Erreichbarkeit nachvollziehbar einordnen.
16. einen Negativtest für einen verbotenen öffentlichen Datenbankpfad auswählen.
17. eine Härtungsmaßnahme mit betrieblicher Regression gemeinsam neu entwerfen.
18. verbleibende Modell-, Lieferketten- und Last-Risiken belastbar dokumentieren.
