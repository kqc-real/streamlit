# 🚀 Fallstudie & Projektplanung: Release 2.0

**Projekt:** MC-Test Streamlit App  
**Release:** 2.0  
**Datum:** 18. November 2025  
**Zielgruppe:** BWL-Studierende im Kurs "Agiles Projektmanagement"  
**Didaktisches Ziel:** Anwendung agiler Methoden (Scrum) zur Konzeption eines digitalen Produkts. Die studentischen Teams erstellen Business-Artefakte, die als Implementierungsauftrag für eine externe IT-Abteilung dienen.

---

## 1. Projektvision & Strategische Ziele

### Elevator Pitch

> **Für** Lehrende und Content-Creators, **die** viel Zeit bei der Erstellung von Lernmaterialien verlieren, **ist** unsere App eine KI-gestützte SaaS-Plattform, **die** automatisch hochwertige Fragensets generiert. **Im Gegensatz zu** generischen KI-Tools **bieten wir** zwei maßgeschneiderte Lösungen: ein kostengünstiges, datenschutzkonformes Freemium-Modell und ein flexibles "Bring-Your-Own-Key"-Modell für professionelle Anwender.

### Aufteilung in Scrum-Teams

Für die Umsetzung von Release 2.0 werden zwei spezialisierte Scrum-Teams gebildet. Jedes Team arbeitet autonom an einem strategischen Ziel. Das Ergebnis jedes Sprints sind **konkrete Anforderungsdokumente (Business-Artefakte)**, die als klarer Arbeitsauftrag an die IT-Abteilung zur technischen Implementierung übergeben werden.

*   **Team A (Kernprodukt & Freemium):** Konzentriert sich auf die Konzeption des Hauptprodukts und des Freemium-Modells, um eine breite Nutzerbasis zu gewinnen.
*   **Team B (Power-User & Flexibilität):** Konzentriert sich auf das "Bring-Your-Own-Key" (BYOK)-Modell, das professionellen Nutzern maximale Flexibilität und Kostenkontrolle bietet.

---

## 2. Team A: Kernprodukt & Freemium – Sprint-Planung

**Sprint-Ziel:** Ein vollständiges Business-Konzept für das Kernprodukt und das Freemium/Pro-Modell zu erstellen. Dieses Konzept dient als detaillierter Implementierungsauftrag für die IT-Abteilung.

### User Stories für Team A

1.  **User Story 1.1 (Marktanalyse):** Aus der Rolle des **Produktmanagers** möchte ich eine **Wettbewerbsanalyse** durchführen, um unser Freemium-Angebot optimal im EdTech-Markt zu positionieren.
    *   **Akzeptanzkriterien:**
        *   Mindestens 3 relevante Wettbewerber (z.B. Kahoot, Quizlet, Particify) sind analysiert.
        *   Deren Preise, Features und Limitierungen sind dokumentiert.
        *   Eine klare Empfehlung für die Ausgestaltung unseres Freemium-Tiers (z.B. "3 kostenlose Fragensets pro Monat") ist abgeleitet.
    *   **Lieferobjekt:** Dokument "Wettbewerbsanalyse".

2.  **User Story 1.2 (Zielgruppendefinition):** Aus der Rolle des **Marketing-Managers** möchte ich eine detaillierte **User Persona** für unsere Kernzielgruppe ("Digitale Lehrerin Lisa") erstellen, um Marketingbotschaften und die Produktansprache zu schärfen.
    *   **Akzeptanzkriterien:**
        *   Die Persona umfasst Demografie, Ziele, Pain Points und bevorzugte Kanäle.
        *   Die Persona wurde vom Product Owner abgenommen.
    *   **Lieferobjekt:** Dokument "Persona-Steckbrief".

3.  **User Story 1.3 (Prozessoptimierung):** Aus der Rolle des **Produktmanagers** möchte ich eine **User Journey Map** für den Onboarding-Prozess (von der Registrierung bis zur ersten erfolgreichen Fragengenerierung) visualisieren, um Reibungspunkte für den Nutzer zu identifizieren und zu minimieren.
    *   **Akzeptanzkriterien:**
        *   Die Map visualisiert die Schritte, Gedanken und Emotionen des Nutzers.
        *   Mindestens 3 potenzielle Reibungspunkte (z.B. "komplizierte Registrierung") sind identifiziert.
        *   Konkrete Verbesserungsvorschläge sind dokumentiert (z.B. "Social-Login anbieten").
    *   **Lieferobjekt:** Visualisierung "User Journey Map".

4.  **User Story 1.4 (Anforderungsdefinition):** Aus der Rolle des **Produktmanagers** möchte ich ein **Anforderungsdokument für das User-Management** erstellen, damit die IT die Registrierungs- und Login-Funktionen umsetzen kann.
    *   **Akzeptanzkriterien:**
        *   Der Prozess für Registrierung, Login und Passwort-Reset ist als Flussdiagramm beschrieben.
        *   Die Anforderungen an die Datenspeicherung (DSGVO-konform) sind definiert.
    *   **Lieferobjekt:** Anforderungsdokument "User-Management".

