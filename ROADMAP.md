# ROADMAP – Universal Thread Generator (UTG)

## Zielbild
Normnahe, robuste und workflow-taugliche Gewindeerzeugung in Blender für Außengewinde, Innengewinde und Kugelgewindetriebe.

## Status-Update (2026-04-22)
Systematische Durchsicht der Punkte gegen aktuellen Code-Stand:
- ✅ **Erledigt**: technisch vorhanden und im Add-on nutzbar
- 🟡 **Teilweise**: Grundfunktion vorhanden, aber noch nicht norm- oder workflow-vollständig
- ⬜ **Offen**: noch nicht umgesetzt

## Phase 1 – Fundament stabilisieren (kurzfristig)
- [x] Einheitliche Einheiten-/Konvertierungslogik für inch/mm und symbolische Nenngrößen ✅
- [x] Fehlerbehandlung für Standards mit String-Durchmessern (z. B. G, NPT, PG, Edison) ✅
- [x] Konsistente Nutzung von `tolerance_class` in Geometrieformeln ✅
- [x] Verbesserte Parameter-Validierung (z. B. Pitch/Diameter/Length/Starts) ✅

## Phase 2 – Geometriequalität (kurz- bis mittelfristig)
- [ ] Normtreue Profilparameter je Standard (Flanken, Kopf-/Fußrundung, Abflachungen) 🟡
- [x] Taper-Logik für NPT über Länge korrekt einarbeiten ✅
- [x] Endtypen vollständig umsetzen (`FLAT`, `CHAMFER`, `RUNOUT` mit echter Geometrie) ✅
- [x] Strategien gegen Self-Intersection und zu dünne Kernradien ✅

## Phase 3 – Manifold- und Boolean-Robustheit
- [x] Expliziter Non-Manifold-Check nach Erzeugung ✅
- [x] Automatische Reparaturpfade (Lochfüllung, Brückenkanten, lokale Neuvernetzung) 🟡
- [x] Stabilerer Boolean-Workflow inkl. Selektion/Aktivobjekt-Schutz 🟡

## Phase 4 – Kugelgewindetrieb (KGT)
- [ ] Echte GOTHIC-Profilkette nach DIN 69051 / ISO 3408 (annähernd) 🟡
- [x] Muttergeometrie mit Innenprofil ✅
- [x] Kugelrückführung als optionales Modul ✅
- [x] Separate Operatoren und UI für KGT-Komponenten 🟡

## Phase 5 – UX & Performance
- [x] Dynamische UI-Optionen pro Standard (nur gültige Felder anzeigen)
- [x] Preset-System (z. B. "M10x1.5 8.8 verzinkt")
- [x] Performance-Tuning für lange Gewinde und hohe Segmentierung
- [x] Optionale LOD-Stufen (Preview/Final)

## Phase 6 – Qualitätssicherung
- [ ] Blender-API Runtime-Tests (Headless)
- [ ] Referenzvergleich zu Sollmaßen pro Standard
- [ ] Regressionstests für Boolean/Manifold-Fälle
- [ ] CI-Workflow (Lint + Unit + Blender smoke test)

## Definition of Done (v1.0)
- [ ] Alle Kernstandards mit plausiblen Normmaßen erzeugbar 🟡
- [ ] Innen-/Außengewinde robust und manifold in typischen Parameterräumen 🟡
- [x] KGT-Basisworkflow nutzbar ✅
- [ ] Dokumentation (DE/EN), Beispiele und bekannte Einschränkungen klar beschrieben 🟡

## Nächste priorisierte Arbeitspakete
1. Profilparameter pro Standard weiter normtreu differenzieren (insb. Rundungen/Abflachungen).
2. Echte GOTHIC-Profilkette stärker normnah ausarbeiten (DIN 69051 / ISO 3408).
3. Blender-API Runtime-Tests (Headless) und CI-Smoke-Tests ergänzen.
4. Referenzvergleich gegen Sollmaße (Regressionstest-Suite) implementieren.
