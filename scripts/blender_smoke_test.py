"""Headless Blender smoke test for UTG add-on.

Run via:
blender -b --factory-startup --python scripts/blender_smoke_test.py
"""

import importlib.util
import math
import pathlib
import sys

if importlib.util.find_spec("bpy") is None:
    if "pytest" in sys.modules:
        import pytest

        pytest.skip("bpy is required for Blender smoke test", allow_module_level=True)
    raise SystemExit("bpy is required. Run this script through Blender.")

import bmesh
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

def assert_solid_external_rod(obj, expected_length, nominal_diameter):
    """Beweist die Kernregel im Blender-Smoke-Test: volle Außengewindestange."""
    mesh = obj.data
    radii = [math.hypot(vertex.co.x, vertex.co.y) for vertex in mesh.vertices]
    z_values = [vertex.co.z for vertex in mesh.vertices]

    assert min(z_values) >= -1e-5, f"Mesh ragt unter z=0: {min(z_values)}"
    assert max(z_values) <= expected_length + 1e-5, f"Mesh ragt über Länge hinaus: {max(z_values)}"
    assert abs(min(z_values)) <= 1e-5, f"Bounding Box startet nicht bei z=0: {min(z_values)}"
    assert abs(max(z_values) - expected_length) <= 1e-5, f"Bounding Box endet nicht bei Länge: {max(z_values)}"

    nominal_major_radius = nominal_diameter / 2.0
    assert max(radii) >= nominal_major_radius - 0.08, f"Kein Vertex nahe Major-Radius: {max(radii)}"

    center_vertices = [radius for radius in radii if radius <= 1e-5]
    assert len(center_vertices) <= 2, f"Unerwartete Achs-Vertices außerhalb der Cap-Zentren: {len(center_vertices)}"

    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        volume = abs(bm.calc_volume())
    finally:
        bm.free()

    thin_shell_volume = math.pi * (nominal_major_radius**2 - (nominal_major_radius - 0.2) ** 2) * expected_length
    assert volume > thin_shell_volume * 3.0, f"Volumen wirkt wie dünne Hülle: {volume}"


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
    assert_solid_external_rod(created, expected_length=props.length, nominal_diameter=10.0)

    bpy.ops.mesh.primitive_cube_add(size=20.0, location=(0.0, 0.0, 10.0))
    target = bpy.context.active_object
    props.negative_mode = True
    result = bpy.ops.utg.create_thread()
    assert "FINISHED" in result

    assert target is not None and target.type == "MESH"
finally:
    addon.unregister()
