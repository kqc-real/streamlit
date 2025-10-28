### Finale Anleitung: So importieren Sie Ihre Fragen in Anki

Herzlichen Glückwunsch! Sie haben soeben ein Fragenset aus unserer App exportiert. Folgen Sie diesen Schritten, um es in Ihr Anki-Programm zu importieren und mit dem Lernen zu beginnen.

**Voraussetzung:** Sie haben die `anki_import.tsv`-Datei aus unserer App heruntergeladen.

### Kurz-Anleitung (schnell)

Folgen Sie diesen drei schnellen Schritten, wenn Sie den Export sofort in Anki importieren möchten. Für Details siehe weiter unten.

1. Notiztyp (einmalig): Werkzeuge → Notiztypen verwalten → Hinzufügen → Basis → Name: **MC-Test-Frage**. Fügen Sie die Felder hinzu (siehe unten).
2. Import: Datei → Importieren → wähle `anki_import.tsv` → Notiztyp: **MC-Test-Frage** → Häkchen: HTML in Feldern erlauben → Prüfe Feldzuordnung → Importieren.
3. Kontrolle: Öffne ein paar Karten; wenn Layout/Stil fehlt, kopiere die Vorlagen aus dieser Anleitung in den Notiztyp (siehe Vorlagen weiter oben).

Feld‑Zuordnung (TSV-Spalten → Anki‑Felder): kopierbar

```
1 -> Frage
2 -> Optionen
3 -> Antwort_Korrekt
4 -> Erklaerung_Basis
5 -> Erklaerung_Erweitert
6 -> Glossar
7 -> Fragenset_Titel
8 -> Thema
9 -> Schwierigkeit
10 -> Tags_Alle
```

Prüf‑Check vor Import: Notiztyp erstellt, HTML erlaubt, Datei in UTF-8 (keine BOM).

#### Schritt 1: Einen passenden Notiztyp in Anki erstellen

Damit Anki die Daten korrekt zuordnen kann, benötigen Sie einen passenden "Notiztyp". Diesen müssen Sie nur **einmalig** anlegen.

1.  Öffnen Sie Anki und gehen Sie im Menü auf `Werkzeuge` → `Notiztypen verwalten`.
2.  Klicken Sie auf `Hinzufügen`, wählen Sie `Basis` als Vorlage und geben Sie dem Notiztyp einen Namen, z.B. **"MC-Test-Frage"**.
3.  Wählen Sie den neuen Notiztyp aus und klicken Sie auf `Felder...`.
4.  Stellen Sie sicher, dass die folgenden Felder vorhanden sind (benennen Sie "Vorderseite"/"Rückseite" um und fügen Sie den Rest hinzu):
    *   `Frage`
    *   `Antwort_Korrekt`
    *   `Optionen`
    *   `Erklaerung_Basis`
    *   `Erklaerung_Erweitert`
    *   `Glossar`
    *   `Fragenset_Titel`
    *   `Thema`
    *   `Schwierigkeit`
    *   `Tags_Alle` (für die Anki-Suchfunktion)
5.  Schließen Sie das Felder-Fenster.

#### Schritt 2 (Empfohlen): Das Kartenlayout anpassen

Damit alle importierten Informationen schön dargestellt werden, sollten Sie das Layout der Karten anpassen.

1.  Während der Notiztyp "MC-Test-Frage" noch markiert ist, klicken Sie auf `Karten...`.
2.  Ersetzen Sie den Inhalt der drei Bereiche (`Vorderseite-Vorlage`, `Styling`, `Rückseite-Vorlage`) mit dem folgenden Code:

**Code für die `Vorderseite-Vorlage`:**
```html
<div class="meta-info">
  <span class="meta-item"><strong>Fragenset:</strong> {{Fragenset_Titel}}</span>
  <span class="meta-item"><strong>Thema:</strong> {{Thema}}</span>
  <span class="meta-item"><strong>Schwierigkeit:</strong> {{Schwierigkeit}}</span>
</div>
<div class="card-front">
  <div class="question-block">{{Frage}}</div>
  <div class="options-block">{{Optionen}}</div>
</div>
```

**Code für das `Styling`-Feld:**
```css
.card { font-family: Arial, sans-serif; font-size: 18px; text-align: left; color: black; background-color: white; }
.section-title { font-size: 1em; font-weight: bold; color: #005A9C; margin-top: 1.5em; margin-bottom: 0.5em; border-bottom: 1px solid #ccc; padding-bottom: 3px; }
.options-block ol { list-style-type: upper-alpha; padding-left: 2em; }
.meta-info { background-color: #f7f7f7; padding: 8px 12px; border-radius: 5px; margin-bottom: 15px; font-size: 0.85em; color: #555; display: flex; flex-wrap: wrap; gap: 15px; }
.meta-item strong { color: #000; }
dl dt { font-weight: bold; margin-top: 0.5em; }
dl dd { margin-left: 1.5em; margin-bottom: 0.5em; }
```

