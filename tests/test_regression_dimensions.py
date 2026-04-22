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


class ReferenceRegressionTests(unittest.TestCase):
    def test_symbolic_pipe_resolution_g_half(self):
        diameter_mm, pitch_mm = database.resolve_thread_parameters("PIPE_G", "G1/2")
        self.assertAlmostEqual(diameter_mm, 20.955, places=6)
        self.assertAlmostEqual(pitch_mm, 25.4 / 14.0, places=6)

    def test_npt_resolution_one_half(self):
        diameter_mm, pitch_mm = database.resolve_thread_parameters("NPT", "1 1/2")
        self.assertAlmostEqual(diameter_mm, 48.3, places=6)
        self.assertAlmostEqual(pitch_mm, 25.4 / 11.5, places=6)

    def test_metric_profile_reference_radii(self):
        diameter_mm, pitch_mm = 10.0, 1.5
        points = geometry_engine.generate_profile("METRIC_ISO", diameter_mm, pitch_mm)
        d3 = database.THREAD_STANDARDS["METRIC_ISO"]["d3_formula"](diameter_mm, pitch_mm)

        self.assertEqual(len(points), 6)
        self.assertAlmostEqual(points[0].x, diameter_mm / 2.0 - 0.01, places=6)
        self.assertAlmostEqual(points[2].x, d3 / 2.0 - 0.01, places=6)

    def test_ball_screw_gothic_profile_regression_shape(self):
        points = geometry_engine.generate_profile("BALL_SCREW", diameter=20.0, pitch=5.0)
        self.assertEqual(len(points), 34)
        self.assertAlmostEqual(points[-1].y, 5.0, places=6)
        self.assertLess(min(p.y for p in points), 0.0)
        self.assertGreater(max(p.y for p in points), 5.0)

    def test_v_profile_parameterization_differs_by_standard(self):
        pitch = 1.5
        metric = geometry_engine.generate_profile("METRIC_ISO", diameter=10.0, pitch=pitch)
        unc = geometry_engine.generate_profile("UNC", diameter=10.0, pitch=pitch)
        bsw = geometry_engine.generate_profile("WHITWORTH_BSW", diameter=10.0, pitch=pitch)

        # Root-/Crest-Breiten unterscheiden sich je Normfamilie.
        self.assertNotAlmostEqual(metric[1].y, unc[1].y, places=6)
        self.assertNotAlmostEqual(unc[4].y, bsw[4].y, places=6)

    def test_ball_screw_gothic_uses_standard_specific_ratios(self):
        points = geometry_engine.generate_profile("BALL_SCREW", diameter=25.0, pitch=5.0)
        r2 = database.THREAD_STANDARDS["BALL_SCREW"]["d2_formula"](25.0, 5.0) / 2.0 - 0.01
        expected_min_x = r2 - 2.0 * (5.0 * 0.52)
        self.assertAlmostEqual(min(p.x for p in points), expected_min_x, places=6)

    def test_core_standards_generate_non_degenerate_profiles(self):
        cases = [
            ("METRIC_ISO", 10.0, 1.5),
            ("METRIC_FINE", 10.0, 1.25),
            ("WHITWORTH_BSW", 12.0, 1.4),
            ("UNC", 10.0, 1.5),
            ("UNF", 10.0, 1.0),
            ("PIPE_G", 20.0, 1.814285714),
            ("TRAPEZOIDAL", 20.0, 4.0),
            ("BUTTRESS", 20.0, 5.0),
            ("ROUND", 20.0, 4.0),
            ("ACME", 20.0, 2.0),
            ("NPT", 20.0, 1.8),
            ("PG", 20.4, 1.41),
            ("EDISON", 27.0, 3.5),
            ("BALL_SCREW", 20.0, 5.0),
        ]
        for standard, diameter, pitch in cases:
            with self.subTest(standard=standard):
                points = geometry_engine.generate_profile(standard, diameter=diameter, pitch=pitch)
                self.assertGreaterEqual(len(points), 3)
                self.assertLess(min(p.x for p in points), max(p.x for p in points))

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


if __name__ == "__main__":
    unittest.main()
