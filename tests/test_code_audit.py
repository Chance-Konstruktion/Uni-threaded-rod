import ast
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

    import importlib.util

    spec = importlib.util.spec_from_file_location(full_name, ROOT / f"{module_name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = module
    spec.loader.exec_module(module)
    return module


class CodeAuditTests(unittest.TestCase):
    def test_removed_unused_mesh_builder_entry_points(self):
        tree = ast.parse((ROOT / "mesh_builder.py").read_text())
        function_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
        self.assertNotIn("_sort_vertices_radially", function_names)

    def test_create_thread_mesh_signature_has_no_unused_name_parameter(self):
        tree = ast.parse((ROOT / "mesh_builder.py").read_text())
        create_thread_mesh = next(
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "create_thread_mesh"
        )
        argument_names = [argument.arg for argument in create_thread_mesh.args.args]
        self.assertNotIn("name", argument_names)

    def test_ratio_warnings_are_returned_without_module_global_state(self):
        tree = ast.parse((ROOT / "geometry_engine.py").read_text())
        assigned_names = {
            target.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name)
        }
        self.assertNotIn("_RATIO_WARNINGS", assigned_names)

        database = _load_utg_module("database")
        geometry_engine = _load_utg_module("geometry_engine")
        original = database.THREAD_STANDARDS["NPT"]["special_params"].get("root_radius")
        database.THREAD_STANDARDS["NPT"]["special_params"]["root_radius"] = "bad ratio"
        try:
            profile, warnings = geometry_engine.generate_profile(
                "NPT",
                diameter=10.0,
                pitch=1.5,
                return_warnings=True,
            )
        finally:
            if original is None:
                database.THREAD_STANDARDS["NPT"]["special_params"].pop("root_radius", None)
            else:
                database.THREAD_STANDARDS["NPT"]["special_params"]["root_radius"] = original

        self.assertGreaterEqual(len(profile), 3)
        self.assertEqual(1, len(warnings))
        self.assertIn("bad ratio", warnings[0])


if __name__ == "__main__":
    unittest.main()
