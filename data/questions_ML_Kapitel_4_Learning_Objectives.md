# Übergeordnete Lernziele: Trainieren von ML-Modellen

## Grundlagen der Linearen Regression und Parameterschätzung
**Mathematische Grundlagen und vektorielle Darstellungen zur Schätzung optimaler Modellparameter in geschlossener Form beschreiben.**

Dieses Cluster umfasst die Fähigkeit, Vorhersagen eines linearen Modells als gewichtete Summe von Merkmalen zu verstehen und mathematisch abzubilden. Du lernst, wie der Bias-Term ($\theta_0$) durch künstliche Merkmale ($x_0=1$) in die Vektorschreibweise integriert wird, um Berechnungen mittels Skalarprodukten effizient durchzuführen. Zudem vergleichst du analytische Ansätze wie die Normalengleichung und die stabilere Singulärwertzerlegung (SVD) hinsichtlich ihrer algorithmischen Komplexität und Anwendbarkeit bei singulären Matrizen.

---

## Iterative Optimierung mittels Gradientenverfahren
**Die Funktionsweise, Varianten und Konvergenzbedingungen verschiedener Gradientenabstiegsverfahren zur Minimierung von Kostenfunktionen bestimmen.**

In diesem Bereich entwickelst du ein tiefes Verständnis für das Gradientenverfahren als universelles Optimierungswerkzeug. Du lernst, zwischen Batch-, stochastischem (SGD) und Mini-Batch-Gradientenverfahren abzuwägen und deren spezifische Vorteile in Bezug auf Rechengeschwindigkeit und Hardware-Beschleunigung (GPUs) zu nutzen. Dabei beherrschst du die Steuerung zentraler Hyperparameter wie der Lernrate ($\eta$) und setzt Techniken wie Learning Schedules ein, um trotz stochastischen Rauschens eine präzise Konvergenz zum globalen Minimum zu erzwingen.

---

## Modell-Diagnose mittels Lernkurven und Fehleranalyse
**Den Trainingszustand von Modellen anhand grafischer Lernkurven diagnostizieren und die Balance zwischen Bias und Varianz bewerten.**

Du lernst, die Generalisierungsfähigkeit von Machine-Learning-Modellen systematisch zu beurteilen. Durch die Analyse von Lernkurven erkennst du charakteristische Muster von Underfitting (hoher Bias) und Overfitting (hohe Varianz). Du verstehst den Einfluss der Modellkomplexität und der Datenmenge auf diese Fehlerkomponenten und kannst begründen, warum bestimmte Metriken wie der RMSE für die finale Evaluation intuitiver sind als die beim Training genutzte Kostenfunktion (MSE).

---

## Regularisierungstechniken zur Komplexitätskontrolle
**Methoden zur Einschränkung von Modellfreiheitsgraden auswählen und begründen, um die Überanpassung an Trainingsdaten effektiv zu verhindern.**

Dieses Cluster fokussiert sich auf fortgeschrittene Techniken zur Vermeidung von Overfitting. Du lernst die Unterschiede zwischen Ridge- (L2), Lasso- (L1) und Elastic-Net-Regression kennen und setzt diese gezielt zur Gewichtsreduktion oder automatischen Merkmalsauswahl ein. Zudem beherrschst du das Early Stopping als iterative Regularisierungsmethode, um den optimalen Abbruchpunkt des Trainings basierend auf dem Validierungsfehler zu bestimmen.

---

## Probabilistische Klassifikation und Entscheidungsgrenzen
**Logistische und Softmax-Regressionsmodelle zur Wahrscheinlichkeitsschätzung implementieren und deren lineare Entscheidungsgrenzen interpretieren.**

Du erweiterst dein Wissen von der Regression auf Klassifikationsaufgaben. Du lernst, wie die Sigmoid-Funktion (binär) und die Softmax-Funktion (multinomial) Scores in Wahrscheinlichkeitsverteilungen transformieren. Dabei verstehst du den mathematischen Zusammenhang zwischen Logits und Wahrscheinlichkeiten sowie die Bedeutung des Log Loss als Kostenfunktion. Du kannst Entscheidungsgrenzen im Merkmalsraum bestimmen, um diskrete Klassenzugehörigkeiten für neue Datenpunkte vorherzusagen.

---

# Detaillierte Lernziele

Im Kontext des Thema **Trainieren von ML-Modellen** soll dir dieses Fragenset helfen, die folgenden detaillierten Lernziele zu erreichen:

### Reproduktion

**Du kannst …**

1. die Definition der Normalengleichung zur direkten Parameterschätzung wiedergeben
2. den Begriff der Epoche im Kontext iterativer Trainingsverfahren definieren
3. die Funktion der Lernrate $\eta$ als Hyperparameter benennen

### Anwendung

**Du kannst …**

1. Vorhersagen eines linearen Modells mittels Skalarprodukt berechnen
2. ein Batch-Gradientenverfahren anhand eines Python-Codebeispiels identifizieren
3. Merkmalsskalierung zur Beschleunigung der Konvergenz beim Gradientenabstieg einsetzen
4. die Kostenfunktion der Ridge-Regression (L2) formal korrekt aufstellen
5. Ridge-Regularisierung in der Scikit-Learn API mittels `penalty`-Parameter aktivieren
6. den Pfad des Batch-Gradientenverfahrens im Vergleich zum SGD beschreiben
7. Hardware-Vorteile von Mini-Batches für GPU-Berechnungen nutzen
8. die Anzahl neuer Merkmale nach einer Transformation durch `PolynomialFeatures` bestimmen
9. die Sigmoid-Funktion zur Wahrscheinlichkeitsberechnung bei binärer Klassifikation anwenden
10. die Summe der Wahrscheinlichkeiten in einer Softmax-Verteilung bestimmen
11. den Bias-Fehler als Folge falscher Modellannahmen identifizieren
12. Early Stopping basierend auf dem Verlauf des Validierungsfehlers anwenden
13. den Log Loss als Standard-Kostenfunktion für logistische Modelle auswählen
14. künstliche Bias-Merkmale ($x_0 = 1$) zur Vereinfachung der Vektorschreibweise einsetzen
15. den mathematischen Zusammenhang zwischen Logit- und Sigmoid-Funktion bestimmen
16. Vorhersagen an einer Entscheidungsgrenze für neue Instanzen klassifizieren
17. den RMSE als intuitiv interpretierbare Performancemetrik einsetzen
18. Underfitting anhand des Verlaufs von Trainings- und Validierungskurven erkennen

### Strukturelle Analyse

**Du kannst …**

1. die algorithmische Komplexität von SVD-basierten Lösungen gegenüber der Normalengleichung analysieren
2. die Auswirkungen fehlender Daten-Durchmischung (IID-Verletzung) auf SGD ableiten
3. die automatische Merkmalsauswahl der Lasso-Regression gegenüber Ridge abwägen
4. Ursachen für hohe Generalisierungsfehler diagnostizieren und Gegenmaßnahmen ableiten
5. Elastic Net für korrelierte Merkmale gegenüber Lasso begründen
6. die Ursache für die Singularität der Normalengleichung bei $n > m$ herleiten
7. die Auswirkungen steigender Regularisierung auf Bias und Varianz abwägen
8. die Notwendigkeit unregularisierter Bias-Terme $\theta_0$ begründen
9. die Konvergenz von SGD mittels Learning Schedules bewerten