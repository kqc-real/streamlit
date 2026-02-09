# Übergeordnete Lernziele: Data Analytics & Big Data

## Grundlagen & Werkzeuge
**Du beherrschst das technische Ökosystem für reproduzierbare Analysen.**
Du kannst Python-Datenstrukturen sicher nutzen, Umgebungen mit Docker isolieren und interaktive Dashboards mit Streamlit erstellen. Du setzt Git zur Versionskontrolle ein und nutzt Pandas für effiziente Tabellenoperationen sowie die Handhabung verschiedener Dateiformate (CSV, Parquet).

---

## Datenvorbereitung & EDA
**Du kannst Daten explorieren, bereinigen und für die Modellierung transformieren.**
Du identifizierst Ausreißer und fehlende Werte, wendest Feature-Engineering-Techniken an und nutzt PCA zur Dimensionsreduktion. Du verstehst den Einfluss von Skalierung auf distanzbasierte Algorithmen und führst explorative Analysen (EDA) zur Hypothesengenerierung durch.

---

## Datenvisualisierung
**Du kannst komplexe Zusammenhänge durch zielgerichtete Visualisierungen kommunizieren.**
Du wählst passende Diagrammtypen (Scatterplots, Boxplots, Histogramme) aus und nutzt Bibliotheken wie Plotly Express und Seaborn, um Verteilungen, Korrelationen und statistische Kennzahlen interaktiv darzustellen.

---

## Machine Learning Grundlagen
**Du verstehst die theoretischen Fundamente und Zielkonflikte des maschinellen Lernens.**
Du kannst zwischen Regression und Klassifikation unterscheiden, erkennst Overfitting und Underfitting und bewertest den Bias-Variance-Trade-off zur Sicherstellung der Generalisierungsfähigkeit deiner Modelle.

---

## Modelle & Algorithmen
**Du kannst ML-Algorithmen situationsgerecht auswählen und konfigurieren.**
Du kennst die Funktionsweise der "Big 3" Algorithmen (KNN, Decision Trees, K-Means) sowie Ensemble-Methoden wie Random Forest und verstehst deren Vor- und Nachteile hinsichtlich Interpretierbarkeit, Rechenaufwand und Robustheit.

---

## Modellbewertung & Validierung
**Du kannst die Güte von Modellen robust messen und interpretieren.**
Du setzt Kreuzvalidierung und Stratifizierung ein, analysierst Konfusionsmatrizen und wählst kontextabhängig Metriken wie Precision, Recall, F1-Score oder ROC-AUC aus, insbesondere um Fehlentscheidungen bei unausgeglichenen Klassen zu vermeiden.

---

## MLOps & Deployment
**Du kannst den gesamten ML-Lebenszyklus von der Fragestellung bis zum Betrieb steuern.**
Du wendest das QUA³CK-Prozessmodell an, nutzt MLflow für das Experiment-Tracking und stellst Modelle als REST-APIs (FastAPI) oder Cloud-Apps bereit. Du überwachst Modelle im Betrieb auf Daten-Drift und implementierst CI/CD-Pipelines.

---

## Big Data & Systeme
**Du kannst Architekturen für die Verarbeitung massiver Datenmengen entwerfen.**
Du unterscheidest Data Lakes von Warehouses, nutzt spaltenorientierte Formate (Parquet) und verstehst Konzepte wie Partitionierung in Kafka, In-Memory-Verarbeitung in Spark sowie die fundamentalen Trade-offs des CAP-Theorems.

---

## Deep Learning
**Du verstehst die Mechanismen und Architekturen moderner neuronaler Netze.**
Du erklärst Aktivierungsfunktionen, Backpropagation und Optimierer (Adam). Du ordnest spezialisierte Architekturen wie CNNs für Bilder und Transformer für NLP-Aufgaben korrekt zu und nutzt Techniken wie Transfer Learning.

---

## Spezialthemen & Methoden
**Du kannst fortgeschrittene Methoden zur Analyse und Absicherung von KI-Systemen einsetzen.**
Du nutzt Explainable AI (SHAP, LIME) für Transparenz, führst A/B-Tests methodisch sauber durch und verstehst die Prinzipien von Computer Vision (Segmentierung, Augmentation) sowie Reinforcement Learning.

---

## Datenqualität & Leakage
**Du kannst die Integrität von Daten sicherstellen und regulatorische Risiken minimieren.**
Du erkennst und vermeidest Data Leakage durch saubere Pipeline-Trennung, setzt Validierungs-Constraints um und wendest Datenschutzkonzepte wie Anonymisierung und Differential Privacy (Privacy Budget) an.

---

# Detaillierte Lernziele

Im Kontext des Themas **Data Analytics & Big Data** soll dir dieses Fragenset helfen, die folgenden detaillierten Lernziele zu erreichen:

### Reproduktion
**Du kannst …**

