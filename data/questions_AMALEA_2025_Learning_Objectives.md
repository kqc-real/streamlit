Im Kontext des Themas **AMALEA 2025 - Werkzeuge, MLOps und Machine Learning** soll dir dieses Fragenset helfen, die folgenden Lernziele zu erreichen:

# Übergeordnete Lernziele

## 1. Docker & Containerisierung
**Du kannst die Rolle von Docker in modernen Data-Science-Projekten verstehen und anwenden.**

Du verstehst, wie Docker reproduzierbare und isolierte Entwicklungsumgebungen schafft, kannst Dockerfiles als Bauanleitungen für Images erstellen, den Unterschied zwischen Images und Containern erklären, Multi-Container-Anwendungen mit Docker Compose orchestrieren und Docker-Volumes für persistente Datenspeicherung einsetzen. Du erkennst die Vorteile für Team-Zusammenarbeit und kannst Multi-Stage-Builds zur Optimierung von Image-Größen nutzen.

---

## 2. Python & Pandas Grundlagen
**Du kannst grundlegende Python-Konzepte und pandas-Operationen für die Datenanalyse anwenden.**

Du beherrschst fundamentale Python-Konstrukte (Funktionen, Listen, Dictionaries), kannst DataFrames als zentrale Datenstruktur nutzen, CSV-Dateien einlesen und verarbeiten, typische Fehler (KeyError, ModuleNotFoundError) identifizieren und beheben, Paketmanagement mit pip und conda handhaben, sowie Performance-Optimierungen durch Vektorisierung, Indexierung und alternative Datenformate (Parquet) durchführen.

---

## 3. Jupyter Notebooks & Streamlit
**Du kannst interaktive Entwicklungs- und Präsentationsumgebungen für Data-Science-Projekte nutzen.**

Du kannst Jupyter Notebooks für explorative Datenanalyse mit Code, Text und Visualisierungen einsetzen, Zelltypen (Code, Markdown) effektiv nutzen und mit Tastaturkürzeln arbeiten. Du verstehst, wie Streamlit interaktive Web-Anwendungen ermöglicht, kannst Widgets (sidebar, metric, file_uploader, columns) zur UI-Gestaltung verwenden, Session-State für Zustandsverwaltung einsetzen und Caching-Mechanismen für Performance-Optimierung nutzen.

---

## 4. QUA³CK-Prozessmodell & MLOps
**Du kannst strukturierte Prozessmodelle und moderne MLOps-Praktiken auf Data-Science-Projekte anwenden.**

Du verstehst die fünf Phasen des QUA³CK-Modells (Question, Understanding, A³, Conclude, Knowledge Transfer) und kannst sie auf Projekte anwenden. Du erkennst die Bedeutung präziser Problemdefinition in der Q-Phase, kannst systematisches Experiment-Tracking mit MLflow in der A³-Phase durchführen, Modellvergleiche in der C-Phase strukturiert vornehmen und Deployment sowie Portfolio-Erstellung in der K-Phase umsetzen. Du verstehst die Integration von MLOps-Praktiken in klassische Data-Science-Workflows.

---

## 5. Klassische Machine-Learning-Algorithmen
**Du kannst die grundlegenden ML-Paradigmen verstehen und die "Big 3"-Algorithmen situationsgerecht einsetzen.**

Du verstehst den Unterschied zwischen Supervised und Unsupervised Learning und kannst Decision Trees für interpretierbare, regelbasierte Klassifikation nutzen, deren Stärken (White-Box-Charakter) und Schwächen (Overfitting-Tendenz) einordnen. Du kannst K-Nearest Neighbors für distanzbasierte, nicht-parametrische Klassifikation anwenden, Hyperparameter wie k wählen und Feature-Skalierung berücksichtigen. Du beherrschst K-Means für unüberwachtes Clustering, kannst die optimale Clusteranzahl mit der Ellbogenmethode bestimmen und Clustering-Ergebnisse mit dem Adjusted Rand Score bewerten.

---

## 6. Deep Learning Grundlagen
**Du kannst fundamentale Konzepte neuronaler Netze verstehen und auf praktische Probleme anwenden.**

Du verstehst die Architektur neuronaler Netze (Schichten, Gewichte, Aktivierungen), die Rolle von Aktivierungsfunktionen (ReLU, Sigmoid, Softmax) und deren Auswirkungen auf das Training. Du kannst Backpropagation als Lernmechanismus erklären, Probleme wie Vanishing/Exploding Gradients identifizieren und Regularisierungstechniken (Dropout, Batch Normalization, Early Stopping) zur Overfitting-Vermeidung einsetzen. Du verstehst Optimierungsverfahren (SGD, Adam) und deren Trade-offs sowie die Bedeutung von Loss Functions, Lernraten und Gewichtsinitialisierung.

