# Arbeitsanweisung für ChatGPT Codex — Uni-threaded-rod

Diese Datei ist die zentrale Auftragsliste für alle weiteren ChatGPT-Codex-Sessions
in diesem Repository. Sie wurde nach einem vollständigen Code- und Test-Review erstellt.
Bearbeite die Tasks in der angegebenen Reihenfolge (P0 → P3). Nach jedem Task:
`python -m unittest discover -s tests -p "test_*.py"` muss grün bleiben und
`ruff check .` darf keine neuen Findings melden.

---

## 0. Projekt-Kontext (Pflichtlektüre vor Start)

- Blender-Add-on (Blender ≥ 4.0) für parametrische Erzeugung von **Außengewinde-Vollstangen**.
- Der Negativ-/Innengewinde-Cutter-Modus wurde bewusst entfernt (Commit `5119d9a`).
  `apply_boolean_cutter` ist nur noch als API-Hilfe vorhanden, keine UI nutzt es.
- Stack: reines Python, Blender-API (`bpy`, `bmesh`, `mathutils`), keine externen Deps.
- Tests laufen **ohne Blender** über stub-Imports — die Tests stubben `bpy`/`bmesh`/`mathutils`.
- CI: GitHub Actions (`.github/workflows/ci.yml`) führt `ruff` + `unittest` + headless
  `blender --python scripts/blender_smoke_test.py` aus.
- Die Files im Repo-Root sind das Add-on selbst — `__init__.py` ist der Blender-Entry-Point
  mit `bl_info`. Lass diese Struktur unverändert.

---

## 1. Ist-Stand nach Abschluss (16.05.2026)

### Test-Lauf
```
Ran 74 tests — OK
ruff check . — All checks passed!
```
Alles grün; die Coverage-Lücken aus P1.1 sind mit Regressionstests geschlossen.

### ✅ Release 0.2 Vorbereitung (16.05.2026)
- `bl_info["version"]` ist auf `(0, 2, 0)` gesetzt.
- README beschreibt den aktuellen Scope ohne entfernte Innengewinde-Cutter-UI.
- `validate_thread_input(..., standard_key="NOT_A_STANDARD")` liefert einen sprechenden Validierungsfehler statt einer stillen metrischen Ersatzformel.


### ✅ Implementierte Normen (26 von 26 versprochenen)
`ACME`, `BSF`, `BSPT`, `BUTTRESS`, `CABLE_GLAND_M`, `CONDUIT_PG`, `EDISON`,
`KNUCKLE`, `LAMP_B`, `METRIC_FINE`, `METRIC_ISO`, `METRIC_TRAPEZOIDAL_FINE`,
`NPT`, `PG`, `PIPE_G`, `PIPE_R`, `ROUND`, `SPARK_PLUG`, `STORZ`,
`STUB_ACME`, `TRAPEZOIDAL`, `UNC`, `UNEF`, `UNF`, `UNS`, `WHITWORTH_BSW`.

### ✅ Ehemals fehlende README-Normen (9 von 9 erledigt)
| Key | Name | Norm | Einheit | Profil |
| --- | --- | --- | --- | --- |
| `BSF` | British Standard Fine | BS 84 | inch | V (55°) |
| `UNS` | Unified National Special | ANSI/ASME B1.1 | inch | V (60°) |
| `METRIC_TRAPEZOIDAL_FINE` | Metrisches Feintrapezgewinde | DIN 380 | mm | Trapezoid (30°) |
| `STUB_ACME` | Stub ACME | ASME B1.8 | inch | Trapezoid (29°, halbe Höhe) |
| `KNUCKLE` | Knuckle thread | ASME B1.9 | inch | Round |
| `SPARK_PLUG` | Zündkerzengewinde | ISO 28741 | mm | V |
| `CABLE_GLAND_M` | Kabelverschraubung, metrisch | DIN EN 60423 / IEC 60423 | mm | V |
| `CONDUIT_PG` | Panzergewinde Elektroinstallation | DIN 40430 | mm | V |
| `LAMP_B` | Bayonett-Lampensockel (B15/B22 …) | IEC 60061-1 | mm | Round (Bajonett) |

---

## 2. Aufgaben — Priorisiert

### P0 — Kritische Bugs (vor allem anderen fixen)

