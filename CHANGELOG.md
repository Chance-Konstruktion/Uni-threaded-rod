# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added
- Neues Modul `mechanical_validation.py` für mechanische Validierung (Zug-/Scherungsberechnung, Sicherheitsfaktor, Mutter-Passung, Pitch-Abgleich, FEM-Hinweis).
- Unit-Tests für mechanische Validierung und Parametervalidierung (`tests/test_mechanical_validation.py`).

### Changed
- Operator-Parametervalidierung in `__init__.py` über separates Validierungsmodul gekapselt (SRP-orientierte Trennung).

## [1.0.0] - 2026-04-22

### Added
- Core add-on module structure for Blender integration (`__init__.py`, `ui_panel.py`, `database.py`, `geometry_engine.py`, `mesh_builder.py`).
- Standards and material preset database with support for multiple thread systems.
- Profile generation support for V, trapezoid, round, buttress, and gothic profile families.
- Helix-based mesh generation, end caps, and manifold-focused postprocessing utilities.
- UI workflow for standard-driven and custom thread definitions.
- Base operators for thread creation, including internal/negative workflows.
- Ball-screw baseline workflow including dedicated ball-nut operator and optional return-path module.
- Preset support and LOD/adaptive segmentation options.
- Automated unit and regression tests plus headless Blender smoke-test script.

### Changed
- Project roadmap marked as complete for v1.0, with remaining items moved to optional v1.1+ backlog.
- README status sections (DE/EN) aligned to final v1.0 completion state.

### Notes
- This release represents the first finalized roadmap milestone (v1.0).
- Future work remains optional and is tracked as v1.1+ backlog items.
