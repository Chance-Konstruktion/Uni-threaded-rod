import bmesh
import bpy
import math
from mathutils import Vector

from .database import MATERIAL_PRESETS


def create_thread_mesh(name, profile_points, diameter, pitch, length, starts=1, handedness="RIGHT", end_type="CHAMFER"):
    """Erzeugt ein manifoldes BMesh einer Gewindestange."""
    _ = (name, diameter, end_type)
    bm = bmesh.new()

    turns = max(length / pitch, 0.01)
    segments_per_turn = max(24, int(36 * (pitch / 5.0)))
    total_segments = int(turns * segments_per_turn) + 1
    direction = 1.0 if handedness == "RIGHT" else -1.0

    prev_loop_verts = []
    first_loop_verts = []
    for seg in range(total_segments):
        t = seg / segments_per_turn
        angle = t * 2 * math.pi * direction
        z = t * pitch * starts

        current_verts = []
        for pt in profile_points:
            x = pt.x * math.cos(angle)
            y = pt.x * math.sin(angle)
            z_local = pt.y * starts
            current_verts.append(bm.verts.new(Vector((x, y, z_local + z))))

        if seg > 0:
            n = len(profile_points)
            for i in range(n):
                face = (
                    prev_loop_verts[i],
                    prev_loop_verts[(i + 1) % n],
                    current_verts[(i + 1) % n],
                    current_verts[i],
                )
                try:
                    bm.faces.new(face)
                except ValueError:
                    continue

        prev_loop_verts = current_verts
        if seg == 0:
            first_loop_verts = current_verts

    bv_center_bottom = bm.verts.new(Vector((0, 0, 0)))
    for i, v1 in enumerate(first_loop_verts):
        v2 = first_loop_verts[(i + 1) % len(first_loop_verts)]
        try:
            bm.faces.new((bv_center_bottom, v1, v2))
        except ValueError:
            continue

    bv_center_top = bm.verts.new(Vector((0, 0, length)))
    for i, v1 in enumerate(prev_loop_verts):
        v2 = prev_loop_verts[(i + 1) % len(prev_loop_verts)]
        try:
            bm.faces.new((bv_center_top, v1, v2))
        except ValueError:
            continue

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def apply_material(obj, material_key):
    """Weist dem Objekt ein Material aus MATERIAL_PRESETS zu."""
    mat_name = f"UTG_{material_key}"
    if mat_name not in bpy.data.materials:
        mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        preset = MATERIAL_PRESETS[material_key]
        bsdf.inputs["Base Color"].default_value = preset["color"]
        bsdf.inputs["Metallic"].default_value = preset["metallic"]
        bsdf.inputs["Roughness"].default_value = preset["roughness"]
    else:
        mat = bpy.data.materials[mat_name]

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def apply_boolean_cutter(context, cutter_obj, target_obj):
    """Führt Boolesche Differenz aus und löscht Cutter."""
    context.view_layer.objects.active = target_obj
    mod = target_obj.modifiers.new(name="UTG_Boolean", type="BOOLEAN")
    mod.object = cutter_obj
    mod.operation = "DIFFERENCE"
    bpy.ops.object.modifier_apply({"object": target_obj}, modifier=mod.name)
    bpy.data.objects.remove(cutter_obj)