#### ✅ P0.1 STORZ-Pipeline-Bug
**Problem:** `STORZ`-Einträge haben `pitch=0` im `diam_pitch_map`. Beim Aufruf von
`generate_profile("STORZ", …)` schlägt `_check_profile_inputs` mit
`"Steigung (Pitch) muss > 0 sein"` fehl, **bevor** der `BAYONET`-NotImplementedError
greifen kann. Dadurch ist STORZ in API + UI komplett tot, obwohl es im UI-Enum auswählbar ist.

**Akzeptanzkriterien:**
- `generate_profile("STORZ", 133.0, 0.0)` darf nicht mit unverständlichem `ValueError`
  enden, sondern mit klarem `NotImplementedError("STORZ: Bajonett-/Knaggenkupplung …")`.
- `_check_profile_inputs` muss `BAYONET`-Profile vor der Pitch-Validierung abfangen
  ODER STORZ wird aus dem UI-Enum ausgeblendet, bis eine echte Pipeline existiert.
- Operator `UTG_OT_create_thread` muss einen verständlichen User-Report
  (`{"ERROR"}`) liefern, wenn STORZ gewählt wurde.
- Neuer Test in `tests/test_regression_dimensions.py`:
  `test_storz_raises_not_implemented_with_clear_message`.

#### ✅ P0.2 Toter `N_A`-Branch in `__init__.py:112`
**Problem:** `__init__.py` prüft `props.tolerance_class == "N_A"`, aber `N_A` ist
in `ui_panel.py` nirgends als gültiger Enum-Wert definiert. Der Branch ist unerreichbar.

**Akzeptanzkriterien:**
- Entweder Branch ersatzlos entfernen, ODER `get_tolerance_items` so erweitern,
  dass `("N_A", "—", "Keine Toleranzklasse definiert")` zurückkommt, wenn die
  Norm gar keine `tolerance_classes` hinterlegt hat. Empfehlung: **Branch entfernen**,
  weil `get_tolerance_items` heute schon einen `("6g", "6g", "Standard")`-Fallback liefert.
- Test ergänzen, der bestätigt, dass Standards ohne `tolerance_classes`
  (`BUTTRESS`, `ROUND`, `NPT`, `PG`, `EDISON`, `STORZ`) im UI keine Tolerance-Selektion
  zeigen oder eine sinnvolle Default-Option bekommen.

#### ✅ P0.3 `api.thread(material=…)` widersprüchlich zur UI
**Problem:** `api.thread()` erwartet eine **ISO-898-Festigkeitsklasse** als String
(`"4.6"`, `"8.8"`, …), aber `ui_panel.UTG_Properties.material` verwendet die
**MATERIAL_PRESETS-Keys** (`"STEEL_8.8"`, `"STAINLESS_A2"`, …). Wer die API mit
einem UI-Wert füttert, bekommt `ValueError: Unbekannte Festigkeitsklasse: STEEL_8.8`.

**Akzeptanzkriterien:**
- `api.thread()` akzeptiert beide Schreibweisen. Mapping in einer Hilfsfunktion
  `_resolve_property_class(material_or_preset)` zentralisieren:
  - direkter Match in `ISO_898_PROPERTY_CLASS_RM_MPA` → übernehmen
  - sonst `MATERIAL_PRESETS`-Key wie `"STEEL_8.8"` → Suffix nach `_` als Klasse
  - sonst klarer `ValueError` mit Liste der erlaubten Werte
- Erweitere `tests/test_mechanical_validation.py::HighEndMechanicsTests` um
  `test_high_level_thread_api_accepts_ui_material_keys`.

#### ✅ P0.4 Unbekannter Standard → KeyError
**Problem:** `api.thread(spec="M10", standard="NOT_A_STANDARD")` wirft einen
nackten `KeyError`, statt wie `geometry_engine` einen sprechenden `ValueError`.

**Akzeptanzkriterien:**
- `database.resolve_thread_parameters` muss `ValueError(f"Unbekannter Standard: {standard_key}")`
  werfen, wenn der Key nicht in `THREAD_STANDARDS` ist.
- Test ergänzen.

---

### ✅ P1 — Fehlende Gewindearten (Hauptauftrag laut User)

