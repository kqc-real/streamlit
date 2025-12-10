Im Kontext des Themas **Python für Data Analysis (Komplettset)** soll dir dieses Fragenset helfen, die folgenden Lernziele zu erreichen:

### Reproduktion

**Du kannst …**

1. den fundamentalen Unterschied zwischen statischer Typisierung in Java und dynamischer Typisierung in Python beschreiben.
2. die Einrückung (Indentation) als Methode zur Strukturierung von Code-Blöcken identifizieren.
3. NumPy als die Standardbibliothek für numerische Berechnungen und Arrays in Python benennen.
4. die Funktion `df.describe()` nutzen, um eine statistische Zusammenfassung numerischer Spalten zu erhalten.
5. die Syntax zur Selektion einzelner Spalten in einem Pandas DataFrame wiedergeben.
6. die Methode `dropna()` identifizieren, um Zeilen mit fehlenden Werten aus einem Datensatz zu entfernen.
7. den Befehl `pd.read_csv()` zum Importieren von CSV-Dateien nennen.
8. die Funktion `np.arange()` zur Erstellung von Zahlenreihen mit definierter Schrittweite beschreiben.
9. die Funktion `pd.to_datetime()` zur Konvertierung von Strings in Zeitstempel benennen.
10. Seaborn als Bibliothek für statistische Visualisierungen identifizieren, die auf Matplotlib aufbaut.
11. das Python-Dictionary als Äquivalent zur Java HashMap einordnen.
12. die Methode `copy()` nennen, um eine unabhängige Kopie eines DataFrames zu erstellen.
13. die Unveränderlichkeit (Immutability) von Tupeln im Vergleich zu Listen beschreiben.
14. die Konvention für Modul-Aliasse (wie `import matplotlib.pyplot as plt`) wiedergeben.
15. den Zugriff auf das letzte Element einer Liste mittels negativer Indizierung (`-1`) identifizieren.
16. das Verhalten von Slicing-Operationen bei Listen und Strings beschreiben.
17. erkennen, dass Elemente eines Tupels nach der Erstellung nicht mehr verändert werden können.
18. die Syntax von f-Strings zur Formatierung und Interpolation von Variablen in Strings identifizieren.
19. Fehler erkennen, die durch falsche Einrückung in Schleifen verursacht werden.
20. die korrekte Import-Syntax für Klassen aus einem Paket beschreiben.
21. die Methode `.items()` benennen, um über Schlüssel und Werte eines Dictionaries zu iterieren.
22. die Bedeutung des Parameters `self` in Instanzmethoden von Klassen wiedergeben.
23. die Methode `dropna()` zur Bereinigung von Datensätzen mit `NaN`-Werten benennen.
24. die Methode `reshape()` identifizieren, um die Dimensionen eines NumPy-Arrays zu ändern.
25. das Schlüsselwort `elif` zur Definition mehrfacher Bedingungen in Kontrollstrukturen nennen.
26. das Attribut `.shape` verwenden, um die Dimensionen eines DataFrames abzufragen.
27. das Schlüsselwort `pass` als Platzhalter für leere Codeblöcke identifizieren.
28. `None` als das Python-Äquivalent zum `null`-Wert in Java benennen.
29. das Attribut `.columns` nutzen, um auf die Spaltennamen eines DataFrames zuzugreifen.
30. die Built-in Funktion `len()` verwenden, um die Länge von Sequenzen global zu ermitteln.

### Anwendung

**Du kannst …**

