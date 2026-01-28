# Übergeordnete Lernziele: Machine-Learning: Kapitel 2

## ML-Projektzyklus & Methodik
**Den gesamten ML-Lebenszyklus von der Problemdefinition bis zum Deployment strukturieren und methodisch absichern.**

Du lernst, die Phasen eines ML-Projekts logisch zu gliedern und entscheidende Weichenstellungen – wie die Trennung von Trainings- und Testdaten oder die Wahl der richtigen Cross-Validation-Strategie – vorzunehmen, um reproduzierbare und generalisierbare Ergebnisse zu erzielen.

## Datenaufbereitung & Pipeline-Design
**Robuste Preprocessing-Pipelines für heterogene Daten (numerisch/kategorisch) entwerfen und implementieren.**

Du entwickelst die Kompetenz, Rohdaten durch Imputation, Skalierung und Encoding (OneHot, Ordinal) in modellgerechte Formate zu überführen. Dabei lernst du, komplexe Abläufe fehlerfrei in `scikit-learn`-Pipelines und ColumnTransformern zu kapseln, um Data Leakage zu vermeiden.

## Feature Engineering & Selection
**Merkmale gezielt transformieren und selektieren, um die Modellleistung zu maximieren.**

Du verstehst, wie du durch Log-Transformationen, Korrelationsanalysen und PCA die Informationsdichte in deinen Daten erhöhst. Zudem lernst du, kritische Fehler wie Leakage beim Target Encoding oder der Feature Selection zu identifizieren und zu verhindern.

## Modelltraining & Optimierung
**Lernalgorithmen effektiv trainieren, tunen und typische Fehler wie Overfitting diagnostizieren.**

Du wirst befähigt, Modelle (von Regression bis Random Forests) zu konfigurieren, Hyperparameter mittels GridSearch zu optimieren und anhand von Lernkurven zwischen Bias (Underfitting) und Variance (Overfitting) zu unterscheiden.

## Evaluierung & Metriken
**Modellgüte situationsabhängig bewerten und Metriken an Business-Zielen ausrichten.**

Du lernst, über einfache Accuracy hinauszuwachsen und Metriken wie RMSE, MAE, Precision, Recall oder F1-Score gezielt einzusetzen – insbesondere in herausfordernden Szenarien wie starker Klassendissbalance oder medizinischen Screenings.

---

# Detaillierte Lernziele

Im Kontext des Themas **Machine-Learning: Kapitel 2** soll dir dieses Fragenset helfen, die folgenden detaillierten Lernziele zu erreichen:

### Reproduktion

**Du kannst …**

1. die Hauptphasen eines Machine-Learning-Projekts von der Definition bis zum Betrieb wiedergeben.
2. den Zweck der `fit()`-Methode innerhalb einer `sklearn`-Pipeline benennen.
3. die Bedeutung des RMSE im Hinblick auf die Bestrafung großer Vorhersagefehler beschreiben.

### Anwendung

**Du kannst …**

1. stratifiziertes Sampling auswählen, um repräsentative Verteilungen in Train/Test-Splits zu sichern.
2. Data-Snooping-Risiken durch strikte Isolation des Testdatensatzes vor der Modellauswahl erkennen.
3. den `random_state`-Parameter zur Sicherstellung der Reproduzierbarkeit von Experimenten einsetzen.
4. die Median-Imputation für rechtsschiefe numerische Merkmale mit Ausreißern auswählen.
5. die Imputation fehlender kategorischer Werte mittels häufigstem Wert oder Platzhalter durchführen.
6. das passende Encoding (OneHot vs. Ordinal) basierend auf dem Vorhandensein einer natürlichen Ordnung bestimmen.
7. den StandardScaler gegenüber dem MinMaxScaler bei ausreißerbehafteten Daten auswählen.
8. eine Log-Transformation zur Stabilisierung der Varianz bei rechtsschiefen Verteilungen anwenden.
9. eine Korrelationsmatrix zur Identifikation linearer Zusammenhänge zwischen Merkmalen einsetzen.
10. die korrekte Reihenfolge von Imputation, Transformation und Skalierung in einer Pipeline bestimmen.
11. den `ColumnTransformer` für die parallele Verarbeitung gemischter Datentypen einsetzen.
12. den `FunctionTransformer` zur Einbindung eigener Python-Funktionen in Pipelines einsetzen.
13. das `param_grid`-Dictionary für eine systematische Hyperparameter-Suche (GridSearchCV) bestimmen.
14. k-fache Kreuzvalidierung zur robusten Qualitätsschätzung bei begrenzten Daten einsetzen.
15. Overfitting anhand der Differenz zwischen Trainings- und Validierungsfehlern erkennen.
16. die Bedeutung von `feature_importances_` zur Interpretation von Random Forests erkennen.
17. die Robustheit von Random Forests gegenüber einzelnen Entscheidungsbäumen durch Ensemble-Mittelung erkennen.
18. den MAE als Metrik bei Regressionsproblemen mit zu erwartenden Ausreißern auswählen.

### Strukturelle Analyse

**Du kannst …**

1. die Fehlerursache einer falschen Reihenfolge (Skalieren vor Imputieren) analysieren.
2. die Notwendigkeit der Feature Selection innerhalb des Cross-Validation-Loops begründen.
3. das Data-Leakage-Risiko bei unreguliertem Target Encoding analysieren.
4. die Auswirkungen fehlender Skalierung auf die Komponenten einer PCA herleiten.
5. High Bias (Underfitting) anhand von stagnierenden Lernkurven diagnostizieren.
6. die Rauschempfindlichkeit von Gradient Boosting im Vergleich zu Random Forests analysieren.
7. den Einsatz von Nested Cross-Validation zur fairen Performance-Schätzung bei Hyperparameter-Tuning begründen.
8. die Irreführung durch die Accuracy-Metrik bei starker Klassendissbalance bewerten.
9. die Priorisierung von Recall (Sensitivität) für medizinische Screening-Szenarien herleiten.