Implementiere alle 9 fehlenden Normen in `database.py::THREAD_STANDARDS`. Halte dich
strikt an die in der bestehenden Tabelle genutzte Struktur. Jeder Eintrag braucht
mindestens: `name`, `standard`, `unit`, `flank_angle`, `profile_type`,
`diam_pitch_map`, `d2_formula`, `d3_formula`, `tensile_stress_area_formula`,
`tolerance_classes` (sofern Norm vorsieht), ggf. `diam_nominal_map`, `special_params`.

#### ✅ P1.1 Coverage-Lücken vorhandener Normen mitbeheben
Bevor neue Normen kommen, schließe diese Lücken in den bestehenden Einträgen
(`tensile_stress_area_formula` fehlt komplett):

- `BUTTRESS`, `ROUND`, `ACME`, `NPT`, `PG`, `EDISON`, `STORZ`

`STORZ` braucht keine Stress-Formula (Bajonett, keine Last-Annahme über Gewindeflanke).
Für die anderen: konservative Näherung über Kerndurchmesser `d3`:
`tensile_stress_area_formula = lambda d, p: math.pi * 0.25 * (d3(d,p))**2 / (π/4)`
— effektiv `d - k*p` mit profilabhängigem `k`. Werte aus Normliteratur belegen
und als Kommentar (eine kurze Zeile) hinterlegen.

#### ✅ P1.2 Neue Normen einzeln

**Bei jeder neuen Norm:**
- mindestens 6 typische Nennweiten in `diam_pitch_map`
- `tensile_stress_area_formula` (zumindest konservative Näherung)
- ein `test_core_standards_generate_non_degenerate_profiles`-Eintrag in
  `tests/test_regression_dimensions.py`
- ein Pfad in `tests/test_regression_dimensions.py::HighEndDataCoverageTests`,
  der mindestens einen typischen Nenndurchmesser und die zugehörige Steigung prüft.
- README-Tabelle ist bereits up-to-date; nur prüfen, ob Norm/Bezeichnung passt.

##### ✅ a) `BSF` — British Standard Fine
- `flank_angle: 55.0`, `profile_type: "V"`, `unit: "inch"`
- `diam_pitch_map` (TPI) — typisch: `{3/16: 32, 7/32: 28, 1/4: 26, 5/16: 22, 3/8: 20, 7/16: 18, 1/2: 16, 9/16: 16, 5/8: 14, 11/16: 14, 3/4: 12, 7/8: 11, 1.0: 10, 1.125: 9, 1.25: 9, 1.5: 8, 1.75: 7, 2.0: 7}`
- Formeln wie `WHITWORTH_BSW` (`d2 = d - 0.640327*p`, `d3 = d - 1.280654*p`,
  `tensile = d - 0.960490*p`)
- `tolerance_classes: {"external": ["Close", "Medium", "Free"]}`
- `special_params: {"rounded_radius": "0.137329*P", "crest_flat": "P/12", "root_flat": "P/6"}`

##### ✅ b) `UNS` — Unified National Special
- `flank_angle: 60.0`, `profile_type: "V"`, `unit: "inch"`
- `diam_pitch_map`: sonderkombinierte TPI, z. B.
  `{1/2: 12, 5/8: 16, 3/4: 14, 7/8: 18, 1.0: 16, 1.125: 16, 1.25: 16, 1.5: 14}`
  (Quelle: ASME B1.1, Tabelle 5).
- Formeln wie `UNC` (`d2 = d - 0.649519*p`, `d3 = d - 1.299038*p`,
  `tensile = d - 0.974279*p`)
- `tolerance_classes: {"external": ["2A", "3A"], "internal": ["2B", "3B"]}`
- `special_params: {"flat_root": True}`

##### ✅ c) `METRIC_TRAPEZOIDAL_FINE` — DIN 380
- `flank_angle: 30.0`, `profile_type: "TRAPEZOID"`, `unit: "mm"`
- `diam_pitch_map` (Auswahl aus DIN 380-2 Reihe 1):
  `{10: 1.5, 12: 2, 16: 2, 20: 2, 24: 3, 30: 3, 36: 3, 42: 4, 48: 4, 60: 5, 70: 5}`