1. List Comprehensions anwenden, um Berechnungen auf Iterables kompakt durchzuführen.
2. die Vektorisierung in NumPy nutzen, um Rechenoperationen auf Arrays ohne explizite Schleifen durchzuführen.
3. den positionsbasierten Zugriff mittels `iloc` und Slicing auf DataFrames anwenden.
4. Boolean Indexing (Masking) einsetzen, um Daten basierend auf logischen Bedingungen zu filtern.
5. Daten mittels `groupby` gruppieren und Aggregationsfunktionen wie `sum()` darauf anwenden.
6. die Komponenten eines Boxplots, insbesondere den Interquartilsabstand (IQR), korrekt interpretieren.
7. die Methode `apply()` mit Lambda-Funktionen als Alternative zu Iterationen einsetzen.
8. einen Left Join durchführen, um Daten aus zwei Tabellen unter Beibehaltung aller Schlüssel der linken Tabelle zu verknüpfen.
9. die Achsen-Parameter (`axis=0` vs. `axis=1`) bei DataFrame-Operationen korrekt anwenden.
10. DataFrames vertikal mittels `pd.concat()` zusammenfügen.
11. Performanzprobleme durch die Verwendung von `iterrows()` erkennen und vektorisierte Alternativen bevorzugen.
12. `pivot_table` verwenden, um Daten zu aggregieren und in ein breites Format umzuwandeln.
13. den `.str`-Accessor nutzen, um String-Operationen auf Pandas-Series vektorisiert anzuwenden.
14. die Korrelation in Scatterplots anhand der Steigung und Streuung der Punktewolke interpretieren.
15. Sets verwenden, um Duplikate aus einer Liste effizient zu entfernen.
16. Method Chaining anwenden, um Datenbereinigung und Typkonvertierung in einem Schritt durchzuführen.
17. Dictionaries oder `Counter` nutzen, um Häufigkeiten von Elementen zu zählen.
18. bitweise Operatoren (`&`) anstelle von logischen Operatoren (`and`) für elementweise Vergleiche in Pandas verwenden.
19. Filterbedingungen innerhalb einer List Comprehension implementieren.
20. die Methode `.get()` verwenden, um sicher auf Dictionary-Werte zuzugreifen und KeyErrors zu vermeiden.
21. Boolesche Masken nutzen, um Werte in einem NumPy-Array bedingt zu modifizieren.
22. Fehler beim Broadcasting von NumPy-Arrays aufgrund inkompatibler Dimensionen identifizieren.
23. das Scoping-Verhalten von lokalen Variablen in Funktionen vorhersagen.
24. den Unterschied zwischen In-Place-Sortierung (`sort()`) und der Erstellung einer neuen sortierten Liste (`sorted()`) anwenden.
25. den `else`-Block in einer `try-except`-Struktur für Code nutzen, der nur bei Erfolg ausgeführt werden soll.
26. das Rückgabeobjekt einer `groupby`-Operation als Zwischenschritt zur Aggregation verstehen.
27. Tuple Unpacking anwenden, um Werte aus Sequenzen Variablen zuzuweisen.
28. die Syntax einer List Comprehension zur Transformation von Listen korrekt aufbauen.
29. das `with`-Statement als Context Manager für sicheres Datei-Handling einsetzen.
30. eine Lambda-Funktion definieren, um komplexe Datenstrukturen nach einem spezifischen Element zu sortieren.
31. den Befehl `plt.show()` korrekt platzieren, um Plots in Skripten sichtbar zu machen.
32. den Operator `is` zur Prüfung auf Objekt-Identität im Gegensatz zur Wertegleichheit anwenden.
33. das `del`-Statement nutzen, um Elemente aus Datenstrukturen oder Variablen aus dem Speicher zu entfernen.
34. `assert`-Statements einsetzen, um Annahmen im Code zu validieren und Fehler frühzeitig abzufangen.
35. den `.T`-Accessor verwenden, um DataFrames zu transponieren.

### Strukturelle Analyse

**Du kannst …**

1. das Verhalten von Views und Copies bei Pandas-Zuweisungen analysieren, um ungewollte Datenänderungen zu vermeiden.
2. den Speichervorteil des Datentyps `category` bei Strings mit geringer Kardinalität begründen.
3. die Robustheit des Medians gegenüber dem Mittelwert bei Ausreißern analysieren.
4. den Zusammenhang zwischen Mittelwert und Median bei linksschiefen Verteilungen herleiten.
5. die Problematik der Zwangskonvertierung von Integers zu Floats bei Vorhandensein von `NaN`-Werten analysieren.
6. die Fallstricke veränderlicher Default-Argumente (Mutable Defaults) in Funktionen untersuchen und vermeiden.
7. Overfitting anhand der Diskrepanz zwischen Trainings- und Testgenauigkeit diagnostizieren.
8. die Rolle von `__init__` im Vergleich zu Java-Konstruktoren im Objekt-Lebenszyklus einordnen.
9. den Programmablauf bei der Modifikation von Listen, die als Default-Parameter dienen, nachvollziehen.
10. die Ursache der `SettingWithCopyWarning` analysieren und korrekte Zuweisungsstrategien wählen.
11. die Ungenauigkeiten bei Gleitkomma-Berechnungen nach IEEE 754 analysieren und Vergleiche korrekt durchführen.
12. das Referenzverhalten bei der Zuweisung von Listen analysieren, um zwischen flachen Kopien und Referenzen zu unterscheiden.
13. die Achsen-Logik bei der Anwendung von benutzerdefinierten Funktionen mittels `apply` herleiten und korrigieren.
14. die Notwendigkeit und Syntax des Aufrufs von Eltern-Initialisierern mittels `super()` in Vererbungshierarchien begründen.
15. die Effizienz und Lesbarkeit des `in`-Operators für Mitgliedschaftstests bewerten.