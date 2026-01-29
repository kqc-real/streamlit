# Übergeordnete Lernziele: Skalarprodukt, Orthogonalitaet & QR-Zerlegung

## **Skalarprodukt, Normen & Winkel**
**Skalarprodukt, Norm und Winkelbezug sicher einordnen.**

Du kannst das Skalarprodukt als Mass fuer Ausrichtung verstehen, die euklidische Norm korrekt definieren und zentrale Winkelbeziehungen wie Kosinusformel, Cauchy-Schwarz und Dreiecksungleichung anwenden. Damit kannst du geometrische Aussagen im $\mathbb{R}^n$ sicher einordnen.

---

## **Orthogonalitaet & Projektionen**
**Orthogonale Projektionen und Projektoren beschreiben.**

Du kannst den Restvektor bei Projektionen interpretieren, Projektoren ueber ihre Gleichungen erkennen und Projektionen auf Unterraeume berechnen. Das hilft dir, Geometrie und Fehlerterme in LS-Problemen zu verstehen.

---

## **Orthonormalbasen & Gram-Schmidt**
**ONB-Eigenschaften und Gram-Schmidt-Verfahren einordnen.**

Du kannst Eigenschaften von Orthonormalbasen nennen, das klassische und modifizierte Gram-Schmidt-Verfahren unterscheiden und die Voraussetzungen fuer eine ONB beurteilen.

---

## **QR-Zerlegung: Grundlagen & Eigenschaften**
**QR-Struktur und Eigenschaften von Q und R bestimmen.**

Du kannst die Rolle von $Q$ und $R$ in $A=QR$ erklaeren, die Form von $R$ begruenden und Eigenschaften des duenneren QR erkennen. Damit verstehst du, wie QR die Struktur von Matrizen bewahrt.

---

## **QR-Konstruktion & Numerik**
**Householder- und Givens-Verfahren zielgerichtet einordnen.**

Du kannst den Effekt von Householder-Reflexionen und Givens-Rotationen beschreiben und numerische Stabilitaetsvorteile gegenueber klassischen Verfahren erkennen.

---

## **Least Squares mit QR**
**LS-Probleme stabil ueber QR loesen.**

Du kannst die QR-Schritte fuer Least Squares korrekt anwenden, Bedingungen fuer eindeutige Loesungen erkennen und die Stabilitaet gegenueber Normalengleichungen begruenden.

---

# Detaillierte Lernziele

Im Kontext des Themas **Skalarprodukt, Orthogonalitaet & QR-Zerlegung** soll dir dieses Fragenset helfen, die folgenden detaillierten Lernziele zu erreichen:

### Reproduktion

**Du kannst …**

1. beschreiben, was das Skalarprodukt ueber die Ausrichtung zweier Vektoren misst.
2. die Definition der euklidischen Norm $\|x\|=\sqrt{\langle x,x\rangle}$ angeben.
3. nennen, dass Orthogonalitaet durch $\langle x,y\rangle=0$ charakterisiert ist.
4. identifizieren, dass der Restvektor $r=x-Px$ orthogonal zum Unterraum ist.
5. beschreiben, dass eine ONB aus paarweise orthogonalen Einheitsvektoren besteht.
6. benennen, dass klassisches Gram-Schmidt numerisch instabiler ist.
7. nennen, dass Gram-Schmidt eine ONB liefert, wenn die Eingangsvektoren linear unabhaengig sind.
8. benennen, dass $Q^\top Q=I$ orthonormale Spalten bedeutet.
9. angeben, dass $R$ in $A=QR$ eine obere Dreiecksmatrix ist.
10. benennen, dass $Q$ eine orthogonale Transformation darstellt.
11. angeben, dass beim duenneren QR $Q\in\mathbb{R}^{m\times n}$ orthonormale Spalten hat.
12. beschreiben, dass orthogonale Transformationen Normen und Winkel erhalten.
13. beschreiben, dass LS via QR ueber $A=QR$ und $Rx=Q^\top b$ geloest wird.
14. identifizieren, dass das Residuum zur LS-Loesung orthogonal zum Spaltenraum von $A$ ist.
15. identifizieren, dass der Kosinuswinkel bei Skalierung von $x$ oder $y$ invariant ist.
16. nennen, dass $|\langle x,y\rangle|\le \|x\|\,\|y\|$ gilt.
17. angeben, dass die Dreiecksungleichung $\|x+y\|\le \|x\|+\|y\|$ gilt.
18. benennen, dass Givens-Rotationen Eintraege durch planare Rotation eliminieren.

### Anwendung

**Du kannst …**

1. bestimmen, dass ein orthogonaler Projektor durch $P^2=P$ und $P^\top=P$ charakterisiert ist.
2. die Projektion auf $\operatorname{span}\{u\}$ fuer einen Einheitsvektor $u$ bestimmen.
3. die Projektionsformel $\operatorname{proj}_U(x)=\sum_i\langle x,u_i\rangle u_i$ anwenden.
4. anwenden, dass $P=UU^\top$ eine orthogonale Projektion liefert.
5. die Projektion fuer gegebene Vektoren anhand von Skalarprodukt und Norm bestimmen.
6. bestimmen, dass $x-Px$ orthogonal zu $U$ ist.
7. das Skalarprodukt gegebener Vektoren berechnen.
8. die richtige Aussage zur Kosinus-Aehnlichkeit in Anwendungen auswaehlen.
9. erkennen, dass MGS gegenueber CGS numerisch stabiler ist.
10. die Reihenfolge des klassischen Gram-Schmidt-Verfahrens korrekt anwenden.
11. bestimmen, dass bei vollem Spaltenrang die Diagonale von $R$ nicht null ist.
12. $R$ aus $Q$ und $A$ als $R=Q^\top A$ bestimmen.
13. fuer $m>n$ die Eigenschaft des duenneren $Q$ korrekt zuordnen.
14. erkennen, dass Householder-Reflexionen eine ganze Unterspalte in einem Schritt nullen.
15. die Schritte fuer Least Squares via QR korrekt anordnen.
16. eine typische Fehlerquelle bei GS/QR identifizieren.
17. $Rx=y$ per Rueckwaertseinsetzen korrekt loesen.

### Strukturelle Analyse

**Du kannst …**

1. begruenden, warum QR gegenueber Normalengleichungen numerisch stabiler ist.
2. begruenden, welche Bedingung eine eindeutige LS-Loesung garantiert.
3. bewerten, welche QR-Variante numerisch stabiler ist.
4. begruenden, warum orthogonale Transformationen bei schlecht konditionierten Spalten vorteilhaft sind.
