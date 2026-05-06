# Uni-Threaded-rod for Blender

Parametrische Gewindegeometrie für Blender: Außengewinde, Innengewinde/Boolean-Cutter, mehrgängige Gewinde und ein normnaher Kugelgewindetrieb-Basisworkflow.

Parametric thread geometry for Blender: external threads, internal/boolean-cutter workflows, multi-start threads, and a standards-aligned baseline ball-screw workflow.

## Inhalt / Contents
- [Kurzfassung / Executive Summary](#kurzfassung--executive-summary)
- [Installation](#installation-blender-add-on)
- [Grundbedienung / Basic usage](#grundbedienung--basic-usage)
- [Features](#features)
- [Qualitätssicherung / Testing](#qualitätssicherung--testing)
- [Engineering- und Normhinweis / Engineering and standards note](#engineering--und-normhinweis--engineering-and-standards-note)
- [Projektstruktur / Project structure](#projektstruktur--project-structure)
- [Release-Hinweis / Release notes](#release-hinweis--release-notes)

---

## Kurzfassung / Executive Summary

### 🇩🇪 Deutsch
**Uni-Threaded-rod** ist ein Blender-Add-on zur parametrischen Gewindeerzeugung für Außen- und Innengewinde sowie einen KGT-Basisworkflow.

**Kernfunktionen**
- Parametrische Erzeugung von Außengewinden, Innengewinden im Negativ-/Boolean-Workflow und mehrgängigen Gewinden
- Unterstützte Profilfamilien: V, Trapez, Rund, Buttress, Gothic
- Presets, LOD-Stufen (Preview/Final/Custom) und adaptive Segmentierung
- NPT-Taper entlang der Gewindelänge
- Engineering-Helfer für Normbindung, Material-/Festigkeitsklassen, Kernquerschnitt, Zug-/Scherungs-, Knick- und Plausibilitätschecks
- High-Level-Python-API für CAD-nahe Aufrufe, z. B. `api.thread("M10", fit="6g/6H", material="8.8", length=50)`

**Hinweis**
Das Add-on erzeugt CAD-Geometrie normnah, ersetzt aber keine vollständige technische Auslegung.

### 🇬🇧 English
**Uni-Threaded-rod** is a Blender add-on for parametric thread generation covering external threads, internal thread cutter workflows, and a baseline ball-screw workflow.

**Core features**
- Parametric creation of external threads, internal threads via negative/boolean workflows, and multi-start threads
- Supported profile families: V, trapezoid, round, buttress, gothic
- Presets, LOD levels (Preview/Final/Custom), and adaptive segmentation
- NPT taper along the threaded length
- Engineering helpers for standard binding, material/property classes, core area, tensile/shear, buckling, and plausibility checks
- High-level Python API for CAD-oriented calls, e.g. `api.thread("M10", fit="6g/6H", material="8.8", length=50)`

**Note**
The add-on targets standards-aligned CAD geometry generation and does not replace full engineering verification.

---

## Status

### 🇩🇪 Deutsch
Dieses Repository enthält eine **funktionsfähige Implementierung gemäß v1.0** inklusive Modulstruktur, Datenbank, Profilgenerator, Mesh-Builder, UI, Operatoren und automatisierter Tests. Die v1.1-Engineering-Erweiterungen sind ebenfalls im Code dokumentiert und teilweise bereits umgesetzt.

Bereits umgesetzt:
- Modulstruktur mit `__init__.py`, `database.py`, `geometry_engine.py`, `mesh_builder.py`, `ui_panel.py`
- Norm-/Materialdatenbank mit vielen Standards
- Profilgenerator für mehrere Profiltypen (V, Trapez, Rund, Buttress, Gothic)
- Helix-Mesh-Erzeugung inkl. Endkappen und Basis-Manifold-Postprocessing
- N-Panel UI inkl. Custom-Mode, Presets, LOD-Stufen und adaptiver Segmentierung
- Basis-Operatoren für Gewinde und einfachen KGT-Startpunkt
- Eigenständiger KGT-Mutter-Operator mit Innenprofil (Boolean-basiert)
- Optionales Rückführungsmodul für KGT-Mutter (vereinfachte Geometrie)
- NPT-Taper entlang der Gewindelänge
- Mechanische Validierung in `mechanical_validation.py`

Roadmap-Status:
- ✅ v1.0-Roadmap vollständig abgeschlossen
- ✅ v1.1-Engineering-Bausteine weitgehend integriert
- 🟡 v1.2-Bilingual-Workflow teilweise umgesetzt; exportierbare Reports bleiben optionaler Ausbaupfad

### 🇬🇧 English
This repository provides a **functional v1.0 implementation** including module layout, database, profile generation, mesh builder, UI, operators, and automated tests. The v1.1 engineering extensions are also documented and partially implemented in the codebase.

Already implemented:
- Core module layout (`__init__.py`, `database.py`, `geometry_engine.py`, `mesh_builder.py`, `ui_panel.py`)
- Standards/material database with many thread systems
- Profile generation for multiple profile types (V, trapezoid, round, buttress, gothic)
- Helix mesh generation with end caps and basic manifold post-processing
- N-panel UI including custom mode, presets, LOD levels, and adaptive segmentation
- Base operators for thread creation and an initial ball-screw entry point
- Dedicated ball-nut operator with internal profile (boolean-based)
- Optional return-path module for ball nuts (simplified geometry)
- NPT taper along the threaded length
- Mechanical validation in `mechanical_validation.py`

Roadmap status:
- ✅ v1.0 roadmap fully completed
- ✅ v1.1 engineering building blocks largely integrated
- 🟡 v1.2 bilingual workflow partially implemented; exportable reports remain optional future work

---

## Installation (Blender Add-on)

1. Repository als ZIP verpacken oder den Ordner lokal als Add-on-Ordner bereitstellen.
   Package this repository as a ZIP or keep it as a local add-on folder.
2. Blender öffnen → **Edit > Preferences > Add-ons**.
   Open Blender → **Edit > Preferences > Add-ons**.
3. **Install...** wählen und ZIP/Ordner installieren.
   Click **Install...** and select the ZIP/folder.
4. Add-on aktivieren: **Uni-threaded-rod**.
   Enable the add-on: **Uni-threaded-rod**.
5. Im 3D-Viewport: **Sidebar (N) > Uni-threaded-rod**.
   In the 3D Viewport: **Sidebar (N) > Uni-threaded-rod**.

---

## Grundbedienung / Basic usage

### Standard-Workflow
1. Norm auswählen, z. B. `METRIC_ISO`.
   Choose a standard, e.g. `METRIC_ISO`.
2. Durchmesser und Länge setzen.
   Set diameter and length.
3. Optional Toleranz, Spiel, Drehrichtung, Endtyp, Material und LOD konfigurieren.
   Optionally configure tolerance, clearance, handedness, end type, material, and LOD.
4. **Gewinde erstellen** klicken.
   Click **Gewinde erstellen** (Create thread).

### Custom-Workflow
1. Norm auf **CUSTOM** stellen.
   Switch standard to **CUSTOM**.
2. `custom_diameter`, `custom_pitch`, `custom_profile_type` und `custom_starts` setzen.
   Set `custom_diameter`, `custom_pitch`, `custom_profile_type`, and `custom_starts`.
3. Gewinde erzeugen.
   Create the thread.

### Python-API
```python
from api import thread

spec = thread("M10", fit="6g/6H", material="8.8", length=50)
```

---

## Features

### 🇩🇪 Deutsch
- **Gewindetypen:** Außengewinde, Innengewinde als Boolean-Cutter, Mehrganggewinde, KGT-Basisgeometrie
- **Profilfamilien:** V, Trapez, Rund, Buttress, Gothic
- **Normdaten:** ISO-metrische Regelreihe `M1`–`M64`, UNC/UNF und weitere Gewindefamilien mit mm/inch-Auflösung
- **Geometrie:** Helix-Sweep, Endkappen, optionale Endtypen, NPT-Taper, Manifold-orientiertes Postprocessing
- **UI:** N-Panel, Custom-Mode, Presets, Preview-/Final-/Custom-LOD, adaptive Segmentierung
- **Engineering:** Normbindungscheck, Festigkeitsklassen, Zug-/Scherungs- und Knicknäherungen, nicht-blockierende Warnungen

### 🇬🇧 English
- **Thread types:** external threads, internal threads as boolean cutters, multi-start threads, baseline ball-screw geometry
- **Profile families:** V, trapezoid, round, buttress, gothic
- **Standards data:** ISO metric coarse series `M1`–`M64`, UNC/UNF, and additional thread families with mm/inch resolution
- **Geometry:** helix sweep, end caps, optional end types, NPT taper, manifold-oriented post-processing
- **UI:** N-panel, custom mode, presets, Preview/Final/Custom LOD, adaptive segmentation
- **Engineering:** standard-binding checks, property classes, tensile/shear and buckling approximations, non-blocking warnings

---

## Qualitätssicherung / Testing

- **Schneller Unit-Testlauf ohne Blender / Fast unit tests without Blender:**
  ```bash
  python -m unittest discover -s tests -p 'test_*.py'
  ```
- **Headless Blender-Smoke-Test / Headless Blender smoke test:**
  ```bash
  blender -b --factory-startup --python scripts/blender_smoke_test.py
  ```
- **CI:** GitHub Actions (`.github/workflows/ci.yml`) führt Ruff, Unit-Tests und den Blender-Smoke-Test aus, sofern Blender in der Umgebung verfügbar ist.
  GitHub Actions (`.github/workflows/ci.yml`) runs Ruff, unit tests, and the Blender smoke test when Blender is available in the environment.

Hinweis: Die Unit-Tests in `tests/` sind absichtlich ohne Blender-Laufzeit ausgelegt. Details stehen in `tests/README.md`.

---

## Engineering- und Normhinweis / Engineering and standards note

### 🇩🇪 Deutsch
Dieses Projekt erzeugt primär **CAD-Geometrie**. Es ersetzt keine vollständige technische Auslegung nach Norm:
- Keine vollständige Tragfähigkeits-/Festigkeitsrechnung für reale Lastfälle.
- Keine vollumfängliche Toleranzkettenrechnung für Fertigungsprozesse.
- Für reale Bauteile müssen Einsatzfall, Lastannahmen, Material, Sicherheitsfaktoren und passende Normausgaben projektspezifisch geprüft werden.

Empfohlener Minimal-Workflow für reale Anwendungen:
1. Zielnorm und Gewindefamilie festlegen, z. B. ISO metrisch, UNC/UNF oder Pipe.
2. Parameter eindeutig dokumentieren: `d`, `pitch`, `length`, `tolerance_class`, `clearance`, `material`.
3. Geometrie gegen Referenztabellen verifizieren.
4. Mechanische Nachweise separat rechnen, mindestens Zug, Scherung/Abstreifen und Sicherheitsfaktor.

### 🇬🇧 English
This project primarily generates **CAD geometry**. It does not replace complete standards-based engineering verification:
- It does not provide a complete strength verification for real load cases.
- It does not provide complete tolerance-chain verification for manufacturing processes.
- Real parts still require project-specific use cases, load assumptions, materials, safety factors, and applicable standard editions.

Recommended minimum workflow for real applications:
1. Choose the target standard and thread family, e.g. ISO metric, UNC/UNF, or pipe.
2. Document parameters explicitly: `d`, `pitch`, `length`, `tolerance_class`, `clearance`, `material`.
3. Verify generated geometry against reference tables.
4. Run mechanical verification separately, at minimum tensile, shear/stripping, and safety-factor checks.

---

## Bekannte Einschränkungen / Known limitations

- ISO-Regelgewinde sind für die Grobreihe tabellarisch von **M1 bis M64** hinterlegt; andere Familien bleiben teilweise normnahe Näherungen.
  ISO metric coarse threads are tabulated from **M1 to M64**; some other families remain standards-aligned approximations.
- Die Gothic-Kette für KGT ist verbessert, aber weiterhin eine **annähernde** Auslegung.
  The gothic ball-screw chain is improved but still an **approximate** design.
- Sehr extreme Parameterkombinationen, z. B. sehr hohe Startanzahl, sehr kurze Länge und sehr kleiner Kerndurchmesser, sollten manuell geprüft werden.
  Very extreme parameter combinations, e.g. many starts, very short length, and very small core diameters, should be reviewed manually.
- Blender-Boolean-Workflows können je nach Objektgröße, Segmentierung und Szene zusätzliche Nacharbeit erfordern.
  Blender boolean workflows may require additional cleanup depending on object size, segmentation, and scene state.

---

## Projektstruktur / Project structure

- `__init__.py` – Registrierung, Operatoren, `bl_info` / registration, operators, `bl_info`
- `api.py` – High-Level-Python-API / high-level Python API
- `database.py` – Standards, Materialpresets, Pitch-Helfer / standards, material presets, pitch helpers
- `geometry_engine.py` – 2D-Profilberechnung / 2D profile generation
- `mesh_builder.py` – Helix-Extrusion, Material, Boolean-Helfer / helix extrusion, material, boolean helpers
- `mechanical_validation.py` – Engineering-Validierung / engineering validation
- `ui_panel.py` – N-Panel und Properties / N-panel and properties
- `ui_i18n.py` – UI-Textressourcen / UI text resources
- `scripts/blender_smoke_test.py` – Headless Blender-Smoke-Test / headless Blender smoke test
- `tests/` – Unit- und Regressionstests / unit and regression tests
- `ROADMAP.md` – Entwicklungsplan / development roadmap
- `CHANGELOG.md` – Versionshistorie / release history

---

## Release-Hinweis / Release notes

- Der initiale Abschlussstand ist als **v1.0.0** dokumentiert.
  The initial completed milestone is documented as **v1.0.0**.
- Laufende Änderungen stehen im Abschnitt **Unreleased** des `CHANGELOG.md`.
  Current changes are tracked in the **Unreleased** section of `CHANGELOG.md`.