**Code für die `Rückseite-Vorlage`:**
```html
{{FrontSide}}
<hr>
<div class="card-back">
  <div class="answer-block">
    <h3 class="section-title">Korrekte Antwort</h3>
    <div class="answer-content">{{Antwort_Korrekt}}</div>
  </div>
  {{#Erklaerung_Basis}}
  <div class="explanation-block">
    <h3 class="section-title">Erklärung</h3>
    <div class="explanation-content">{{Erklaerung_Basis}}</div>
  </div>
  {{/Erklaerung_Basis}}
  {{#Erklaerung_Erweitert}}
  <div class="extended-explanation-block">
    <h3 class="section-title">Erweiterte Erklärung</h3>
    <div class="extended-explanation-content">{{Erklaerung_Erweitert}}</div>
  </div>
  {{/Erklaerung_Erweitert}}
  {{#Glossar}}
  <div class="glossary-block">
    <h3 class="section-title">Glossar</h3>
    <div class="glossary-content">{{Glossar}}</div>
  </div>
  {{/Glossar}}
</div>
```

---
**Visuelle Vorschau des Ergebnisses**

So würde eine Karte mit diesem Layout und Beispieldaten in Anki aussehen:

> **Vorderseite:**
>
> <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; font-family: Arial, sans-serif;">
>   <div style="background-color: #f7f7f7; padding: 8px 12px; border-radius: 5px; margin-bottom: 15px; font-size: 0.85em; color: #555; display: flex; flex-wrap: wrap; gap: 15px;">
>     <span style="color: #000;"><strong>Fragenset:</strong></span> Projektmanagement Grundlagen
>     <span style="color: #000;"><strong>Thema:</strong></span> Agile Methoden
>     <span style="color: #000;"><strong>Schwierigkeit:</strong></span> mittel
>   </div>
>   <div style="font-size: 18px;">
>     Was ist ein "Sprint" in Scrum?
>     <ol type="A" style="padding-left: 2em; margin-top: 10px;">
>       <li>Ein Meeting, das täglich stattfindet.</li>
>       <li>Ein festgelegter Zeitabschnitt, in dem ein fertiges Inkrement erstellt wird.</li>
>       <li>Ein Dokument, das die Projektanforderungen beschreibt.</li>
>     </ol>
>   </div>
> </div>

> **Rückseite (nach dem Umdrehen):**
>
> <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; font-family: Arial, sans-serif;">
>   <!-- (Vorderseite wird hier wiederholt) -->
>   <hr style="margin-top: 20px; margin-bottom: 20px;">
>   <div>
>     <h3 style="font-size: 1em; font-weight: bold; color: #005A9C; margin: 1.5em 0 0.5em 0; border-bottom: 1px solid #ccc; padding-bottom: 3px;">Korrekte Antwort</h3>
>     <div>Ein festgelegter Zeitabschnitt, in dem ein fertiges Inkrement erstellt wird.</div>
>     <h3 style="font-size: 1em; font-weight: bold; color: #005A9C; margin: 1.5em 0 0.5em 0; border-bottom: 1px solid #ccc; padding-bottom: 3px;">Erklärung</h3>
>     <div>In Scrum ist ein Sprint ein iterativer Zyklus von typischerweise 2-4 Wochen, an dessen Ende ein potenziell auslieferbares Produktinkrement steht.</div>
>   </div>
> </div>

---

#### Schritt 3: Die TSV-Datei importieren

1.  Kehren Sie zum Hauptfenster von Anki zurück und wählen Sie im Menü `Datei` → `Importieren...`.
2.  Wählen Sie die heruntergeladene `anki_import.tsv`-Datei aus.
3.  Im Import-Fenster, nehmen Sie folgende Einstellungen vor:
    *   **Notiztyp:** Wählen Sie **"MC-Test-Frage"**.
    *   **Deck:** Wählen Sie das gewünschte Deck.
    *   **HTML in Feldern erlauben:** Sicherstellen, dass hier ein **Häkchen gesetzt** ist.
    *   **Feldzuordnung:** Prüfen, ob die Zuordnung korrekt ist (Feld 1 → `Frage`, Feld 2 → `Antwort_Korrekt`, usw.).
4.  Klicken Sie auf `Importieren`.

**Fertig!** Ihre Fragen sind nun formatiert und vollständig in Anki. Viel Erfolg beim Lernen!
