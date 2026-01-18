# Übergeordnete Lernziele: Machine Learning Grundlagen

## Grundverständnis von Machine Learning
**Machine Learning als datengetriebenen Ansatz verstehen und von klassischer Programmierung abgrenzen**

Du entwickelst ein Verständnis dafür, wie Machine Learning durch das Lernen aus Beispieldaten funktioniert und welche grundlegenden Konzepte wie überwachtes und unüberwachtes Lernen, Generalisierung und Features das Fundament bilden. Du erkennst die zentralen Unterschiede zwischen regelbasierter Programmierung und datengetriebenem Lernen und kannst einordnen, wann welcher Ansatz sinnvoll ist.

---

## Datenvorverarbeitung und Feature Engineering
**Daten für Machine Learning systematisch aufbereiten und transformieren**

Du beherrschst die wesentlichen Techniken zur Vorbereitung von Daten: Du weißt, warum Feature-Skalierung für viele Algorithmen notwendig ist, kannst kategoriale Merkmale mittels One-Hot-Encoding kodieren und erkennst, wann Log-Transformationen sinnvoll sind. Diese Kompetenzen bilden die Grundlage für erfolgreiches Training und stabile Modelle.

---

## Modellauswahl und -anwendung
**Verschiedene ML-Modelle kennen und situationsgerecht einsetzen**

Du kannst zentrale Modellklassen wie logistische Regression, Entscheidungsbäume, k-nächste Nachbarn und lineare Regression unterscheiden und deren typische Einsatzgebiete benennen. Du verstehst, für welche Aufgabentypen – Klassifikation oder Regression – welches Modell geeignet ist und welche grundlegenden Eigenschaften die Verfahren auszeichnen.

---

## Evaluation und Metriken
**Modellleistung messen, interpretieren und kritisch bewerten**

Du kennst zentrale Evaluationsmetriken wie Accuracy, Precision, Recall, ROC-AUC und PR-AUC und verstehst deren Bedeutung. Du kannst einschätzen, warum bei unausgewogenen Klassen spezifische Metriken wie PR-AUC aussagekräftiger sind als Accuracy, und weißt, wie Validierungs- und Testsets zur robusten Bewertung eingesetzt werden. Du erkennst die Notwendigkeit, Schwellenwerte anwendungsspezifisch zu wählen und Metriken im Kontext von Kosten und Nutzen zu interpretieren.

---

## Training und Optimierung
**Trainingsverfahren verstehen und Parameter gezielt steuern**

Du verstehst die Rolle zentraler Trainingskonzepte wie Loss-Funktionen, Lernrate, Epochen und Batch-Normalisierung. Du erkennst, wie diese Parameter die Konvergenz, Stabilität und Geschwindigkeit des Trainings beeinflussen, und kannst grundlegende Optimierungsstrategien anwenden.

---

## Regularisierung und Generalisierung
**Overfitting vermeiden und Modellkomplexität kontrollieren**

Du kennst Regularisierungstechniken wie L1- und L2-Regularisierung sowie Dropout und verstehst deren Wirkungsweise. Du erkennst die Unterschiede zwischen den Verfahren – etwa dass L1 zu spärlichen Lösungen führt, während L2 Gewichte gleichmäßiger schrumpft – und kannst diese gezielt einsetzen, um die Generalisierung zu verbessern.

---

## Validierung und Splits
**Datensplitting systematisch durchführen und Leakage vermeiden**

Du verstehst die Bedeutung von Trainings-, Validierungs- und Testsets und kennst Techniken wie Kreuzvalidierung und Stratifizierung. Du kannst Datenlecks in ML-Pipelines erkennen und durch korrekte Anwendung von Preprocessing-Schritten innerhalb von Folds vermeiden. Du weißt, wie probabilistische Klassifikatoren durch Schwellenwahl an Anwendungsziele angepasst werden.

---

