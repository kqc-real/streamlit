# Übergeordnete Lernziele: AMALEA

## **Python & Pandas Grundlagen**
**Grundlegende Python- und Pandas-Konzepte sicher nutzen.**

Du kannst zentrale Python-Konstrukte, Datenstrukturen und den Umgang mit Abhängigkeiten sicher benennen. In pandas verstehst du Kernbegriffe wie DataFrame, Einlesen, Vektorisierung und Performanz-Grundlagen, um Daten sauber zu handhaben.

---

## **Notebooks & Streamlit**
**Interaktive Analysen dokumentieren und Ergebnisse verständlich präsentieren.**

Du nutzt Jupyter Notebooks für eine nachvollziehbare Analyse mit Code- und Markdown-Zellen. In Streamlit setzt du typische Widgets ein und gestaltest einfache, interaktive Daten-Apps.

---

## **Docker & Infrastruktur**
**Reproduzierbare Umgebungen bauen und verwalten.**

Du verstehst die Bausteine von Docker (Images, Container, Dockerfiles) und kannst Multi-Container-Setups mit Compose strukturieren. Zusätzlich kennst du zentrale Konzepte wie Volumes, Layer-Caching und Port-Hinweise.

---

## **QUA³CK & MLOps**
**Projekte strukturiert planen und Wissen transferieren.**

Du ordnest die Phasen des QUA³CK-Modells ein und kennst deren Ziele. Dazu gehört das Experiment-Tracking mit MLflow sowie der Transfer von Ergebnissen in Deployment und Dokumentation.

---

## **Klassische ML-Algorithmen**
**Grundlegende Lernparadigmen und zentrale Algorithmen einordnen.**

Du unterscheidest supervised und unsupervised Learning und kennst die Stärken und Schwächen von Decision Trees, KNN und K-Means. Damit kannst du Algorithmen passend zu typischen Problemen auswählen.

---

## **Deep Learning Grundlagen**
**Kernmechanismen neuronaler Netze verstehen.**

Du kennst die Bauteile neuronaler Netze, Aktivierungen, Verlustfunktionen und den Lernprozess per Backpropagation. Zudem kannst du typische Trainingsprobleme wie Overfitting oder instabile Gradienten einordnen.

---

## **CNNs, Bildverarbeitung & Sequenzen**
**Spezialisierte Architekturen und Filterprinzipien einordnen.**

Du erkennst, warum CNNs für Bilddaten geeignet sind, wie Filter, Weight Sharing und Feature Maps funktionieren und wie klassische Kantenfilter arbeiten. Außerdem kannst du RNNs als Modell für Sequenzdaten auswählen.

# Detaillierte Lernziele

Im Kontext des Themas **AMALEA** soll dir dieses Fragenset helfen, die folgenden detaillierten Lernziele zu erreichen:

### Reproduktion

**Du kannst …**

