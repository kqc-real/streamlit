# Übergeordnete Lernziele: Machine Learning: Kapitel 2

## **ML-Projekt & Reproduzierbarkeit**
**Projektphasen und Reproduzierbarkeit sicher einordnen.**

Du kannst typische ML-Projektphasen von Problemdefinition bis Betrieb benennen und weißt, wie Reproduzierbarkeit durch feste Zufallsseeds in Experimenten hergestellt wird.

---

## **Datenaufbereitung & Datenqualität**
**Daten sauber vorbereiten und typische Fehler vermeiden.**

Du kannst Sampling-Strategien begründen, fehlende Werte geeignet imputieren und den Einfluss von Datenlecks durch falsche Prozessreihenfolgen erkennen.

---

## **Feature Engineering & Kodierung**
**Merkmale sinnvoll transformieren und kodieren.**

Du kannst geeignete Kodierungen für kategoriale Daten wählen, Transformationen wie Log-Scaling begründen und Risiken wie Leakage beim Target Encoding erkennen.

---

## **Pipelines & Prozesslogik**
**Pipelines korrekt aufbauen und integrieren.**

Du kannst sinnvolle Reihenfolgen in Preprocessing-Pipelines wählen, ColumnTransformer gezielt einsetzen und eigene Transformer korrekt einbinden.

---

## **Modelle & Ensembles**
**Modelleigenschaften und Ensemblevorteile erklären.**

Du kannst Merkmalsbedeutungen in Random Forests interpretieren und Ensemble-Unterschiede wie Random Forest vs. Gradient Boosting einordnen.

---

## **Modelltraining & Optimierung**
**Trainingsstrategie und Tuning sauber begründen.**

Du kannst Cross-Validation nutzen, Hyperparameter-Tuning korrekt strukturieren und Über- bzw. Unterfitting aus Fehlerkurven ableiten.

---

## **Evaluierung & Metriken**
**Evaluierung korrekt und problembezogen durchführen.**

Du kannst geeignete Metriken für Regression und Klassifikation auswählen, die Grenzen von Accuracy bei Imbalance erklären und geeignete Kennzahlen für medizinische Screenings priorisieren.

---

# Detaillierte Lernziele

Im Kontext des Themas **Machine Learning: Kapitel 2** soll dir dieses Fragenset helfen, die folgenden detaillierten Lernziele zu erreichen:

### Reproduktion

**Du kannst …**

1. die typischen Phasen eines ML-Projekts benennen.
2. beschreiben, was der RMSE über Vorhersagefehler ausdrückt.
3. die Funktion von `fit()` in einer sklearn-Pipeline benennen.

### Anwendung

**Du kannst …**

1. stratifiziertes Sampling gegenüber Zufallssampling auswählen.
2. begründen, warum der Testdatensatz vor Modellauswahl tabu ist.
3. eine geeignete Imputation für rechtsschiefe Merkmale auswählen.
4. OneHotEncoder gegenüber OrdinalEncoder passend einsetzen.
5. StandardScaler gegenüber MinMaxScaler situationsgerecht wählen.
6. eine sinnvolle Reihenfolge für numerisches Preprocessing festlegen.
7. ColumnTransformer für gemischte Datentypen anwenden.
8. den Effekt von `random_state` auf Reproduzierbarkeit anwenden.
9. `feature_importances_` im Random Forest interpretieren.
10. eine Korrelationsmatrix zur Merkmalsauswahl nutzen.
11. fehlende Kategorien mit einer geeigneten Strategie auffüllen.
12. Log-Transformation für stark schiefe Umsatz-Features einsetzen.
13. eine eigene Funktion als Pipeline-Transformer einbinden.
14. den Nutzen von k-facher Kreuzvalidierung begründen.
15. das `param_grid` für GridSearchCV korrekt definieren.
16. Overfitting anhand von Trainings- und Validierungsfehlern erkennen.
17. eine robuste Metrik für Regression mit Ausreißern auswählen.
18. die Robustheit von Random Forests gegenüber einzelnen Bäumen begründen.

### Strukturelle Analyse

**Du kannst …**

1. die Fehlerwirkung der Reihenfolge „Skalieren vor Imputieren“ begründen.
2. die Irreführung durch Accuracy bei starker Klassendissbalance erklären.
3. Unterfitting anhand von Lernkurven herleiten.
4. Data Leakage durch Feature Selection vor dem Split begründen.
5. Leakage-Risiken beim Target Encoding ohne Regularisierung bewerten.
6. die höhere Empfindlichkeit von Gradient Boosting gegenüber Random Forests begründen.
7. die geeignete Metrik für medizinische Screenings herleiten.
8. die Notwendigkeit von Nested Cross-Validation bei Tuning begründen.
9. die Auswirkung fehlender Skalierung vor PCA herleiten.