- Formeln: `d2 = d - 0.5*p`, `d3 = d - p - 0.5*ac` mit `ac=0.15` (typisch DIN 380)
  als konservative Näherung. Genau: `d3 = d - p - 0.15` für die häufigen kleinen
  Steigungen, `d3 = d - p - 0.25` für `p >= 4`. Lies aus DIN 380-1 Tabelle 1 ab,
  wenn unklar, **dokumentiere Entscheidung als Kommentar**.
- `tensile_stress_area_formula = lambda d, p: d - 0.5*p - 0.25`
- `tolerance_classes: {"external": ["7e", "8e", "9e"], "internal": ["7H", "8H"]}`
- `special_params: {"crest_width": "0.5*P", "root_width": "0.5*P - 0.15"}`

##### ✅ d) `STUB_ACME` — ASME B1.8 (halbe Trapez-Höhe)
- `flank_angle: 29.0`, `profile_type: "TRAPEZOID"`, `unit: "inch"`
- `diam_pitch_map`: z. B. `{1/4: 16, 5/16: 14, 3/8: 12, 1/2: 10, 5/8: 8, 3/4: 6, 1.0: 5, 1.25: 5, 1.5: 4, 2.0: 4}`
- Profilhöhe ist **0,5·H** vom Standard-ACME → vermerke das im `special_params`
  (`"height_factor": 0.5`).
- `d2_formula: lambda d, p: d - 0.25 * p`
- `d3_formula: lambda d, p: d - 0.5 * p - 0.020 * MM_PER_INCH`
- `tensile_stress_area_formula: lambda d, p: d - 0.5 * p`
- `tolerance_classes: {"external": ["2G", "3G", "4G"]}`
- **Geometrie-Engine erweitern:** im `TRAPEZOID`-Branch von `geometry_engine.py`
  einen `height_factor` aus `special_params` lesen, der die Verjüngungstiefe
  steuert. Default 1.0 (bisheriges Verhalten bleibt für `TRAPEZOIDAL`, `ACME` erhalten).

##### ✅ e) `KNUCKLE` — ASME B1.9, Round
- `flank_angle: 30.0`, `profile_type: "ROUND"`, `unit: "inch"`
- `diam_pitch_map` (auszugsweise): `{1/4: 20, 3/8: 16, 1/2: 12, 5/8: 10, 3/4: 8, 1.0: 6, 1.25: 5, 1.5: 4, 2.0: 3}`
- `d2_formula: lambda d, p: d - 0.5 * p`
- `d3_formula: lambda d, p: d - p - 0.5 * (p/4.0)` (konservativ)
- `tensile_stress_area_formula: lambda d, p: d - 0.5 * p - 0.125`
- `tolerance_classes: {"external": ["2A"], "internal": ["2B"]}` (Standardklassen)
- `special_params: {"radius": "P/4"}`

##### ✅ f) `SPARK_PLUG` — ISO 28741
- `flank_angle: 60.0`, `profile_type: "V"`, `unit: "mm"`
- `diam_pitch_map`: `{"M8x1": 1.0, "M10x1": 1.0, "M12x1.25": 1.25, "M14x1.25": 1.25, "M18x1.5": 1.5}`
- `diam_nominal_map`: `{"M8x1": 8.0, "M10x1": 10.0, "M12x1.25": 12.0, "M14x1.25": 14.0, "M18x1.5": 18.0}`
- Formeln wie `METRIC_ISO` (`d2 = d - 0.649519*p`, `d3 = d - 1.226869*p`,
  `tensile = d - 0.9382*p`)
- `tolerance_classes: {"external": ["6g"], "internal": ["6H"]}`
- `special_params: {"crest_flat": "P/8", "root_flat": "P/4"}`

##### ✅ g) `CABLE_GLAND_M` — DIN EN 60423
- `flank_angle: 60.0`, `profile_type: "V"`, `unit: "mm"`
- Standardgrößen: `{"M12x1.5": 1.5, "M16x1.5": 1.5, "M20x1.5": 1.5, "M25x1.5": 1.5, "M32x1.5": 1.5, "M40x1.5": 1.5, "M50x1.5": 1.5, "M63x1.5": 1.5}`
- `diam_nominal_map`: passend (12, 16, 20, 25, 32, 40, 50, 63).
- Formeln wie `METRIC_ISO`
- `tolerance_classes: {"external": ["6g"], "internal": ["6H"]}`
- `special_params: {"crest_flat": "P/8", "root_flat": "P/4"}`

