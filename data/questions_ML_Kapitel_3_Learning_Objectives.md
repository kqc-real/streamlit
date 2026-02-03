# Übergeordnete Lernziele: Machine Learning: Kapitel 3

## **MNIST & Datenzugriff**
**Datenquellen korrekt laden und Formen sicher einordnen.**

Du kannst typische ML-Datensätze wie MNIST korrekt laden und die resultierenden Datenformen zuverlässig einordnen. Dadurch erkennst du schnell, welche Dimensionen für Modellierung und Feature-Engineering relevant sind.

---

## **Qualitätsmaße & Schwellenwerte**
**Klassifikationsmetriken passend wählen und interpretieren.**

Du kannst zentrale Metriken wie Präzision, Recall, FPR und PR-/ROC-Kurven zielgerichtet einsetzen und ihre Aussagekraft im Kontext von Imbalance einschätzen. So wählst du passende Evaluationsstrategien für unterschiedliche Problemstellungen.

---

## **Multiclass-Strategien in sklearn**
**Mehrklassen-Klassifikation in sklearn sicher einordnen.**

Du kannst OvR- und OvO-Strategien unterscheiden, Kennzahlen aus `decision_function` interpretieren und die Anzahl benötigter Modelle korrekt bestimmen. Damit behältst du den Überblick über die Modelllogik in Mehrklassen-Setups.

---

## **Fehleranalyse & Verbesserungen**
**Fehlerbilder sichtbar machen und gezielt verbessern.**

Du kannst Konfusionsmatrizen zweckmäßig normalisieren, Fehler stärker hervorheben und wirksame Maßnahmen zur Modellverbesserung ableiten. Das hilft dir, konkrete Schwächen systematisch zu adressieren.

---

## **Multilabel-Strategien & Bewertung**
**Mehrfach-Labels korrekt modellieren und bewerten.**

Du kannst Multilabel-Probleme von Multiclass unterscheiden, geeignete Metriken wählen und die Vorteile von ClassifierChains nutzen. So berücksichtigst du Label-Abhängigkeiten und realistische Evaluationslogiken.

---

## **Multioutput & Denoising**
**Mehrere Ausgaben pro Instanz sauber modellieren.**

Du kannst Multioutput-Szenarien wie Denoising-Aufgaben korrekt beschreiben und die Besonderheiten diskreter Zielwerte einordnen. Dadurch wählst du geeignete Modell- und Bewertungsstrategien.

---

# Detaillierte Lernziele

Im Kontext des Themas **Machine Learning: Kapitel 3** soll dir dieses Fragenset helfen, die folgenden detaillierten Lernziele zu erreichen:

### Reproduktion

**Du kannst …**

1. die Form des MNIST-Feature-Arrays bei `as_frame=False` angeben.
2. die `make_*`-Funktionen in `sklearn.datasets` benennen.
3. die Bedeutung von Recall als Anteil erkannter Positiver beschreiben.
4. den typischen Effekt einer höheren Entscheidungsschwelle wiedergeben.
5. die ROC-AUC eines Zufallsklassifikators nennen.
6. die Rolle von `classes_` für die Klassenreihenfolge beschreiben.

### Anwendung

**Du kannst …**

1. die Irreführung durch Accuracy bei unbalancierten Daten erkennen.
2. die Bedeutung von `cv=3` in `cross_val_score` bestimmen.
3. den fehlenden Term in der Präzisionsformel bestimmen.
4. die passende Methode für Entscheidungs-Scores auswählen.
5. erkennen, dass `precision_recall_curve` einen Zusatzpunkt für einen extremen Threshold nutzt.
6. die FPR als Anteil negativer Fälle bestimmen.
7. die Anzahl OvO-Klassifikatoren für N Klassen berechnen.
8. die Anzahl der OvR-Estimatoren in `estimators_` bestimmen.
9. die Anzahl der `decision_function`-Scores pro Instanz bestimmen.
10. das von `SGDClassifier` genutzte Multiclass-Verfahren auswählen.
11. die Normalisierung `normalize='pred'` der Konfusionsmatrix zuordnen.
12. den Zweck von `sample_weight` in der Fehleranalyse erkennen.
13. den Effekt von Data Augmentation auf die Generalisierung erkennen.
14. den Unterschied zwischen `macro` und `weighted` beim F1-Score zuordnen.
15. eine Multilabel-Aufgabe als Mehrfach-Label pro Instanz erkennen.
16. den Nutzen von ClassifierChain bei Label-Abhängigkeiten erkennen.
17. eine Multioutput-Klassifikation als mehrere Outputs pro Instanz bestimmen.
18. das Ziel `y_train_mod` im Denoising-Setup bestimmen.

### Strukturelle Analyse

**Du kannst …**

1. die Wahl der PR-Kurve bei seltenen Positiven begründen.
2. den Einfluss von StandardScaler auf die SGD-Optimierung analysieren.
3. die Wahl von `average='weighted'` bei ungleichen Labelhäufigkeiten begründen.
4. die Notwendigkeit von CV in ClassifierChains zur Leckagevermeidung begründen.
5. die Einordnung des Pixel-Targets als regressionsnah bewerten.
6. eine zielgerichtete Maßnahme gegen Verwechslungen mit '8' ableiten.
