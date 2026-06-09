import pathlib
import sys
import types
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]


class FreeCADWorkbenchTests(unittest.TestCase):
    def test_package_metadata_points_to_root_workbench(self):
        tree = ET.parse(ROOT / "package.xml")
        root = tree.getroot()

        self.assertEqual(root.findtext(".//subdirectory"), "./")
        self.assertEqual(root.findtext(".//classname"), "UniThreadedRodWorkbench")
        self.assertTrue((ROOT / "InitGui.py").exists())

    def test_init_gui_registers_without_file_global(self):
        registered = []
        freecad_gui = types.ModuleType("FreeCADGui")
        freecad_gui.Workbench = type("Workbench", (), {})
        freecad_gui.addWorkbench = registered.append
        sys.modules["FreeCADGui"] = freecad_gui

        source = (ROOT / "InitGui.py").read_text(encoding="utf-8")
        code = compile(source, str(ROOT / "InitGui.py"), "exec")
        globals_dict = {"__builtins__": __builtins__, "__name__": "InitGui"}
        locals_dict = {}

        try:
            exec(code, globals_dict, locals_dict)
        finally:
            sys.modules.pop("FreeCADGui", None)

        self.assertEqual(len(registered), 1)
        workbench = registered[0]
        self.assertEqual(workbench.__class__.__name__, "UniThreadedRodWorkbench")
        self.assertEqual(workbench.MenuText, "Uni-threaded-rod")
        self.assertTrue(workbench.Icon.endswith("freecad_backend/workbench/icons/uni_threaded_rod.svg"))

    def test_freecad_params_use_shared_core_presets(self):
        from freecad_backend.params import FreeCADThreadParameters

        params = FreeCADThreadParameters.from_standard("METRIC_ISO", "10", length=30.0)

        self.assertEqual(params.standard, "METRIC_ISO")
        self.assertEqual(params.diameter_mm, 10.0)
        self.assertEqual(params.pitch_mm, 1.5)


if __name__ == "__main__":
    unittest.main()