##### ✅ h) `CONDUIT_PG` — DIN 40430 (Erweiterung, NICHT Duplikat von `PG`)
- Vorhandener `PG`-Eintrag bleibt (Werkstattbezeichnung). `CONDUIT_PG` ergänzt
  die elektroinstallationsspezifischen Größen:
  `{"Pg7": 1.27, "Pg9": 1.41, "Pg11": 1.41, "Pg13.5": 1.41, "Pg16": 1.41, "Pg21": 1.588, "Pg29": 1.588, "Pg36": 1.814, "Pg42": 1.814, "Pg48": 1.814}`
- Falls Inhalt identisch zu `PG`: setze `CONDUIT_PG` als **Alias**-Eintrag,
  der den `PG`-Eintrag rein zeigt (`THREAD_STANDARDS["CONDUIT_PG"] = THREAD_STANDARDS["PG"]`).
  In dem Fall README so anpassen, dass nur eine Zeile bleibt.
- Empfehlung: **vereinige zu `PG` und lösche `CONDUIT_PG` aus der README**, weil
  es keine semantische Differenz gibt. Setze die README-Änderung in den Commit.

##### ✅ i) `LAMP_B` — IEC 60061-1, Bajonett-Lampensockel
- `profile_type: "BAYONET"` (gleiche Sackgasse wie STORZ!).
- Erst implementierbar, wenn entweder eine echte Bayonet-Geometrie-Pipeline
  existiert (Task P3.1) oder klargestellt ist, dass das nur ein Datenbankeintrag
  ohne Mesh-Generierung wird.
- Liefere mindestens den Datenbankeintrag mit Größen `B15s`, `B15d`, `B22d`
  (Nenndurchmesser 15, 15, 22 mm) und `diam_pitch_map` mit `0.0` (analog STORZ).
- Operator/UI muss diesen Fall sauber mit `{"ERROR"}` melden (siehe P0.1).

---

### ✅ P2 — Code-Qualität / Konsistenz

#### ✅ P2.1 `starts`-Obergrenzen vereinheitlichen
UI: `max=8`. `mechanical_validation.validate_thread_input`: `max=16`.
Operator warnt ab `>2`. Wähle **eine** Obergrenze (Empfehlung: `8`) und
trage sie überall ein. Operator-Warnung beibehalten — sie ist berechtigt.

#### ✅ P2.2 `custom_profile_type` im UI um `EDISON` erweitern
`ui_panel.py::UTG_Properties.custom_profile_type` muss auch `EDISON` enthalten,
sonst sind eigene Edison-ähnliche Profile nicht baubar. Add: `("EDISON", "Edison", "")`.

#### ✅ P2.3 Backwards-Compat-Klausel in `_check_profile_inputs`
Die Stelle „auch bei Normfamilien ohne 6g-Klasse" ist ein Tech-Debt-Workaround.
Klären, ob das noch nötig ist; wenn ja, kommentieren mit Referenz auf den Aufrufer.
Wenn nicht, entfernen. Wenn entfernt: `api.thread()` muss vorher die richtige
Default-Klasse pro Norm bestimmen, statt blind `6g` durchzureichen.

#### ✅ P2.4 `apply_boolean_cutter` als toter API-Pfad
Funktion ist exportiert, aber kein Operator nutzt sie mehr. Entscheide:
- entfernen (sauberer), oder
- mit einem Deprecation-Kommentar (max. 1 Zeile) als „public helper for downstream
  add-ons (Uni-threaded-sleeve)" markieren.

#### ✅ P2.5 `internal=True`-Pfad in `generate_profile`
Wird außer in Tests nicht mehr aufgerufen. `Uni-threaded-sleeve` ist ein eigenes
Repo, der Pfad muss erhalten bleiben. **Markiere** im Docstring von
`generate_profile`, dass `internal=True` ausschließlich vom Sleeve-Repo genutzt
wird, und schließe einen End-to-End-Test in `tests/test_regression_dimensions.py`
ab, der `internal=True` mindestens einmal mit assert auf Radius-Offset prüft.