1. einen DataFrame als tabellarische Datenstruktur definieren.
2. die Standardfunktion `pd.read_csv()` zum Einlesen von CSV-Dateien nennen.
3. den Unterschied zwischen `pip` und `conda` beschreiben.
4. den Unterschied zwischen Liste und Dictionary in Python beschreiben.
5. das Schlüsselwort `def` zur Funktionsdefinition nennen.
6. den Zweck einer `requirements.txt` benennen.
7. den Fehler `ModuleNotFoundError` bei fehlenden Modulen identifizieren.
8. die Methode `df.head()` zur Anzeige der ersten Zeilen nennen.
9. einen Vorteil von Funktionen in der Programmierung benennen.
10. den Unterschied zwischen `import pandas as pd` und `from pandas import *` beschreiben.
11. ein Tuple als unveränderliche Sequenz definieren.
12. den Unterschied zwischen `st.session_state` und normalen Variablen beschreiben.
13. Parquet als performantes Speicherformat für DataFrames benennen.
14. Vektorisierung in `pandas` als Operation auf ganzen Spalten definieren.
15. eine Chained-Assignment-Warnung in `pandas` beschreiben.
16. die Taste `Y` zum Wechsel in eine Code-Zelle in Jupyter Notebooks identifizieren.
17. den Fehler `KeyError` bei Zugriff auf eine nicht existierende Spalte identifizieren.
18. einen zentralen Vorteil von Jupyter Notebooks für explorative Analysen benennen.
19. den primären Anwendungsfall von Streamlit benennen.
20. die Nutzung von `st.sidebar` für Bedienelemente beschreiben.
21. den Fehlertyp `StreamlitAPIException` bei Widget-Fehlern identifizieren.
22. den Zweck von `st.metric` zur KPI-Anzeige benennen.
23. einen Vorteil von Markdown in Jupyter Notebooks benennen.
24. den typischen Einsatz von `st.file_uploader` benennen.
25. die moderne Interpretation der A³-Phase mit MLflow benennen.
26. den Zweck von `@st.cache_data` benennen.
27. das Streamlit-Element `st.columns()` zur Spalten-Darstellung identifizieren.
28. MLflow als Werkzeug für Experiment-Tracking benennen.
29. die Taste `M` zum Wechsel in eine Markdown-Zelle identifizieren.
30. die Best Practice des Modellvergleichs benennen.
31. den Hauptvorteil von Docker für reproduzierbare Arbeitsumgebungen benennen.
32. den Zweck eines Dockerfiles benennen.
33. den Unterschied zwischen Docker-Image und Docker-Container beschreiben.
34. den Zweck einer `docker-compose.yml` benennen.
35. den Unterschied zwischen `docker ps` und `docker images` beschreiben.
36. einen Vorteil von Docker Compose gegenüber einzelnen `docker run`-Befehlen benennen.
37. den Unterschied zwischen `docker stop` und `docker rm` beschreiben.
38. einen Vorteil von Docker für Teamarbeit benennen.
39. den Hauptvorteil von Multi-Stage-Builds in Dockerfiles benennen.
40. den Zweck von Docker-Volumes für Datenpersistenz benennen.
41. den Zweck von `docker-compose down` benennen.
42. den dokumentarischen Zweck von `EXPOSE` im Dockerfile benennen.
43. das Kernziel der Q-Phase im QUA³CK-Modell benennen.
44. den Hauptzweck des QUA³CK-Prozessmodells benennen.
45. die C-Phase (Conclude and Compare) im QUA³CK-Modell benennen.
46. die K-Phase mit Wissens-Transfer und Deployment benennen.
47. den Unterschied zwischen Supervised und Unsupervised Learning beschreiben.
48. einen Vorteil von Entscheidungsbäumen benennen.
49. einen Nachteil einzelner Entscheidungsbäume benennen.
50. das Funktionsprinzip von KNN als Nachbarschaftsmehrheit beschreiben.
51. einen Vorteil des KNN-Algorithmus benennen.
52. einen Nachteil von KNN bei fehlender Skalierung benennen.
53. den Zweck der Ellbogenmethode zur Wahl von `k` benennen.
54. einen internen Knoten im Entscheidungsbaum als Test auf ein Feature beschreiben.
55. einen Vorteil von K-Means benennen.
56. einen Nachteil von K-Means benennen.
57. die 'Big 3'-Algorithmen im ML benennen.
58. ein grundlegendes Merkmal neuronaler Netze benennen.
59. die Hauptfunktion einer Aktivierungsfunktion benennen.
60. Backpropagation als Verfahren zur Gewichtsaktualisierung benennen.
61. eine typische Ursache für Overfitting benennen.
62. Dropout als Regularisierungstechnik benennen.
63. den Zweck einer Loss Function im Training benennen.
64. einen Hauptvorteil von Batch Normalization benennen.
65. das Problem von vanishing bzw. exploding gradients benennen.
66. einen Vorteil von SGD benennen.
67. die Funktion eines Hidden Layers benennen.
68. einen Nachteil der Sigmoid-Funktion in tiefen Netzen benennen.
69. einen Vorteil von Adam gegenüber SGD benennen.
70. die Rolle der Softmax-Funktion in der Ausgabeschicht benennen.
71. einen Nachteil einer zu hohen Lernrate benennen.
72. einen Filter/Kern als Merkmalsdetektor in CNNs beschreiben.
73. die Funktion eines Mean-Filters zur Glättung benennen.
74. Sobel- und Prewitt-Filter zur Kantendetektion benennen.
75. die Wirkung eines Prewitt-Filters in x-Richtung beschreiben.
76. eine Feature Map als Aktivierungskarte benennen.
77. die typische Abfolge von CNN-Layern benennen.

### Anwendung

**Du kannst …**

1. eine Indexierung zur Beschleunigung von Filteroperationen in `pandas` einsetzen.
2. den `stratify`-Parameter zur Erhaltung von Klassenverteilungen einsetzen.
3. den Adjusted Rand Score zur Bewertung von K-Means-Clustern auswählen.
4. K-Means für ein Clustering-Szenario auswählen.
5. ein Beispiel für Unsupervised Learning auswählen.
6. Entscheidungsbäume für regulierte Anwendungsfelder auswählen.
7. KNN für einen Einsatzbereich wie Empfehlungssysteme auswählen.
8. K-Means zur Kundensegmentierung auswählen.
9. CNNs für Aufgaben der Bildverarbeitung auswählen.
10. RNNs für Sequenzdaten auswählen.

### Strukturelle Analyse

**Du kannst …**

1. begründen, warum `COPY requirements.txt` vor `COPY . .` im Dockerfile steht.
2. begründen, warum `k` bei binärer KNN-Klassifikation ungerade sein sollte.
3. vergleichen, warum Entscheidungsbäume keine Feature-Skalierung benötigen.
4. vergleichen, warum KNN flexible Entscheidungsgrenzen ermöglicht.
5. ableiten, warum K-Means ohne Labels eingesetzt werden kann.
6. begründen, warum ReLU gegenüber Sigmoid vorteilhaft ist.
7. begründen, warum Early Stopping Overfitting reduziert.
8. begründen, warum eine gute Gewichtsinitialisierung wichtig ist.
9. ableiten, warum Deep Learning Feature Learning automatisiert.
10. vergleichen, warum CNNs weniger Parameter als Fully-Connected Nets benötigen.
11. analysieren, wie Gewichtsteilung und Pooling Positionsinvarianz ermöglichen.
12. begründen, warum Weight Sharing die Parameterzahl reduziert.
13. vergleichen, dass CNN-Filter gelernt und klassische Filter fest definiert sind.
