import importlib.util
import math
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


if __name__ == "__main__":
    unittest.main()
