# 🐍 Installation mit Conda / Miniforge

Diese Variante ist empfohlen, wenn du bereits Anaconda, Miniforge oder Mambaforge nutzt. Sie legt ein eigenes Environment `mctest` an, damit die App-Abhängigkeiten nicht mit der globalen `base`-Umgebung kollidieren.

Conda liefert außerdem fertige Binärpakete (von `conda-forge`) und umgeht viele native Build-Probleme, z.B. bei `pyarrow`, `brotli`, `zopfli`, `cairo`, `pango` oder `gdk-pixbuf`.

## Warum Conda?
- Vorbuildete Pakete für `pyarrow`, `brotli`, `zopfli`, `cairo` und mehr
- Einfaches Festlegen der Python-Version (nutze `python=3.12`)
- Sauberes, isoliertes Environment ohne System-Python zu ändern
- Keine Vermischung mit der globalen Anaconda-`base`-Umgebung
- Mamba (Schnellinstaller) reduziert Wartezeiten

---

## Schritt-für-Schritt (empfohlen)

Wähle zuerst, welches Conda-Paket du installieren möchtest. Am einfachsten ist die GitHub‑Releases‑Seite von Miniforge/Mambaforge — dort findest du die passenden Installer für macOS und Windows:

- Releases-Seite (wähle die passende Datei für dein System): https://github.com/conda-forge/miniforge/releases/latest

Empfohlene Auswahl für die meisten Nutzer:

- macOS (Apple Silicon / M1/M2): lade `Mambaforge-MacOSX-arm64.sh` oder `Miniforge3-MacOSX-arm64.sh` herunter.
- macOS (Intel): lade `Mambaforge-MacOSX-x86_64.sh` oder `Miniforge3-MacOSX-x86_64.sh` herunter.
- Windows (64-bit): lade `Mambaforge-Windows-x86_64.exe` oder `Miniforge3-Windows-x86_64.exe` herunter.

Hinweis: Falls du unsicher bist, welche Architektur dein Mac hat, klicke oben links auf das Apple‑Logo → "Über diesen Mac" → dort steht "Chip" (Apple Silicon) oder "Intel".

### macOS / Linux (Terminal)

1) Installiere Mambaforge / Miniforge (einmalig). Folge dem Installer auf der Projektseite.

2) Erstelle und aktiviere ein Environment mit Python 3.12:

```bash
conda create -n mctest python=3.12 -y
conda activate mctest
```

3) Installiere die problematischen nativen Pakete aus `conda-forge`:

```bash
conda install -c conda-forge pyarrow brotli zopfli cairo pango gdk-pixbuf -y
```

4) Python-Abhängigkeiten der App installieren:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

5) App starten:

```bash
streamlit run app.py
```

---

### Windows (PowerShell / Eingabeaufforderung)

1) Installiere Mambaforge/Miniforge für Windows (grafischer Installer).

2) Erstelle und aktiviere das Environment:

```powershell
conda create -n mctest python=3.12 -y
conda activate mctest
```

3) Installiere native Pakete aus `conda-forge`:

```powershell
conda install -c conda-forge pyarrow brotli zopfli cairo pango gdk-pixbuf -y
```

4) Python-Abhängigkeiten der App installieren:

```powershell
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

5) Starte die App:

```powershell
streamlit run app.py
```

---

### Tipp: Mamba statt conda (viel schneller)

```bash
# einmalig im base env
conda install -n base -c conda-forge mamba -y
# dann z.B.
mamba create -n mctest python=3.12 -y
conda activate mctest
mamba install -c conda-forge pyarrow brotli zopfli -y
```

---

## Hinweise
- Verwende Python 3.12 im Environment, nicht 3.14.
- `requirements.txt` pinnt Streamlit aktuell auf `streamlit==1.58.0`.
- Starte die App immer aus dem aktivierten Environment: `conda activate mctest`.
- Conda-Umgebungen belegen zusätzlichen Speicherplatz, sind dafür aber sehr zuverlässig.