5.  **User Story 1.5 (UI-Konzeption):** Aus der Rolle des **Produktmanagers** möchte ich ein **Konzept für das User-Dashboard** entwerfen, damit Nutzer ihren aktuellen Status (Freemium/Pro) und ihre verbleibenden Credits einsehen können.
    *   **Akzeptanzkriterien:**
        *   Ein Wireframe (einfache Skizze) des Dashboards existiert.
        *   Alle anzuzeigenden Elemente (z.B. Credit-Anzeige, Upgrade-Button) sind definiert und beschrieben.
    *   **Lieferobjekt:** Wireframe & Feature-Liste "User-Dashboard".

6.  **User Story 1.6 (Geschäftsprozess):** Aus der Rolle des **Produktmanagers** möchte ich ein **Konzept für die Payment-Integration** erstellen, um die Anforderungen für die Bezahlung des Pro-Plans an die IT zu übergeben.
    *   **Akzeptanzkriterien:**
        *   Der Bezahlprozess für ein Monatsabonnement ist als Flussdiagramm skizziert.
        *   Die Anforderungen an die Rechnungsstellung sind definiert.
        *   Der Payment-Provider (Stripe) ist als Anforderung festgehalten.
    *   **Lieferobjekt:** Prozessbeschreibung "Payment-Flow".

7.  **User Story 1.7 (Risikomanagement):** Aus der Rolle des **Controllers** möchte ich eine **Risikoanalyse für das Freemium-Modell** durchführen, um potenzielle geschäftliche Gefahren (z.B. übermäßige Kosten durch Gratis-Nutzer) zu identifizieren.
    *   **Akzeptanzkriterien:**
        *   Mindestens 3 Risiken sind identifiziert (z.B. "Missbrauch durch Wegwerf-Accounts").
        *   Für jedes Risiko ist eine Gegenmaßnahme vorgeschlagen (z.B. "Rate-Limiting pro IP-Adresse").
    *   **Lieferobjekt:** Dokument "Risiko-Matrix".

### Organisation & Arbeitsweise (Team A)

*   **Tool:** Das Team organisiert seine Arbeit in einem **digitalen Kanban-Board** (GitHub Projects) mit den Spalten "Product Backlog", "Sprint Backlog", "In Arbeit" und "Fertig (zur Übergabe an IT)". Jede User Story ist eine Karte auf dem Board.
*   **Prozess in 4 Arbeitssitzungen (via BigBlueButton):**
    1.  **Sprint Planning:** Das Team wählt alle User Stories für den Sprint aus. Die Akzeptanzkriterien werden besprochen und Aufgaben verteilt (z.B. "Anna erstellt Wettbewerbsanalyse", "Ben skizziert User Journey").
    2.  **Mid-Sprint-Abstimmung:** Zwischenpräsentation der erstellten Entwürfe (z.B. Persona, erster Wireframe). Das Team gibt sich gegenseitig Feedback zur Verbesserung.
    3.  **Finalisierung der Artefakte:** Die Dokumente und Diagramme werden basierend auf dem Feedback finalisiert und als professionelle Business-Artefakte aufbereitet.
    4.  **Sprint Review & Retrospektive:** Das Team präsentiert dem Product Owner die fertigen Lieferobjekte (Übergabe in GitHub Projects). Diese werden abgenommen und bilden den Implementierungsauftrag für die IT. Anschließend reflektiert das Team in der Retrospektive die Zusammenarbeit und identifiziert Verbesserungspotenziale für den nächsten Sprint.

---

## 3. Team B: Power-User & Flexibilität – Sprint-Planung

**Sprint-Ziel:** Das "Bring-Your-Own-Key" (BYOK)-Modell als Geschäftsmodell so detailliert zu konzipieren, dass die IT-Abteilung die Anforderungen für die Integration externer LLM-Provider versteht.

### User Stories für Team B

1.  **User Story 2.1 (Marktanalyse):** Aus der Rolle des **Produktmanagers** möchte ich eine **Marktanalyse für BYOK-Modelle** bei anderen SaaS-Tools durchführen, um Best Practices für die Benutzeroberfläche und die Nutzerkommunikation zu identifizieren.
    *   **Akzeptanzkriterien:**
        *   Mindestens 3 Tools mit BYOK-Modell sind analysiert.
        *   Screenshots und Beschreibungen des Key-Eingabe-Prozesses sind vorhanden.
        *   Eine Empfehlung für unsere UI-Gestaltung ist abgeleitet ("So machen es die Marktführer").
    *   **Lieferobjekt:** Dokument "Best-Practice-Analyse BYOK".

2.  **User Story 2.2 (Zielgruppendefinition):** Aus der Rolle des **Marketing-Managers** möchte ich eine **User Persona für unsere Power-User** ("Freelance-Trainer Tom") erstellen, um die Vorteile des BYOK-Modells gezielt zu bewerben.
    *   **Akzeptanzkriterien:**
        *   Die Persona beschreibt einen technisch versierten Nutzer mit Fokus auf Kostenkontrolle und Flexibilität.
        *   Die Kernbotschaft für das Marketing ("Volle Kontrolle, keine Abofalle") ist klar formuliert.
    *   **Lieferobjekt:** Dokument "Persona-Steckbrief Power-User".

