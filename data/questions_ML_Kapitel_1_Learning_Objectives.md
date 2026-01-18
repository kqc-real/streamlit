# Übergeordnete Lernziele: Machine Learning

## Grundlagen des Machine Learning

**Du verstehst die fundamentalen Konzepte, Definitionen und theoretischen Grundlagen des Machine Learning.**

Du kannst die historische Entwicklung des Feldes nachvollziehen, beginnend mit Arthur Samuels wegweisender Definition von 1959, die Machine Learning als die Fähigkeit von Computern beschreibt, zu lernen ohne explizit programmiert zu werden. Du verstehst zentrale theoretische Konzepte wie das No-Free-Lunch-Theorem und den Bias-Variance-Tradeoff, die dir helfen, die Grenzen und Möglichkeiten von ML-Systemen realistisch einzuschätzen. Du kennst die verschiedenen kognitiven Komplexitätsstufen (Reproduktion, Anwendung, Analyse) und kannst diese auf Lernaufgaben anwenden.

---

## Lernparadigmen und Methodenwahl

**Du kannst verschiedene Machine-Learning-Paradigmen unterscheiden und für gegebene Problemstellungen die geeignete Lernstrategie auswählen.**

Du beherrschst die Unterscheidung zwischen überwachtem, unüberwachtem und Reinforcement Learning sowie deren jeweilige Anwendungsgebiete. Du verstehst die Vor- und Nachteile von Batch- versus Online-Learning und kannst entscheiden, welcher Ansatz für dynamische versus statische Umgebungen geeignet ist. Du kannst fortgeschrittene Methoden wie selbstüberwachtes Lernen, Transfer Learning und teilüberwachtes Lernen anwenden, um dateneffiziente Lösungen zu entwickeln. Du erkennst, wann instanzbasiertes versus modellbasiertes Lernen angebracht ist.

---

## Datenmanagement und Feature Engineering

**Du kannst Trainingsdaten professionell aufbereiten, qualitativ bewerten und durch gezieltes Feature Engineering für Machine-Learning-Aufgaben optimieren.**

Du beherrschst den Umgang mit realen Datenproblemen wie fehlenden Werten, Stichprobenverzerrung und nicht-repräsentativen Daten. Du verstehst die kritische Bedeutung von Datenqualität über Quantität und kannst systematische Fehler in Erhebungsmethoden identifizieren. Durch Feature Engineering kannst du aussagekräftige Merkmale extrahieren und Dimensionsreduktion anwenden, um Trainingsprozesse zu beschleunigen und Overfitting zu reduzieren. Du erkennst die Vorteile der Datenvereinfachung für effizienteres Training.

---

## Modelloptimierung und Fehlerdiagnose

**Du kannst Machine-Learning-Modelle systematisch optimieren, Fehlerquellen diagnostizieren und durch gezielte Maßnahmen die Generalisierungsfähigkeit verbessern.**

Du erkennst die Symptome von Overfitting und Underfitting und kannst gezielt Gegenmaßnahmen wie Regularisierung, Modellanpassung oder Datenaugmentation einsetzen. Du verstehst den fundamentalen Bias-Variance-Tradeoff und kannst die optimale Modellkomplexität für ein gegebenes Problem finden. Du kannst Lernraten konfigurieren und deren Auswirkungen auf Stabilität versus Anpassungsgeschwindigkeit abwägen. Du beherrschst die systematische Fehleranalyse anhand von Trainings- und Testfehlern und kannst daraus die richtigen Schlüsse für Modellverbesserungen ziehen.

---

## Validierung und Evaluation

**Du kannst robuste Validierungsstrategien entwickeln und implementieren, um die wahre Generalisierungsleistung von Modellen unvoreingenommen zu bewerten.**

Du verstehst die kritische Trennung von Trainings-, Validierungs- und Testdatensätzen und deren jeweilige Rollen im ML-Workflow. Du kannst Hold-out-Validierung korrekt anwenden, einschließlich der Wiederverwertung des Validierungsdatensatzes nach der Modellauswahl. Du erkennst subtile Fehlerquellen wie Data Leakage und Test Set Contamination, die zu überoptimistischen Leistungsschätzungen führen. Du weißt, wie Hyperparameter-Tuning korrekt durchzuführen ist, ohne den Testdatensatz zu "verbrauchen".

---

# Detaillierte Lernziele

Im Kontext des Themas **Machine Learning** soll dir dieses Fragenset helfen, die folgenden detaillierten Lernziele zu erreichen:

### Reproduktion

**Du kannst …**

1. die Definition von Machine Learning nach Arthur Samuel (1959) wiedergeben.
2. den Begriff "Trainingsdatensatz" korrekt benennen.
3. die Zuordnung zwischen Gewicht und Cognitive Level beschreiben.

### Anwendung

**Du kannst …**

1. einen Spamfilter als überwachtes Lernen (Klassifikation) einordnen.
2. die Vorhersage von Autopreisen als Regressionsaufgabe identifizieren.
3. Clustering zur Gruppierung ähnlicher Blogbesucher anwenden.
4. Online-Learning mit angepasster Lernrate für dynamische Umgebungen nutzen.
5. Overfitting anhand der Diskrepanz zwischen Trainings- und Testgenauigkeit erkennen.
6. Regularisierung zur Bekämpfung von Overfitting einsetzen.
7. Feature-Extraktion durch Kombination vorhandener Merkmale durchführen.
8. k-nächste-Nachbarn als instanzbasiertes Lernen klassifizieren.
9. sinnvolle Strategien für den Umgang mit fehlenden Werten bestimmen.
10. Anomalieerkennung für die Identifikation betrügerischer Transaktionen anwenden.
11. selbstüberwachtes Vortraining mit anschließendem Finetuning nutzen.
12. den Validierungsdatensatz für Hyperparameter-Tuning und Modellauswahl verwenden.
13. die Auswirkungen einer zu hohen Lernrate auf die Systemstabilität einordnen.
14. die Grenzen der Dimensionsreduktion bei der Modellleistung einschätzen.
15. Stichprobenverzerrung als Ursache für systematische Fehler erkennen.
16. Model Rot durch sich ändernde Datenmuster identifizieren.
17. den Validierungsdatensatz nach der Modellauswahl mit Trainingsdaten kombinieren.

### Strukturelle Analyse

**Du kannst …**

1. die praktischen Implikationen des No-Free-Lunch-Theorems für die Modellauswahl herleiten.
2. die Lernziele eines Reinforcement-Learning-Agents (Policy Learning) analysieren.
3. den Nutzen selbstüberwachten Lernens für nachfolgende Klassifikationsaufgaben begründen.
4. die optimale Modellkomplexität zwischen Underfitting und Overfitting bestimmen.
5. teilüberwachtes Lernen zur effizienten Nutzung gelabelter und ungelabelter Daten einsetzen.
6. Overfitting auf den Testdatensatz durch wiederholte Evaluation diagnostizieren.
7. den Bias-Variance-Tradeoff als fundamentale Herausforderung im Machine Learning interpretieren.