#### ✅ P2.6 `tolerance_classes` fehlen für 6 Normen
`BUTTRESS`, `ROUND`, `NPT`, `PG`, `EDISON`, `STORZ` haben keine
`tolerance_classes`. Trage zumindest die Werkstoff-üblichen Klassen ein
(BUTTRESS DIN 513 → 7e/8e/9e; ROUND DIN 405 → analog Trapezoidal; NPT → L1/L2;
PG → keine Klassen, dokumentieren).

---

### ✅ P3 — Erweiterungen (nicht blockierend für „README-Erfüllung")

#### ✅ P3.1 Echte Bayonet-/Knaggenkupplungs-Pipeline (STORZ, LAMP_B)
Mesh-Generierung für STORZ und LAMP_B: kein helikales Profil, sondern
2–3 radiale Knaggen mit umlaufender Nut. **Eigener Builder** in einem neuen
Modul `bayonet_builder.py`. Operator entscheidet nach `profile_type`, welcher
Builder läuft. Beachte: für STORZ existieren festgelegte Knaggen-Geometrien
(DIN 14318), für LAMP_B B15/B22 (IEC 60061-1, Sheet 7004-11).

#### ✅ P3.2 Konsistenter Konus für NPT/PIPE_R/BSPT
`taper_ratio` ist im `mesh_builder` als simple Radiusskalierung pro Z. Korrekt
wäre eine kegelige Erweiterung mit Anfangs-Major-Diameter laut Norm
(`pitch_diameter + taper * length`). Quelle: ISO 7-1 / ANSI B1.20.1.
Headless-Smoke-Test ergänzen.

#### ✅ P3.3 Spannungsquerschnitt für alle Profilfamilien
Aktuell nutzt `mechanical_validation` einen metrischen Fallback `d - 0.9382*p`,
wenn die Norm keine eigene Formel hat. Nach P1.1 ist das obsolet — entferne
den Fallback und werfe einen `ValueError` mit klarer Norm-Referenz.

#### ✅ P3.4 i18n für Operator-Reports
Die `self.report(…)`-Strings im Operator sind hart deutsch. Ziehe sie über
`ui_i18n.ui_label(...)` und ergänze entsprechende Keys (`error_*`, `warning_*`)
in `ui_i18n.UI_TEXT`.

---

## 3. Test-Pflicht für jede Änderung

1. `python -m unittest discover -s tests -p "test_*.py"` muss grün sein.
2. `ruff check .` darf **keine** neuen Findings melden.
3. Für jede neue Norm in P1: mindestens ein Eintrag im Subtest
   `test_core_standards_generate_non_degenerate_profiles` und in
   `HighEndDataCoverageTests`.
4. Für jeden Bugfix in P0: ein expliziter Regressionstest, der den alten
   Fehlerpfad reproduziert hätte.

---

## 4. Commit-Regeln

- Pro Task ein Commit mit Präfix `feat:`, `fix:`, `docs:`, `chore:` oder `test:`.
- Branch-Konvention vom Repo übernehmen (z. B. `codex/p1-add-bsf-thread`).
- Kein „WIP"-Commit, kein gebündeltes Mega-Commit.
- Commit-Body referenziert den Task-Identifier aus dieser Datei
  (Beispiel: „Resolves P0.1 — STORZ pipeline raises clear NotImplementedError.").

---

## 5. Out-of-Scope für Codex

- Keine Änderungen an `.github/workflows/ci.yml` ohne Rückfrage.
- Keine neuen externen Python-Dependencies (Numpy, SciPy, …).
- Keine Verschiebung der Modul-Dateien aus dem Repo-Root — Blender erwartet sie dort.
- Keine Refactor-Welle auf bestehende Module „nebenbei". Ein Task = ein Scope.

---

## 6. Schnellverweise

- Add-on-Entry: `__init__.py`
- Normen-Datenbank: `database.py::THREAD_STANDARDS`
- Profilberechnung: `geometry_engine.py::generate_profile`
- Mesh-Erzeugung: `mesh_builder.py::create_thread_mesh`
- UI-Panel: `ui_panel.py`
- High-Level API: `api.py::thread`
- Tests: `tests/test_*.py`
- Headless-Smoke: `scripts/blender_smoke_test.py`
