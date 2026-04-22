# Uni-threaded-rod for Blender

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

Roadmap-Fokus (v1.1+):
- Performance-Optimierung für sehr lange Gewinde
- Erweiterte KGT-Features (Mutter/Rückführung)
- Zusätzliche automatisierte Blender-Regressionstests

---

### Was ist UTG?
Der **Universal Thread Generator** erstellt parametrisierte Gewindegeometrie in Blender:
- Außengewinde
- Innengewinde via Negativ-/Boolean-Modus
- Mehrgängige Gewinde
- (In Entwicklung) Kugelgewindetriebe

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

### Projektstruktur
- `__init__.py` – Registrierung, Operatoren, `bl_info`
- `ui_panel.py` – N-Panel und Properties
- `database.py` – Standards, Materialpresets, Pitch-Helfer
- `geometry_engine.py` – 2D-Profilberechnung
- `mesh_builder.py` – Helix-Extrusion, Material, Boolean-Helfer
- `ROADMAP.md` – offener Entwicklungsplan

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

Roadmap focus (v1.1+):
- Performance tuning for very long threads
- Extended ball-screw features (nut/return path)
- Additional automated Blender regression tests

---

### What is UTG?
The **Universal Thread Generator** creates parametric thread geometry in Blender:
- External threads
- Internal threads via negative/boolean mode
- Multi-start threads
- (In progress) ball screw geometry

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
