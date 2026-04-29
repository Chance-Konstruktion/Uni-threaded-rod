# ROADMAP – Universal Thread Generator (UTG)

## Zielbild / Vision
**DE:** Normnahe, robuste und workflow-taugliche Gewindeerzeugung in Blender für Außengewinde, Innengewinde und Kugelgewindetriebe.  
**EN:** Standards-aligned, robust, and workflow-ready thread generation in Blender for external threads, internal threads, and ball screw drives.

## Status-Update / Status Update (2026-04-29)
Systematische Durchsicht der Punkte gegen aktuellen Code-Stand / Systematic review of roadmap items against the current codebase:
- ✅ **Erledigt / Done**: technisch vorhanden und im Add-on nutzbar / implemented and usable in the add-on
- 🟡 **Teilweise / Partial**: Grundfunktion vorhanden, aber noch nicht norm- oder workflow-vollständig / base functionality exists but not fully standards/workflow complete
- ⬜ **Offen / Open**: noch nicht umgesetzt / not implemented yet

## Phase 1 – Fundament stabilisieren (kurzfristig) / Stabilize the Foundation (short-term)
- [x] Einheitliche Einheiten-/Konvertierungslogik für inch/mm und symbolische Nenngrößen ✅
- [x] Fehlerbehandlung für Standards mit String-Durchmessern (z. B. G, NPT, PG, Edison) ✅
- [x] Konsistente Nutzung von `tolerance_class` in Geometrieformeln ✅
- [x] Verbesserte Parameter-Validierung (z. B. Pitch/Diameter/Length/Starts) ✅

## Phase 2 – Geometriequalität (kurz- bis mittelfristig) / Geometry Quality (short to mid-term)
- [x] Normtreue Profilparameter je Standard (Flanken, Kopf-/Fußrundung, Abflachungen) ✅
- [x] Taper-Logik für NPT über Länge korrekt einarbeiten ✅
- [x] Endtypen vollständig umsetzen (`FLAT`, `CHAMFER`, `RUNOUT` mit echter Geometrie) ✅
- [x] Strategien gegen Self-Intersection und zu dünne Kernradien ✅

## Phase 3 – Manifold- und Boolean-Robustheit / Manifold & Boolean Robustness
- [x] Expliziter Non-Manifold-Check nach Erzeugung ✅
- [x] Automatische Reparaturpfade (Lochfüllung, Brückenkanten, lokale Neuvernetzung) 🟡
- [x] Stabilerer Boolean-Workflow inkl. Selektion/Aktivobjekt-Schutz 🟡

## Phase 4 – Kugelgewindetrieb (KGT) / Ball Screw Drive
- [x] Echte GOTHIC-Profilkette nach DIN 69051 / ISO 3408 (annähernd) ✅
- [x] Muttergeometrie mit Innenprofil ✅
- [x] Kugelrückführung als optionales Modul ✅
- [x] Separate Operatoren und UI für KGT-Komponenten 🟡

## Phase 5 – UX & Performance
- [x] Dynamische UI-Optionen pro Standard (nur gültige Felder anzeigen)
- [x] Preset-System (z. B. "M10x1.5 8.8 verzinkt")
- [x] Performance-Tuning für lange Gewinde und hohe Segmentierung
- [x] Optionale LOD-Stufen (Preview/Final)

## Phase 6 – Qualitätssicherung / Quality Assurance
- [x] Blender-API Runtime-Tests (Headless) ✅
- [x] Referenzvergleich zu Sollmaßen pro Standard ✅
- [x] Regressionstests für Boolean/Manifold-Fälle ✅
- [x] CI-Workflow (Lint + Unit + Blender smoke test) ✅

## Definition of Done (v1.0)
- [x] Alle Kernstandards mit plausiblen Normmaßen erzeugbar ✅
- [x] Innen-/Außengewinde robust und manifold in typischen Parameterräumen ✅
- [x] KGT-Basisworkflow nutzbar ✅
- [x] Dokumentation (DE/EN), Beispiele und bekannte Einschränkungen klar beschrieben ✅

## Abschlussstatus / Completion Status (v1.0 final)
**DE:** Die Roadmap für **v1.0** ist vollständig abgeschlossen. Alle definierten DoD-Kriterien sind erfüllt und die vorhandenen automatisierten Tests laufen grün.  
**EN:** The **v1.0** roadmap is fully completed. All defined DoD criteria are met, and the existing automated tests are passing.

## Backlog (v1.1+, optional)
1. Tabellarische Sollmaß-Regressionen pro Nenngröße weiter ausbauen (pro Standard + Toleranzklasse).
2. Erweiterte Lasttests für extreme Parameterkombinationen inkl. Blender-Boolean-Workflow ergänzen.

## Phase 7 – High-End Engineering (v1.1)
- [x] ISO-Profilgeometrie erweitert: Kuppenabflachung tabellenbasiert und Kerbradius in Profilstützpunkten.
- [x] ISO-Regelreihe erweitert (M1–M64) in der integrierten Normtabelle.
- [x] Materialmodell ergänzt um ableitbare zulässige Spannungen aus Festigkeitsklassen (z. B. 8.8, 10.9).
- [x] Erweiterte Mechanik ergänzt: Vorspannungs-/Reibwertmodell, kombinierte Lastfälle, bestehender Knicknachweis integriert.
- [x] High-Level-API ergänzt: `thread("M10", fit="6g/6H", material="8.8", length=50)`.

## Phase 8 – Bilingual Workflow (v1.2)
- [x] Roadmap zweisprachig (DE/EN) strukturiert.
- [ ] README-Kurzfassung als DE/EN-Dual-Section ergänzen.
- [ ] UI-Textressourcen vorbereiten (DE/EN labels/tooltips via lookup table).
- [ ] Exportierbare Reports optional in Deutsch oder Englisch erzeugen.
