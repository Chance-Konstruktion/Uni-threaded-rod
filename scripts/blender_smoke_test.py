"""Headless Blender smoke test for UTG add-on.

Run via:
blender -b --factory-startup --python scripts/blender_smoke_test.py
"""

import importlib.util
import pathlib
import sys

import bpy

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_NAME = "utg_addon"

spec = importlib.util.spec_from_file_location(
    MODULE_NAME,
    ROOT / "__init__.py",
    submodule_search_locations=[str(ROOT)],
)
addon = importlib.util.module_from_spec(spec)
sys.modules[MODULE_NAME] = addon
spec.loader.exec_module(addon)

addon.register()

try:
    scene = bpy.context.scene
    props = scene.utg_props

    props.standard = "METRIC_ISO"
    props.diameter_enum = "10.0"
    props.length = 20.0
    props.starts = 1
    props.end_type = "CHAMFER"

    result = bpy.ops.utg.create_thread()
    assert "FINISHED" in result

    created = bpy.data.objects.get("Gewinde")
    assert created is not None
    assert created.type == "MESH"

    non_manifold = [e for e in created.data.edges if not e.is_manifold]
    assert not non_manifold, f"Non-manifold edges found: {len(non_manifold)}"

    bpy.ops.mesh.primitive_cube_add(size=20.0, location=(0.0, 0.0, 10.0))
    target = bpy.context.active_object
    props.negative_mode = True
    result = bpy.ops.utg.create_thread()
    assert "FINISHED" in result

    assert target is not None and target.type == "MESH"
finally:
    addon.unregister()