3.  **User Story 2.3 (UI-Konzeption):** Aus der Rolle des **Produktmanagers** möchte ich ein **UI-Konzept für die API-Key-Eingabe** entwerfen, das sicher und benutzerfreundlich ist.
    *   **Akzeptanzkriterien:**
        *   Ein Wireframe zeigt, wo und wie der Nutzer seinen API-Key eingeben kann.
        *   Ein klarer Datenschutzhinweis ("Ihr Key wird nur lokal im Browser gespeichert und nicht an unsere Server gesendet") ist formuliert.
        *   Die unterstützten Provider (z.B. OpenAI, Google, Anthropic, Hugging Face) sind im UI-Konzept aufgeführt.
    *   **Lieferobjekt:** Wireframe & Textbausteine "API-Key-Management".

4.  **User Story 2.4 (Anforderungsdefinition):** Aus der Rolle des **Produktmanagers** möchte ich ein **Anforderungsdokument für den BYOK-Prozess** erstellen, damit die IT die technische Logik implementieren kann.
    *   **Akzeptanzkriterien:**
        *   Der Prozess beschreibt, wie die App den vom Nutzer eingegebenen Key für die API-Anfrage verwendet.
        *   Es ist definiert, dass BYOK-Nutzer automatisch alle Pro-Features der App freigeschaltet bekommen.
    *   **Lieferobjekt:** Anforderungsdokument "BYOK-Backend-Logik".

5.  **User Story 2.5 (Prozessoptimierung):** Aus der Rolle des **Support-Managers** möchte ich ein **Konzept für die Fehlerbehandlung** im BYOK-Modus entwerfen, um Nutzer bei Problemen bestmöglich zu unterstützen.
    *   **Akzeptanzkriterien:**
        *   Mindestens 3 typische Fehlerfälle sind definiert (z.B. "API-Key ungültig", "API-Provider nicht erreichbar", "Kostenlimit beim Provider überschritten").
        *   Für jeden Fehlerfall ist eine klare und hilfreiche Fehlermeldung für den Nutzer formuliert.
    *   **Lieferobjekt:** Dokument "Fehlerkatalog & Fehlermeldungen".

6.  **User Story 2.6 (Kundenkommunikation):** Aus der Rolle des **Support-Managers** möchte ich eine **FAQ-Sektion für das BYOK-Modell** entwerfen, um die häufigsten Nutzerfragen proaktiv zu beantworten und den Support zu entlasten.
    *   **Akzeptanzkriterien:**
        *   Mindestens 5 relevante Fragen sind formuliert (z.B. "Wo finde ich meinen API-Key?", "Ist die Speicherung sicher?").
        *   Die Antworten sind klar und verständlich für die Zielgruppe geschrieben.
    *   **Lieferobjekt:** Dokument "FAQ-Sektion BYOK".

7.  **User Story 2.7 (Rechtliche Prüfung):** Aus der Rolle des **Produktmanagers** möchte ich eine **Analyse der rechtlichen Rahmenbedingungen** für das BYOK-Modell durchführen, um Haftungsfragen zu klären.
    *   **Akzeptanzkriterien:**
        *   Es ist dokumentiert, dass der Nutzer für die Kosten und die Einhaltung der Nutzungsbedingungen seines LLM-Providers selbst verantwortlich ist.
        *   Ein Entwurf für einen entsprechenden Passus in den AGB ist formuliert.
    *   **Lieferobjekt:** Dokument "Analyse rechtlicher Aspekte BYOK".

### Organisation & Arbeitsweise (Team B)

*   **Tool:** Das Team nutzt ebenfalls ein **digitales Kanban-Board** zur Organisation seiner Aufgaben.
*   **Prozess in 4 Arbeitssitzungen:**
    1.  **Sprint Planning:** Das Team plant seinen Sprint, indem es die User Stories aus dem Backlog zieht. Die Aufgaben werden im Team verteilt (z.B. "Carla recherchiert Best Practices", "David entwirft die Wireframes").
    2.  **Mid-Sprint-Abstimmung:** Das Team stellt sich gegenseitig die Entwürfe der Artefakte vor (z.B. erste Version der FAQ, Wireframe für die Key-Eingabe) und sammelt internes Feedback.
    3.  **Finalisierung der Artefakte:** Die Konzepte und Analysen werden finalisiert und als klare, verständliche Dokumente aufbereitet.
    4.  **Sprint Review & Retrospektive:** Die fertigen Lieferobjekte werden dem Product Owner als abgeschlossene Konzeptionsarbeit via GitHub Projects übergeben und bilden die Grundlage für die Implementierungsaufträge an die IT. In der anschließenden Retrospektive wird die Zusammenarbeit im Team reflektiert.