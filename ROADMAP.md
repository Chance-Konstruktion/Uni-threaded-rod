# Uni-threaded Roadmap — Rod + Sleeve

**Audit baseline:** 2026-10-26  
**Status:** Two separate Blender add-ons with a runtime dependency. This is the shared roadmap for API compatibility, geometry, quality gates, and coordinated releases.

- Core engine: [Uni-threaded-rod](https://github.com/Chance-Konstruktion/Uni-threaded-rod)
- Dependent add-on: [Uni-threaded-sleeve](https://github.com/Chance-Konstruktion/Uni-threaded-sleeve)
- Sleeve-specific work: [Uni-threaded-sleeve/ROADMAP.md](https://github.com/Chance-Konstruktion/Uni-threaded-sleeve/blob/main/ROADMAP.md)

## Responsibilities and shared contract

**Rod owns** the canonical thread-standard database, token resolution, profile generation, tolerance defaults, mechanical validation, and solid external-thread mesh builder.

**Sleeve owns** the outer sleeve body, presets, internal-thread cutting, flange geometry, and Blender integration that consumes Rod.

Rules for both repositories:

1. Rod is the single source of truth for standard keys, nominal dimensions, pitch, profile formulas, and tolerance defaults. Sleeve must use the Rod database forwarder rather than maintain a second copy.
2. Public dimensions and pitch are in millimetres. Conversion to Blender metres happens only at the mesh boundary.
3. Rod's high-level thread API with internal=True remains a supported integration path for Sleeve. Changes to its signature, return values, tolerance resolution, standards data, or mesh builder require a real-Rod Sleeve integration run.
4. Returned API data must be self-consistent: pitch, generated profile, dimensions, and mechanics must describe the same geometry, including when a custom pitch override is used.
5. Errors caused by a missing or incompatible Rod add-on must be actionable. Empty standards or fallback UI entries must not silently disguise a broken dependency during object creation.
6. A standard being present in the database is not proof of certified dimensional compliance. Approximate/proprietary profiles—especially PET bottle and closure finishes—must remain labelled as modelling approximations.

## Audit baseline and verification gap

The latest visible successful GitHub Actions runs on both main branches are dated **2026-07-15**. This audit is dated 2026-10-26, so those results are useful history but do not prove the current state is still green. New code changes must trigger fresh CI; use the results of those runs as the verification baseline.

Rod CI currently uses Python 3.11. Sleeve unit tests cover Python 3.10, 3.11, and 3.12, plus real-Rod integration and a Blender smoke test. Decide and document the intended support matrix rather than letting this difference be accidental.

## Prioritized roadmap

### P0 — Release blockers and geometry correctness

- [x] **SLEEVE-001 — Flange bore regression.** Fuse flange geometry into one watertight outer body before running the internal-thread Boolean. Test no-flange and both-sided-flange cases in headless Blender; assert an open bore through both flange regions and manifold output.
- [ ] **SLEEVE-002 — Validate public API calls.** Reject non-finite or non-positive length, diameter, wall thickness, invalid starts, negative clearance, and non-positive resulting dimensions in the Sleeve API/builders. Do not rely on UI property ranges as the only validation.
- [ ] **CI-001 — Refresh the test baseline.** Confirm fresh Rod lint, unit, and headless Blender checks plus Sleeve unit, real-Rod integration, and headless Blender checks on the same Rod commit. Do not mark a release ready based on July 2026 results.
- [ ] **GEOM-001 — No silent degraded mesh.** Ensure failed Boolean operations or invalid profile parameters cancel cleanly, remove temporary cutter/flange objects, and do not leave partially generated scene objects.

### P1 — Stable Rod ↔ Sleeve API and standards data

- [ ] **API-001 — Pitch override consistency.** When a custom pitch is supplied, regenerate profile points and recompute any derived mechanics/dimension metadata—or explicitly narrow the API contract. No response may combine a custom pitch with a profile or mechanics data from the default pitch.
- [ ] **API-002 — Define compatibility.** Document the supported Rod API/version contract and check required capabilities when Sleeve loads. Add a clear diagnostic for an older or incompatible Rod installation.
- [ ] **DB-001 — Standard-by-standard contract tests.** For each available standard, check token resolution, positive finite pitch/diameter, non-degenerate profile, and a representative internal cutter. Keep reference-dimension tests for standards with published exact values.
- [ ] **DB-002 — Data provenance and duplicate audit.** Record source/edition and confidence for dimension maps and formulas; review similar keys such as PG and CONDUIT_PG. Distinguish normative data from aliases or simplified modelling values.
- [ ] **TOL-001 — Tolerance semantics.** Audit internal vs. external classes and radial-offset conventions against standard definitions. Do not present a generic offset map as a complete tolerance implementation.

### P2 — Mesh robustness, packaging, and usability

- [ ] **MESH-001 — Geometry regression matrix.** Cover metric V, 55-degree V, trapezoidal, round, buttress, and tapered profiles; multi-start and left-hand threads; representative end conditions; bounds, volume, and manifold checks.
- [ ] **MESH-002 — Taper validation.** Verify NPT/PIPE_R/BSPT taper dimensions at multiple axial stations against published reference values, not only that the start is larger than the end.
- [ ] **PACK-001 — Reproducible packaging.** Validate installation from the exact ZIP/folder layout Blender users receive, including hyphenated folder names and missing-dependency diagnostics.
- [ ] **DOC-001 — Installation and API examples.** Keep README, changelog, version metadata, supported-standard table, and actual API signatures synchronized. Explicitly label non-certified bottle/closure profiles.
- [ ] **REL-001 — Coordinated releases.** Keep independent versions but publish a compatibility note for each Sleeve release naming the Rod API/revision tested. A Rod release that changes the public contract must run Sleeve integration before release.

## Change protocol

1. A Rod change to standards, profile generation, tolerance logic, API return values, or mesh-builder behaviour must include Rod regression tests and a Sleeve real-engine integration run.
2. Sleeve geometry changes must include unit tests and headless Blender checks for both ordinary and flange presets.
3. Keep bug fixes, tests, and roadmap updates focused; do not combine unrelated refactors.
4. Before release, run:
   - Rod: ruff check ., python -m unittest discover -s tests -p "test_*.py", and blender -b --factory-startup --python scripts/blender_smoke_test.py.
   - Sleeve: compile-check the add-on modules, run python -m unittest discover -s tests -v with UNI_THREADED_ROD_PATH set, and run the Blender smoke script with the same Rod path.
5. Update this file and the Sleeve-specific roadmap when priorities, dependency contract, or acceptance criteria change.