---

## 7. Convolutional Neural Networks (CNNs)
**Du kannst CNNs für Bildverarbeitungsaufgaben verstehen, anwenden und deren Vorteile gegenüber klassischen Ansätzen erkennen.**

Du verstehst die Funktionsweise von Faltungsoperationen (Convolutions) und Pooling-Layern, kannst Filter/Kernels als gelernte Merkmalsdetektoren interpretieren und den Unterschied zu fest definierten klassischen Filtern (Sobel, Prewitt, Mean) erklären. Du erkennst die Vorteile von CNNs (drastische Parameterreduktion durch Weight Sharing, Translation Invariance) gegenüber Fully-Connected Networks und kannst typische CNN-Architekturen (Convolutional → Pooling → Flatten → Dense) für Bildklassifikation und Objekterkennung anwenden.

---

## 8. Fortgeschrittene Deep-Learning-Konzepte
**Du kannst spezialisierte neuronale Netzarchitekturen und deren Anwendungsgebiete einordnen.**

Du verstehst, dass Recurrent Neural Networks (RNNs) für Sequenzdaten (Text, Zeitreihen) mit temporalen Abhängigkeiten geeignet sind. Du erkennst den fundamentalen Vorteil von Deep Learning (automatisches Feature Learning aus Rohdaten) gegenüber klassischen ML-Methoden mit manuellem Feature Engineering und kannst verschiedene Netzarchitekturen (CNNs für Bilder, RNNs für Sequenzen) problemspezifisch auswählen.

# Fragenbezogene Lernziele

## Reproduktion

**Du kannst …**

1. den Hauptvorteil von Docker (reproduzierbare, isolierte Projektumgebungen) benennen.
2. einen DataFrame in pandas als zweidimensionale, tabellarische Datenstruktur definieren.
3. den Zweck eines Dockerfile (Bauanleitung für Docker-Images) beschreiben.
4. die Taste `Y` im Command Mode zur Umwandlung in eine Code-Zelle in Jupyter Notebooks identifizieren.
5. den fundamentalen Unterschied zwischen Docker-Image (schreibgeschützte Vorlage) und Docker-Container (laufende Instanz) erklären.
6. den primären Zweck einer `docker-compose.yml`-Datei (Definition von Multi-Container-Anwendungen) wiedergeben.
7. die Standardfunktion `pd.read_csv()` zum Einlesen von CSV-Dateien in pandas benennen.
8. einen zentralen Vorteil von Jupyter Notebooks (interaktive Code-Ausführung mit Text und Visualisierungen) beschreiben.
9. den primären Anwendungsfall für Streamlit (Erstellung interaktiver Web-Anwendungen) identifizieren.
10. den fundamentalen Unterschied zwischen Listen (geordnete Sequenzen) und Dictionaries (Schlüssel-Wert-Paare) in Python erläutern.
11. das Schlüsselwort `def` zur Definition von Funktionen in Python nennen.
12. den typischen Fehler `ModuleNotFoundError` bei nicht installierten Python-Modulen identifizieren.
13. den Unterschied zwischen `docker ps` (laufende Container) und `docker images` (verfügbare Images) beschreiben.
14. einen wesentlichen Vorteil von Docker Compose (deklarative Verwaltung mehrerer Services) erkennen.
15. die Verwendung von `st.sidebar` zur Platzierung von Steuerelementen in Streamlit erläutern.
16. die Verwendung von `df.head()` zur Anzeige der ersten Zeilen eines DataFrames nennen.
17. einen wesentlichen Vorteil von Funktionen (Wiederverwendbarkeit und logische Strukturierung) beschreiben.
18. den Unterschied zwischen `docker stop` (Container anhalten) und `docker rm` (Container entfernen) erklären.
19. den typischen Fehlertyp `StreamlitAPIException` bei falscher Widget-Verwendung identifizieren.
20. den Zweck des `st.metric`-Widgets (Anzeige von KPIs mit Vergleichswerten) in Streamlit beschreiben.
21. einen Hauptvorteil von Markdown in Jupyter Notebooks (reichhaltige Textformatierung zur Dokumentation) erkennen.
22. den Unterschied zwischen `import pandas as pd` (Alias-Import) und `from pandas import *` (Wildcard-Import) erläutern.
23. den typischen Anwendungsfall für `st.file_uploader` (Hochladen von Benutzerdateien) in Streamlit identifizieren.
24. die Bedeutung von `def` als Schlüsselwort zur Funktionsdefinition in Python wiedergeben.
25. einen Vorteil von Docker für Team-Zusammenarbeit (identische, versionierte Umgebungen) beschreiben.
26. die Performance-Verbesserung durch `set_index()` bei Filteroperationen in pandas erkennen.
27. den Hauptvorteil eines Multi-Stage-Builds (Reduzierung der Image-Größe) in Dockerfiles erklären.
28. den primären Zweck des Dekorators `@st.cache_data` (Caching datenintensiver Funktionen) in Streamlit beschreiben.
29. das Problem persistenter Datenspeicherung durch Docker-Volumes identifizieren.
30. den Unterschied zwischen `st.session_state` (persistent über Reruns) und normalen Variablen in Streamlit erläutern.
31. Parquet als performanteres Datenformat gegenüber CSV für große DataFrames nennen.
32. Vektorisierung in pandas als Anwendung von Operationen auf ganze Spalten definieren.
33. den Zweck des Befehls `docker-compose down` (Stoppen und Entfernen von Ressourcen) beschreiben.
34. den Hauptunterschied zwischen Supervised Learning (gelabelte Daten) und Unsupervised Learning (keine Labels) erklären.
35. das Streamlit-Element `st.columns()` zur Darstellung nebeneinanderliegender Spalten identifizieren.
36. die Optimierung von `COPY requirements.txt` vor `COPY . .` im Dockerfile (Layer-Caching) erkennen.
37. eine Chained Assignment-Warnung in pandas als Hinweis auf Zuweisung auf Kopien beschreiben.
38. MLflow als Werkzeug für Experiment-Tracking im Kurs-Setup identifizieren.
39. die Wirkung der Taste `M` im Command Mode (Umwandlung in Markdown-Zelle) in Jupyter Notebooks nennen.
40. den dokumentarischen Zweck der `EXPOSE`-Anweisung in Dockerfiles erläutern.
41. die Funktion einer Aktivierungsfunktion (Einführung von Nichtlinearität) in neuronalen Netzen beschreiben.
42. einen Mean-Filter als Glättungswerkzeug zur Rauschreduktion in der Bildverarbeitung identifizieren.
43. das Schlüsselwort `def` als Funktionsdefinition in Python wiedergeben.

