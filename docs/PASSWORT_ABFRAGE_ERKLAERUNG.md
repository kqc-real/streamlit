# 🔒 Passwort-Abfrage: Wann und warum?

## 🤔 Frage: Warum werde ich nicht nach dem Passwort gefragt?

**Antwort:** Du arbeitest in einer **lokalen Entwicklungsumgebung** mit leerem Admin-Key.

---

## 📋 Aktuelle Konfiguration (lokal)

```bash
# .env
MC_TEST_ADMIN_KEY=""              # ← LEER!
MC_TEST_ADMIN_USER="Albert Einstein"
```

**Ergebnis:**
- ⚠️ Warnung in Sidebar: "Admin-Key nicht gesetzt!"
- ✅ Direkter Admin-Zugriff ohne Passwort
- ✅ **KEINE** Passwort-Abfrage beim Löschen von Daten
- ✅ Bequem für lokale Tests

---

## 🔐 Wie aktiviere ich die Passwort-Abfrage?

### **Schritt 1: Admin-Key setzen**

```bash
# In .env ändern:
MC_TEST_ADMIN_KEY="mein_sicheres_passwort_123"
```

### **Schritt 2: App neu starten**

```bash
streamlit run app.py
```

### **Schritt 3: Verhalten testen**

1. **Sidebar:**
   - ✅ KEINE Warnung mehr
   - 🔐 Expander: "Admin Panel" mit Passwort-Eingabefeld
   - Nach Eingabe → Admin-Panel öffnet sich

2. **Beim Löschen von Daten:**
   - 🔒 Eingabefeld: "Admin-Key zur Bestätigung"
   - Bei falscher Eingabe → "🔒 Falscher Admin-Key. Löschung abgebrochen."
   - Bei korrekter Eingabe → Daten werden gelöscht

---

## 🎯 Übersicht: Zwei Modi

### **Modus 1: Lokale Entwicklung (aktuell)**

```bash
MC_TEST_ADMIN_KEY=""              # Leer
```

| Aktion | Passwort erforderlich? |
|--------|------------------------|
| Admin-Panel öffnen | ❌ NEIN |
| Benutzerergebnisse löschen | ❌ NEIN |
| Datenexport | ❌ NEIN |
| Systemeinstellungen ändern | ❌ NEIN |

**Vorteil:** ✅ Schnelles Testen  
**Nachteil:** ⚠️ Unsicher bei Shared Hosting

---

### **Modus 2: Produktion**

```bash
MC_TEST_ADMIN_KEY="sicheres_passwort_123"
```

| Aktion | Passwort erforderlich? |
|--------|------------------------|
| Admin-Panel öffnen | ✅ JA (einmalig beim Öffnen) |
| Benutzerergebnisse löschen | ✅ JA (jedes Mal!) |
| Datenexport | ❌ NEIN (lesend, unkritisch) |
| Systemeinstellungen ändern | ❌ NEIN (Phase 1.5, optional) |

**Vorteil:** 🔒 Sicher  
**Nachteil:** ⌨️ Passwort muss eingegeben werden

---

## 💻 Code-Logik (admin_panel.py, Zeile 130)

```python
# Vor kritischen Aktionen (z.B. Löschen):
if not app_config.admin_key or check_admin_key(reauth_key, app_config):
    # Aktion durchführen (z.B. Daten löschen)
    delete_user_results_for_qset(user_name_plain, q_file)
else:
    st.error("🔒 Falscher Admin-Key. Löschung abgebrochen.")
```

**Bedeutung:**
- `not app_config.admin_key` → **TRUE** wenn Admin-Key leer → **Direkter Zugriff**
- `check_admin_key(...)` → **TRUE** wenn eingegebener Key korrekt → **Zugriff erlaubt**

---

## 🧪 Schnelltest: Passwort-Abfrage aktivieren

### **1. Temporär Admin-Key setzen**

```bash
# In .env:
MC_TEST_ADMIN_KEY="test123"
```

### **2. App neu starten**

```bash
streamlit run app.py
```

### **3. Als Admin einloggen**

- Pseudonym: "Albert Einstein"
- Test starten

### **4. Admin-Panel öffnen**

- 🔐 Passwort-Eingabe erscheint
- Eingeben: `test123`
- Panel öffnet sich

### **5. Daten löschen testen**

- Tab: "Leaderboard"
- Expander: "Benutzerergebnisse für dieses Set zurücksetzen"
- Wähle einen Benutzer
- 🔒 **Passwort-Eingabe erscheint erneut!**
- Falsche Eingabe → Fehler
- Korrekte Eingabe (`test123`) → Löschung erfolgreich

### **6. Zurück zu leerem Key**

```bash
# In .env:
MC_TEST_ADMIN_KEY=""
```

```bash
streamlit run app.py
```

→ Wieder direkter Zugriff ohne Passwort

---

## 🎓 Best Practices

### **Für Studenten / Kursteilnehmer:**
✅ `MC_TEST_ADMIN_KEY=""` (leer lassen)  
✅ Warnung akzeptieren  
✅ Schnelles lokales Testen

### **Für Dozenten / IU-Server:**
✅ `MC_TEST_ADMIN_KEY` mit starkem Passwort setzen  
✅ Mindestens 16 Zeichen  
✅ Alphanumerisch + Sonderzeichen  
✅ Beispiel: `Iu2025!SecureAdmin#Key789`

---

## 🔄 Deployment-Checkliste

**Vor Produktiv-Deployment:**

- [ ] `MC_TEST_ADMIN_KEY` mit sicherem Passwort gesetzt
- [ ] Admin-Passwort in Passwort-Manager gespeichert
- [ ] Admin-Passwort NICHT in Git committed
- [ ] `.env` in `.gitignore` vorhanden
- [ ] Test durchgeführt: Passwort-Abfrage funktioniert
- [ ] Test durchgeführt: Falsches Passwort wird abgelehnt

**Nach Deployment:**

- [ ] Admin-Panel testen (Passwort-Eingabe erforderlich?)
- [ ] Lösch-Funktion testen (Re-Auth erforderlich?)
- [ ] Warnung in Sidebar verschwunden?

---

## 📚 Weitere Informationen

- **Vollständige Sicherheitsanalyse:** `SECURITY_ANALYSIS_ADMIN_AUTH.md`
- **Implementation Details:** `CHANGELOG_SECURITY_PHASE1.md`
- **Zusammenfassung:** `SECURITY_PHASE1_SUMMARY.md`

---

**Fazit:** ✅ Das aktuelle Verhalten ist korrekt und gewollt!  
**Für Produktion:** Setze `MC_TEST_ADMIN_KEY` mit einem sicheren Passwort.
