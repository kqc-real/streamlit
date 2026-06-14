# Datenschutzerklärung

Informationen gemäß Art. 13 Datenschutz-Grundverordnung (DSGVO) für `https://mc-test.streamlit.app/`.

## 1. Verantwortlicher

Prof. Dr.-Ing. habil. Klaus Quibeldey-Cirkel  
IU Internationale Hochschule · Duales Studium  
Juri-Gagarin-Ring 152  
99084 Erfurt  
Deutschland

E-Mail: [klaus.quibeldey-cirkel@iu.org](mailto:klaus.quibeldey-cirkel@iu.org)

## 2. Zweck der App

MC-Test ist eine Streamlit-App zum Auswählen, Erstellen, Üben und Auswerten von Multiple-Choice-Fragensets. Die App nutzt Pseudonyme statt Klarnamen. Bitte gib keine echten Namen, Matrikelnummern, E-Mail-Adressen oder sonstigen Personendaten in Pseudonyme, Freitexte oder hochgeladene Fragensets ein.

## 3. Hosting und Zugriffsdaten

Die App wird über Streamlit Community Cloud unter `mc-test.streamlit.app` bereitgestellt. Beim Aufruf verarbeitet der Plattformanbieter technisch notwendige Zugriffsdaten, zum Beispiel IP-Adresse, Zeitpunkt des Zugriffs, Browser- und Geräteinformationen sowie die aufgerufene URL. Diese Verarbeitung ist für Auslieferung, Sicherheit und Betrieb der App erforderlich.

Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO: unser berechtigtes Interesse am sicheren und funktionsfähigen Betrieb der App.

## 4. Daten, die die App selbst speichert

Die App speichert in einer SQLite-Datenbank insbesondere:

- Pseudonym und daraus abgeleitete technische Nutzerkennung,
- ausgewähltes Fragenset, Testmodus, Tempo und Startzeit einer Testsitzung,
- Antworten, Punkte, Richtig-/Falsch-Status und optional angegebene Antwortsicherheit,
- Bookmarks und gemeldetes Frage-Feedback,
- Ergebnis-Zusammenfassungen für Historie und Bestenliste,
- optionales Recovery-Geheimwort nur als Salt und Hash, nicht im Klartext,
- Sprache und Tempo als Einstellungen für reservierte Pseudonyme,
- technische Heartbeats zur Anzeige aktiver Sitzungen,
- Admin- und Sicherheitsprotokolle, wenn Admin-Funktionen genutzt werden.

Wenn du ein eigenes Fragenset hochlädst oder einfügst, speichert die App außerdem den Fragenset-Inhalt, technische Metadaten wie Upload-Zeitpunkt, ursprünglichen Dateinamen sowie das zugehörige Pseudonym beziehungsweise dessen Hash.

## 5. Zwecke und Rechtsgrundlagen

Die Daten werden verarbeitet, um Testsitzungen zu starten, Antworten auszuwerten, Fortschritt und Ergebnisse anzuzeigen, eigene Fragensets temporär bereitzustellen, Pseudonyme optional wiederherstellbar zu machen und Missbrauch oder technische Fehler nachvollziehen zu können.

Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO. Das berechtigte Interesse liegt im Betrieb einer Lern- und Übungsanwendung. Das Recovery-Geheimwort ist freiwillig; ohne Recovery kann ein Pseudonym nach Ablauf der Freigabezeit wieder frei werden.

## 6. Externe Dienste

Die App ruft selbst keine externen LLM-APIs auf. Prompt-Texte können angezeigt, kopiert oder heruntergeladen werden. Wenn du diese Prompts oder Fragensets in externe KI-Dienste einfügst, geschieht das außerhalb dieser App und nach den dort geltenden Bedingungen.

Die App setzt keine eigenen Tracking-, Analyse- oder Werbe-Cookies und nutzt keine eigenen Analyse- oder Werbe-Tools. Für den technischen Betrieb kann Streamlit Community Cloud technisch notwendige Cookies, lokalen Browser-Speicher oder vergleichbare Technologien einsetzen, etwa zur Sitzungssteuerung und Auslieferung der App. Diese technisch notwendigen Funktionen sind erforderlich, um die App bereitzustellen.

## 7. Speicherdauer

Nicht reservierte Pseudonyme werden nach Ablauf der konfigurierten Freigabezeit standardmäßig nach 24 Stunden wieder freigegeben. Dabei werden zugehörige Sitzungen, Antworten, Bookmarks und Feedback gelöscht. Ergebnis-Zusammenfassungen können für Bestenlisten und Auswertungen erhalten bleiben.

Temporäre Nutzer-Fragensets werden standardmäßig nach 24 Stunden bereinigt. Bei reservierten Pseudonymen kann die Aufbewahrung temporärer Fragensets bis zu 14 Tage betragen. Nutzerinnen und Nutzer sowie Administratoren können temporäre Fragensets vorher löschen.

Recovery-Salt und Recovery-Hash bleiben gespeichert, solange das reservierte Pseudonym besteht. Admin- und Sicherheitsprotokolle werden nur so lange vorgehalten, wie sie für Betrieb, Fehlersuche und Schutz der App erforderlich sind.

## 8. Empfänger

Empfänger personenbezogener oder personenbeziehbarer Daten können der technische Plattformanbieter Streamlit Community Cloud beziehungsweise Snowflake Inc. sowie die für Betrieb und Administration der App verantwortlichen Personen sein. Eine Weitergabe zu Werbezwecken findet nicht statt.

## 9. Deine Rechte

Du hast nach Maßgabe der DSGVO das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und Widerspruch. Du kannst dich außerdem bei einer Datenschutz-Aufsichtsbehörde beschweren.

Für Anfragen nutze bitte die im Impressum angegebene E-Mail-Adresse und nenne, soweit möglich, dein Pseudonym. Verwende dabei keine zusätzlichen sensiblen Daten, wenn sie für die Anfrage nicht nötig sind.

## 10. Stand

Stand: 14. Juni 2026
