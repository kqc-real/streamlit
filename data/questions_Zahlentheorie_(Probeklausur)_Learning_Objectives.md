Im Kontext des Themas **Zahlentheorie für Wirtschaftsinformatik** soll dir dieses Fragenset helfen, die folgenden Lernziele zu erreichen:

### Reproduktion
**Du kannst …**

1. die Eigenschaft der Teilbarkeit zweier ganzer Zahlen definieren und an einfachen Beispielen erläutern, dass eine Zahl eine andere genau dann teilt, wenn bei der Division kein Rest entsteht.
2. den Begriff der Restklasse modulo $n$ beschreiben und erklären, dass er die Menge aller ganzen Zahlen umfasst, die bei Division durch $n$ denselben Rest lassen.

### Anwendung
**Du kannst …**

1. Dezimalzahlen systematisch in die entsprechende Binärdarstellung umrechnen, indem du Zweierpotenzen identifizierst und die zugehörigen Bits setzt.
2. Dezimalzahlen in die entsprechende Hexadezimaldarstellung und zurück umrechnen und dabei die Stellenwerte im System zur Basis 16 sicher verwenden.
3. den Speicherbedarf von Zahlen abschätzen, indem du Hexadezimalziffern der passenden Anzahl an Bits (z.B. 4 Bit pro Hex-Stelle) zuordnest.

4. den größten gemeinsamen Teiler zweier ganzer Zahlen mithilfe von Teilermengen oder Primfaktorzerlegung bestimmen.
5. den Euklidischen Algorithmus zur effizienten Berechnung des ggT zweier ganzer Zahlen anwenden und seine Schrittfolge nachvollziehen.
6. die Aussage, dass es unendlich viele Primzahlen gibt, in Beispielen einordnen und ihre Bedeutung für Zahlentheorie und Kryptografie erläutern.

7. Modulo-Rechnungen wie $27 \bmod 6$ durch Division mit Rest berechnen und das Ergebnis als Rest interpretieren.
8. den erweiterten Euklidischen Algorithmus verwenden, um neben dem ggT auch Koeffizienten $x$ und $y$ zu bestimmen, so dass $ax + by = \mathrm{ggT}(a,b)$ gilt.
9. anhand des Kriteriums $\mathrm{ggT}(a,n) \mid b$ entscheiden, ob eine lineare Kongruenz $ax \equiv b \pmod n$ lösbar ist.

10. Aufgaben zu kryptografischen Hash-Funktionen bearbeiten, indem du Zweck und zentrale Eigenschaften (feste Ausgabelänge, Determinismus, Integritätsprüfung) korrekt beschreibst und anwendest.
11. typische Szenarien von Hash-Kollisionen einordnen und erklären, weshalb Kollisionsresistenz für Integrität und Sicherheit in Anwendungen essenziell ist.

12. die symmetrische Differenz $A \Delta B$ zweier Mengen bestimmen und sie als mengenlogische Umsetzung des exklusiven Oder (XOR) interpretieren.
13. zu einer Implikation $A \to B$ die logisch äquivalente Kontraposition $\neg B \to \neg A$ bilden und in Argumentationen gezielt einsetzen.

14. rekursive Funktionen so entwerfen, dass ein klarer Basisfall (Abbruchbedingung) die Rekursionskette zuverlässig beendet.
15. Beweise mit vollständiger Induktion strukturieren, indem du Induktionsanfang, Induktionsvoraussetzung und Induktionsschritt korrekt formulierst und verwendest.

16. an den Körperaxiomen prüfen, ob eine gegebene algebraische Struktur ein Körper ist, insbesondere die Existenz multiplikativer Inversen für alle Elemente $a \neq 0$ kontrollieren.
17. an Beispielen herausarbeiten, warum $(\mathbb{Z}, +, \cdot)$ nur ein Ring, aber kein Körper ist, und den Unterschied zwischen Ring und Körper verständlich darstellen.
18. die Rolle endlicher Körper (z.B. $GF(2^8)$) in Fehlerkorrekturcodes und Verschlüsselungsverfahren nachvollziehen und die Vorteile eines festen, endlichen Wertebereichs einordnen.

19. das Prinzip asymmetrischer Verschlüsselung erläutern, bei dem ein öffentlicher und ein privater Schlüssel unterschiedliche Rollen beim Ver- und Entschlüsseln übernehmen.
20. mithilfe der Primfaktorzerlegung begründen, warum die leichte Berechnung von $N = p \cdot q$ und die schwierige Umkehr (Faktorisierung) die Sicherheitsbasis des RSA-Verfahrens bildet.
21. den Diffie–Hellman-Schlüsselaustausch beschreiben und die Bedeutung des schwer lösbaren diskreten Logarithmusproblems für die Sicherheit des Verfahrens einordnen.

### Strukturelle Analyse
**Du kannst …**

1. den Unterschied zwischen Gleichheit $=$ und Kongruenz $\equiv$ analysieren und anhand von Beispielen wie $14 \equiv 2 \pmod{12}$ erklären, warum kongruente Zahlen nicht identisch sein müssen.
2. herleiten, warum ein multiplikatives Inverses von $a$ modulo $n$ nur existiert, wenn $\mathrm{ggT}(a,n) = 1$ gilt, und diesen Zusammenhang mithilfe des Lemmas von Bézout begründen.
3. scheinbar korrekte Induktionsbeweise (z.B. „alle Autos haben dieselbe Farbe“) kritisch untersuchen und den logischen Fehler, insbesondere beim Übergang von $n=1$ auf $n=2$, präzise identifizieren.
4. analysieren, warum Hash-Kollisionen bei digitalen Signaturen ein Sicherheitsrisiko darstellen, indem du beschreibst, wie eine gültige Signatur von einem harmlosen auf ein manipuliertes Dokument übertragen werden kann.
5. aus der Größe des RSA-Moduls $N = p \cdot q$ sicherheitstechnische Schlüsse ziehen und begründen, warum zu kleine Schlüssellängen eine sofortige Faktorisierung und damit unsichere Systeme ermöglichen.
6. das One-Time-Pad hinsichtlich seiner informationstheoretischen Perfektsicherheit und seiner praktischen Unbrauchbarkeit analysieren, insbesondere im Hinblick auf Schlüsselgenerierung und -verteilung.
7. Kerckhoffs’ Prinzip auf reale Kryptosysteme anwenden und begründen, warum „Security by Obscurity“ als unzureichend gilt und Sicherheit primär an der Geheimhaltung des Schlüssels statt des Algorithmus festgemacht werden muss.
