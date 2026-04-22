import bmesh
import bpy
import math
from mathutils import Vector

from .database import MATERIAL_PRESETS


def _apply_end_profile(loop_verts, end_type, z_center):
    if end_type == "FLAT" or not loop_verts:
        return

    zs = [v.co.z for v in loop_verts]
    z_min, z_max = min(zs), max(zs)
    span = max(1e-6, z_max - z_min)

    for v in loop_verts:
        rel = (v.co.z - z_min) / span
        if end_type == "CHAMFER":
            # lineare 45°-ähnliche Verjüngung
            shrink = 1.0 - 0.12 * rel
        else:  # RUNOUT
            # weichere S-Kurve
            shrink = 1.0 - 0.16 * (rel * rel * (3.0 - 2.0 * rel))
        v.co.x *= shrink
        v.co.y *= shrink
        v.co.z += z_center


def create_thread_mesh(
    name,
    profile_points,
    diameter,
    pitch,
    length,
    starts=1,
    handedness="RIGHT",
    end_type="CHAMFER",
    taper_ratio=0.0,
    lod_level="FINAL",
    segment_override=48,
):
    """Erzeugt ein manifoldes BMesh einer Gewindestange."""
    _ = (name, diameter)
    bm = bmesh.new()

    turns = max(length / max(pitch, 1e-6), 0.01)
    if lod_level == "PREVIEW":
        lod_factor = 0.70
    elif lod_level == "CUSTOM":
        lod_factor = 1.0
    else:
        lod_factor = 1.15

    auto_segments = max(24, int((36 * (pitch / 5.0) + diameter * 0.6) * lod_factor))
    segments_per_turn = max(12, int(segment_override)) if lod_level == "CUSTOM" else auto_segments
    if length > 250.0:
        segments_per_turn = max(18, int(segments_per_turn * 0.85))
    total_segments = int(turns * segments_per_turn) + 1
    direction = 1.0 if handedness == "RIGHT" else -1.0

    prev_loop_verts = []
    first_loop_verts = []

    for seg in range(total_segments):
        t = seg / segments_per_turn
        angle = t * 2.0 * math.pi * direction
        z = t * pitch * starts

        current_verts = []
        taper_scale = 1.0
        if taper_ratio > 0.0:
            # NPT: Durchmesseränderung über Länge mit 1:x-Verhältnis
            diam_delta = z * taper_ratio
            taper_scale = max(0.2, 1.0 - diam_delta / max(diameter, 1e-6))
        for pt in profile_points:
            radial = pt.x * taper_scale
            x = radial * math.cos(angle)
            y = radial * math.sin(angle)
            z_local = pt.y * starts
            current_verts.append(bm.verts.new(Vector((x, y, z_local + z))))

        if seg > 0:
            n = len(profile_points)
            for i in range(n):
                v1 = prev_loop_verts[i]
                v2 = prev_loop_verts[(i + 1) % n]
                v3 = current_verts[(i + 1) % n]
                v4 = current_verts[i]
                try:
                    bm.faces.new((v1, v2, v3, v4))
                except ValueError:
                    pass

        prev_loop_verts = current_verts
        if seg == 0:
            first_loop_verts = current_verts

    # Endtyp-Modifikation an den äußersten Querschnitten
    _apply_end_profile(first_loop_verts, end_type, z_center=0.0)
    _apply_end_profile(prev_loop_verts, end_type, z_center=0.0)

    center_bottom = bm.verts.new(Vector((0.0, 0.0, 0.0)))
    for i in range(len(first_loop_verts)):
        v1 = first_loop_verts[i]
        v2 = first_loop_verts[(i + 1) % len(first_loop_verts)]
        try:
            bm.faces.new((center_bottom, v1, v2))
        except ValueError:
            pass

    center_top = bm.verts.new(Vector((0.0, 0.0, length)))
    for i in range(len(prev_loop_verts)):
        v1 = prev_loop_verts[i]
        v2 = prev_loop_verts[(i + 1) % len(prev_loop_verts)]
        try:
            bm.faces.new((center_top, v2, v1))
        except ValueError:
            pass

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
    if non_manifold_edges:
        bmesh.ops.holes_fill(bm, edges=non_manifold_edges, sides=0)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    return bm


def apply_material(obj, material_key, surface_key="NONE"):
    """Weist dem Objekt ein Material aus MATERIAL_PRESETS zu."""
    resolved_key = material_key
    if surface_key in {"ZINC", "HOT_DIP"}:
        resolved_key = surface_key

    mat_name = f"UTG_{resolved_key}"
    if mat_name not in bpy.data.materials:
        mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        preset = MATERIAL_PRESETS[resolved_key]
        bsdf.inputs["Base Color"].default_value = preset["color"]
        bsdf.inputs["Metallic"].default_value = preset["metallic"]
        bsdf.inputs["Roughness"].default_value = preset["roughness"]
        if "IOR" in bsdf.inputs:
            bsdf.inputs["IOR"].default_value = preset["ior"]
    else:
        mat = bpy.data.materials[mat_name]

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def apply_boolean_cutter(context, cutter_obj, target_obj):
    """Führt Boolesche Differenz aus und löscht Cutter.

    Sichert und restauriert den Objekt-/Selektionszustand, damit der Workflow
    auch in komplexeren Szenen stabil bleibt.
    """
    prev_active = context.view_layer.objects.active
    prev_selected = [obj for obj in context.selected_objects]

    try:
        for obj in prev_selected:
            obj.select_set(False)

        context.view_layer.objects.active = target_obj
        target_obj.select_set(True)
        cutter_obj.select_set(True)

        mod = target_obj.modifiers.new(name="UTG_Boolean", type="BOOLEAN")
        mod.object = cutter_obj
        mod.operation = "DIFFERENCE"

        bpy.ops.object.modifier_apply({"object": target_obj, "active_object": target_obj}, modifier=mod.name)
        bpy.data.objects.remove(cutter_obj, do_unlink=True)
    finally:
        for obj in context.selected_objects:
            obj.select_set(False)
        for obj in prev_selected:
            if obj.name in bpy.data.objects:
                obj.select_set(True)
        if prev_active and prev_active.name in bpy.data.objects:
            context.view_layer.objects.active = prev_active


def create_nut_body_mesh(name, outer_diameter, length, segments=64):
    """Erzeugt einen einfachen zylindrischen Mutterrohling als BMesh."""
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=max(16, int(segments)),
        radius1=max(outer_diameter * 0.5, 0.1),
        radius2=max(outer_diameter * 0.5, 0.1),
        depth=max(length, 0.1),
    )
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector((0.0, 0.0, length * 0.5)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def create_return_tube_mesh(name, major_radius, minor_radius, location):
    """Erzeugt ein optionales Rückführungsmodul (vereinfachter Torus)."""
    bm = bmesh.new()
    bmesh.ops.create_torus(
        bm,
        major_segments=40,
        minor_segments=16,
        major_radius=max(major_radius, 0.1),
        minor_radius=max(minor_radius, 0.05),
    )
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(location))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm
