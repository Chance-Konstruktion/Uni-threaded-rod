# ROADMAP – Universal Thread Generator (UTG)

## Zielbild
Normnahe, robuste und workflow-taugliche Gewindeerzeugung in Blender für Außengewinde, Innengewinde und Kugelgewindetriebe.

## Phase 1 – Fundament stabilisieren (kurzfristig)
- [ ] Einheitliche Einheiten-/Konvertierungslogik für inch/mm und symbolische Nenngrößen
- [ ] Fehlerbehandlung für Standards mit String-Durchmessern (z. B. G, NPT, PG, Edison)
- [ ] Konsistente Nutzung von `tolerance_class` in Geometrieformeln
- [ ] Verbesserte Parameter-Validierung (z. B. Pitch/Diameter/Length/Starts)

## Phase 2 – Geometriequalität (kurz- bis mittelfristig)
- [ ] Normtreue Profilparameter je Standard (Flanken, Kopf-/Fußrundung, Abflachungen)
- [ ] Taper-Logik für NPT über Länge korrekt einarbeiten
- [ ] Endtypen vollständig umsetzen (`FLAT`, `CHAMFER`, `RUNOUT` mit echter Geometrie)
- [ ] Strategien gegen Self-Intersection und zu dünne Kernradien

## Phase 3 – Manifold- und Boolean-Robustheit
- [ ] Expliziter Non-Manifold-Check nach Erzeugung
- [ ] Automatische Reparaturpfade (Lochfüllung, Brückenkanten, lokale Neuvernetzung)
- [ ] Stabilerer Boolean-Workflow inkl. Selektion/Aktivobjekt-Schutz

## Phase 4 – Kugelgewindetrieb (KGT)
- [ ] Echte GOTHIC-Profilkette nach DIN 69051 / ISO 3408 (annähernd)
- [ ] Muttergeometrie mit Innenprofil
- [ ] Kugelrückführung als optionales Modul
- [ ] Separate Operatoren und UI für KGT-Komponenten

## Phase 5 – UX & Performance
- [ ] Dynamische UI-Optionen pro Standard (nur gültige Felder anzeigen)
- [ ] Preset-System (z. B. "M10x1.5 8.8 verzinkt")
- [ ] Performance-Tuning für lange Gewinde und hohe Segmentierung
- [ ] Optionale LOD-Stufen (Preview/Final)

## Phase 6 – Qualitätssicherung
- [ ] Blender-API Runtime-Tests (Headless)
- [ ] Referenzvergleich zu Sollmaßen pro Standard
- [ ] Regressionstests für Boolean/Manifold-Fälle
- [ ] CI-Workflow (Lint + Unit + Blender smoke test)

## Definition of Done (v1.0)
- [ ] Alle Kernstandards mit plausiblen Normmaßen erzeugbar
- [ ] Innen-/Außengewinde robust und manifold in typischen Parameterräumen
- [ ] KGT-Basisworkflow nutzbar
- [ ] Dokumentation (DE/EN), Beispiele und bekannte Einschränkungen klar beschrieben
