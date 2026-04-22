# Uni-Threaded-rod for Blender

## 🇩🇪 Deutsch

### Status
Dieses Repository enthält jetzt eine **funktionsfähige Implementierung gemäß Arbeitsanweisung v1.0** (Modulstruktur, Datenbank, Profilgenerator, Mesh-Builder, UI und Operatoren).

Bereits umgesetzt:
- Modulstruktur mit `__init__.py`, `database.py`, `geometry_engine.py`, `mesh_builder.py`, `ui_panel.py`
- Norm-/Materialdatenbank mit vielen Standards
- Profilgenerator für mehrere Profiltypen (V, Trapez, Rund, Buttress, Gothic)
- Helix-Mesh-Erzeugung inkl. Endkappen und Basis-Manifold-Postprocessing
- N-Panel UI inkl. Custom-Mode
- Basis-Operatoren für Gewinde und einfachen KGT-Startpunkt
- Eigenständiger KGT-Mutter-Operator mit Innenprofil (Boolean-basiert)
- Optionales Rückführungsmodul für KGT-Mutter (vereinfachte Geometrie)
- NPT-Taper entlang der Gewindelänge
- Presets inkl. Schnellanwendung im UI
- LOD-Stufen (Preview/Final/Custom) und adaptive Segmentierung für lange Gewinde

Roadmap-Status:
- ✅ v1.0-Roadmap vollständig abgeschlossen
- v1.1+ als optionaler Ausbaupfad (Performance, zusätzliche Maß-Regressionen, Lasttests)

---

### Was ist Uni-Threaded-rod?
Das Add-on **Uni-Threaded-rod** erstellt parametrisierte Gewindegeometrie in Blender:
- Außengewinde
- Innengewinde via Negativ-/Boolean-Modus
- Mehrgängige Gewinde
- Kugelgewindetriebe (Basisworkflow verfügbar)

---

### Installation (Blender Add-on)
1. Repository als ZIP verpacken (oder Ordner lokal bereitstellen).
2. Blender öffnen → **Edit > Preferences > Add-ons**.
3. **Install...** wählen und ZIP/Ordner installieren.
4. Add-on aktivieren: **Uni-threaded-rod**.
5. Im 3D-Viewport: **Sidebar (N) > Uni-threaded-rod**.

---

### Grundbedienung
1. Norm auswählen (z. B. METRIC_ISO).
2. Durchmesser und Länge setzen.
3. Optional: Toleranz, Spiel, Drehrichtung, Endtyp.
4. Material wählen.
5. **Gewinde erstellen** klicken.

Für freie Parameter:
1. Norm auf **CUSTOM** stellen.
2. `custom_diameter`, `custom_pitch`, `custom_profile_type`, `custom_starts` setzen.
3. Gewinde erzeugen.

---


### Qualitätssicherung / Tests
- **Schneller Unit-Testlauf (ohne Blender):** `python -m unittest discover -s tests -p 'test_*.py'`
- **Headless Blender-Smoke-Test:** `blender -b --factory-startup --python scripts/blender_smoke_test.py`
- **CI:** GitHub Actions (`.github/workflows/ci.yml`) führt Ruff, Unit-Tests und den Blender-Smoke-Test aus.

### Release-Hinweis
- Der initiale Abschlussstand ist als **v1.0.0** dokumentiert.
- Änderungsverlauf siehe `CHANGELOG.md`.

### Bekannte Einschränkungen
- ISO-Regelgewinde sind für die Grobreihe tabellarisch von **M1 bis M64** hinterlegt; andere Familien bleiben teilweise als normnahe Näherung implementiert.
- Die GOTHIC-Kette für KGT ist verbessert, aber weiterhin eine **annähernde** Auslegung.
- Sehr extreme Parameterkombinationen (sehr hohe Starts + sehr kurze Länge + sehr kleine Kerndurchmesser) sollten weiterhin manuell geprüft werden.

### Engineering- und Normhinweis (wichtig)
Dieses Projekt erzeugt primär **CAD-Geometrie**. Es ersetzt keine vollständige technische Auslegung nach Norm:
- Keine automatische Tragfähigkeits-/Festigkeitsrechnung (z. B. Nachweis über Spannungsquerschnitt).
- Keine vollumfängliche Toleranzkettenrechnung für reale Fertigungsprozesse.
- Für reale Bauteile müssen Einsatzfall, Lastannahmen, Material, Sicherheitsfaktoren und passende Normausgaben projektspezifisch geprüft werden.

Empfohlener Minimal-Workflow für reale Anwendungen:
1. Zielnorm und Gewindefamilie festlegen (z. B. ISO metrisch, UNC/UNF, Pipe).
2. Parameter eindeutig dokumentieren (`d`, `pitch`, `length`, `tolerance`, `clearance`, `material`).
3. Geometrie gegen Referenztabellen verifizieren.
4. Mechanische Nachweise (mindestens Zug/Scherung, Sicherheitsfaktor) separat rechnen.