## Anwendung

**Du kannst …**

1. das Kernziel der Q-Phase (Formulierung der geschäftlichen Fragestellung) im QUA³CK-Modell anwenden.
2. einen `KeyError` bei Zugriff auf nicht existierende Spalten in pandas identifizieren und vermeiden.
3. den wesentlichen Unterschied zwischen `pip` (Python-Pakete) und `conda` (Umgebungen und Nicht-Python-Pakete) einordnen.
4. den Zweck einer `requirements.txt`-Datei (Listing von Paketabhängigkeiten) in Python-Projekten anwenden.
5. die systematische Protokollierung von Experimenten mit MLflow in der A³-Phase einsetzen.
6. den `stratify`-Parameter in `train_test_split` zur Beibehaltung von Klassenverteilungen verwenden.
7. die C-Phase (Conclude and Compare) als Phase für Modellvergleich und Schlussfolgerungen im QUA³CK-Modell identifizieren.
8. die K-Phase mit MLOps-Praktiken (Cloud-Deployment und Portfolio-Erstellung) assoziieren.
9. die Best Practice anwenden, mehrere Algorithmen zu evaluieren statt einen einzelnen zu wählen.
10. die "Big 3"-Algorithmen (Decision Tree, KNN, K-Means) zur konzeptionellen Einordnung von ML-Projekten nutzen.
11. ein grundlegendes Merkmal neuronaler Netze (Schichten von gewichteten Neuronen) auf Architekturen anwenden.
12. typische Ursachen für Overfitting (zu viele Parameter, zu wenig Daten) bei neuronalen Netzen erkennen und adressieren.
13. den Zweck einer Loss Function (Fehlerquantifizierung) im Training neuronaler Netze einsetzen.
14. das Problem von Vanishing/Exploding Gradients in tiefen Netzen identifizieren.
15. einen Vorteil von EntscheidungsBäumen (hohe Interpretierbarkeit) in regulierten Branchen anwenden.
16. einen Nachteil von EntscheidungsBäumen (Overfitting-Tendenz) erkennen und durch Pruning adressieren.
17. die Funktionsweise von K-Nearest Neighbors (Klassifikation per Nachbarschaftsmehrheit) auf praktische Probleme anwenden.
18. die Wahl eines ungeraden `k` bei KNN für binäre Klassifikation begründen.
19. K-Means Clustering für die Gruppierung von Datenpunkten ohne Labels einsetzen.
20. einen Vorteil von K-Means (Entdeckung verborgener Muster) für explorative Datenanalyse nutzen.
21. einen Nachteil von K-Means (a priori Festlegung von k) durch Ellbogenmethode adressieren.
22. die Ellbogenmethode zur Bestimmung einer geeigneten Anzahl von Clustern anwenden.
23. interne Knoten in EntscheidungsBäumen als Feature-basierte Entscheidungsregeln interpretieren.
24. einen Vorteil von KNN (keine Annahmen über Datenverteilung) in flexiblen Szenarien nutzen.
25. einen Nachteil von KNN (Empfindlichkeit gegenüber Feature-Skalierung) durch Normalisierung beheben.
26. einen Vorteil von EntscheidungsBäumen (keine Feature-Skalierung nötig) gegenüber KNN einordnen.
27. einen Vorteil von KNN (flexible Entscheidungsgrenzen) gegenüber EntscheidungsBäumen nutzen.
28. einen Vorteil von K-Means (Unsupervised Learning) gegenüber KNN für unlabelled Daten anwenden.
29. den Adjusted Rand Score zur Bewertung von K-Means-Clustering mit bekannten Labels einsetzen.
30. Prewitt- oder Sobel-Filter zur Kantendetektion in Bildern anwenden.
31. die Wirkung eines Prewitt-Filters in x-Richtung (Hervorhebung vertikaler Kanten) interpretieren.
32. CNNs für Aufgaben mit gitterartigen Daten (Bildklassifikation, Objekterkennung) einsetzen.
33. einen Vorteil des Adam-Optimierers (adaptive Lernraten) gegenüber SGD nutzen.
34. Early Stopping zur Vermeidung von Overfitting durch Validierungsüberwachung anwenden.
35. einen Nachteil einer zu großen Lernrate (Instabilität, Überspringen des Optimums) erkennen.
36. Filter in einem Convolutional Layer als Merkmalsdetektoren interpretieren.

