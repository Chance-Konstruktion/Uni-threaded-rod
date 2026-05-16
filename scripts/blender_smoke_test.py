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

def assert_solid_external_rod(obj, expected_length_mm, nominal_diameter_mm):
    """Beweist die Kernregel im Blender-Smoke-Test: volle Außengewindestange."""
    mesh = obj.data
    radii = [math.hypot(vertex.co.x, vertex.co.y) for vertex in mesh.vertices]
    z_values = [vertex.co.z for vertex in mesh.vertices]

    expected_length = expected_length_mm / 1000.0
    assert min(z_values) >= -1e-5, f"Mesh ragt unter z=0: {min(z_values)}"
    assert max(z_values) <= expected_length + 1e-5, f"Mesh ragt über Länge hinaus: {max(z_values)}"
    assert abs(min(z_values)) <= 1e-5, f"Bounding Box startet nicht bei z=0: {min(z_values)}"
    assert abs(max(z_values) - expected_length) <= 1e-5, f"Bounding Box endet nicht bei Länge: {max(z_values)}"

    nominal_major_radius = nominal_diameter_mm / 2000.0
    assert max(radii) >= nominal_major_radius - 0.00008, f"Kein Vertex nahe Major-Radius: {max(radii)}"

    center_vertices = [radius for radius in radii if radius <= 1e-5]
    assert len(center_vertices) <= 2, f"Unerwartete Achs-Vertices außerhalb der Cap-Zentren: {len(center_vertices)}"

    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        volume = abs(bm.calc_volume())
    finally:
        bm.free()

    shell_thickness = 0.0002
    thin_shell_volume = math.pi * (nominal_major_radius**2 - (nominal_major_radius - shell_thickness) ** 2) * expected_length
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
    assert_solid_external_rod(created, expected_length_mm=props.length, nominal_diameter_mm=10.0)

    npt_diameter = 21.3
    npt_pitch = 1.814
    npt_length = 32.0
    npt_profile = addon.generate_profile("NPT", npt_diameter, npt_pitch, tolerance_class="L1")
    npt_bm = addon.create_thread_mesh(
        npt_profile,
        npt_diameter,
        npt_pitch,
        npt_length,
        end_type="FLAT",
        taper_ratio=1 / 16,
        lod_level="PREVIEW",
    )
    try:
        start_radius = max(math.hypot(v.co.x, v.co.y) for v in npt_bm.verts if abs(v.co.z) <= 1e-8)
        end_z = npt_length / 1000.0
        end_radius = max(math.hypot(v.co.x, v.co.y) for v in npt_bm.verts if abs(v.co.z - end_z) <= 1e-8)
        assert start_radius > end_radius, "NPT-Konus startet nicht am größeren Ende"
    finally:
        npt_bm.free()

    storz_bm = addon.create_bayonet_mesh("STORZ", diameter=66.0, length=35.0, lod_level="PREVIEW")
    try:
        storz_radii = [math.hypot(v.co.x, v.co.y) for v in storz_bm.verts if math.hypot(v.co.x, v.co.y) > 1e-8]
        assert max(storz_radii) > 66.0 / 2000.0, "STORZ-Knaggen fehlen"
        assert min(storz_radii) < 66.0 / 2000.0, "STORZ-Nut fehlt"
    finally:
        storz_bm.free()

finally:
    addon.unregister()
