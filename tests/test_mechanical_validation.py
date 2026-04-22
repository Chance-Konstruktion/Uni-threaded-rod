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


mech = _load_utg_module("mechanical_validation")


class MechanicalValidationTests(unittest.TestCase):
    def test_parameter_validation_rejects_negative_clearance(self):
        result = mech.validate_thread_input(diameter=10.0, pitch=1.5, length=25.0, starts=1, clearance=-0.01)
        self.assertFalse(result.ok)
        self.assertIn("Clearance", result.message)

    def test_nut_fit_positive_case(self):
        result = mech.check_nut_fit(bolt_major_diameter=10.0, nut_minor_diameter=10.3, radial_clearance=0.1)
        self.assertTrue(result["fits"])
        self.assertAlmostEqual(result["required_minor_diameter"], 10.2, places=6)

    def test_nut_fit_interference_case(self):
        result = mech.check_nut_fit(bolt_major_diameter=10.0, nut_minor_diameter=10.1, radial_clearance=0.1)
        self.assertFalse(result["fits"])
        self.assertGreater(result["interference_mm"], 0.0)

    def test_pitch_match(self):
        ok = mech.check_pitch_match(1.5, 1.5, tolerance_mm=1e-6)
        bad = mech.check_pitch_match(1.5, 1.4, tolerance_mm=0.01)
        self.assertTrue(ok["matches"])
        self.assertFalse(bad["matches"])

    def test_mechanical_load_case_calculates_stresses_and_sf(self):
        result = mech.validate_mechanical_load_case(
            force_n=5000.0,
            allowable_tensile_mpa=320.0,
            allowable_shear_mpa=180.0,
            diameter=10.0,
            pitch=1.5,
            engagement_length=10.0,
        )
        self.assertGreater(result["tensile"].stress_mpa, 0.0)
        self.assertGreater(result["shear"].stress_mpa, 0.0)
        self.assertGreater(result["tensile"].safety_factor, 1.0)
        self.assertGreater(result["min_safety_factor"], 1.0)

    def test_validate_thread_input_uses_standard_core_formula(self):
        result = mech.validate_thread_input(
            diameter=10.0,
            pitch=1.5,
            length=20.0,
            starts=1,
            clearance=0.0,
            standard_key="METRIC_ISO",
        )
        self.assertTrue(result.ok)

    def test_property_class_tensile_check(self):
        result = mech.validate_property_class_tensile(
            force_n=10000.0,
            standard_key="METRIC_ISO",
            diameter=10.0,
            pitch=1.5,
            property_class="8.8",
            required_safety_factor=1.5,
        )
        self.assertIn("stress_mpa", result)
        self.assertIn("core_area_mm2", result)
        self.assertGreater(result["safety_factor"], 1.0)

    def test_norm_binding_for_metric_external_6g(self):
        result = mech.validate_norm_binding("METRIC_ISO", tolerance_class="6g", internal=False)
        self.assertTrue(result.ok)
        self.assertIn("ISO 68-1", result.message)

    def test_norm_binding_rejects_wrong_side_tolerance(self):
        result = mech.validate_norm_binding("METRIC_ISO", tolerance_class="6H", internal=False)
        self.assertFalse(result.ok)
        self.assertIn("nicht zulässig", result.message)

    def test_validate_thread_input_rejects_extreme_length_ratio(self):
        result = mech.validate_thread_input(
            diameter=1.0,
            pitch=0.2,
            length=1500.0,
            starts=1,
            clearance=0.0,
            standard_key="METRIC_ISO",
        )
        self.assertFalse(result.ok)
        self.assertIn("extrem hoch", result.message)

    def test_validate_buckling_returns_safety_factor(self):
        d3 = mech._resolve_core_diameter("METRIC_ISO", diameter=10.0, pitch=1.5)
        result = mech.validate_buckling(
            force_n=1000.0,
            core_diameter_mm=d3,
            unsupported_length_mm=100.0,
            e_modulus_mpa=210000.0,
            k_factor=1.0,
        )
        self.assertGreater(result["critical_load_n"], 0.0)
        self.assertGreater(result["safety_factor"], 1.0)


if __name__ == "__main__":
    unittest.main()