1. den Hauptzweck von Docker für reproduzierbare Umgebungen benennen.
2. den Befehl `streamlit run` zum Starten von Web-Apps identifizieren.
3. einen Pandas DataFrame als zweidimensionale, tabellarische Datenstruktur definieren.
4. den Zweck einer `requirements.txt`-Datei zur Abhängigkeitsverwaltung beschreiben.
5. die Standard-Syntax zur Spaltenauswahl in Pandas (`df['Spalte']`) wiedergeben.
6. den Befehl `docker ps` zur Anzeige laufender Container nennen.
7. Python-Datentypen wie Tupel (unveränderlich) und Dictionaries (Key-Value) charakterisieren.
8. die Funktion der `fit()`-Methode beim Modelltraining in Scikit-learn beschreiben.
9. eine Epoche als kompletten Durchlauf durch den Trainingsdatensatz definieren.
10. das Akronym QUA³CK auflösen und die fünf Phasen benennen.
11. das prognostizierte Wachstum des MLOps-Marktes bis 2034 wiedergeben.

### Anwendung
**Du kannst …**

1. `RUN`-Befehle in einem Dockerfile zur Paketinstallation einsetzen.
2. interaktive Streamlit-Widgets wie `st.slider()`, `st.file_uploader()` und `st.sidebar` in Apps integrieren.
3. Pandas-Operationen wie `read_csv()`, `fillna()`, `groupby()` und `concat()` zur Datenmanipulation anwenden.
4. zwischen Supervised (mit Labels) und Unsupervised Learning (ohne Labels) im Kontext unterscheiden.
5. den K-Means-Algorithmus zur Clusterbildung auf ungelabelte Daten anwenden.
6. die Softmax-Aktivierungsfunktion für Multi-Klassen-Klassifikationen in der Ausgabeschicht auswählen.
7. Techniken der Data Augmentation zur Reduktion von Overfitting in der Bildverarbeitung einsetzen.
8. FastAPI zur Bereitstellung von ML-Modellen als performante REST-APIs nutzen.
9. Hyperparameter-Tuning mittels `GridSearchCV` zur Modelloptimierung durchführen.
10. Transfer Learning Workflows (Einfrieren von Schichten, Fine-tuning) für spezialisierte Aufgaben umsetzen.
11. Kreuzvalidierung zur stabilen Schätzung der Modellgüte anwenden.
12. SQL Window Functions (`OVER`-Klausel) für rollierende Metriken in Analysen einsetzen.
13. ein methodisch sauberes A/B-Test-Design (Power, Signifikanz) entwerfen.
14. Erasure Coding als kosteneffiziente Redundanzstrategie in Object Storage Systemen auswählen.
15. Kafka-Keys zur Sicherstellung der Ereignisreihenfolge innerhalb von Partitionen einsetzen.

### Strukturelle Analyse
**Du kannst …**

1. die Elbow-Methode zur Bestimmung der optimalen Clusteranzahl bei K-Means analysieren.
2. die Vorteile von CNNs (Parameter-Effizienz durch Weight Sharing) gegenüber Fully-Connected-Netzen begründen.
3. Transformer-Modelle (Attention-Mechanismus) gegenüber LSTMs hinsichtlich Parallelisierung und Sequenzlänge bewerten.
4. den Nutzen von MLflow für systematisches Experiment-Tracking und Modell-Versionierung herleiten.
5. die Irreführung durch Accuracy bei unbalancierten Klassen diagnostizieren und Precision/Recall als Alternativen ableiten.
6. das Vanishing-Gradient-Problem in tiefen Netzen analysieren und Gegenmaßnahmen (ReLU, Batch Normalization) bewerten.
7. den funktionalen Unterschied zwischen `iloc` (Position) und `loc` (Label) in Pandas herleiten.
8. den Bias-Variance-Trade-off als zentrale Herausforderung für die Generalisierungsfähigkeit begründen.
9. Symptome von Data Leakage (überoptimistische Test-Scores) erkennen und Vermeidungsstrategien (Split before Pre-processing) ableiten.
10. Random Forests als Ensemble-Methode zur Varianzreduktion gegenüber einzelnen Decision Trees bewerten.
11. PCA als statistisches Verfahren zur Dimensionsreduktion unter Beibehaltung maximaler Varianz analysieren.
12. die Implikationen des CAP-Theorems (Konsistenz vs. Verfügbarkeit) für verteilte Systeme ableiten.
13. Kappa-Architekturen (einheitlicher Stream-Pfad) gegenüber Lambda-Architekturen hinsichtlich Komplexität abwägen.
14. das Konzept der Differential Privacy (Privacy Budget) zur Balance zwischen Datennutzen und Anonymität analysieren.
15. Explainable AI Methoden (SHAP, LIME) zur Steigerung der Akzeptanz und Nachvollziehbarkeit von "Black Box"-Modellen bewerten.
