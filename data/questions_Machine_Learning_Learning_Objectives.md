# Übergeordnete Lernziele: Machine Learning & Deep Learning

## Grundlagen & Praxis
**Du verstehst den Paradigmenwechsel hin zu datengetriebenen Systemen.**
Du kannst den Unterschied zwischen klassischer Programmierung und Machine Learning erklären. Du identifizierst passende Problemtypen (Regression, Klassifikation, Clustering) für Business-Anforderungen und bewertest ethische Risiken wie Bias, Fairness und Datenschutz (z. B. Federated Learning).

---

## Neuronale Netze – Grundlagen
**Du beherrschst die Architektur und Mechanik künstlicher Neuronen.**
Du kannst den Informationsfluss in Schichten (Input, Hidden, Output) beschreiben und die Rolle von Gewichten und Bias erklären. Du verstehst, wie Aktivierungsfunktionen (ReLU, Sigmoid, Softmax) Nichtlinearität einführen und wie Backpropagation den Fehler zur Gewichtsaktualisierung nutzt.

---

## Training & Optimierung
**Du kannst Lernprozesse steuern, stabilisieren und optimieren.**
Du setzt Optimierungsalgorithmen wie SGD und Adam gezielt ein und steuerst die Konvergenz über die Lernrate. Du wendest Regularisierungstechniken (Dropout, L1/L2, Early Stopping) an, um Overfitting zu vermeiden, und nutzt Batch Normalization für stabileres Training.

---

## Netzarchitekturen
**Du wählst spezialisierte Architekturen passend zur Datenstruktur aus.**
Du verstehst Faltungsoperationen in CNNs für räumliche Muster (Bilder), rekurrente Strukturen (LSTM/GRU) für sequentielle Abhängigkeiten und den Attention-Mechanismus in Transformern für hochparallele NLP-Aufgaben. Du kannst das kompetitive Prinzip von GANs (Generator vs. Diskriminator) erklären.

---

## Anwendungen
**Du nutzt moderne Workflows für effiziente Modellentwicklung.**
Du setzt Transfer Learning ein, um vortrainiertes Wissen (z. B. ImageNet) auf neue Aufgaben zu übertragen, und nutzt Data Augmentation zur künstlichen Erweiterung von Datensätzen. Du verstehst die Konzepte hinter Objekterkennung (YOLO, Faster R-CNN) und NLP-Embeddings.

---

## Reinforcement Learning
**Du verstehst das Prinzip des Lernens durch Interaktion und Belohnung.**
Du kannst das Zusammenspiel von Agent, Umgebung, Zustand und Aktion beschreiben. Du analysierst den Exploration-Exploitation Trade-off und verstehst, wie eine Policy die langfristige kumulative Belohnung maximiert.

---

## Überwachtes Lernen
**Du entwickelst präzise Vorhersagemodelle auf Basis von Labels.**
Du unterscheidest zwischen Regression (kontinuierlich) und Klassifikation (diskret). Du kannst Algorithmen wie SVM (inkl. Kernel-Trick), k-NN und Entscheidungsbäume hinsichtlich ihrer Eignung für spezifische Datensätze bewerten.

---

## Unüberwachtes Lernen
**Du entdeckst verborgene Strukturen und Redundanzen in Rohdaten.**
Du nutzt Clustering (k-Means) zur Segmentierung, PCA und SVD zur Dimensionsreduktion sowie Autoencoder zur Merkmalsextraktion oder Anomalieerkennung, ohne auf vordefinierte Zielwerte angewiesen zu sein.

---

## Modellbewertung & Validierung
**Du sicherst die Generalisierungsfähigkeit und Robustheit deiner Modelle.**
Du interpretierst Metriken wie MSE, Precision, Recall und ROC-AUC/PR-AUC im Kontext der Fehlerkosten. Du setzt Cross-Validation und Stratifizierung ein, um belastbare Leistungsschätzungen zu erhalten und den Bias-Variance Trade-off zu optimieren.

---

## Daten & Features
**Du transformierst Rohdaten in aussagekräftige Repräsentationen.**
Du beherrschst Techniken wie Standardisierung, One-Hot-Encoding und Log-Transformationen. Du verstehst den Einfluss der Feature-Skalierung auf distanzbasierte Verfahren und die Bedeutung des Feature-Learnings in tiefen Netzen.

---

## Lineare Algebra
**Du verstehst die mathematische Sprache der Algorithmen.**
Du führst Matrixoperationen (Multiplikation, Transposition, Inversion) sicher aus. Du nutzt Konzepte wie Eigenwerte, Orthogonalität und Vektornormen (L1/L2), um die Geometrie von Datenräumen und Regularisierungseffekten zu verstehen.

---

## Statistik & Wahrscheinlichkeit
**Du nutzt statistische Prinzipien für Modellierung und Inferenz.**
Du wendest den Satz von Bayes für probabilistische Vorhersagen an und nutzt Maximum Likelihood Estimation (MLE) zur Parameterschätzung. Du analysierst Verteilungen über Erwartungswert, Varianz und Kovarianzmatrizen.

