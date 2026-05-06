import ast
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
INIT_FILE = ROOT / "__init__.py"


class AddonMetadataTests(unittest.TestCase):
    def test_bl_info_is_defined_without_blender_runtime(self):
        spec = importlib.util.spec_from_file_location(
            "utg_addon_metadata",
            INIT_FILE,
            submodule_search_locations=[str(ROOT)],
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.assertEqual(module.bl_info["name"], "Uni-threaded-rod")
        self.assertIn("version", module.bl_info)
        self.assertIn("blender", module.bl_info)

    def test_bl_info_is_a_top_level_assignment_for_blender_scanner(self):
        tree = ast.parse(INIT_FILE.read_text(encoding="utf-8"))
        top_level_assignments = {
            target.id
            for node in tree.body
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name)
        }

        self.assertIn("bl_info", top_level_assignments)


if __name__ == "__main__":
    unittest.main()