## Strukturelle Analyse

**Du kannst …**

1. die moderne Interpretation der A³-Phase (systematisches Experiment-Tracking mit MLflow) im AMALEA-Ansatz analysieren.
2. einen wesentlichen Vorteil der ReLU-Aktivierung (geringeres Vanishing-Gradient-Problem) gegenüber Sigmoid herleiten.
3. das Backpropagation-Verfahren als effiziente Gradientenberechnung bezüglich der Gewichte analysieren.
4. Dropout als Regularisierungstechnik (zufälliges Deaktivieren von Neuronen) zur Overfitting-Vermeidung interpretieren.
5. einen Hauptvorteil von Batch Normalization (Beschleunigung und Stabilisierung des Trainings) begründen.
6. CNNs als besonders geeignet für gitterartige Daten durch Faltungsoperationen analysieren.
7. einen Vorteil von Stochastic Gradient Descent (Speichereffizienz bei großen Datensätzen) herleiten.
8. die Funktion von Hidden Layers (Lernen hierarchischer, komplexer Merkmale) in neuronalen Netzen interpretieren.
9. einen Nachteil der Sigmoid-Funktion (Vanishing Gradient durch Sättigung) in tiefen Netzen analysieren.
10. einen Vorteil des Adam-Optimierers (individuelle, adaptive Lernraten) gegenüber SGD begründen.
11. Early Stopping als Regularisierung (Abbruch bei Validierungsstagnation) zur Overfitting-Vermeidung interpretieren.
12. die Rolle der Softmax-Funktion (Umwandlung in Wahrscheinlichkeitsverteilung) in der Ausgabeschicht analysieren.
13. die Wichtigkeit guter Gewichtsinitialisierung (Vermeidung von Vanishing/Exploding Gradients) begründen.
14. RNNs als besonders geeignet für Sequenzdaten (Text, Zeitreihen) durch internes Gedächtnis analysieren.
15. einen entscheidenden Vorteil von Deep Learning (automatisches Feature Learning) gegenüber klassischen ML-Algorithmen herleiten.
16. den Hauptvorteil von CNNs (drastische Parameterreduktion durch lokale Verbindungen und Weight Sharing) gegenüber Fully-Connected Networks analysieren.
17. Translation Invariance in CNNs (positionsunabhängige Objekterkennung) durch Gewichtsteilung und Pooling interpretieren.
18. die Wichtigkeit von Weight Sharing (drastische Parameterreduktion) in CNNs begründen.
19. eine Feature Map als Aktivierungskarte nach Filteranwendung in CNNs interpretieren.
20. eine typische CNN-Architektur (Convolutional, Pooling, Flatten, Dense) strukturell analysieren.
21. den Unterschied zwischen gelernten Filtern in CNNs und fest definierten klassischen Filtern (z.B. Sobel) herleiten.
