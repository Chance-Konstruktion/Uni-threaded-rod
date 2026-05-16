import ast
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
INIT_FILE = ROOT / "__init__.py"
README_FILE = ROOT / "README.md"


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
        self.assertEqual(module.bl_info["version"], (0, 2, 0))
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

    def test_readme_describes_release_scope_without_removed_cutter_ui(self):
        text = README_FILE.read_text(encoding="utf-8").lower()

        self.assertIn("release 0.2", text)
        self.assertIn("external threads", text)
        self.assertNotIn("internal-thread cutters", text)
        self.assertNotIn("innengewinde-cuttern", text)


if __name__ == "__main__":
    unittest.main()