Neu im Engineering-Modul:
- Standardabhängige Kerndurchmesserprüfung in der Parametervalidierung (`d3` aus Normdatenbank, fallback 60°-Profil).
- ISO-898-nahe Zugprüfung über `validate_property_class_tensile(...)` mit Festigkeitsklassen (`4.6`, `5.8`, `8.8`, `10.9`, `12.9`).
- Kernquerschnittsauswertung via `estimate_core_area_from_standard(...)` für reproduzierbare Spannungsabschätzung.
- Normbindungs-Check via `validate_norm_binding(...)` (inkl. ISO-Referenz für metrische Gewinde und Toleranzklassenprüfung 6g/6H).
- Optionaler Euler-Knickcheck via `validate_buckling(...)` auf Basis des Kerndurchmessers.
- Integrierte ISO-Regelgewinde-Normtabelle (`M1`–`M64`) für reproduzierbare Nennwerte inkl. Crest-/Kerbradius-Parametern.
- Ergänzter Flankentragfähigkeitscheck via `validate_thread_engagement_strength(...)` (Scher-/Abstreifnäherung mit Sicherheitsfaktor).
- Nicht-blockierende Engineering-Hinweise via `collect_validation_warnings(...)` für kritische Eingabe-Kombinationen.
- High-Level-Python-API via `api.thread("M10", fit="6g/6H", material="8.8", length=50)` für CAD-nahe Aufrufe.

### Engineering-Level-Checkliste (verbindlich)
- **Ziel:** Parametrische Gewindestange (Außengewinde) und zugehörige Innengewinde-Geometrie für CAD/3D-Druck.
- **Normbezug:** Primär `DIN 13 / ISO 68-1` (metrisch), zusätzlich `ANSI/ASME B1.1` (UNC/UNF) und weitere Gewindefamilien.
- **Einheiten:** Interne Geometrieberechnung in **mm**; Zollnormen werden beim Auflösen auf mm umgerechnet.
- **Parameterliste (Mindestumfang):**
  - `d` (Nenndurchmesser, mm)
  - `pitch` (Steigung, mm)
  - `length` (Gewindelänge, mm)
  - `tolerance_class` (z. B. `6g`, `6H`, `2A`, `2B`)
  - `clearance` / Spiel (radiales Zusatzspiel, mm)
- **Normkonformitäts-Status:**
  - ISO-V-Profil für metrische Gewinde mit normnahen Kennwerten (`d2`, `d3`, Crest-/Root-Parameter) implementiert.
  - Kerndurchmesserberechnung (`d3`) je Gewindefamilie in der Normdatenbank hinterlegt.
  - Toleranz- und Spiel-Offsets für Außen-/Innengewinde im Profilgenerator berücksichtigt.
- **Optional unterstützt:**
  - Auswahl unterschiedlicher Familien inkl. **DIN/ISO** und **UNC/UNF**.
  - Material-/Festigkeitsklassen über Presets (z. B. Stahl **8.8**, 10.9, A2, A4).

---

### Projektstruktur
- `__init__.py` – Registrierung, Operatoren, `bl_info`
- `ui_panel.py` – N-Panel und Properties
- `database.py` – Standards, Materialpresets, Pitch-Helfer
- `geometry_engine.py` – 2D-Profilberechnung
- `mesh_builder.py` – Helix-Extrusion, Material, Boolean-Helfer
- `ROADMAP.md` – offener Entwicklungsplan
- `CHANGELOG.md` – Versionshistorie

---

## 🇬🇧 English

### Status
This repository now provides a **functional implementation aligned with work instruction v1.0** (module layout, database, profile generation, mesh builder, UI and operators).

Already implemented:
- Core module layout (`__init__.py`, `database.py`, `geometry_engine.py`, `mesh_builder.py`, `ui_panel.py`)
- Standards/material database with many thread systems
- Profile generation for multiple profile types (V, trapezoid, round, buttress, gothic)
- Helix mesh generation with end caps and basic manifold post-processing
- N-panel UI and custom mode
- Base operators for thread creation and an initial ball-screw entry point
- Dedicated ball-nut operator with internal profile (boolean-based)
- Optional return-path module for ball nuts (simplified geometry)

Roadmap status:
- ✅ v1.0 roadmap fully completed
- v1.1+ remains an optional expansion path (performance, extra dimensional regressions, stress tests)

---

### What is Uni-Threaded-rod?
The **Uni-Threaded-rod** add-on creates parametric thread geometry in Blender:
- External threads
- Internal threads via negative/boolean mode
- Multi-start threads
- Ball screw geometry (baseline workflow available)

---

### Installation (Blender Add-on)
1. Package this repository as a ZIP (or keep as a local addon folder).
2. Open Blender → **Edit > Preferences > Add-ons**.
3. Click **Install...** and select ZIP/folder.
4. Enable the add-on: **Uni-threaded-rod**.
5. In 3D Viewport: **Sidebar (N) > Uni-threaded-rod**.

---

### Basic usage
1. Choose a standard (e.g., METRIC_ISO).
2. Set diameter and length.
3. Optionally configure tolerance, clearance, handedness, and end type.
4. Choose material.
5. Click **Gewinde erstellen** (Create thread).

For free/custom parameters:
1. Switch standard to **CUSTOM**.
2. Set `custom_diameter`, `custom_pitch`, `custom_profile_type`, `custom_starts`.
3. Create thread.

---

### Project structure
- `__init__.py` – registration, operators, `bl_info`
- `ui_panel.py` – N-panel and properties
- `database.py` – standards, material presets, pitch helper
- `geometry_engine.py` – 2D profile generation
- `mesh_builder.py` – helix extrusion, material, boolean helpers
- `ROADMAP.md` – open development roadmap
- `CHANGELOG.md` – release history

### Engineering and standards note
This add-on is intended for **parametric CAD geometry generation** and is not a complete engineering verifier:
- No automatic structural strength verification.
- No complete tolerance-chain verification for manufacturing.
- Real projects still require explicit load cases, material selection, safety factors, and standard-specific checks.
