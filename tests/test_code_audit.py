import ast
import importlib.machinery
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

    def test_blender_reload_refreshes_geometry_engine_before_operator_uses_it(self):
        original_modules = {
            name: sys.modules[name]
            for name in list(sys.modules)
            if (
                name == "bpy"
                or name == "bmesh"
                or name == "mathutils"
                or name == "utg"
                or name.startswith("utg.")
            )
        }
        for name in original_modules:
            sys.modules.pop(name, None)

        bpy = types.ModuleType("bpy")
        bpy.__spec__ = importlib.machinery.ModuleSpec("bpy", loader=None)

        class Operator:
            def report(self, level, message):
                pass

        def property_stub(**kwargs):
            return None

        bpy.types = types.SimpleNamespace(
            Operator=Operator,
            PropertyGroup=type("PropertyGroup", (), {}),
            Panel=type("Panel", (), {}),
            Scene=type("Scene", (), {}),
        )
        bpy.props = types.SimpleNamespace(
            EnumProperty=property_stub,
            FloatProperty=property_stub,
            IntProperty=property_stub,
            BoolProperty=property_stub,
            PointerProperty=property_stub,
        )
        bpy.utils = types.SimpleNamespace(
            register_class=lambda cls: None, unregister_class=lambda cls: None
        )
        bpy.data = types.SimpleNamespace(
            meshes=types.SimpleNamespace(new=lambda name: types.SimpleNamespace(name=name)),
            objects=types.SimpleNamespace(new=lambda name, mesh: types.SimpleNamespace(name=name, mesh=mesh)),
        )
        sys.modules["bpy"] = bpy
        sys.modules["bmesh"] = types.ModuleType("bmesh")
        mathutils = types.ModuleType("mathutils")
        mathutils.Vector = lambda value: value
        sys.modules["mathutils"] = mathutils

        pkg = types.ModuleType("utg")
        pkg.__path__ = [str(ROOT)]
        sys.modules["utg"] = pkg
        geometry_engine = _load_utg_module("geometry_engine")

        def old_generate_profile(
            standard_key,
            diameter,
            pitch,
            tolerance_class="6g",
            internal=False,
            clearance=0.0,
            standard=None,
        ):
            return []

        geometry_engine.generate_profile = old_generate_profile

        try:
            spec = importlib.util.spec_from_file_location(
                "utg", ROOT / "__init__.py", submodule_search_locations=[str(ROOT)]
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules["utg"] = module
            spec.loader.exec_module(module)
            module.create_thread_mesh = lambda **kwargs: types.SimpleNamespace(
                to_mesh=lambda mesh: None, free=lambda: None
            )
            module.apply_material = lambda *args, **kwargs: None

            props = types.SimpleNamespace(
                standard="METRIC_ISO",
                diameter_enum="10",
                length=20.0,
                starts=1,
                clearance=0.0,
                tolerance_class="6g",
                handedness="RIGHT",
                end_type="FLAT",
                lod_level="PREVIEW",
                segment_override=0,
                material="STEEL_8.8",
                surface="NONE",
            )
            context = types.SimpleNamespace(
                scene=types.SimpleNamespace(utg_props=props),
                active_object=None,
                collection=types.SimpleNamespace(objects=types.SimpleNamespace(link=lambda obj: None)),
            )

            self.assertEqual({"FINISHED"}, module.UTG_OT_create_thread().execute(context))
            self.assertIsNot(module.generate_profile, old_generate_profile)
        finally:
            for name in list(sys.modules):
                if (
                    name == "bpy"
                    or name == "bmesh"
                    or name == "mathutils"
                    or name == "utg"
                    or name.startswith("utg.")
                ):
                    sys.modules.pop(name, None)
            sys.modules.update(original_modules)

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
