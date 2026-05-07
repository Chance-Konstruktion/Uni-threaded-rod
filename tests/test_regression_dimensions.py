import ast
import importlib.util
import pathlib
import sys
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load_utg_module(module_name: str):
    pkg_name = "utg"
    if pkg_name not in sys.modules:
        pkg = types.ModuleType(pkg_name)
        pkg.__path__ = [str(ROOT)]
        sys.modules[pkg_name] = pkg

    full_name = f"{pkg_name}.{module_name}"
    if full_name in sys.modules:
        return sys.modules[full_name]

    spec = importlib.util.spec_from_file_location(full_name, ROOT / f"{module_name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = module
    spec.loader.exec_module(module)
    return module


database = _load_utg_module("database")
geometry_engine = _load_utg_module("geometry_engine")

ui_i18n = _load_utg_module("ui_i18n")


class ReferenceRegressionTests(unittest.TestCase):
    def test_symbolic_pipe_resolution_g_half(self):
        diameter_mm, pitch_mm = database.resolve_thread_parameters("PIPE_G", "G1/2")
        self.assertAlmostEqual(diameter_mm, 20.955, places=6)
        self.assertAlmostEqual(pitch_mm, 25.4 / 14.0, places=6)

    def test_symbolic_tapered_sealing_pipe_resolution_r_half(self):
        diameter_mm, pitch_mm = database.resolve_thread_parameters("PIPE_R", "R1/2")
        self.assertAlmostEqual(diameter_mm, 20.955, places=6)
        self.assertAlmostEqual(pitch_mm, 25.4 / 14.0, places=6)

    def test_tapered_sealing_pipe_thread_metadata(self):
        pipe_r = database.THREAD_STANDARDS["PIPE_R"]
        self.assertEqual(pipe_r["standard"], "DIN EN 10226 / ISO 7-1")
        self.assertEqual(pipe_r["flank_angle"], 55.0)
        self.assertEqual(pipe_r["special_params"]["taper_ratio"], 1 / 16)

    def test_npt_resolution_one_half(self):
        diameter_mm, pitch_mm = database.resolve_thread_parameters("NPT", "1 1/2")
        self.assertAlmostEqual(diameter_mm, 48.3, places=6)
        self.assertAlmostEqual(pitch_mm, 25.4 / 11.5, places=6)

    def test_metric_profile_reference_radii(self):
        diameter_mm, pitch_mm = 10.0, 1.5
        points = geometry_engine.generate_profile("METRIC_ISO", diameter_mm, pitch_mm)
        d3 = database.THREAD_STANDARDS["METRIC_ISO"]["d3_formula"](diameter_mm, pitch_mm)

        self.assertEqual(len(points), 8)
        self.assertAlmostEqual(points[0].x, diameter_mm / 2.0 - 0.01, places=6)
        self.assertAlmostEqual(points[3].x, d3 / 2.0 - 0.01, places=6)

    def test_v_profile_parameterization_differs_by_standard(self):
        pitch = 1.5
        metric = geometry_engine.generate_profile("METRIC_ISO", diameter=10.0, pitch=pitch)
        unc = geometry_engine.generate_profile("UNC", diameter=10.0, pitch=pitch)
        bsw = geometry_engine.generate_profile("WHITWORTH_BSW", diameter=10.0, pitch=pitch)

        # Root-/Crest-Breiten unterscheiden sich je Normfamilie.
        self.assertNotAlmostEqual(metric[1].y, unc[1].y, places=6)
        self.assertNotAlmostEqual(unc[4].y, bsw[4].y, places=6)

    def test_core_standards_generate_non_degenerate_profiles(self):
        cases = [
            ("METRIC_ISO", 10.0, 1.5),
            ("METRIC_FINE", 10.0, 1.25),
            ("WHITWORTH_BSW", 12.0, 1.4),
            ("UNC", 10.0, 1.5),
            ("UNF", 10.0, 1.0),
            ("PIPE_G", 20.0, 1.814285714),
            ("PIPE_R", 20.0, 1.814285714),
            ("TRAPEZOIDAL", 20.0, 4.0),
            ("BUTTRESS", 20.0, 5.0),
            ("ROUND", 20.0, 4.0),
            ("ACME", 20.0, 2.0),
            ("NPT", 20.0, 1.8),
            ("PG", 20.4, 1.41),
            ("EDISON", 27.0, 3.5),
        ]
        for standard, diameter, pitch in cases:
            with self.subTest(standard=standard):
                points = geometry_engine.generate_profile(standard, diameter=diameter, pitch=pitch)
                self.assertGreaterEqual(len(points), 3)
                self.assertLess(min(p.x for p in points), max(p.x for p in points))

    def test_external_profiles_start_and_end_at_major_radius(self):
        cases = [
            ("METRIC_ISO", 10.0, 1.5),
            ("TRAPEZOIDAL", 20.0, 4.0),
            ("ROUND", 20.0, 4.0),
            ("BUTTRESS", 20.0, 5.0),
        ]
        for standard, diameter, pitch in cases:
            with self.subTest(standard=standard):
                points = geometry_engine.generate_profile(standard, diameter=diameter, pitch=pitch)
                major_radius = diameter / 2.0 - 0.01
                self.assertAlmostEqual(points[0].x, major_radius, places=6)
                self.assertAlmostEqual(points[0].y, 0.0, places=6)
                self.assertAlmostEqual(points[-1].x, major_radius, places=6)
                self.assertAlmostEqual(points[-1].y, pitch, places=6)

    def test_rejects_metric_v_profile_with_regressed_root_shoulder_radius(self):
        diameter_mm, pitch_mm = 10.0, 1.5
        points = geometry_engine.generate_profile("METRIC_ISO", diameter_mm, pitch_mm)
        major_radius = diameter_mm / 2.0 - 0.01
        d3 = database.THREAD_STANDARDS["METRIC_ISO"]["d3_formula"](diameter_mm, pitch_mm)
        core_radius = d3 / 2.0 - 0.01
        root_flat = pitch_mm / 4.0
        bad_points = list(points)
        bad_points[1] = geometry_engine.ProfilePoint(
            major_radius - (major_radius - core_radius) + root_flat * 0.5,
            points[1].y,
        )

        with self.assertRaisesRegex(ValueError, "Kernradius"):
            geometry_engine._validate_external_profile_points(
                bad_points,
                major_radius,
                core_radius,
                pitch_mm,
            )

    def test_rejects_non_positive_pitch(self):
        with self.assertRaisesRegex(ValueError, "Steigung"):
            geometry_engine.generate_profile("METRIC_ISO", diameter=10.0, pitch=0.0)

    def test_rejects_unknown_standard(self):
        with self.assertRaisesRegex(ValueError, "Unbekannter Standard"):
            geometry_engine.generate_profile("NOT_A_STANDARD", diameter=10.0, pitch=1.5)

    def test_rejects_undefined_tolerance_class(self):
        with self.assertRaisesRegex(ValueError, "Toleranzklasse"):
            geometry_engine.generate_profile("METRIC_ISO", diameter=10.0, pitch=1.5, tolerance_class="9Z")

    def test_metric_iso_core_diameter_matches_reference_formula(self):
        diameter_mm, pitch_mm = 12.0, 1.75
        d3 = database.THREAD_STANDARDS["METRIC_ISO"]["d3_formula"](diameter_mm, pitch_mm)
        self.assertAlmostEqual(d3, diameter_mm - 1.226869 * pitch_mm, places=6)

    def test_tolerance_and_clearance_shift_profile_radius(self):
        base = geometry_engine.generate_profile("METRIC_ISO", diameter=10.0, pitch=1.5, tolerance_class="6g", clearance=0.0)
        loose_internal = geometry_engine.generate_profile(
            "METRIC_ISO",
            diameter=10.0,
            pitch=1.5,
            tolerance_class="6H",
            internal=True,
            clearance=0.2,
        )
        self.assertGreater(loose_internal[0].x, base[0].x)

    def test_iso_table_row_resolution_m10(self):
        row = database.resolve_iso_metric_coarse_row(10.0, 1.5)
        self.assertIsNotNone(row)
        self.assertAlmostEqual(row["d2_basic"], 9.026, places=3)


class HighEndDataCoverageTests(unittest.TestCase):
    def test_metric_iso_series_contains_m1_to_m64(self):
        expected_tokens = {"M1", "M1.2", "M1.4", "M1.6", "M2", "M2.5", "M3", "M4", "M5", "M6", "M8", "M10", "M12", "M16", "M20", "M24", "M30", "M36", "M42", "M48", "M56", "M64"}
        self.assertTrue(expected_tokens.issubset(set(database.ISO_METRIC_COARSE_TABLE.keys())))

    def test_metric_fine_series_contains_nominal_sizes_below_m8(self):
        expected = {
            1.0: 0.2,
            1.2: 0.2,
            1.4: 0.2,
            1.6: 0.2,
            1.8: 0.2,
            2.0: 0.25,
            2.5: 0.35,
            3.0: 0.35,
            3.5: 0.35,
            4.0: 0.5,
            5.0: 0.5,
            6.0: 0.75,
            7.0: 0.75,
        }
        fine_map = database.THREAD_STANDARDS["METRIC_FINE"]["diam_pitch_map"]
        for diameter, pitch in expected.items():
            with self.subTest(diameter=diameter):
                self.assertIn(diameter, fine_map)
                self.assertEqual(fine_map[diameter], pitch)

    def test_metric_iso_row_contains_crest_and_root_radius(self):
        row = database.resolve_iso_metric_coarse_row(10.0, 1.5)
        self.assertIsNotNone(row)
        self.assertGreater(row["crest_flat"], 0.0)
        self.assertGreater(row["root_radius"], 0.0)


class LocalizationAndReferenceExpansionTests(unittest.TestCase):
    def test_ui_i18n_has_de_and_en_labels_for_core_keys(self):
        keys = [
            "standard", "diameter", "length", "handedness", "starts",
            "tolerance", "create_thread",
        ]
        for key in keys:
            with self.subTest(key=key):
                self.assertIsInstance(ui_i18n.ui_label(key, "de"), str)
                self.assertIsInstance(ui_i18n.ui_label(key, "en"), str)
                self.assertNotEqual(ui_i18n.ui_label(key, "de"), "")
                self.assertNotEqual(ui_i18n.ui_label(key, "en"), "")

    def test_threaded_rod_length_label_uses_rod_not_thread(self):
        self.assertEqual(ui_i18n.ui_label("length", "de"), "Gewindestangenlänge")
        self.assertEqual(ui_i18n.ui_label("length", "en"), "Threaded rod length")

    def test_mm_input_properties_do_not_use_blender_length_unit_conversion(self):
        tree = ast.parse((ROOT / "ui_panel.py").read_text(encoding="utf-8"))
        properties = {
            node.target.id: {keyword.arg: keyword.value for keyword in node.annotation.keywords}
            for node in ast.walk(tree)
            if isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id in {"length", "clearance", "custom_diameter", "custom_pitch"}
        }

        self.assertEqual(properties["length"]["name"].value, "Gewindestangenlänge (mm)")
        self.assertEqual(properties["length"]["default"].value, 100.0)
        self.assertEqual(properties["clearance"]["name"].value, "Spiel (mm)")
        self.assertEqual(properties["custom_diameter"]["name"].value, "Durchmesser (mm)")
        self.assertEqual(properties["custom_pitch"]["name"].value, "Steigung (mm)")
        for keywords in properties.values():
            self.assertNotIn("unit", keywords)

    def test_iso_reference_rows_additional_sizes(self):
        cases = [
            (1.0, 0.25),
            (8.0, 1.25),
            (24.0, 3.0),
            (64.0, 6.0),
        ]
        for diameter, pitch in cases:
            with self.subTest(diameter=diameter, pitch=pitch):
                row = database.resolve_iso_metric_coarse_row(diameter, pitch)
                self.assertIsNotNone(row)
                self.assertAlmostEqual(row["d2_basic"], diameter - 0.649519 * pitch, places=6)
                self.assertAlmostEqual(row["d3_basic"], diameter - 1.226869 * pitch, places=6)

    def test_tensile_stress_area_formula_available_for_v_families(self):
        for standard in ["METRIC_ISO", "METRIC_FINE", "WHITWORTH_BSW", "UNC", "UNF", "PIPE_G", "PIPE_R"]:
            with self.subTest(standard=standard):
                formula = database.THREAD_STANDARDS[standard].get("tensile_stress_area_formula")
                self.assertIsNotNone(formula)
                self.assertLess(formula(10.0, 1.5), 10.0)


if __name__ == "__main__":
    unittest.main()