---

# Detaillierte Lernziele

Im Kontext des Themas **Machine Learning & Deep Learning** soll dir dieses Fragenset helfen, die folgenden detaillierten Lernziele zu erreichen:

### Reproduktion
**Du kannst …**

1. den Zweck einer Aktivierungsfunktion (Einführung von Nichtlinearität) benennen.
2. die Bestandteile eines GANs (Generator und Diskriminator) identifizieren.
3. die Definition einer Epoche als vollständigen Durchlauf durch den Trainingsdatensatz wiedergeben.
4. den Unterschied zwischen überwachtem (mit Labels) und unüberwachtem Lernen (ohne Labels) nennen.
5. die Standard-Syntax für Matrixmultiplikation in NumPy (`dot()` oder `@`) identifizieren.
6. den Zweck von Dropout (Regularisierung durch zufälliges Deaktivieren von Neuronen) beschreiben.
7. die Formel des Satzes von Bayes und die Bedeutung von Prior und Posterior benennen.
8. den Unterschied zwischen Klassifikation (diskret) und Regression (kontinuierlich) wiedergeben.
9. die Funktion der `fit()`-Methode beim Modelltraining beschreiben.
10. den Begriff „Sparsity“ im Zusammenhang mit L1-Regularisierung definieren.

### Anwendung
**Du kannst …**

1. die Softmax-Funktion für Multi-Klassen-Klassifikationen in der Ausgabeschicht auswählen.
2. Techniken der Data Augmentation (Drehen, Spiegeln) zur Reduktion von Overfitting einsetzen.
3. Transfer Learning Workflows (Einfrieren von Schichten, Fine-tuning) für Bilddaten umsetzen.
4. den k-Means-Algorithmus zur Clusterbildung auf ungelabelte Daten anwenden.
5. Matrix-Vektor-Produkte und Gradienten einfacher Funktionen berechnen.
6. One-Hot-Encoding zur Transformation kategorialer Merkmale anwenden.
7. Kreuzvalidierung zur stabilen Schätzung der Modellgüte einsetzen.
8. den Adam-Optimierer zur adaptiven Anpassung der Lernrate konfigurieren.
9. Log-Transformationen zur Behandlung rechtsschiefer Verteilungen nutzen.
10. Precision und Recall im Kontext von unausgeglichenen Klassen (z. B. Betrugserkennung) interpretieren.
11. Skip Connections (Residual Learning) zur Ermöglichung tieferer Architekturen einsetzen.
12. den Kernel-Trick in SVMs zur Trennung nicht-linearer Daten anwenden.
13. Early Stopping basierend auf der Validierungs-Loss-Kurve implementieren.
14. den Erwartungswert einer Zufallsvariablen aus gegebenen Wahrscheinlichkeiten berechnen.
15. die L2-Norm zur Berechnung der euklidischen Länge von Vektoren nutzen.

### Strukturelle Analyse
**Du kannst …**

1. den Bias-Variance Trade-off als zentrales Problem der Generalisierungsfähigkeit analysieren.
2. das Vanishing Gradient Problem in tiefen Netzen diagnostizieren und Gegenmaßnahmen (ReLU, Batch-Norm) bewerten.
3. die Vorteile von CNNs (Parameter-Effizienz durch Weight Sharing) gegenüber Fully-Connected-Netzen begründen.
4. Transformer-Modelle (Attention-Mechanismus) gegenüber RNNs hinsichtlich Parallelisierung und Langzeitabhängigkeiten bewerten.
5. die geometrische Wirkung der L1-Norm (Sparsity) gegenüber der L2-Norm (Shrinkage) herleiten.
6. die Irreführung durch Accuracy bei unbalancierten Klassen analysieren und PR-AUC als Alternative ableiten.
7. den Nutzen der Log-Likelihood gegenüber der einfachen Likelihood (numerische Stabilität) begründen.
8. die Implikationen des CAP-Theorems für die Architektur verteilter ML-Systeme ableiten.
9. den funktionalen Unterschied zwischen `iloc` (Position) und `loc` (Label) in Datenstrukturen herleiten.
10. die Rolle der Hesse-Matrix bei der Bestimmung von lokalen Minima gegenüber Sattelpunkten analysieren.
11. PCA als Verfahren zur Dimensionsreduktion unter Beibehaltung maximaler Varianz analysieren.
12. den Exploration-Exploitation Trade-off im Reinforcement Learning als Optimierungsproblem bewerten.
13. die Eignung von YOLO gegenüber Faster R-CNN für Echtzeit-Anwendungen abwägen.
14. den Einfluss der Feature-Skalierung auf die Distanzberechnung in k-NN und k-Means herleiten.
15. die Bedeutung von Erklärbarkeit (SHAP, LIME) für die Akzeptanz von „Black Box“-Modellen in regulierten Bereichen analysieren.
