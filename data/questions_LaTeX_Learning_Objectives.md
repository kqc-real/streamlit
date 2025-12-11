Im Kontext des Themas **LaTeX für wissenschaftliches Schreiben** soll dir dieses Fragenset helfen, die folgenden Lernziele zu erreichen:

### Reproduktion
**Du kannst …**

1. die grundlegende Dokumentenklasse mit `\documentclass{...}` definieren und ihre Rolle in der Präambel eines LaTeX-Dokuments beschreiben.
2. die Dokumentenumgebung zwischen `\begin{document}` und `\end{document}` als Bereich für den sichtbaren Inhalt des Dokuments erläutern.
3. das Kommentarzeichen `%` als Mittel zur Auskommentierung von Quelltextzeilen identifizieren und seine Wirkung auf die Kompilierung wiedergeben.
4. den Befehl `\\` als erzwungenen Zeilenumbruch innerhalb eines Absatzes beschreiben und ihn von der Erzeugung eines neuen Absatzes unterscheiden.
5. den Befehl `\textbf{...}` als Standard zur Erzeugung von fettem Text im Fließtext benennen.
6. das Paket `graphicx` als Voraussetzung für den Befehl `\includegraphics` zur Einbindung externer Grafiken benennen.
7. das Zeichen `&` als Spaltentrennzeichen in Tabellen- und Matrixumgebungen charakterisieren.
8. die Dateiendung `.bib` einer BibTeX-Literaturdatenbank zuordnen und ihre Funktion für das Literaturverzeichnis beschreiben.
9. den Befehl `\tableofcontents` als Mechanismus zur automatischen Erzeugung des Inhaltsverzeichnisses auf Basis der Gliederungsbefehle definieren.

### Anwendung
**Du kannst …**

1. das Paket `float` mit der Platzierungsoption `[H]` einsetzen, um eine Abbildung an genau der im Quelltext vorgesehenen Position zu fixieren.
2. das Paket `tabularx` nutzen, um Tabellenbreiten auf `\textwidth` zu begrenzen und Spalten mit dem Typ `X` flexibel umbrechen zu lassen.
3. mit der Umgebung `tabularx` oder geeigneten Spaltentypen Tabellen so gestalten, dass sie trotz vieler Spalten in die Textbreite passen.
4. den Befehl `\caption{...}` in einer `figure`-Umgebung verwenden, um nummerierte Bildunterschriften korrekt zu erzeugen.
5. das Paket `listings` für Quellcode mit Syntax-Highlighting, Zeilennummern und Sprachauswahl gezielt einsetzen.
6. den Befehl `\verb|...|` verwenden, um Codefragmente oder Dateinamen mit Unterstrichen wortwörtlich im Fließtext auszugeben.
7. Pakete wie `tagpdf` oder vergleichbare Lösungen einsetzen, um PDF-Dokumente mit Tags für bessere Barrierefreiheit und Screenreader-Unterstützung zu versehen.
8. mit `\multicolumn{...}{...}{...}` Tabellenzellen über mehrere Spalten hinweg verbinden und so übersichtliche Kopfzeilen erstellen.
9. mit `\addbibresource{...}` im BibLaTeX-Workflow eine `.bib`-Datei als Literaturquelle einbinden.
10. den Schalter `\centering` innerhalb von Umgebungen wie `figure` nutzen, um Inhalte ohne zusätzlichen vertikalen Abstand zu zentrieren.
11. mit `\input{...}` und `\include{...}` LaTeX-Dokumente modular strukturieren und Quelltextdateien sinnvoll aufteilen.
12. typische Mathe-Fehlermeldungen wie „Missing $ inserted“ auf unmaskierte Sonderzeichen wie `_` und `^` zurückführen und durch Mathemodus oder Escaping beheben.
13. mit `\setcounter{tocdepth}{...}` steuern, bis zu welcher Gliederungsebene Einträge im Inhaltsverzeichnis erscheinen.
14. gezielt `\noindent` oder globale Einstellungen für `\parindent` verwenden, um Absatzeinzüge typografisch passend zu steuern.

### Strukturelle Analyse
**Du kannst …**

1. die Kompilierkette aus LaTeX, BibTeX/Biber und erneuten LaTeX-Läufen analysieren und daraus Maßnahmen zum Beheben von „undefined citation“-Fehlern ableiten.
2. das Platzierungsverhalten von Gleitobjekten analysieren und erklären, warum große Bilder bei knappen Seitenrändern ans Kapitelende oder auf eigene Float-Seiten verschoben werden.
3. die Risiken des Einsatzes von `\def` im Vergleich zu `\newcommand` begründen und bewerten, insbesondere im Hinblick auf Namenskonflikte und Wartbarkeit.
4. beurteilen, wie starke Schriftverkleinerung in Tabellen die typografische Konsistenz und Lesbarkeit eines wissenschaftlichen Dokuments beeinträchtigt.
5. Encoding-Probleme nach Copy & Paste aus PDF-Dateien kritisch untersuchen und auf inkompatible Unicode-Zeichen wie „smart quotes“ oder spezielle Minuszeichen zurückführen.
6. die interne Arbeitsweise von `\include` mit erzwungenen Seitenumbrüchen und separaten `.aux`-Dateien analysieren und von `\input` abgrenzen.
7. typografisch und semantisch begründen, warum vordefinierte Operatoren wie `\sin` für mathematische Funktionen im Mathemodus gegenüber reinem Text `sin` zu bevorzugen sind.
8. Strategien zur globalen Anpassung von Bezeichnern wie `\figurename` (z. B. von „Abbildung“ zu „Abb.“) entwickeln und deren Wirkung auf die Konsistenz der Lokalisierung im gesamten Dokument bewerten.
9. den Einsatz spezialisierter Pakete wie `algorithm2e` gegenüber einfacher `verbatim`-Ausgabe für Pseudocode abwägen und hinsichtlich Strukturierung, Mathematikintegration und Lesbarkeit analysieren.
10. Ursachen für Encoding-Mismatches zwischen tatsächlicher Dateikodierung und `inputenc`-Einstellungen identifizieren und geeignete Korrekturen auf Editor- oder LaTeX-Ebene begründen.
