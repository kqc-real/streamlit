# Übergeordnete Lernziele: LaTeX für Einsteiger/innen - Abschlussarbeit

## Dokumentaufbau & Präambel
**LaTeX-Dokumente für Abschlussarbeiten strukturiert und regelkonform aufsetzen**

Du richtest Präambel, Dokumentstart und grundlegende Umgebungen so ein, dass ein konsistenter Aufbau entsteht, und stellst sicher, dass Seitenränder, Inhaltsverzeichnis und Listen den formalen Vorgaben entsprechen.

---

## Mathematiksatz & Ausrichtung
**Mathematische Inhalte sauber markieren und in Formelumgebungen ausrichten**

Du markierst Inline- und Display-Mathematik korrekt, platzierst Ausrichtungspunkte präzise und nutzt Standardbefehle für Brüche, sodass Formeln lesbar und technisch fehlerfrei gesetzt werden.

---

## Grafiken, Floats & Layoutsteuerung
**Abbildungen zielgerichtet einbinden und die Float-Logik beherrschen**

Du bindest Grafiken mit passenden Größen ein, wählst Float-Platzierungen bewusst und steuerst Ausgaben mit Platzierungsoptionen oder Seitenumbrüchen, um Staus am Dokumentende zu vermeiden.

---

## Referenzen & Labeling
**Beschriftungen, Labels und Querverweise konsistent verknüpfen**

Du kombinierst Captions, Labels und Referenzen so, dass Nummerierungen stabil bleiben, nutzt prägnante Präfixe und interpretierst Compiler-Warnungen korrekt, inklusive notwendiger Mehrfachkompilierungen.

---

## Sprache & Typografie
**Sprachspezifische Typografie sicher anwenden**

Du setzt Lokalisierung, Anführungszeichen und Sonderzeichen korrekt um und stellst die passende Silbentrennung sicher, damit der Text typografisch stimmig und fehlerfrei ist.

---

## Literatur & Zitation
**Literaturverwaltung mit biblatex/biber zuverlässig ausführen**

Du richtest den vollständigen Backend-Lauf ein, kontrollierst Pfade und Diagnosehinweise und sorgst dafür, dass Zitate und Bibliografie vollständig und korrekt erscheinen.

---

## Fehlersuche & Debugging
**Compiler- und Layoutwarnungen gezielt diagnostizieren**

Du liest Logmeldungen, ordnest typische Fehlerquellen in LaTeX zu und leitest präzise Korrekturen ab, um Compilerabbrüche oder Layoutabweichungen schnell zu beheben.

---

# Detaillierte Lernziele

Im Kontext des Themas **LaTeX für Einsteiger/innen - Abschlussarbeit** soll dir dieses Fragenset helfen, die folgenden detaillierten Lernziele zu erreichen:

### Reproduktion
**Du kannst …**

1. das Kommentarzeichen `%` in LaTeX benennen
2. den Beginn des Dokumentenkörpers als `\begin{document}` identifizieren
3. Paketladebefehle mit `\usepackage{...}` angeben
4. Abschnittsüberschriften in article mit `\section{...}` kennzeichnen
5. Inline-Mathematik mit Math-Begrenzern kennzeichnen, z. B. einleitendes und schließendes Dollarzeichen
6. die Sprachoption `ngerman` im `babel`-Paket der neuen Rechtschreibung zuordnen

### Anwendung
**Du kannst …**

1. für Bullet-Point-Listen die `itemize`-Umgebung auswählen
2. Seitenränder auf A4 mit `geometry` und `margin=2.5cm` konfigurieren
3. ein automatisches Inhaltsverzeichnis mit `\tableofcontents` nach `\begin{document}` erzeugen
4. Quellcode mit `listings` und `\begin{lstlisting}` einbinden
5. angesammelte Floats vor einem Abschnittswechsel mit `\clearpage` ausgeben
6. Grafiken mit `\includegraphics[width=0.6\textwidth]{...}` skalieren und einfügen
7. Float-Platzierung mit sinnvollen Breiten und `[htbp]`-Option steuern
8. Ausrichtungspunkte in `align`-Umgebungen mit `&` setzen
9. Brüche im Math-Modus mit `\frac{...}{...}` setzen
10. `\caption` und `\label` direkt im `figure` koppeln, indem `\label` nach der `\caption` steht
11. Abbildungen im Text mit `\ref{fig:...}` referenzieren
12. fehlende Referenzen durch Mehrfachkompilieren inklusive Backendlauf beheben
13. Labels durch konsistente Präfixe wie `fig:` oder `tab:` strukturieren
14. den biblatex-Workflow `pdflatex -> biber -> pdflatex -> pdflatex` ausführen
15. Prozentzeichen im Fließtext durch `\%` maskieren
16. deutsche Anführungszeichen mit `csquotes` und `\enquote` setzen

### Strukturelle Analyse
**Du kannst …**

1. einen "Undefined control sequence"-Fehler auf fehlende Pakete oder Tippfehler eingrenzen
2. einen "Runaway argument?"-Fehler auf nicht geschlossene Klammern zurückführen
3. Overfull-`\hbox`-Warnungen analysieren anhand typischer Ursachen wie fehlender Trennstellen
4. `align`-Fehler "Too many &" diagnostizieren durch Abgleich der &-Anzahl pro Zeile
5. fehlende Literaturangaben trotz `\printbibliography` auf fehlende biber/bibtex-Läufe zurückführen
6. Float-Staus analysieren anhand von Bildgrößen und Platzierungsoptionen
7. falsche Silbentrennung auf eine fehlerhafte Sprachwahl in `babel` zurückführen
8. die Warnung "Label(s) may have changed. Rerun to get cross-references right." als Aufforderung zur erneuten Kompilierung interpretieren
