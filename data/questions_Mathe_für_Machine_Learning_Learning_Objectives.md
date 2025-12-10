Im Kontext des Themas **Mathematik für Machine Learning** soll dir dieses Fragenset helfen, die folgenden Lernziele zu erreichen:

### Reproduktion
**Du kannst …**

1. für Matrizen $A \in \mathbb{R}^{m \times n}$ und $B \in \mathbb{R}^{n \times k}$ die Dimension des Produkts $C = A \cdot B$ korrekt angeben.
2. beschreiben, was der Gradient $\nabla f(x)$ einer skalaren Funktion $f : \mathbb{R}^n \to \mathbb{R}$ geometrisch ausdrückt und in welche Richtung er zeigt.
3. die zentrale Eigenschaft des Matrixrangs als maximale Anzahl linear unabhängiger Zeilen- bzw. Spaltenvektoren einer Matrix erläutern.
4. erklären, dass beim Satz von Bayes die bedingte Wahrscheinlichkeit $P(A \mid B)$ mithilfe von $P(B \mid A)$, $P(A)$ und $P(B)$ berechnet wird.
5. die L2-Norm eines Vektors als euklidische Länge interpretieren und ihre Berechnung mit $\sqrt{\sum_i x_i^2}$ nachvollziehen.
6. die Spur einer Matrix als Summe der Diagonaleinträge $ \operatorname{tr}(A) = \sum_i A_{ii} $ definieren und ihren Zusammenhang zur Summe der Eigenwerte wiedergeben.
7. beschreiben, dass bei Unabhängigkeit zweier Zufallsvariablen $X$ und $Y$ ihre Kovarianz $\operatorname{Cov}(X, Y)$ gleich $0$ ist.
8. erläutern, dass eine quadratische Matrix genau dann invertierbar ist, wenn ihre Determinante $\det(A) \neq 0$ ist.
9. die Eigenwertgleichung $A v = \lambda v$ als Charakterisierung von Eigenvektoren und Eigenwerten einer Matrix angeben.
10. wiedergeben, dass in NumPy die Matrixinverse mit `np.linalg.inv(A)` berechnet wird und elementweise Operationen wie `1 / A` dafür ungeeignet sind.

### Anwendung
**Du kannst …**

1. die Eigenschaft der positiven Definitheit nutzen, um zu entscheiden, ob eine symmetrische Matrix $A$ die quadratische Form $x^\top A x$ streng konvex macht.
2. den Gradienten einer Funktion $f(x, y) = x^2 + 3y$ bestimmen, indem du die partiellen Ableitungen zu einem Vektor $\nabla f = (2x, 3)^\top$ zusammenfasst.
3. die Singulärwertzerlegung $A = U \Sigma V^\top$ zur Dimensionsreduktion einsetzen, etwa indem du nur die größten Singulärwerte in $\Sigma$ beibehältst.
4. aus dem Skalarprodukt $a^\top b = 0$ folgern, dass zwei Vektoren $a, b \in \mathbb{R}^n$ orthogonal zueinander stehen.
5. einfache Matrix-Vektor-Produkte berechnen, indem du Zeilen einer Matrix mit einem Spaltenvektor multiplizierst und so z.B. $(4, 3)^\top$ als Ergebnis erhältst.
6. den Erwartungswert einer diskreten Zufallsvariablen in NumPy durch den gewichteten Mittelwert $E[X] = \sum_i x_i p_i$ mit `np.sum(x * p)` berechnen.
7. in NumPy mit `A.dot(B)` (oder `A @ B`) eine Matrixmultiplikation durchführen und sie von elementweisen Produkten unterscheiden.
8. die Konvexitätsungleichung
   $$
   f(\lambda x + (1-\lambda)y) \le \lambda f(x) + (1-\lambda)f(y)
   $$
   anwenden und geometrisch als „Graph liegt unter der Verbindungsgeraden“ interpretieren.
9. Maximum-Likelihood-Estimation (MLE) verwenden, um Parameter $\theta$ so zu bestimmen, dass die beobachteten Daten unter $P(X \mid \theta)$ möglichst wahrscheinlich sind.
10. die Kettenregel auf verschachtelte Funktionen $f(x) = g(h(x))$ anwenden und die Ableitung als $f'(x) = g'(h(x)) \cdot h'(x)$ formulieren.
11. die Taylor-Approximation erster Ordnung $f(x) \approx f(a) + f'(a)(x-a)$ als lokale Linearisierung einer Funktion nutzen.
12. die Kovarianzmatrix zentrierter Daten $X \in \mathbb{R}^{N \times D}$ über $\frac{1}{N-1} X^\top X$ berechnen und als Maß für lineare Zusammenhänge zwischen Features interpretieren.
13. bei einem Nebenbedingungenproblem die Lagrange-Funktion $L(x,\lambda) = f(x) - \lambda g(x)$ aufstellen, um Extrema unter der Bedingung $g(x) = 0$ zu bestimmen.
14. in einem neuronalen Layer $y = \sigma(Wx + b)$ aus der Neuronenzahl $k$ die passende Dimension des Bias-Vektors $b \in \mathbb{R}^k$ herleiten.

### Strukturelle Analyse
**Du kannst …**

1. aus der Bedingung $\nabla f(x^\ast) = 0$ und einer positiv definiten Hesse-Matrix $H_f(x^\ast)$ folgern, dass an der Stelle $x^\ast$ ein lokales Minimum vorliegt.
2. begründen, warum die Verwendung der Log-Likelihood $\ln L(\theta)$ statt der Likelihood $L(\theta)$ numerisch stabiler ist und die Ableitung als Summe von Log-Wahrscheinlichkeiten vereinfacht.
3. analysieren, weshalb die L1-Regularisierung mit der Norm $\lVert w \rVert_1$ typischerweise zu sparsamen Parametervektoren mit vielen Einträgen $w_i = 0$ führt, während L2-Regularisierung nur die Größe der Parameter begrenzt.
4. erklären, warum der Nullvektor $v = 0$ aus der Definition von Eigenvektoren ausgeschlossen wird, da $A0 = \lambda 0$ für jedes $\lambda$ gilt und somit keine Richtungsinformation enthält.
5. herleiten, wie aus einer zentrierten Datenmatrix $X$ über das Produkt $\frac{1}{N-1} X^\top X$ eine Kovarianzmatrix entsteht und wie dies die Grundlage von Verfahren wie PCA bildet.
6. analysieren, weshalb die Sigmoid-Funktion $\sigma(x) = \frac{1}{1 + e^{-x}}$ für große Beträge von $x$ zu sehr kleinen Ableitungen $\sigma'(x)$ führt und damit das Vanishing-Gradient-Problem in tiefen neuronalen Netzen verursacht.