## Unüberwachtes Lernen
**Strukturen in Daten ohne Labels erkennen und bewerten**

Du verstehst die Ziele unüberwachter Verfahren und kannst grundlegende Clustering-Algorithmen wie k-Means anwenden. Du erkennst die Herausforderungen hochdimensionaler Daten (Fluch der Dimensionalität) und kannst die Qualität von Clustern mittels Metriken wie der Silhouette bewerten.

---

## Ethik und verantwortungsvoller ML-Einsatz
**ML-Systeme transparent, fair und nachvollziehbar gestalten**

Du erkennst die Bedeutung von Transparenz, Fairness und Datenethik im ML-Kontext. Du verstehst, wie systematische Verzerrungen (Bias) entstehen können, und kennst Praktiken wie Monitoring, Dokumentation und Reproduzierbarkeit, die einen verantwortungsvollen Einsatz von ML-Systemen sicherstellen.

---

# Detaillierte Lernziele

Im Kontext des Themas **Machine Learning Grundlagen** soll dir dieses Fragenset helfen, die folgenden detaillierten Lernziele zu erreichen:

### Reproduktion
**Du kannst …**

1. das Hauptziel von Machine Learning im Vergleich zu klassischer Programmierung benennen
2. den Unterschied zwischen überwachtem und unüberwachtem Lernen beschreiben
3. einen Datensatz im ML-Kontext definieren
4. Generalisierung beschreiben
5. ein Feature im Sinne von Machine Learning definieren
6. den Zweck von Feature-Skalierung nennen
7. One-Hot-Encoding beschreiben
8. Anwendungsfälle für Log-Transformationen identifizieren
9. typische Modellklassen für Klassifikationsaufgaben nennen
10. den Einsatzzweck von Entscheidungsbäumen beschreiben
11. k-nächste Nachbarn als Lernverfahren charakterisieren
12. den Zweck linearer Regression beschreiben
13. Precision als Kennzahl für binäre Klassifikation definieren
14. den Nutzen der ROC-AUC benennen
15. die Funktion eines Validierungssplits beschreiben
16. die Bedeutung der Lernrate bei Gradientenverfahren nennen
17. einen Epochendurchlauf definieren
18. die Rolle der Loss-Funktion im Training beschreiben
19. den Nutzen von Kreuzvalidierung nennen
20. den Zweck eines Testsets beschreiben
21. die Wirkung von L2-Regularisierung beschreiben
22. den Hauptunterschied zwischen L1- und L2-Regularisierung nennen
23. den Zweck von Dropout beschreiben
24. überwachtes Lernen charakterisieren
25. typische Ziele unüberwachter Lernverfahren nennen
26. die Rolle von Transparenz in ML-Projekten beschreiben
27. Bias im ethischen Kontext definieren

### Anwendung
**Du kannst …**

1. Batch-Normalisierung in tiefen Netzen zur Stabilisierung einsetzen
2. Stratifizierung bei unausgewogenen Klassen anwenden
3. binäre Kreuzentropie als Loss-Funktion für binäre Klassifikation auswählen
4. geeignete Metriken bei unausgewogenen Klassen bestimmen
5. k-Means zur Clusterbildung anwenden
6. die Silhouette zur Bewertung von Clustern nutzen
7. Herausforderungen hochdimensionaler Daten für distanzbasierte Verfahren erkennen
8. Monitoring und Evaluationskriterien im Betrieb umsetzen
9. Datenlecks in ML-Pipelines durch korrekte Validierung vermeiden

### Strukturelle Analyse
**Du kannst …**

1. PR-AUC als Metrik bei stark unausgewogenen Klassen begründen
2. die Schwellenwahl bei probabilistischen Klassifikatoren in Bezug auf Kosten und Nutzen ableiten
3. Herausforderungen der Datenethik im ML-Kontext analysieren
4. Maßnahmen zur Reproduzierbarkeit von ML-Experimenten bewerten
